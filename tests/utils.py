# TODO: Validate
"""Helpers shared by every endpoint's tests.

Nothing here knows about a particular endpoint. What an endpoint's own test file
brings is the ids it downloads, the model it parses into and what it expects to
find; recording a response and reading it back is the same either way.

A recording is filed under the name of the model that reads it, which is what
lets `generate_models.py` build each model from everything recorded for it.
"""

from __future__ import annotations

import json
import operator
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal

import pytest
from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import Callable

    from pools_closed.exceptions import PoolsClosedError

type Dump = dict[str, Any] | list[Any]
type Category = Literal["Multipage", "Error"] | None

FILES_PATH = Path(__file__).parent / "_files"
"""Where the recorded responses live."""

_INVALID_FILE_NAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
"""Characters Windows does not allow in a file name."""

_RESERVED_FILE_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)},
)
"""Device names Windows reserves and cannot be used as a file name."""


# TODO: Validate
def sanitized_file_name(name: str | int) -> str:
    """Turn a name into a file name that is valid on Windows.

    Invalid characters are replaced with an underscore, trailing dots and spaces
    are stripped because Windows silently drops them, and reserved device names
    are suffixed so they stay usable.
    """
    sanitized = _INVALID_FILE_NAME_CHARS.sub("_", str(name)).rstrip(". ")
    if not sanitized:
        return "_"
    if sanitized.partition(".")[0].upper() in _RESERVED_FILE_NAMES:
        return f"{sanitized}_"
    return sanitized


