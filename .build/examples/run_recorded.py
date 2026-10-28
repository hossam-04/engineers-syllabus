# Run every example that shows its output, in a fresh temporary folder, and compare what it prints
# with the recorded output. Writes recorded.json. Usage: run_recorded.py [vol ...]
import json, os, re, subprocess, sys, tempfile, pathlib, time
from concurrent.futures import ThreadPoolExecutor
E = [e for e in json.load(open(pathlib.Path(__file__).parent / "examples.json"))
     if any(b["out"] for b in e["blocks"]) and (len(sys.argv) < 2 or e["vol"] in sys.argv[1:])]
def fname(e):
    m = re.match(r'\s*([\w.-]+\.py)\b', e["cap"]); return m.group(1) if m else f"ex{e['n']:02d}.py"
def run(e):
    code = "\n".join(b["text"] for b in e["blocks"] if not b["out"] and b["lang"] == "python")
    want = "\n".join(b["text"] for b in e["blocks"] if b["out"]).rstrip("\n")
    d = pathlib.Path(tempfile.mkdtemp(prefix=f"ex-{e['vol']}-{e['n']:02d}-"))
    f = d / fname(e); f.write_text(code + "\n", encoding="utf-8")
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1", LC_ALL="C.UTF-8", TZ="UTC")
    t = time.time()
    try:
        r = subprocess.run([sys.executable, f.name], cwd=d, capture_output=True, text=True, timeout=300, env=env)
        got, err, rc = r.stdout.rstrip("\n"), r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        got, err, rc = "", "TIMEOUT", -9
    both = (got + ("\n" + err.rstrip("\n") if err else "")).strip("\n")
    status = "same" if got == want else ("same+stderr" if both == want else "DIFF")
    return {"vol": e["vol"], "n": e["n"], "ch": e["ch"], "file": f.name, "status": status, "rc": rc,
            "secs": round(time.time() - t, 1), "want": want, "got": got, "err": err[-2000:]}
with ThreadPoolExecutor(6) as ex: res = list(ex.map(run, E))
prev = pathlib.Path(__file__).parent / "recorded.json"
old = {(r["vol"], r["n"]): r for r in json.load(open(prev))} if prev.exists() and len(sys.argv) > 1 else {}
for r in res: old[(r["vol"], r["n"])] = r
json.dump(sorted(old.values(), key=lambda r: (r["vol"], r["n"])), open(prev, "w"), indent=1)
for r in res:
    if r["status"] == "DIFF" or r["rc"] != 0: print(f"{r['vol']:20} {r['n']:2} {r['ch']} {r['file']:24} {r['status']} rc={r['rc']} {r['secs']}s")
import collections; print(collections.Counter((r["vol"], r["status"]) for r in res))
