# Estimate each SVG text label's box from the series' font sizes and flag labels that leave the
# viewBox, overlap or touch another label, don't fit inside the box they sit in (3px padding each
# side), straddle the edge of a box, or have a straight line running through them; and boxes or
# lines that leave the viewBox. Usage: svglint.py VOLUME.html
# As a module, check_svg(svg) returns the problems with the shapes involved, for figreview.py.
import sys, re, html
# (font size, width of one character in em, bold) for each text class
FONT = {"dg-title": (11, 0.6 + 0.12, True), "dg-label": (12.5, 0.6, False), "dg-small": (11.5, 0.6, False),
        "dg-msg-label": (11.5, 0.6, False), "dg-tick": (10.5, 0.6, False), "dg-step": (10.5, 0.6, True),
        "dg-note": (13, 0.5, False), "dg-gap-text": (11.5, 0.6, True), "dg-ok-text": (11.5, 0.6, True)}
BOLD_MOD = {"dg-hot-text", "hot", "dg-proof-text"}
BOXES = {"dg-box", "dg-hot", "dg-iface", "dg-body", "dg-head", "dg-ok-box", "dg-doubt", "dg-proof", "dg-span",
         "dg-span-hot", "dg-bar", "dg-bar-hot", "dg-dead", "dg-node"}
num = lambda a, k: float(re.search(r'\b' + k + r'="([-\d.]+)"', a).group(1))

def crosses(x1, y1, x2, y2, bx):
    """Does the segment cross the rectangle bx? (Liang-Barsky clipping.)"""
    t0, t1, dx, dy = 0.0, 1.0, x2 - x1, y2 - y1
    for p_, q_ in ((-dx, x1 - bx[0]), (dx, bx[2] - x1), (-dy, y1 - bx[1]), (dy, bx[3] - y1)):
        if p_ == 0:
            if q_ < 0: return False
        else:
            t = q_ / p_
            if p_ < 0: t0 = max(t0, t)
            else: t1 = min(t1, t)
            if t0 > t1: return False
    return True

