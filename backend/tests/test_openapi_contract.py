"""Frozen /api/v1 contract gate for the v2 strangler refactor.

The snapshot in tests/contract/openapi_v1_snapshot.json is the v1 API
surface as of the v1-baseline tag. Module extractions must not remove or
change existing operations; additions are allowed. Regenerate the
snapshot only for an intentional, reviewed contract change.
"""

import json
from pathlib import Path

from app.main import app

SNAPSHOT_PATH = Path(__file__).parent / "contract" / "openapi_v1_snapshot.json"


def _load_snapshot() -> dict:
    with SNAPSHOT_PATH.open() as f:
        return json.load(f)


def test_no_operation_removed_from_v1_contract():
    snapshot = _load_snapshot()
    current = app.openapi()

    missing = []
    for path, methods in snapshot["paths"].items():
        current_methods = current["paths"].get(path)
        if current_methods is None:
            missing.append(path)
            continue
        for method in methods:
            if method not in current_methods:
                missing.append(f"{method.upper()} {path}")

    assert not missing, (
        "Breaking change: operations present in the frozen v1 snapshot are "
        f"missing from the live schema: {missing}"
    )


def test_no_success_response_dropped():
    snapshot = _load_snapshot()
    current = app.openapi()

    dropped = []
    for path, methods in snapshot["paths"].items():
        for method, op in methods.items():
            current_op = current["paths"].get(path, {}).get(method)
            if current_op is None:
                continue  # covered by the removal test
            snap_success = {s for s in op.get("responses", {}) if s.startswith("2")}
            curr_success = {s for s in current_op.get("responses", {}) if s.startswith("2")}
            for status in snap_success - curr_success:
                dropped.append(f"{method.upper()} {path} -> {status}")

    assert not dropped, f"Breaking change: success responses dropped: {dropped}"
