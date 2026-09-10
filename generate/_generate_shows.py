from __future__ import annotations

import logging

from get_around import build_client_automatically
from good_ass_pydantic_integrator.recordings import (
    RecordingId,
    download_missing,
    load_ids,
    rebuild_model,
)

from generate.constants import GENERATOR_PATHS
from pools_closed import PoolsClosed
from pools_closed.shows import extract_shows

MODEL_NAME = "ShowsModel"


# TODO: Validate
class ShowsId(RecordingId[PoolsClosed]):
    page: str

    # TODO: Validate
    def download(self, client: PoolsClosed) -> str:
        return client.shows.download()


PAGES = load_ids(GENERATOR_PATHS, MODEL_NAME, ShowsId)


# TODO: Validate
def generate_shows(client: PoolsClosed) -> None:
    download_missing(GENERATOR_PATHS, MODEL_NAME, PAGES, client)
    rebuild_model(GENERATOR_PATHS, MODEL_NAME, ShowsId, extract_shows)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generate_shows(PoolsClosed(build_client_automatically()))
