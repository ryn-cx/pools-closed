from typing import Any, Self
from pydantic import ModelWrapValidatorHandler, PrivateAttr, model_validator
from pydantic import BaseModel, ConfigDict, Field

class Show(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    title: str | None = None
    slug: str | None = None
    poster: str | None = None
    url: str | None = None
    full_seasons: bool | None = Field(None, alias='fullSeasons')

class FeaturedShow(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    title: str | None = None
    slug: str | None = None
    poster: str | None = None
    url: str | None = None
    full_seasons: bool | None = Field(None, alias='fullSeasons')
    id: str | None = None
    alignment: str | None = None
    color: str | None = None
    image: str | None = None

class ShowsModel(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    description: str | None = None
    shows: list[Show] | None = None
    thumbnail: str | None = None
    title: str | None = None
    featured_show: FeaturedShow | None = Field(None, alias='featuredShow')
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
