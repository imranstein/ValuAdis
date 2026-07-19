"""
Audit-log retention (S13).

Deletes audit_logs older than the retention window. Run on a schedule
(cron / the scraper-worker-style loop) via `python -m app.services.audit_retention`.
Kept as a plain service function so it is unit-testable without a scheduler.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.data.models.audit_log import AuditLog

logger = logging.getLogger("ValuAdis_AuditRetention")

# ponytail: single knob via env; default two years of audit history.
DEFAULT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "730"))


def purge_expired_audit_logs(db: Session, retention_days: int = DEFAULT_RETENTION_DAYS,
                             now: Optional[datetime] = None) -> int:
    """Delete audit_logs older than retention_days. Returns the count removed.

    `now` is injectable so the cutoff is testable without real time.
    """
    if retention_days <= 0:
        raise ValueError("retention_days must be positive")
    reference = now or datetime.utcnow()
    cutoff = reference - timedelta(days=retention_days)
    deleted = (
        db.query(AuditLog)
        .filter(AuditLog.timestamp < cutoff)
        .delete(synchronize_session=False)
    )
    db.commit()
    logger.info("audit retention: deleted %s logs older than %s", deleted, cutoff.date())
    return deleted


def main() -> None:  # pragma: no cover - thin runner
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        purge_expired_audit_logs(db)
    finally:
        db.close()


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    main()
