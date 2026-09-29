# ruff: noqa: D100
from typing import TYPE_CHECKING

from good_ass_pydantic_integrator import load

from .optional_models import ShowsModel as OptionalModel
from .strict_models import ShowsModel as StrictModel

if TYPE_CHECKING:
    from .strict_models import (
        FeaturedShow,
        Show,
        ShowsModel,
    )
else:
    from .optional_models import (
        FeaturedShow,
        Show,
        ShowsModel,
    )

__all__ = [
    "FeaturedShow",
    "Show",
    "ShowsModel",
    "model_validate_json",
]


def model_validate_json(data: str | bytes | object, log_id: str) -> ShowsModel:
    """Read a downloaded file into ShowsModel."""
    return load.model_validate_json(StrictModel, OptionalModel, data, log_id)
