"""Core video building logic."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from moviepy.audio.fx import audio_loop  # type: ignore
from moviepy.editor import (  # type: ignore
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    VideoClip,
    concatenate_videoclips,
    vfx,
)

from .overlays import build_overlay

ImagePath = Path


@dataclass
class VideoSettings:
    """Configuration for the rendered video."""

    fps: int = 30
    resolution: Tuple[int, int] = (1280, 720)
    image_duration: float = 3.0
    transition_duration: float = 0.5
    zoom_factor: float = 0.08
    overlay: Optional[str] = None
    overlay_intensity: float = 0.5


class VideoMaker:
    """Create an animated slideshow from images and an audio track."""

    def __init__(self, settings: Optional[VideoSettings] = None) -> None:
        self.settings = settings or VideoSettings()

    def build(
        self,
        images: Sequence[ImagePath],
        audio_path: Path,
        output_path: Path,
    ) -> Path:
        """Render the video."""

        if not images:
            raise ValueError("No images provided")

        clips = self._build_image_clips(images)
        video = self._compose_video(clips)
        audio = self._prepare_audio(audio_path, video.duration)

        video = video.set_audio(audio)

        if self.settings.overlay:
            overlay_clip = build_overlay(
                self.settings.overlay,
                duration=video.duration,
                size=self.settings.resolution,
                fps=self.settings.fps,
                intensity=self.settings.overlay_intensity,
            ).resize(newsize=self.settings.resolution)
            video = CompositeVideoClip([video, overlay_clip])

        output_path = output_path.expanduser().resolve()
        video.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=self.settings.fps,
            preset="ultrafast",
            threads=4,
        )

        return output_path

    def _build_image_clips(self, images: Sequence[ImagePath]) -> List[VideoClip]:
        clips: List[VideoClip] = []
        for index, image_path in enumerate(images):
            clip = ImageClip(str(image_path)).resize(newsize=self.settings.resolution)
            clip = clip.set_duration(self.settings.image_duration)

            if self.settings.zoom_factor:
                clip = clip.fx(
                    vfx.resize,
                    lambda t: 1
                    + self.settings.zoom_factor * (t / max(self.settings.image_duration, 1e-6)),
                )

            if index != 0:
                clip = clip.crossfadein(self.settings.transition_duration)

            clips.append(clip)

        return clips

    def _compose_video(self, clips: Sequence[VideoClip]) -> VideoClip:
        return concatenate_videoclips(
            list(clips),
            method="compose",
            padding=-self.settings.transition_duration,
        ).set_fps(self.settings.fps)

    def _prepare_audio(self, audio_path: Path, duration: float) -> AudioFileClip:
        audio_clip = AudioFileClip(str(audio_path))
        if audio_clip.duration < duration:
            audio_clip = audio_loop(audio_clip, duration=duration)
        else:
            audio_clip = audio_clip.subclip(0, duration)
        return audio_clip


def build_video(
    images: Iterable[ImagePath],
    audio_path: Path,
    output_path: Path,
    settings: Optional[VideoSettings] = None,
) -> Path:
    maker = VideoMaker(settings)
    return maker.build(list(images), audio_path, output_path)
