import pandas as pd

OUTPUT_FILE = "data/historical/repository_contributors_monthly.csv"


def main():
    print("Testing contributor history dataset...")

    df = pd.read_csv(OUTPUT_FILE)

    required_columns = [
        "repo_id",
        "full_name",
        "language",
        "month",
        "contributors",
        "new_contributors",
        "returning_contributors",
    ]

    for column in required_columns:
        assert column in df.columns, f"Missing required column: {column}"

    assert df.duplicated(["repo_id", "month"]).sum() == 0, \
        "Found duplicate repo-month rows."

    assert df.isna().sum().sum() == 0, \
        "Found missing values."

    count_columns = [
        "contributors",
        "new_contributors",
        "returning_contributors",
    ]

    assert (df[count_columns] < 0).sum().sum() == 0, \
        "Found negative contributor counts."

    assert (
        df["new_contributors"] + df["returning_contributors"]
        == df["contributors"]
    ).all(), \
        "Contributor totals do not match new + returning contributors."

    assert df["repo_id"].nunique() > 0, \
        "No repositories found."

    assert len(df) > 0, \
        "Contributor history dataset is empty."

    print("\nContributor history dataset is valid!")
    print(f"Repositories: {df['repo_id'].nunique()}")
    print(f"Rows: {len(df)}")
    print(f"Total contributor-months: {df['contributors'].sum()}")
    print(f"New contributor-months: {df['new_contributors'].sum()}")
    print(f"Returning contributor-months: {df['returning_contributors'].sum()}")


if __name__ == "__main__":
    main()