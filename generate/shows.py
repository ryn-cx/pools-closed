# TODO: Validate
"""Rebuilds ShowsModel."""

from __future__ import annotations

import logging

from get_around import build_client_automatically

from generate.constants import FILES_PATH, POOLS_CLOSED_PATH
from generate.utils import download_if_missing, rebuild_model
from pools_closed import PoolsClosed
from pools_closed.shows import read_shows

RECORDING_NAME = "videos"
"""What the videos page is recorded as, since it is asked for without an id."""


# TODO: Validate
def generate_shows(client: PoolsClosed) -> None:
    """Rebuild ShowsModel."""
    download_if_missing(
        FILES_PATH,
        "ShowsModel",
        RECORDING_NAME,
        client.shows.download,
    )
    rebuild_model(FILES_PATH, POOLS_CLOSED_PATH, "ShowsModel", read_shows)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generate_shows(PoolsClosed(build_client_automatically()))
