# Diagrams for the Whetstone. Each figNN() draws the inside of one <svg>; the chapter template
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
    f.text("dg-small", 736, 22, "f='my notes.txt';  in the folder: a.txt, b c.txt, notes.md", "end")
    rows = [("YOU TYPE", 62), ("PARAMETER EXPANSION", 120), ("WORD SPLITTING", 178), ("GLOBBING", 236),
            ("THE PROGRAM GETS", 294)]
    for label, y in rows: f.text("dg-title", 24, y, label)
    for (_, y1), (_, y2) in zip(rows, rows[1:]): f.line("dg-edge", 200, y1 + 10, 200, y2 - 22, "n")
    f.code(230, 62, [("showargs ", False), ("$f", True), (" *.txt", False)])
    f.code(230, 120, [("showargs ", False), ("my notes.txt", True), (" *.txt", False)])
    f.words(230, 160, ["showargs", "my", "notes.txt", "*.txt"], hot={"my", "notes.txt"})
    f.words(230, 218, ["showargs", "my", "notes.txt", "a.txt", "b c.txt"], hot={"a.txt", "b c.txt"})
    centres = f.words(230, 276, ["showargs", "my", "notes.txt", "a.txt", "b c.txt"])
    for i, c in enumerate(centres): f.text("dg-tick", c, 322, f"argv[{i}]", "middle")
    return f.svg()

def fig02():
    f = Fig("f02")
    columns = [(24, "talk > out.txt 2>&1", [("START", "terminal", "terminal", None),
                                             ("AFTER > out.txt", "out.txt", "terminal", 1),
                                             ("AFTER 2>&1", "out.txt", "out.txt", 2)],
                "dg-ok-text", "both lines land in out.txt"),
               (404, "talk 2>&1 > out.txt", [("START", "terminal", "terminal", None),
                                              ("AFTER 2>&1", "terminal", "terminal", 2),
                                              ("AFTER > out.txt", "out.txt", "terminal", 1)],
                "dg-gap-text", "stderr still reaches the terminal")]
    for x0, command, steps, result_cls, result in columns:
        f.text("dg-label", x0, 26, command)
        for k, (label, one, two, changed) in enumerate(steps):
            y = 48 + 80 * k
            f.text("dg-step", x0, y + 12, label)
            for row, (fd, name, target) in enumerate(((1, "1 stdout", one), (2, "2 stderr", two))):
                top = y + 20 + 26 * row
                f.text("dg-small", x0, top + 15, name)
                f.line("dg-edge", x0 + 82, top + 11, x0 + 126, top + 11, "n")
                hot = changed == fd
                f.rect("dg-hot" if hot else "dg-box", x0 + 130, top, 110, 22)
                f.text("dg-small" + (" dg-hot-text" if hot else ""), x0 + 185, top + 15, target, "middle")
        f.text(result_cls, x0, 296, result)
    f.line("dg-sep", 380, 14, 380, 300)
    return f.svg()

def fig03():
    f = Fig("f03")
    log = ["192.0.2.41 - - [...", "192.0.2.41 - - [...", "203.0.113.7 - - [...",
           "192.0.2.41 - - [...", "203.0.113.7 - - [...", "..."]
    counts = ["4 203.0.113.90", "19 203.0.113.7", "2 198.51.100.5", "8 192.0.2.41", "13 198.51.100.23",
              "2 192.0.2.200"]
    ranked = ["19 203.0.113.7", "13 198.51.100.23", "8 192.0.2.41", "4 203.0.113.90", "2 192.0.2.200",
              "2 198.51.100.5"]
    stages = [("THE LOG", "access.log", log, "48 lines", 0),
              ("COUNT BY ADDRESS", "awk '{n[$1]++} END ...'", counts, "6 lines, in any order", 0),
              ("SORT", "sort -k1,1nr -k2,2", ranked, "by count, then address", 0),
              ("KEEP THREE", "head -n 3", ranked[:3], "the answer", 3)]
    w, gap, x = 166, 24, 12
    for k, (title, command, lines, note, hot) in enumerate(stages):
        f.text("dg-title", x, 30, title)
        f.text("dg-small dg-hot-text" if hot else "dg-small", x, 50, command)
        f.rect("dg-hot" if hot else "dg-box", x, 62, w, 140)
        for i, line in enumerate(lines): f.text("dg-small", x + 10, 84 + 21 * i, line)
        f.text("dg-tick", x, 224, note)
        if k < len(stages) - 1: f.line("dg-edge", x + w + 3, 132, x + w + gap - 3, 132, "n")
        x += w + gap
    f.text("dg-note", 12, 256, "Each stage reads the previous one's output as it's produced; the four run at the same time.")
    return f.svg()

