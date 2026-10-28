# Re-run every python example exactly as it appears in the built volume and check that it prints
# exactly the output shown under it. Each example runs twice: in a plain environment, and in a
# hostile one (another hash seed, temp folder, time zone, and a HOME whose git and shell settings
# would change the output of any example that doesn't isolate itself). Both must match.
# Usage: verify.py VOLUME.html [example numbers...]
import sys, re, html, os, pathlib, subprocess, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from hostile import hostile_env
doc = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
only = {int(a) for a in sys.argv[2:]}
FIG = re.compile(r'<span class="file">(.*?)</span></figcaption><pre><code class="language-python">(.*?)</code></pre>'
                 r'<div class="out-h">Output</div><pre class="out"><code class="language-plaintext">(.*?)</code></pre>', re.S)

bad = 0
for i, (caption, src, shown) in enumerate(FIG.findall(doc), 1):
    if only and i not in only: continue
    name = html.unescape(re.sub(r'<[^>]+>', '', caption)).split(" ")[0]
    want = html.unescape(shown.replace("&#xFFFD;", "�"))
    code = html.unescape(src)
    long = [n for n, l in enumerate(code.splitlines(), 1) if len(l) > 108]
    results = []
    for mode in ("plain", "hostile"):
        root = pathlib.Path(tempfile.mkdtemp(prefix=f"verify-{mode}-"))
        f = root / name; f.write_text(code, encoding="utf-8")
        env = dict(os.environ, PYTHONHASHSEED="1") if mode == "plain" else hostile_env(root)
        r = subprocess.run([sys.executable, str(f)], capture_output=True, text=True, cwd=root, env=env, timeout=900)
        results.append((mode, r.returncode, r.stdout.rstrip("\n"), r.stderr))
    ok = all(rc == 0 and out == want for _, rc, out, _ in results) and not long
    bad += not ok
    print(f"example {i:2} {name:18} {'OK' if ok else 'MISMATCH'}" + (f"  lines over 108: {long}" if long else ""))
    if not ok:
        for mode, rc, out, err in results:
            if rc or out != want:
                print(f"   [{mode}] exit {rc}; stderr: {err[-600:]}")
                wl, gl = want.splitlines(), out.splitlines()
                for k in range(max(len(wl), len(gl))):
                    a = wl[k] if k < len(wl) else "<missing>"; b = gl[k] if k < len(gl) else "<missing>"
                    if a != b: print(f"   line {k + 1}\n     shown: {a!r}\n     got:   {b!r}"); break
print("ALL EXAMPLES MATCH" if not bad else f"{bad} PROBLEM(S)")
sys.exit(1 if bad else 0)
