import pandas as pd


ACTIVITY_FILE = "data/historical/repository_activity_monthly.csv"
CONTRIBUTOR_FILE = "data/historical/repository_contributors_monthly.csv"
COLLABORATION_FILE = "data/historical/repository_collaboration_monthly.csv"

OUTPUT_FILE = "data/historical/repository_monthly_features.csv"


def load_data():
    """Load the three historical datasets."""

    activity = pd.read_csv(ACTIVITY_FILE)
    contributors = pd.read_csv(CONTRIBUTOR_FILE)
    collaboration = pd.read_csv(COLLABORATION_FILE)

    return activity, contributors, collaboration


def validate_keys(activity, contributors, collaboration):
    """Ensure all datasets contain the same repository-month observations."""

    key_columns = ["repo_id", "month"]

    activity_keys = set(
        zip(activity["repo_id"], activity["month"])
    )

    contributor_keys = set(
        zip(contributors["repo_id"], contributors["month"])
    )

    collaboration_keys = set(
        zip(collaboration["repo_id"], collaboration["month"])
    )

    assert activity_keys == contributor_keys, (
        "Activity and contributor repository-month keys do not match"
    )

    assert activity_keys == collaboration_keys, (
        "Activity and collaboration repository-month keys do not match"
    )

    assert activity.duplicated(key_columns).sum() == 0, (
        "Duplicate repository-month rows in activity data"
    )

    assert contributors.duplicated(key_columns).sum() == 0, (
        "Duplicate repository-month rows in contributor data"
    )

    assert collaboration.duplicated(key_columns).sum() == 0, (
        "Duplicate repository-month rows in collaboration data"
    )


def integrate_data(activity, contributors, collaboration):
    """Merge the three historical datasets."""

    contributor_columns = [
        "repo_id",
        "month",
        "contributors",
        "new_contributors",
        "returning_contributors",
    ]

    collaboration_columns = [
        "repo_id",
        "month",
        "pr_opened",
        "pr_closed",
        "pr_merged",
        "issues_opened",
        "issues_closed",
    ]

    output = activity.merge(
        contributors[contributor_columns],
        on=["repo_id", "month"],
        how="inner",
    )

    output = output.merge(
        collaboration[collaboration_columns],
        on=["repo_id", "month"],
        how="inner",
    )

    return output


def main():
    print("Starting historical data integration...\n")

    activity, contributors, collaboration = load_data()

    print("Input datasets:")
    print(f"  Activity rows: {len(activity)}")
    print(f"  Contributor rows: {len(contributors)}")
    print(f"  Collaboration rows: {len(collaboration)}")

    print("\nValidating repository-month keys...")

    validate_keys(
        activity,
        contributors,
        collaboration,
    )

    print("Repository-month validation passed!")

    output = integrate_data(
        activity,
        contributors,
        collaboration,
    )

    # Mark the current month as partial.
    current_month = pd.Timestamp.now(
        tz="UTC"
    ).strftime("%Y-%m")

    output["is_partial_month"] = (
        output["month"] == current_month
    )

    output = output.sort_values(
        ["repo_id", "month"]
    ).reset_index(drop=True)

    expected_columns = [
        "repo_id",
        "full_name",
        "language",
        "month",
        "commits",
        "contributors",
        "new_contributors",
        "returning_contributors",
        "pr_opened",
        "pr_closed",
        "pr_merged",
        "issues_opened",
        "issues_closed",
        "is_partial_month",
    ]

    assert list(output.columns) == expected_columns, (
        "Unexpected output columns"
    )

    assert len(output) == len(activity), (
        "Integrated dataset row count changed"
    )

    assert output.duplicated(
        ["repo_id", "month"]
    ).sum() == 0, (
        "Duplicate repository-month rows detected"
    )

    assert output.isna().sum().sum() == 0, (
        "Missing values detected"
    )

    output.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nHistorical data integration complete!")

    print(f"Repositories: {output['repo_id'].nunique()}")
    print(f"Rows: {len(output)}")
    print(
        f"Partial months: "
        f"{output['is_partial_month'].sum()}"
    )

    print("\nColumns:")
    for column in output.columns:
        print(f"  - {column}")

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()