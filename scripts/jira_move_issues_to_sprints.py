#!/usr/bin/env python3
"""
Move VALU issues to their sprints via Jira Agile REST API.
Board view only updates when issues are moved with this API (not just customfield_10020).

Usage:
  export JIRA_URL="https://imransteina.atlassian.net"
  export JIRA_USERNAME="your-email@example.com"
  export JIRA_API_TOKEN="your-api-token"
  python scripts/jira_move_issues_to_sprints.py
"""
import os
import urllib.request
import urllib.error
import json

JIRA_URL = os.environ.get("JIRA_URL", "").rstrip("/")
JIRA_USERNAME = os.environ.get("JIRA_USERNAME", "")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN", "")

# Sprint ID -> list of issue keys (from our earlier assignment)
SPRINT_ISSUES = {
    9: ["SCRUM-77"],                    # VALU S1: Doc & foundation
    8: ["SCRUM-78", "SCRUM-116", "SCRUM-117"],  # VALU S2: Backend & API
    10: ["SCRUM-79"],                   # VALU S3: Frontend & dashboard
    12: ["SCRUM-80", "SCRUM-81"],       # VALU S4: Integration & test
    11: ["SCRUM-82"],                   # VALU S5: QA handoff
}


def move_issues_to_sprint(sprint_id: int, issue_keys: list[str]) -> None:
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = json.dumps({"issues": issue_keys}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    req.add_header(
        "Authorization",
        "Basic "
        + __import__("base64").b64encode(f"{JIRA_USERNAME}:{JIRA_API_TOKEN}".encode()).decode(),
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 204):
                print(f"  Sprint {sprint_id}: moved {issue_keys}")
            else:
                print(f"  Sprint {sprint_id}: unexpected status {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"  Sprint {sprint_id}: HTTP {e.code} - {body}")
    except Exception as e:
        print(f"  Sprint {sprint_id}: error - {e}")


def main() -> None:
    if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
        print("Set JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN in the environment.")
        return
    print("Moving VALU issues to sprints (Agile API)...")
    for sprint_id, keys in SPRINT_ISSUES.items():
        if keys:
            move_issues_to_sprint(sprint_id, keys)
    print("Done. Refresh your Scrum board.")


if __name__ == "__main__":
    main()
