import pandas as pd
import numpy as np


INPUT_FILE = "data/historical/repository_monthly_features.csv"
OUTPUT_FILE = "data/historical/repository_engineered_features.csv"


ACTIVITY_COLUMNS = [
    "commits",
    "contributors",
    "pr_opened",
    "pr_closed",
    "pr_merged",
    "issues_opened",
    "issues_closed",
]


def load_data():
    df = pd.read_csv(INPUT_FILE)

    df["month"] = pd.to_datetime(
        df["month"],
        format="%Y-%m",
    )

    df = df.sort_values(
        ["repo_id", "month"]
    ).reset_index(drop=True)

    return df


def add_meaningful_activity(df):
    df["meaningful_activity"] = (
        df[ACTIVITY_COLUMNS].sum(axis=1) > 0
    )

    return df


def add_project_age(df):
    first_month = (
        df.groupby("repo_id")["month"]
        .transform("min")
    )

    df["project_age_months"] = (
        (df["month"].dt.year - first_month.dt.year) * 12
        + (
            df["month"].dt.month
            - first_month.dt.month
        )
    )

    df["project_age_years"] = (
        df["project_age_months"] / 12
    )

    df["observation_month_index"] = (
        df["project_age_months"] + 1
    )

    return df


def add_development_features(df):
    grouped = df.groupby(
        "repo_id",
        group_keys=False,
    )

    df["commit_rate_6m"] = (
        grouped["commits"]
        .rolling(6, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["active_month_ratio_12m"] = (
        grouped["meaningful_activity"]
        .rolling(12, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["commit_volatility_6m"] = (
        grouped["commits"]
        .rolling(6, min_periods=2)
        .std()
        .reset_index(level=0, drop=True)
        .fillna(0)
    )

    df["zero_commit_streak"] = 0

    for repo_id, group in df.groupby("repo_id"):
        streak = 0

        for index in group.index:
            if df.loc[index, "commits"] == 0:
                streak += 1
            else:
                streak = 0

            df.loc[index, "zero_commit_streak"] = streak

    df["commit_trend_6m"] = (
        grouped["commits"]
        .transform(
            lambda x: x.rolling(
                6,
                min_periods=3,
            ).apply(
                lambda y: np.polyfit(
                    np.arange(len(y)),
                    y,
                    1,
                )[0],
                raw=True,
            )
        )
    )

    return df


def add_community_features(df):
    grouped = df.groupby(
        "repo_id",
        group_keys=False,
    )

    df["avg_contributors_6m"] = (
        grouped["contributors"]
        .rolling(6, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["contributor_volatility_6m"] = (
        grouped["contributors"]
        .rolling(6, min_periods=2)
        .std()
        .reset_index(level=0, drop=True)
        .fillna(0)
    )

    new_sum = (
        df.groupby("repo_id")["new_contributors"]
        .rolling(6, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    returning_sum = (
        df.groupby("repo_id")["returning_contributors"]
        .rolling(6, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    contributor_sum = (
        df.groupby("repo_id")["contributors"]
        .rolling(6, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    contributor_sum = contributor_sum.replace(
        0,
        np.nan,
    )

    df["new_contributor_rate_6m"] = (
        new_sum / contributor_sum
    )

    df["returning_contributor_rate_6m"] = (
        returning_sum / contributor_sum
    )

    df["contributor_zero_streak"] = 0

    for repo_id, group in df.groupby("repo_id"):
        streak = 0

        for index in group.index:
            if df.loc[index, "contributors"] == 0:
                streak += 1
            else:
                streak = 0

            df.loc[index, "contributor_zero_streak"] = streak

    df["contributor_trend_6m"] = (
        grouped["contributors"]
        .transform(
            lambda x: x.rolling(
                6,
                min_periods=3,
            ).apply(
                lambda y: np.polyfit(
                    np.arange(len(y)),
                    y,
                    1,
                )[0],
                raw=True,
            )
        )
    )

    return df


def add_collaboration_features(df):
    grouped = df.groupby(
        "repo_id",
        group_keys=False,
    )

    df["avg_pr_opened_6m"] = (
        grouped["pr_opened"]
        .rolling(6, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["avg_issues_opened_6m"] = (
        grouped["issues_opened"]
        .rolling(6, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    pr_merged_6m = (
        df.groupby("repo_id")["pr_merged"]
        .rolling(6, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    pr_closed_6m = (
        df.groupby("repo_id")["pr_closed"]
        .rolling(6, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    pr_opened_6m = (
        df.groupby("repo_id")["pr_opened"]
        .rolling(6, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    issues_closed_6m = (
        df.groupby("repo_id")["issues_closed"]
        .rolling(6, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    issues_opened_6m = (
        df.groupby("repo_id")["issues_opened"]
        .rolling(6, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    df["pr_merge_rate_6m"] = (
        pr_merged_6m
        / pr_closed_6m.replace(0, np.nan)
    )

    # Net PR flow:
    # positive -> more PRs opened than closed
    # negative -> more PRs closed than opened
    df["pr_net_flow_6m"] = (
        pr_opened_6m - pr_closed_6m
    )

    # Net issue flow:
    # positive -> more issues opened than closed
    # negative -> more issues closed than opened
    df["issue_net_flow_6m"] = (
        issues_opened_6m - issues_closed_6m
    )

    pr_activity = (
        df["pr_opened"]
        + df["pr_closed"]
        + df["pr_merged"]
    )

    df["pr_activity_trend_6m"] = (
        pr_activity.groupby(df["repo_id"])
        .transform(
            lambda x: x.rolling(
                6,
                min_periods=3,
            ).apply(
                lambda y: np.polyfit(
                    np.arange(len(y)),
                    y,
                    1,
                )[0],
                raw=True,
            )
        )
    )

    issue_activity = (
        df["issues_opened"]
        + df["issues_closed"]
    )

    df["issue_activity_trend_6m"] = (
        issue_activity.groupby(df["repo_id"])
        .transform(
            lambda x: x.rolling(
                6,
                min_periods=3,
            ).apply(
                lambda y: np.polyfit(
                    np.arange(len(y)),
                    y,
                    1,
                )[0],
                raw=True,
            )
        )
    )

    collaboration_activity = (
        pr_activity
        + issue_activity
    )

    df["collaboration_trend_6m"] = (
        collaboration_activity.groupby(df["repo_id"])
        .transform(
            lambda x: x.rolling(
                6,
                min_periods=3,
            ).apply(
                lambda y: np.polyfit(
                    np.arange(len(y)),
                    y,
                    1,
                )[0],
                raw=True,
            )
        )
    )

    return df


def add_decline_features(df):
    grouped = df.groupby(
        "repo_id",
        group_keys=False,
    )

    df["activity_total"] = (
        df[ACTIVITY_COLUMNS].sum(axis=1)
    )

    previous_activity = (
        grouped["activity_total"]
        .shift(3)
    )

    current_activity = df["activity_total"]

    df["activity_change_3m"] = np.nan

    positive_previous = (
        previous_activity > 0
    )

    df.loc[positive_previous, "activity_change_3m"] = (
        (
            current_activity[positive_previous]
            - previous_activity[positive_previous]
        )
        / previous_activity[positive_previous]
    )

    both_zero = (
        (previous_activity == 0)
        & (current_activity == 0)
    )

    df.loc[both_zero, "activity_change_3m"] = 0.0

    # When previous activity is zero but current
    # activity is positive, percentage change is undefined.
    # Leave it as NaN instead of creating infinity.

    df["inactivity_streak"] = 0
    df["longest_inactivity_gap"] = 0

    for repo_id, group in df.groupby("repo_id"):
        current_streak = 0
        longest_streak = 0

        for index in group.index:
            if not df.loc[index, "meaningful_activity"]:
                current_streak += 1

                longest_streak = max(
                    longest_streak,
                    current_streak,
                )
            else:
                current_streak = 0

            df.loc[index, "inactivity_streak"] = (
                current_streak
            )

            df.loc[index, "longest_inactivity_gap"] = (
                longest_streak
            )

    return df


def build_features(df):
    df = add_meaningful_activity(df)
    df = add_project_age(df)
    df = add_development_features(df)
    df = add_community_features(df)
    df = add_collaboration_features(df)
    df = add_decline_features(df)

    return df


def main():
    print("Starting feature engineering...\n")

    df = load_data()

    print(f"Input rows: {len(df)}")
    print(f"Repositories: {df['repo_id'].nunique()}")

    df = build_features(df)

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nFeature engineering complete!")
    print(f"Output rows: {len(df)}")
    print(f"Output columns: {len(df.columns)}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nNew features:")

    original_columns = [
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

    for column in df.columns:
        if column not in original_columns:
            print(f"  - {column}")


if __name__ == "__main__":
    main()