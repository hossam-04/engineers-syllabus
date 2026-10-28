# Parse and run every Python block that has no recorded output to compare against. Classifies each as
# ok (ran to the end), fragment (needs names or packages defined elsewhere), error, or syntax error.
# Writes python.json.
import ast, json, os, re, subprocess, sys, tempfile, pathlib, time
from concurrent.futures import ThreadPoolExecutor
HERE = pathlib.Path(__file__).parent
REC = {(e["vol"], e["n"]) for e in json.load(open(HERE / "examples.json")) if any(b["out"] for b in e["blocks"])}
B = [b for b in json.load(open(HERE / "blocks.json")) if b["lang"] == "python" and (b["vol"], b["fig"]) not in REC]
def run(b):
    r = {"id": b["id"], "vol": b["vol"], "ch": b["ch"], "kind": b["kind"], "fig": b["fig"], "cap": b["cap"], "lines": b["text"].count("\n") + 1}
    try: ast.parse(b["text"])
    except SyntaxError as e: r.update(status="syntax", err=f"line {e.lineno}: {e.msg}"); return r
    d = pathlib.Path(tempfile.mkdtemp(prefix="py-", dir="/tmp")); (d / "x.py").write_text(b["text"] + "\n", encoding="utf-8")
    # a clean environment: some examples print os.environ, and the recording is published
    env = dict(PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin", HOME=str(d), LANG="en_US.UTF-8",
               PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1", TZ="UTC")
    t = time.time()
    try:
        p = subprocess.run([sys.executable, "x.py"], cwd=d, capture_output=True, text=True, timeout=120, env=env, stdin=subprocess.DEVNULL)
        out, err, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired: out, err, rc = "", "TIMEOUT", -9
    last = err.strip().splitlines()[-1] if err.strip() else ""
    if rc == 0: st = "ok"
    elif re.match(r"(NameError|ModuleNotFoundError|ImportError)\b", last): st = "fragment"
    else: st = "error"
    r.update(status=st, rc=rc, out=out[-3000:], err=err[-1500:], last=last, secs=round(time.time() - t, 1))
    return r
with ThreadPoolExecutor(6) as ex: res = list(ex.map(run, B))
json.dump(res, open(HERE / "python.json", "w"), indent=1)
import collections
c = collections.Counter((r["vol"], r["kind"], r["status"]) for r in res)
for k in sorted(c): print(f"{k[0]:24} {k[1]:9} {k[2]:9} {c[k]}")
