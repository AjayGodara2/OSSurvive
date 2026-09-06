import subprocess
from pathlib import Path
from collections import Counter

import pandas as pd


REPO_FILE = Path("data/raw/repositories.csv")
CLONE_DIR = Path("data/repositories")
OUTPUT_FILE = Path("data/historical/repository_activity_monthly.csv")

RANDOM_SEED = 42


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


def reconstruct_months(repo, monthly_commits):
    """Create a continuous monthly timeline for one repository."""

    created = pd.to_datetime(
        repo["created_at"],
        utc=True,
    )

    created_month = pd.Timestamp(
        created.year,
        created.month,
        1,
    )

    # Use the latest complete month.
    current_month = pd.Timestamp.now().to_period("M")

    end_month = (
        current_month.start_time
    )

    # Exclude the current partial month.
    end_month = (
        end_month - pd.offsets.MonthBegin(1)
    )

    months = pd.date_range(
        start=created_month,
        end=end_month,
        freq="MS",
    )

    rows = []

    for month in months:

        month_key = month.strftime("%Y-%m")

        rows.append(
            {
                "repo_id": repo["repo_id"],
                "full_name": repo["full_name"],
                "language": repo["language"],
                "month": month_key,
                "commits": monthly_commits.get(
                    month_key,
                    0,
                ),
            }
        )

    return rows


def save_results(rows):
    """Save collected results safely."""

    if not rows:
        return

    df = pd.DataFrame(rows)

    df = (
        df.drop_duplicates(
            subset=["repo_id", "month"]
        )
        .sort_values(
            ["repo_id", "month"]
        )
        .reset_index(drop=True)
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_file = OUTPUT_FILE.with_suffix(".tmp")

    df.to_csv(
        temp_file,
        index=False,
    )

    temp_file.replace(OUTPUT_FILE)


def main():

    print("=" * 70)
    print("OSSurvive - Full Historical Activity Collection")
    print("=" * 70)

    repos = pd.read_csv(REPO_FILE).sample(
    n=min(20, len(pd.read_csv(REPO_FILE))),
    random_state=RANDOM_SEED,
    )

    CLONE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Load existing progress
    # ---------------------------------------------------------

    if OUTPUT_FILE.exists():

        existing = pd.read_csv(
            OUTPUT_FILE
        )

        completed_repo_ids = set(
            existing["repo_id"]
            .astype(int)
        )

        all_results = existing.to_dict(
            "records"
        )

        print(
            f"\nExisting progress found:"
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
        all_results = []

        print(
            "\nNo previous collection found."
        )

    # ---------------------------------------------------------
    # Process repositories
    # ---------------------------------------------------------

    total = len(repos)

    print(
        f"\nRepositories in sampling dataset: "
        f"{total}"
    )

    for index, (_, repo) in enumerate(
        repos.iterrows(),
        start=1,
    ):

        repo_id = int(repo["repo_id"])
        full_name = repo["full_name"]

        if repo_id in completed_repo_ids:

            print(
                f"[{index}/{total}] "
                f"SKIP {full_name} "
                f"(already collected)"
            )

            continue

        print(
            f"\n[{index}/{total}] "
            f"Processing: {full_name}"
        )

        repository_path = (
            CLONE_DIR
            / f"{repo['owner']}__{repo['name']}"
        )

        repo_url = (
            f"https://github.com/"
            f"{repo['owner']}/"
            f"{repo['name']}.git"
        )

        try:

            clone_repository(
                repo_url,
                repository_path,
            )

            monthly_commits = (
                get_monthly_commits(
                    repository_path
                )
            )

            rows = reconstruct_months(
                repo,
                monthly_commits,
            )

            all_results.extend(rows)

            completed_repo_ids.add(
                repo_id
            )

            save_results(
                all_results
            )

            print(
                f"  Months reconstructed: "
                f"{len(rows)}"
            )

            print(
                f"  Total commits found: "
                f"{sum(monthly_commits.values())}"
            )

            print(
                f"  Progress: "
                f"{len(completed_repo_ids)}/{total}"
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
    # Final summary
    # ---------------------------------------------------------

    if not all_results:
        raise RuntimeError(
            "No historical activity data collected."
        )

    df = pd.DataFrame(all_results)

    df = (
        df.drop_duplicates(
            subset=["repo_id", "month"]
        )
        .sort_values(
            ["repo_id", "month"]
        )
        .reset_index(drop=True)
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\n" + "=" * 70)
    print("HISTORICAL COLLECTION SUMMARY")
    print("=" * 70)

    print(
        f"\nRepositories collected: "
        f"{df['repo_id'].nunique()}"
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Total commits: "
        f"{df['commits'].sum()}"
    )

    print(
        f"Date range: "
        f"{df['month'].min()} → "
        f"{df['month'].max()}"
    )

    print(
        f"\nOutput: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()