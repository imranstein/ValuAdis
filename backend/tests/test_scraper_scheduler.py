"""
Scraper scheduler unit tests.

Exercises the due-scheduling logic with an injected clock, a stub session
factory, and a recording run_target — no real time, database, network, or
Playwright.
"""

from datetime import datetime, time, timedelta
from typing import List

import pytest

from scraper.scheduler import (
    DEFAULT_DAILY_TIME,
    DueTarget,
    ScraperScheduler,
    is_due,
    parse_schedule,
)


class _StubTarget:
    def __init__(self, id, domain, schedule, last_run, enabled=True, max_pages=1):
        self.id = id
        self.domain = domain
        self.schedule = schedule
        self.last_run = last_run
        self.enabled = enabled
        self.max_pages = max_pages


class _StubQuery:
    def __init__(self, rows):
        self._rows = rows

    def filter(self, *_):
        return self

    def order_by(self, *_):
        return self

    def all(self):
        return self._rows


class _StubSession:
    def __init__(self, rows):
        self._rows = rows
        self.closed = False

    def query(self, _model):
        return _StubQuery([r for r in self._rows if r.enabled])

    def close(self):
        self.closed = True


# --- parse_schedule -------------------------------------------------------

def test_parse_schedule_daily_at_specific_time():
    assert parse_schedule("daily@02:30") == ("daily", time(2, 30))


def test_parse_schedule_interval_hours():
    assert parse_schedule("every:6h") == ("interval", timedelta(hours=6))


def test_parse_schedule_legacy_daily_uses_default_time():
    assert parse_schedule("daily") == ("daily", DEFAULT_DAILY_TIME)


def test_parse_schedule_unknown_falls_back_to_daily_default():
    assert parse_schedule("garbage") == ("daily", DEFAULT_DAILY_TIME)


def test_parse_schedule_rejects_out_of_range_time():
    # 25:00 is invalid, so it must fall back rather than crash
    assert parse_schedule("daily@25:00") == ("daily", DEFAULT_DAILY_TIME)


# --- is_due ---------------------------------------------------------------

def test_daily_is_due_when_never_run_and_past_slot():
    now = datetime(2026, 7, 12, 3, 0)
    assert is_due("daily@02:00", None, now) is True


def test_daily_not_due_before_slot():
    now = datetime(2026, 7, 12, 1, 0)
    assert is_due("daily@02:00", None, now) is False


def test_daily_not_due_when_already_ran_today_after_slot():
    now = datetime(2026, 7, 12, 5, 0)
    last_run = datetime(2026, 7, 12, 2, 5)
    assert is_due("daily@02:00", last_run, now) is False


def test_daily_due_again_next_day():
    now = datetime(2026, 7, 13, 2, 1)
    last_run = datetime(2026, 7, 12, 2, 5)
    assert is_due("daily@02:00", last_run, now) is True


def test_interval_due_when_elapsed():
    now = datetime(2026, 7, 12, 12, 0)
    last_run = datetime(2026, 7, 12, 5, 0)
    assert is_due("every:6h", last_run, now) is True


def test_interval_not_due_before_elapsed():
    now = datetime(2026, 7, 12, 10, 0)
    last_run = datetime(2026, 7, 12, 5, 0)
    assert is_due("every:6h", last_run, now) is False


# --- get_due_targets ------------------------------------------------------

def test_get_due_targets_filters_by_schedule_and_enabled():
    now = datetime(2026, 7, 12, 3, 0)
    rows = [
        _StubTarget(1, "due.example", "daily@02:00", last_run=None),
        _StubTarget(2, "notyet.example", "daily@23:00", last_run=None),
        _StubTarget(3, "disabled.example", "daily@02:00", last_run=None, enabled=False),
    ]
    scheduler = ScraperScheduler(session_factory=lambda: _StubSession(rows))

    due = scheduler.get_due_targets(now)

    assert [t.id for t in due] == [1]


def test_get_due_targets_closes_the_session():
    session = _StubSession([])
    scheduler = ScraperScheduler(session_factory=lambda: session)
    scheduler.get_due_targets(datetime(2026, 7, 12, 3, 0))
    assert session.closed is True


# --- run_pending ----------------------------------------------------------

@pytest.mark.asyncio
async def test_run_pending_runs_each_due_target_once():
    ran: List[int] = []

    async def record(target):
        ran.append(target.id)

    async def no_sleep(_seconds):
        return None

    rows = [
        _StubTarget(1, "a.example", "daily@02:00", last_run=None),
        _StubTarget(2, "b.example", "every:1h", last_run=None),
    ]
    scheduler = ScraperScheduler(
        session_factory=lambda: _StubSession(rows),
        run_target=record,
        clock=lambda: datetime(2026, 7, 12, 3, 0),
        sleep=no_sleep,
    )

    count = await scheduler.run_pending()

    assert count == 2
    assert ran == [1, 2]


@pytest.mark.asyncio
async def test_run_pending_continues_after_a_target_fails():
    ran: List[int] = []

    async def record(target):
        if target.id == 1:
            raise RuntimeError("boom")
        ran.append(target.id)

    async def no_sleep(_seconds):
        return None

    rows = [
        _StubTarget(1, "boom.example", "every:1h", last_run=None),
        _StubTarget(2, "ok.example", "every:1h", last_run=None),
    ]
    scheduler = ScraperScheduler(
        session_factory=lambda: _StubSession(rows),
        run_target=record,
        clock=lambda: datetime(2026, 7, 12, 3, 0),
        sleep=no_sleep,
    )

    count = await scheduler.run_pending()

    # The failing target did not stop the second one from running.
    assert count == 2
    assert ran == [2]
