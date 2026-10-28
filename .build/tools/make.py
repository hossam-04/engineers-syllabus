# Build a volume from its folder: assemble every template, build preview/volume.html (the page that
# gets published) and preview/index.html (the same with a document skeleton, for local viewing),
# then lint the diagrams. Usage: make.py VOL_DIR [--verify] [--partial]
# --partial reports problems but carries on, for previews while chapters are still missing.
import sys, subprocess, pathlib, shutil
VOL = pathlib.Path(sys.argv[1]).resolve(); T = pathlib.Path(__file__).parent
PARTIAL = "--partial" in sys.argv
def step(*args):
    r = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    print(r.stdout.rstrip())
    if r.returncode:
        print(r.stderr.rstrip())
        if not PARTIAL: sys.exit(f"step failed: {pathlib.Path(args[0]).name}")
tpls = sorted(p.name for p in VOL.glob("[0-9][0-9]_*.tpl"))
step(T / "assemble.py", VOL, *tpls)
(VOL / "90_back.html").write_text((VOL / "90_back.part").read_text(encoding="utf-8") + "\n"
                                  + (VOL / "tail.part").read_text(encoding="utf-8"), encoding="utf-8")
src = VOL / "src"; shutil.rmtree(src, ignore_errors=True); src.mkdir()
for p in VOL.glob("[0-9][0-9]_*.html"): shutil.copy(p, src / p.name)
(VOL / "preview").mkdir(exist_ok=True)
step(T / "build.py", src, VOL / "preview" / "volume.html")
page = (VOL / "preview" / "volume.html").read_text(encoding="utf-8")
(VOL / "preview" / "index.html").write_text(
    '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
    'content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>\n' + page + '\n</body></html>\n',
    encoding="utf-8")
step(T / "svglint.py", VOL / "preview" / "volume.html")
if "--verify" in sys.argv: step(T / "verify.py", VOL / "preview" / "volume.html")
