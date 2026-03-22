"""Valuation status transition service"""

from sqlalchemy.orm import Session
from app.data.models.vehicle_valuation import VehicleValuation, VehicleValuationStatus
import logging

logger = logging.getLogger(__name__)


class ValuationStatusService:
    """Handle valuation status transitions"""

    VALID_TRANSITIONS = {
        'draft': ['pending'],
        'pending': ['approved'],
        'approved': ['archived'],
        'archived': []
    }

    def transition_status(self, valuation_id: int, new_status: str, db: Session) -> VehicleValuation:
        """Transition valuation to new status"""
        valuation = db.query(VehicleValuation).filter(VehicleValuation.id == valuation_id).first()
        if not valuation:
            raise ValueError(f"Valuation {valuation_id} not found")

        current = valuation.status.value if hasattr(valuation.status, 'value') else str(valuation.status)

        if new_status not in self.VALID_TRANSITIONS.get(current, []):
            raise ValueError(f"Invalid transition from {current} to {new_status}")

        valuation.status = VehicleValuationStatus(new_status)
        db.commit()
        logger.info(f"Valuation {valuation_id}: {current} → {new_status}")
        return valuation


valuation_status_service = ValuationStatusService()
