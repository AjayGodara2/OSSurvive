import pandas as pd
import matplotlib.pyplot as plt

from lifelines import KaplanMeierFitter


INPUT_FILE = (
    "data/historical/repository_survival_dataset.csv"
)

OUTPUT_DATA = (
    "data/historical/kaplan_meier_survival.csv"
)

OUTPUT_PLOT = (
    "data/historical/kaplan_meier_curve.png"
)


def main():

    print("Running Kaplan-Meier survival analysis...\n")

    df = pd.read_csv(INPUT_FILE)

    print(f"Repositories: {len(df)}")
    print(f"Events: {df['event'].sum()}")
    print(
        f"Censored: "
        f"{(df['event'] == 0).sum()}"
    )

    # ---------------------------------------------------------
    # Kaplan-Meier
    # ---------------------------------------------------------

    kmf = KaplanMeierFitter()

    kmf.fit(
        durations=df["duration_months"],
        event_observed=df["event"],
    )

    survival_table = kmf.survival_function_.reset_index()

    survival_table.columns = [
        "duration_months",
        "survival_probability",
    ]

    survival_table.to_csv(
        OUTPUT_DATA,
        index=False,
    )

    # ---------------------------------------------------------
    # Plot
    # ---------------------------------------------------------

    plt.figure(figsize=(10, 6))

    kmf.plot_survival_function()

    plt.xlabel("Months since project start")
    plt.ylabel("Probability of remaining active")
    plt.title(
        "Kaplan-Meier Survival Curve — OSSurvive Pilot"
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_PLOT,
        dpi=150,
    )

    plt.close()

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print("\nKaplan-Meier analysis complete!")

    print(
        f"Median survival time: "
        f"{kmf.median_survival_time_} months"
    )

    print(
        f"Survival probability at 12 months: "
        f"{kmf.predict(12):.3f}"
    )

    print(
        f"Survival probability at 24 months: "
        f"{kmf.predict(24):.3f}"
    )

    print(
        f"Survival probability at 36 months: "
        f"{kmf.predict(36):.3f}"
    )

    print(
        f"\nSaved survival table to: "
        f"{OUTPUT_DATA}"
    )

    print(
        f"Saved plot to: "
        f"{OUTPUT_PLOT}"
    )


if __name__ == "__main__":
    main()