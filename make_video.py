"""Grade 2 lesson video: draw ones, tens, and hundreds to count up (Eureka Math2 G2 M1 L21-22)."""
import os
import sys

from engine import (COL, Arrow, Circle, El, Hundred, Mark, NumberLine, One, Rect, Seg, Ten, Text,
                    add, clear, render, rm)

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


def plural(n, unit):
    return f"{words(n)} {unit}" + ("" if n == 1 else "s")


SEGS = []


def say(text, *actions, pad=0.45, caption=None, min_dur=0.0):
    SEGS.append(Seg(text, list(actions), pad=pad, caption=caption, min_dur=min_dur))


def pause(dur, *actions, caption=""):
    SEGS.append(Seg("", list(actions), pad=0, caption=caption, min_dur=dur, silent=True))


def header(title, color="purple"):
    f_w = 30 * 0.62 * len(title) + 60
    return [add(Rect(30, 18, 30 + f_w, 72, fill=color, r=27, id="hdr_bg", anim="pop")),
            add(Text(30 + f_w / 2, 45, title, 32, "white", id="hdr_t"), 0.1)]


# ================================================================== 1. title
def title_scene():
    acts = [clear()]
    acts.append(add(Text(640, 200, "Counting Up with", 64, "ink", id="t1"), 0.0))
    acts.append(add(Text(640, 285, "Ones, Tens & Hundreds", 72, "purple", id="t2"), 0.4))
    acts.append(add(Text(640, 370, "Grade 2  •  Draw units to count", 34, "soft", 600, id="t3"), 0.8))
    x = 380
    for i in range(3):
        acts.append(add(Hundred(x + i * 80, 430, 64), 1.0 + 0.15 * i))
    for i in range(4):
        acts.append(add(Ten(x + 250 + i * 26, 430, 16, 64), 1.5 + 0.1 * i))
    for i in range(5):
        acts.append(add(One(x + 370 + i * 24, 480, 16), 1.9 + 0.08 * i))
    say("Hi friends! Welcome to math time!", *acts, min_dur=2.6)
    say("Today we will learn how to count up from one number to another number, "
        "by drawing ones, tens, and hundreds. Let's go!")


# ================================================================== 2. units
def units_scene():
    say("First, let's meet our three units.", clear(), *header("Meet the units", "blue"))
    say("This little cube is one. We call it a one.",
        add(One(170, 260, 60, id="cube")),
        add(Text(200, 370, "1 one", 40, "orange", id="l1"), 0.6))
    # ten ones
    say("Now let's put ten ones together. Count with me!", rm("l1"))
    for i in range(10):
        y = 560 - (i + 1) * 40
        say(words(i + 1).capitalize() + ("!" if i == 9 else ","), add(One(450, y, 38, id=f"c{i}")),
            pad=0.12, caption=str(i + 1))
    say("Ten ones make one ten! A ten looks like a long stick.",
        rm("c*"), add(Ten(450, 160, 38, 400, id="bigten")),
        add(Text(470, 600, "1 ten = 10 ones", 36, "green", id="l2"), 0.4), pad=0.6)
    say("Now let's put ten tens together. Count by tens with me!", rm(["cube", "bigten", "l2"]))
    for i in range(10):
        say(words((i + 1) * 10).capitalize() + ("!" if i == 9 else ","),
            add(Ten(380 + i * 52, 160, 38, 380, id=f"r{i}")), pad=0.12, caption=str((i + 1) * 10))
    say("Ten tens make one hundred! A hundred looks like a big flat square.",
        rm("r*"), add(Hundred(450, 150, 380, id="bighun")),
        add(Text(640, 585, "1 hundred = 10 tens", 36, "purple", id="l3"), 0.4), pad=0.6)
    say("So, ten ones make a ten, and ten tens make a hundred.",
        rm(["bighun", "l3"]),
        add(One(230, 330, 40)), add(Text(250, 430, "one", 38, "orange"), 0.1),
        add(Text(380, 350, "→", 60, "ink", fam="dejavu"), 0.4),
        add(Ten(560, 250, 34, 340), 0.8), add(Text(577, 625, "ten", 38, "green"), 0.9),
        add(Text(720, 350, "→", 60, "ink", fam="dejavu"), 1.3),
        add(Hundred(860, 250, 200), 1.7), add(Text(960, 500, "hundred", 38, "purple"), 1.8),
        min_dur=3.0)


