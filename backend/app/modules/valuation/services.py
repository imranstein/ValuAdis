"""
Valuation Service

Business logic for property valuation calculations following Ethiopian standards
and Proclamation 1365/2025 compliance requirements.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from statistics import median
from typing import Dict, Any, Optional, Tuple, List
from app.services.spatial_service import SpatialService
from app.core.exceptions import ValuAdisException, PropertyValidationError
from .schemas import ValuationCreate
from sqlalchemy.orm import Session
import structlog

logger = structlog.get_logger()


class ValuationService:
    """
    Property valuation service for Ethiopian properties

    Implements market value and taxable value calculations per
    Proclamation 1365/2025 requirements.
    """

    # ------------------------------------------------------------------
    # Rent valuation constants (plans/valuadis-rentals/plan.mdx, Phase A)
    # ------------------------------------------------------------------

    # Published band = suggested rent ± 10%, frozen on the listing at
    # publish time (Phase B concern; this is the band the engine computes).
    RENT_BAND_PCT: Decimal = Decimal("0.10")

    # Below this blended confidence score, the result is not precise
    # enough to publish unattended and must be reviewed by a rental
    # officer before a listing/band is finalized.
    RENT_CONFIDENCE_FLOOR: Decimal = Decimal("0.50")

    # Comp count at/above which the comps method contributes its maximum
    # share of the confidence score. Confidence scales linearly up to it.
    RENT_COMPS_FOR_FULL_CONFIDENCE: int = 5

    # Confidence contribution when both estimate methods agree/are present
    # vs. only one, before the comp-count-weighted bonus is added.
    RENT_CONFIDENCE_BASE_BOTH_METHODS: Decimal = Decimal("0.60")
    RENT_CONFIDENCE_BASE_RATIO_ONLY: Decimal = Decimal("0.40")
    RENT_CONFIDENCE_BASE_COMPS_ONLY: Decimal = Decimal("0.50")
    RENT_CONFIDENCE_COMP_COUNT_WEIGHT: Decimal = Decimal("0.40")

    # Trend adjustment is capped to a modest nudge — it reflects short-run
    # market momentum, not a replacement for the ratio/comps estimate.
    RENT_MAX_TREND_ADJUSTMENT: Decimal = Decimal("0.05")

    # Conservative citywide fallback ratio (~7.2% annual gross residential
    # yield / 12) used when a district has no rent-tagged market listings
    # yet. app.data.seeders.rent_ratio_seeder imports this constant so the
    # seeded config and the runtime fallback never drift apart.
    RENT_RATIO_CITYWIDE_FALLBACK: Decimal = Decimal("0.006")

    def __init__(self, spatial_service: SpatialService, db: Optional[Session] = None):
        self._spatial_service = spatial_service
        self.db = db
        if db:
            from app.data.repositories.valuation_repository import ValuationRepository
            self.valuation_repo = ValuationRepository(db)

        # Ethiopian municipality base rates (Birr per square meter)
        # Tier 1: Capital / Major Commercial
        # Tier 2: Regional Capitals
        # Tier 3: Secondary Cities
        self._base_rates: Dict[str, Decimal] = {
            # Tier 1 – Capital / Major Commercial
            "Addis Ababa": Decimal("1000.00"),
            "Dire Dawa":   Decimal("800.00"),
            # Tier 2 – Regional Capitals
            "Mekelle":     Decimal("600.00"),
            "Bahir Dar":   Decimal("550.00"),
            "Adama":       Decimal("500.00"),
            "Hawassa":     Decimal("450.00"),
            "Gonder":      Decimal("400.00"),
            "Jimma":       Decimal("350.00"),
            # Tier 3 – Secondary Cities
            "Dessie":      Decimal("320.00"),
            "Jijiga":      Decimal("310.00"),
            "Shashamane":  Decimal("300.00"),
            "Arba Minch":  Decimal("290.00"),
            "Harar":       Decimal("280.00"),
            "Nekemte":     Decimal("270.00"),
            "Debre Markos":Decimal("260.00"),
            "Debre Birhan":Decimal("250.00"),
        }

        # Property type multipliers
        self._property_type_multipliers: Dict[str, Decimal] = {
            "residential":  Decimal("1.0"),
            "commercial":   Decimal("1.5"),
            "industrial":   Decimal("1.3"),
            "agricultural": Decimal("0.3"),
            "mixed_use":    Decimal("1.2"),
        }

        # Condition grade adjustments (Proclamation 1365/2025 Annex B)
        # Applied as a multiplier on the base calculation
        self._condition_factors: Dict[str, Decimal] = {
            "excellent": Decimal("1.20"),  # New / recently renovated
            "good":      Decimal("1.00"),  # Well-maintained
            "fair":      Decimal("0.80"),  # Some wear, minor repairs needed
            "poor":      Decimal("0.60"),  # Significant deterioration
        }

        # Neighborhood quality multipliers
        self._neighborhood_multipliers: Dict[str, Decimal] = {
            "prime":       Decimal("1.30"),  # CBD / high-demand zones
            "above_average": Decimal("1.10"),
            "average":     Decimal("1.00"),  # Default
            "below_average": Decimal("0.85"),
            "developing":  Decimal("0.70"),
        }

        # Annual depreciation rate for structures (straight-line)
        _ANNUAL_DEPRECIATION = Decimal("0.01")   # 1% per year
        _MAX_DEPRECIATION    = Decimal("0.50")    # Cap at 50%
        self._annual_depreciation = _ANNUAL_DEPRECIATION
        self._max_depreciation    = _MAX_DEPRECIATION

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_market_value(self, property_data: Dict[str, Any]) -> Decimal:
        """
        Calculate market value following Proclamation 1365/2025.

        Formula:
            land_value     = base_rate × area × type_multiplier
            structure_val  = land_value × structure_ratio × (1 – depreciation)
            neighborhood   = (land_value + structure_val) × neighborhood_multiplier
            market_value   = neighborhood × condition_factor

        Args:
            property_data: dict with keys:
                - municipality (str)
                - area_sqm (float | int | str)
                - property_type (str, optional) default "residential"
                - condition (str, optional)  default "good"
                - neighborhood_quality (str, optional)  default "average"
                - construction_year (int, optional)

        Returns:
            Market value in Ethiopian Birr (Decimal)
        """
        self._validate_property_data(property_data)

        municipality  = property_data["municipality"]
        area_sqm      = Decimal(str(property_data["area_sqm"]))
        property_type = property_data.get("property_type", "residential")
        condition     = property_data.get("condition", "good")
        neighborhood  = property_data.get("neighborhood_quality", "average")
        construction_year = property_data.get("construction_year")

        base_rate = self._base_rates.get(municipality)
        if not base_rate:
            # Fall back to the lowest tier rate for unlisted municipalities
            base_rate = Decimal("220.00")

        type_mult          = self._property_type_multipliers.get(property_type, Decimal("1.0"))
        condition_factor   = self._condition_factors.get(condition, Decimal("1.0"))
        neighborhood_mult  = self._neighborhood_multipliers.get(neighborhood, Decimal("1.0"))

        # Base land + structure value
        base_value = base_rate * area_sqm * type_mult

        # Apply age-based depreciation to structure component (40% of value)
        structure_ratio = Decimal("0.40")
        land_value      = base_value * (Decimal("1") - structure_ratio)
        structure_value = base_value * structure_ratio

        depreciation = self._calculate_depreciation(construction_year)
        structure_value_depreciated = structure_value * (Decimal("1") - depreciation)

        subtotal     = land_value + structure_value_depreciated
        after_nhd    = subtotal * neighborhood_mult
        market_value = after_nhd * condition_factor

        return market_value.quantize(Decimal("0.01"))

    def calculate_taxable_value(self, market_value: Decimal) -> Decimal:
        """
        Calculate taxable value per Proclamation 1365/2025 Art. 12.

        Taxable value = 25% of market value.
        """
        if market_value < 0:
            raise PropertyValidationError("Market value must be greater than 0")
        taxable_value = market_value * Decimal("0.25")
        if taxable_value < Decimal("100"):
            return taxable_value.quantize(Decimal("0.01"))
        return taxable_value.quantize(Decimal("1E+2"), rounding=ROUND_HALF_UP)

    def get_valuation_breakdown(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a full valuation breakdown for transparency / certificate generation.
        """
        self._validate_property_data(property_data)

        municipality       = property_data["municipality"]
        area_sqm           = Decimal(str(property_data["area_sqm"]))
        property_type      = property_data.get("property_type", "residential")
        condition          = property_data.get("condition", "good")
        neighborhood       = property_data.get("neighborhood_quality", "average")
        construction_year  = property_data.get("construction_year")

        is_fallback_rate   = municipality not in self._base_rates
        base_rate          = self._base_rates.get(municipality, Decimal("220.00"))
        type_mult          = self._property_type_multipliers.get(property_type, Decimal("1.0"))
        condition_factor   = self._condition_factors.get(condition, Decimal("1.0"))
        neighborhood_mult  = self._neighborhood_multipliers.get(neighborhood, Decimal("1.0"))
        depreciation       = self._calculate_depreciation(construction_year)

        base_value         = base_rate * area_sqm * type_mult
        structure_ratio    = Decimal("0.40")
        land_value         = (base_value * (Decimal("1") - structure_ratio)).quantize(Decimal("0.01"))
        structure_value    = (base_value * structure_ratio).quantize(Decimal("0.01"))
        structure_depreciated = (structure_value * (Decimal("1") - depreciation)).quantize(Decimal("0.01"))
        subtotal           = land_value + structure_depreciated
        after_nhd          = (subtotal * neighborhood_mult).quantize(Decimal("0.01"))
        market_value       = (after_nhd * condition_factor).quantize(Decimal("0.01"))
        taxable_value      = self.calculate_taxable_value(market_value)

        return {
            "municipality":              municipality,
            "area_sqm":                  float(area_sqm),
            "property_type":             property_type,
            "condition":                 condition,
            "neighborhood_quality":      neighborhood,
            "construction_year":         construction_year,
            "base_rate_per_sqm":         float(base_rate),
            "is_fallback_rate":          is_fallback_rate,
            "type_multiplier":           float(type_mult),
            "condition_factor":          float(condition_factor),
            "neighborhood_multiplier":   float(neighborhood_mult),
            "depreciation_rate":         float(depreciation),
            "land_value":                float(land_value),
            "structure_value_before_depreciation": float(structure_value),
            "structure_value_after_depreciation":  float(structure_depreciated),
            "subtotal":                  float(subtotal),
            "market_value":              float(market_value),
            "taxable_value":             float(taxable_value),
            "proclamation_reference":    "Proclamation 1365/2025 Art. 12",
        }

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def create_valuation(self, valuation_data: ValuationCreate, user_id: int) -> Dict[str, Any]:
        """Create a new valuation record."""
        property_data  = valuation_data.model_dump()
        market_value   = self.calculate_market_value(property_data)
        taxable_value  = self.calculate_taxable_value(market_value)

        coordinates_wkt = self._spatial_service.create_wkt_polygon(property_data["coordinates"])

        db_valuation = self.valuation_repo.create({
            "property_id":  valuation_data.property_id,
            "user_id":      user_id,
            "property_type": valuation_data.property_type,
            "municipality": valuation_data.municipality,
            "area_sqm":     valuation_data.area_sqm,
            "market_value": market_value,
            "taxable_value": taxable_value,
            "status":       "draft",
            "coordinates":  coordinates_wkt,
        })

        return db_valuation.to_dict() if hasattr(db_valuation, "to_dict") else {
            "id":            db_valuation.id,
            "property_id":  db_valuation.property_id,
            "market_value": db_valuation.market_value,
            "taxable_value": db_valuation.taxable_value,
            "status":       db_valuation.status,
        }

    def get_user_valuations(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], int]:
        valuations_list = self.valuation_repo.get_user_valuations(user_id=user_id, skip=skip, limit=limit)
        total = self.db.query(self.valuation_repo.model).filter_by(user_id=user_id).count()
        return [v.to_dict() if hasattr(v, "to_dict") else v.__dict__ for v in valuations_list], total

    def get_valuation_by_id(self, valuation_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        valuation = self.valuation_repo.get_valuation_by_id_and_user(valuation_id, user_id)
        if valuation:
            return valuation.to_dict() if hasattr(valuation, "to_dict") else valuation.__dict__
        return None

    def update_valuation(self, valuation_id: int, updates: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        valuation = self.valuation_repo.get_valuation_by_id_and_user(valuation_id, user_id)
        if valuation:
            updated = self.valuation_repo.update(valuation, updates)
            return updated.to_dict() if hasattr(updated, "to_dict") else updated.__dict__
        raise ValuAdisException("Valuation not found or unauthorized")

    def delete_valuation(self, valuation_id: int, user_id: int) -> bool:
        valuation = self.valuation_repo.get_valuation_by_id_and_user(valuation_id, user_id)
        if valuation:
            self.db.delete(valuation)
            self.db.commit()
            return True
        return False

    # ------------------------------------------------------------------
    # Status transition
    # ------------------------------------------------------------------

    # Valid state machine transitions
    VALID_TRANSITIONS = {
        "draft": ["pending"],
        "pending": ["approved", "rejected"],
        "approved": ["archived"],
        "rejected": [],
        "archived": [],
        "expired": [],
    }

    def transition_status(
        self, valuation_id: int, new_status: str, actor_user_id: int, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transition a valuation to a new status following the defined state machine.

        Allowed transitions:
            draft     → pending
            pending   → approved | rejected
            approved  → archived

        Args:
            valuation_id:   ID of the valuation to transition
            new_status:     Target status string (draft/pending/approved/archived/rejected)
            actor_user_id:  ID of the user performing the transition
            reason:         Optional reason/note for the transition (stored in audit log)

        Returns:
            Updated valuation dict

        Raises:
            ValuAdisException: If valuation not found or transition is invalid
        """
        from app.data.models.valuation import ValuationStatus

        valuation = self.valuation_repo.get_valuation_by_id(valuation_id)
        if not valuation:
            raise ValuAdisException(f"Valuation {valuation_id} not found")

        current_status = (
            valuation.status.value
            if hasattr(valuation.status, "value")
            else str(valuation.status)
        )

        allowed = self.VALID_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise ValuAdisException(
                f"Invalid transition: '{current_status}' → '{new_status}'. "
                f"Allowed: {allowed if allowed else 'no transitions allowed from this status'}"
            )

        # Validate new_status is a valid enum value
        try:
            target_status = ValuationStatus(new_status)
        except ValueError:
            raise ValuAdisException(f"Unknown status value: '{new_status}'")

        updated = self.valuation_repo.update(valuation, {"status": target_status})
        self.db.commit()

        logger.info(
            "Valuation status transitioned",
            valuation_id=valuation_id,
            from_status=current_status,
            to_status=new_status,
            actor_user_id=actor_user_id,
            reason=reason,
        )

        return updated.to_dict() if hasattr(updated, "to_dict") else {
            "id": updated.id,
            "status": updated.status.value if hasattr(updated.status, "value") else str(updated.status),
        }

    def override_valuation(
        self,
        valuation_id: int,
        market_value: float,
        taxable_value: Optional[float],
        override_reason: Optional[str],
    ) -> Dict[str, Any]:
        """
        Override market_value and taxable_value (admin/senior valuer only).
        taxable_value defaults to 25% of market_value if not provided.
        """
        valuation = self.valuation_repo.get_valuation_by_id(valuation_id)
        if not valuation:
            raise ValuAdisException("Valuation not found")

        from decimal import Decimal
        mv = Decimal(str(market_value))
        tv = Decimal(str(taxable_value)) if taxable_value is not None else self.calculate_taxable_value(mv)

        updates = {"market_value": float(mv), "taxable_value": float(tv)}
        updated = self.valuation_repo.update(valuation, updates)
        return updated.to_dict() if hasattr(updated, "to_dict") else {
            "id": updated.id,
            "property_id": updated.property_id,
            "market_value": updated.market_value,
            "taxable_value": updated.taxable_value,
            "status": updated.status.value if hasattr(updated.status, "value") else str(updated.status),
        }

    # ------------------------------------------------------------------
    # Rent valuation (Phase A — plans/valuadis-rentals/plan.mdx)
    #
    # Suggested rent blends: (a) the ratio method — market value × a
    # district rent-to-price ratio, (b) direct comps — median asking rent
    # of comparable rental listings, and (c) a trend adjustment. The pure
    # math lives in small testable methods with no DB/network access;
    # get_rent_valuation() is the only method that touches the database,
    # to fetch the district ratio, comps, and trend inputs.
    # ------------------------------------------------------------------

    def calculate_rent_from_ratio(self, market_value: Decimal, ratio: Decimal) -> Decimal:
        """Ratio method: suggested monthly rent = market_value × district ratio."""
        return (market_value * ratio).quantize(Decimal("0.01"))

    def calculate_rent_from_comps(self, comp_rents: List[Decimal]) -> Optional[Decimal]:
        """Direct comps method: median asking rent of comparable listings."""
        if not comp_rents:
            return None
        return Decimal(str(median(comp_rents))).quantize(Decimal("0.01"))

    def apply_rent_trend_adjustment(self, base_rent: Decimal, trend_pct: Decimal) -> Decimal:
        """
        Apply a period-over-period trend percentage to the blended rent
        estimate, capped at RENT_MAX_TREND_ADJUSTMENT in either direction.
        """
        capped = max(-self.RENT_MAX_TREND_ADJUSTMENT, min(self.RENT_MAX_TREND_ADJUSTMENT, trend_pct))
        return (base_rent * (Decimal("1") + capped)).quantize(Decimal("0.01"))

    def blend_rent_estimates(
        self,
        ratio_estimate: Optional[Decimal],
        comps_estimate: Optional[Decimal],
        comp_count: int,
    ) -> Tuple[Decimal, Decimal]:
        """
        Blend the ratio-method and comps-method estimates into a single
        suggested rent plus a 0..1 confidence score.

        - Both methods present: simple average, confidence starts high.
        - Only one method present: use it, confidence starts lower.
        - Neither present: caller error — at least the ratio method must
          always be available (every district has a ratio, real or
          fallback).
        """
        if ratio_estimate is None and comps_estimate is None:
            raise PropertyValidationError("At least one rent estimate method must produce a value")

        if ratio_estimate is not None and comps_estimate is not None:
            blended = ((ratio_estimate + comps_estimate) / Decimal("2")).quantize(Decimal("0.01"))
            base_confidence = self.RENT_CONFIDENCE_BASE_BOTH_METHODS
        elif comps_estimate is not None:
            blended = comps_estimate
            base_confidence = self.RENT_CONFIDENCE_BASE_COMPS_ONLY
        else:
            blended = ratio_estimate
            base_confidence = self.RENT_CONFIDENCE_BASE_RATIO_ONLY

        comp_weight = min(
            Decimal(comp_count) / Decimal(self.RENT_COMPS_FOR_FULL_CONFIDENCE),
            Decimal("1"),
        ) * self.RENT_CONFIDENCE_COMP_COUNT_WEIGHT
        confidence = min(base_confidence + comp_weight, Decimal("1")).quantize(Decimal("0.01"))

        return blended, confidence

    def calculate_rent_band(self, suggested_rent: Decimal) -> Tuple[Decimal, Decimal]:
        """Published band = suggested rent ± RENT_BAND_PCT."""
        band_min = (suggested_rent * (Decimal("1") - self.RENT_BAND_PCT)).quantize(Decimal("0.01"))
        band_max = (suggested_rent * (Decimal("1") + self.RENT_BAND_PCT)).quantize(Decimal("0.01"))
        return band_min, band_max

    def calculate_rent_valuation(
        self,
        market_value: Decimal,
        ratio: Decimal,
        comp_rents: List[Decimal],
        trend_pct: Decimal = Decimal("0"),
    ) -> Dict[str, Any]:
        """
        Pure orchestrator: given a market value, a district ratio, a list
        of comparable rents, and a trend percentage, compute the full rent
        valuation result. No DB or network access — safe to unit test with
        plain Decimal inputs.
        """
        ratio_estimate = self.calculate_rent_from_ratio(market_value, ratio)
        comps_estimate = self.calculate_rent_from_comps(comp_rents)
        blended, confidence = self.blend_rent_estimates(ratio_estimate, comps_estimate, len(comp_rents))
        suggested_rent = self.apply_rent_trend_adjustment(blended, trend_pct)
        band_min, band_max = self.calculate_rent_band(suggested_rent)
        requires_officer_review = confidence < self.RENT_CONFIDENCE_FLOOR

        return {
            "suggested_rent": float(suggested_rent),
            "band_min": float(band_min),
            "band_max": float(band_max),
            "confidence": float(confidence),
            "requires_officer_review": requires_officer_review,
            "comp_count": len(comp_rents),
            "ratio_estimate": float(ratio_estimate),
            "comps_estimate": float(comps_estimate) if comps_estimate is not None else None,
        }

    def get_rent_valuation(
        self, property_data: Dict[str, Any], market_value: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        DB-backed rent valuation for a property: resolves the district
        ratio, comparable rents, and trend from the database (falling back
        to conservative defaults when no DB session is available), then
        delegates to the pure calculate_rent_valuation() for the math.
        """
        if market_value is None:
            market_value = self.calculate_market_value(property_data)

        municipality = property_data["municipality"]
        ratio = self._get_district_rent_ratio(municipality)
        comp_rents = self._get_comparable_rents(property_data)
        trend_pct = self._calculate_rent_trend_pct(municipality)

        result = self.calculate_rent_valuation(market_value, ratio, comp_rents, trend_pct)
        result["base_market_value"] = float(market_value)
        result["district_ratio"] = float(ratio)
        return result

    def _get_district_rent_ratio(self, municipality: str) -> Decimal:
        """Look up the seeded rent-to-price ratio for a district, or fall back."""
        if self.db is not None:
            from app.data.models.district_rent_ratio import DistrictRentRatio

            row = (
                self.db.query(DistrictRentRatio)
                .filter(DistrictRentRatio.district == municipality)
                .first()
            )
            if row is not None:
                return Decimal(str(row.monthly_rent_to_price_ratio))
        return self.RENT_RATIO_CITYWIDE_FALLBACK

    def _get_comparable_rents(self, property_data: Dict[str, Any], limit: int = 50) -> List[Decimal]:
        """
        Median-comps input: asking rents from raw_market_listings rows
        tagged listing_type='rent' in the same district/subtype. Returns
        an empty list (not an error) when no such rows exist yet — the
        scraper does not populate rent-tagged rows until a later phase,
        so the confidence score correctly stays low via blend_rent_estimates
        until real comps exist.
        """
        if self.db is None:
            return []

        from app.data.models.market_listing import RawMarketListing

        query = self.db.query(RawMarketListing).filter(
            RawMarketListing.listing_type == "rent",
            RawMarketListing.asking_price_etb.isnot(None),
            RawMarketListing.asking_price_etb > 0,
        )

        municipality = property_data.get("municipality")
        if municipality:
            query = query.filter(RawMarketListing.location_subcity.ilike(f"%{municipality}%"))

        property_type = property_data.get("property_type")
        if property_type:
            query = query.filter(RawMarketListing.property_type == property_type)

        rows = query.order_by(RawMarketListing.scrape_date.desc()).limit(limit).all()
        return [Decimal(str(row.asking_price_etb)) for row in rows]

    def _calculate_rent_trend_pct(self, municipality: str) -> Decimal:
        """
        Period-over-period trend, mirroring the growth-rate pattern used
        by the analytics trends endpoint (app/modules/analytics/routes.py):
        compare the average market_value of the earliest and latest
        calendar-month cohorts of historical valuations for the district.
        Capped at RENT_MAX_TREND_ADJUSTMENT. Returns 0 with insufficient
        history or no DB session.
        """
        if self.db is None:
            return Decimal("0")

        from app.data.models.valuation import Valuation

        rows = (
            self.db.query(Valuation.valuation_date, Valuation.market_value)
            .filter(Valuation.municipality == municipality, Valuation.market_value.isnot(None))
            .order_by(Valuation.valuation_date.asc())
            .all()
        )

        monthly: Dict[Tuple[int, int], List[Decimal]] = {}
        for valuation_date, market_value in rows:
            if not valuation_date:
                continue
            key = (valuation_date.year, valuation_date.month)
            monthly.setdefault(key, []).append(Decimal(str(market_value)))

        if len(monthly) < 2:
            return Decimal("0")

        periods = sorted(monthly.keys())
        first_values = monthly[periods[0]]
        last_values = monthly[periods[-1]]
        first_avg = sum(first_values) / Decimal(len(first_values))
        last_avg = sum(last_values) / Decimal(len(last_values))

        if first_avg <= 0:
            return Decimal("0")

        raw_pct = (last_avg - first_avg) / first_avg
        return max(-self.RENT_MAX_TREND_ADJUSTMENT, min(self.RENT_MAX_TREND_ADJUSTMENT, raw_pct))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _calculate_depreciation(self, construction_year: Optional[int]) -> Decimal:
        """Straight-line depreciation from construction year, capped at 50%."""
        if not construction_year:
            return Decimal("0")
        from datetime import date
        age = max(0, date.today().year - construction_year)
        depreciation = min(
            self._annual_depreciation * Decimal(str(age)),
            self._max_depreciation,
        )
        return depreciation

    def _validate_property_data(self, property_data: Dict[str, Any]) -> None:
        """Validate property data meets Ethiopian standards."""
        for field in ("municipality", "area_sqm"):
            if field not in property_data:
                raise PropertyValidationError(f"Missing required field: {field}")

        municipality = property_data["municipality"]
        if not isinstance(municipality, str) or len(municipality.strip()) < 2:
            raise PropertyValidationError("Municipality must be a valid string")

        area_sqm = property_data["area_sqm"]
        try:
            area_decimal = Decimal(str(area_sqm))
            if area_decimal <= 0:
                raise PropertyValidationError("Area must be greater than 0")
            if area_decimal > 100000:
                raise PropertyValidationError("Area exceeds maximum allowed size (100 000 sqm)")
        except (InvalidOperation, ValueError, TypeError) as e:
            raise PropertyValidationError("Invalid area value") from e

        condition = property_data.get("condition", "good")
        if condition not in self._condition_factors:
            valid = ", ".join(self._condition_factors.keys())
            raise PropertyValidationError(f"Invalid condition '{condition}'. Must be one of: {valid}")

        neighborhood = property_data.get("neighborhood_quality", "average")
        if neighborhood not in self._neighborhood_multipliers:
            valid = ", ".join(self._neighborhood_multipliers.keys())
            raise PropertyValidationError(
                f"Invalid neighborhood_quality '{neighborhood}'. Must be one of: {valid}"
            )

        if "coordinates" in property_data:
            coordinates = property_data["coordinates"]
            if not self._spatial_service.validate_polygon(coordinates):
                raise PropertyValidationError(
                    "Coordinates must form a valid closed polygon (≥ 4 points, first == last)"
                )
            if not self._spatial_service.validate_ethiopian_coordinates(coordinates):
                raise PropertyValidationError("Coordinates must be within Ethiopia")
