"""PDF editions, in two passes: lay each book out once to find the page every contents entry
starts on, then again with those numbers on its contents page, and check they still hold.

    python3 make_pdfs.py WS OUTDIR [slug ...]"""
import json, subprocess, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bookmeta import books

WS = pathlib.Path(sys.argv[1]).resolve(); OUT = pathlib.Path(sys.argv[2]).resolve(); ONLY = sys.argv[3:]
WORK = OUT.parent / ".print"; OUT.mkdir(parents=True, exist_ok=True)
RENDER = str(HERE / "render")


def run(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "CFURL" not in l)
    if r.returncode: raise SystemExit(out)
    return out


for b in books(WS):
    if ONLY and b["slug"] not in ONLY: continue
    slug, html, toc, pages = b["slug"], WORK / f'{b["slug"]}.html', WORK / f'{b["slug"]}.toc.json', WORK / f'{b["slug"]}.pages.json'
    raw = WORK / f"{slug}.raw.pdf"
    pages.unlink(missing_ok=True)
    for attempt in range(3):
        run(sys.executable, str(HERE / "make_print.py"), str(WS), str(WORK), slug)
        before = json.loads(pages.read_text()) if pages.exists() else None
        run(RENDER, "pdf", str(html), str(raw))
        title = json.loads(toc.read_text())["title"]
        final = OUT / (title.replace("The Engineer's ", "") + ".pdf")
        report = run(RENDER, "finish", str(raw), str(final), str(toc), str(pages))
        after = json.loads(pages.read_text())
        if before == after: break
    missing = [e["label"] for e, n in zip(json.loads(toc.read_text())["entries"], after) if n < 0]
    status = "ok" if before == after and not missing else "CHECK"
    print(f"{status:5} {final.name:16} {report}" + (f"  not found: {missing}" if missing else ""))