# ================================================================== 3. quick drawings
def quick_scene():
    say("Drawing blocks takes a long time. So, mathematicians use quick drawings!",
        clear(), *header("Quick drawings", "green"))
    say("For a one, we draw a little line.",
        add(Text(260, 160, "one", 46, "orange")),
        add(Mark("one", 260, 230, 110, width=9), 0.5),
        add(Text(260, 395, "= 1", 40, "ink"), 0.9))
    say("For a ten, we draw a line with a cross on it. It looks like a stick tied together.",
        add(Text(640, 160, "ten", 46, "green")),
        add(Mark("ten", 640, 230, 110, width=9), 0.5),
        add(Text(640, 395, "= 10", 40, "ink"), 0.9))
    say("For a hundred, we draw a square.",
        add(Text(1020, 160, "hundred", 46, "purple")),
        add(Mark("hundred", 1020, 240, 110, width=8), 0.5),
        add(Text(1020, 395, "= 100", 40, "ink"), 0.9))
    acts = [add(Text(640, 470, "Let's try:  234", 40, "ink", id="try"))]
    acts2 = []
    x = 430
    for i in range(2):
        acts2.append(add(Mark("hundred", x + i * 70, 520, 66), 0.3 + i * 0.4))
    for i in range(3):
        acts2.append(add(Mark("ten", x + 170 + i * 46, 520, 70), 1.3 + i * 0.35))
    for i in range(4):
        acts2.append(add(Mark("one", x + 340 + i * 36, 520, 70), 2.4 + i * 0.3))
    say("Let's try two hundred thirty-four.", *acts)
    say("Two hundreds, three tens, and four ones.", *acts2, min_dur=4.0)


# ================================================================== 4. friendly numbers
def friendly_scene():
    say("When we count up, it helps to land on friendly numbers.",
        clear(), *header("Next ten, next hundred", "orange"))
    say("Friendly numbers end in zero, like forty, or in two zeros, like two hundred.",
        add(Text(450, 170, "40", 80, "green")), add(Text(830, 170, "200", 80, "purple"), 0.8))
    nl = NumberLine(140, 1140, 380, 30, 50, 1, labels=(30, 37, 40, 50), id="nl")
    say("What is the next ten after thirty-seven?", clear(), *header("Next ten, next hundred", "orange"),
        add(Text(640, 160, "What is the next ten after 37?", 46, "ink", id="q")),
        add(nl, 0.3), add(Circle(nl.X(37), 380, 14, fill="pink", outline="pink", id="dot"), 0.9))
    say("Let's count up by ones.")
    for v in (38, 39, 40):
        say(words(v).capitalize() + ("!" if v == 40 else ","),
            add(Arrow(nl.X(v - 1), nl.X(v), 365, 40, "orange", label="+1", label_size=24)), pad=0.25)
    say("Forty is the next ten! We drew three ones to get there.",
        add(Text(640, 520, "Next ten after 37 is 40", 46, "green")), pad=0.6)

    nl2 = NumberLine(140, 1140, 400, 100, 200, 10, labels=(100, 120, 150, 200), id="nl2")
    say("Now, what is the next hundred after one hundred twenty?", clear(),
        *header("Next ten, next hundred", "orange"),
        add(Text(640, 160, "What is the next hundred after 120?", 46, "ink")),
        add(nl2, 0.3), add(Circle(nl2.X(120), 400, 14, fill="pink", outline="pink"), 0.9))
    say("Let's count up by tens.")
    for v in range(130, 201, 10):
        say(words(v).capitalize() + ("!" if v == 200 else ","),
            add(Arrow(nl2.X(v - 10), nl2.X(v), 385, 40, "green", label="+10", label_size=22)), pad=0.2)
    say("Two hundred is the next hundred! We drew eight tens to get there.",
        add(Text(640, 540, "Next hundred after 120 is 200", 46, "purple")), pad=0.6)


