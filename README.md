# Video Maker

Create fast MP4 slideshows by combining a folder of images with a soundtrack. The web
app animates each image with a gentle zoom effect, adds smooth crossfade transitions,
and optionally mixes in configurable overlays such as sparkles or color filters.

## Features

- Browser-based workflow – upload your images and soundtrack without installing a CLI
- Accepts a directory of images and an audio file to produce an MP4 video
- Adds zoom animation and configurable crossfade transitions between slides
- Optional overlays: sparkles, warm tint, or animated green/red stripes
- Audio is automatically trimmed or looped to match the video duration
- Uses the ultrafast encoder preset for quick rendering

## Installation

1. Install the required dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Ensure FFmpeg is available on your system. MoviePy relies on FFmpeg for video
   encoding.

## Usage

### Run the web server

Start the Flask app and open the reported URL in your browser (defaults to
<http://127.0.0.1:8000>):

```bash
python -m video_maker.webapp
```

You can also rely on Flask's built-in runner:

```bash
flask --app video_maker.webapp run --host 0.0.0.0 --port 8000
```

### Rendering a video

1. Upload multiple images (hold Ctrl/⌘ or Shift to pick several files at once).
2. Upload an audio file – it will be trimmed or looped to match the final video.
3. Adjust optional settings such as resolution, FPS, zoom, crossfade duration, and
   overlay effect.
4. Click **Render video** and wait for the MP4 download to start.

The generated video uses the ultrafast H.264 preset with AAC audio for speedy exports.
