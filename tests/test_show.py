# TODO: Validate
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pools_closed.exceptions import ShowNotFoundError

if TYPE_CHECKING:
    from pools_closed import PoolsClosed

SLUGS = [
    # https://www.adultswim.com/videos/robot-chicken
    pytest.param("robot-chicken", id="a show with many seasons"),
    # https://www.adultswim.com/videos/our-bodies
    pytest.param("our-bodies", id="an online original"),
]


# TODO: Validate
@pytest.mark.parametrize("slug", SLUGS)
def test_download(client: PoolsClosed, slug: str) -> None:
    show = client.show(slug)
    assert show.slug == slug
    assert show.seasons
    for season in show.seasons:
        assert season.number is not None
        assert all(episode.title for episode in season.episodes)


# TODO: Validate
def test_download_invalid(client: PoolsClosed) -> None:
    with pytest.raises(ShowNotFoundError):
        client.show.download("show-that-does-not-exist")
