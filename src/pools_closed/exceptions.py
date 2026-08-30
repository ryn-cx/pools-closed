# TODO: Validate
"""Exceptions."""

from __future__ import annotations

from typing import Any


# TODO: Validate
class PoolsClosedError(Exception):
    """Base exception for Pool's Closed."""

    response: str | dict[str, Any] | None = None
    """The response that caused the error."""


# TODO: Validate
class HTTPError(PoolsClosedError):
    """Raised when HTTP request fails with unexpected status code."""

    # TODO: Validate
    def __init__(
        self,
        status_code: int,
        response: str | dict[str, Any] | None,
    ) -> None:
        """Initialize the HTTPError with the status code and response body."""
        self.status_code = status_code
        self.response = response
        super().__init__(f"Unexpected response status code: {status_code}")


# TODO: Validate
class ResourceNotFoundError(HTTPError):
    """Raised when the site reports that the requested page does not exist."""


# TODO: Validate
class ShowNotFoundError(ResourceNotFoundError):
    """Raised when the requested show does not exist."""

    # TODO: Validate
    def __init__(
        self,
        slug: str,
        status_code: int,
        response: str | dict[str, Any] | None,
    ) -> None:
        """Initialize with the show slug and the originating response."""
        self.slug = slug
        super().__init__(status_code, response)


# TODO: Validate
class ExtractionError(PoolsClosedError):
    """Raised when the downloaded page carries no __NEXT_DATA__ script."""

    # TODO: Validate
    def __init__(self, response: str) -> None:
        """Initialize with the page the script was looked for in."""
        self.response = response
        super().__init__("The downloaded page carries no __NEXT_DATA__ script")
