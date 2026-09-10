from typing import Self
from pydantic import ModelWrapValidatorHandler, PrivateAttr, model_validator
from typing import Any
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

class Metadata(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    description: str | None = None
    thumbnail: str | None = None
    title: str | None = None

class Hero(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    image_alignment: str | None = Field(None, alias='imageAlignment')
    image_url: str | None = Field(None, alias='imageURL')
    marathon_callout: str | None = Field(None, alias='marathonCallout')
    marathon_image_url: str | None = Field(None, alias='marathonImageURL')
    mobile_image_url: str | None = Field(None, alias='mobileImageURL')

class Theme(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    background_color: str | None = Field(None, alias='backgroundColor')

class Marathon(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    id: str | None = None
    slug: str | None = None

class Episode(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    id: str | None = None
    collection_slug: str | None = Field(None, alias='collectionSlug')
    auth: bool | None = None
    description: str | None = None
    duration: int | float | None = None
    episode_number: int | None = Field(None, alias='episodeNumber')
    expiration_date: Any | AwareDatetime | None = Field(None, alias='expirationDate')
    first_airing: Any | AwareDatetime | None = Field(None, alias='firstAiring')
    launch_date: AwareDatetime | None = Field(None, alias='launchDate')
    poster: str | None = None
    season_number: int | None = Field(None, alias='seasonNumber')
    slug: str | None = None
    title: str | None = None
    tv_rating: str | None = Field(None, alias='tvRating')
    type: str | None = None

class Season(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    number: int | None = None
    name: str | None = None
    episode_count: int | None = Field(None, alias='episodeCount')
    episodes: list[Episode] | None = None

class ShowModel(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    slug: str | None = None
    title: str | None = None
    headline: Any | None = None
    tune_in: str | None = Field(None, alias='tuneIn')
    season_order: str | None = Field(None, alias='seasonOrder')
    include_clips: bool | None = Field(None, alias='includeClips')
    adfuel_registry_url: str | None = Field(None, alias='adfuelRegistryURL')
    collection_id: str | None = Field(None, alias='collectionId')
    collection_type: str | None = Field(None, alias='collectionType')
    tv_rating: str | None = Field(None, alias='tvRating')
    episode_count: int | None = Field(None, alias='episodeCount')
    metadata: Any | Metadata | None = None
    hero: Hero | None = None
    theme: Theme | None = None
    marathon: Any | Marathon | None = None
    seasons: list[Season] | None = None
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
