"""Printable lesson handout (Letter, portrait): concept pages + one solved problem per page."""
import os

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image as RLImage, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

import make_video
from engine import Bubble, Bundle, Kid, Mark, Straw, Text

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, "build", "handout")
os.makedirs(BUILD, exist_ok=True)

pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

PINK = colors.HexColor("#C81E64")
GREEN = colors.HexColor("#229654")
INK = colors.HexColor("#2B2B3A")
SOFT = colors.HexColor("#6E6E7D")
CREAM = colors.HexColor("#FFF8EC")

S = {
    "title": ParagraphStyle("title", fontName="DVB", fontSize=24, leading=30, textColor=PINK, alignment=TA_CENTER),
    "sub": ParagraphStyle("sub", fontName="DV", fontSize=12, leading=16, textColor=SOFT, alignment=TA_CENTER),
    "h": ParagraphStyle("h", fontName="DVB", fontSize=16, leading=22, textColor=GREEN, spaceBefore=10, spaceAfter=6),
    "body": ParagraphStyle("body", fontName="DV", fontSize=12.5, leading=18, textColor=INK),
    "step": ParagraphStyle("step", fontName="DV", fontSize=13, leading=19, textColor=INK, leftIndent=18,
                           bulletIndent=2, spaceAfter=3),
    "task": ParagraphStyle("task", fontName="DVB", fontSize=15, leading=21, textColor=INK),
    "ican": ParagraphStyle("ican", fontName="DV", fontSize=13, leading=19, textColor=INK, alignment=TA_CENTER),
}


def draw(elements, size, name):
    """Render engine elements onto a white image and save it."""
    img = Image.new("RGBA", size, (255, 255, 255, 255))
    for el in elements:
        spr, x, y = el.sprite()
        img.paste(spr, (x, y), spr)
    path = os.path.join(BUILD, name + ".png")
    img.convert("RGB").save(path)
    return path


def pic(path, width, max_h=None):
    w, h = Image.open(path).size
    if max_h and width * h / w > max_h:
        width = max_h * w / h
    return RLImage(path, width=width, height=width * h / w)


def units_image():
    els = [Straw(95, 40, 14, 120), Text(102, 195, "1 one", 30, "pink"),
           Bundle(305, 40, 10, 120), Text(325, 195, "1 ten", 30, "pink"),
           Text(325, 232, "= 10 ones", 24, "soft", 600),
           Bundle(520, 40, 100, 120), Text(574, 195, "1 hundred", 30, "pink"),
           Text(574, 232, "= 10 tens", 24, "soft", 600)]
    return draw(els, (720, 260), "units")


def quick_image():
    els = [Text(110, 30, "one", 30, "ink"), Mark("one", 110, 60, 80, width=7), Text(110, 170, "1", 30, "pink"),
           Text(360, 30, "ten", 30, "ink"), Mark("ten", 360, 60, 80, width=7), Text(360, 170, "10", 30, "pink"),
           Text(610, 30, "hundred", 30, "ink"), Mark("hundred", 610, 60, 80, width=7),
           Text(610, 170, "100", 30, "pink")]
    x = 190
    for i in range(3):
        els.append(Mark("hundred", x, 230, 56, width=5)); x += 44
    x += 18
    for i in range(2):
        els.append(Mark("ten", x, 230, 56, width=5)); x += 38
    x += 18
    for i in range(6):
        els.append(Mark("one", x, 230, 56, width=5)); x += 17
    els.append(Text(370, 318, "326 = 3 hundreds, 2 tens, 6 ones", 26, "ink", 600))
    return draw(els, (720, 345), "quick")


def problem_images():
    """Final drawing of each solved problem, without the kid, speech bubble, or banner."""
    segs = make_video.build()
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
    pages.append(elements)
    out = []
    for els in pages:
        if not any(isinstance(e, Kid) for e in els):
            continue
        keep = []
        for e in els:
            if isinstance(e, (Kid, Bubble)):
                continue
            x0, y0, x1, y1 = e.bbox()
            if y0 < 80 or x0 > 740:  # header row and everything in/near the speech bubble
                continue
            keep.append(e)
        x1 = max(e.bbox()[2] for e in keep) + 30
        y1 = max(e.bbox()[3] for e in keep) + 20
        img = Image.new("RGBA", (1280, 720), (255, 255, 255, 255))
        for e in keep:
            spr, x, y = e.sprite()
            img.paste(spr, (x, y), spr)
        path = os.path.join(BUILD, f"problem{len(out) + 1}.png")
        img.crop((30, 85, int(x1), int(y1))).convert("RGB").save(path)
        out.append(path)
    return out


PROBLEMS = [
    ("Practice Partner, Problem 1", 37, 200, True),
    ("Practice Partner, Problem 2", 326, 750, False),
    ("Practice, Problem 1", 112, 200, True),
    ("Practice, Problem 2", 476, 800, False),
    ("Lesson 22 Practice, Problem 2", 578, 920, False),
]


