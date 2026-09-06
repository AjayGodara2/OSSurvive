import os
import re
import time
from typing import Any, Dict, Optional
from urllib.parse import unquote

from dotenv import load_dotenv
import requests


load_dotenv()


class GitHubClient:
    """
    Wrapper around the GitHub REST API.

    Handles:
    - API requests
    - Authentication
    - Rate-limit detection
    - Page-based pagination
    - Cursor-based pagination
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

    def _handle_response(self, response):
        """Handle common GitHub API errors."""

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

        if not response.ok:
            raise RuntimeError(
                f"GitHub API error {response.status_code}: "
                f"{response.text}"
            )

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

        self._handle_response(response)

        return response.json()

    def get_all(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> list:
        """
        Fetch all pages using standard page-based pagination.
        """

        params = dict(params or {})
        params["per_page"] = 100

        results = []
        page = 1

        while True:
            page_params = dict(params)
            page_params["page"] = page

            data = self.get(
                endpoint,
                params=page_params
            )

            if not data:
                break

            results.extend(data)

            if len(data) < 100:
                break

            page += 1

        return results

    def get_all_cursor(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> list:
        """
        Fetch all pages using cursor-based pagination.

        GitHub may return an `after` cursor in the Link header
        for large datasets.
        """

        params = dict(params or {})
        params["per_page"] = 100

        results = []
        after = None

        while True:
            page_params = dict(params)

            if after:
                page_params["after"] = after

            url = (
                endpoint
                if endpoint.startswith("http")
                else f"{self.BASE_URL}{endpoint}"
            )

            response = self.session.get(
                url,
                params=page_params,
                timeout=30
            )

            self._handle_response(response)

            data = response.json()

            if not data:
                break

            results.extend(data)

            link_header = response.headers.get("Link", "")

            if 'rel="next"' not in link_header:
                break

            match = re.search(
                r"after=([^&>]+)",
                link_header
            )

            if not match:
                break

            after = unquote(match.group(1))

        return results

    def get_rate_limit(self) -> Dict[str, Any]:
        """
        Get current GitHub API rate-limit information.
        """

        return self.get("/rate_limit")