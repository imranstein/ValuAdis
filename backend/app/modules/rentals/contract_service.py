"""
Tenancy Contract Service (Phase C)

Officers register a tenancy contract from an accepted application. The
contract number is a per-year registry sequence (AA-RNT-<year>-<seq>)
allocated under a row lock with a unique-constraint backstop, so concurrent
creation cannot collide. Money is evidenced, never held: a contract is
`draft` until a deposit receipt whose amount matches the contract deposit is
recorded, which transitions it to `active`. Every transition is audited.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
import structlog

from app.core.exceptions import AuthorizationException, ValidationException, ValuAdisException
from app.data.models.audit_log import AuditLog
from app.data.models.property import Property
from app.data.models.user import User
from app.data.models.valuation import Valuation
from .models import (
    RentalApplication,
    RentalApplicationStatus,
    RentalContractSequence,
    RentalListing,
    TenancyContract,
    TenancyContractStatus,
)
from .repositories import RentalListingRepository, TenancyContractRepository

logger = structlog.get_logger()

CONTRACT_NO_PREFIX = "AA-RNT"
CONTRACT_NO_MAX_ATTEMPTS = 25
# First + last month deposit is the default (plan / proclamation practice).
DEFAULT_DEPOSIT_MONTHS = 2
# Contract PDFs are generated on demand; the stored value is the retrieval
# path (there is no third-party file store in this phase), mirroring how
# valuation certificates are served.
CONTRACT_PDF_PATH_TEMPLATE = "/api/v1/rentals/contracts/{contract_no}/pdf"
# Named cap on the tax-base CSV export (hardening: pagination/row caps on
# every list-producing endpoint), matching the property export's precedent.
CONTRACTS_EXPORT_MAX_ROWS = 10000


class TenancyContractService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TenancyContractRepository(db)
        self.listing_repo = RentalListingRepository(db)

    # ------------------------------------------------------------------
    # Contract creation
    # ------------------------------------------------------------------

    def create_contract(
        self,
        application_id: int,
        officer: User,
        start_date: date,
        end_date: date,
        deposit_amount: Optional[float] = None,
        deposit_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        application = (
            self.db.query(RentalApplication)
            .filter(RentalApplication.id == application_id)
            .first()
        )
        if not application:
            raise ValuAdisException("Application not found")

        # Contracts may only be created from an accepted application.
        if application.status != RentalApplicationStatus.ACCEPTED.value:
            raise ValidationException(
                f"A contract can only be created from an accepted application "
                f"(this one is '{application.status}')."
            )

        if self.repo.get_for_application(application_id) is not None:
            raise ValidationException("A contract already exists for this application.")

        if end_date <= start_date:
            raise ValidationException("end_date must be after start_date.")

        # Rent is captured server-side from the accepted offer, never trusted
        # from the client.
        monthly_rent = float(application.offered_rent)
        default_deposit = round(monthly_rent * DEFAULT_DEPOSIT_MONTHS, 2)
        if deposit_amount is None:
            resolved_deposit = default_deposit
        else:
            resolved_deposit = float(deposit_amount)
            if abs(resolved_deposit - default_deposit) > 0.005 and not (deposit_reason and deposit_reason.strip()):
                raise ValidationException(
                    "A reason is mandatory when overriding the default deposit "
                    f"(default is {default_deposit:,.2f} ETB = {DEFAULT_DEPOSIT_MONTHS} x monthly rent)."
                )

        contract = self._insert_with_contract_no(
            application=application,
            monthly_rent=monthly_rent,
            start_date=start_date,
            end_date=end_date,
            deposit_amount=resolved_deposit,
        )

        self._audit(
            "create",
            contract,
            officer.id,
            {
                "contract_no": contract.contract_no,
                "monthly_rent": monthly_rent,
                "deposit_amount": resolved_deposit,
                "deposit_override_reason": deposit_reason if deposit_amount is not None else None,
            },
        )
        logger.info(
            "Tenancy contract created",
            contract_no=contract.contract_no,
            application_id=application_id,
            officer_id=officer.id,
        )
        return self.to_dict(contract)

    def _insert_with_contract_no(
        self,
        application: RentalApplication,
        monthly_rent: float,
        start_date: date,
        end_date: date,
        deposit_amount: float,
    ) -> TenancyContract:
        """Allocate a registry number and insert the contract, retrying on the
        unique-constraint backstop so a race can never mint a duplicate."""
        year = datetime.now(timezone.utc).year
        last_error: Optional[Exception] = None
        for _ in range(CONTRACT_NO_MAX_ATTEMPTS):
            try:
                seq = self._next_sequence_value(year)
                contract_no = f"{CONTRACT_NO_PREFIX}-{year}-{seq:06d}"
                contract = TenancyContract(
                    contract_no=contract_no,
                    listing_id=application.listing_id,
                    application_id=application.id,
                    monthly_rent=monthly_rent,
                    start_date=start_date,
                    end_date=end_date,
                    deposit_amount=deposit_amount,
                    status=TenancyContractStatus.DRAFT.value,
                    contract_pdf=CONTRACT_PDF_PATH_TEMPLATE.format(contract_no=contract_no),
                )
                self.db.add(contract)
                self.db.commit()
                self.db.refresh(contract)
                return contract
            except IntegrityError as exc:
                # contract_no or application_id uniqueness lost a race — retry
                # the number; a duplicate application_id will keep failing and
                # surface as a genuine "already exists" on the next check.
                self.db.rollback()
                last_error = exc
                if self.repo.get_for_application(application.id) is not None:
                    raise ValidationException("A contract already exists for this application.")
            except OperationalError as exc:
                # e.g. SQLite "database is locked" under contention — retry.
                self.db.rollback()
                last_error = exc
        raise ValuAdisException(
            f"Could not allocate a unique contract number after retries: {last_error}"
        )

    def _next_sequence_value(self, year: int) -> int:
        """Atomically increment the per-year counter under a row lock."""
        row = (
            self.db.query(RentalContractSequence)
            .filter(RentalContractSequence.year == year)
            .with_for_update()
            .first()
        )
        if row is None:
            row = RentalContractSequence(year=year, last_value=0)
            self.db.add(row)
            try:
                self.db.flush()
            except IntegrityError:
                # Another transaction created the row first; re-read under lock.
                self.db.rollback()
                row = (
                    self.db.query(RentalContractSequence)
                    .filter(RentalContractSequence.year == year)
                    .with_for_update()
                    .first()
                )
        row.last_value = (row.last_value or 0) + 1
        self.db.flush()
        return row.last_value

    # ------------------------------------------------------------------
    # Deposit recording — the draft -> active gate
    # ------------------------------------------------------------------

    def record_deposit(
        self,
        contract_no: str,
        officer: User,
        deposit_receipt_ref: str,
        amount: float,
        paid_on: Optional[date] = None,
    ) -> Dict[str, Any]:
        contract = self.repo.get_by_contract_no(contract_no)
        if not contract:
            raise ValuAdisException("Contract not found")

        # State machine: only a draft contract without a receipt can be
        # activated. active/terminated/expired are all guarded.
        if contract.status != TenancyContractStatus.DRAFT.value:
            raise ValidationException(
                f"Deposit can only be recorded on a draft contract (this one is '{contract.status}')."
            )
        if contract.deposit_receipt_ref:
            raise ValidationException("A deposit receipt has already been recorded for this contract.")

        # The receipt amount must match the contract deposit exactly; a
        # mismatch is rejected with a clear error, never silently accepted.
        if abs(float(amount) - float(contract.deposit_amount)) > 0.005:
            raise ValidationException(
                f"Receipt amount {float(amount):,.2f} does not match the required deposit "
                f"{float(contract.deposit_amount):,.2f} ETB."
            )

        now = datetime.now(timezone.utc)
        updated = self.repo.update(
            contract,
            {
                "deposit_receipt_ref": deposit_receipt_ref,
                "deposit_paid_on": paid_on,
                "deposit_recorded_at": now,
                "status": TenancyContractStatus.ACTIVE.value,
                "activated_at": now,
            },
        )
        self._audit(
            "deposit_recorded",
            updated,
            officer.id,
            {
                "deposit_receipt_ref": deposit_receipt_ref,
                "amount": float(amount),
                "status": updated.status,
            },
        )
        logger.info(
            "Deposit recorded, contract activated",
            contract_no=contract_no,
            officer_id=officer.id,
        )
        return self.to_dict(updated)

    # ------------------------------------------------------------------
    # Reads + PDF context
    # ------------------------------------------------------------------

    def list_contracts(self, skip: int = 0, limit: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        contracts, total = self.repo.list_all(skip, limit)
        return [self.to_dict(c) for c in contracts], total

    def list_contracts_for_export(self, limit: int = CONTRACTS_EXPORT_MAX_ROWS) -> List[Dict[str, Any]]:
        """Full contract rows for the tax-base CSV export (officer-gated —
        party IDs are intentionally included here, unlike every public
        serializer in this module)."""
        contracts, _ = self.repo.list_all(0, limit)
        return [self._to_export_dict(c) for c in contracts]

    def _to_export_dict(self, contract: TenancyContract) -> Dict[str, Any]:
        listing = contract.listing
        application = contract.application
        prop = listing.property if listing else None
        owner = self.db.query(User).filter(User.id == listing.owner_user_id).first() if listing else None
        renter = (
            self.db.query(User).filter(User.id == application.renter_user_id).first()
            if application
            else None
        )
        return {
            "contract_no": contract.contract_no,
            "property_address": prop.address if prop else "",
            "municipality": prop.municipality if prop else "",
            "subcity": prop.subcity if prop else "",
            "owner_name": owner.full_name if owner else "",
            "owner_fayda_id": owner.fayda_id_number if owner else "",
            "renter_name": renter.full_name if renter else "",
            "renter_fayda_id": renter.fayda_id_number if renter else "",
            "monthly_rent": contract.monthly_rent,
            "deposit_amount": contract.deposit_amount,
            "deposit_receipt_ref": contract.deposit_receipt_ref or "",
            "status": contract.status,
            "start_date": contract.start_date.isoformat() if contract.start_date else "",
            "end_date": contract.end_date.isoformat() if contract.end_date else "",
            "created_at": contract.created_at.isoformat() if contract.created_at else "",
        }

    def get_contract(self, contract_no: str) -> Optional[TenancyContract]:
        return self.repo.get_by_contract_no(contract_no)

    def can_view_contract(self, contract: TenancyContract, user: User) -> bool:
        """Officer (or admin) always; otherwise only the owner or renter party."""
        from .services import _is_rental_officer

        if _is_rental_officer(user):
            return True
        listing = contract.listing
        application = contract.application
        if listing and listing.owner_user_id == user.id:
            return True
        if application and application.renter_user_id == user.id:
            return True
        return False

    def build_pdf_context(self, contract: TenancyContract) -> Dict[str, Any]:
        """Assemble everything the contract PDF template needs (parties with
        Fayda IDs, property identification, band, valuation reference)."""
        listing: RentalListing = contract.listing
        application: RentalApplication = contract.application
        prop = self.db.query(Property).filter(Property.id == listing.property_id).first()
        owner_user = self.db.query(User).filter(User.id == listing.owner_user_id).first()
        renter_user = self.db.query(User).filter(User.id == application.renter_user_id).first()
        valuation = self.db.query(Valuation).filter(Valuation.id == listing.valuation_id).first()

        return {
            "contract": self.to_dict(contract),
            "owner": _party_dict(owner_user),
            "renter": _party_dict(renter_user),
            "property_data": {
                "address": prop.address if prop else "—",
                "municipality": prop.municipality if prop else "—",
                "subcity": prop.subcity if prop else "—",
                "property_type": prop.property_type if prop else "—",
                "area_sqm": prop.area_sqm if prop else 0,
            },
            "rent_context": {
                "band_min": listing.band_min,
                "band_max": listing.band_max,
                "valuation_reference": f"VAL-{valuation.id}" if valuation else "—",
            },
        }

    @staticmethod
    def to_dict(contract: TenancyContract) -> Dict[str, Any]:
        return {
            "contract_no": contract.contract_no,
            "listing_public_id": contract.listing.public_id if contract.listing else None,
            "application_id": contract.application_id,
            "monthly_rent": contract.monthly_rent,
            "start_date": contract.start_date.isoformat() if contract.start_date else None,
            "end_date": contract.end_date.isoformat() if contract.end_date else None,
            "deposit_amount": contract.deposit_amount,
            "deposit_receipt_ref": contract.deposit_receipt_ref,
            "deposit_paid_on": contract.deposit_paid_on.isoformat() if contract.deposit_paid_on else None,
            "status": contract.status,
            "activated_at": contract.activated_at.isoformat() if contract.activated_at else None,
            "contract_pdf": contract.contract_pdf,
            "created_at": contract.created_at.isoformat() if contract.created_at else None,
        }

    def _audit(
        self,
        action: str,
        contract: TenancyContract,
        actor_user_id: int,
        new_values: Dict[str, Any],
    ) -> None:
        self.db.add(
            AuditLog(
                table_name="tenancy_contracts",
                record_id=contract.id,
                action=action,
                new_values={"contract_no": contract.contract_no, **new_values},
                user_id=actor_user_id,
            )
        )
        self.db.commit()


def _party_dict(user: Optional[User]) -> Dict[str, Any]:
    return {
        "full_name": user.full_name if user else "—",
        "fayda_id_number": user.fayda_id_number if user else None,
        "phone": user.phone if user else None,
    }
