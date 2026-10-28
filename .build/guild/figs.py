# Diagrams for the Guild. Each figNN() draws the inside of one <svg>; the chapter template
# supplies the <svg> element with its viewBox and aria-label, and refers to the drawing as __SVG:figNN__.
import html

MONO = 0.6                                             # width of a monospace character, in ems

class Fig:
    def __init__(self, tag):
        self.tag, self.out = tag, []
        self.out.append(f'<defs><marker id="{tag}-n" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                        f'markerHeight="7" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" '
                        f'fill="var(--ink-soft)"></path></marker><marker id="{tag}-h" viewBox="0 0 10 10" '
                        f'refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                        f'<path d="M 0 1 L 10 5 L 0 9 z" fill="var(--marine)"></path></marker></defs>')
    def rect(self, cls, x, y, w, h, rx=None):
        self.out.append(f'<rect class="{cls}" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"'
                        + (f' rx="{rx:g}"' if rx else '') + '></rect>')
    def text(self, cls, x, y, s, anchor=None):
        a = f' text-anchor="{anchor}"' if anchor else ''
        self.out.append(f'<text class="{cls}" x="{x:g}" y="{y:g}"{a}>{html.escape(s, quote=False)}</text>')
    def line(self, cls, x1, y1, x2, y2, arrow=None):
        m = f' marker-end="url(#{self.tag}-{arrow})"' if arrow else ''
        self.out.append(f'<line class="{cls}" x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}"{m}></line>')
    def path(self, cls, d, arrow=None):
        m = f' marker-end="url(#{self.tag}-{arrow})"' if arrow else ''
        self.out.append(f'<path class="{cls}" d="{d}"{m}></path>')
    def circle(self, cls, x, y, r):
        self.out.append(f'<circle class="{cls}" cx="{x:g}" cy="{y:g}" r="{r:g}"></circle>')
    def svg(self): return "\n          ".join(self.out)

    # ---- helpers shared by several figures ----
    def words(self, x, y, words, hot=(), size=12.5, h=26, gap=8, cls="dg-label"):
        """A row of boxed words starting at x, with y the top of the boxes; returns each box's centre."""
        centres = []
        for w in words:
            width = len(w) * size * MONO + 18
            self.rect("dg-hot" if w in hot else "dg-box", x, y, width, h)
            self.text(cls + (" dg-hot-text" if w in hot else ""), x + width / 2, y + h / 2 + size * 0.35, w,
                      "middle")
            centres.append(x + width / 2); x += width + gap
        return centres
    def code(self, x, y, parts, cls="dg-label", anchor=None):
        """One line of text made of (text, hot) pieces; the hot pieces are highlighted in place."""
        body = "".join(f'<tspan class="dg-hot-text">{html.escape(s, quote=False)}</tspan>' if hot
                       else html.escape(s, quote=False) for s, hot in parts)
        a = f' text-anchor="{anchor}"' if anchor else ''
        self.out.append(f'<text class="{cls}" x="{x:g}" y="{y:g}"{a}>{body}</text>')

def fig01():
    f = Fig("f01")
    f.text("dg-title", 24, 24, "BREADTH: THE SIXTEEN STAGES")
    for i in range(16):
        x = 24 + i * 44
        f.rect("dg-hot" if i == 8 else "dg-box", x, 36, 40, 28)
        f.text("dg-small" + (" dg-hot-text" if i == 8 else ""), x + 20, 54, f"{i:02}", "middle")
    f.text("dg-title", 24, 100, "DEPTH IN ONE AREA")
    f.text("dg-small", 24, 120, "stage 08, databases")
    levels = [(76, "use it", "dg-box"), (120, "configure and debug it", "dg-box"),
              (180, "know its internals and failure modes", "dg-hot"),
              (224, "change it: fix, contribute, rebuild", "dg-hot")]
    f.line("dg-edge", 396, 64, 396, 76)
    for n, (y, label, cls) in enumerate(levels, 1):
        f.rect(cls, 376, y, 40, 36)
        f.text("dg-label" + (" dg-hot-text" if cls == "dg-hot" else ""), 396, y + 23, str(n), "middle")
        f.text("dg-small", 430, y + 22, label)
    f.line("dg-life", 24, 168, 736, 168)
    f.text("dg-small", 24, 160, "what most teams need, above the line")
    f.text("dg-small dg-hot-text", 736, 296, "levels 3 and 4: where you're the one they call", "end")
    return f.svg()


def fig02():
    f = Fig("f02")
    for x, label in ((24, "INPUT SPLITS"), (170, "MAP TASKS"), (370, "SHUFFLE"), (480, "REDUCERS")):
        f.text("dg-title", x, 22, label)
    ys = [40 + i * 30 for i in range(8)]
    for i, y in enumerate(ys):
        f.rect("dg-box", 24, y, 96, 22)
        f.text("dg-small", 72, y + 15, f"split {i}", "middle")
        failed = i == 3
        f.rect("dg-doubt" if failed else "dg-box", 170, y, 150, 22)
        f.text("dg-small", 245, y + 15, "map 3 died: re-run" if failed else f"map {i}", "middle")
        f.line("dg-edge", 120, y + 11, 168, y + 11, "n")
        f.line("dg-edge", 320, y + 11, 368, y + 11, "n")
    f.rect("dg-iface", 370, 40, 70, 232)
    f.text("dg-small", 405, 150, "by key", "middle")
    f.text("dg-small", 405, 166, "hash", "middle")
    for r in range(3):
        y = 60 + r * 74
        f.line("dg-edge", 440, y + 18, 478, y + 18, "n")
        f.rect("dg-hot", 480, y, 120, 36)
        f.text("dg-label dg-hot-text", 540, y + 23, f"reduce {r}", "middle")
        f.line("dg-edge", 600, y + 18, 638, y + 18, "n")
        f.text("dg-small", 644, y + 22, f"output {r}")
    f.text("dg-small", 24, 296, "each map writes one partition per reducer; a combiner adds up repeats first")
    return f.svg()


def fig03():
    f = Fig("f03")
    E = 60                                                  # pixels per epsilon
    t1 = 170
    f.line("dg-axis", 40, 220, 730, 220, "n")
    f.text("dg-small", 730, 240, "true time", "end")
    # node A's interval when T1 asks to commit, and the timestamp s taken from its top
    f.text("dg-title", 40, 36, "NODE A: T1 COMMITS")
    f.rect("dg-span", t1 - E, 52, 2 * E, 18)
    f.text("dg-small", t1 - E - 8, 66, "TT.now()", "end")
    f.line("dg-life", t1, 44, t1, 220)
    f.text("dg-small", t1, 238, "t1", "middle")
    f.line("dg-life", t1 + E, 44, t1 + E, 220)
    f.text("dg-small dg-hot-text", t1 + E, 238, "s = latest", "middle")
    # commit wait: until node A's earliest bound passes s
    f.rect("dg-span-hot", t1, 92, 2 * E, 18)
    f.text("dg-small", t1 + 2 * E + 10, 106, "commit wait, about 2 epsilon")
    f.rect("dg-span", t1 + E, 132, 2 * E, 18)
    f.text("dg-small", t1 + 3 * E + 10, 146, "now earliest > s: T1 becomes visible")
    f.line("dg-life", t1 + 2 * E, 112, t1 + 2 * E, 220)
    # T2 starts afterwards on node B, whose clock may be off by up to epsilon either way
    tb = t1 + 2 * E + 110
    f.text("dg-title", tb - E, 176, "NODE B: T2 STARTS LATER")
    f.rect("dg-ok-box", tb - E, 186, 2 * E, 18)
    f.text("dg-small", tb + E + 10, 200, "so its timestamp is greater than s")
    return f.svg()


def fig04():
    f = Fig("f04")
    def stack(x, w, title, rows, note):
        f.text("dg-title", x, 26, title)
        for i, (label, cls) in enumerate(rows):
            y = 40 + i * 32
            f.rect(cls, x, y, w, 24)
            f.text("dg-small" + (" dg-hot-text" if cls == "dg-hot" else ""), x + w / 2, y + 16, label, "middle")
            if i:
                f.line("dg-edge", x + 24, y - 8, x + 24, y - 1, "n")
        f.text("dg-small", x, 40 + len(rows) * 32 + 12, note)
    common = [("json.dumps", "dg-box"), ("JSONEncoder.encode", "dg-box"), ("JSONEncoder.iterencode", "dg-box")]
    stack(40, 250, "DEFAULT: WITH THE ACCELERATOR", common + [("c_make_encoder, in C (_json)", "dg-hot")],
          "3 Python-level calls; the rest is C")
    stack(400, 320, "ACCELERATOR SWITCHED OFF", common + [("_make_iterencode", "dg-box"),
          ("_iterencode (a generator)", "dg-box"), ("_iterencode_dict (a generator)", "dg-box"),
          ("_iterencode_list, and more resumptions", "dg-box")],
          "49 Python-level calls, same output")
    return f.svg()


def fig05():
    f = Fig("f05")
    rungs = [("user", "runs it"), ("reporter", "files issues someone can reproduce"),
             ("contributor", "sends small, tested, explained patches"),
             ("regular", "a name the maintainers recognise"),
             ("reviewer", "trusted to judge other people's patches"),
             ("maintainer", "decides what the project is")]
    f.line("dg-edge", 40, 226, 40, 30, "h")
    for i, (name, what) in enumerate(rungs):
        y = 196 - i * 34
        top = i >= 4
        f.rect("dg-hot" if top else "dg-box", 60, y, 150, 26)
        f.text("dg-label" + (" dg-hot-text" if top else ""), 135, y + 18, name, "middle")
        f.text("dg-small", 226, y + 17, what)
    f.text("dg-small dg-hot-text", 736, 238, "each step is granted for making the maintainers' work easier", "end")
    return f.svg()


def fig06():
    f = Fig("f06")
    f.text("dg-title", 24, 22, "SECTION")
    f.text("dg-title", 300, 22, "THE REVIEWER'S QUESTION IT ANSWERS")
    rows = [("First paragraph", "What are you proposing, in two sentences?", True),
            ("Context", "Why now, and what's the evidence?", False),
            ("Goals and non-goals", "How will we know it worked? What's out of scope?", True),
            ("Proposal", "How does it work?", False),
            ("Alternatives considered", "Why not the obvious others, or doing nothing?", True),
            ("Risks", "What could go wrong, and what then?", False),
            ("Rollout", "How does it ship, and how do we undo it?", False),
            ("Open questions", "What's still undecided?", False)]
    for i, (name, question, hot) in enumerate(rows):
        y = 34 + i * 36
        f.rect("dg-hot" if hot else "dg-box", 24, y, 230, 28)
        f.text("dg-small" + (" dg-hot-text" if hot else ""), 36, y + 19, name)
        f.line("dg-edge", 254, y + 14, 290, y + 14, "n")
        f.text("dg-small", 300, y + 19, question)
    return f.svg()


def fig07():
    f = Fig("f07")
    X0, X1 = 230, 710                                       # 0% and 100% on the axis
    px = lambda p: X0 + (X1 - X0) * p / 100
    f.text("dg-title", 24, 22, "SHARE OF FUTURES WHERE MANAGED IS CHEAPER")
    f.line("dg-axis", X0, 200, X1, 200)
    for p in (0, 25, 50, 75, 100):
        f.line("dg-grid", px(p), 40, px(p), 200)
        f.text("dg-tick", px(p), 216, f"{p}%", "middle")
    rows = [("traffic growth", 62, 96), ("incidents a year", 68, 90), ("time to run it", 69, 90),
            ("cost of an incident", 71, 87)]
    for i, (name, lo, hi) in enumerate(rows):
        y = 48 + i * 36
        f.text("dg-small", X0 - 12, y + 16, name, "end")
        f.rect("dg-bar-hot" if i == 0 else "dg-bar", px(lo), y, px(hi) - px(lo), 22)
        f.text("dg-tick", px(lo) - 6, y + 15, f"{lo}%", "end")
        f.text("dg-tick", px(hi) + 6, y + 15, f"{hi}%")
    f.line("dg-life", px(79), 40, px(79), 200)
    f.text("dg-small", px(79), 240, "79% overall", "middle")
    return f.svg()


def fig08():
    f = Fig("f08")
    rows = [("words per sentence", 27.7, 14.8, 30), ("hedges", 8, 1, 10), ("passive constructions", 5, 0, 10),
            ("throat-clearing", 3, 0, 10), ("reading ease (higher is easier)", 58, 66, 100)]
    X0, W = 270, 380
    f.rect("dg-bar", 270, 14, 14, 12)
    f.text("dg-small", 290, 24, "draft")
    f.rect("dg-bar-hot", 360, 14, 14, 12)
    f.text("dg-small", 380, 24, "rewrite")
    for i, (name, a, b, top) in enumerate(rows):
        y = 44 + i * 38
        f.text("dg-small", X0 - 14, y + 17, name, "end")
        for j, (v, cls) in enumerate(((a, "dg-bar"), (b, "dg-bar-hot"))):
            w = max(2, W * v / top)
            f.rect(cls, X0, y + j * 13, w, 11)
            f.text("dg-tick", X0 + w + 8, y + j * 13 + 10, f"{v:g}")
    return f.svg()


def fig09():
    f = Fig("f09")
    def node(x, y, label, sub, cls="dg-box", w=120):
        f.rect(cls, x, y, w, 40)
        hot = " dg-hot-text" if cls == "dg-hot" else ""
        f.text("dg-small" + hot, x + w / 2, y + 17, label, "middle")
        f.text("dg-tick", x + w / 2, y + 32, sub, "middle")
        return x, y, w
    node(24, 104, "design", "2 / 3 / 6", "dg-hot")
    node(180, 24, "migration", "1 / 2 / 5")
    node(180, 104, "api", "3 / 5 / 10", "dg-hot")
    node(336, 104, "ui", "4 / 6 / 12", "dg-hot")
    node(336, 184, "payments", "2 / 4 / 15", "dg-doubt")
    node(492, 104, "load test", "1 / 2 / 4", "dg-hot")
    node(636, 104, "launch", "1 / 1 / 3", "dg-hot", w=100)
    f.line("dg-edge", 144, 118, 178, 50, "n")
    f.line("dg-msg-hot", 144, 124, 178, 124, "h")
    f.line("dg-msg-hot", 300, 124, 334, 124, "h")
    f.line("dg-edge", 300, 136, 334, 196, "n")
    f.line("dg-edge", 300, 44, 490, 112, "n")
    f.line("dg-msg-hot", 456, 124, 490, 124, "h")
    f.line("dg-edge", 456, 204, 490, 136, "n")
    f.line("dg-msg-hot", 612, 124, 634, 124, "h")
    f.text("dg-small", 476, 214, "on the critical path in 43% of runs")
    f.text("dg-tick", 24, 240, "best / most likely / worst, in days; highlighted: the plan's critical path")
    return f.svg()


def fig10():
    f = Fig("f10")
    X0, PX = 200, 12                                       # day 0, pixels per day
    days = {"data model": 5, "admin screens": 8, "reporting": 6, "email templates": 3,
            "bank API integration": 7, "fraud rules": 6, "migration of old data": 5, "load and failover test": 4}
    short = {"bank API integration": "bank API", "fraud rules": "fraud", "admin screens": "admin",
             "data model": "model", "reporting": "reports", "migration of old data": "migrate",
             "email templates": "mail", "load and failover test": "test"}
    risky = {"bank API integration", "fraud rules", "migration of old data"}
    plans = [("comfortable first", ["data model", "email templates", "admin screens", "reporting",
                                    "migration of old data", "fraud rules", "bank API integration",
                                    "load and failover test"], 0, 33),
             ("riskiest first", ["bank API integration", "fraud rules", "data model", "migration of old data",
                                 "reporting", "email templates", "admin screens", "load and failover test"], 0, 7),
             ("after a 2-day spike", ["bank API integration", "fraud rules", "data model", "migration of old data",
                                      "reporting", "email templates", "admin screens", "load and failover test"], 2, 2)]
    for i, (name, order, spike, first) in enumerate(plans):
        y = 30 + i * 62
        f.text("dg-small", X0 - 14, y + 17, name, "end")
        day = 0
        if spike:
            f.rect("dg-ok-box", X0, y, spike * PX, 24)
            day = spike
        for t in order:
            w = days[t] * PX
            f.rect("dg-hot" if t in risky else "dg-box", X0 + day * PX, y, w, 24)
            if t in short:
                f.text("dg-tick" + (" dg-hot-text" if t in risky else ""), X0 + day * PX + w / 2, y + 16,
                       short[t], "middle")
            day += days[t]
        f.line("dg-msg-hot", X0 + first * PX, y + 46, X0 + first * PX, y + 28, "h")
        late = first > 22                                  # label a late marker on its left, to stay in frame
        f.text("dg-tick", X0 + first * PX + (-8 if late else 8), y + 46, f"first surprise, median day {first}",
               "end" if late else None)
    f.line("dg-axis", X0, 222, X0 + 46 * PX, 222)
    for d in (0, 11, 22, 33, 44):
        f.text("dg-tick", X0 + d * PX, 240, f"day {d}", "middle")
    return f.svg()


def fig11():
    f = Fig("f11")
    f.rect("dg-box", 24, 40, 190, 88)
    f.text("dg-title", 36, 62, "PROJECT DATA")
    for i, s in enumerate(("open tasks, with ranges", "blockers", "decisions needed")):
        f.text("dg-small", 36, 84 + i * 16, s)
    f.rect("dg-iface", 24, 168, 190, 52)
    f.text("dg-label", 119, 190, "forecast", "middle")
    f.text("dg-small", 119, 208, "P50, P85 and the odds", "middle")
    f.line("dg-edge", 119, 128, 119, 166, "n")
    outs = [("LEADERSHIP: TWO LINES", "colour, confidence, the decision needed", 30),
            ("PARTNER TEAMS", "what we need from you, and what a delay costs", 106),
            ("THE TEAM", "done, open, the forecast and the next priority", 182)]
    for title, what, y in outs:
        f.rect("dg-hot", 330, y, 406, 54)
        f.text("dg-title", 344, y + 22, title)
        f.text("dg-small", 344, y + 42, what)
        f.line("dg-edge", 214, 194, 328, y + 27, "n")
    return f.svg()


def fig12():
    f = Fig("f12")
    # concept: (x, y, state)   state: known, fragile, ready, path, goal, other
    N = {"files and fsync": (24, 236, "ready"), "pages, buffer pool": (204, 236, "path"),
         "B-trees": (384, 236, "other"), "indexes": (544, 236, "fragile"),
         "statistics": (544, 156, "ready"), "query plans": (600, 76, "fragile"),
         "transactions": (24, 116, "known"), "write-ahead log": (204, 116, "path"),
         "crash recovery": (384, 116, "goal"), "replication": (204, 36, "fragile"),
         "MVCC": (384, 36, "other")}
    cls = {"known": "dg-ok-box", "fragile": "dg-doubt", "ready": "dg-hot", "path": "dg-hot", "goal": "dg-hot",
           "other": "dg-box"}
    W, H = 150, 30
    edges = [("files and fsync", "pages, buffer pool"), ("pages, buffer pool", "B-trees"), ("B-trees", "indexes"),
             ("files and fsync", "write-ahead log"), ("transactions", "write-ahead log"),
             ("write-ahead log", "crash recovery"), ("pages, buffer pool", "crash recovery"),
             ("write-ahead log", "replication"), ("transactions", "MVCC")]
    def c(n, dx=0.5, dy=0.5):
        x, y, _ = N[n]; return x + W * dx, y + H * dy
    for a, b in edges:
        (x1, y1), (x2, y2) = c(a), c(b)
        xa, ya = N[a][0], N[a][1]; xb, yb = N[b][0], N[b][1]
        if ya == yb:
            f.line("dg-edge", xa + W, y1, xb - 2, y2, "n")
        else:
            up = yb < ya
            f.line("dg-edge", x1, ya if up else ya + H, x2, (yb + H + 2) if up else yb - 2, "n")
    f.line("dg-edge", 612, 236, 650, 108, "n")              # indexes -> query plans
    f.line("dg-edge", 612, 156, 650, 108, "n")              # statistics -> query plans
    for n, (x, y, state) in N.items():
        f.rect(cls[state], x, y, W, H)
        f.text("dg-small" + (" dg-hot-text" if state in ("ready", "path", "goal") else ""), x + W / 2, y + 20, n,
               "middle")
    key = [("dg-ok-box", "known, solid"), ("dg-doubt", "known, fragile"), ("dg-hot", "ready now, or on the path")]
    for i, (k, label) in enumerate(key):
        f.rect(k, 24 + i * 200, 290 - 12, 12, 12)
        f.text("dg-tick", 42 + i * 200, 289, label)
    return f.svg()


def fig13():
    f = Fig("f13")
    rows = [("cache invoice PDFs", 36_480, "3 weeks of work, pays back in 5.7 weeks"),
            ("faster checkout", 27_200, "6 weeks of work, pays back in 7.6 weeks"),
            ("fix bulk-invoice failures", 10_200, "8 weeks of work, pays back in 20.4 weeks")]
    X0, W = 230, 300
    f.text("dg-title", 24, 22, "VALUE PER WEEK OF ENGINEERING EFFORT")
    for i, (name, v, note) in enumerate(rows):
        y = 44 + i * 58
        f.text("dg-small", X0 - 14, y + 18, name, "end")
        w = W * v / 40_000
        f.rect("dg-bar-hot" if i == 0 else "dg-bar", X0, y, w, 26)
        f.text("dg-tick", X0 + w + 8, y + 17, f"${v:,}")
        f.text("dg-tick", X0, y + 44, note)
    return f.svg()


def fig14():
    f = Fig("f14")
    f.rect("dg-bar", 24, 14, 14, 12)
    f.text("dg-small", 44, 24, "weekly releases")
    f.rect("dg-bar-hot", 190, 14, 14, 12)
    f.text("dg-small", 210, 24, "daily releases")
    panels = [("deploys a week", 1, 5, 6, "{:g}"), ("lead time", 51, 3, 60, "{:g} h"),
              ("failure rate", 67, 13, 100, "{:g}%"), ("time to restore", 4.8, 0.6, 6, "{:g} h")]
    for i, (name, a, b, top, fmt) in enumerate(panels):
        x = 24 + i * 184
        f.text("dg-title", x, 58, name.upper())
        base, H = 210, 120
        for j, (v, cls) in enumerate(((a, "dg-bar"), (b, "dg-bar-hot"))):
            h = max(2, H * v / top)
            bx = x + 20 + j * 64
            f.rect(cls, bx, base - h, 44, h)
            f.text("dg-tick", bx + 22, base - h - 8, fmt.format(v), "middle")
        f.line("dg-axis", x, base, x + 160, base)
    f.text("dg-tick", 24, 238, "lead time and deploys follow from the schedule; the failure figures come from an invented log")
    return f.svg()


def fig15():
    f = Fig("f15")
    X0, PX = 230, 60                                       # day 0, pixels per day
    f.text("dg-title", 24, 22, "FROM ASKING TO DONE, ON AVERAGE")
    rows = [("start everything", 0.0, 7.14, "5.4 in progress"), ("limit WIP to 4", 1.72, 4.51, "3.4 in progress")]
    for i, (name, wait, work, wip) in enumerate(rows):
        y = 50 + i * 64
        f.text("dg-small", X0 - 14, y + 18, name, "end")
        if wait:
            f.rect("dg-dead", X0, y, wait * PX, 26)
            f.text("dg-tick", X0 + wait * PX / 2, y + 17, "queue", "middle")
        f.rect("dg-bar-hot" if i else "dg-bar", X0 + wait * PX, y, work * PX, 26)
        f.text("dg-tick", X0 + (wait + work) * PX + 8, y + 17, f"{wait + work:.1f} days")
        f.text("dg-tick", X0 - 14, y + 36, wip, "end")
    f.line("dg-axis", X0, 180, X0 + 8 * PX, 180)
    for d in range(0, 9, 2):
        f.text("dg-tick", X0 + d * PX, 198, f"{d} d", "middle")
    f.text("dg-tick", 24, 214, "both finish 0.74 items a day; dashed: waiting in the queue, solid: being worked on")
    return f.svg()


def fig16():
    f = Fig("f16")
    rows = [("mentoring", 4, 0), ("design", 3, 2), ("reliability", 3, 2), ("writing", 2, 1), ("leadership", 1, 0)]
    X0, PX = 170, 70
    f.rect("dg-bar-hot", 170, 12, 14, 12)
    f.text("dg-small", 190, 22, "with a measured result")
    f.rect("dg-bar", 400, 12, 14, 12)
    f.text("dg-small", 420, 22, "without")
    for i, (name, n, measured) in enumerate(rows):
        y = 40 + i * 34
        f.text("dg-small", X0 - 14, y + 16, name, "end")
        if measured:
            f.rect("dg-bar-hot", X0, y, measured * PX, 22)
        if n - measured:
            f.rect("dg-bar", X0 + measured * PX, y, (n - measured) * PX, 22)
        f.text("dg-tick", X0 + n * PX + 8, y + 15, f"{n} entr{'ies' if n != 1 else 'y'}")
    f.text("dg-tick", 24, 220, "weeks with nothing written down: W05 and W10")
    return f.svg()
