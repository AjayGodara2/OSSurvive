import pandas as pd

INPUT_FILE = "data/historical/repository_monthly_features.csv"

ACTIVITY_COLUMNS = [
    "commits",
    "contributors",
    "pr_opened",
    "pr_closed",
    "pr_merged",
    "issues_opened",
    "issues_closed",
]


def find_inactive_periods(group):
    group = group.sort_values("month").reset_index(drop=True)

    inactive = group[ACTIVITY_COLUMNS].sum(axis=1).eq(0)

    periods = []
    start = None

    for i, is_inactive in enumerate(inactive):
        if is_inactive and start is None:
            start = i

        if (not is_inactive or i == len(inactive) - 1) and start is not None:
            end = i if is_inactive else i - 1

            periods.append({
                "start": group.loc[start, "month"],
                "end": group.loc[end, "month"],
                "months": end - start + 1,
            })

            start = None

    return periods


def main():
    df = pd.read_csv(INPUT_FILE)

    print("Inactive periods:\n")

    for repo, group in df.groupby("full_name"):
        periods = find_inactive_periods(group)

        print(f"{repo}:")

        if not periods:
            print("  No inactive periods")
        else:
            for period in periods:
                print(
                    f"  {period['start']} -> {period['end']} "
                    f"({period['months']} months)"
                )

        print()


if __name__ == "__main__":
    main()