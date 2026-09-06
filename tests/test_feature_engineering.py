import pandas as pd
import numpy as np


INPUT_FILE = "data/historical/repository_engineered_features.csv"


EXPECTED_FEATURES = [
    "meaningful_activity",
    "project_age_months",
    "project_age_years",
    "observation_month_index",

    "commit_rate_6m",
    "active_month_ratio_12m",
    "commit_volatility_6m",
    "zero_commit_streak",
    "commit_trend_6m",

    "avg_contributors_6m",
    "contributor_volatility_6m",
    "new_contributor_rate_6m",
    "returning_contributor_rate_6m",
    "contributor_zero_streak",
    "contributor_trend_6m",

    "avg_pr_opened_6m",
    "avg_issues_opened_6m",
    "pr_merge_rate_6m",
    "pr_net_flow_6m",
    "issue_net_flow_6m",
    "pr_activity_trend_6m",
    "issue_activity_trend_6m",
    "collaboration_trend_6m",

    "activity_total",
    "activity_change_3m",
    "inactivity_streak",
    "longest_inactivity_gap",
]


NON_NEGATIVE_FEATURES = [
    "project_age_months",
    "project_age_years",
    "observation_month_index",
    "commit_rate_6m",
    "active_month_ratio_12m",
    "commit_volatility_6m",
    "zero_commit_streak",
    "avg_contributors_6m",
    "contributor_volatility_6m",
    "contributor_zero_streak",
    "avg_pr_opened_6m",
    "avg_issues_opened_6m",
    "activity_total",
    "inactivity_streak",
    "longest_inactivity_gap",
]


RATE_FEATURES = [
    "new_contributor_rate_6m",
    "returning_contributor_rate_6m",
    "pr_merge_rate_6m",
]


TREND_FEATURES = [
    "commit_trend_6m",
    "contributor_trend_6m",
    "pr_activity_trend_6m",
    "issue_activity_trend_6m",
    "collaboration_trend_6m",
]


def main():
    print("Running feature engineering validation...\n")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows: {len(df)}")
    print(f"Repositories: {df['repo_id'].nunique()}")
    print(f"Columns: {len(df.columns)}")

    # ---------------------------------------------------------
    # Basic structure
    # ---------------------------------------------------------

    assert len(df) == 515
    assert df["repo_id"].nunique() == 5

    # ---------------------------------------------------------
    # Required features
    # ---------------------------------------------------------

    missing_features = [
        feature
        for feature in EXPECTED_FEATURES
        if feature not in df.columns
    ]

    assert not missing_features, (
        f"Missing expected features: {missing_features}"
    )

    # ---------------------------------------------------------
    # Repository-month uniqueness
    # ---------------------------------------------------------

    duplicates = df.duplicated(
        subset=["repo_id", "month"]
    ).sum()

    assert duplicates == 0

    # ---------------------------------------------------------
    # Month parsing
    # ---------------------------------------------------------

    parsed_months = pd.to_datetime(
        df["month"],
        errors="coerce",
    )

    assert parsed_months.notna().all()

    # ---------------------------------------------------------
    # Numeric feature validity
    # ---------------------------------------------------------

    numeric_columns = [
        feature
        for feature in EXPECTED_FEATURES
        if feature in df.columns
        and feature != "meaningful_activity"
    ]

    numeric_data = (
    df[numeric_columns]
    .select_dtypes(include=np.number)
    )

    infinite_values = np.isinf(numeric_data)

    assert not infinite_values.any().any(), (
    "Infinite values detected in numeric features"
    )

    print(
        f"Infinite values: {infinite_values.sum().sum()}"
    )
    print(
        f"NaN values: {numeric_data.isna().sum().sum()}"
    )

    # ---------------------------------------------------------
    # Non-negative features
    # ---------------------------------------------------------

    negative_values = (
        df[NON_NEGATIVE_FEATURES] < 0
    ).sum().sum()

    assert negative_values == 0

    # ---------------------------------------------------------
    # Bounded rate features
    # ---------------------------------------------------------

    for feature in RATE_FEATURES:
        valid_values = (
            df[feature]
            .dropna()
        )

        assert (
            (valid_values >= 0)
            & (valid_values <= 1)
        ).all(), (
            f"{feature} contains values outside [0, 1]"
        )

    # ---------------------------------------------------------
    # Active month ratio
    # ---------------------------------------------------------

    assert (
        (df["active_month_ratio_12m"] >= 0)
        & (df["active_month_ratio_12m"] <= 1)
    ).all()

    # ---------------------------------------------------------
    # Contributor rate consistency
    # ---------------------------------------------------------

    rate_sum = (
        df["new_contributor_rate_6m"]
        + df["returning_contributor_rate_6m"]
    )

    valid_rate_sum = rate_sum.dropna()

    assert (
        valid_rate_sum <= 1 + 1e-9
    ).all(), (
        "New + returning contributor rates exceed 1"
    )

    # ---------------------------------------------------------
    # Inactivity consistency
    # ---------------------------------------------------------

    expected_inactive = (
        df["meaningful_activity"] == False
    )

    assert (
        (
            df["inactivity_streak"] == 0
        )
        | expected_inactive
    ).all()

    # ---------------------------------------------------------
    # Partial month
    # ---------------------------------------------------------

    partial_months = df[
        df["is_partial_month"]
    ].copy()

    assert len(partial_months) == 5

    partial_month_values = (
        pd.to_datetime(
            partial_months["month"],
            errors="coerce",
        )
        .dt.strftime("%Y-%m")
    )

    assert partial_month_values.notna().all()
    assert partial_month_values.nunique() == 1
    assert partial_month_values.iloc[0] == "2026-09"

    # ---------------------------------------------------------
    # Trend features
    # ---------------------------------------------------------

    for feature in TREND_FEATURES:
        assert feature in df.columns

        # Trend values can legitimately be NaN during
        # the first few months because at least 3 months
        # of history are required.
        assert not np.isinf(
            df[feature].dropna()
        ).any()

    # ---------------------------------------------------------
    # Activity change
    # ---------------------------------------------------------

    assert not np.isinf(
        df["activity_change_3m"].dropna()
    ).any()

    # ---------------------------------------------------------
    # Missing value report
    # ---------------------------------------------------------

    print("\nMissing values:")

    missing_values = (
        df[
            EXPECTED_FEATURES
        ]
        .isna()
        .sum()
    )

    print(
        missing_values.to_string()
    )

    # ---------------------------------------------------------
    # Validation summary
    # ---------------------------------------------------------

    print("\nValidation checks passed:")

    print(
        f"  Duplicate repository-month rows: "
        f"{duplicates}"
    )

    print(
        f"  Negative impossible values: "
        f"{negative_values}"
    )

    print(
        f"  Partial-month rows: "
        f"{len(partial_months)}"
    )

    # ---------------------------------------------------------
    # Feature ranges
    # ---------------------------------------------------------

    print("\nFeature ranges:")

    for feature in [
        "commit_rate_6m",
        "active_month_ratio_12m",
        "avg_contributors_6m",
        "new_contributor_rate_6m",
        "returning_contributor_rate_6m",
        "pr_merge_rate_6m",
        "pr_net_flow_6m",
        "issue_net_flow_6m",
        "activity_change_3m",
        "inactivity_streak",
        "longest_inactivity_gap",
    ]:
        print(
            f"  {feature}: "
            f"min={df[feature].min()}, "
            f"max={df[feature].max()}"
        )

    print(
        "\nFeature engineering validation passed!"
    )


if __name__ == "__main__":
    main()