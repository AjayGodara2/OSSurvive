from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/raw/repositories.csv")

LANGUAGES = {
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "C++",
    "C",
    "Go",
    "Rust",
    "Ruby",
    "PHP",
}

STAR_BANDS = {
    "0-100": (0, 100),
    "101-1K": (101, 1_000),
    "1K-10K": (1_001, 10_000),
    "10K-50K": (10_001, 50_000),
    "50K+": (50_001, float("inf")),
}

MIN_AGE_DAYS = 365


def expected_star_band(stars: int) -> str:
    """Return the expected star band for a repository."""

    for label, (lower, upper) in STAR_BANDS.items():
        if lower <= stars <= upper:
            return label

    raise ValueError(f"Invalid star count: {stars}")


def main():
    print("=" * 70)
    print("OSSurvive - Repository Sample Validation")
    print("=" * 70)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # ---------------------------------------------------------
    # Required columns
    # ---------------------------------------------------------

    required_columns = {
        "repo_id",
        "owner",
        "name",
        "full_name",
        "language",
        "created_at",
        "updated_at",
        "stars",
        "forks",
        "open_issues",
        "archived",
        "age_days",
        "html_url",
        "star_band",
    }

    missing_columns = required_columns - set(df.columns)

    print("\nRequired columns:")
    print(f"  Missing: {len(missing_columns)}")

    assert not missing_columns, (
        f"Missing columns: {missing_columns}"
    )

    # ---------------------------------------------------------
    # Duplicate repositories
    # ---------------------------------------------------------

    duplicate_repo_ids = df["repo_id"].duplicated().sum()
    duplicate_full_names = df["full_name"].duplicated().sum()

    print("\nDuplicates:")
    print(f"  Duplicate repo_id: {duplicate_repo_ids}")
    print(f"  Duplicate full_name: {duplicate_full_names}")

    assert duplicate_repo_ids == 0
    assert duplicate_full_names == 0

    # ---------------------------------------------------------
    # Missing values
    # ---------------------------------------------------------

    missing_values = df[list(required_columns)].isna().sum().sum()

    print("\nMissing required values:")
    print(f"  {missing_values}")

    assert missing_values == 0

    # ---------------------------------------------------------
    # Language validation
    # ---------------------------------------------------------

    invalid_languages = sorted(
        set(df["language"]) - LANGUAGES
    )

    print("\nLanguages:")
    print(f"  Invalid languages: {invalid_languages}")

    assert not invalid_languages

    # ---------------------------------------------------------
    # Repository age
    # ---------------------------------------------------------

    too_young = (
        df["age_days"] < MIN_AGE_DAYS
    ).sum()

    print("\nRepository age:")
    print(f"  Younger than 1 year: {too_young}")

    assert too_young == 0

    # ---------------------------------------------------------
    # Fork validation
    # ---------------------------------------------------------

    # repository_selection.py explicitly searches with fork:false.
    # We still inspect the stored fork count for anomalies.
    negative_forks = (
        df["forks"] < 0
    ).sum()

    print("\nFork data:")
    print(f"  Negative fork counts: {negative_forks}")

    assert negative_forks == 0

    # ---------------------------------------------------------
    # Star validation
    # ---------------------------------------------------------

    negative_stars = (
        df["stars"] < 0
    ).sum()

    print("\nStars:")
    print(f"  Negative star counts: {negative_stars}")

    assert negative_stars == 0

    # ---------------------------------------------------------
    # Star-band validation
    # ---------------------------------------------------------

    expected_bands = df["stars"].apply(
        expected_star_band
    )

    invalid_star_bands = (
        expected_bands != df["star_band"]
    ).sum()

    print("\nStar bands:")
    print(
        f"  Incorrect assignments: "
        f"{invalid_star_bands}"
    )

    assert invalid_star_bands == 0

    # ---------------------------------------------------------
    # Language × star-band coverage
    # ---------------------------------------------------------

    cross_tab = pd.crosstab(
        df["language"],
        df["star_band"],
    ).reindex(
        index=sorted(LANGUAGES),
        columns=list(STAR_BANDS.keys()),
        fill_value=0,
    )

    print("\nLanguage × star band:")
    print(cross_tab.to_string())

    # ---------------------------------------------------------
    # Archived repositories
    # ---------------------------------------------------------

    archived_counts = (
        df["archived"]
        .value_counts()
        .sort_index()
    )

    print("\nArchived repositories:")
    print(archived_counts.to_string())

    # ---------------------------------------------------------
    # Age distribution
    # ---------------------------------------------------------

    print("\nAge distribution (years):")
    print(
        (df["age_days"] / 365)
        .describe()
        .to_string()
    )

    # ---------------------------------------------------------
    # Star distribution
    # ---------------------------------------------------------

    print("\nStar distribution:")
    print(
        df["stars"]
        .describe()
        .to_string()
    )

    # ---------------------------------------------------------
    # Concentration check
    # ---------------------------------------------------------

    print("\nTop 20 repositories by stars:")

    print(
        df[
            [
                "full_name",
                "language",
                "star_band",
                "stars",
                "archived",
            ]
        ]
        .sort_values("stars", ascending=False)
        .head(20)
        .to_string(index=False)
    )

    # ---------------------------------------------------------
    # Final validation
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("VALIDATION RESULT")
    print("=" * 70)

    print("\nAll structural validation checks passed.")
    print("Dataset is ready for suitability analysis.")


if __name__ == "__main__":
    main()