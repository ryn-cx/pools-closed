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
from pools_closed.show import extract_show

MODEL_NAME = "ShowModel"


# TODO: Validate
class ShowId(RecordingId[PoolsClosed]):
    slug: str

    # TODO: Validate
    def download(self, client: PoolsClosed) -> str:
        return client.show.download(self.slug)


SLUGS = load_ids(GENERATOR_PATHS, MODEL_NAME, ShowId)


# TODO: Validate
def generate_show(client: PoolsClosed) -> None:
    download_missing(GENERATOR_PATHS, MODEL_NAME, SLUGS, client)
    rebuild_model(GENERATOR_PATHS, MODEL_NAME, ShowId, extract_show)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generate_show(PoolsClosed(build_client_automatically()))
