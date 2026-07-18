"""
Contract Number Concurrency Test (Phase C)

The registry contract number must be unique and never reused even under
concurrent creation. This spins up real threads with independent DB
sessions, each allocating a number and inserting a contract, and asserts the
numbers are unique, contiguous, and exactly N — proving the per-year
sequence + unique-constraint-with-retry allocator is race-safe.
"""

import os
import tempfile
import threading
from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.data.models.tenancy_contract import RentalContractSequence, TenancyContract
from app.modules.rentals.contract_service import TenancyContractService

THREADS = 20


@pytest.fixture
def concurrent_sessionmaker():
    tmp_dir = tempfile.mkdtemp(prefix="valuadis-concurrency-")
    db_path = os.path.join(tmp_dir, "concurrency.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _busy_timeout(dbapi_connection, _):
        # Writers wait instead of failing immediately on the DB-level lock, so
        # the retry loop only re-runs on genuine unique-constraint races.
        dbapi_connection.execute("PRAGMA busy_timeout = 30000")

    # Only the two tables the allocator touches; TenancyContract's FKs to
    # other tables are fine to leave dangling on SQLite (FK enforcement off).
    RentalContractSequence.__table__.create(bind=engine)
    TenancyContract.__table__.create(bind=engine)

    Session = sessionmaker(bind=engine)
    yield Session
    engine.dispose()


def test_parallel_contract_creation_yields_unique_contiguous_numbers(concurrent_sessionmaker):
    results: list = []
    errors: list = []
    barrier = threading.Barrier(THREADS)

    def worker(index: int):
        session = concurrent_sessionmaker()
        try:
            barrier.wait()  # maximise contention: all threads allocate at once
            service = TenancyContractService(session)
            application = SimpleNamespace(id=index + 1, listing_id=index + 1)
            contract = service._insert_with_contract_no(
                application=application,
                monthly_rent=10000.0,
                start_date=date(2026, 8, 1),
                end_date=date(2027, 8, 1),
                deposit_amount=20000.0,
            )
            results.append(contract.contract_no)
        except Exception as exc:  # noqa: BLE001 - surfaced via the errors list
            errors.append(repr(exc))
        finally:
            session.close()

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"workers raised: {errors}"
    assert len(results) == THREADS
    # No duplicates.
    assert len(set(results)) == THREADS
    # Contiguous 1..N sequence — proves no gaps and no reuse.
    seqs = sorted(int(no.split("-")[-1]) for no in results)
    assert seqs == list(range(1, THREADS + 1))
