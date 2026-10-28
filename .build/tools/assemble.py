# Expand chapter templates in a volume folder.
#   __EXAMPLE:name|caption__  a code figure: the code of v/name.py and the output of running it
#                             (or v/name.out when that file exists, for examples whose output varies)
#   __SVG:figNN__             the drawing returned by figNN() in the volume's figs.py
# Captions must not contain underscores. Usage: assemble.py VOL_DIR NN_chXX.tpl ...
import sys, re, html, pathlib, subprocess, importlib.util
VOL = pathlib.Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("figs", VOL / "figs.py")
figs = importlib.util.module_from_spec(spec); spec.loader.exec_module(figs)

def run(name):
    rec = VOL / "v" / f"{name}.out"
    if rec.exists(): return rec.read_text(encoding="utf-8").rstrip("\n")
    r = subprocess.run([sys.executable, str(VOL / "v" / f"{name}.py")], capture_output=True,
                       text=True, cwd=VOL / "v", timeout=900)
    if r.returncode: raise SystemExit(f"{name} failed:\n{r.stderr}")
    return r.stdout.rstrip("\n")
def code(name): return (VOL / "v" / f"{name}.py").read_text(encoding="utf-8").rstrip("\n")
def example(m):
    name, caption = m.group(1), m.group(2)
    out = html.escape(run(name), quote=False).replace(chr(0xFFFD), "&#xFFFD;")
    return ('<figure class="code"><figcaption><span class="tag">Example</span>'
            f'<span class="file">{caption}</span></figcaption>'
            f'<pre><code class="language-python">{code(name)}</code></pre>'
            '<div class="out-h">Output</div>'
            f'<pre class="out"><code class="language-plaintext">{out}</code></pre></figure>')
for tpl in sys.argv[2:]:
    p = VOL / tpl
    t = p.read_text(encoding="utf-8")
    t = re.sub(r'__EXAMPLE:([a-z0-9_]+)\|([^_]+?)__', example, t)
    t = re.sub(r'__SVG:(fig\d\d)__', lambda m: getattr(figs, m.group(1))(), t)
    assert not re.search(r'__(EXAMPLE|SVG)', t), tpl
    p.with_suffix(".html").write_text(t, encoding="utf-8")
    print("assembled", p.with_suffix(".html").name)
