"""
Performance utility tests for deterministic thresholds and metric capture.
"""

import os
import time

from app.core.performance import DatabaseOptimizer, get_performance_metrics, track_performance


def test_slow_query_threshold_uses_env_override(monkeypatch):
    monkeypatch.setenv("SLOW_QUERY_THRESHOLD", "250")

    assert DatabaseOptimizer.get_slow_query_threshold() == 250


def test_slow_query_threshold_defaults_when_env_missing(monkeypatch):
    monkeypatch.delenv("SLOW_QUERY_THRESHOLD", raising=False)

    assert DatabaseOptimizer.get_slow_query_threshold() == 1000


def test_track_performance_records_execution_time():
    @track_performance("test_performance_probe")
    def _probe():
        time.sleep(0.001)

    before = get_performance_metrics().get("test_performance_probe_duration", {})
    before_count = before.get("count", 0)

    _probe()

    after = get_performance_metrics()["test_performance_probe_duration"]
    assert after["count"] == before_count + 1
    assert after["avg"] >= 0
