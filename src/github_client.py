import os
import time
from typing import Any, Dict, Optional
from dotenv import load_dotenv

import requests

load_dotenv()
class GitHubClient:
    """
    Wrapper around the GitHub REST API.

    Handles:
    - API requests
    - Authentication
    - Basic error handling
    - Rate-limit detection
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")

        self.session = requests.Session()

        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Send a GET request to the GitHub API.
        """

        url = (
            endpoint
            if endpoint.startswith("http")
            else f"{self.BASE_URL}{endpoint}"
        )

        response = self.session.get(
            url,
            params=params,
            timeout=30
        )

        # Check for rate limit
        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining")

            if remaining == "0":
                reset_time = int(
                    response.headers.get(
                        "X-RateLimit-Reset",
                        time.time()
                    )
                )

                wait_seconds = max(
                    reset_time - int(time.time()),
                    0
                )

                raise RuntimeError(
                    f"GitHub API rate limit reached. "
                    f"Try again in approximately "
                    f"{wait_seconds} seconds."
                )

        # Check for other errors
        if not response.ok:
            raise RuntimeError(
                f"GitHub API error {response.status_code}: "
                f"{response.text}"
            )

        return response.json()

    def get_rate_limit(self) -> Dict[str, Any]:
        """
        Get current GitHub API rate-limit information.
        """

        return self.get("/rate_limit")