"""Video overlay effects."""
from __future__ import annotations

from typing import Callable, Tuple

import numpy as np
from moviepy.editor import ColorClip, VideoClip  # type: ignore

OverlayFactory = Callable[[float, Tuple[int, int], int, float], VideoClip]

__all__ = ["build_overlay", "available_overlays"]


def build_overlay(
    name: str,
    *,
    duration: float,
    size: Tuple[int, int],
    fps: int,
    intensity: float,
) -> VideoClip:
    name = name.lower()
    intensity = max(0.0, min(1.0, intensity))
    factory = _OVERLAYS.get(name)
    if not factory:
        raise ValueError(f"Unknown overlay '{name}'. Available: {', '.join(sorted(_OVERLAYS))}")
    overlay = factory(duration, size, fps, intensity)
    return overlay.set_duration(duration).set_fps(fps)


def _sparkle_overlay(duration: float, size: Tuple[int, int], fps: int, intensity: float) -> VideoClip:
    width, height = size
    sparkle_count = max(10, int(width * height / 20000))

    def make_frame(t: float) -> np.ndarray:
        rng = np.random.default_rng(int(t * fps))
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        for _ in range(sparkle_count):
            x = rng.integers(0, width)
            y = rng.integers(0, height)
            radius = rng.integers(2, 6)
            y_min = max(y - radius, 0)
            y_max = min(y + radius, height)
            x_min = max(x - radius, 0)
            x_max = min(x + radius, width)
            frame[y_min:y_max, x_min:x_max, :3] = 255
        return frame

    opacity = 0.25 + 0.5 * intensity
    return VideoClip(make_frame=make_frame, duration=duration, ismask=False).set_opacity(opacity)


def _color_overlay(duration: float, size: Tuple[int, int], fps: int, intensity: float) -> VideoClip:
    color = (int(255 * intensity), int(100 * intensity), int(100 * intensity))
    clip = ColorClip(size, color)
    return clip.set_opacity(0.15 + intensity * 0.35)


def _green_red_overlay(duration: float, size: Tuple[int, int], fps: int, intensity: float) -> VideoClip:
    width, height = size
    stripe_height = max(10, height // 6)

    def make_frame(t: float) -> np.ndarray:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        shift = int((t * fps) % (2 * stripe_height))
        for row in range(0, height + stripe_height, stripe_height):
            color = (0, 255, 0) if (row // stripe_height) % 2 == 0 else (255, 0, 0)
            y_start = max(row - shift, 0)
            y_end = min(row - shift + stripe_height, height)
            frame[y_start:y_end, :, :3] = color
        return frame

    opacity = 0.18 + 0.4 * intensity
    return VideoClip(make_frame=make_frame, duration=duration, ismask=False).set_opacity(opacity)


_OVERLAYS = {
    "sparkles": _sparkle_overlay,
    "warm": _color_overlay,
    "green_red": _green_red_overlay,
}


def available_overlays() -> Tuple[str, ...]:
    """Return the overlay identifiers supported by the builder."""

    return tuple(sorted(_OVERLAYS))
