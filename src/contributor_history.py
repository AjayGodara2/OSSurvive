from pathlib import Path
from collections import defaultdict
import subprocess

import pandas as pd


REPO_FILE = Path("data/raw/repositories.csv")
CLONE_DIR = Path("data/repositories")
OUTPUT_FILE = Path(
    "data/historical/repository_contributors_monthly.csv"
)

RANDOM_SEED = 42
MVP_REPOS = 20


def get_commit_contributors(repository_path):
    """
    Extract commit author identities grouped by month.

    Identity is represented as:
        author name + author email
    """

    result = subprocess.run(
        [
            "git",
            "-C",
            str(repository_path),
            "log",
            "--all",
            "--date=format:%Y-%m",
            "--format=%ad%x09%aN%x09%aE",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    monthly_authors = defaultdict(set)

    for line in result.stdout.splitlines():

        if not line.strip():
            continue

        parts = line.split("\t")

        if len(parts) != 3:
            continue

        month, author_name, author_email = parts

        identity = (
            author_name.strip(),
            author_email.strip().lower(),
        )

        monthly_authors[month].add(identity)

    return monthly_authors


def reconstruct_months(repo, monthly_authors):
    """Build a continuous monthly contributor timeline."""

    created = pd.to_datetime(
        repo["created_at"],
        utc=True,
    )

    created_month = pd.Timestamp(
        created.year,
        created.month,
        1,
    )

    # Latest complete month.
    end_month = (
        pd.Timestamp.now()
        .to_period("M")
        .start_time
        - pd.offsets.MonthBegin(1)
    )

    months = pd.date_range(
        start=created_month,
        end=end_month,
        freq="MS",
    )

    rows = []

    previous_authors = set()

    for month in months:

        month_key = month.strftime("%Y-%m")

        current_authors = monthly_authors.get(
            month_key,
            set(),
        )

        new_authors = (
            current_authors - previous_authors
        )

        returning_authors = (
            current_authors & previous_authors
        )

        rows.append(
            {
                "repo_id": repo["repo_id"],
                "full_name": repo["full_name"],
                "language": repo["language"],
                "month": month_key,
                "contributors": len(current_authors),
                "new_contributors": len(new_authors),
                "returning_contributors": len(
                    returning_authors
                ),
            }
        )

        previous_authors.update(
            current_authors
        )

    return rows


def save_results(results):
    """Save current progress safely."""

    if not results:
        return

    df = pd.DataFrame(results)

    df = (
        df.drop_duplicates(
            subset=["repo_id", "month"]
        )
        .sort_values(
            ["repo_id", "month"]
        )
        .reset_index(drop=True)
    )

    temp_file = OUTPUT_FILE.with_suffix(".tmp")

    df.to_csv(
        temp_file,
        index=False,
    )

    temp_file.replace(OUTPUT_FILE)


def main():

    print("=" * 70)
    print("OSSurvive - MVP Historical Contributor Collection")
    print("=" * 70)

    repos = pd.read_csv(REPO_FILE)

    # Same deterministic 20-repository MVP sample
    repos = repos.sample(
        n=min(MVP_REPOS, len(repos)),
        random_state=RANDOM_SEED,
    ).reset_index(drop=True)

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
            existing["repo_id"].astype(int)
        )

        results = existing.to_dict(
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
        results = []

        print(
            "\nNo previous contributor dataset found."
        )

    print(
        f"\nMVP repositories: "
        f"{len(repos)}"
    )

    # ---------------------------------------------------------
    # Collect contributors
    # ---------------------------------------------------------

    for index, (_, repo) in enumerate(
        repos.iterrows(),
        start=1,
    ):

        repo_id = int(repo["repo_id"])
        full_name = repo["full_name"]

        if repo_id in completed_repo_ids:

            print(
                f"[{index}/{len(repos)}] "
                f"SKIP {full_name} "
                f"(already collected)"
            )

            continue

        print(
            f"\n[{index}/{len(repos)}] "
            f"Processing: {full_name}"
        )

        repository_path = (
            CLONE_DIR
            / f"{repo['owner']}__{repo['name']}"
        )

        if not repository_path.exists():

            print(
                "  Local repository not found."
            )

            print(
                "  Run historical_activity.py first."
            )

            continue

        try:

            monthly_authors = (
                get_commit_contributors(
                    repository_path
                )
            )

            rows = reconstruct_months(
                repo,
                monthly_authors,
            )

            results.extend(rows)

            completed_repo_ids.add(
                repo_id
            )

            save_results(results)

            total_unique = len(
                set().union(
                    *monthly_authors.values()
                )
            ) if monthly_authors else 0

            print(
                f"  Total unique contributors: "
                f"{total_unique}"
            )

            print(
                f"  Months reconstructed: "
                f"{len(rows)}"
            )

            print(
                f"  Progress: "
                f"{len(completed_repo_ids)}/"
                f"{len(repos)}"
            )

        except Exception as error:

            print(
                f"  ERROR: {error}"
            )

            print(
                "  Skipping repository and "
                "continuing safely."
            )

    # ---------------------------------------------------------
    # Final dataset
    # ---------------------------------------------------------

    if not results:

        raise RuntimeError(
            "No contributor data collected."
        )

    df = pd.DataFrame(results)

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
    print("CONTRIBUTOR COLLECTION COMPLETE")
    print("=" * 70)

    print(
        f"\nRepositories: "
        f"{df['repo_id'].nunique()}"
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Total contributor-months: "
        f"{df['contributors'].sum()}"
    )

    print(
        f"Total new contributor-months: "
        f"{df['new_contributors'].sum()}"
    )

    print(
        f"Total returning contributor-months: "
        f"{df['returning_contributors'].sum()}"
    )

    print(
        f"\nDate range: "
        f"{df['month'].min()} → "
        f"{df['month'].max()}"
    )

    print(
        f"\nOutput: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()