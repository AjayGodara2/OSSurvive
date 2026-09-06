import pandas as pd


FEATURES_FILE = (
    "data/historical/repository_engineered_features.csv"
)

TARGETS_FILE = (
    "data/historical/repository_prediction_targets.csv"
)

OUTPUT_FILE = (
    "data/historical/repository_modeling_dataset.csv"
)


def main():

    print("Building modeling dataset...\n")

    features = pd.read_csv(FEATURES_FILE)
    targets = pd.read_csv(TARGETS_FILE)

    features["observation_month"] = (
        pd.to_datetime(features["month"])
        .dt.strftime("%Y-%m")
    )

    print(f"Feature rows: {len(features)}")
    print(f"Target rows: {len(targets)}")

    modeling = features.merge(
        targets[
            [
                "repo_id",
                "observation_month",
                "inactive_within_12m",
            ]
        ],
        on=["repo_id", "observation_month"],
        how="inner",
        validate="one_to_one",
    )

    modeling = modeling[
        ~modeling["is_partial_month"]
    ].copy()

    modeling = modeling.sort_values(
        ["observation_month", "repo_id"]
    ).reset_index(drop=True)

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    assert len(modeling) == len(targets)

    assert modeling.duplicated(
        ["repo_id", "observation_month"]
    ).sum() == 0

    assert modeling["inactive_within_12m"].isin(
        [0, 1]
    ).all()

    assert modeling["observation_month"].notna().all()

    assert modeling["inactive_within_12m"].notna().all()

    # No partial months
    assert not modeling["is_partial_month"].any()

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    modeling.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nModeling dataset complete!")

    print(f"Rows: {len(modeling)}")
    print(
        f"Repositories: "
        f"{modeling['repo_id'].nunique()}"
    )

    print(
        f"Positive targets: "
        f"{modeling['inactive_within_12m'].sum()}"
    )

    print(
        f"Negative targets: "
        f"{(modeling['inactive_within_12m'] == 0).sum()}"
    )

    print(
        "\nObservation range:"
    )

    print(
        f"  {modeling['observation_month'].min()}"
        f" → "
        f"{modeling['observation_month'].max()}"
    )

    print(
        f"\nSaved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()