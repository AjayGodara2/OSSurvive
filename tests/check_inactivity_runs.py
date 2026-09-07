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


def longest_inactive_run(group):
    inactive = group[ACTIVITY_COLUMNS].sum(axis=1).eq(0)

    max_run = 0
    current_run = 0

    for is_inactive in inactive:
        if is_inactive:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0

    return max_run


def main():
    df = pd.read_csv(INPUT_FILE)

    print("Longest consecutive inactive runs:\n")

    for repo, group in df.groupby("full_name"):
        group = group.sort_values("month")

        longest = longest_inactive_run(group)

        print(f"{repo}: {longest} months")


if __name__ == "__main__":
    main()