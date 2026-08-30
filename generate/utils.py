# TODO: Validate
"""Helpers for putting a downloaded response where the generator reads it."""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any

from good_ass_pydantic_integrator.generate import (
    generate_model,
    redundant_recordings,
)

from generate.constants import IDS_PATH

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


logger = logging.getLogger(__name__)

type Id = str | int | tuple[str | int | None, ...] | None
"""One id, which is what a response is downloaded with."""

type Ids = list[Id] | dict[str, Id]
"""The ids a model's responses are recorded for.

A mapping is what a model whose recordings are named uses, keyed by that name.
"""


# TODO: Validate
def sanitized_file_name(name: str | int) -> str:
    """Turn a name into a file name that is valid on Windows."""
    sanitized = re.compile(r'[<>:"/\|?*\x00-\x1f]').sub("_", str(name)).rstrip(". ")
    return sanitized or "_"


# TODO: Validate
def download_if_missing(
    files_path: Path,
    model_name: str,
    name: str | int,
    download: Callable[[], str],
    suffix: str = ".json",
) -> None:
    """Download a response into `_files` when it is not recorded yet.

    Args:
        files_path: Where the recorded responses live.
        model_name: The model class name the response is recorded under.
        name: What the response is recorded as.
        download: Downloads the response.
        suffix: The extension the recording is written with. A model read from
            something other than JSON keeps the extension it was served as.
    """
    recorded_path = files_path / model_name / f"{sanitized_file_name(name)}{suffix}"
    if recorded_path.exists():
        return
    logger.info("Downloading %s/%s.", model_name, name)
    recorded_path.parent.mkdir(parents=True, exist_ok=True)
    recorded_path.write_text(download(), encoding="utf-8")


# TODO: Validate
def read_id(entry: object) -> Id:
    """Return one id as the generator reads it.

    An id written as a list is read back as a tuple, which is how an id made of
    more than one value is given.
    """
    return tuple(entry) if isinstance(entry, list) else entry


# TODO: Validate
def load_ids(model_name: str) -> Ids:
    """Return the ids a model's responses are recorded for.

    A file holding an object is read back as a mapping of the name each response
    is recorded under to the id it is downloaded with.
    """
    entries = json.loads((IDS_PATH / f"{model_name}.json").read_text(encoding="utf-8"))
    if isinstance(entries, dict):
        return {name: read_id(entry) for name, entry in entries.items()}
    return [read_id(entry) for entry in entries]


# TODO: Validate
def save_ids(model_name: str, ids: Ids) -> None:
    """Write the ids a model's responses are recorded for."""
    ids_path = IDS_PATH / f"{model_name}.json"
    ids_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(ids, dict):
        entries: object = {name: written_id(id_) for name, id_ in ids.items()}
    else:
        entries = [written_id(id_) for id_ in ids]
    ids_path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")


# TODO: Validate
def written_id(id_: Id) -> object:
    """Return one id as the file holds it."""
    return list(id_) if isinstance(id_, tuple) else id_


# TODO: Validate
def drop_redundant_recordings(
    files_path: Path,
    model_name: str,
    read: Callable[[str], Any] = json.loads,
    name_of: Callable[[Id], str] = str,
) -> None:
    """Delete the recordings a model does not need, and the ids they came from.

    A recording the ids file does not name is kept. Nothing takes it out of what
    the generator downloads, so deleting it downloads it again on the next run.

    Args:
        files_path: Where the recorded responses live.
        model_name: The model class name, e.g. `SeriesModel`.
        read: Turns a recording into the object the model reads.
        name_of: Returns the name an id is recorded under, for an id that is not
            the name itself.
    """
    if not (IDS_PATH / f"{model_name}.json").exists():
        return

    ids = load_ids(model_name)
    if isinstance(ids, dict):
        recorded_names = {sanitized_file_name(name) for name in ids}
    else:
        recorded_names = {sanitized_file_name(name_of(id_)) for id_ in ids}

    redundant = [
        recording
        for recording in redundant_recordings(files_path, model_name, read)
        if recording.stem in recorded_names
    ]
    if not redundant:
        return

    for recording in redundant:
        logger.info("Dropping %s.", recording.relative_to(files_path))
        recording.unlink()

    dropped = {recording.stem for recording in redundant}
    if isinstance(ids, dict):
        kept: Ids = {
            name: id_
            for name, id_ in ids.items()
            if sanitized_file_name(name) not in dropped
        }
    else:
        kept = [id_ for id_ in ids if sanitized_file_name(name_of(id_)) not in dropped]
    save_ids(model_name, kept)


# TODO: Validate
def rebuild_model(
    files_path: Path,
    package_path: Path,
    model_name: str,
    read: Callable[[str], Any] = json.loads,
    name_of: Callable[[Id], str] = str,
) -> None:
    """Rewrite a model from its recordings, then drop the ones it does not need.

    A model that needs a customizer calls `generate_model` and
    `drop_redundant_recordings` itself, since the customizer does not fit here.
    """
    generate_model(files_path, package_path, model_name, read)
    drop_redundant_recordings(files_path, model_name, read, name_of)
