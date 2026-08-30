# TODO: Validate
"""Contains the PoolsClosed class."""

import re
from http import HTTPStatus
from logging import NullHandler, getLogger
from time import monotonic, sleep
from typing import Any

from get_around import GetAround

from pools_closed.exceptions import ExtractionError, HTTPError, ResourceNotFoundError
from pools_closed.show import Show
from pools_closed.shows import Shows

logger = getLogger(__name__)
logger.addHandler(NullHandler())

API_DOMAIN = "www.adultswim.com"

NEXT_DATA_PATTERN = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(?P<json>.*?)</script>',
    re.DOTALL,
)
"""Where a page keeps the JSON it was rendered from."""


# TODO: Validate
class PoolsClosed:
    """Adult Swim website wrapper."""

    # TODO: Validate
    def __init__(
        self,
        get_around_client: GetAround | None = None,
        sleep_time: float = 0,
    ) -> None:
        """Initializes the PoolsClosed client.

        The client holds one attribute per endpoint, so `client.show(slug)`
        looks a show up and `client.show.download(slug)` and
        `client.show.load(data)` are the halves of it.
        """
        self.sleep_time = sleep_time
        self.get_around_client = get_around_client or GetAround()

        self.shows = Shows(self)
        self.show = Show(self)

    # TODO: Validate
    def _default_headers(self) -> dict[str, str]:
        """Return the headers a browser sends when it asks for a page."""
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "priority": "u=0, i",
        }

    # TODO: Validate
    def download(
        self,
        endpoint: str,
        params: dict[str, Any],
        headers: dict[str, str],
        log_id: str,
    ) -> str:
        """Downloads a page and returns the JSON it was rendered from.

        Adult Swim has no public API. The page is rendered on the server and the
        data it was rendered from is written into it as a `__NEXT_DATA__`
        script, so that script is what a download comes back as.
        """
        logger.debug("Downloading: %s", log_id)
        url = f"https://{API_DOMAIN}/{endpoint}"
        start = monotonic()
        response = self.get_around_client.get(
            url,
            params=params,
            headers={**self._default_headers(), **headers},
            follow_redirects=True,
        )

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ResourceNotFoundError(response.status_code, response.text)
        if response.status_code != HTTPStatus.OK:
            raise HTTPError(response.status_code, response.text)

        logger.debug("Downloaded %s (%.4f s)", log_id, monotonic() - start)
        sleep(self.sleep_time)
        return self._extract_next_data(response.text)

    # TODO: Validate
    @staticmethod
    def _extract_next_data(html: str) -> str:
        """Return the `__NEXT_DATA__` JSON the page was rendered from."""
        match = NEXT_DATA_PATTERN.search(html)
        if match is None:
            raise ExtractionError(html)
        return match.group("json")
