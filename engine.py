"""Tiny 2D animation engine: timed narration segments + pop-in sprites -> mp4.

Visuals are drawn with Pillow, narration is synthesized offline with Kokoro TTS,
and frames are piped straight into ffmpeg.
"""
import hashlib
import math
import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FPS = 30
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
BUILD = os.path.join(ROOT, "build")

COL = dict(
    bg=(255, 248, 236),
    ink=(43, 43, 58),
    soft=(110, 110, 125),
    white=(255, 255, 255),
    blue=(86, 156, 226),
    blue_d=(36, 90, 160),
    pink=(200, 30, 100),
    green=(34, 150, 84),
    orange=(236, 120, 20),
    purple=(118, 70, 220),
    yellow=(255, 205, 60),
    cream_d=(245, 232, 210),
)

_fonts = {}


def font(size, weight=700, fam="fredoka"):
    key = (size, weight, fam)
    if key not in _fonts:
        if fam == "dejavu":
            path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        else:
            path = os.path.join(FONT_DIR, f"{fam}-latin-{weight}-normal.woff")
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


# ---------------------------------------------------------------- elements
class El:
    anim = "pop"
    dur = 0.35

    def __init__(self, id=None, anim=None, dur=None):
        self.id = id
        if anim:
            self.anim = anim
        if dur is not None:
            self.dur = dur
        self._spr = None

    def bbox(self):
        raise NotImplementedError

    def draw(self, d, ox, oy):
        raise NotImplementedError

    def sprite(self):
        if self._spr is None:
            x0, y0, x1, y1 = [int(v) for v in self.bbox()]
            x0 -= 6; y0 -= 6; x1 += 6; y1 += 6
            img = Image.new("RGBA", (max(1, x1 - x0), max(1, y1 - y0)), (0, 0, 0, 0))
            self.draw(ImageDraw.Draw(img), x0, y0)
            self._spr = (img, x0, y0)
        return self._spr


class Text(El):
    def __init__(self, x, y, text, size=40, color="ink", weight=700, fam="fredoka",
                 anchor="mm", stroke=0, stroke_color="white", **kw):
        super().__init__(**kw)
        self.x, self.y, self.text, self.anchor = x, y, text, anchor
        self.f = font(size, weight, fam)
        self.color = COL.get(color, color) if isinstance(color, str) else color
        self.stroke = stroke
        self.sc = COL.get(stroke_color, stroke_color) if isinstance(stroke_color, str) else stroke_color

    def bbox(self):
        b = self.f.getbbox(self.text, anchor=self.anchor, stroke_width=self.stroke)
        return (self.x + b[0], self.y + b[1], self.x + b[2], self.y + b[3])

    def draw(self, d, ox, oy):
        d.text((self.x - ox, self.y - oy), self.text, font=self.f, fill=self.color,
               anchor=self.anchor, stroke_width=self.stroke, stroke_fill=self.sc)


class Rect(El):
    anim = "fade"

    def __init__(self, x0, y0, x1, y1, fill="white", outline=None, width=4, r=18, **kw):
        super().__init__(**kw)
        self.b = (x0, y0, x1, y1)
        self.fill = COL.get(fill, fill) if isinstance(fill, str) else fill
        self.outline = COL.get(outline, outline) if isinstance(outline, str) else outline
        self.width, self.r = width, r

    def bbox(self):
        return self.b

    def draw(self, d, ox, oy):
        x0, y0, x1, y1 = self.b
        d.rounded_rectangle((x0 - ox, y0 - oy, x1 - ox, y1 - oy), radius=self.r,
                            fill=self.fill, outline=self.outline,
                            width=self.width if self.outline else 0)


class Circle(El):
    def __init__(self, cx, cy, r, fill="white", outline="ink", width=5, **kw):
        super().__init__(**kw)
        self.cx, self.cy, self.r = cx, cy, r
        self.fill = COL.get(fill, fill) if isinstance(fill, str) else fill
        self.outline = COL.get(outline, outline) if isinstance(outline, str) else outline
        self.width = width

    def bbox(self):
        return (self.cx - self.r, self.cy - self.r, self.cx + self.r, self.cy + self.r)

    def draw(self, d, ox, oy):
        d.ellipse((self.cx - self.r - ox, self.cy - self.r - oy, self.cx + self.r - ox,
                   self.cy + self.r - oy), fill=self.fill, outline=self.outline, width=self.width)


