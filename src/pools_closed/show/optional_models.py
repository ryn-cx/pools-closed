from typing import Self
from pydantic import ModelWrapValidatorHandler, PrivateAttr, model_validator
from typing import Any
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

class Metadata(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    description: str | Any = Field(default=None, union_mode='left_to_right')
    thumbnail: str | Any = Field(default=None, union_mode='left_to_right')
    title: str | Any = Field(default=None, union_mode='left_to_right')

class Hero(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    image_alignment: str | Any = Field(None, alias='imageAlignment', union_mode='left_to_right')
    image_url: str | Any = Field(None, alias='imageURL', union_mode='left_to_right')
    marathon_callout: str | Any = Field(None, alias='marathonCallout', union_mode='left_to_right')
    marathon_image_url: str | Any = Field(None, alias='marathonImageURL', union_mode='left_to_right')
    mobile_image_url: str | Any = Field(None, alias='mobileImageURL', union_mode='left_to_right')

class Theme(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    background_color: str | Any = Field(None, alias='backgroundColor', union_mode='left_to_right')

class Marathon(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    id: str | Any = Field(default=None, union_mode='left_to_right')
    slug: str | Any = Field(default=None, union_mode='left_to_right')

class Episode(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    id: str | Any = Field(default=None, union_mode='left_to_right')
    collection_slug: str | Any = Field(None, alias='collectionSlug', union_mode='left_to_right')
    auth: bool | Any = Field(default=None, union_mode='left_to_right')
    description: str | Any = Field(default=None, union_mode='left_to_right')
    duration: int | float | Any = Field(default=None, union_mode='left_to_right')
    episode_number: int | Any = Field(None, alias='episodeNumber', union_mode='left_to_right')
    expiration_date: AwareDatetime | Any = Field(None, alias='expirationDate', union_mode='left_to_right')
    first_airing: AwareDatetime | Any = Field(None, alias='firstAiring', union_mode='left_to_right')
    launch_date: AwareDatetime | Any = Field(None, alias='launchDate', union_mode='left_to_right')
    poster: str | Any = Field(default=None, union_mode='left_to_right')
    season_number: int | Any = Field(None, alias='seasonNumber', union_mode='left_to_right')
    slug: str | Any = Field(default=None, union_mode='left_to_right')
    title: str | Any = Field(default=None, union_mode='left_to_right')
    tv_rating: str | Any = Field(None, alias='tvRating', union_mode='left_to_right')
    type: str | Any = Field(default=None, union_mode='left_to_right')

class Season(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    number: int | Any = Field(default=None, union_mode='left_to_right')
    name: str | Any = Field(default=None, union_mode='left_to_right')
    type: str | Any = Field(default=None, union_mode='left_to_right')
    episode_count: int | Any = Field(None, alias='episodeCount', union_mode='left_to_right')
    episodes: list[Episode] | Any = Field(default=None, union_mode='left_to_right')

class ShowModel(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    slug: str | Any = Field(default=None, union_mode='left_to_right')
    title: str | Any = Field(default=None, union_mode='left_to_right')
    headline: Any | None = None
    tune_in: str | Any = Field(None, alias='tuneIn', union_mode='left_to_right')
    season_order: str | Any = Field(None, alias='seasonOrder', union_mode='left_to_right')
    include_clips: bool | Any = Field(None, alias='includeClips', union_mode='left_to_right')
    adfuel_registry_url: str | Any = Field(None, alias='adfuelRegistryURL', union_mode='left_to_right')
    collection_id: str | Any = Field(None, alias='collectionId', union_mode='left_to_right')
    collection_type: str | Any = Field(None, alias='collectionType', union_mode='left_to_right')
    tv_rating: str | Any = Field(None, alias='tvRating', union_mode='left_to_right')
    episode_count: int | Any = Field(None, alias='episodeCount', union_mode='left_to_right')
    metadata: Metadata | Any = Field(default=None, union_mode='left_to_right')
    hero: Hero | Any = Field(default=None, union_mode='left_to_right')
    theme: Theme | Any = Field(default=None, union_mode='left_to_right')
    marathon: Marathon | Any = Field(default=None, union_mode='left_to_right')
    seasons: list[Season] | Any = Field(default=None, union_mode='left_to_right')
    _raw_input: Any = PrivateAttr(default=None)

    @model_validator(mode='wrap')
    @classmethod
    def _capture_raw_input(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        """Validate the model and keep the input it was built from."""
        model = handler(data)
        model._raw_input = data
        return model

    @property
    def raw_input(self) -> Any:
        """The input this model was validated from, as it was handed over."""
        return self._raw_input
