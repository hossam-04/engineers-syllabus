# Print each runnable example's output beside the prose that follows it. Usage: show.py VOL [max_out] [max_prose]
import json, re, html, sys, pathlib
v = sys.argv[1]; mo = int(sys.argv[2]) if len(sys.argv) > 2 else 700; mp = int(sys.argv[3]) if len(sys.argv) > 3 else 450
WS = pathlib.Path(__file__).resolve().parents[2]; d = (WS / f"{v}-handbook.html").read_text()
B = {b["id"]: b for b in json.load(open(pathlib.Path(__file__).parent / "blocks.json"))}
for r in json.load(open(pathlib.Path(__file__).parent / "python.json")):
    if r["vol"] != v or r["kind"] != "figure": continue
    b = B[r["id"]]; end = d.find("</figure>", b["pos"]) + 9
    prose = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", d[end:end + 2500]))).strip()[:mp]
    out = r.get("out", "").strip()
    print(f"### {r['id']} {r['ch']} [{r['status']}] {r['cap'][:60]}")
    if r["status"] != "ok": print("   last:", r.get("last", "")[:150])
    print("   OUT:", (out[:mo] + (" ..." if len(out) > mo else "")).replace("\n", "\n        "))
    print("   TEXT:", prose)