def fig04():
    f = Fig("f04")
    x1, w1, x2, w2, h = 40, 330, 440, 290, 30
    rows = [("check the arguments", "wrong: usage line, exit 2", "gap"),
            ("check the folder exists", "missing: error message, exit 1", "gap"),
            ("take the lock: mkdir .tidy.lock", "already there: exit 1", "gap"),
            ("trap 'rmdir lock' EXIT", None, None),
            ("each file: category, then a free name", "-n: print the plan; else mv -n", "box"),
            ("exit 0, and the trap removes the lock", "the trap also runs after an error or Ctrl-C", "note")]
    for k, (step, side, kind) in enumerate(rows):
        y = 20 + 50 * k
        hot = side is None
        f.rect("dg-hot" if hot else "dg-box", x1, y, w1, h)
        f.text("dg-label" + (" dg-hot-text" if hot else ""), x1 + 14, y + 19.5, step)
        f.text("dg-step", 14, y + 19.5, str(k + 1))
        if k < len(rows) - 1: f.line("dg-edge", x1 + 40, y + h, x1 + 40, y + 48, "n")
        if kind == "gap":
            f.line("dg-msg-bad", x1 + w1, y + h / 2, x2 - 2, y + h / 2, "n")
            f.rect("dg-doubt", x2, y, w2, h); f.text("dg-gap-text", x2 + 12, y + 19.5, side)
        elif kind == "box":
            f.line("dg-edge", x1 + w1, y + h / 2, x2 - 2, y + h / 2, "n")
            f.rect("dg-box", x2, y, w2, h); f.text("dg-small", x2 + 12, y + 19.5, side)
        elif kind == "note":
            f.text("dg-note", x2, y + 19.5, side)
    f.path("dg-msg-async", f"M {x1 + w1 - 30} {20 + 50 * 5} C {x1 + w1 + 30} {20 + 50 * 5 - 40} "
                           f"{x1 + w1 + 30} {20 + 50 * 3 + 40} {x1 + w1 + 2} {20 + 50 * 3 + 20}", "h")
    return f.svg()

def fig05():
    f = Fig("f05")
    for x0, title, first, broken in ((20, "BEFORE", "notes.txt", False),
                                     (400, "AFTER mv notes.txt renamed.txt", "renamed.txt", True)):
        f.text("dg-title", x0, 22, title)
        f.text("dg-tick", x0, 44, "the folder's table")
        names = [first, "hard.txt", "soft.txt"]
        for i, name in enumerate(names):
            hot = broken and i == 0
            f.rect("dg-hot" if hot else "dg-box", x0, 54 + 30 * i, 120, 30)
            f.text("dg-small" + (" dg-hot-text" if hot else ""), x0 + 10, 73 + 30 * i, name)
        # inode A, named by the first two entries
        f.rect("dg-box", x0 + 186, 50, 164, 86)
        for j, s in enumerate(("inode A", "link count: 2", "owner, permissions", "data: version 2")):
            f.text("dg-label" if j == 0 else "dg-small", x0 + 198, 70 + 20 * j, s)
        f.line("dg-edge", x0 + 120, 69, x0 + 184, 80, "n"); f.line("dg-edge", x0 + 120, 99, x0 + 184, 96, "n")
        # inode B, the symbolic link
        f.rect("dg-doubt" if broken else "dg-box", x0 + 186, 166, 164, 66)
        for j, s in enumerate(("inode B", "a symbolic link", 'data: "notes.txt"')):
            f.text("dg-label" if j == 0 else "dg-small", x0 + 198, 186 + 20 * j, s)
        f.line("dg-edge", x0 + 120, 129, x0 + 184, 190, "n")
        if broken: f.text("dg-gap-text", x0 + 120, 256, "that name is gone: broken")
        else: f.text("dg-note", x0 + 120, 256, "looked up by name on every use")
    f.line("dg-sep", 380, 10, 380, 280)
    return f.svg()