def book_sentences(start, end, given_box):
    steps = make_video.plan_steps(start, end)
    out = [] if given_box else [f"First, I draw {start}."]
    for ri, (unit, vals, why) in enumerate(steps):
        n, target = len(vals), vals[-1]
        units = make_video.unit_name(n, unit)
        k = ri if given_box else ri + 1
        if k == 0:
            out.append(f"The next ten is {target}. I draw ones to get to {target}.")
        elif ri == len(steps) - 1:
            out.append(f"Last, I draw {n} {units} to get to {target}.")
        elif k == 1:
            out.append(f"Next, I draw {n} {units} to get to {target}.")
        else:
            out.append(f"Then, I draw {n} {units} to get to {target}.")
    return out


def counts_line(start, end):
    vals = [str(v) for _, vs, _ in make_video.plan_steps(start, end) for v in vs]
    return f"{start}, " + ", ".join(vals)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 9)
    canvas.setFillColor(SOFT)
    canvas.drawString(0.75 * inch, 0.5 * inch, "Grade 2  •  Module 1  •  Topic E  •  Lessons 21–22  •  Draw units to count")
    canvas.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def box(flowables, border=GREEN, bg=CREAM):
    t = Table([[flowables]], colWidths=[6.9 * inch])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1.5, border), ("BACKGROUND", (0, 0), (-1, -1), bg),
                           ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    return t


def build():
    out = os.path.join(ROOT, "counting_up_grade2_handout.pdf")
    doc = SimpleDocTemplate(out, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.8 * inch,
                            title="Draw Ones, Tens, and Hundreds – Grade 2", author="Lesson handout")
    st = []
    # ---- page 1: concepts
    st += [Paragraph("Draw Ones, Tens, and Hundreds", S["title"]),
           Paragraph("Grade 2  •  Module 1  •  Topic E  •  Lessons 21–22", S["sub"]), Spacer(1, 12),
           box([Paragraph("<b>I can</b> draw ones, tens, and hundreds to make groups of tens, "
                          "hundreds, and 1 thousand.", S["ican"])]),
           Paragraph("1. Our units", S["h"]),
           Paragraph("A straw is <b>1 one</b>. We bundle 10 ones to make <b>1 ten</b>. "
                     "We bundle 10 tens to make <b>1 hundred</b>. And 10 hundreds make <b>1 thousand</b>.",
                     S["body"]), Spacer(1, 4), pic(units_image(), 5.4 * inch),
           Paragraph("2. Quick drawings", S["h"]),
           Paragraph("Drawing straws takes a long time, so we draw units the quick way: "
                     "a <b>line</b> for a one, a <b>line with a line across it</b> for a ten, "
                     "and a <b>bundle</b> for a hundred.", S["body"]), Spacer(1, 4),
           pic(quick_image(), 5.0 * inch), PageBreak()]
    # ---- page 2: the method
    st += [Paragraph("3. How to draw units to count", S["h"]),
           Paragraph("We count up from the first number to the last number. "
                     "We say each number as we draw it.", S["body"]), Spacer(1, 6)]
    for i, t in enumerate(["Draw the first number.",
                           "Draw <b>ones</b> to get to the next ten.",
                           "Draw <b>tens</b> to get to the next hundred.",
                           "Draw <b>hundreds</b>. Stop before you go past the last number.",
                           "Draw <b>tens</b> (or ones) to finish."], 1):
        st.append(Paragraph(t, S["step"], bulletText=f"{i}."))
    st += [Spacer(1, 10), Paragraph("Example from the book: 326 to 750", S["h"]),
           box([Paragraph(s, S["body"]) for s in book_sentences(326, 750, False)], border=PINK, bg=colors.white),
           Spacer(1, 8),
           Paragraph(f"<b>We say:</b> {counts_line(326, 750)}", S["body"]),
           Spacer(1, 14),
           Paragraph("Tip", S["h"]),
           Paragraph("The <b>next ten</b> after 37 is 40. The <b>next hundred</b> after 120 is 200. "
                     "Numbers that end in 0 or 00 are easy to jump from!", S["body"]),
           PageBreak()]
    # ---- one page per problem
    imgs = problem_images()
    for (label, a, b, given_box), img in zip(PROBLEMS, imgs):
        st += [Paragraph(label, S["h"]),
               Paragraph(f"Draw units to count from {a} to {b}.", S["task"]), Spacer(1, 10),
               box([pic(img, 6.4 * inch, 4.4 * inch)], border=colors.HexColor("#999999"), bg=colors.white),
               Spacer(1, 10), Paragraph("What I did:", S["h"]),
               box([Paragraph(s, S["body"]) for s in book_sentences(a, b, given_box)], border=PINK,
                   bg=colors.white),
               Spacer(1, 8), Paragraph(f"<b>We say:</b> {counts_line(a, b)}", S["body"]),
               PageBreak()]
    st.pop()
    doc.build(st, onFirstPage=footer, onLaterPages=footer)
    print("->", out)


if __name__ == "__main__":
    build()
