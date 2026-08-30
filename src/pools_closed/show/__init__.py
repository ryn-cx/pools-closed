# TODO: Validate
"""Contains the Show class."""

from __future__ import annotations

import json
from http import HTTPStatus
from logging import NullHandler, getLogger
from typing import Any

from pools_closed.base_api_endpoint import BaseEndpoint
from pools_closed.exceptions import ResourceNotFoundError, ShowNotFoundError
from pools_closed.show.models import ShowModel, model_validate_json

logger = getLogger(__name__)
logger.addHandler(NullHandler())

type ApolloState = dict[str, Any]
"""The Apollo cache a show page was rendered from, keyed by cache id."""


# TODO: Validate
def _resolve(state: ApolloState, value: Any) -> Any:  # noqa: ANN401
    """Return what a value holds, following it into the cache when it is a reference."""
    if isinstance(value, dict) and value.get("type") == "id":
        return state.get(value["id"])
    return value


# TODO: Validate
def _without_typename(value: Any) -> Any:  # noqa: ANN401
    """Return an object without the type name Apollo files it under."""
    if not isinstance(value, dict):
        return value
    return {name: field for name, field in value.items() if name != "__typename"}


# TODO: Validate
def _connections(
    state: ApolloState,
    holder: dict[str, Any],
    field_name: str,
) -> list[dict[str, Any]]:
    """Return what every field named `field_name` on `holder` points at.

    A field is cached under the name it was queried with, arguments and all, so
    the same field shows up once per set of arguments the page asked for.
    """
    return [
        resolved
        for name, value in holder.items()
        if name.startswith(f"{field_name}(")
        and isinstance(resolved := _resolve(state, value), dict)
    ]


# TODO: Validate
def _episodes(state: ApolloState, season: dict[str, Any]) -> list[dict[str, Any]]:
    """Return every episode of a season, in episode order."""
    episodes_by_id: dict[str, dict[str, Any]] = {}
    for connection in _connections(state, season, "videos"):
        for node in connection.get("nodes") or []:
            episode = _without_typename(_resolve(state, node))
            if isinstance(episode, dict) and "title" in episode:
                episodes_by_id[episode["id"]] = episode
    return sorted(
        episodes_by_id.values(),
        key=lambda episode: (
            episode.get("episodeNumber") is None,
            episode.get("episodeNumber") or 0,
        ),
    )


# TODO: Validate
def _episode_count(state: ApolloState, season: dict[str, Any]) -> int | None:
    """Return how many episodes the site counts for a season."""
    counts = [
        connection["totalCount"]
        for connection in _connections(state, season, "videos")
        if "totalCount" in connection
    ]
    return max(counts) if counts else None


# TODO: Validate
def _seasons(state: ApolloState, collection: dict[str, Any]) -> list[dict[str, Any]]:
    """Return every season of a show, in season order, with its episodes.

    A page asks for its seasons more than once, sorted differently each time, so
    a season that shows up twice is kept once with the most episodes found for
    it.
    """
    seasons_by_number: dict[Any, dict[str, Any]] = {}
    for connection in _connections(state, collection, "seasons"):
        for node in connection.get("nodes") or []:
            season = _resolve(state, node)
            if not isinstance(season, dict):
                continue
            episodes = _episodes(state, season)
            recorded = seasons_by_number.get(season.get("number"))
            if recorded is not None and len(recorded["episodes"]) >= len(episodes):
                continue
            seasons_by_number[season.get("number")] = {
                "number": season.get("number"),
                "name": season.get("name"),
                "episodeCount": _episode_count(state, season),
                "episodes": episodes,
            }
    return sorted(
        seasons_by_number.values(),
        key=lambda season: (season["number"] is None, season["number"] or 0),
    )


# TODO: Validate
def read_show(data: str) -> dict[str, Any]:
    """Parse a downloaded show page into the show, its seasons and its episodes.

    A show page is rendered from an Apollo cache, which is every object the page
    needs filed flat under its own key and pointed at by reference. This walks
    those references and writes the show back out as one object.

    `load` reads a downloaded page with this, and the model generator reads the
    recorded pages with it too, so the two can never disagree.
    """
    state = json.loads(data)["props"]["pageProps"]["__APOLLO_STATE__"]
    show = _resolve(state, next(iter(state["ROOT_QUERY"].values())))
    collection = _resolve(state, show.get("collection")) or {}
    seasons = _seasons(state, collection)
    return {
        "slug": show.get("slug"),
        "title": show.get("title"),
        "headline": show.get("headline"),
        "tuneIn": show.get("tuneIn"),
        "seasonOrder": show.get("seasonOrder"),
        "includeClips": show.get("includeClips"),
        "adfuelRegistryURL": show.get("adfuelRegistryURL"),
        "collectionId": collection.get("id"),
        "collectionType": collection.get("type"),
        "tvRating": collection.get("tvRating"),
        "episodeCount": sum(season["episodeCount"] or 0 for season in seasons),
        "metadata": _without_typename(_resolve(state, show.get("metadata"))),
        "hero": _without_typename(_resolve(state, show.get("hero"))),
        "theme": _without_typename(_resolve(state, show.get("theme"))),
        "marathon": _without_typename(_resolve(state, show.get("marathon"))),
        "seasons": seasons,
    }


# TODO: Validate
class Show(BaseEndpoint):
    """Manage the show file, which is a show with its seasons and episodes.

    Source: https://www.adultswim.com/videos/{slug}
    """

    # TODO: Validate
    def __call__(self, slug: str) -> ShowModel:
        """Look the show up and return the model it is read into."""
        log_id = self.get_log_id(self.__call__, locals())
        return self.load(self.download(slug), log_id)

    # TODO: Validate
    def download(self, slug: str) -> str:
        """Download the show page.

        Raises:
            ShowNotFoundError: If no show is under that slug.
        """
        log_id = self.get_log_id(self.download, locals())
        try:
            response = self._client.download(
                endpoint=f"videos/{slug}",
                params={},
                headers={"referer": "https://www.adultswim.com/videos"},
                log_id=log_id,
            )
        except ResourceNotFoundError as err:
            raise ShowNotFoundError(slug, err.status_code, err.response) from err
        return self._validate_download(response, slug)

    # TODO: Validate
    @staticmethod
    def _validate_download(response: str, slug: str) -> str:
        """Check that the page is the one that was asked for."""
        if read_show(response)["slug"] != slug:
            raise ShowNotFoundError(slug, HTTPStatus.OK, response)
        return response

    # TODO: Validate
    def load(self, data: str, log_id: str = "") -> ShowModel:
        """Read a downloaded show page into its model.

        The page is written back out as the show, its seasons and its episodes
        before it is read.
        """
        return model_validate_json(read_show(data), log_id or self.default_log_id)
