"""Audit-log retention job tests."""

from datetime import datetime, timedelta

import pytest

from app.data.models.audit_log import AuditLog
from app.services.audit_retention import purge_expired_audit_logs


def _add_log(db, days_ago: int):
    db.add(AuditLog(
        table_name="properties", record_id=1, action="UPDATE",
        timestamp=datetime.utcnow() - timedelta(days=days_ago),
    ))


def test_purges_only_logs_older_than_retention(db_session):
    _add_log(db_session, days_ago=800)   # expired (>730)
    _add_log(db_session, days_ago=900)   # expired
    _add_log(db_session, days_ago=10)    # fresh
    db_session.commit()

    deleted = purge_expired_audit_logs(db_session, retention_days=730)

    assert deleted == 2
    assert db_session.query(AuditLog).count() == 1


def test_keeps_everything_when_all_within_window(db_session):
    _add_log(db_session, days_ago=5)
    _add_log(db_session, days_ago=100)
    db_session.commit()

    deleted = purge_expired_audit_logs(db_session, retention_days=730)

    assert deleted == 0
    assert db_session.query(AuditLog).count() == 2


def test_rejects_non_positive_retention(db_session):
    with pytest.raises(ValueError):
        purge_expired_audit_logs(db_session, retention_days=0)