def fig06():
    f = Fig("f06")
    x0, w, gap = 120, 36, 4
    for i, ch in enumerate("-rwxr-x---"):
        x = x0 + i * (w + gap)
        f.rect("dg-box" if i else "dg-span", x, 18, w, 36)
        f.text("dg-label", x + w / 2, 41, ch, "middle")
    groups = [("type", 0, 0, "a file"), ("owner", 1, 3, "4+2+1 = 7"), ("group", 4, 6, "4+0+1 = 5"),
              ("others", 7, 9, "0+0+0 = 0")]
    for name, a, b, value in groups:
        left, right = x0 + a * (w + gap), x0 + b * (w + gap) + w
        f.line("dg-edge", left, 64, right, 64)
        f.text("dg-title", (left + right) / 2, 84, name.upper(), "middle")
        f.text("dg-small", (left + right) / 2, 104, value, "middle")
    f.text("dg-label dg-hot-text", x0 + 10 * (w + gap) + 24, 41, "= 750")
    f.text("dg-title", 40, 150, "BIT"); f.text("dg-title", 100, 150, "ON A FILE"); f.text("dg-title", 400, 150, "ON A FOLDER")
    rows = [("r", "read its contents", "list the names in it"),
            ("w", "change its contents", "create, delete and rename entries in it"),
            ("x", "run it as a program", "go into it, and reach files inside by name")]
    for k, (bit, on_file, on_folder) in enumerate(rows):
        y = 186 + 34 * k
        f.line("dg-sep", 40, y - 22, 720, y - 22)
        f.text("dg-label", 40, y, bit); f.text("dg-small", 100, y, on_file)
        f.text("dg-small dg-hot-text" if bit == "w" else "dg-small", 400, y, on_folder)
    f.text("dg-note", 40, 290, "Deleting a file changes its folder's list of names, so the folder's w decides who may.")
    return f.svg()

def fig07():
    f = Fig("f07")
    f.text("dg-title", 30, 22, "COPIES FLOW DOWN")
    f.rect("dg-box", 30, 34, 230, 70)
    for j, s in enumerate(("your shell", "x=1, exported", "PATH=bin2:bin1:...")):
        f.text("dg-label" if j == 0 else "dg-small", 42, 54 + 20 * j, s)
    f.line("dg-edge", 100, 104, 100, 158, "n"); f.text("dg-msg-label", 110, 136, "a copy, at start")
    f.rect("dg-hot", 30, 160, 230, 70)
    for j, s in enumerate(("bash setup.sh", "its own x=1, PATH=...", "cd sub; export GREETING")):
        f.text("dg-label dg-hot-text" if j == 0 else "dg-small", 42, 180 + 20 * j, s)
    f.line("dg-msg-bad", 290, 158, 290, 108, "n")
    f.line("dg-cross", 280, 124, 300, 142); f.line("dg-cross", 300, 124, 280, 142)
    f.text("dg-gap-text", 310, 138, "never back up")
    f.text("dg-small", 30, 256, "when it exits, its cd and export are gone")
    f.text("dg-note", 30, 284, "source setup.sh runs the same lines in your shell itself")
    f.line("dg-sep", 440, 12, 440, 290)
    f.text("dg-title", 466, 22, "LOOKING UP greet")
    for k, (folder, result, cls) in enumerate((("$DEMO/bin2", "has greet: runs it", "dg-hot"),
                                                ("$DEMO/bin1", "has greet: never reached", "dg-box"),
                                                ("/usr/bin, ...", "not searched", "dg-dead"))):
        y = 40 + 62 * k
        f.text("dg-step", 466, y + 26, f"{k + 1}")
        f.rect(cls, 486, y, 250, 42)
        f.text("dg-label" + (" dg-hot-text" if k == 0 else ""), 498, y + 18, folder)
        f.text("dg-small", 498, y + 35, result)
        if k < 2: f.line("dg-edge", 600, y + 42, 600, y + 60, "n")
    f.text("dg-small", 466, 256, "PATH=$DEMO/bin2:$DEMO/bin1:/usr/bin")
    f.text("dg-note", 466, 284, "the first match wins")
    return f.svg()

