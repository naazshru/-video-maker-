"""Command-line interface for the video maker."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:  # pragma: no cover - import only for type hints
    from .builder import VideoMaker, VideoSettings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a video from images and audio.")
    parser.add_argument("images", help="Path to folder containing images")
    parser.add_argument("audio", help="Path to the audio file (mp3, wav, etc.)")
    parser.add_argument("output", help="Output mp4 file")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument(
        "--resolution",
        type=str,
        default="1280x720",
        help="Output resolution as WIDTHxHEIGHT",
    )
    parser.add_argument(
        "--image-duration",
        type=float,
        default=3.0,
        help="Duration of each image in seconds",
    )
    parser.add_argument(
        "--transition",
        type=float,
        default=0.5,
        help="Crossfade duration between images in seconds",
    )
    parser.add_argument(
        "--zoom",
        type=float,
        default=0.08,
        help="Zoom factor applied over the duration of each image",
    )
    parser.add_argument(
        "--overlay",
        type=str,
        choices=["sparkles", "warm", "green_red"],
        help="Optional overlay effect",
    )
    parser.add_argument(
        "--overlay-intensity",
        type=float,
        default=0.5,
        help="Overlay intensity between 0 and 1",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    from .builder import VideoMaker, VideoSettings  # Local import to avoid heavy deps on help

    resolution = _parse_resolution(args.resolution)
    settings = VideoSettings(
        fps=args.fps,
        resolution=resolution,
        image_duration=args.image_duration,
        transition_duration=args.transition,
        zoom_factor=args.zoom,
        overlay=args.overlay,
        overlay_intensity=args.overlay_intensity,
    )

    images = sorted(
        (p for p in Path(args.images).expanduser().iterdir() if p.suffix.lower() in _IMAGE_EXTS),
        key=lambda p: p.name,
    )

    if not images:
        parser.error("No supported image files found in the provided directory.")

    maker = VideoMaker(settings)
    maker.build(images, Path(args.audio), Path(args.output))
    return 0


def _parse_resolution(value: str) -> tuple[int, int]:
    try:
        width_str, height_str = value.lower().split("x", 1)
        width = int(width_str)
        height = int(height_str)
    except ValueError as exc:  # pragma: no cover - defensive programming
        raise argparse.ArgumentTypeError(
            "Resolution must be in the format WIDTHxHEIGHT"
        ) from exc

    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("Resolution dimensions must be positive integers")

    return width, height


_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
