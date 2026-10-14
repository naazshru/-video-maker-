# Ushvika product films

Cinematic 3D product trailers for **USHVIKA – Nature's Goodness. For You**.
Each product is shown only from its real photos: the label and pack are never redrawn.

| Film | Folder | Length | Notes |
|---|---|---|---|
| Rose Tea Premix | `trailer/` | 30 s | First film – carries the USHVIKA brand intro |
| Rose Jelly | `jelly/` | 24.2 s | Continuation film, Hindi voice-over |
| Rose Badam Shake Premix | `badam/` | 27 s | Continuation film, Hindi voice-over |
| Rose Petal Twist (rose milk shake) | `twist/` | 24.2 s | Pouch, 8-photo 360° morph, Hindi voice-over |

## Build on your own computer (graphics card = much faster)

1. Install **Node.js 18+** (nodejs.org) and **ffmpeg** (ffmpeg.org; on Windows: `winget install ffmpeg`).
2. Get the project:
   ```
   git clone https://github.com/naazshru/-video-maker-.git
   cd -video-maker-
   git checkout claude/rose-tea-cinematic-trailer-yb0cdj
   npm install
   npx playwright install chromium
   ```
3. Render:
   ```
   node build.mjs --gpu              # all films, uses the graphics card (a browser window opens – leave it)
   node build.mjs --gpu jelly        # just one film (tea, jelly, badam, twist)
   ```
   Finished videos appear in `out/` as 1920×1080 MP4. Rendering resumes where it stopped if interrupted.

Without a graphics card, drop `--gpu` (software rendering – slow but identical output).
On a big cloud machine with many CPU cores, use e.g. `node build.mjs --workers 16`.

## How it is made

- `*/index.html` – the scene: Three.js 3D stage, petals, sparkles, light rays, motion-graphic text, timeline (`window.renderAt(t)`).
- `*/tex/` – the product photos (only scaled/cropped, never altered). Round jars use a cylindrical
  re-projection of 4 photos; the pouch morphs between its 8 photos.
- `trailer/score.py` + `*/music.json` – original procedural music (royalty-free).
- `*/vo_raw.mp3` + `*/vo_segments.txt` + `trailer/mix.sh` – Hindi voice-over placed per scene, music ducked under the voice → `final_audio.wav`.
- `build.mjs` – renders frames in headless Chromium and encodes MP4 with ffmpeg.