def fig08():
    f = Fig("f08")
    f.text("dg-title", 30, 26, "~/dotfiles: PUBLIC")
    f.text("dg-title", 446, 26, "~: YOUR HOME FOLDER")
    repo = [("install.sh", 52), ("zshrc", 90), ("gitconfig", 128), ("gitignore_global", 166), (".gitignore: *.local", 204)]
    for name, y in repo:
        f.rect("dg-box", 30, y, 250, 30); f.text("dg-small", 42, y + 19.5, name)
    home = [(".zshrc", 90, "link"), (".gitconfig", 128, "link"), (".config/git/ignore", 166, "link"),
            (".gitconfig.local", 214, "private"), (".dotfiles-backup/", 252, "backup")]
    for name, y, kind in home:
        f.rect("dg-hot" if kind == "link" else "dg-box", 446, y, 290, 30)
        f.text("dg-small" + (" dg-hot-text" if kind == "link" else ""), 458, y + 19.5, name)
        if kind == "link": f.line("dg-msg-hot", 444, y + 15, 284, y + 15, "h")
    f.text("dg-tick", 724, 233.5, "this machine's email", "end")
    f.text("dg-tick", 724, 271.5, "the old .zshrc, kept", "end")
    f.text("dg-msg-label hot", 364, 82, "symbolic links", "middle")
    f.path("dg-msg-async", "M 280 150 C 340 160 360 222 442 229", "n")
    f.text("dg-msg-label", 300, 214, "[include]")
    f.text("dg-note", 30, 288, "Edit through a link and you edit the tracked file.")
    return f.svg()

def fig09():
    f = Fig("f09")
    def obj(x, y, w, kind, oid, note, cls="dg-box"):
        f.rect(cls, x, y, w, 44)
        f.code(x + 10, y + 18, [(kind + " ", False), (oid, cls == "dg-hot")])
        f.text("dg-small", x + 10, y + 36, note)
    obj(60, 20, 230, "commit", "883e680", "Start the shop")
    obj(470, 20, 230, "commit", "7018825", "Add opening hours")
    f.line("dg-msg", 468, 42, 292, 42, "n"); f.text("dg-msg-label", 380, 34, "parent", "middle")
    obj(60, 108, 230, "tree", "c93e4e9", "README.md, src/")
    obj(470, 108, 230, "tree", "080446f", "README.md, src/")
    f.line("dg-edge", 175, 64, 175, 106, "n"); f.line("dg-edge", 585, 64, 585, 106, "n")
    obj(20, 200, 190, "blob", "a00621b", '"# Shop"')
    obj(550, 200, 190, "blob", "9921cee", '"# Shop", hours')
    obj(285, 196, 190, "tree", "5234dad", "src/: app.py", "dg-hot")
    f.line("dg-edge", 130, 152, 115, 198, "n"); f.line("dg-edge", 220, 152, 300, 194, "n")
    f.line("dg-edge", 540, 152, 460, 194, "n"); f.line("dg-edge", 630, 152, 645, 198, "n")
    f.text("dg-msg-label hot", 380, 186, "shared", "middle")
    obj(285, 252, 190, "blob", "9cf595f", "print('shop')")
    f.line("dg-edge", 380, 240, 380, 250, "n")
    return f.svg()

def fig10():
    f = Fig("f10")
    def commit(x, y, name):
        f.circle("dg-node", x, y, 14); f.text("dg-label", x, y + 4.5, name, "middle")
    def parent(x1, y1, x2, y2):                      # an arrow from a commit back to its parent
        import math
        d = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / d, (y2 - y1) / d
        f.line("dg-edge", x1 + 15 * ux, y1 + 15 * uy, x2 - 17 * ux, y2 - 17 * uy, "n")
    def ref(x, y, name, cls="dg-box", text_cls="dg-small"):
        w = len(name) * 11.5 * MONO + 16
        f.rect(cls, x - w / 2, y, w, 22); f.text(text_cls, x, y + 15, name, "middle")
    panels = [(10, "1. TWO COMMITS ON main"), (264, "2. COMMIT C ON feature"), (518, "3. DETACHED, COMMIT D")]
    for x0, title in panels: f.text("dg-title", x0 + 6, 22, title)
    for x0 in (254, 508): f.line("dg-sep", x0, 10, x0, 280)
    # panel 1
    commit(50, 170, "A"); commit(130, 170, "B"); parent(130, 170, 50, 170)
    ref(130, 104, "main"); f.line("dg-edge", 130, 126, 130, 154, "n")
    ref(130, 44, "HEAD", "dg-hot", "dg-small dg-hot-text"); f.line("dg-msg-hot", 130, 66, 130, 102, "h")
    ref(130, 220, "feature"); f.line("dg-edge", 130, 220, 130, 186, "n")
    # panel 2
    commit(300, 170, "A"); commit(370, 170, "B"); commit(440, 170, "C"); parent(370, 170, 300, 170); parent(440, 170, 370, 170)
    ref(370, 104, "main"); f.line("dg-edge", 370, 126, 370, 154, "n")
    ref(440, 104, "feature"); f.line("dg-edge", 440, 126, 440, 154, "n")
    ref(440, 44, "HEAD", "dg-hot", "dg-small dg-hot-text"); f.line("dg-msg-hot", 440, 66, 440, 102, "h")
    # panel 3
    commit(548, 150, "A"); commit(612, 150, "B"); commit(676, 150, "C"); parent(612, 150, 548, 150); parent(676, 150, 612, 150)
    ref(612, 84, "main"); f.line("dg-edge", 612, 106, 612, 134, "n")
    ref(676, 84, "feature"); f.line("dg-edge", 676, 106, 676, 134, "n")
    commit(660, 222, "D"); parent(660, 222, 612, 150)
    ref(590, 236, "HEAD", "dg-hot", "dg-small dg-hot-text"); f.line("dg-msg-hot", 612, 245, 644, 228, "h")
    f.text("dg-tick", 690, 226, "no branch")
    f.text("dg-note", 524, 284, "git branch experiment D names it")
    return f.svg()

