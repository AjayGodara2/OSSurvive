import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


INPUT_FILE = "data/historical/repository_modeling_dataset.csv"
OUTPUT_FILE = "data/historical/model_feature_importance.csv"


FEATURES = [
    "commit_rate_6m",
    "active_month_ratio_12m",
    "commit_volatility_6m",
    "zero_commit_streak",
    "commit_trend_6m",
    "avg_contributors_6m",
    "contributor_volatility_6m",
    "new_contributor_rate_6m",
    "returning_contributor_rate_6m",
    #"contributor_zero_streak",
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
    "project_age_months",
    #"observation_month_index",
]


def main():

    print("Analyzing OSSurvive model features...\n")

    df = pd.read_csv(INPUT_FILE)

    df["observation_month"] = pd.to_datetime(
        df["observation_month"]
    )

    df = df.sort_values(
        "observation_month"
    ).reset_index(drop=True)

    X = df[FEATURES]
    y = df["inactive_within_12m"]

    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    y_train = y.iloc[:split_index]

    model = Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        ),
        (
            "classifier",
            LogisticRegression(
                class_weight="balanced",
                max_iter=2000,
                random_state=42,
            )
        ),
    ])

    model.fit(X_train, y_train)

    classifier = model.named_steps["classifier"]

    coefficients = classifier.coef_[0]

    importance = pd.DataFrame({
        "feature": FEATURES,
        "coefficient": coefficients,
        "absolute_importance": np.abs(coefficients),
    })

    importance["direction"] = np.where(
        importance["coefficient"] > 0,
        "increases_risk",
        "decreases_risk",
    )

    importance = importance.sort_values(
        "absolute_importance",
        ascending=False
    ).reset_index(drop=True)

    importance.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Feature importance:\n")

    print(
        importance[
            [
                "feature",
                "coefficient",
                "direction",
            ]
        ].to_string(index=False)
    )

    print(
        f"\nSaved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()