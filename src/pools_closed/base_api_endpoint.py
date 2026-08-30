# TODO: Validate
"""Contains BaseEndpoint."""

from __future__ import annotations

from inspect import Parameter, signature
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from pools_closed import PoolsClosed


# TODO: Validate
class BaseEndpoint:
    """Base class for API endpoints."""

    WEBSITE = "Adult Swim"

    # TODO: Validate
    @property
    def default_log_id(self) -> str:
        """Get the log id of the endpoint itself, without any arguments."""
        return f"{self.WEBSITE} - {self.__class__.__name__}"

    # TODO: Validate
    def __init__(self, client: PoolsClosed) -> None:
        """Initialize the endpoint with the PoolsClosed client."""
        self._client = client

    # TODO: Validate
    @staticmethod
    def non_default_args(
        func: Callable[..., Any],
        values: dict[str, Any],
    ) -> dict[str, Any]:
        """Return the args that are changed from their default values."""
        return {
            name: values[name]
            for name, param in signature(func).parameters.items()
            if param.default is not Parameter.empty
            and name in values
            and values[name] != param.default
        }

    # TODO: Validate
    def get_log_id(self, func: Callable[..., Any], values: dict[str, Any]) -> str:
        """Get the log id.

        Example: Adult Swim - ClassName (arg1='value1' arg2='value2')
        """
        required = {
            name: values[name]
            for name, param in signature(func).parameters.items()
            if param.default is Parameter.empty and name in values
        }
        set_args = {**required, **self.non_default_args(func, values)}
        parts = [
            *(f"{name}={value!r}" for name, value in set_args.items()),
        ]
        if not parts:
            return self.default_log_id
        return f"{self.default_log_id} ({' '.join(parts)})"