class Hundred(El):
    """Base-ten flat: 10x10 grid."""

    def __init__(self, x, y, s=48, **kw):
        super().__init__(**kw)
        self.x, self.y, self.s = x, y, s

    def bbox(self):
        return (self.x, self.y, self.x + self.s, self.y + self.s)

    def draw(self, d, ox, oy):
        x, y, s = self.x - ox, self.y - oy, self.s
        d.rectangle((x, y, x + s, y + s), fill=COL["blue"], outline=COL["blue_d"], width=max(2, min(4, s // 24)))
        for i in range(1, 10):
            p = s * i / 10
            d.line((x + p, y, x + p, y + s), fill=COL["blue_d"], width=1)
            d.line((x, y + p, x + s, y + p), fill=COL["blue_d"], width=1)


class Ten(El):
    """Base-ten rod: 10 stacked cubes."""

    def __init__(self, x, y, w=14, h=100, **kw):
        super().__init__(**kw)
        self.x, self.y, self.w, self.h = x, y, w, h

    def bbox(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def draw(self, d, ox, oy):
        x, y = self.x - ox, self.y - oy
        d.rectangle((x, y, x + self.w, y + self.h), fill=COL["blue"], outline=COL["blue_d"],
                    width=max(2, self.w // 10))
        for i in range(1, 10):
            p = y + self.h * i / 10
            d.line((x, p, x + self.w, p), fill=COL["blue_d"], width=1)


class One(El):
    def __init__(self, x, y, s=14, **kw):
        super().__init__(**kw)
        self.x, self.y, self.s = x, y, s

    def bbox(self):
        return (self.x, self.y, self.x + self.s, self.y + self.s)

    def draw(self, d, ox, oy):
        x, y = self.x - ox, self.y - oy
        d.rectangle((x, y, x + self.s, y + self.s), fill=COL["blue"], outline=COL["blue_d"],
                    width=max(2, self.s // 10))


class Mark(El):
    """Book-style quick drawing (all pink): one = line, ten = line with a cross,
    hundred = a bundle of lines tied with a band."""
    anim = "wipe_down"
    dur = 0.3

    def __init__(self, kind, cx, top, h=56, color="pink", width=6, **kw):
        super().__init__(**kw)
        self.kind, self.cx, self.top, self.h, self.width = kind, cx, top, h, width
        self.color = COL.get(color, color)

    def bbox(self):
        half = {"one": self.width, "ten": self.h * 0.32, "hundred": self.h * 0.34}[self.kind]
        return (self.cx - half, self.top, self.cx + half, self.top + self.h)

    def draw(self, d, ox, oy):
        cx, top, h, c, w = self.cx - ox, self.top - oy, self.h, self.color, self.width
        if self.kind == "hundred":
            half = h * 0.2
            n = 6
            for i in range(n):
                x = cx - half + 2 * half * i / (n - 1)
                d.line((x, top + 2, x, top + h - 2), fill=c, width=max(3, w // 2))
            for yy in (top + h * 0.42, top + h * 0.58):
                d.line((cx - h * 0.32, yy, cx + h * 0.32, yy), fill=c, width=w)
            return
        d.line((cx, top, cx, top + h), fill=c, width=w)
        d.ellipse((cx - w / 2, top - w / 2, cx + w / 2, top + w / 2), fill=c)
        d.ellipse((cx - w / 2, top + h - w / 2, cx + w / 2, top + h + w / 2), fill=c)
        if self.kind == "ten":
            half = h * 0.28
            d.line((cx - half, top + h / 2, cx + half, top + h / 2), fill=c, width=w)


class Straw(El):
    """One straw (a 'one' in the book)."""

    def __init__(self, x, y, w=10, h=80, **kw):
        super().__init__(**kw)
        self.x, self.y, self.w, self.h = x, y, w, h

    def bbox(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def draw(self, d, ox, oy):
        x, y = self.x - ox, self.y - oy
        d.rounded_rectangle((x, y, x + self.w, y + self.h), radius=self.w // 2,
                            fill=COL["blue"], outline=COL["blue_d"], width=2)


class Bundle(El):
    """A bundle of straws tied with a band: n=10 is a ten, n=100 is a hundred."""

    def __init__(self, x, y, n=10, h=80, **kw):
        super().__init__(**kw)
        self.x, self.y, self.n, self.h = x, y, n, h
        self.w = h * 0.34 if n == 10 else h * 0.9

    def bbox(self):
        return (self.x - 3, self.y, self.x + self.w + 3, self.y + self.h)

    def draw(self, d, ox, oy):
        x, y, w, h = self.x - ox, self.y - oy, self.w, self.h
        dark, fill = COL["blue_d"], COL["blue"]
        if self.n == 10:
            d.rounded_rectangle((x, y, x + w, y + h), radius=w * 0.3, fill=fill, outline=dark, width=2)
            for i in range(1, 4):
                xx = x + w * i / 4
                d.line((xx, y + 3, xx, y + h - 3), fill=dark, width=2)
            for yy in (y + h * 0.36, y + h * 0.6):
                d.line((x - 1, yy, x + w + 1, yy), fill=dark, width=3)
            return
        e = h * 0.24
        d.rectangle((x, y + e / 2, x + w, y + h - e / 2), fill=fill)
        d.ellipse((x, y + h - e, x + w, y + h), fill=fill, outline=dark, width=2)
        d.rectangle((x + 2, y + e / 2, x + w - 2, y + h - e / 2), fill=fill)
        d.line((x, y + e / 2, x, y + h - e / 2), fill=dark, width=2)
        d.line((x + w, y + e / 2, x + w, y + h - e / 2), fill=dark, width=2)
        for i in range(1, 10):
            xx = x + w * i / 10
            d.line((xx, y + e, xx, y + h - e * 0.3), fill=dark, width=1)
        d.ellipse((x, y, x + w, y + e), fill=(170, 205, 240), outline=dark, width=2)
        r = max(2, w / 22)
        for j in range(3):
            for i in range(9):
                cx = x + w * (i + 1) / 10
                cy = y + e * (0.25 + 0.25 * j)
                if ((cx - (x + w / 2)) / (w / 2)) ** 2 + ((cy - (y + e / 2)) / (e / 2)) ** 2 < 0.8:
                    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=dark, width=1)
        for yy in (y + h * 0.45, y + h * 0.6):
            d.line((x - 2, yy, x + w + 2, yy), fill=dark, width=4)


class Kid(El):
    """Simple kid character, like the helper in the book."""

    def __init__(self, cx, top, **kw):
        super().__init__(**kw)
        self.cx, self.top = cx, top

    def bbox(self):
        return (self.cx - 50, self.top, self.cx + 60, self.top + 210)

    def draw(self, d, ox, oy):
        cx, t = self.cx - ox, self.top - oy
        skin, ink = (240, 200, 165), COL["ink"]
        d.rectangle((cx - 14, t + 150, cx - 4, t + 205), fill=(90, 90, 100))
        d.rectangle((cx + 4, t + 150, cx + 14, t + 205), fill=(90, 90, 100))
        d.rounded_rectangle((cx - 30, t + 62, cx + 30, t + 155), radius=14, fill=(225, 75, 60))
        d.line((cx + 26, t + 80, cx + 55, t + 60), fill=(225, 75, 60), width=12)
        d.ellipse((cx + 48, t + 50, cx + 62, t + 64), fill=skin)
        d.line((cx - 26, t + 80, cx - 34, t + 130), fill=(225, 75, 60), width=12)
        d.ellipse((cx - 30, t + 2, cx + 30, t + 66), fill=skin, outline=ink, width=2)
        d.chord((cx - 32, t - 2, cx + 32, t + 50), 180, 360, fill=(95, 60, 35))
        d.ellipse((cx - 13, t + 34, cx - 7, t + 40), fill=ink)
        d.ellipse((cx + 7, t + 34, cx + 13, t + 40), fill=ink)
        d.arc((cx - 12, t + 38, cx + 12, t + 56), 20, 160, fill=ink, width=3)


class Bubble(El):
    """Speech bubble (rounded box with a tail on the left)."""
    anim = "fade"

    def __init__(self, x0, y0, x1, y1, tail_y=None, **kw):
        super().__init__(**kw)
        self.b = (x0, y0, x1, y1)
        self.tail_y = tail_y

    def bbox(self):
        x0, y0, x1, y1 = self.b
        return (x0 - 40 if self.tail_y else x0, y0, x1, y1)

    def draw(self, d, ox, oy):
        x0, y0, x1, y1 = [v - o for v, o in zip(self.b, (ox, oy, ox, oy))]
        d.rounded_rectangle((x0, y0, x1, y1), radius=22, fill=COL["white"], outline=COL["pink"], width=4)
        if self.tail_y:
            ty = self.tail_y - oy
            d.polygon([(x0 + 2, ty - 18), (x0 - 36, ty + 10), (x0 + 2, ty + 18)], fill=COL["white"])
            d.line([(x0, ty - 18), (x0 - 36, ty + 10), (x0, ty + 18)], fill=COL["pink"], width=4)


class Arrow(El):
    """Curved hop arrow from x0 to x1 at baseline y, optional label above."""
    anim = "wipe_right"
    dur = 0.45

    def __init__(self, x0, x1, y, height=60, color="pink", label=None, label_size=28, width=5, **kw):
        super().__init__(**kw)
        self.x0, self.x1, self.y, self.hgt, self.width = x0, x1, y, height, width
        self.color = COL.get(color, color)
        self.label = label
        self.lf = font(label_size, 700)

    def bbox(self):
        top = self.y - self.hgt - (self.lf.size + 14 if self.label else 0)
        lw = self.lf.getlength(self.label) / 2 if self.label else 0
        mid = (self.x0 + self.x1) / 2
        return (min(self.x0, mid - lw) - 12, top, max(self.x1, mid + lw) + 12, self.y + 12)

    def draw(self, d, ox, oy):
        x0, x1, y = self.x0 - ox, self.x1 - ox, self.y - oy
        cx, cy = (x0 + x1) / 2, y - 2 * self.hgt
        pts = []
        for i in range(41):
            t = i / 40
            pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1,
                        (1 - t) ** 2 * y + 2 * (1 - t) * t * cy + t * t * y))
        d.line(pts, fill=self.color, width=self.width, joint="curve")
        (ax, ay), (bx, by) = pts[-4], pts[-1]
        ang = math.atan2(by - ay, bx - ax)
        L = 16
        p1 = (bx - L * math.cos(ang - 0.45), by - L * math.sin(ang - 0.45))
        p2 = (bx - L * math.cos(ang + 0.45), by - L * math.sin(ang + 0.45))
        d.polygon([(bx, by), p1, p2], fill=self.color)
        if self.label:
            d.text((cx, y - self.hgt - 8), self.label, font=self.lf, fill=self.color, anchor="md")


class NumberLine(El):
    anim = "wipe_right"
    dur = 0.6

    def __init__(self, x0, x1, y, vmin, vmax, step, labels=(), size=26, **kw):
        super().__init__(**kw)
        self.x0, self.x1, self.y, self.vmin, self.vmax, self.step = x0, x1, y, vmin, vmax, step
        self.labels = labels
        self.f = font(size, 600)

    def X(self, v):
        return self.x0 + (v - self.vmin) / (self.vmax - self.vmin) * (self.x1 - self.x0)

    def bbox(self):
        return (self.x0 - 30, self.y - 20, self.x1 + 30, self.y + 60)

    def draw(self, d, ox, oy):
        y = self.y - oy
        c = COL["ink"]
        d.line((self.x0 - 25 - ox, y, self.x1 + 25 - ox, y), fill=c, width=4)
        for sgn, xe in ((-1, self.x0 - 25), (1, self.x1 + 25)):
            xe -= ox
            d.polygon([(xe + sgn * 10, y), (xe, y - 8), (xe, y + 8)], fill=c)
        v = self.vmin
        while v <= self.vmax + 1e-9:
            x = self.X(v) - ox
            big = v in self.labels
            d.line((x, y - (14 if big else 8), x, y + (14 if big else 8)), fill=c, width=3 if big else 2)
            if big:
                d.text((x, y + 22), str(v), font=self.f, fill=c, anchor="mt")
            v += self.step


# ---------------------------------------------------------------- timeline
class Seg:
    def __init__(self, text, actions, pad=0.45, caption=None, min_dur=0.0, silent=False):
        self.text = text
        self.actions = actions
        self.pad = pad
        self.caption = text if caption is None else caption
        self.min_dur = min_dur
        self.silent = silent
        self.audio = None
        self.dur = 0


def add(el, at=0.0):
    return ("add", at, el)


def rm(id, at=0.0):
    return ("rm", at, id)


def clear(at=0.0):
    return ("clear", at, None)


class TTS:
    def __init__(self, voice="af_heart", speed=0.88):
        from kokoro_onnx import Kokoro
        tdir = os.environ.get("KOKORO_DIR", "/home/user/tts")
        self.k = Kokoro(os.path.join(tdir, "kokoro-v1.0.onnx"), os.path.join(tdir, "voices-v1.0.bin"))
        self.voice, self.speed = voice, speed
        self.sr = 24000
        os.makedirs(os.path.join(BUILD, "tts"), exist_ok=True)

    def say(self, text):
        key = hashlib.md5(f"{self.voice}|{self.speed}|{text}".encode()).hexdigest()
        path = os.path.join(BUILD, "tts", key + ".npy")
        if os.path.exists(path):
            return np.load(path)
        samples, sr = self.k.create(text, voice=self.voice, speed=self.speed, lang="en-us")
        samples = np.asarray(samples, dtype=np.float32)
        # trim leading/trailing silence
        nz = np.where(np.abs(samples) > 0.01)[0]
        if len(nz):
            samples = samples[max(0, nz[0] - 600): nz[-1] + 1200]
        np.save(path, samples)
        return samples


def ease_back(p):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


def _alpha(img, k):
    if k >= 0.999:
        return img
    img = img.copy()
    a = img.getchannel("A").point(lambda v: int(v * k))
    img.putalpha(a)
    return img


def make_background():
    bg = Image.new("RGBA", (W, H), COL["bg"] + (255,))
    d = ImageDraw.Draw(bg)
    for x in range(0, W, 40):
        for y in range(0, H - 80, 40):
            d.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=COL["cream_d"])
    sq = [("purple", 18, 16), ("green", 40, 16), ("pink", 62, 16), ("orange", 18, 38), ("blue", 40, 38)]
    for c, x, y in sq:
        d.rectangle((W - 90 + x, y - 8, W - 90 + x + 14, y + 6), fill=COL[c])
    return bg


def caption_sprite(text):
    if not text:
        return None
    f = font(27, 700, "andika")
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) > 1160 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    lines = lines[:2]
    h = 12 + 34 * len(lines)
    img = Image.new("RGBA", (W, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    wmax = max(f.getlength(l) for l in lines)
    x0 = (W - wmax) / 2 - 24
    d.rounded_rectangle((x0, 0, W - x0, h), radius=16, fill=(43, 43, 58, 225))
    for i, l in enumerate(lines):
        d.text((W / 2, 8 + 34 * i), l, font=f, fill=(255, 255, 255), anchor="mt")
    return img, H - h - 8


def render(segs, out_path, voice="af_heart"):
    os.makedirs(BUILD, exist_ok=True)
    tts = TTS(voice=voice)
    sr = tts.sr
    # ---- audio + timing
    chunks, t = [], 0.0
    lead = 0.15
    for s in segs:
        last_action = max([a[1] for a in s.actions] + [0])
        if s.text and not s.silent:
            s.audio = tts.say(s.text)
            alen = len(s.audio) / sr
        else:
            s.audio, alen = None, 0
        s.dur = max(lead + alen + s.pad, s.min_dur, last_action + 0.55)
        s.start = t
        buf = np.zeros(int(round(s.dur * sr)), dtype=np.float32)
        if s.audio is not None:
            i0 = int(lead * sr)
            buf[i0:i0 + len(s.audio)] = s.audio[: len(buf) - i0]
        chunks.append(buf)
        t += s.dur
    total = t + 1.0
    chunks.append(np.zeros(int(sr * 1.0), dtype=np.float32))
    audio = np.concatenate(chunks)
    audio = audio / max(1e-6, np.abs(audio).max()) * 0.89
    wav_path = os.path.join(BUILD, "narration.wav")
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    print(f"timeline: {len(segs)} segments, {total/60:.1f} min", flush=True)

    # ---- events
    events = []
    for si, s in enumerate(segs):
        for kind, at, payload in s.actions:
            events.append((s.start + at, si, kind, payload))
    events.sort(key=lambda e: (e[0], e[1]))

    bg = make_background()
    caps = [caption_sprite(s.caption if not s.silent else s.caption) for s in segs]

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav_path,
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest", out_path]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    elements = []  # list of [el, t0, settled]
    base = bg.copy()
    ei = 0
    seg_i = 0
    nframes = int(total * FPS)
    last_key, last_bytes = None, None
    dirty = False
    base_ver = 0
    for fi in range(nframes):
        t = fi / FPS
        while seg_i + 1 < len(segs) and segs[seg_i + 1].start <= t:
            seg_i += 1
        while ei < len(events) and events[ei][0] <= t:
            et, _, kind, payload = events[ei]
            if kind == "add":
                if payload.id:
                    elements = [e for e in elements if e[0].id != payload.id]
                    dirty = True
                elements.append([payload, et, False])
            elif kind == "rm":
                ids = payload if isinstance(payload, (list, tuple)) else [payload]
                elements = [e for e in elements
                            if not (e[0].id and any(e[0].id == i or (i.endswith("*") and e[0].id.startswith(i[:-1])) for i in ids))]
                dirty = True
            elif kind == "clear":
                elements = []
                dirty = True
            ei += 1
        # settle finished animations
        for e in elements:
            if not e[2] and t - e[1] >= e[0].dur:
                e[2] = True
                dirty = True
        if dirty:
            base = bg.copy()
            for el, _, settled in elements:
                if settled:
                    spr, x, y = el.sprite()
                    base.alpha_composite(spr, (x, y)) if x >= 0 and y >= 0 else base.paste(spr, (x, y), spr)
            dirty = False
            base_ver += 1
        animating = [e for e in elements if not e[2]]
        key = (base_ver, seg_i)
        if not animating and key == last_key:
            ff.stdin.write(last_bytes)
            continue
        frame = base.copy()
        for el, t0, _ in animating:
            p = max(0.0, min(1.0, (t - t0) / el.dur))
            spr, x, y = el.sprite()
            w, h = spr.size
            if el.anim == "pop":
                s = max(0.05, ease_back(p))
                nw, nh = max(1, int(w * s)), max(1, int(h * s))
                img = _alpha(spr.resize((nw, nh), Image.BILINEAR), min(1, p * 2.5))
                frame.paste(img, (int(x + (w - nw) / 2), int(y + (h - nh) / 2)), img)
            elif el.anim == "wipe_down":
                hh = max(1, int(h * p))
                img = spr.crop((0, 0, w, hh))
                frame.paste(img, (x, y), img)
            elif el.anim == "wipe_right":
                ww = max(1, int(w * p))
                img = spr.crop((0, 0, ww, h))
                frame.paste(img, (x, y), img)
            else:  # fade
                img = _alpha(spr, p)
                frame.paste(img, (x, y), img)
        cap = caps[seg_i]
        if cap:
            frame.alpha_composite(cap[0], (0, cap[1]))
        data = frame.convert("RGB").tobytes()
        ff.stdin.write(data)
        last_key, last_bytes = (key if not animating else None), data
        if fi % (FPS * 30) == 0:
            print(f"  frame {fi}/{nframes} ({100*fi/nframes:.0f}%)", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done ->", out_path, flush=True)
    return total
