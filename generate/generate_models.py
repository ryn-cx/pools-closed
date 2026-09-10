from __future__ import annotations

import logging

from get_around import build_client_automatically
from good_ass_pydantic_integrator.recordings import generate_all

import generate
from pools_closed import PoolsClosed
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generate_all(generate, PoolsClosed(build_client_automatically()))
