# Check every outside link in the given HTML files: status code and page title, 12 at a time.
# Usage: linkcheck.py OUT.tsv FILE.html ...
import concurrent.futures, html, re, subprocess, sys, tempfile, pathlib
out = pathlib.Path(sys.argv[1]); files = sys.argv[2:]
where = {}
for f in files:
    for u in re.findall(r'href="(https?://[^"]+)"', pathlib.Path(f).read_text(encoding="utf-8")):
        u = html.unescape(u)
        if "fonts.g" in u: continue
        where.setdefault(u, set()).add(pathlib.Path(f).name)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
def check(u):
    best = None
    for attempt in range(2):
        with tempfile.NamedTemporaryFile() as t:
            r = subprocess.run(["curl", "-sL", "-m", "40", "-A", UA, "-o", t.name, "-w", "%{http_code}\t%{url_effective}", u],
                               capture_output=True, text=True)
            code, final = (r.stdout.split("\t") + [""])[:2]
            body = pathlib.Path(t.name).read_bytes()[:400000].decode("utf-8", "ignore")
            m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
            title = html.unescape(" ".join(m.group(1).split()))[:90] if m else "-"
            best = (code, final, title)
            if code.startswith("2"): break
    return u, best
with concurrent.futures.ThreadPoolExecutor(12) as ex:
    rows = list(ex.map(check, sorted(where)))
with out.open("w") as f:
    for u, (code, final, title) in rows:
        f.write("\t".join([code, u, final, title, ",".join(sorted(where[u]))]) + "\n")
print(len(rows), "links;", sum(1 for _, b in rows if not b[0].startswith("2")), "not 2xx")