# ================================================================== 5. plan
def plan_scene():
    say("Here is our counting plan. We will use it for every problem.",
        clear(), *header("Our counting plan", "pink"))
    steps = [
        ("Draw the start number.", "ink", "We start by drawing the first number."),
        ("Draw ONES to get to the next ten.", "orange", "Next, we draw ones to get to the next ten."),
        ("Draw TENS to get to the next hundred.", "green", "Then, we draw tens to get to the next hundred."),
        ("Draw HUNDREDS to get close.", "purple", "Then, we take big jumps. We draw hundreds to get close to the end number."),
        ("Draw TENS or ONES to finish.", "blue_d", "Last, we draw tens, or ones, to finish."),
    ]
    for i, (txt, c, narr) in enumerate(steps):
        y = 135 + i * 92
        say(narr, add(Circle(120, y, 30, fill=c, outline=c)),
            add(Text(120, y, str(i + 1), 34, "white"), 0.1),
            add(Text(175, y, txt, 42, c, anchor="lm"), 0.25))
    say("And remember: say each number out loud as you draw it!", pad=0.7)


# ================================================================== problem solver
UNIT_COLOR = {"one": "orange", "ten": "green", "hundred": "purple"}
UNIT_SIZE = {"one": 1, "ten": 10, "hundred": 100}


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
        steps.append(("ten", vals, "finish_tens"))
        cur = vals[-1]
    if cur < end:
        steps.append(("one", list(range(cur + 1, end + 1)), "finish_ones"))
    return steps


def start_blocks(n, at0=0.0, step=0.18):
    """Base-ten blocks for n inside the left box. Returns (hundred_acts, ten_acts, one_acts)."""
    h, t, o = n // 100, (n // 10) % 10, n % 10
    acts = ([], [], [])
    y = 125
    for i in range(h):
        acts[0].append(add(Hundred(62 + i * 58, y, 50, id=f"blk_h{i}"), at0 + i * step))
    y2 = y + 70 if h else 140
    rh = 100 if h else 150
    for i in range(t):
        acts[1].append(add(Ten(62 + i * 22, y2, 15, rh, id=f"blk_t{i}"), at0 + i * step))
    cx = 62 + t * 22 + (14 if t else 0)
    for i in range(o):
        col, row = divmod(i, 5)
        acts[2].append(add(One(cx + col * 20, y2 + rh - 17 - row * 20, 15, id=f"blk_o{i}"), at0 + i * step))
    return acts


def counter(v):
    return add(Text(255, 492, str(v), 68, "pink", id="counter"))


