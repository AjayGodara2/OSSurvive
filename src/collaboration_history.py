import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.github_client import GitHubClient


REPOSITORIES_FILE = "data/raw/repositories.csv"
OUTPUT_FILE = "data/historical/repository_collaboration_monthly.csv"

PILOT_SIZE = 5
RANDOM_STATE = 42


def get_month(timestamp):
    """Convert GitHub timestamp to YYYY-MM."""
    return pd.to_datetime(timestamp, utc=True).strftime("%Y-%m")


def collect_pull_requests(client, repo):
    """Collect all pull requests for a repository."""
    return client.get_all(
        f"/repos/{repo}/pulls",
        params={
            "state": "all",
            "sort": "created",
            "direction": "asc",
        },
    )


def collect_issues(client, repo):
    """
    Collect issues from the repository issues endpoint.

    Pull requests are excluded because GitHub's issues endpoint
    also returns pull requests.
    """
    return client.get_all_cursor(
        f"/repos/{repo}/issues",
        params={
            "state": "all",
            "sort": "created",
            "direction": "asc",
        },
    )


def build_monthly_rows(repo_info, pull_requests, issues):
    """Convert PR and issue events into a continuous monthly timeline."""

    events = {}

    def ensure_month(month):
        if month not in events:
            events[month] = {
                "pr_opened": 0,
                "pr_closed": 0,
                "pr_merged": 0,
                "issues_opened": 0,
                "issues_closed": 0,
            }

    # Pull requests
    for pr in pull_requests:
        created_at = pr.get("created_at")
        closed_at = pr.get("closed_at")
        merged_at = pr.get("merged_at")

        if created_at:
            month = get_month(created_at)
            ensure_month(month)
            events[month]["pr_opened"] += 1

        if closed_at:
            month = get_month(closed_at)
            ensure_month(month)
            events[month]["pr_closed"] += 1

        if merged_at:
            month = get_month(merged_at)
            ensure_month(month)
            events[month]["pr_merged"] += 1

    # Issues
    for issue in issues:
        created_at = issue.get("created_at")
        closed_at = issue.get("closed_at")

        if created_at:
            month = get_month(created_at)
            ensure_month(month)
            events[month]["issues_opened"] += 1

        if closed_at:
            month = get_month(closed_at)
            ensure_month(month)
            events[month]["issues_closed"] += 1

    # --------------------------------------------------
    # Build continuous timeline
    # --------------------------------------------------

    repo_created = pd.to_datetime(
        repo_info["created_at"],
        utc=True
    )

    start_month = pd.Timestamp(
        repo_created.year,
        repo_created.month,
        1
    )

    current_month = pd.Timestamp(
        pd.Timestamp.now(tz="UTC").year,
        pd.Timestamp.now(tz="UTC").month,
        1
    )

    all_months = pd.date_range(
        start=start_month,
        end=current_month,
        freq="MS"
    )

    rows = []

    for timestamp in all_months:

        month = timestamp.strftime("%Y-%m")

        if month not in events:
            events[month] = {
                "pr_opened": 0,
                "pr_closed": 0,
                "pr_merged": 0,
                "issues_opened": 0,
                "issues_closed": 0,
            }

        row = {
            "repo_id": repo_info["repo_id"],
            "full_name": repo_info["full_name"],
            "language": repo_info["language"],
            "month": month,
            **events[month],
        }

        rows.append(row)

    return rows

def main():
    print("Starting collaboration history pilot...")

    repositories = pd.read_csv(REPOSITORIES_FILE)

    pilot = (
        repositories
        .sample(PILOT_SIZE, random_state=RANDOM_STATE)
        .reset_index(drop=True)
    )

    print("\nPilot repositories:")

    for repo in pilot["full_name"]:
        print(f"- {repo}")

    client = GitHubClient()

    all_rows = []

    for index, (_, repo_info) in enumerate(pilot.iterrows(), start=1):

        repo = repo_info["full_name"]

        print(
            f"\n[{index}/{len(pilot)}] "
            f"Collecting collaboration history: {repo}"
        )

        pull_requests = collect_pull_requests(client, repo)

        print(f"  Pull requests: {len(pull_requests)}")

        issues_with_prs = collect_issues(client, repo)

        issues = [
            item
            for item in issues_with_prs
            if "pull_request" not in item
        ]

        print(f"  Issues: {len(issues)}")

        rows = build_monthly_rows(
            repo_info,
            pull_requests,
            issues,
        )

        print(f"  Monthly rows: {len(rows)}")

        all_rows.extend(rows)

    output = pd.DataFrame(all_rows)

    output = output.sort_values(
        ["repo_id", "month"]
    ).reset_index(drop=True)

    output.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nCollaboration history pilot complete!")

    print(f"Repositories: {output['repo_id'].nunique()}")
    print(f"Rows: {len(output)}")

    print("\nTotals:")

    print(f"PRs opened: {output['pr_opened'].sum()}")
    print(f"PRs closed: {output['pr_closed'].sum()}")
    print(f"PRs merged: {output['pr_merged'].sum()}")
    print(f"Issues opened: {output['issues_opened'].sum()}")
    print(f"Issues closed: {output['issues_closed'].sum()}")

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()