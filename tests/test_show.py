# TODO: Validate
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pools_closed.exceptions import ShowNotFoundError
from pools_closed.show.models import ShowModel
from tests.utils import RecordedEndpoint

if TYPE_CHECKING:
    from pools_closed import PoolsClosed

SLUGS = [
    # https://www.adultswim.com/videos/robot-chicken
    pytest.param("robot-chicken", id="a show with many seasons"),
    # https://www.adultswim.com/videos/our-bodies
    pytest.param("our-bodies", id="an online original"),
]


# TODO: Validate
class ShowTest(RecordedEndpoint):
    MODEL = ShowModel
    # Episodes come and go from the site as their licenses run out.
    IGNORED = ("ShowModel.seasons", "ShowModel.episode_count")


# TODO: Validate
@pytest.mark.parametrize("slug", SLUGS)
def test_download(client: PoolsClosed, slug: str) -> None:
    ShowTest.download_test(slug, lambda: client.show.download(slug))


# TODO: Validate
@pytest.mark.parametrize("slug", SLUGS)
def test_parse(client: PoolsClosed, slug: str) -> None:
    show = client.show.load(ShowTest.recorded_content(slug))
    assert show.slug == slug
    assert show.seasons
    for season in show.seasons:
        assert season.number is not None
        assert all(episode.title for episode in season.episodes)


# TODO: Validate
@pytest.mark.parametrize(
    "slug",
    [pytest.param("show-that-does-not-exist", id="show that does not exist")],
)
def test_download_invalid(client: PoolsClosed, slug: str) -> None:
    ShowTest.error_test(
        slug,
        lambda: client.show.download(slug),
        ShowNotFoundError,
    )