def problem(start, end, label, color, practice=False, source=""):
    steps = plan_steps(start, end)
    hdr = header(label, color)
    task = f"Draw units to count from {start} to {end}."
    say(("Your turn! " if practice else "") +
        f"Let's draw units to count from {words(start)} to {words(end)}.",
        clear(), *hdr,
        add(Text(330 + 30 * 0.62 * len(label), 45, task, 36, "ink", anchor="lm", id="task"), 0.2),
        caption=task)
    if practice:
        say("Pause the video and try it on your paper. Then press play, and we will check it together!",
            add(Rect(340, 250, 940, 470, fill="yellow", outline="ink", width=5, r=30, id="pz_bg", anim="pop")),
            add(Text(640, 330, "Pause and try!", 64, "ink", id="pz1"), 0.2),
            add(Text(640, 405, "Then press play to check.", 36, "ink", 600, id="pz2"), 0.4))
        pause(2.5, caption="Pause and try!")
        say("Okay, let's check together!", rm(["pz_bg", "pz1", "pz2"]))

    # left panel
    h, t, o = start // 100, (start // 10) % 10, start % 10
    say(f"First, we draw {words(start)}.",
        add(Rect(38, 100, 478, 340, fill="white", outline="blue", width=4, id="box")),
        add(Text(258, 372, str(start), 44, "blue_d", id="startlbl"), 0.3))
    ha, ta, oa = start_blocks(start)
    if h:
        say(plural(h, "hundred").capitalize() + ",", *ha, pad=0.2, caption=f"{h} hundreds")
    if t:
        say(plural(t, "ten").capitalize() + ",", *ta, pad=0.2, caption=f"{t} tens")
    if o:
        say(("and " if (h or t) else "") + plural(o, "one") + ".", *oa, pad=0.3, caption=f"{o} ones")
    say(f"That's {words(start)}.",
        add(Rect(38, 418, 478, 560, fill="white", outline="pink", width=4, id="cbox")),
        add(Text(255, 440, "We are at:", 28, "soft", 600, id="cl"), 0.1), counter(start),
        add(Text(258, 600, f"Goal: {end}", 40, "green", id="goal"), 0.3))

    cur = start
    row_y = [112, 240, 368, 496]
    for ri, (unit, vals, why) in enumerate(steps):
        ytop = row_y[ri]
        tag = {"one": "+ ones", "ten": "+ tens", "hundred": "+ hundreds"}[unit]
        c = UNIT_COLOR[unit]
        tag_acts = [add(Rect(505, ytop + 8, 645, ytop + 54, fill=c, r=23, id=f"tag{ri}", anim="pop")),
                    add(Text(575, ytop + 31, tag, 26, "white", id=f"tagt{ri}"), 0.1)]
        if why == "next_ten":
            say(f"What is the next ten after {words(cur)}?", pad=0.3)
            say(f"It's {words(vals[-1])}! Let's draw ones to get there.", *tag_acts)
        elif why == "next_hundred":
            say(f"Now, what is the next hundred after {words(cur)}?", pad=0.3)
            say(f"It's {words(vals[-1])}! Let's draw tens to get there.", *tag_acts)
        elif why == "hundreds":
            say(f"{words(end).capitalize()} is still far away. So let's take big jumps, and draw hundreds!",
                *tag_acts)
        elif why == "finish_tens":
            say(f"We need to get to {words(end)}. Let's draw tens.", *tag_acts)
        else:
            say(f"Now let's draw ones to get to {words(end)}.", *tag_acts)
        for i, v in enumerate(vals):
            x = 690 + i * 72
            mh = 50 if unit == "hundred" else 56
            say(words(v).capitalize() + ("!" if v == vals[-1] else ","),
                add(Mark(unit, x, ytop + 4, mh, id=f"m{ri}_{i}")),
                add(Text(x, ytop + 84, str(v), 25, "ink", 600, id=f"ml{ri}_{i}"), 0.15),
                counter(v), pad=0.15, caption=str(v))
        cur = vals[-1]
        n = len(vals)
        if cur == end:
            break
        if why == "hundreds":
            say(f"Can we draw one more hundred? No! {words(cur + 100).capitalize()} is more than "
                f"{words(end)}. So we stop drawing hundreds.", pad=0.4)
        elif why == "finish_tens" and steps[-1][2] == "finish_ones":
            say(f"One more ten would be {words(cur + 10)}. That's too much! So we stop.", pad=0.4)
        else:
            say(f"We drew {plural(n, unit)}. Now we are at {words(cur)}.", pad=0.4)
    say(f"We made it to {words(end)}! Great job!",
        add(Rect(830, 590, 1250, 640, fill="green", r=25, id="win", anim="pop")),
        add(Text(1040, 615, f"We made it to {end}!", 32, "white", id="wint"), 0.1), pad=0.8)

    # ---- summary hop chain
    say("Let's look at our jumps.", clear(), *header(label, color),
        add(Text(330 + 30 * 0.62 * len(label), 45, task, 36, "ink", anchor="lm"), 0.0))
    pts = [start] + [v[-1] for _, v, _ in steps]
    nb = len(pts)
    gap = min(260, 1100 / max(1, nb - 1))
    xs = [640 - gap * (nb - 1) / 2 + i * gap for i in range(nb)]
    y = 360
    say(f"We started at {words(start)}.", add(Circle(xs[0], y, 62, fill="white", outline="blue_d", width=6)),
        add(Text(xs[0], y, str(start), 40, "blue_d"), 0.1))
    parts = []
    for i, (unit, vals, _) in enumerate(steps):
        n, c = len(vals), UNIT_COLOR[unit]
        lbl = f"+{n} {unit}{'' if n == 1 else 's'}"
        parts.append(n * UNIT_SIZE[unit])
        say(f"We drew {plural(n, unit)} to get to {words(vals[-1])}.",
            add(Arrow(xs[i] + 50, xs[i + 1] - 50, y - 50, 70, c, label=lbl, label_size=28)),
            add(Circle(xs[i + 1], y, 62, fill="white", outline=c, width=6), 0.4),
            add(Text(xs[i + 1], y, str(vals[-1]), 40, c), 0.5), pad=0.3)
    eq = " + ".join(str(p) for p in parts) + f" = {sum(parts)}"
    spoken = ", plus ".join(words(p) for p in parts)
    if len(parts) > 1:
        say(f"Bonus! If we add up all our jumps: {spoken}. That makes {words(sum(parts))}.",
            add(Text(640, 520, eq, 46, "ink")), pad=0.3)
    say(f"So, {words(start)} plus {words(sum(parts))} equals {words(end)}!",
        add(Rect(320, 575, 960, 640, fill="yellow", r=30, anim="pop")),
        add(Text(640, 608, f"{start} + {sum(parts)} = {end}", 44, "ink"), 0.1), pad=1.0)


