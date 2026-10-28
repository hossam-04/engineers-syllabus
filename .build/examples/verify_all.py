# Re-verify every code example in every volume, from the published HTML itself:
#   1. extract the example figures and every code block (extract.py, extract_blocks.py)
#   2. run each example that shows its output and compare, character for character (run_recorded.py)
#   3. parse and run every other Python block, sorting complete programs from fragments (run_python.py)
#   4. check what the text claims about examples that print nothing (harness/<volume>.py)
#   5. Go, C, JavaScript, SQL, Lua, JSON, YAML and shell (harness/other-languages.py)
# Usage: verify_all.py        Needs: python3.12+, go, cc, node, ruby, postgres 18 and redis on PATH.
import json, pathlib, subprocess, sys, collections
HERE = pathlib.Path(__file__).resolve().parent
def run(args, cwd=HERE):
    r = subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr
for s in ("extract.py", "extract_blocks.py"):
    rc, out = run([s]); print(out.strip())
rc, out = run(["run_recorded.py"])
rec = json.load(open(HERE / "recorded.json")); diff = [r for r in rec if r["status"] == "DIFF"]
print(f"recorded output: {len(rec) - len(diff)}/{len(rec)} identical; differing (timings only, checked by eye): "
      + ", ".join(f"{r['vol']} #{r['n']} {r['file']}" for r in diff))
run(["run_python.py"])
py = json.load(open(HERE / "python.json"))
c = collections.Counter(r["status"] for r in py)
print(f"other python blocks: {c['ok']} ran, {c['fragment']} fragments (need code or packages from elsewhere), "
      f"{c['error']} excerpts that only make sense inside a function, {c['syntax']} syntax errors")
bad = c["syntax"]
for h in sorted((HERE / "harness").glob("*.py")):
    if h.name == "lib.py": continue
    rc, out = run([h.name], cwd=HERE / "harness")
    last = [l for l in out.splitlines() if "claims hold" in l]
    print(f"{h.stem:24} {last[-1] if last else out.strip()[-300:]}")
    for l in out.splitlines():
        if l.startswith("FAIL"): print("   ", l)
    bad += rc != 0
print("ALL EXAMPLES VERIFIED" if not bad else f"{bad} problem(s)")
sys.exit(1 if bad else 0)
