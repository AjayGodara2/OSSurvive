from src.github_client import GitHubClient


def main():
    print("Testing GitHub API connection...")

    client = GitHubClient()

    rate_limit = client.get_rate_limit()

    core = rate_limit["resources"]["core"]

    print("\nGitHub API connection successful!")
    print(f"Remaining requests: {core['remaining']}")
    print(f"Request limit: {core['limit']}")


if __name__ == "__main__":
    main()