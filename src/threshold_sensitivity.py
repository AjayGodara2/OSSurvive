import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter


INPUT_FILE = "data/historical/repository_engineered_features.csv"
OUTPUT_CSV = "data/historical/survival_threshold_comparison.csv"
OUTPUT_PLOT = "data/historical/survival_threshold_comparison.png"

THRESHOLDS = [6, 12, 18]


def find_event_month(group, threshold):
    group = group.sort_values("month").reset_index(drop=True)

    streak = 0

    for _, row in group.iterrows():
        if not row["meaningful_activity"]:
            streak += 1
        else:
            streak = 0

        if streak >= threshold:
            return row["month"]

    return pd.NaT


def month_difference(start, end):
    return (
        (end.year - start.year) * 12
        + (end.month - start.month)
    )


def build_survival_data(df, threshold):
    rows = []

    for repo_id, group in df.groupby("repo_id"):
        group = group.sort_values("month").reset_index(drop=True)

        start_month = group["month"].min()
        end_month = group["month"].max()

        event_month = find_event_month(group, threshold)

        if pd.notna(event_month):
            duration = month_difference(
                start_month,
                event_month
            )
            event = 1
        else:
            duration = month_difference(
                start_month,
                end_month
            )
            event = 0

        rows.append({
            "repo_id": repo_id,
            "full_name": group["full_name"].iloc[0],
            "threshold_months": threshold,
            "start_month": start_month.strftime("%Y-%m"),
            "end_month": end_month.strftime("%Y-%m"),
            "event_month": (
                event_month.strftime("%Y-%m")
                if pd.notna(event_month)
                else None
            ),
            "duration_months": duration,
            "event": event,
        })

    return pd.DataFrame(rows)


def main():

    print("Running inactivity threshold sensitivity analysis...\n")

    df = pd.read_csv(INPUT_FILE)
    df["month"] = pd.to_datetime(df["month"])

    # Remove partial current month
    df = df[~df["is_partial_month"]].copy()

    all_results = []

    for threshold in THRESHOLDS:

        result = build_survival_data(
            df,
            threshold
        )

        all_results.append(result)

        events = result["event"].sum()
        censored = len(result) - events

        print(
            f"{threshold}-month threshold:"
        )
        print(f"  Events: {events}")
        print(f"  Censored: {censored}")

        for _, row in result[result["event"] == 1].iterrows():
            print(
                f"  Event: "
                f"{row['full_name']} "
                f"→ {row['event_month']}"
            )

        print()

    comparison = pd.concat(
        all_results,
        ignore_index=True
    )

    comparison.to_csv(
        OUTPUT_CSV,
        index=False
    )

    # ---------------------------------------------------------
    # Kaplan-Meier comparison
    # ---------------------------------------------------------

    plt.figure(figsize=(10, 6))

    for threshold in THRESHOLDS:

        result = comparison[
            comparison["threshold_months"] == threshold
        ]

        kmf = KaplanMeierFitter()

        kmf.fit(
            durations=result["duration_months"],
            event_observed=result["event"],
            label=f"{threshold}-month threshold"
        )

        kmf.plot_survival_function()

    plt.xlabel("Months since project start")
    plt.ylabel("Probability of remaining active")
    plt.title(
        "OSSurvive Survival Curves "
        "under Different Inactivity Thresholds"
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_PLOT,
        dpi=150
    )

    plt.close()

    print("Sensitivity analysis complete!")
    print(f"\nSaved comparison to: {OUTPUT_CSV}")
    print(f"Saved plot to: {OUTPUT_PLOT}")


if __name__ == "__main__":
    main()