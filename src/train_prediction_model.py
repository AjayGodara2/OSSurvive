import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
)


INPUT_FILE = "data/historical/repository_modeling_dataset.csv"
OUTPUT_FILE = "data/historical/prediction_results.csv"


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
    "project_age_months",
    "observation_month_index",
]


def main():

    print("Training OSSurvive early-warning model...\n")

    df = pd.read_csv(INPUT_FILE)

    df["observation_month"] = pd.to_datetime(
        df["observation_month"]
    )

    df = df.sort_values(
        "observation_month"
    ).reset_index(drop=True)

    X = df[FEATURES]
    y = df["inactive_within_12m"]

    print(f"Total observations: {len(df)}")
    print(f"Positive targets: {y.sum()}")
    print(f"Negative targets: {(y == 0).sum()}")

    # ---------------------------------------------------------
    # Chronological split
    # ---------------------------------------------------------

    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    train_dates = df["observation_month"].iloc[:split_index]
    test_dates = df["observation_month"].iloc[split_index:]

    print("\nChronological split:")
    print(
        f"Training: {len(X_train)} observations "
        f"({train_dates.min().strftime('%Y-%m')} "
        f"→ {train_dates.max().strftime('%Y-%m')})"
    )

    print(
        f"Testing:  {len(X_test)} observations "
        f"({test_dates.min().strftime('%Y-%m')} "
        f"→ {test_dates.max().strftime('%Y-%m')})"
    )

    print(
        f"Training positives: {y_train.sum()}"
    )

    print(
        f"Testing positives: {y_test.sum()}"
    )

    # ---------------------------------------------------------
    # Model
    # ---------------------------------------------------------

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

    probabilities = model.predict_proba(X_test)[:, 1]

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    # ---------------------------------------------------------
    # Evaluation
    # ---------------------------------------------------------

    print("\nEvaluation:")

    print(
        f"Accuracy:  "
        f"{accuracy_score(y_test, predictions):.3f}"
    )

    print(
        f"Precision: "
        f"{precision_score(y_test, predictions, zero_division=0):.3f}"
    )

    print(
        f"Recall:    "
        f"{recall_score(y_test, predictions, zero_division=0):.3f}"
    )

    print(
        f"F1:        "
        f"{f1_score(y_test, predictions, zero_division=0):.3f}"
    )

    unique_test_classes = y_test.nunique()

    if unique_test_classes == 2:

        roc_auc = roc_auc_score(
            y_test,
            probabilities
        )

        pr_auc = average_precision_score(
            y_test,
            probabilities
        )

        print(
            f"ROC-AUC:   {roc_auc:.3f}"
        )

        print(
            f"PR-AUC:    {pr_auc:.3f}"
        )

    else:

        print(
            "ROC-AUC:   unavailable "
            "(test set contains only one class)"
        )

        print(
            "PR-AUC:    unavailable "
            "(test set contains only one class)"
        )

    # ---------------------------------------------------------
    # Save predictions
    # ---------------------------------------------------------

    results = df.iloc[split_index:].copy()

    results["predicted_probability"] = probabilities
    results["predicted_inactive"] = predictions

    results[
        [
            "repo_id",
            "full_name",
            "observation_month",
            "inactive_within_12m",
            "predicted_probability",
            "predicted_inactive",
        ]
    ].to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved predictions to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()