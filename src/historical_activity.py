import time
from pathlib import Path

import pandas as pd

from src.github_client import GitHubClient


REPO_FILE = Path("data/raw/repositories.csv")
OUTPUT_FILE = Path("data/historical/repository_activity_monthly.csv")

PILOT_REPOS = 5


def get_months(start_date, end_date):
    """Generate month-start dates between two dates."""
    months = pd.date_range(
        start=start_date,
        end=end_date,
        freq="MS"
    )

    return months


def count_commits(client, owner, repo, start, end):
    """Count commits between two dates."""

    page = 1
    total = 0

    while True:
        data = client.get(
            f"/repos/{owner}/{repo}/commits",
            params={
                "since": start.isoformat(),
                "until": end.isoformat(),
                "per_page": 100,
                "page": page,
            },
        )

        if not data:
            break

        total += len(data)

        if len(data) < 100:
            break

        page += 1

        time.sleep(0.1)

    return total


def main():
    print("Starting historical activity pilot...")

    repos = pd.read_csv(REPO_FILE)

    # Deterministic pilot sample
    pilot = repos.sample(
        n=min(PILOT_REPOS, len(repos)),
        random_state=42
    )

    Path("data/historical").mkdir(
        parents=True,
        exist_ok=True
    )

    client = GitHubClient()

    results = []

    for _, repo in pilot.iterrows():

        owner = repo["owner"]
        name = repo["name"]

        created = pd.to_datetime(repo["created_at"], utc=True)
        end_date = pd.Timestamp.now(tz="UTC")

        print(f"\nProcessing: {repo['full_name']}")

        months = get_months(
            created,
            end_date
        )

        for i, month in enumerate(months):

            month_start = month

            if i + 1 < len(months):
                month_end = months[i + 1]
            else:
                month_end = end_date

            print(
                f"  {month_start.strftime('%Y-%m')}",
                end=" ... "
            )

            commits = count_commits(
                client,
                owner,
                name,
                month_start,
                month_end
            )

            print(f"{commits} commits")

            results.append({
                "repo_id": repo["repo_id"],
                "full_name": repo["full_name"],
                "language": repo["language"],
                "month": month_start.strftime("%Y-%m"),
                "commits": commits,
            })

    df = pd.DataFrame(results)

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nPilot complete!")
    print(f"Rows collected: {len(df)}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nPreview:")
    print(df.head(20).to_string(index=False))


if __name__ == "__main__":
    main()