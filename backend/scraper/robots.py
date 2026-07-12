"""
robots.txt politeness for the scraper worker.

`is_path_allowed` is a pure decision over robots.txt text (unit-testable with
fixtures); `fetch_robots_txt` retrieves it over HTTP. Policy: if robots.txt
cannot be retrieved, default to allowed but let the caller log it — an
unreachable robots file must not silently disable a configured target.
"""

import logging
from typing import Optional
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

logger = logging.getLogger("ValuAdis_Scraper")

DEFAULT_TIMEOUT_SECONDS = 10.0


def is_path_allowed(robots_txt: str, user_agent: str, url: str) -> bool:
    """Return whether `user_agent` may fetch `url` under the given robots.txt."""
    parser = RobotFileParser()
    parser.parse(robots_txt.splitlines())
    path = urlsplit(url).path or "/"
    return parser.can_fetch(user_agent, path)


def robots_url_for(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}/robots.txt"


def fetch_robots_txt(url: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> Optional[str]:
    """Fetch robots.txt for the host of `url`; None if unreachable.

    Uses httpx when available, falling back to urllib so the worker has no
    hard new dependency.
    """
    robots_url = robots_url_for(url)
    try:
        import httpx

        response = httpx.get(robots_url, timeout=timeout, follow_redirects=True)
        if response.status_code >= 400:
            return None
        return response.text
    except ImportError:
        pass
    except Exception as error:  # network error, DNS, timeout
        logger.warning(f"robots.txt fetch failed for {robots_url}: {error}")
        return None

    try:
        from urllib.request import urlopen

        with urlopen(robots_url, timeout=timeout) as handle:  # noqa: S310 (trusted target host)
            return handle.read().decode("utf-8", errors="replace")
    except Exception as error:
        logger.warning(f"robots.txt fetch failed for {robots_url}: {error}")
        return None
