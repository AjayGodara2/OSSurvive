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
    """
    Validate repository-month keys.

    Activity and contributor datasets should match exactly.

    Collaboration may contain fewer repositories because some
    large repositories may not have completed collection.
    """

    key_columns = ["repo_id", "month"]

    activity_keys = set(
        zip(
            activity["repo_id"],
            activity["month"],
        )
    )

    contributor_keys = set(
        zip(
            contributors["repo_id"],
            contributors["month"],
        )
    )

    collaboration_keys = set(
        zip(
            collaboration["repo_id"],
            collaboration["month"],
        )
    )

    # ---------------------------------------------------------
    # Activity / contributor validation
    # ---------------------------------------------------------

    assert activity_keys == contributor_keys, (
        "Activity and contributor repository-month keys "
        "do not match"
    )

    # ---------------------------------------------------------
    # Duplicate validation
    # ---------------------------------------------------------

    assert activity.duplicated(
        key_columns
    ).sum() == 0, (
        "Duplicate repository-month rows in activity data"
    )

    assert contributors.duplicated(
        key_columns
    ).sum() == 0, (
        "Duplicate repository-month rows in contributor data"
    )

    assert collaboration.duplicated(
        key_columns
    ).sum() == 0, (
        "Duplicate repository-month rows in collaboration data"
    )

    # ---------------------------------------------------------
    # Coverage information
    # ---------------------------------------------------------

    activity_repos = set(
        activity["repo_id"]
    )

    collaboration_repos = set(
        collaboration["repo_id"]
    )

    missing_repositories = (
        activity_repos
        - collaboration_repos
    )

    print(
        f"  Activity repositories: "
        f"{len(activity_repos)}"
    )

    print(
        f"  Collaboration repositories: "
        f"{len(collaboration_repos)}"
    )

    if missing_repositories:

        print(
            "\n  WARNING:"
        )

        print(
            "  Collaboration data is missing "
            f"{len(missing_repositories)} "
            "repository/repositories."
        )

        print(
            "  These repositories will be excluded "
            "from the integrated dataset."
        )

    return missing_repositories


def integrate_data(
    activity,
    contributors,
    collaboration,
):
    """
    Merge datasets using repository-month keys.

    Only repository-month observations that exist in all
    three datasets are retained.
    """

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

    # ---------------------------------------------------------
    # Activity + contributors
    # ---------------------------------------------------------

    output = activity.merge(
        contributors[
            contributor_columns
        ],
        on=[
            "repo_id",
            "month",
        ],
        how="inner",
        validate="one_to_one",
    )

    # ---------------------------------------------------------
    # Add collaboration
    # ---------------------------------------------------------

    output = output.merge(
        collaboration[
            collaboration_columns
        ],
        on=[
            "repo_id",
            "month",
        ],
        how="inner",
        validate="one_to_one",
    )

    return output


def main():

    print(
        "Starting historical data integration...\n"
    )

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    activity, contributors, collaboration = (
        load_data()
    )

    print(
        "Input datasets:"
    )

    print(
        f"  Activity rows: "
        f"{len(activity)}"
    )

    print(
        f"  Contributor rows: "
        f"{len(contributors)}"
    )

    print(
        f"  Collaboration rows: "
        f"{len(collaboration)}"
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    print(
        "\nValidating repository-month keys..."
    )

    missing_repositories = validate_keys(
        activity,
        contributors,
        collaboration,
    )

    print(
        "\nRepository-month validation passed!"
    )

    # ---------------------------------------------------------
    # Integration
    # ---------------------------------------------------------

    output = integrate_data(
        activity,
        contributors,
        collaboration,
    )

    # ---------------------------------------------------------
    # Partial month
    # ---------------------------------------------------------

    current_month = (
        pd.Timestamp.now(
            tz="UTC"
        ).strftime("%Y-%m")
    )

    output[
        "is_partial_month"
    ] = (
        output["month"]
        == current_month
    )

    # ---------------------------------------------------------
    # Sort
    # ---------------------------------------------------------

    output = (
        output
        .sort_values(
            [
                "repo_id",
                "month",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    # ---------------------------------------------------------
    # Expected schema
    # ---------------------------------------------------------

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

    assert list(
        output.columns
    ) == expected_columns, (
        "Unexpected output columns"
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    assert output.duplicated(
        [
            "repo_id",
            "month",
        ]
    ).sum() == 0, (
        "Duplicate repository-month rows detected"
    )

    assert output.isna().sum().sum() == 0, (
        "Missing values detected"
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    output.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # ---------------------------------------------------------
    # Report
    # ---------------------------------------------------------

    print(
        "\nHistorical data integration complete!"
    )

    print(
        f"Repositories: "
        f"{output['repo_id'].nunique()}"
    )

    print(
        f"Rows: "
        f"{len(output)}"
    )

    print(
        f"Partial months: "
        f"{output['is_partial_month'].sum()}"
    )

    if missing_repositories:

        print(
            "\nExcluded repositories:"
        )

        excluded_names = (
            activity[
                activity["repo_id"].isin(
                    missing_repositories
                )
            ]["full_name"]
            .drop_duplicates()
            .tolist()
        )

        for name in excluded_names:

            print(
                f"  - {name}"
            )

    print(
        "\nColumns:"
    )

    for column in output.columns:

        print(
            f"  - {column}"
        )

    print(
        f"\nSaved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()