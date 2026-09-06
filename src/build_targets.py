import pandas as pd


INPUT_FILE = "data/historical/repository_engineered_features.csv"

PREDICTION_OUTPUT = (
    "data/historical/repository_prediction_targets.csv"
)

SURVIVAL_OUTPUT = (
    "data/historical/repository_survival_dataset.csv"
)


def load_data():
    df = pd.read_csv(INPUT_FILE)

    df["month"] = pd.to_datetime(df["month"])

    return df


def remove_partial_months(df):
    return df[~df["is_partial_month"]].copy()


def find_event_month(group):
    """
    Find the first month where a repository reaches
    12 consecutive inactive months.
    """

    group = group.sort_values("month").reset_index(drop=True)

    streak = 0

    for index, row in group.iterrows():

        if not row["meaningful_activity"]:
            streak += 1
        else:
            streak = 0

        if streak >= 12:
            return row["month"]

    return pd.NaT


def build_survival_dataset(df):
    rows = []

    for repo_id, group in df.groupby("repo_id"):

        group = group.sort_values("month").reset_index(drop=True)

        event_month = find_event_month(group)

        start_month = group["month"].min()
        last_month = group["month"].max()

        if pd.notna(event_month):

            duration_months = (
                event_month.year - start_month.year
            ) * 12 + (
                event_month.month - start_month.month
            )

            event = 1

        else:

            duration_months = (
                last_month.year - start_month.year
            ) * 12 + (
                last_month.month - start_month.month
            )

            event = 0

        rows.append({
            "repo_id": repo_id,
            "full_name": group["full_name"].iloc[0],
            "language": group["language"].iloc[0],
            "start_month": start_month.strftime("%Y-%m"),
            "end_month": last_month.strftime("%Y-%m"),
            "event_month": (
                event_month.strftime("%Y-%m")
                if pd.notna(event_month)
                else None
            ),
            "duration_months": duration_months,
            "event": event,
        })

    return pd.DataFrame(rows)


def build_prediction_targets(df):
    rows = []

    for repo_id, group in df.groupby("repo_id"):

        group = group.sort_values("month").reset_index(drop=True)

        event_month = find_event_month(group)

        for index, row in group.iterrows():

            observation_month = row["month"]

            future = group[
                group["month"] > observation_month
            ].copy()

            if len(future) < 12:
                continue

            future_12m = future.head(12)

            future_event = False

            if pd.notna(event_month):

                future_event = (
                    event_month > observation_month
                    and event_month <= future_12m["month"].max()
                )

            rows.append({
                "repo_id": repo_id,
                "full_name": row["full_name"],
                "language": row["language"],
                "observation_month": (
                    observation_month.strftime("%Y-%m")
                ),
                "inactive_within_12m": int(future_event),
            })

    return pd.DataFrame(rows)


def validate_survival_dataset(df):
    assert len(df) > 0

    assert df["repo_id"].nunique() == 5

    assert df["event"].isin([0, 1]).all()

    assert (df["duration_months"] >= 0).all()

    assert df["repo_id"].duplicated().sum() == 0

    event_rows = df[df["event"] == 1]

    for _, row in event_rows.iterrows():
        assert pd.notna(row["event_month"])


def validate_prediction_targets(df):
    assert len(df) > 0

    assert df["inactive_within_12m"].isin([0, 1]).all()

    duplicates = df.duplicated(
        subset=["repo_id", "observation_month"]
    ).sum()

    assert duplicates == 0


def main():

    print("Building survival and prediction targets...\n")

    df = load_data()

    print(f"Input rows: {len(df)}")

    df = remove_partial_months(df)

    print(f"Complete-month rows: {len(df)}")

    print("\nBuilding survival dataset...")

    survival = build_survival_dataset(df)

    validate_survival_dataset(survival)

    survival.to_csv(
        SURVIVAL_OUTPUT,
        index=False,
    )

    print(f"Survival rows: {len(survival)}")
    print(
        f"Events: {survival['event'].sum()}"
    )

    print("\nBuilding prediction targets...")

    prediction = build_prediction_targets(df)

    validate_prediction_targets(prediction)

    prediction.to_csv(
        PREDICTION_OUTPUT,
        index=False,
    )

    print(
        f"Prediction rows: {len(prediction)}"
    )

    print(
        f"Positive targets: "
        f"{prediction['inactive_within_12m'].sum()}"
    )

    print(
        f"Negative targets: "
        f"{(prediction['inactive_within_12m'] == 0).sum()}"
    )

    print("\nSurvival dataset:")
    print(survival.to_string(index=False))

    print("\nSaved:")
    print(f"  {SURVIVAL_OUTPUT}")
    print(f"  {PREDICTION_OUTPUT}")


if __name__ == "__main__":
    main()