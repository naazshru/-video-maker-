"""Grade 2 lesson video that follows Eureka Math2 California, G2 M1 Topic E, Lessons 21-22:
"I can draw ones, tens, and hundreds to make groups of tens, hundreds, and 1 thousand."
Draw units to count from one number to another, the way the book shows it."""
import os
import sys

from engine import (Bubble, Bundle, Kid, Mark, Rect, Seg, Straw, Text, add, clear, font, render, rm)

ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
        "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def words(n):
    if n == 1000:
        return "one thousand"
    h, r = divmod(n, 100)
    parts = []
    if h:
        parts.append(ONES[h] + " hundred")
    if r:
        parts.append(ONES[r] if r < 20 else TENS[r // 10] + ("-" + ONES[r % 10] if r % 10 else ""))
    return " ".join(parts) or "zero"


def cap(s):
    return s[0].upper() + s[1:]


def unit_name(n, unit):
    return unit + ("" if n == 1 else "s")


SEGS = []


def say(text, *actions, pad=0.45, caption=None, min_dur=0.0):
    SEGS.append(Seg(text, list(actions), pad=pad, caption=caption, min_dur=min_dur))


def pause(dur, *actions, caption=""):
    SEGS.append(Seg("", list(actions), pad=0, caption=caption, min_dur=dur, silent=True))


def header(title, color="green"):
    w = font(30, 700).getlength(title) + 56
    return [add(Rect(30, 18, 30 + w, 70, fill=color, r=26, anim="pop")),
            add(Text(30 + w / 2, 44, title, 30, "white"), 0.1)], 30 + w


# ================================================================== 1. title
def title_scene():
    acts = [clear(),
            add(Text(640, 150, "Topic E  •  Lesson 21", 40, "soft", 600)),
            add(Text(640, 240, "Draw Ones, Tens, and Hundreds", 62, "pink"), 0.3),
            add(Rect(170, 310, 1110, 450, fill="white", outline="green", width=4, r=24), 0.6),
            add(Text(640, 350, "I can draw ones, tens, and hundreds to make", 36, "ink", 600), 0.8),
            add(Text(640, 405, "groups of tens, hundreds, and 1 thousand.", 36, "ink", 600), 0.8)]
    x = 480
    acts.append(add(Bundle(x, 490, 100, 90), 1.2))
    acts.append(add(Bundle(x + 110, 490, 10, 90), 1.4))
    acts.append(add(Bundle(x + 150, 490, 10, 90), 1.5))
    for i in range(3):
        acts.append(add(Straw(x + 200 + i * 18, 495, 10, 85), 1.7 + 0.1 * i))
    say("Hi friends! Welcome to math time! Today's lesson is about drawing ones, tens, and hundreds.",
        *acts, min_dur=3.0)
    say("I can draw ones, tens, and hundreds to make groups of tens, hundreds, and one thousand.")


# ================================================================== 2. units (straws and bundles)
def units_scene():
    h, _ = header("Ones, tens, and hundreds", "blue")
    say("Let's start with our units.", clear(), *h)
    say("This is one straw. It is one. We call it a one.",
        add(Straw(200, 200, 18, 150, id="s0")), add(Text(209, 400, "1 one", 40, "pink", id="l1"), 0.5))
    say("Let's count ten ones.", rm(["s0", "l1"]))
    for i in range(10):
        say(cap(words(i + 1)) + ("!" if i == 9 else ","), add(Straw(380 + i * 30, 200, 18, 150, id=f"s{i}")),
            pad=0.1, caption=str(i + 1))
    say("We put ten ones together in a bundle. Ten ones make one ten!",
        rm("s*"), add(Bundle(560, 190, 10, 170, id="b10")),
        add(Text(590, 410, "10 ones = 1 ten", 40, "pink", id="l2"), 0.4), pad=0.6)
    say("Now let's count ten tens. Count by tens with me!", rm(["b10", "l2"]))
    for i in range(10):
        say(cap(words((i + 1) * 10)) + ("!" if i == 9 else ","),
            add(Bundle(300 + i * 66, 200, 10, 150, id=f"t{i}")), pad=0.1, caption=str((i + 1) * 10))
    say("We put ten tens together in a big bundle. Ten tens make one hundred!",
        rm("t*"), add(Bundle(540, 180, 100, 200, id="b100")),
        add(Text(640, 430, "10 tens = 1 hundred", 40, "pink", id="l3"), 0.4), pad=0.6)
    say("Now let's count ten hundreds. Count by hundreds!", rm(["b100", "l3"]))
    for i in range(10):
        v = (i + 1) * 100
        say(cap(words(v)) + ("!" if i == 9 else ","),
            add(Bundle(120 + i * 106, 210, 100, 100, id=f"h{i}")),
            add(Text(165 + i * 106, 345, str(v), 26, "ink", 600, id=f"hl{i}"), 0.1),
            pad=0.1, caption=str(v))
    say("Ten hundreds make one thousand!",
        add(Text(640, 450, "10 hundreds = 1 thousand", 46, "pink", id="l4")), pad=0.8)


# ================================================================== 3. quick drawings
def quick_scene():
    h, _ = header("Draw units", "green")
    say("Drawing straws takes a long time. So we draw units the quick way.", clear(), *h)
    say("To draw a one, I draw a line.",
        add(Text(260, 150, "one", 46, "ink")), add(Mark("one", 260, 210, 120, width=9), 0.4),
        add(Text(260, 380, "1", 44, "pink"), 0.8))
    say("To draw a ten, I draw a line with a line across it.",
        add(Text(640, 150, "ten", 46, "ink")), add(Mark("ten", 640, 210, 120, width=9), 0.4),
        add(Text(640, 380, "10", 44, "pink"), 0.8))
    say("To draw a hundred, I draw a bundle, like this.",
        add(Text(1020, 150, "hundred", 46, "ink")), add(Mark("hundred", 1020, 210, 120, width=9), 0.4),
        add(Text(1020, 380, "100", 44, "pink"), 0.8))
    acts, x = [], 420
    for i in range(3):
        acts.append(add(Mark("hundred", x + i * 52, 450, 66), 0.4 + 0.35 * i))
    x += 3 * 52 + 20
    for i in range(2):
        acts.append(add(Mark("ten", x + i * 40, 450, 66), 1.6 + 0.35 * i))
    x += 2 * 40 + 20
    for i in range(6):
        acts.append(add(Mark("one", x + i * 28, 450, 66), 2.5 + 0.25 * i))
    acts.append(add(Text(560, 560, "326", 40, "ink"), 4.1))
    say("Here is three hundred twenty-six: three hundreds, two tens, and six ones.", *acts, min_dur=4.8)


# ================================================================== problem solver
UNIT_SIZE = {"one": 1, "ten": 10, "hundred": 100}
MARK_GAP = {"one": 17, "ten": 30, "hundred": 44}


def plan_steps(start, end):
    steps, cur = [], start
    if cur % 10 and (cur // 10 + 1) * 10 <= end:
        nt = (cur // 10 + 1) * 10
        steps.append(("one", list(range(cur + 1, nt + 1)), "next_ten"))
        cur = nt
    if cur % 100 and (cur // 100 + 1) * 100 <= end:
        nh = (cur // 100 + 1) * 100
        steps.append(("ten", list(range(cur + 10, nh + 1, 10)), "next_hundred"))
        cur = nh
    if cur + 100 <= end:
        vals = list(range(cur + 100, end // 100 * 100 + 1, 100))
        steps.append(("hundred", vals, "hundreds"))
        cur = vals[-1]
    if cur + 10 <= end:
        vals = list(range(cur + 10, end // 10 * 10 + 1, 10))
        steps.append(("ten", vals, "finish"))
        cur = vals[-1]
    if cur < end:
        steps.append(("one", list(range(cur + 1, end + 1)), "finish"))
    return steps


def wrap(text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    return lines


class BubbleText:
    """Adds sentences into the speech bubble, one under another."""
    X, Y, MAXW, LH, SIZE = 790, 120, 430, 34, 27

    def __init__(self):
        self.y = self.Y
        self.f = font(self.SIZE, 600)

    def line(self, sentence, at=0.2):
        acts = []
        for i, l in enumerate(wrap(sentence, self.f, self.MAXW)):
            acts.append(add(Text(self.X, self.y, l, self.SIZE, "ink", 600, anchor="lm"), at + 0.15 * i))
            self.y += self.LH
        self.y += 10
        return acts


def box_start(n):
    """The book's box with straws/bundles and the number under them (used when the book gives a box)."""
    h, t, o = n // 100, (n // 10) % 10, n % 10
    acts = [add(Rect(50, 92, 50 + 70 + h * 80 + t * 34 + o * 16 + (20 if o > 5 else 0), 222,
                     fill="white", outline="ink", width=3, r=6))]
    x, d = 70, 0.3
    for i in range(h):
        acts.append(add(Bundle(x, 102, 100, 82), d)); x += 80; d += 0.2
    for i in range(t):
        acts.append(add(Bundle(x, 102, 10, 82), d)); x += 34; d += 0.15
    if t:
        x += 6
    for i in range(o):
        acts.append(add(Straw(x, 104, 9, 80), d)); x += 16 + (20 if i == 4 else 0); d += 0.1
    width = 70 + h * 80 + t * 34 + o * 16 + (20 if o > 5 else 0)
    acts.append(add(Text(50 + width / 2, 204, str(n), 30, "ink", 600), d + 0.1))
    return acts


def quick_start(n):
    """Draw the start number with quick drawings, number underneath (like the book's 326)."""
    h, t, o = n // 100, (n // 10) % 10, n % 10
    acts, x, d = [], 75, 0.0
    for kind, cnt in (("hundred", h), ("ten", t), ("one", o)):
        for i in range(cnt):
            acts.append(add(Mark(kind, x, 105, 56, width=5), d))
            x += MARK_GAP[kind]
            d += 0.3
        if cnt:
            x += 18
    acts.append(add(Text((75 + x - 18 - MARK_GAP["one"]) / 2 + 10, 196, str(n), 30, "ink", 600), d))
    return acts, d


def problem(start, end, label, color, given_box, practice=False):
    steps = plan_steps(start, end)
    hacts, hx = header(label, color)
    task = f"Draw units to count from {start} to {end}."
    bt = BubbleText()
    say(("Your turn! " if practice else "") + f"Draw units to count from {words(start)} to {words(end)}.",
        clear(), *hacts, add(Text(hx + 30, 44, task, 34, "ink", anchor="lm"), 0.2), caption=task)
    if practice:
        say("Pause the video and try it on your paper. Then press play, and we will check it together!",
            add(Rect(340, 250, 940, 470, fill="yellow", outline="ink", width=5, r=30, id="pz_bg", anim="pop")),
            add(Text(640, 330, "Pause and try!", 64, "ink", id="pz1"), 0.2),
            add(Text(640, 405, "Then press play to check.", 36, "ink", 600, id="pz2"), 0.4))
        pause(2.5, caption="Pause and try!")
        say("Okay, let's check together!", rm(["pz_bg", "pz1", "pz2"]))

    side = [add(Kid(690, 400)), add(Bubble(760, 90, 1250, 630, tail_y=470), 0.1)]
    h, t, o = start // 100, (start // 10) % 10, start % 10
    parts = [f"{words(c)} {unit_name(c, u)}" for c, u in ((h, "hundred"), (t, "ten"), (o, "one")) if c]
    spoken_parts = (parts[0] if len(parts) == 1 else
                    f"{parts[0]} and {parts[1]}" if len(parts) == 2 else
                    f"{parts[0]}, {parts[1]}, and {parts[2]}")
    if given_box:
        say(f"The box shows {words(start)}. That's {spoken_parts}.", *side, *box_start(start), pad=0.6)
    else:
        acts, d = quick_start(start)
        say(f"First, I draw {words(start)}. {cap(spoken_parts)}.", *side, *acts,
            *bt.line(f"First, I draw {start}.", d + 0.3), min_dur=d + 1.2)

    row_y = [255, 350, 445, 540]
    x0 = 75
    cur = start
    for ri, (unit, vals, why) in enumerate(steps):
        n = len(vals)
        target = vals[-1]
        units = unit_name(n, unit)
        last = ri == len(steps) - 1
        k = ri if given_box else ri + 1
        if k == 0:
            first = f"The next ten is {target}. I draw ones to get to {target}."
            say(first.replace(str(target), words(target)), *bt.line(first), caption=first, pad=0.3)
        elif why == "next_ten":
            say(f"The next ten is {words(target)}. I draw ones to get to {words(target)}.", pad=0.3)
        elif why == "next_hundred":
            say(f"The next hundred is {words(target)}. I draw tens to get to {words(target)}.", pad=0.3)
        elif why == "hundreds":
            say(f"Now I can draw hundreds. I draw hundreds to get to {words(target)}.", pad=0.3)
        else:
            say(f"I draw {unit}s to get to {words(target)}.", pad=0.3)
        ytop = row_y[ri]
        for i, v in enumerate(vals):
            x = x0 + i * 64
            say(cap(words(v)) + ("!" if v == vals[-1] else ","),
                add(Mark(unit, x, ytop, 52)),
                add(Text(x, ytop + 72, str(v), 25, "ink", 600), 0.15), pad=0.15, caption=str(v))
        if why == "hundreds" and not last:
            say(f"I stop at {words(target)}, because {words(target + 100)} is more than {words(end)}.", pad=0.3)
        # book-style sentence in the speech bubble
        if k == 0:
            cur = target
            continue
        if last:
            sentence = f"Last, I draw {n} {units} to get to {target}."
        elif k == 1:
            sentence = f"Next, I draw {n} {units} to get to {target}."
        else:
            sentence = f"Then, I draw {n} {units} to get to {target}."
        say(sentence.replace(str(target), words(target)).replace(f" {n} ", f" {words(n)} "),
            *bt.line(sentence), caption=sentence, pad=0.5)
        cur = target
    say(f"I got to {words(end)}! Great job!",
        add(Rect(80, 600, 520, 648, fill="green", r=24, anim="pop")),
        add(Text(300, 624, f"We counted to {end}!", 30, "white"), 0.1), pad=1.0)


# ================================================================== recap
def recap_scene():
    h, _ = header("Remember!", "green")
    say("Great work! Let's remember how we draw units to count.", clear(), *h)
    pts = ["Draw the first number.",
           "Draw ones to get to the next ten.",
           "Draw tens to get to the next hundred.",
           "Draw hundreds.",
           "Draw tens or ones to finish.",
           "Say each number as you draw!"]
    for i, p in enumerate(pts):
        y = 140 + i * 78
        say(p, add(Text(110, y, "★", 40, "yellow", fam="dejavu", stroke=2, stroke_color="ink")),
            add(Text(160, y, p, 40, "ink", anchor="lm"), 0.15))
    say("Great job today, mathematicians! See you next time. Bye bye!",
        add(Rect(340, 610, 940, 655, fill="pink", r=22, anim="pop")),
        add(Text(640, 632, "Great job! See you next time!", 30, "white"), 0.1), pad=1.5)


def build():
    title_scene()
    units_scene()
    quick_scene()
    say("Now let's solve the problems from our book.", clear(),
        add(Text(640, 330, "Let's solve!", 90, "pink")), pad=0.6)
    problem(37, 200, "Practice Partner 1", "green", given_box=True)
    problem(326, 750, "Practice Partner 2", "green", given_box=False)
    problem(112, 200, "Practice 1", "pink", given_box=True, practice=True)
    problem(476, 800, "Practice 2", "pink", given_box=False, practice=True)
    problem(578, 920, "Lesson 22: Problem 2", "purple", given_box=False, practice=True)
    recap_scene()
    return SEGS


if __name__ == "__main__":
    segs = build()
    if len(sys.argv) > 2 and sys.argv[1] == "--only":
        a, b = map(int, sys.argv[2].split(":"))
        segs = segs[a:b]
    name = sys.argv[-1] if sys.argv[-1].endswith(".mp4") else "counting_up_grade2.mp4"
    render(segs, os.path.join(os.path.dirname(os.path.abspath(__file__)), name))
