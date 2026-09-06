import pandas as pd


OUTPUT_FILE = "data/historical/repository_activity_monthly.csv"


def main():
    print("Testing historical activity dataset...")

    df = pd.read_csv(OUTPUT_FILE)

    duplicate_rows = df.duplicated(
        ["repo_id", "month"]
    ).sum()

    missing_commits = df["commits"].isna().sum()

    negative_commits = (df["commits"] < 0).sum()

    assert duplicate_rows == 0, (
        f"Found {duplicate_rows} duplicate repo-month rows."
    )

    assert missing_commits == 0, (
        f"Found {missing_commits} missing commit values."
    )

    assert negative_commits == 0, (
        f"Found {negative_commits} negative commit values."
    )

    assert df["repo_id"].nunique() > 0, (
        "No repositories found."
    )

    assert len(df) > 0, (
        "Historical dataset is empty."
    )

    print("\nHistorical activity dataset is valid!")
    print(f"Repositories: {df['repo_id'].nunique()}")
    print(f"Rows: {len(df)}")
    print(f"Zero-commit months: {(df['commits'] == 0).sum()}")
    print(f"Active months: {(df['commits'] > 0).sum()}")


if __name__ == "__main__":
    main()