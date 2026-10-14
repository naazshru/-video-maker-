"""Cut a product "character sheet" (transparent PNG, views laid out in rows) into separate views.

usage: python3 tools/crop_sheet.py <sheet.png> <out_dir> [--height 900] [--names A,B,C,D,E,F,G,H,TOP,BOTTOM]

How it works (nothing is redrawn, pixels are only cropped and scaled):
 1. Read the alpha channel (transparency). Product pixels are opaque, background is transparent.
 2. Row split: for every pixel row, measure how much of it is opaque. Runs of "busy" rows separated
    by empty gaps are the rows of the sheet.
 3. Column split: inside each row do the same per pixel column -> one run per product view.
 4. Tight box: inside each cell keep only rows/columns that are clearly opaque (threshold ignores
    stray specks and soft glow), crop the original pixels to that box.
 5. Normalise: side views are scaled to the same height (same physical product = same height)
    and centred on one shared canvas, so all views line up for the 360° turntable.
    Top/bottom views are centred on a square canvas.
Writes <name>.png per view plus meta.json with each view's relative width (used by the pouch morph).
"""
import sys, json, argparse
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("sheet"); ap.add_argument("out")
ap.add_argument("--height", type=int, default=900)
ap.add_argument("--names", default="A,B,C,D,E,F,G,H,TOP,BOTTOM")
ap.add_argument("--alpha", type=int, default=200, help="opacity that counts as product")
a = ap.parse_args()

import os; os.makedirs(a.out, exist_ok=True)
im = Image.open(a.sheet).convert("RGBA")
A = np.array(im)
solid = A[:, :, 3] > a.alpha

def runs(mask, minlen=20):
    out, s = [], None
    for i, v in enumerate(mask):
        if v and s is None: s = i
        if not v and s is not None:
            if i - s > minlen: out.append((s, i))
            s = None
    if s is not None and len(mask) - s > minlen: out.append((s, len(mask)))
    return out

cells = []
for y0, y1 in runs(solid.mean(1) > 0.02):                 # rows of the sheet
    for x0, x1 in runs(solid[y0:y1].mean(0) > 0.05):      # views in that row
        cells.append((x0, y0, x1, y1))

names = a.names.split(",")
crops = {}
for n, (x0, y0, x1, y1) in zip(names, cells):
    X0, Y0 = max(0, x0 - 8), max(0, y0 - 8)
    sub = solid[Y0:y1 + 8, X0:x1 + 8]
    rr = np.where(sub.mean(1) > 0.03)[0]; cc = np.where(sub.mean(0) > 0.03)[0]
    box = (X0 + cc.min(), Y0 + rr.min(), X0 + cc.max() + 1, Y0 + rr.max() + 1)
    crops[n] = im.crop(box)
    crops[n].save(f"{a.out}/{n}_raw.png")
    print(n, box, crops[n].size)

side = [n for n in names if n in crops and n not in ("TOP", "BOTTOM")]
H = a.height
scaled = {n: crops[n].resize((round(crops[n].width * H / crops[n].height), H), Image.LANCZOS) for n in side}
CW = max(s.width for s in scaled.values())
widths = {}
for n, s in scaled.items():
    c = Image.new("RGBA", (CW, H), (0, 0, 0, 0)); c.paste(s, ((CW - s.width) // 2, 0))
    c.save(f"{a.out}/{n}.png"); widths[n] = s.width / CW
for n in ("TOP", "BOTTOM"):
    if n in crops:
        c = crops[n]; S = max(c.size)
        sq = Image.new("RGBA", (S, S), (0, 0, 0, 0)); sq.paste(c, ((S - c.width) // 2, (S - c.height) // 2))
        sq.resize((800, 800), Image.LANCZOS).save(f"{a.out}/{n}.png")
json.dump({"canvas": [CW, H], "widths": widths}, open(f"{a.out}/meta.json", "w"), indent=1)
print("canvas", CW, "x", H)
