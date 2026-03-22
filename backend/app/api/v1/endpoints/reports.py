"""Reports API endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from io import BytesIO
import logging

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.report_generator import report_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/compliance")
async def generate_compliance_report(
    valuation_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Generate compliance report for a valuation"""
    try:
        pdf_content = report_generator.generate_compliance_report(valuation_id, db)

        return FileResponse(
            BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=compliance_report_{valuation_id}.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error generating compliance report"
        )
