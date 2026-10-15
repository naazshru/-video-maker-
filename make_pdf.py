"""Export the lesson as a PDF: the finished screen of every scene (no captions)."""
import os

from engine import make_background
import make_video


def scene_stills(segs):
    """Replay add/rm/clear actions and grab the final picture before each clear."""
    pages, elements, started = [], [], False
    for s in segs:
        for kind, at, payload in sorted(s.actions, key=lambda a: a[1]):
            if kind == "clear":
                if started and elements:
                    pages.append(list(elements))
                elements, started = [], True
            elif kind == "add":
                if payload.id:
                    elements = [e for e in elements if e.id != payload.id]
                elements.append(payload)
            elif kind == "rm":
                ids = payload if isinstance(payload, (list, tuple)) else [payload]
                elements = [e for e in elements if not (e.id and any(
                    e.id == i or (i.endswith("*") and e.id.startswith(i[:-1])) for i in ids))]
    if elements:
        pages.append(elements)
    imgs = []
    for els in pages:
        img = make_background()
        for el in els:
            spr, x, y = el.sprite()
            img.paste(spr, (x, y), spr)
        imgs.append(img.convert("RGB"))
    return imgs


if __name__ == "__main__":
    imgs = scene_stills(make_video.build())
    imgs = [im for i, im in enumerate(imgs) if i != 3]  # skip the "Let's solve!" title card
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "counting_up_grade2.pdf")
    imgs[0].save(out, save_all=True, append_images=imgs[1:], resolution=96)
    print(len(imgs), "pages ->", out)