def _node(f, x, y, label, note=None, note_dy=32, cls="dg-node", text_cls="dg-small"):
    f.circle(cls, x, y, 13)
    f.text("dg-label", x, y + 4.5, label, "middle")
    if note: f.text(text_cls, x, y + note_dy, note, "middle")

def _parent(f, x1, y1, x2, y2, cls="dg-edge", r=13):
    import math
    d = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / d, (y2 - y1) / d
    f.line(cls, x1 + (r + 1) * ux, y1 + (r + 1) * uy, x2 - (r + 3) * ux, y2 - (r + 3) * uy, "n")

def fig11():
    f = Fig("f11")
    f.text("dg-title", 20, 22, "MERGE: A COMMIT WITH TWO PARENTS")
    _node(f, 50, 150, "B", "base", 34)
    _node(f, 160, 80, "M", "lemon cake", -22); _parent(f, 160, 80, 50, 150)
    _node(f, 160, 220, "L", "sourdough", 34); _parent(f, 160, 220, 50, 150)
    f.circle("dg-node", 280, 150, 13); f.text("dg-label", 280, 154.5, "m", "middle")
    _parent(f, 280, 150, 160, 80); _parent(f, 280, 150, 160, 220)
    f.text("dg-small dg-hot-text", 280, 128, "the merge", "middle")
    f.text("dg-tick", 236, 100, "parent 1", "middle"); f.text("dg-tick", 236, 214, "parent 2", "middle")
    f.text("dg-small", 20, 286, "line 2 from lunch, line 5 from main")
    f.line("dg-sep", 380, 10, 380, 290)
    f.text("dg-title", 400, 22, "REBASE: THE SAME CHANGES, NEW COMMITS")
    for x, label in ((420, "A"), (490, "M"), (560, "T")): _node(f, x, 100, label)
    _parent(f, 490, 100, 420, 100); _parent(f, 560, 100, 490, 100)
    f.text("dg-small", 560, 66, "main", "middle")
    f.circle("dg-span-hot", 630, 100, 13); f.text("dg-label dg-hot-text", 630, 104.5, "L'", "middle")
    f.circle("dg-span-hot", 700, 100, 13); f.text("dg-label dg-hot-text", 700, 104.5, "C'", "middle")
    _parent(f, 630, 100, 560, 100); _parent(f, 700, 100, 630, 100)
    f.text("dg-small dg-hot-text", 700, 66, "drinks", "middle")
    f.circle("dg-dead", 490, 210, 13); f.text("dg-label", 490, 214.5, "L", "middle")
    f.circle("dg-dead", 560, 210, 13); f.text("dg-label", 560, 214.5, "C", "middle")
    _parent(f, 490, 210, 420, 100, "dg-msg-async"); _parent(f, 560, 210, 490, 210, "dg-msg-async")
    f.path("dg-msg-async", "M 576 204 C 610 190 625 150 629 118", "h")
    f.text("dg-msg-label hot", 646, 176, "replayed")
    f.text("dg-tick", 420, 252, "the old commits: no name points at them now")
    f.text("dg-small", 400, 286, "new ids, the same lines added and removed")
    return f.svg()

