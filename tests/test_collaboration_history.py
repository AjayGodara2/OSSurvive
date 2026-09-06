import pandas as pd


OUTPUT_FILE = "data/historical/repository_collaboration_monthly.csv"

EXPECTED_COLUMNS = [
    "repo_id",
    "full_name",
    "language",
    "month",
    "pr_opened",
    "pr_closed",
    "pr_merged",
    "issues_opened",
    "issues_closed",
]


def main():
    print("Running collaboration history validation...\n")

    df = pd.read_csv(OUTPUT_FILE)

    # --------------------------------------------------
    # 1. Basic dataset checks
    # --------------------------------------------------

    assert len(df) > 0, "Dataset is empty"

    assert list(df.columns) == EXPECTED_COLUMNS, (
        "Unexpected columns found"
    )

    # --------------------------------------------------
    # 2. Repository checks
    # --------------------------------------------------

    repositories = df["repo_id"].nunique()

    assert repositories == 5, (
        f"Expected 5 repositories, found {repositories}"
    )

    # --------------------------------------------------
    # 3. Duplicate repo-month check
    # --------------------------------------------------

    duplicates = df.duplicated(
        subset=["repo_id", "month"]
    ).sum()

    assert duplicates == 0, (
        f"Found {duplicates} duplicate repo-month rows"
    )

    # --------------------------------------------------
    # 4. Missing value check
    # --------------------------------------------------

    missing = df.isna().sum().sum()

    assert missing == 0, (
        f"Found {missing} missing values"
    )

    # --------------------------------------------------
    # 5. Negative value check
    # --------------------------------------------------

    numeric_columns = [
        "pr_opened",
        "pr_closed",
        "pr_merged",
        "issues_opened",
        "issues_closed",
    ]

    negative_values = (
        df[numeric_columns] < 0
    ).sum().sum()

    assert negative_values == 0, (
        f"Found {negative_values} negative values"
    )

    # --------------------------------------------------
    # 6. PR consistency checks
    # --------------------------------------------------

    invalid_merged = (
        df["pr_merged"] > df["pr_closed"]
    ).sum()

    assert invalid_merged == 0, (
        "Found months where merged PRs exceed closed PRs"
    )

    # --------------------------------------------------
    # 7. Month format check
    # --------------------------------------------------

    parsed_months = pd.to_datetime(
        df["month"],
        format="%Y-%m",
        errors="coerce"
    )

    invalid_months = parsed_months.isna().sum()

    assert invalid_months == 0, (
        f"Found {invalid_months} invalid month values"
    )

        # --------------------------------------------------
    # 8. Continuous monthly timeline check
    # --------------------------------------------------

    timeline_errors = 0

    for repo_id, group in df.groupby("repo_id"):

        months = pd.to_datetime(
            group["month"],
            format="%Y-%m"
        ).sort_values().reset_index(drop=True)

        expected_months = pd.date_range(
            start=months.min(),
            end=months.max(),
            freq="MS"
        )

        if not months.equals(
            pd.Series(expected_months)
        ):
            timeline_errors += 1

    assert timeline_errors == 0, (
        f"Found {timeline_errors} repositories "
        f"with non-continuous monthly timelines"
    )

    print(f"Timeline errors: {timeline_errors}")

    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    print("Validation passed!")
    print(f"Repositories: {repositories}")
    print(f"Rows: {len(df)}")
    print(f"Duplicate repo-month rows: {duplicates}")
    print(f"Missing values: {missing}")
    print(f"Negative values: {negative_values}")
    print(f"Invalid merged PR rows: {invalid_merged}")
    print(f"Invalid month values: {invalid_months}")

    print("\nTotals:")
    print(f"PRs opened: {df['pr_opened'].sum()}")
    print(f"PRs closed: {df['pr_closed'].sum()}")
    print(f"PRs merged: {df['pr_merged'].sum()}")
    print(f"Issues opened: {df['issues_opened'].sum()}")
    print(f"Issues closed: {df['issues_closed'].sum()}")


if __name__ == "__main__":
    main()