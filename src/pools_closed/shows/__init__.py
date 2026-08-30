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
def read_shows(data: str) -> dict[str, Any]:
    """Parse a downloaded videos page and return the part that lists the shows.

    `load` reads a downloaded page with this, and the model generator reads the
    recorded pages with it too, so the two can never disagree.
    """
    page: dict[str, Any] = json.loads(data)
    return page["props"]["pageProps"]


# TODO: Validate
class Shows(BaseEndpoint):
    """Manage the videos page, which lists every show on the site.

    Source: https://www.adultswim.com/videos
    """

    # TODO: Validate
    def __call__(self) -> ShowsModel:
        """Look the videos page up and return the model it is read into."""
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
        """Read a downloaded videos page into its model."""
        return model_validate_json(read_shows(data), log_id or self.default_log_id)
