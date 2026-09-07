import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.github_client import GitHubClient


REPOSITORIES_FILE = "data/raw/repositories.csv"
OUTPUT_FILE = "data/historical/repository_collaboration_monthly.csv"

MVP_SIZE = 20
RANDOM_STATE = 42


def get_month(timestamp):
    """Convert GitHub timestamp to YYYY-MM."""
    return pd.to_datetime(
        timestamp,
        utc=True
    ).strftime("%Y-%m")


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
    Collect all issues for a repository.

    GitHub's issues endpoint also returns pull requests,
    so pull requests are filtered out later.
    """

    return client.get_all_cursor(
        f"/repos/{repo}/issues",
        params={
            "state": "all",
            "sort": "created",
            "direction": "asc",
        },
    )


def build_monthly_rows(
    repo_info,
    pull_requests,
    issues
):
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

    # ---------------------------------------------------------
    # Pull requests
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Issues
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Continuous timeline
    # ---------------------------------------------------------

    repo_created = pd.to_datetime(
        repo_info["created_at"],
        utc=True,
    )

    start_month = pd.Timestamp(
        repo_created.year,
        repo_created.month,
        1,
    )

    # Latest COMPLETE month.
    now = pd.Timestamp.now(tz="UTC")

    current_month = pd.Timestamp(
        now.year,
        now.month,
        1,
    )

    end_month = (
        current_month
        - pd.offsets.MonthBegin(1)
    )

    all_months = pd.date_range(
        start=start_month,
        end=end_month,
        freq="MS",
    )

    rows = []

    for timestamp in all_months:

        month = timestamp.strftime("%Y-%m")

        ensure_month(month)

        rows.append(
            {
                "repo_id": repo_info["repo_id"],
                "full_name": repo_info["full_name"],
                "language": repo_info["language"],
                "month": month,
                **events[month],
            }
        )

    return rows


def save_results(results):
    """Save current progress safely."""

    if not results:
        return

    output = pd.DataFrame(results)

    output = (
        output
        .drop_duplicates(
            subset=["repo_id", "month"]
        )
        .sort_values(
            ["repo_id", "month"]
        )
        .reset_index(drop=True)
    )

    OUTPUT_PATH = Path(OUTPUT_FILE)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_file = OUTPUT_PATH.with_suffix(".tmp")

    output.to_csv(
        temp_file,
        index=False,
    )

    temp_file.replace(OUTPUT_PATH)


def main():

    print("=" * 70)
    print("OSSurvive - MVP Historical Collaboration Collection")
    print("=" * 70)

    repositories = pd.read_csv(
        REPOSITORIES_FILE
    )

    # ---------------------------------------------------------
    # Same deterministic 20-repository MVP sample
    # ---------------------------------------------------------

    repositories = (
        repositories
        .sample(
            n=min(
                MVP_SIZE,
                len(repositories)
            ),
            random_state=RANDOM_STATE,
        )
        .reset_index(drop=True)
    )

    print(
        f"\nMVP repositories: "
        f"{len(repositories)}"
    )

    print("\nRepositories:")

    for repo in repositories["full_name"]:

        print(
            f"- {repo}"
        )

    # ---------------------------------------------------------
    # Existing progress
    # ---------------------------------------------------------

    if Path(OUTPUT_FILE).exists():

        existing = pd.read_csv(
            OUTPUT_FILE
        )

        completed_repo_ids = set(
            existing["repo_id"].astype(int)
        )

        results = existing.to_dict(
            "records"
        )

        print(
            "\nExisting progress found:"
        )

        print(
            f"  Completed repositories: "
            f"{len(completed_repo_ids)}"
        )

        print(
            f"  Existing rows: "
            f"{len(existing)}"
        )

    else:

        completed_repo_ids = set()

        results = []

        print(
            "\nNo previous collaboration dataset found."
        )

    # ---------------------------------------------------------
    # GitHub client
    # ---------------------------------------------------------

    client = GitHubClient()

    # ---------------------------------------------------------
    # Collection
    # ---------------------------------------------------------

    for index, (_, repo_info) in enumerate(
        repositories.iterrows(),
        start=1,
    ):

        repo_id = int(
            repo_info["repo_id"]
        )

        repo = repo_info["full_name"]

        if repo_id in completed_repo_ids:

            print(
                f"\n[{index}/{len(repositories)}] "
                f"SKIP {repo} "
                f"(already collected)"
            )

            continue

        print(
            f"\n[{index}/{len(repositories)}] "
            f"Collecting collaboration history: "
            f"{repo}"
        )

        try:

            # -------------------------------------------------
            # Pull requests
            # -------------------------------------------------

            pull_requests = (
                collect_pull_requests(
                    client,
                    repo,
                )
            )

            print(
                f"  Pull requests: "
                f"{len(pull_requests)}"
            )

            # -------------------------------------------------
            # Issues
            # -------------------------------------------------

            issues_with_prs = (
                collect_issues(
                    client,
                    repo,
                )
            )

            issues = [
                item
                for item in issues_with_prs
                if "pull_request" not in item
            ]

            print(
                f"  Issues: "
                f"{len(issues)}"
            )

            # -------------------------------------------------
            # Monthly reconstruction
            # -------------------------------------------------

            rows = build_monthly_rows(
                repo_info,
                pull_requests,
                issues,
            )

            print(
                f"  Monthly rows: "
                f"{len(rows)}"
            )

            results.extend(rows)

            completed_repo_ids.add(
                repo_id
            )

            # Save immediately.
            save_results(results)

            print(
                f"  Progress: "
                f"{len(completed_repo_ids)}/"
                f"{len(repositories)}"
            )

        except Exception as error:

            print(
                f"  ERROR: {error}"
            )

            print(
                "  Skipping repository and "
                "continuing safely."
            )

            continue

    # ---------------------------------------------------------
    # Final dataset
    # ---------------------------------------------------------

    if not results:

        raise RuntimeError(
            "No collaboration data collected."
        )

    output = pd.DataFrame(
        results
    )

    output = (
        output
        .drop_duplicates(
            subset=["repo_id", "month"]
        )
        .sort_values(
            ["repo_id", "month"]
        )
        .reset_index(drop=True)
    )

    output.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\n" + "=" * 70)
    print("COLLABORATION COLLECTION COMPLETE")
    print("=" * 70)

    print(
        f"\nRepositories: "
        f"{output['repo_id'].nunique()}"
    )

    print(
        f"Rows: "
        f"{len(output)}"
    )

    print("\nTotals:")

    print(
        f"PRs opened: "
        f"{output['pr_opened'].sum()}"
    )

    print(
        f"PRs closed: "
        f"{output['pr_closed'].sum()}"
    )

    print(
        f"PRs merged: "
        f"{output['pr_merged'].sum()}"
    )

    print(
        f"Issues opened: "
        f"{output['issues_opened'].sum()}"
    )

    print(
        f"Issues closed: "
        f"{output['issues_closed'].sum()}"
    )

    print(
        f"\nDate range: "
        f"{output['month'].min()} → "
        f"{output['month'].max()}"
    )

    print(
        f"\nSaved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()