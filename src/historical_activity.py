import subprocess
from pathlib import Path
from collections import Counter

import pandas as pd


REPO_FILE = Path("data/raw/repositories.csv")
CLONE_DIR = Path("data/repositories")
OUTPUT_FILE = Path("data/historical/repository_activity_monthly.csv")

PILOT_REPOS = 5


def clone_repository(repo_url, destination):
    """Clone a repository if it does not already exist."""

    if destination.exists():
        print("  Repository already cloned.")
        return

    print("  Cloning repository...")

    subprocess.run(
        [
            "git",
            "clone",
            "--filter=blob:none",
            "--no-checkout",
            repo_url,
            str(destination),
        ],
        check=True,
    )


def get_monthly_commits(repository_path):
    """Extract commit counts grouped by month."""

    result = subprocess.run(
        [
            "git",
            "-C",
            str(repository_path),
            "log",
            "--all",
            "--date=format:%Y-%m",
            "--format=%ad",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    months = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]

    return Counter(months)


def main():

    print("Starting OSSurvive historical activity collector v2...")

    repos = pd.read_csv(REPO_FILE)

    pilot = repos.sample(
        n=min(PILOT_REPOS, len(repos)),
        random_state=42,
    )

    CLONE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_results = []

    for _, repo in pilot.iterrows():

        full_name = repo["full_name"]
        owner = repo["owner"]
        name = repo["name"]

        print(f"\nProcessing: {full_name}")

        repository_path = CLONE_DIR / f"{owner}__{name}"

        repo_url = f"https://github.com/{owner}/{name}.git"

        clone_repository(
            repo_url,
            repository_path,
        )

        monthly_commits = get_monthly_commits(
            repository_path
        )

        created = pd.to_datetime(
            repo["created_at"],
            utc=True,
        )

        # Convert to a timezone-naive month start.
        created_month = pd.Timestamp(
            created.year,
            created.month,
            1,
        )

        end_month = (
            pd.Timestamp.now()
            .to_period("M")
            .start_time
        )

        months = pd.date_range(
            start=created_month,
            end=end_month,
            freq="MS",
        )

        for month in months:

            month_key = month.strftime("%Y-%m")

            all_results.append(
                {
                    "repo_id": repo["repo_id"],
                    "full_name": full_name,
                    "language": repo["language"],
                    "month": month_key,
                    "commits": monthly_commits.get(
                        month_key,
                        0,
                    ),
                }
            )

        print(
            f"  Months reconstructed: {len(months)}"
        )

        print(
            f"  Total commits found: "
            f"{sum(monthly_commits.values())}"
        )

    df = pd.DataFrame(all_results)

    df = df.sort_values(
        ["repo_id", "month"]
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\n===================================")
    print("Historical collection complete")
    print("===================================")

    print(
        f"Repositories: "
        f"{df['repo_id'].nunique()}"
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print("\nPreview:")

    print(
        df.head(20).to_string(index=False)
    )


if __name__ == "__main__":
    main()