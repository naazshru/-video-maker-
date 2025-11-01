"""Flask application that exposes the video maker through the browser."""
from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from flask import (
    Flask,
    Response,
    after_this_request,
    render_template,
    request,
    send_file,
)

from .builder import VideoMaker, VideoSettings
from .overlays import available_overlays


def create_app() -> Flask:
    templates = Path(__file__).resolve().parent / "templates"
    app = Flask(__name__, template_folder=str(templates))

    overlays = [(key, key.replace("_", " ").title()) for key in available_overlays()]

    @app.route("/", methods=["GET", "POST"])
    def index() -> Response:
        error: Optional[str] = None
        if request.method == "POST":
            try:
                response = _handle_submission(request.files.getlist("images"), request.files.get("audio"), request.form, overlays)
                return response
            except ValueError as exc:  # expected validation errors
                error = str(exc)

        return render_template("index.html", overlays=overlays, error=error)

    return app


def _handle_submission(image_files, audio_file, form_data, overlays) -> Response:
    image_paths = _save_images(image_files)
    if not image_paths:
        raise ValueError("Upload at least one image file.")

    if not audio_file or not audio_file.filename:
        raise ValueError("Please upload an audio track.")

    work_dir = Path(tempfile.mkdtemp(prefix="video-maker-"))

    @after_this_request
    def cleanup(response: Response) -> Response:  # pragma: no cover - Flask hook
        shutil.rmtree(work_dir, ignore_errors=True)
        return response

    audio_path = work_dir / _safe_name(audio_file.filename, default="audio")
    audio_file.save(audio_path)

    output_path = work_dir / "render.mp4"

    settings = _parse_settings(form_data, overlays)
    maker = VideoMaker(settings)
    try:
        maker.build(image_paths, audio_path, output_path)
    except Exception as exc:  # pragma: no cover - surfaced to user
        raise ValueError("Failed to render the video. See server logs for details.") from exc

    return send_file(output_path, as_attachment=True, download_name="video.mp4")


def _save_images(files) -> List[Path]:
    image_paths: List[Path] = []
    work_dir = Path(tempfile.mkdtemp(prefix="video-maker-images-"))

    @after_this_request
    def cleanup(response: Response) -> Response:  # pragma: no cover - Flask hook
        shutil.rmtree(work_dir, ignore_errors=True)
        return response

    used_names = set()

    for index, storage in enumerate(files):
        if not storage or not storage.filename:
            continue
        filename = _safe_name(storage.filename, default=f"image-{index:04d}")
        if filename in used_names:
            stem = Path(filename).stem
            suffix = Path(filename).suffix
            counter = 1
            candidate = f"{stem}-{counter}{suffix}"
            while candidate in used_names:
                counter += 1
                candidate = f"{stem}-{counter}{suffix}"
            filename = candidate
        used_names.add(filename)
        path = work_dir / filename
        storage.save(path)
        image_paths.append(path)

    return image_paths


def _parse_settings(form, overlays) -> VideoSettings:
    def float_field(name: str, default: float, *, minimum: Optional[float] = None, maximum: Optional[float] = None) -> float:
        raw = form.get(name, "")
        if not raw:
            return default
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"'{name}' must be a number.") from exc
        if minimum is not None and value < minimum:
            raise ValueError(f"'{name}' must be at least {minimum}.")
        if maximum is not None and value > maximum:
            raise ValueError(f"'{name}' must be at most {maximum}.")
        return value

    def int_field(name: str, default: int, *, minimum: Optional[int] = None, maximum: Optional[int] = None) -> int:
        value = float_field(name, float(default), minimum=minimum, maximum=maximum)
        return int(round(value))

    def resolution_field(name: str, default: Tuple[int, int]) -> Tuple[int, int]:
        raw = form.get(name, "")
        if not raw:
            return default
        match = re.match(r"^(\d{2,5})[xX](\d{2,5})$", raw.strip())
        if not match:
            raise ValueError("Resolution must look like 1920x1080.")
        width, height = int(match.group(1)), int(match.group(2))
        if width < 320 or height < 240:
            raise ValueError("Resolution is too small. Minimum is 320x240.")
        if width > 3840 or height > 2160:
            raise ValueError("Resolution is too large. Maximum is 3840x2160.")
        return width, height

    overlay_key = form.get("overlay", "none").strip().lower()
    valid_overlays = {key for key, _ in overlays}
    if overlay_key not in valid_overlays and overlay_key != "none":
        raise ValueError("Unknown overlay option selected.")

    overlay = overlay_key if overlay_key != "none" else None

    settings = VideoSettings(
        fps=int_field("fps", 30, minimum=1, maximum=60),
        resolution=resolution_field("resolution", (1280, 720)),
        image_duration=float_field("image_duration", 3.0, minimum=0.5, maximum=30.0),
        transition_duration=float_field("transition_duration", 0.5, minimum=0.0, maximum=10.0),
        zoom_factor=float_field("zoom_factor", 0.08, minimum=0.0, maximum=1.0),
        overlay=overlay,
        overlay_intensity=float_field("overlay_intensity", 0.5, minimum=0.0, maximum=1.0),
    )
    return settings


def _safe_name(filename: str, *, default: str) -> str:
    stem = Path(filename).stem or default
    suffix = Path(filename).suffix or ""
    clean_stem = re.sub(r"[^a-zA-Z0-9_-]", "-", stem)
    return f"{clean_stem}{suffix}"


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), debug=False)
