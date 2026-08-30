# TODO: Validate
"""Rebuilds ShowModel."""

from __future__ import annotations

import logging

from get_around import build_client_automatically

from generate.constants import FILES_PATH, POOLS_CLOSED_PATH
from generate.utils import download_if_missing, load_ids, rebuild_model
from pools_closed import PoolsClosed
from pools_closed.show import read_show

SLUGS = load_ids("ShowModel")
"""The shows the model is built from."""


# TODO: Validate
def generate_show(client: PoolsClosed) -> None:
    """Rebuild ShowModel."""
    for slug in SLUGS:
        download_if_missing(
            FILES_PATH,
            "ShowModel",
            slug,
            lambda slug=slug: client.show.download(slug),
        )
    rebuild_model(FILES_PATH, POOLS_CLOSED_PATH, "ShowModel", read_show)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generate_show(PoolsClosed(build_client_automatically()))
