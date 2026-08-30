from typing import Any, Self
from pydantic import ModelWrapValidatorHandler, PrivateAttr, model_validator
from pydantic import ConfigDict
from pydantic import BaseModel, Field

class Show(BaseModel):
    model_config = ConfigDict(defer_build=True)
    title: str
    slug: str | None = None
    poster: str
    url: str
    full_seasons: bool | None = Field(None, alias='fullSeasons')

class FeaturedShow(BaseModel):
    model_config = ConfigDict(defer_build=True)
    title: str
    slug: str
    poster: str
    url: str
    full_seasons: bool = Field(..., alias='fullSeasons')
    id: str
    alignment: str
    color: str
    image: str

class ShowsModel(BaseModel):
    model_config = ConfigDict(defer_build=True)
    description: str
    shows: list[Show]
    thumbnail: str
    title: str
    featured_show: FeaturedShow = Field(..., alias='featuredShow')
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
