import os, pathlib, random, shutil, subprocess, tempfile, time

def make_log(path):
    """A web server's access log: client, time, request, status, bytes sent, milliseconds taken."""
    rng = random.Random(3)
    clients = ["203.0.113.7"] * 9 + ["198.51.100.23"] * 6 + ["192.0.2.41"] * 4 + ["203.0.113.90"] * 3 + \
              ["198.51.100.5", "192.0.2.200"]
    pages = [("GET", "/", 200), ("GET", "/api/orders", 200), ("POST", "/api/orders", 201),
             ("GET", "/api/users", 200), ("GET", "/static/app.js", 200), ("POST", "/login", 302),
             ("GET", "/old-page", 404), ("GET", "/api/orders", 500), ("GET", "/api/report", 503)]
    lines = []
    for i in range(48):
        method, page, status = rng.choice(pages)
        ms = rng.randint(900, 2400) if status >= 500 else rng.randint(8, 640)
        stamp = time.strftime("%d/%b/%Y:%H:%M:%S", time.gmtime(1773306000 + 37 * i))
        lines.append(f'{rng.choice(clients)} - - [{stamp} +0000] "{method} {page} HTTP/1.1" '
                     f'{status} {rng.randint(120, 9000)} {ms}ms')
    path.write_text("\n".join(lines) + "\n")

def make_tree(root):
    """A small project folder, with a few files last changed long ago."""
    old = time.time() - 40 * 86400
    for name, text, aged in [("src/app.py", "# TODO: handle empty carts\n", False),
                             ("src/util.py", "x = 1\n", True), ("docs/guide.md", "", True),
                             ("tests/test_app.py", "# TODO: test refunds\n", False),
                             ("build/out.tmp", "", False), ("old notes.tmp", "", True),
                             ("node_modules/pkg/index.js", "", False), ("src/menu.js", "", False)]:
        p = root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
        if aged: os.utime(p, (old, old))

def q(cmd, cwd, env):
    r = subprocess.run([shutil.which("bash"), "--norc", "--noprofile", "-c", cmd], cwd=cwd, env=env,
                       capture_output=True, text=True)
    first, *rest = cmd.splitlines()
    print(f"   $ {first}" + "".join(f"\n   > {line.strip()}" for line in rest))
    for line in r.stdout.splitlines(): print(f"     {line}")

with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp); make_log(root / "access.log"); make_tree(root / "project")
    env = {"PATH": os.environ["PATH"], "HOME": "/home/learner", "LC_ALL": "C"}
    print("The log has lines like this one:")
    q("head -n 1 access.log", root, env)

    print("grep picks lines that match a regular expression")
    q("""grep -cE '" 5[0-9]{2} ' access.log""", root, env)
    q("""grep -E '" 5[0-9]{2} ' access.log | cut -d ' ' -f 1,7,9,11 | head -n 3""", root, env)
    q("""grep -oE '/api/[a-z]+' access.log | sort | uniq -c | awk '{print $1, $2}'""", root, env)

    print("awk splits each line into fields, $1 to $NF, and runs a little program on them")
    q("""awk '{n[$1]++} END {for (ip in n) print n[ip], ip}' access.log | sort -k1,1nr -k2,2 | head -n 3""",
      root, env)
    q("""awk '$NF + 0 > 1400 {print $7, $9, $NF}' access.log""", root, env)
    q("""awk '{c = substr($9, 1, 1) "xx"; t[c] += $NF; n[c]++}
     END {for (c in n) printf "%s %2d requests, average %4.0f ms\\n", c, n[c], t[c] / n[c]}' access.log |
     sort""",
      root, env)

    print("sed edits a stream: here it hides the last two parts of each address, and finds missing pages")
    q("""sed -E 's/^([0-9]+\\.[0-9]+)\\.[0-9]+\\.[0-9]+/\\1.x.x/' access.log |
     cut -d ' ' -f 1,7 | head -n 3""",
      root, env)
    q("""sed -nE 's/.*"GET ([^ ]+) [^"]*" 404 .*/\\1/p' access.log | sort -u""", root, env)

    print("find walks a folder tree and selects files by name, type, age and more")
    q("find . -name '*.py' | sort", root / "project", env)
    q("find . -name node_modules -prune -o -name '*.js' -print", root / "project", env)
    q("find . -type f -mtime +30 | sort", root / "project", env)
    q("grep -rn --include='*.py' TODO . | sort", root / "project", env)

    print("Names with spaces break naive pipelines; -print0 and xargs -0 separate names with a zero byte")
    q("find . -name '*.tmp' | xargs rm 2> /dev/null; find . -name '*.tmp' | sort", root / "project", env)
    q("find . -name '*.tmp' -print0 | xargs -0 rm; find . -name '*.tmp' | wc -l | tr -d ' '",
      root / "project", env)
