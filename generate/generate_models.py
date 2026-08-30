# TODO: Validate
"""Rebuilds every PoolsClosed model from the responses recorded under `_files`.

Run it with `uv run python -m generate.generate_models`, or rebuild one model on
its own with `uv run python -m generate.<module>`.

The modules that rebuild a model are found rather than listed, so a new model
only has to be added as a module next to this one, holding a
`generate_<module>` function.
"""

from __future__ import annotations

import logging
import pkgutil
from importlib import import_module

from get_around import build_client_automatically

import generate
from pools_closed import PoolsClosed

SKIPPED_MODULES = frozenset({"constants", "generate_models", "utils"})
"""The modules next to this one that do not rebuild a model."""

logger = logging.getLogger(__name__)


# TODO: Validate
def model_module_names() -> list[str]:
    """Return the name of every module that rebuilds a model."""
    return sorted(
        module.name
        for module in pkgutil.iter_modules(generate.__path__)
        if module.name not in SKIPPED_MODULES
    )


# TODO: Validate
def generate_all(client: PoolsClosed) -> None:
    """Rebuild every model, one module at a time."""
    for module_name in model_module_names():
        module = import_module(f"generate.{module_name}")
        getattr(module, f"generate_{module_name}")(client)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generate_all(PoolsClosed(build_client_automatically()))
