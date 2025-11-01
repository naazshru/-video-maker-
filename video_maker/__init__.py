"""Video maker package."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - imported only for typing
    from .builder import VideoMaker, build_video

__all__ = ["VideoMaker", "build_video"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module(".builder", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
