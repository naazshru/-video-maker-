"""Render the Ushvika films on Modal (modal.com) by fanning frame ranges out to many containers.

    pip install modal && modal token set ...      (once)
    modal run modal_render.py                     # all films
    modal run modal_render.py --films jelly,twist # some films
    modal run modal_render.py --chunks 40         # more parallel containers = faster

Each container renders a slice of frames with headless Chromium and encodes it to an H.264
segment; segments are joined locally and the film's audio is muxed in -> out/<film>.mp4.
"""
import pathlib, subprocess, tempfile
import modal

ROOT = pathlib.Path(__file__).parent
FILMS = {
    "tea":   ("trailer/index.html", "trailer/music.wav", 30.0),
    "jelly": ("jelly/index.html",   "jelly/final_audio.wav", 24.2),
    "badam": ("badam/index.html",   "badam/final_audio.wav", 27.0),
    "twist": ("twist/index.html",   "twist/final_audio.wav", 24.2),
}

image = (
    modal.Image.from_registry("mcr.microsoft.com/playwright:v1.56.1-noble", add_python="3.12")
    .apt_install("ffmpeg")
    .run_commands("npm i -g playwright@1.56.1")
    .env({"NODE_PATH": "/usr/lib/node_modules"})
    .add_local_dir(ROOT, "/site", ignore=["out", "node_modules", ".git", "*.mp4", "*/src", "*/vo_raw.mp3"])
)
app = modal.App("ushvika-films", image=image)


@app.function(cpu=8, memory=8192, timeout=1800)
def render_chunk(page: str, start: int, end: int, fps: int) -> bytes:
    with tempfile.TemporaryDirectory() as d:
        server = subprocess.Popen(["python", "-m", "http.server", "8765", "-d", "/site"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            procs, per = [], (end - start + 3) // 4          # 4 browsers per container
            for k in range(4):
                a, b = start + k * per, min(end, start + (k + 1) * per)
                if a < b:
                    procs.append(subprocess.Popen(
                        ["node", "/site/trailer/render.mjs", d, str(fps), str(a), str(b)],
                        env={"PAGE_URL": f"http://localhost:8765/{page}", "NODE_PATH": "/usr/lib/node_modules",
                             "PATH": "/usr/bin:/usr/local/bin:/bin"}))
            for p in procs:
                p.wait()
        finally:
            server.terminate()
        seg = f"{d}/seg.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-start_number", str(start),
                        "-i", f"{d}/f%05d.jpg", "-frames:v", str(end - start), "-c:v", "libx264", "-preset", "slow",
                        "-crf", "18", "-pix_fmt", "yuv420p", seg], check=True)
        return pathlib.Path(seg).read_bytes()


@app.local_entrypoint()
def main(films: str = "tea,jelly,badam,twist", chunks: int = 24, fps: int = 30):
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    for name in films.split(","):
        page, audio, dur = FILMS[name]
        total = round(dur * fps)
        step = -(-total // chunks)
        ranges = [(page, s, min(total, s + step), fps) for s in range(0, total, step)]
        print(f"{name}: {total} frames on {len(ranges)} containers")
        segs = list(render_chunk.starmap(ranges))
        with tempfile.TemporaryDirectory() as d:
            lst = pathlib.Path(d, "list.txt")
            lines = []
            for i, b in enumerate(segs):
                p = pathlib.Path(d, f"s{i:03d}.mp4"); p.write_bytes(b); lines.append(f"file '{p}'")
            lst.write_text("\n".join(lines))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                            "-i", str(ROOT / audio), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(dur),
                            "-movflags", "+faststart", str(out / f"{name}.mp4")], check=True)
        print(f"  -> out/{name}.mp4")