# ================================================================== recap
def recap_scene():
    say("Wow, you did it! Let's remember what we learned.", clear(), *header("Remember!", "green"))
    pts = [("Ten ones make a ten. Ten tens make a hundred.", "ink"),
           ("Draw ones to get to the next ten.", "orange"),
           ("Draw tens to get to the next hundred.", "green"),
           ("Draw hundreds to take big jumps.", "purple"),
           ("Say each number as you draw!", "pink")]
    for i, (p, c) in enumerate(pts):
        y = 150 + i * 88
        say(p, add(Text(110, y, "★", 44, "yellow", fam="dejavu", stroke=2, stroke_color="ink")),
            add(Text(160, y, p, 40, c, anchor="lm"), 0.15))
    say("Great job today, mathematicians! Keep practicing, and see you next time. Bye bye!",
        add(Rect(340, 590, 940, 645, fill="purple", r=27, anim="pop")),
        add(Text(640, 617, "Great job! See you next time!", 34, "white"), 0.1), pad=1.5)


def build():
    title_scene()
    units_scene()
    quick_scene()
    friendly_scene()
    plan_scene()
    say("Now let's solve some problems together, just like in our book.", clear(),
        add(Text(640, 330, "Let's solve!", 90, "purple")), pad=0.6)
    problem(37, 200, "Example 1", "blue")
    problem(326, 750, "Example 2", "blue")
    problem(112, 200, "Practice 1", "pink", practice=True)
    problem(476, 800, "Practice 2", "pink", practice=True)
    problem(578, 920, "Practice 3", "pink", practice=True)
    recap_scene()
    return SEGS


if __name__ == "__main__":
    segs = build()
    if len(sys.argv) > 2 and sys.argv[1] == "--only":
        a, b = map(int, sys.argv[2].split(":"))
        segs = segs[a:b]
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[-1] if sys.argv[-1].endswith(".mp4") else "counting_up_grade2.mp4")
    render(segs, out)
