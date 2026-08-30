# TODO: Validate
from __future__ import annotations

from typing import TYPE_CHECKING

from pools_closed.shows.models import ShowsModel
from tests.utils import RecordedEndpoint

if TYPE_CHECKING:
    from pools_closed import PoolsClosed

RECORDING_NAME = "videos"


# TODO: Validate
class ShowsTest(RecordedEndpoint):
    MODEL = ShowsModel
    # The site rotates the show it features and adds shows as they air.
    IGNORED = ("ShowsModel.featured_show", "ShowsModel.shows")


# TODO: Validate
def test_download(client: PoolsClosed) -> None:
    ShowsTest.download_test(RECORDING_NAME, client.shows.download)


# TODO: Validate
def test_parse(client: PoolsClosed) -> None:
    shows = client.shows.load(ShowsTest.recorded_content(RECORDING_NAME))
    assert shows.shows
    assert all(show.url for show in shows.shows)
