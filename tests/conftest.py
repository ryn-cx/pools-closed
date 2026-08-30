# TODO: Validate
import pytest
from get_around import build_client_automatically

from pools_closed import PoolsClosed


# TODO: Validate
@pytest.fixture(scope="session")
def client() -> PoolsClosed:
    return PoolsClosed(build_client_automatically())
