from typing import Any, Self
from pydantic import ModelWrapValidatorHandler, PrivateAttr, model_validator
from pydantic import ConfigDict
from pydantic import AwareDatetime, BaseModel, Field

class Metadata(BaseModel):
    model_config = ConfigDict(defer_build=True)
    description: str
    thumbnail: str
    title: str

class Hero(BaseModel):
    model_config = ConfigDict(defer_build=True)
    image_alignment: str = Field(..., alias='imageAlignment')
    image_url: str = Field(..., alias='imageURL')
    marathon_callout: str | None = Field(..., alias='marathonCallout')
    marathon_image_url: str | None = Field(..., alias='marathonImageURL')
    mobile_image_url: str = Field(..., alias='mobileImageURL')

class Theme(BaseModel):
    model_config = ConfigDict(defer_build=True)
    background_color: str = Field(..., alias='backgroundColor')

class Marathon(BaseModel):
    model_config = ConfigDict(defer_build=True)
    id: str
    slug: str

class Episode(BaseModel):
    model_config = ConfigDict(defer_build=True)
    id: str
    collection_slug: str = Field(..., alias='collectionSlug')
    auth: bool
    description: str
    duration: int | float
    episode_number: int | None = Field(..., alias='episodeNumber')
    expiration_date: AwareDatetime | None = Field(..., alias='expirationDate')
    first_airing: AwareDatetime | None = Field(..., alias='firstAiring')
    launch_date: AwareDatetime = Field(..., alias='launchDate')
    poster: str
    season_number: int = Field(..., alias='seasonNumber')
    slug: str
    title: str
    tv_rating: str | None = Field(..., alias='tvRating')
    type: str

class Season(BaseModel):
    model_config = ConfigDict(defer_build=True)
    number: int
    name: str
    episode_count: int = Field(..., alias='episodeCount')
    episodes: list[Episode]

class ShowModel(BaseModel):
    model_config = ConfigDict(defer_build=True)
    slug: str
    title: str
    headline: None
    tune_in: str | None = Field(..., alias='tuneIn')
    season_order: str | None = Field(..., alias='seasonOrder')
    include_clips: bool | None = Field(..., alias='includeClips')
    adfuel_registry_url: str | None = Field(..., alias='adfuelRegistryURL')
    collection_id: str = Field(..., alias='collectionId')
    collection_type: str | None = Field(..., alias='collectionType')
    tv_rating: str | None = Field(..., alias='tvRating')
    episode_count: int = Field(..., alias='episodeCount')
    metadata: Metadata | None
    hero: Hero
    theme: Theme
    marathon: Marathon | None
    seasons: list[Season]
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
