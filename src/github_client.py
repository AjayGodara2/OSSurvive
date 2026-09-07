import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
import requests


load_dotenv()


class GitHubClient:

    BASE_URL = "https://api.github.com"

    MAX_WORKERS = 5
    MAX_RETRIES = 4
    REQUEST_TIMEOUT = 45

    def __init__(self, token: Optional[str] = None):

        self.token = token or os.getenv("GITHUB_TOKEN")

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

        if self.token:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.token}"
                }
            )

    # =========================================================
    # RESPONSE HANDLING
    # =========================================================

    def _handle_response(self, response):

        if response.status_code == 403:

            remaining = response.headers.get(
                "X-RateLimit-Remaining"
            )

            if remaining == "0":

                reset_time = int(
                    response.headers.get(
                        "X-RateLimit-Reset",
                        time.time(),
                    )
                )

                wait_seconds = max(
                    reset_time - int(time.time()),
                    0,
                )

                raise RuntimeError(
                    "GitHub API rate limit reached. "
                    f"Try again in approximately "
                    f"{wait_seconds} seconds."
                )

        if response.status_code == 422:

            raise RuntimeError(
                f"GitHub API error 422: "
                f"{response.text}"
            )

        if not response.ok:

            raise RuntimeError(
                f"GitHub API error "
                f"{response.status_code}: "
                f"{response.text}"
            )

    # =========================================================
    # REQUEST WITH RETRIES
    # =========================================================

    def _request_with_retry(
        self,
        method,
        url,
        params=None,
        session=None,
    ):

        session = session or self.session

        for attempt in range(
            self.MAX_RETRIES
        ):

            try:

                response = session.request(
                    method,
                    url,
                    params=params,
                    timeout=self.REQUEST_TIMEOUT,
                )

                # ---------------------------------------------
                # Rate limit
                # ---------------------------------------------

                if response.status_code == 429:

                    retry_after = response.headers.get(
                        "Retry-After"
                    )

                    if retry_after:

                        wait_seconds = int(
                            retry_after
                        )

                    else:

                        wait_seconds = 2 ** attempt

                    print(
                        "  Rate limited. "
                        f"Waiting {wait_seconds}s..."
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue

                # ---------------------------------------------
                # Temporary server errors
                # ---------------------------------------------

                if response.status_code in {
                    500,
                    502,
                    503,
                    504,
                }:

                    wait_seconds = 2 ** attempt

                    print(
                        "  Temporary GitHub error "
                        f"{response.status_code}. "
                        f"Retrying in "
                        f"{wait_seconds}s..."
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue

                # ---------------------------------------------
                # Temporary 403
                # ---------------------------------------------

                if response.status_code == 403:

                    remaining = response.headers.get(
                        "X-RateLimit-Remaining"
                    )

                    if remaining != "0":

                        wait_seconds = 2 ** attempt

                        print(
                            "  Temporary API error. "
                            f"Retrying in "
                            f"{wait_seconds}s..."
                        )

                        time.sleep(
                            wait_seconds
                        )

                        continue

                self._handle_response(
                    response
                )

                return response

            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ) as error:

                if attempt == self.MAX_RETRIES - 1:

                    raise error

                wait_seconds = 2 ** attempt

                print(
                    "  Temporary network/API error. "
                    "Retrying..."
                )

                time.sleep(
                    wait_seconds
                )

        raise RuntimeError(
            "GitHub request failed after "
            f"{self.MAX_RETRIES} attempts."
        )

    # =========================================================
    # BASIC GET
    # =========================================================

    def get(
        self,
        endpoint,
        params=None,
    ):

        url = (
            endpoint
            if endpoint.startswith("http")
            else f"{self.BASE_URL}{endpoint}"
        )

        response = self._request_with_retry(
            "GET",
            url,
            params=params,
        )

        return response.json()

    # =========================================================
    # PAGINATED PAGE REQUEST
    # =========================================================

    def _get_page(
        self,
        url,
        params,
        page,
    ):

        session = requests.Session()

        session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

        if self.token:

            session.headers.update(
                {
                    "Authorization": f"Bearer {self.token}"
                }
            )

        page_params = dict(params)

        page_params["page"] = page

        response = self._request_with_retry(
            "GET",
            url,
            params=page_params,
            session=session,
        )

        return (
            page,
            response.json(),
        )

    # =========================================================
    # FIND LAST PAGE
    # =========================================================

    def _get_last_page(
        self,
        response,
    ):

        link_header = response.headers.get(
            "Link",
            "",
        )

        match = re.search(
            r'<[^>]+[?&]page=(\d+)[^>]*>;\s*rel="last"',
            link_header,
        )

        if match:

            return int(
                match.group(1)
            )

        return None

    # =========================================================
    # NORMAL PAGE-BASED PAGINATION
    # =========================================================

    def _get_all_paginated(
        self,
        endpoint,
        params=None,
    ):

        params = dict(
            params or {}
        )

        params["per_page"] = 100

        url = (
            endpoint
            if endpoint.startswith("http")
            else f"{self.BASE_URL}{endpoint}"
        )

        # -----------------------------------------------------
        # First request
        # -----------------------------------------------------

        first_params = dict(params)

        first_params["page"] = 1

        first_response = self._request_with_retry(
            "GET",
            url,
            params=first_params,
        )

        first_data = first_response.json()

        if not first_data:

            return []

        results = list(
            first_data
        )

        # -----------------------------------------------------
        # Determine number of pages
        # -----------------------------------------------------

        last_page = self._get_last_page(
            first_response
        )

        if last_page is None:

            return results

        if last_page <= 1:

            return results

        print(
            f"    GitHub pages detected: "
            f"{last_page}"
        )

        # -----------------------------------------------------
        # Parallel page collection
        # -----------------------------------------------------

        completed = 1

        pages = range(
            2,
            last_page + 1,
        )

        with ThreadPoolExecutor(
            max_workers=self.MAX_WORKERS
        ) as executor:

            futures = {
                executor.submit(
                    self._get_page,
                    url,
                    params,
                    page,
                ): page
                for page in pages
            }

            page_results = {}

            for future in as_completed(
                futures
            ):

                page, data = future.result()

                page_results[
                    page
                ] = data

                completed += 1

                print(
                    f"    Pages collected: "
                    f"{completed}/{last_page}",
                    end="\r",
                )

        print()

        # -----------------------------------------------------
        # Restore correct page order
        # -----------------------------------------------------

        for page in range(
            2,
            last_page + 1,
        ):

            results.extend(
                page_results.get(
                    page,
                    [],
                )
            )

        return results

    # =========================================================
    # NORMAL PAGINATION
    # =========================================================

    def get_all(
        self,
        endpoint,
        params=None,
    ):

        return self._get_all_paginated(
            endpoint,
            params=params,
        )

    # =========================================================
    # CURSOR-BASED PAGINATION
    #
    # Used for GitHub endpoints that reject normal
    # page-based pagination on very large datasets.
    # =========================================================

    def get_all_cursor(
        self,
        endpoint,
        params=None,
    ):

        params = dict(
            params or {}
        )

        params["per_page"] = 100

        url = (
            endpoint
            if endpoint.startswith("http")
            else f"{self.BASE_URL}{endpoint}"
        )

        results = []

        next_url = url

        next_params = dict(
            params
        )

        while True:

            response = self._request_with_retry(
                "GET",
                next_url,
                params=next_params,
            )

            data = response.json()

            if not data:

                break

            results.extend(
                data
            )

            # -------------------------------------------------
            # GitHub supplies the cursor in the Link header.
            #
            # IMPORTANT:
            # We follow the complete "next" URL instead of
            # manually constructing the cursor.
            # -------------------------------------------------

            link_header = response.headers.get(
                "Link",
                "",
            )

            next_match = re.search(
                r'<([^>]+)>;\s*rel="next"',
                link_header,
            )

            if not next_match:

                break

            next_url = next_match.group(1)

            # The next URL already contains the cursor.
            # Do not send page= or the old parameters again.
            next_params = None

        return results

    # =========================================================
    # RATE LIMIT
    # =========================================================

    def get_rate_limit(self):

        return self.get(
            "/rate_limit"
        )