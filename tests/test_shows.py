# TODO: Validate
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pools_closed import PoolsClosed


# TODO: Validate
def test_download(client: PoolsClosed) -> None:
    shows = client.shows()
    assert shows.shows
    assert all(show.url for show in shows.shows)