def fig12():
    f = Fig("f12")
    X = lambda n: 282 + (n - 1) * 11.5               # commit n's position, 1 to 40
    for n in range(1, 41): f.circle("dg-dot", X(n), 34, 4)
    f.circle("dg-dot-hot", X(1), 34, 5); f.circle("dg-dot-hot", X(40), 34, 5)
    for n in (1, 10, 20, 30, 40): f.text("dg-tick", X(n), 58, str(n), "middle")
    f.text("dg-small", 24, 38, "40 commits")
    f.text("dg-ok-text", X(1) - 10, 20, "good", "start"); f.text("dg-gap-text", X(40), 20, "bad", "middle")
    steps = [(2, 40, 20, "good"), (21, 40, 30, "bad"), (21, 30, 25, "good"), (26, 30, 27, "bad"), (26, 27, 26, "good")]
    for k, (lo, hi, test, verdict) in enumerate(steps):
        y = 92 + 38 * k
        f.text("dg-ok-text" if verdict == "good" else "dg-gap-text", 24, y + 4,
               f"{k + 1}. {hi - lo + 1} suspects; {test} is {verdict}")
        f.rect("dg-span", X(lo) - 6, y - 8, X(hi) - X(lo) + 12, 16)
        for n in range(lo, hi + 1): f.circle("dg-dot", X(n), y, 3)
        f.circle("dg-dot-hot", X(test), y, 6)
    f.text("dg-label dg-hot-text", 24, 290, "the first bad commit: 27")
    f.circle("dg-dot-hot", X(27), 286, 6)
    return f.svg()

def fig13():
    f = Fig("f13")
    f.text("dg-title", 40, 22, "ON GITHUB")
    f.text("dg-title", 40, 186, "ON LAPTOPS")
    boxes = [(40, 34, "upstream.git", "the project; Grace can push"), (480, 34, "fork.git", "Ada's copy; Ada can push"),
             (40, 198, "grace", "a clone of upstream"), (480, 198, "ada", "remotes: origin, upstream")]
    for x, y, name, note in boxes:
        f.rect("dg-box", x, y, 240, 54)
        f.text("dg-label", x + 12, y + 22, name); f.text("dg-small", x + 12, y + 42, note)
    f.line("dg-msg-hot", 478, 50, 282, 50, "h"); f.text("dg-msg-label hot", 380, 42, "3 pull request", "middle")
    f.line("dg-msg-async", 282, 76, 478, 76, "n"); f.text("dg-msg-label", 380, 70, "Fork button", "middle")
    f.line("dg-msg", 580, 196, 580, 90, "n"); f.text("dg-msg-label", 572, 150, "2 push", "end")
    f.line("dg-msg", 640, 90, 640, 196, "n"); f.text("dg-msg-label", 648, 150, "1 clone")
    f.line("dg-msg", 150, 196, 150, 90, "n"); f.text("dg-msg-label", 142, 150, "5 push the merge", "end")
    f.line("dg-msg", 220, 90, 220, 196, "n"); f.text("dg-msg-label", 228, 150, "clone")
    f.line("dg-msg", 282, 90, 478, 202, "n"); f.text("dg-msg-label", 472, 228, "4, 6 Ada fetches upstream", "end")
    f.line("dg-msg", 478, 90, 282, 202, "n"); f.text("dg-msg-label", 288, 246, "5 Grace fetches the branch")
    f.text("dg-note", 40, 286, "Ada pushes only to her fork; the pull request asks Grace to merge into the project.")
    return f.svg()

def fig14():
    f = Fig("f14")
    f.code(40, 30, [("query: ", False), ("mdl", True)])
    rows = [("src/shop/models/data_loader.py", {9: "8.1", 16: "9.8", 21: "10.2"}, "28.1", 80),
            ("tests/test_models.py", {11: "9.9", 13: "2.8", 15: "2.8"}, "15.5", 160)]
    cw = 16
    for path, hits, total, y in rows:
        for i, ch in enumerate(path):
            x = 40 + i * cw
            if i in hits:
                f.rect("dg-hot", x - 8, y - 15, 16, 21)
                f.text("dg-label dg-hot-text", x, y, ch, "middle")
                f.text("dg-tick", x, y + 24, hits[i], "middle")
            else:
                f.text("dg-label", x, y, ch, "middle")
        f.text("dg-tick", 700, y - 18, "score", "end")
        f.text("dg-label dg-hot-text" if total == "28.1" else "dg-label", 700, y, total, "end")
    f.text("dg-small", 40, 226, "each letter scores 1, plus 8 at the start of a word, plus 2 in the file name;")
    f.text("dg-small", 40, 248, "plus 8 right after the previous match, minus 0.2 for each letter skipped")
    return f.svg()

