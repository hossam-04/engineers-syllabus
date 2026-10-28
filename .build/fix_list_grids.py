# Fix list items that mix text with inline markup (<b>, <code>, <a>) breaking apart.
#
# Topic lists, chapter checklists and numbered rules drew their marker as the first cell of a
# two-column grid. A grid makes every child element, and every run of loose text, a cell of its
# own, so "Network diagnosis: <b>dig</b>, <b>traceroute</b>" was split across both columns.
# The marker is now positioned absolutely in the item's left padding, which is as wide as the
# old column plus gap, so plain items render exactly as before and mixed ones flow as one text.
#
# Usage: python3 fix_list_grids.py WORKSPACE   (applies to the sources and the built site)
import pathlib, sys

WS = pathlib.Path(sys.argv[1])
SITE = WS / "syllabus-site"

VOLUME = [
    (".checklist li { display: grid; grid-template-columns: 18px minmax(0, 1fr); gap: 10px; padding: 5px 0; font-size: 15.5px; line-height: 1.45; }",
     ".checklist li { position: relative; padding: 5px 0 5px 28px; font-size: 15.5px; line-height: 1.45; }"),
    (".checklist li::before { content: \"\"; width: 11px; height: 11px;",
     ".checklist li::before { content: \"\"; position: absolute; left: 0; top: 5px; width: 11px; height: 11px;"),
    ("ol.rules19 li { counter-increment: r; display: grid; grid-template-columns: 30px minmax(0, 1fr); gap: 10px; padding: 11px 0;",
     "ol.rules19 li { counter-increment: r; position: relative; padding: 11px 0 11px 40px;"),
    ("ol.rules19 li::before { content: counter(r, decimal-leading-zero);",
     "ol.rules19 li::before { content: counter(r, decimal-leading-zero); position: absolute; left: 0; top: 11px;"),
]
HUB_ITEM = ("  display: grid; grid-template-columns: 16px minmax(0, 1fr); gap: 10px;\n"
            "  padding: 4px 0; font-size: 15.5px; line-height: 1.45; align-items: start;\n}",
            "  position: relative;\n"
            "  padding: 4px 0 4px 26px; font-size: 15.5px; line-height: 1.45;\n}")
HUB_MARK = ("  content: \"\";\n  width: 7px; height: 7px; margin-top: 9px; margin-left: 4px;",
            "  content: \"\";\n  position: absolute; left: 0; top: 4px;\n  width: 7px; height: 7px; margin-top: 9px; margin-left: 4px;")
def hub(prefix):
    return [(prefix + "ul.topics li" + sel + "\n" + a, prefix + "ul.topics li" + sel + "\n" + b)
            for sel, (a, b) in (("{" if prefix else " {", HUB_ITEM), ("::before{" if prefix else "::before {", HUB_MARK))]

# Two reading-list entries put two link blocks side by side joined by a loose "and": one block now.
JOINED = ("</div> and <div>", " and ")

volumes = sorted(p.name for p in WS.glob("*-handbook.html"))
pages = sorted(p.name for p in SITE.glob("*.html") if p.name not in ("index.html", "all.html"))
plan = {WS / v: VOLUME for v in volumes}
plan.update({SITE / p: VOLUME for p in pages})
plan[WS / "software-engineering-study-plan.html"] = hub("")
plan[SITE / "index.html"] = hub("")
plan[SITE / "all.html"] = VOLUME + hub(".sa ")
for f in ("security-engineering-handbook.html", "ai-engineering-handbook.html"):
    plan[WS / f] = plan[WS / f] + [JOINED]
for f in ("citadel.html", "foundry.html", "all.html"):
    plan[SITE / f] = plan[SITE / f] + [JOINED]
expect_joined = {"all.html": 2}

for path, subs in sorted(plan.items()):
    s = path.read_text(encoding="utf-8")
    for old, new in subs:
        n = s.count(old)
        want = expect_joined.get(path.name, 1) if old == JOINED[0] else 1
        assert n == want, f"{path.name}: expected {want} of {old[:50]!r}, found {n}"
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8")
    print(f"{path.relative_to(WS)}: {len(subs)} change(s)")
