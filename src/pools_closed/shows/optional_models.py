from typing import Any, Self
from pydantic import ModelWrapValidatorHandler, PrivateAttr, model_validator
from pydantic import BaseModel, ConfigDict, Field

class Show(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    title: str | Any = Field(default=None, union_mode='left_to_right')
    slug: str | Any = Field(default=None, union_mode='left_to_right')
    poster: str | Any = Field(default=None, union_mode='left_to_right')
    url: str | Any = Field(default=None, union_mode='left_to_right')
    full_seasons: bool | Any = Field(None, alias='fullSeasons', union_mode='left_to_right')

class FeaturedShow(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    title: str | Any = Field(default=None, union_mode='left_to_right')
    slug: str | Any = Field(default=None, union_mode='left_to_right')
    poster: str | Any = Field(default=None, union_mode='left_to_right')
    url: str | Any = Field(default=None, union_mode='left_to_right')
    full_seasons: bool | Any = Field(None, alias='fullSeasons', union_mode='left_to_right')
    id: str | Any = Field(default=None, union_mode='left_to_right')
    alignment: str | Any = Field(default=None, union_mode='left_to_right')
    color: str | Any = Field(default=None, union_mode='left_to_right')
    image: str | Any = Field(default=None, union_mode='left_to_right')

class ShowsModel(BaseModel):
    model_config = ConfigDict(extra='ignore', defer_build=True)
    description: str | Any = Field(default=None, union_mode='left_to_right')
    shows: list[Show] | Any = Field(default=None, union_mode='left_to_right')
    thumbnail: str | Any = Field(default=None, union_mode='left_to_right')
    title: str | Any = Field(default=None, union_mode='left_to_right')
    featured_show: FeaturedShow | Any = Field(None, alias='featuredShow', union_mode='left_to_right')
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
