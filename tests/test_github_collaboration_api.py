import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.github_client import GitHubClient


def main():
    client = GitHubClient()

    repo = "vuejs/vue"

    print(f"Testing collaboration API for {repo}...")

    issues = client.get(
        f"/repos/{repo}/issues",
        params={
            "state": "all",
            "sort": "created",
            "direction": "asc",
            "since": "2020-01-01T00:00:00Z",
            "per_page": 100,
        },
    )

    print(f"\nIssues returned: {len(issues)}")

    if issues:
        print("\nFirst returned item:")
        print(f"Number: {issues[0]['number']}")
        print(f"Created: {issues[0]['created_at']}")
        print(f"Is PR: {'pull_request' in issues[0]}")

    pull_requests = client.get_all(
        f"/repos/{repo}/pulls",
        params={
            "state": "all",
            "sort": "created",
            "direction": "asc",
        },
    )

    print(f"\nIssues endpoint returned: {len(issues)}")
    print(f"Pull request endpoint returned: {len(pull_requests)}")

    issue_count = 0
    issue_pr_count = 0

    for item in issues:
        if "pull_request" in item:
            issue_pr_count += 1
        else:
            issue_count += 1

    print(f"\nActual issues: {issue_count}")
    print(f"PRs appearing in issues endpoint: {issue_pr_count}")

    if pull_requests:
        first_pr = pull_requests[0]

        print("\nFirst PR:")
        print(f"Number: {first_pr['number']}")
        print(f"Created: {first_pr['created_at']}")
        print(f"Updated: {first_pr['updated_at']}")
        print(f"Merged: {first_pr.get('merged_at')}")
        print(f"Closed: {first_pr.get('closed_at')}")

    print("\nAPI pilot successful!")


if __name__ == "__main__":
    main()