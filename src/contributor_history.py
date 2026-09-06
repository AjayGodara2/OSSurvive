from pathlib import Path
from collections import defaultdict

import pandas as pd


REPO_FILE = Path("data/raw/repositories.csv")
CLONE_DIR = Path("data/repositories")
OUTPUT_FILE = Path(
    "data/historical/repository_contributors_monthly.csv"
)

PILOT_REPOS = 5


def get_commit_contributors(repository_path):
    """
    Extract commit author identities grouped by month.

    Identity is represented as:
        author name + author email
    """

    import subprocess

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


def main():

    print("Starting OSSurvive contributor history pilot...")

    repos = pd.read_csv(REPO_FILE)

    pilot = repos.sample(
        n=min(PILOT_REPOS, len(repos)),
        random_state=42,
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = []

    for _, repo in pilot.iterrows():

        full_name = repo["full_name"]
        owner = repo["owner"]
        name = repo["name"]

        print(f"\nProcessing: {full_name}")

        repository_path = (
            CLONE_DIR / f"{owner}__{name}"
        )

        if not repository_path.exists():
            print("  Local repository not found.")
            print("  Run historical_activity.py first.")
            continue

        monthly_authors = get_commit_contributors(
            repository_path
        )

        created = pd.to_datetime(
            repo["created_at"],
            utc=True,
        )

        created_month = pd.Timestamp(
            created.year,
            created.month,
            1,
        )

        end_month = pd.Timestamp.now().replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        months = pd.date_range(
            start=created_month,
            end=end_month,
            freq="MS",
        )

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

            results.append(
                {
                    "repo_id": repo["repo_id"],
                    "full_name": full_name,
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
            f"{len(months)}"
        )

    df = pd.DataFrame(results)

    df = df.sort_values(
        ["repo_id", "month"]
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\n===================================")
    print("Contributor history pilot complete")
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