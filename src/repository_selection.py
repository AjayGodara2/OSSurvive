from pathlib import Path
import random
from datetime import datetime, timezone

import pandas as pd

from src.github_client import GitHubClient


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

LANGUAGES = [
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
]

STAR_BANDS = [
    ("0-100", "0..100"),
    ("101-1K", "101..1000"),
    ("1K-10K", "1001..10000"),
    ("10K-50K", "10001..50000"),
    ("50K+", "50001..*"),
]

MIN_REPOSITORY_AGE_DAYS = 365

TARGET_PER_STRATUM = 10
CANDIDATES_PER_STRATUM = 30

RANDOM_SEED = 42

OUTPUT_FILE = Path("data/raw/repositories.csv")


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def calculate_age_days(created_at: str) -> int:
    """Calculate repository age in days."""

    created = datetime.fromisoformat(
        created_at.replace("Z", "+00:00")
    )

    now = datetime.now(timezone.utc)

    return (now - created).days


def extract_repository_metadata(repo: dict) -> dict:
    """Extract fields needed by OSSurvive."""

    created_at = repo["created_at"]

    return {
        "repo_id": repo["id"],
        "owner": repo["owner"]["login"],
        "name": repo["name"],
        "full_name": repo["full_name"],
        "language": repo["language"],
        "created_at": created_at,
        "updated_at": repo["updated_at"],
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "open_issues": repo["open_issues_count"],
        "archived": repo["archived"],
        "age_days": calculate_age_days(created_at),
        "html_url": repo["html_url"],
    }


def search_repositories(
    client: GitHubClient,
    language: str,
    star_range: str,
) -> list[dict]:
    """Search GitHub for repositories in one sampling stratum."""

    query = (
        f"language:{language} "
        f"stars:{star_range} "
        f"fork:false "
        f"created:<{datetime.now(timezone.utc).date()}"
    )

    print(
        f"Searching {language:<12} | "
        f"{star_range:<12}"
    )

    results = client.get(
        "/search/repositories",
        params={
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": CANDIDATES_PER_STRATUM,
            "page": 1,
        },
    )

    return results.get("items", [])


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("OSSurvive - Resumable Stratified Repository Sampling")
    print("=" * 70)

    random.seed(RANDOM_SEED)

    client = GitHubClient()

    # -----------------------------------------------------
    # Load existing dataset if it exists
    # -----------------------------------------------------

    if OUTPUT_FILE.exists():

        print(f"\nExisting dataset found: {OUTPUT_FILE}")

        df_existing = pd.read_csv(OUTPUT_FILE)

        repositories = df_existing.to_dict("records")

        seen_repo_ids = set(
            df_existing["repo_id"].astype(int)
        )

        completed_strata = set(
            zip(
                df_existing["language"],
                df_existing["star_band"],
            )
        )

        print(
            f"Existing repositories: {len(repositories)}"
        )

        print(
            f"Completed strata: "
            f"{len(completed_strata)} / "
            f"{len(LANGUAGES) * len(STAR_BANDS)}"
        )

    else:

        print("\nNo existing dataset found.")

        repositories = []
        seen_repo_ids = set()
        completed_strata = set()

    # -----------------------------------------------------
    # Process each language / star-band stratum
    # -----------------------------------------------------

    total_strata = len(LANGUAGES) * len(STAR_BANDS)
    processed = len(completed_strata)

    for language in LANGUAGES:

        for star_label, star_range in STAR_BANDS:

            stratum = (language, star_label)

            # -------------------------------------------------
            # Skip already completed strata
            # -------------------------------------------------

            if stratum in completed_strata:

                print(
                    f"SKIP {language:<12} | "
                    f"{star_label:<12} | already complete"
                )

                continue

            print(
                f"\n[{processed + 1}/{total_strata}]"
            )

            try:

                items = search_repositories(
                    client=client,
                    language=language,
                    star_range=star_range,
                )

            except RuntimeError as error:

                print(
                    f"\nSTOPPING SAFELY: {error}"
                )

                print(
                    "\nProgress has already been saved."
                )

                break

            candidates = []

            for repo in items:

                age_days = calculate_age_days(
                    repo["created_at"]
                )

                if age_days < MIN_REPOSITORY_AGE_DAYS:
                    continue

                if repo["id"] in seen_repo_ids:
                    continue

                metadata = extract_repository_metadata(repo)

                metadata["star_band"] = star_label

                candidates.append(metadata)

            # -------------------------------------------------
            # Random sampling
            # -------------------------------------------------

            random.shuffle(candidates)

            selected = candidates[:TARGET_PER_STRATUM]

            print(
                f"Candidates: {len(candidates):2d} | "
                f"Selected: {len(selected):2d}"
            )

            for repo in selected:

                seen_repo_ids.add(repo["repo_id"])

                repositories.append(repo)

            # -------------------------------------------------
            # Mark stratum complete
            # -------------------------------------------------

            completed_strata.add(stratum)
            processed += 1

            # -------------------------------------------------
            # Save immediately
            # -------------------------------------------------

            df = pd.DataFrame(repositories)

            df = df.sort_values(
                by=[
                    "language",
                    "star_band",
                    "stars",
                ],
                ascending=[
                    True,
                    True,
                    False,
                ],
            ).reset_index(drop=True)

            OUTPUT_FILE.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            df.to_csv(
                OUTPUT_FILE,
                index=False,
            )

            print(
                f"Saved progress: {len(df)} repositories"
            )

        else:
            # Continue to next language.
            continue

        # Inner loop broke because of rate limit.
        # Stop the outer loop as well.
        break

    # ---------------------------------------------------------
    # Final dataset
    # ---------------------------------------------------------

    df = pd.DataFrame(repositories)

    if df.empty:
        raise RuntimeError(
            "No repositories available."
        )

    df = df.sort_values(
        by=[
            "language",
            "star_band",
            "stars",
        ],
        ascending=[
            True,
            True,
            False,
        ],
    ).reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("CURRENT DATASET")
    print("=" * 70)

    print(
        f"\nRepositories: {len(df)}"
    )

    print(
        f"Completed strata: "
        f"{len(completed_strata)} / "
        f"{total_strata}"
    )

    print("\nBy language:")

    print(
        df["language"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nBy star band:")

    print(
        df["star_band"]
        .value_counts()
        .reindex(
            [band[0] for band in STAR_BANDS]
        )
        .fillna(0)
        .astype(int)
        .to_string()
    )

    print("\nBy language and star band:")

    print(
        pd.crosstab(
            df["language"],
            df["star_band"],
        )
        .reindex(
            index=LANGUAGES,
            columns=[
                band[0]
                for band in STAR_BANDS
            ],
            fill_value=0,
        )
        .to_string()
    )

    print("\nArchived:")

    print(
        df["archived"]
        .value_counts()
        .to_string()
    )

    print("\nAge distribution (years):")

    print(
        (df["age_days"] / 365)
        .describe()
        .to_string()
    )

    print("\nStar distribution:")

    print(
        df["stars"]
        .describe()
        .to_string()
    )


if __name__ == "__main__":
    main()