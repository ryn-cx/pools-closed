# TODO: Validate
"""Contains the Show class."""

from __future__ import annotations

import json
from http import HTTPStatus
from logging import NullHandler, getLogger
from typing import Any

from pools_closed.base_api_endpoint import BaseEndpoint
from pools_closed.exceptions import ShowNotFoundError
from pools_closed.show.models import ShowModel, model_validate_json

logger = getLogger(__name__)
logger.addHandler(NullHandler())

VIDEO_FIELDS = """
id
collectionSlug
auth
description
duration
episodeNumber
expirationDate
firstAiring
launchDate
poster
seasonNumber
slug
title
tvRating
type
"""
"""The fields the site reads a video by."""

SHOW_QUERY = f"""
query Show($show: String, $cursor: String) {{
  show(slug: $show) {{
    slug
    title
    headline {{
      launchDate
      link
      text
    }}
    tuneIn
    seasonOrder
    includeClips
    adfuelRegistryURL
    metadata {{
      description
      thumbnail
      title
    }}
    hero {{
      imageAlignment
      imageURL
      marathonCallout
      marathonImageURL
      mobileImageURL
    }}
    theme {{
      backgroundColor
    }}
    marathon {{
      id
      slug
    }}
    collection {{
      id
      type
      tvRating
      seasons(types: EPISODE, liveOnly: true, sort: ASC) {{
        nodes {{
          number
          name
          episodeCount: videos(types: EPISODE, first: 0, liveOnly: false) {{
            totalCount
          }}
          videos(sort: ["episodeNumber", "launchDate:desc"], first: 1000) {{
            nodes {{
              {VIDEO_FIELDS}
            }}
          }}
        }}
      }}
      clipSeasons: seasons(types: CLIP, sort: ASC) {{
        nodes {{
          number
          name
        }}
      }}
      clips: videos(
        after: $cursor
        types: CLIP
        first: 1000
        seasonsOnly: true
        sort: ["seasonNumber", "episodeNumber"]
      ) {{
        pageInfo {{
          endCursor
          hasNextPage
        }}
        nodes {{
          {VIDEO_FIELDS}
        }}
      }}
    }}
  }}
}}
"""
"""What the show page asks for, in the query a download starts with."""

CLIPS_QUERY = f"""
query ShowClips($show: String, $cursor: String) {{
  show(slug: $show) {{
    slug
    collection {{
      id
      clips: videos(
        after: $cursor
        types: CLIP
        first: 1000
        seasonsOnly: true
        sort: ["seasonNumber", "episodeNumber"]
      ) {{
        pageInfo {{
          endCursor
          hasNextPage
        }}
        nodes {{
          {VIDEO_FIELDS}
        }}
      }}
    }}
  }}
}}
"""
"""What a show with more clips than one page holds is asked for the rest by."""


# TODO: Validate
def _episode_seasons(collection: dict[str, Any]) -> list[dict[str, Any]]:
    """Return every season of a show, with the episodes that belong to it."""
    return [
        {
            "number": season["number"],
            "name": season["name"],
            "type": "EPISODE",
            "episodeCount": season["episodeCount"]["totalCount"],
            "episodes": season["videos"]["nodes"],
        }
        for season in collection["seasons"]["nodes"]
    ]


# TODO: Validate
def _clip_seasons(collection: dict[str, Any]) -> list[dict[str, Any]]:
    """Return every clip season of a show, with the clips that belong to it.

    A clip is filed under a season of its own, numbered apart from the seasons
    the episodes are filed under.
    """
    clips_by_season: dict[Any, list[dict[str, Any]]] = {}
    for clip in collection["clips"]["nodes"]:
        clips_by_season.setdefault(clip["seasonNumber"], []).append(clip)
    return [
        {
            "number": season["number"],
            "name": season["name"],
            "type": "CLIP",
            "episodeCount": len(clips_by_season.get(season["number"], [])),
            "episodes": clips_by_season.get(season["number"], []),
        }
        for season in collection["clipSeasons"]["nodes"]
    ]


# TODO: Validate
def extract_show(data: str) -> dict[str, Any]:
    """Parse a downloaded show into the show, its seasons and its episodes."""
    show = json.loads(data)["show"]
    collection = show["collection"] or {}
    episode_seasons = _episode_seasons(collection) if collection else []
    clip_seasons = _clip_seasons(collection) if collection else []
    return {
        "slug": show["slug"],
        "title": show["title"],
        "headline": show["headline"],
        "tuneIn": show["tuneIn"],
        "seasonOrder": show["seasonOrder"],
        "includeClips": show["includeClips"],
        "adfuelRegistryURL": show["adfuelRegistryURL"],
        "collectionId": collection.get("id"),
        "collectionType": collection.get("type"),
        "tvRating": collection.get("tvRating"),
        "episodeCount": sum(season["episodeCount"] for season in episode_seasons),
        "metadata": show["metadata"],
        "hero": show["hero"],
        "theme": show["theme"],
        "marathon": show["marathon"],
        "seasons": episode_seasons + clip_seasons,
    }


# TODO: Validate
class Show(BaseEndpoint):
    """Contains the show file, which is a show with its seasons and episodes.

    Source: https://www.adultswim.com/videos/{slug}
    """

    # TODO: Validate
    def __call__(self, slug: str) -> ShowModel:
        """Download and parse the show file."""
        log_id = self.get_log_id(self.__call__, locals())
        return self.load(self.download(slug), log_id)

    # TODO: Validate
    def download(self, slug: str) -> str:
        """Download the show, its seasons, its episodes and its clips.

        Raises:
            ShowNotFoundError: If no show is under that slug.
        """
        log_id = self.get_log_id(self.download, locals())
        document = self._client.graphql(SHOW_QUERY, {"show": slug}, log_id)
        self._validate_download(document, slug)
        self._download_remaining_clips(document, slug, log_id)
        return json.dumps(document)

    # TODO: Validate
    def _download_remaining_clips(
        self,
        document: dict[str, Any],
        slug: str,
        log_id: str,
    ) -> None:
        """Add the clips that did not fit in the first page to a downloaded show."""
        collection = document["show"]["collection"]
        while collection and collection["clips"]["pageInfo"]["hasNextPage"]:
            page = self._client.graphql(
                CLIPS_QUERY,
                {"show": slug, "cursor": collection["clips"]["pageInfo"]["endCursor"]},
                log_id,
            )
            clips = page["show"]["collection"]["clips"]
            collection["clips"]["nodes"] += clips["nodes"]
            collection["clips"]["pageInfo"] = clips["pageInfo"]

    # TODO: Validate
    @staticmethod
    def _validate_download(document: dict[str, Any], slug: str) -> None:
        """Check that the show is the one that was asked for.

        Raises:
            ShowNotFoundError: If no show is under that slug.
        """
        show = document["show"]
        if show is None or show["slug"] != slug:
            raise ShowNotFoundError(slug, HTTPStatus.OK, document)

    # TODO: Validate
    def load(self, data: str, log_id: str = "") -> ShowModel:
        """Load a show page into its model."""
        return model_validate_json(extract_show(data), log_id or self.default_log_id)
