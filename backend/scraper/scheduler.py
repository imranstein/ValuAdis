"""
Scraper worker scheduler.

Long-running worker process that runs enabled ScraperTarget rows on their
`schedule` via the existing ScraperRunner. It has no API surface: start it
with `python scraper/scheduler.py` (or the docker-compose `scraper-worker`
service).

Schedule format (the ScraperTarget.schedule column, one of):

- "daily@HH:MM"  run once per day at HH:MM UTC (e.g. "daily@02:30").
- "every:Nh"     run every N whole hours (e.g. "every:6h").
- "daily"        legacy seed value, treated as "daily@02:00".

Any other value falls back to the default daily run at 02:00 UTC and logs
a warning, so a bad schedule never disables a target silently.

Behavior guarantees:

- Due targets run sequentially, never two concurrently, with a stagger
  delay between consecutive runs.
- An individual run failure is logged and the worker moves on; the loop
  itself never dies because one target failed.
- Due-ness is computed from ScraperTarget.last_run, which ScraperRunner
  updates in a terminal state on every run (success or failure), so a
  failing target is retried on its next scheduled slot, not in a hot loop.
"""

import asyncio
import logging
import os
import re
import sys
from datetime import datetime, time, timedelta
from typing import Callable, List, NamedTuple, Optional, Tuple, Union

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.data.models.scraper import ScraperTarget

from scraper.run_scraper import DEFAULT_MAX_PAGES, ScraperRunner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("ValuAdis_Scheduler")

DEFAULT_DAILY_TIME = time(2, 0)
POLL_INTERVAL_SECONDS = 60
STAGGER_SECONDS = 30

_DAILY_AT_PATTERN = re.compile(r"^daily@(\d{1,2}):(\d{2})$")
_EVERY_HOURS_PATTERN = re.compile(r"^every:(\d+)h$")

ScheduleValue = Union[time, timedelta]


class DueTarget(NamedTuple):
    """Plain snapshot of a ScraperTarget so runs never touch a closed session."""

    id: int
    domain: str
    max_pages: int


def parse_schedule(text: Optional[str]) -> Tuple[str, ScheduleValue]:
    """Parse a schedule string into ("daily", time) or ("interval", timedelta)."""
    normalized = (text or "").strip().lower()
    if normalized == "daily":
        return ("daily", DEFAULT_DAILY_TIME)

    daily_match = _DAILY_AT_PATTERN.match(normalized)
    if daily_match:
        hour, minute = int(daily_match.group(1)), int(daily_match.group(2))
        if hour < 24 and minute < 60:
            return ("daily", time(hour, minute))

    interval_match = _EVERY_HOURS_PATTERN.match(normalized)
    if interval_match and int(interval_match.group(1)) > 0:
        return ("interval", timedelta(hours=int(interval_match.group(1))))

    logger.warning(
        f"Unrecognized schedule {text!r}; falling back to daily@"
        f"{DEFAULT_DAILY_TIME.strftime('%H:%M')} UTC"
    )
    return ("daily", DEFAULT_DAILY_TIME)


def _as_naive_utc(value: Optional[datetime]) -> Optional[datetime]:
    """Normalize aware timestamps (Postgres) and naive ones (SQLite) to naive UTC."""
    if value is None or value.tzinfo is None:
        return value
    return value.replace(tzinfo=None)


def is_due(
    schedule_text: Optional[str],
    last_run: Optional[datetime],
    now: datetime,
) -> bool:
    """Decide whether a target should run at `now` given its last run."""
    kind, value = parse_schedule(schedule_text)
    last_run = _as_naive_utc(last_run)
    now = _as_naive_utc(now)

    if kind == "interval":
        return last_run is None or now - last_run >= value

    todays_slot = datetime.combine(now.date(), value)
    if now < todays_slot:
        return False
    return last_run is None or last_run < todays_slot


class ScraperScheduler:
    """Sequential scheduler over enabled ScraperTarget rows.

    `clock`, `sleep`, `session_factory`, and `run_target` are injectable so
    the due-scheduling logic is unit-testable without real time, network,
    or Playwright.
    """

    def __init__(
        self,
        session_factory: Callable = SessionLocal,
        run_target: Optional[Callable] = None,
        clock: Callable[[], datetime] = datetime.utcnow,
        sleep: Callable = asyncio.sleep,
        stagger_seconds: float = STAGGER_SECONDS,
        poll_interval_seconds: float = POLL_INTERVAL_SECONDS,
    ):
        self.session_factory = session_factory
        self.run_target = run_target or self._run_with_scraper_runner
        self.clock = clock
        self.sleep = sleep
        self.stagger_seconds = stagger_seconds
        self.poll_interval_seconds = poll_interval_seconds

    async def _run_with_scraper_runner(self, target: DueTarget) -> None:
        runner = ScraperRunner(
            scraper_id=target.id,
            max_pages=target.max_pages or DEFAULT_MAX_PAGES,
        )
        await runner.run_scraper()

    def get_due_targets(self, now: datetime) -> List[DueTarget]:
        """Snapshot enabled targets whose schedule makes them due at `now`."""
        db = self.session_factory()
        try:
            enabled = (
                db.query(ScraperTarget)
                .filter(ScraperTarget.enabled.is_(True))
                .order_by(ScraperTarget.id)
                .all()
            )
            return [
                DueTarget(id=target.id, domain=target.domain, max_pages=target.max_pages)
                for target in enabled
                if is_due(target.schedule, target.last_run, now)
            ]
        finally:
            db.close()

    async def run_pending(self) -> int:
        """Run every due target sequentially; failures are logged, not raised."""
        due_targets = self.get_due_targets(self.clock())
        for position, target in enumerate(due_targets):
            if position > 0:
                await self.sleep(self.stagger_seconds)
            logger.info(f"Running scheduled scrape for {target.domain} (id={target.id})")
            try:
                await self.run_target(target)
            except Exception as error:
                logger.error(f"Scheduled run failed for {target.domain}: {error}")
        return len(due_targets)

    async def run_forever(self) -> None:
        """Poll for due targets until the process is stopped."""
        logger.info(
            f"Scraper scheduler started (poll every {self.poll_interval_seconds}s, "
            f"stagger {self.stagger_seconds}s)"
        )
        while True:
            try:
                await self.run_pending()
            except Exception as error:
                logger.error(f"Scheduler poll failed: {error}")
            await self.sleep(self.poll_interval_seconds)


if __name__ == "__main__":
    asyncio.run(ScraperScheduler().run_forever())