def fig15():
    f = Fig("f15")
    f.rect("dg-box", 20, 12, 520, 214)
    lines = [(34, "Traceback (most recent call last):", "dg-small"),
             (62, '  File "errors.py", line 35, in <module>', "dg-small"),
             (80, '    average_prices("\\n".join(menu))', "dg-small"),
             (108, '  File "errors.py", line 11, in average_prices', "dg-small"),
             (126, "    result[category] = average(prices)", "dg-small"),
             (154, '  File "errors.py", line 20, in average', "dg-small dg-hot-text"),
             (172, "    ... round(sum(numbers) / len(numbers), 2)", "dg-small dg-hot-text"),
             (206, "ZeroDivisionError: division by zero", "dg-gap-text")]
    for y, s, cls in lines: f.text(cls, 34, y, s.replace(" ", " "))
    f.line("dg-msg-hot", 590, 202, 548, 202, "h"); f.text("dg-msg-label hot", 596, 206, "1. what went wrong")
    f.line("dg-msg-hot", 590, 162, 548, 162, "h"); f.text("dg-msg-label hot", 596, 166, "2. where it happened")
    f.line("dg-msg", 590, 94, 548, 94, "n"); f.text("dg-msg-label", 596, 98, "3. how it got there")
    f.path("dg-msg-async", "M 750 196 L 750 60", "n")
    f.text("dg-tick", 750, 230, "read upwards", "end")
    return f.svg()

def fig16():
    """Average chance of recall over the example's 200 facts, from its own model and random seed."""
    import pathlib, random
    src = (pathlib.Path(__file__).parent / "v" / "ch16_learning.py").read_text().split('print("200 facts')[0]
    model = {}; exec(src, model)
    Fact, chance = model["Fact"], model["chance"]
    rng = random.Random(16); facts = [Fact() for _ in range(200)]; history = []
    for fact in facts:                                # the "fixed" plan, in the same order as the example
        states = [(0.0, fact.S)]
        for day in (1, 3, 7, 14, 28): fact.review(day, rng); states.append((fact.seen, fact.S))
        history.append(states)
    def recall(t, reviewed=True):
        total = 0.0
        for states in history:
            seen, S = max((s for s in states if s[0] <= t), key=lambda s: s[0]) if reviewed else (0.0, 1.0)
            total += chance(t - seen, S)
        return total / len(history)
    f = Fig("f16")
    X = lambda d: 70 + d * 7.3; Y = lambda p: 250 - p * 210
    for p in (0, 0.25, 0.5, 0.75, 1):
        f.line("dg-grid" if p else "dg-axis", X(0), Y(p), X(90), Y(p))
        f.text("dg-tick", 60, Y(p) + 4, f"{p:.0%}", "end")
    for d in (0, 30, 60, 90): f.text("dg-tick", X(d), 270, f"day {d}", "middle")
    for d in (1, 3, 7, 14, 28): f.line("dg-faint dg-edge", X(d), Y(0), X(d), Y(1))
    f.text("dg-tick", X(14), 26, "reviews on days 1, 3, 7, 14 and 28", "middle")
    days = [i / 4 for i in range(0, 361)]
    for reviewed, cls in ((False, "dg-curve"), (True, "dg-curve-hot")):
        pts = []
        for d in days:
            if reviewed and d in (1, 3, 7, 14, 28): pts.append((d, recall(d - 1e-9)))   # just before the review
            pts.append((d, recall(d, reviewed)))
        f.path(cls, "M " + " L ".join(f"{X(d):.1f} {Y(p):.1f}" for d, p in pts))
    f.text("dg-small dg-hot-text", X(90), Y(recall(90)) + 22, f"five reviews: {recall(90):.0%} at day 90", "end")
    f.text("dg-small", X(90), Y(recall(90, False)) - 10, f"no review: {recall(90, False):.0%}", "end")
    return f.svg()
