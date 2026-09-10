# TODO: Validate
"""Contains the Shows class."""

from __future__ import annotations

import json
from logging import NullHandler, getLogger
from typing import Any

from pools_closed.base_api_endpoint import BaseEndpoint
from pools_closed.shows.models import ShowsModel, model_validate_json

logger = getLogger(__name__)
logger.addHandler(NullHandler())


# TODO: Validate
def extract_shows(data: str) -> dict[str, Any]:
    """Parse a downloaded videos page and return the part that lists the shows."""
    page: dict[str, Any] = json.loads(data)
    return page["props"]["pageProps"]


# TODO: Validate
class Shows(BaseEndpoint):
    """Contains the videos page, which lists every show on the site.

    Source: https://www.adultswim.com/videos
    """

    # TODO: Validate
    def __call__(self) -> ShowsModel:
        """Download and parse the videos page file."""
        return self.load(self.download(), self.default_log_id)

    # TODO: Validate
    def download(self) -> str:
        """Download the videos page."""
        return self._client.download(
            endpoint="videos",
            params={},
            headers={"referer": "https://www.adultswim.com/"},
            log_id=self.default_log_id,
        )

    # TODO: Validate
    def load(self, data: str, log_id: str = "") -> ShowsModel:
        """Load a videos file into its model."""
        return model_validate_json(extract_shows(data), log_id or self.default_log_id)