def check_svg(svg):
    """Return (labels, problems); each problem is a dict with kind, msg, boxes and lines."""
    W, H = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    out = []
    def flag(kind, msg, boxes=(), lines=()): out.append(dict(kind=kind, msg=msg, boxes=list(boxes), lines=list(lines)))
    rects = []
    # filled shapes, with their position in drawing order, that can hide a line drawn before them
    covers = []
    for m in re.finditer(r'<(rect|circle)\b([^>]*)>', svg):
        a = m.group(2); cls = set((re.search(r'class="([^"]+)"', a) or re.search(r'()', a)).group(1).split())
        if cls & {"dg-dead", "dg-span", "dg-band", "dg-grid"} or 'fill="none"' in a: continue
        if m.group(1) == "rect":
            covers.append((m.start(), (num(a, "x"), num(a, "y"), num(a, "x") + num(a, "width"), num(a, "y") + num(a, "height"))))
        else:
            cx, cy, r = num(a, "cx"), num(a, "cy"), num(a, "r"); h = r * 0.7   # the square inside the circle
            covers.append((m.start(), (cx - h, cy - h, cx + h, cy + h)))
    for a in re.findall(r'<rect\b([^>]*)>', svg):
        cls = set(re.search(r'class="([^"]+)"', a).group(1).split())
        r = (num(a, "x"), num(a, "y"), num(a, "x") + num(a, "width"), num(a, "y") + num(a, "height"))
        if r[0] < 0 or r[1] < 0 or r[2] > W or r[3] > H:
            flag("leaves", f"a {'/'.join(sorted(cls))} box {tuple(round(v) for v in r)} leaves the {W:.0f}x{H:.0f} viewBox", [r])
        if cls & BOXES: rects.append(r)
    seglines = []
    for m in re.finditer(r'<line\b([^>]*)>', svg):
        a = m.group(1); l = tuple(num(a, k) for k in ("x1", "y1", "x2", "y2")) + (m.start(), 'dg-grid' in a)
        if min(l[0], l[2]) < 0 or max(l[0], l[2]) > W or min(l[1], l[3]) < 0 or max(l[1], l[3]) > H:
            flag("leaves", f"a line {l[:4]} leaves the {W:.0f}x{H:.0f} viewBox", lines=[l[:4]])
        seglines.append(l)
    boxes = []
    for attrs, body in re.findall(r'<text\b([^>]*)>(.*?)</text>', svg, re.S):
        classes = re.search(r'class="([^"]+)"', attrs).group(1).split()
        size, em, bold = FONT.get(classes[0], (12, 0.6, False))
        bold = bold or bool(BOLD_MOD & set(classes))
        x, y = num(attrs, "x"), num(attrs, "y")
        txt = html.unescape(re.sub(r'<[^>]+>', '', body))
        w = len(txt) * size * em * (1.1 if bold else 1)
        anchor = re.search(r'text-anchor="(\w+)"', attrs); a = anchor.group(1) if anchor else "start"
        x0 = x - w / 2 if a == "middle" else (x - w if a == "end" else x)
        box = (x0, y - size * 0.8, x0 + w, y + size * 0.2, txt)
        if box[0] < 0 or box[2] > W or box[1] < 0 or box[3] > H:
            flag("leaves", f"'{txt}' leaves the {W:.0f}x{H:.0f} viewBox: {tuple(round(v) for v in box[:4])}", [box[:4]])
        for o in boxes:                                # labels must also be at least 3px apart
            if box[0] < o[2] + 3 and o[0] < box[2] + 3 and box[1] < o[3] and o[1] < box[3]:
                flag("overlaps", f"'{txt}' overlaps or touches '{o[4]}'", [box[:4], o[:4]])
        inside = [r for r in rects if r[0] <= x <= r[2] and r[1] <= y <= r[3]]
        if inside:
            r = min(inside, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
            if box[0] < r[0] + 3 or box[2] > r[2] - 3 or box[1] < r[1] + 1 or box[3] > r[3] - 1:
                flag("fit", f"'{txt}' does not fit its box {tuple(round(v) for v in r)} with padding "
                            f"(label spans {box[0]:.0f}..{box[2]:.0f})", [box[:4], r])
        for r in rects:
            if r in inside: continue
            if box[0] < r[2] and r[0] < box[2] and box[1] < r[3] and r[1] < box[3]:
                flag("straddles", f"'{txt}' straddles the edge of box {tuple(round(v) for v in r)}", [box[:4], r])
        boxes.append(box)
    for l in seglines:                                 # straight lines must not run through a label,
        if l[5]: continue                              # (faint dashed gridlines behind labels are fine)
        for bx in boxes:                               # unless a filled shape drawn later hides the line there
            inner = (bx[0] + 1, bx[1] + 1, bx[2] - 1, bx[3] - 1)
            if not crosses(*l[:4], inner): continue
            if any(pos > l[4] and c[0] <= inner[0] and c[1] <= inner[1] and c[2] >= inner[2] and c[3] >= inner[3]
                   for pos, c in covers): continue
            flag("runs through", f"a line ({l[0]:g},{l[1]:g})-({l[2]:g},{l[3]:g}) runs through '{bx[4]}'",
                 [bx[:4]], [l[:4]])
    return len(boxes), out

def accepted(volume):
    """Flags judged by eye to be fine, from svglint-accept.txt: volume | svg number | message | reason."""
    path = __import__("pathlib").Path(__file__).with_name("svglint-accept.txt")
    rows = [l.split(" | ") for l in path.read_text().splitlines() if l.strip() and not l.startswith("#")] if path.exists() else []
    return {(r[1].strip(), r[2].strip()): r[3].strip() for r in rows if r[0].strip() == volume}

if __name__ == "__main__":
    doc = open(sys.argv[1], encoding="utf-8").read()
    ok = accepted(__import__("pathlib").Path(sys.argv[1]).name)
    bad = 0
    for n, svg in enumerate(re.findall(r'<svg\b.*?</svg>', doc, re.S), 1):
        labels, problems = check_svg(svg)
        for p in problems:
            why = ok.get((str(n), p["msg"]))
            if why: print(f"svg {n}: accepted: {p['msg']} ({why})"); continue
            print(f"svg {n}: {p['msg']}"); bad += 1
        W, H = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups()
        print(f"svg {n}: {labels} labels, viewBox {float(W):.0f}x{float(H):.0f}")
    print("SVG LABELS OK" if not bad else f"{bad} SVG LABEL PROBLEM(S)")
    sys.exit(1 if bad else 0)