# TODO: Validate
class RecordedEndpoint:
    """What an endpoint's tests share: recording a response and reading it back."""

    MODEL: ClassVar[type[BaseModel]]
    """The model the recorded responses are read with."""

    UPDATE_FREQUENCY: ClassVar[timedelta] = timedelta(days=7)
    """How long a recording stands before it is downloaded again."""

    IGNORED: ClassVar[tuple[str, ...]] = ()
    SAME_TYPE: ClassVar[tuple[str, ...]] = ()
    SORTED: ClassVar[tuple[str, ...]] = ()
    LESS_THAN: ClassVar[tuple[str, ...]] = ()
    LESS_THAN_OR_EQUAL: ClassVar[tuple[str, ...]] = ()
    GREATER_THAN: ClassVar[tuple[str, ...]] = ()
    GREATER_THAN_OR_EQUAL: ClassVar[tuple[str, ...]] = ()

    # TODO: Validate
    @classmethod
    def recorded_path(cls, name: str | int, category: Category = None) -> Path:
        """Return where a response for `name` is recorded."""
        file_name = f"{sanitized_file_name(name)}.json"
        model_name = cls.MODEL.__name__
        if category:
            return FILES_PATH / f"{category}s" / model_name / file_name
        return FILES_PATH / model_name / file_name

    # TODO: Validate
    @classmethod
    def recorded_content(cls, name: str | int, category: Category = None) -> str:
        """Return the recorded response for `name` as it was served."""
        return cls.recorded_path(name, category).read_text(encoding="utf-8")

    # TODO: Validate
    @classmethod
    def write_file(cls, path: Path, content: str) -> None:
        """Write `content`, making the folders it goes in if they are missing."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # TODO: Validate
    @classmethod
    def recorded_age(cls, name: str | int, category: Category = None) -> timedelta:
        """Return how long ago the recording for `name` was last written."""
        modified = cls.recorded_path(name, category).stat().st_mtime
        return datetime.now(UTC) - datetime.fromtimestamp(modified, UTC)

    # TODO: Validate
    @classmethod
    def recorded_documents(
        cls,
        name: str | int,
        category: Category = None,
    ) -> list[str]:
        """Return the recording as the documents the endpoint was served."""
        content = cls.recorded_content(name, category)
        if category == "Multipage":
            # A walk is recorded as the list of pages it was served, so each is
            # written back out on its own.
            return [json.dumps(page) for page in json.loads(content)]
        return [content]

    # TODO: Validate
    @classmethod
    def load_models(
        cls,
        name: str | int,
        category: Category = None,
    ) -> list[BaseModel]:
        """Read the recording for `name` into one model per document."""
        return [
            cls.MODEL.model_validate_json(document)
            for document in cls.recorded_documents(name, category)
        ]

    # TODO: Validate
    @classmethod
    def dump_documents(cls, documents: list[str], category: Category = None) -> str:
        """Return the text a set of downloaded documents is recorded as."""
        if category == "Multipage":
            return json.dumps([json.loads(page) for page in documents], indent=2)
        return documents[0]

    # TODO: Validate
    @classmethod
    def download_test(
        cls,
        name: str | int,
        download: Callable[[], str | list[str]],
        category: Category = None,
    ) -> None:
        """Test that the structure of what the API answers does not change."""
        recorded_path = cls.recorded_path(name, category)

        def downloaded_documents() -> list[str]:
            downloaded = download()
            return [downloaded] if isinstance(downloaded, str) else downloaded

        # Nothing recorded yet, so there is nothing to hold the download against.
        if not recorded_path.exists():
            cls.write_file(
                recorded_path,
                cls.dump_documents(downloaded_documents(), category),
            )
            return

        if cls.recorded_age(name, category) < cls.UPDATE_FREQUENCY:
            pytest.skip("The recorded files are up to date.")

        recorded_models = cls.load_models(name, category)
        new_documents = downloaded_documents()
        new_models = [cls.MODEL.model_validate_json(page) for page in new_documents]

        if differences := cls.differences(recorded_models, new_models):
            new_path = recorded_path.with_name(f"{name}.new.json")
            cls.write_file(new_path, cls.dump_documents(new_documents, category))
            reported = "\n".join(differences)
            pytest.fail(
                f"The downloaded file for {name} does not match the recorded "
                f"one. The old file was kept and the new one saved as "
                f"{new_path.name}.\n{reported}",
            )

        recorded_path.touch()

    # TODO: Validate
    @classmethod
    def parse_test(cls, name: str | int, category: Category = None) -> None:
        """Test that the recording still reads into the model it did before."""
        current = [
            model.model_dump(mode="json") for model in cls.load_models(name, category)
        ]
        expected = cls.expected_dump(name, current, category)
        assert current == expected

    # TODO: Validate
    @classmethod
    def expected_model_path(cls, name: str | int, category: Category = None) -> Path:
        """Return where the dump a recording is expected to read into is kept."""
        file_name = f"{sanitized_file_name(name)}.json"
        model_name = cls.MODEL.__name__
        root = Path(__file__).parent / "_expected_model_dumps"
        if category:
            return root / f"{category}s" / model_name / file_name
        return root / model_name / file_name

    # TODO: Validate
    @classmethod
    def expected_dump(
        cls,
        name: str | int,
        current: list[Dump],
        category: Category = None,
    ) -> list[Dump]:
        """Return the dump `name` is expected to read into, recording a first one."""
        path = cls.expected_model_path(name, category)
        if not path.exists():
            # Nothing recorded to compare against, so what was just parsed is
            # written down and stands as what is expected from now on.
            cls.write_file(path, json.dumps(current, indent=2))
            return current
        return json.loads(path.read_text(encoding="utf-8"))

    # TODO: Validate
    @classmethod
    def error_test(
        cls,
        name: str | int,
        download: Callable[[], object],
        error: type[PoolsClosedError],
    ) -> None:
        """Test that a request nothing is under is refused, and record the refusal."""
        if cls.recorded_path(name, "Error").exists():
            pytest.skip(f"Already recorded for {cls.MODEL.__name__}/{name}")
        with pytest.raises(error) as excinfo:
            download()
        response = excinfo.value.response
        content = response if isinstance(response, str) else json.dumps(response or "")
        cls.write_file(cls.recorded_path(name, "Error"), content)

    # TODO: Validate
    @classmethod
    def differences(
        cls,
        old_value: object,
        new_value: object,
        field_path: str = "",
        field_id: str = "",
    ) -> list[str]:
        """List every field of the model whose value moved in a way it may not."""
        if field_id in cls.IGNORED:
            return []

        if field_id in cls.SAME_TYPE:
            old_type = type(old_value).__name__
            new_type = type(new_value).__name__
            moved = f"{field_path}: was a {old_type}, now a {new_type}"
            return [] if old_type == new_type else [moved]

        if isinstance(old_value, BaseModel) and isinstance(new_value, BaseModel):
            model_name = type(old_value).__name__
            return [
                difference
                for name in type(old_value).model_fields
                for difference in cls.differences(
                    getattr(old_value, name),
                    getattr(new_value, name),
                    f"{field_path}.{name}" if field_path else name,
                    f"{model_name}.{name}",
                )
            ]

        if isinstance(old_value, list) and isinstance(new_value, list):
            if len(old_value) != len(new_value):
                held = f"held {len(old_value)} items, now holds {len(new_value)}"
                return [f"{field_path}: {held}"]
            # The API returns some lists in whatever order it likes, so they are
            # sorted before being held against each other.
            old_items = sorted(old_value) if field_id in cls.SORTED else old_value
            new_items = sorted(new_value) if field_id in cls.SORTED else new_value
            return [
                difference
                for index, (old_item, new_item) in enumerate(
                    zip(old_items, new_items, strict=True),
                )
                for difference in cls.differences(
                    old_item,
                    new_item,
                    f"{field_path}[{index}]",
                    field_id,
                )
            ]

        ordering = next(
            (
                comparison
                for names, comparison in (
                    (cls.LESS_THAN, operator.lt),
                    (cls.LESS_THAN_OR_EQUAL, operator.le),
                    (cls.GREATER_THAN, operator.gt),
                    (cls.GREATER_THAN_OR_EQUAL, operator.ge),
                )
                if field_id in names
            ),
            None,
        )
        # Only numbers are ordered. A field named under one of the comparisons
        # that holds anything else has to come back as it was.
        if (
            ordering is not None
            and isinstance(old_value, int | float)
            and isinstance(new_value, int | float)
        ):
            allowed = ordering(old_value, new_value)
            reason = f"which {ordering.__name__} does not allow"
        else:
            allowed = old_value == new_value
            reason = "and it may not change"

        moved = f"{field_path}: was {old_value!r}, now {new_value!r}, {reason}"
        return [] if allowed else [moved]
