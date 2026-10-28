"""The maintainer's side of open source: two patches arrive for a small project, and each gets the
checks a careful maintainer runs before reading a single line of the diff."""
import ast, os, pathlib, re, subprocess, sys, tempfile

BASE = {"PATH": os.environ["PATH"], "HOME": "/home/maintainer", "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
PEOPLE = {"mira": ("Mira Okafor", "mira@example.org"), "theo": ("Theo Lind", "theo@example.org"),
          "sam": ("Sam Reyes", "sam@example.org")}
clock = [1780000000]

def git(who, *args, cwd):
    clock[0] += 60
    name, email = PEOPLE[who]
    env = dict(BASE, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email, GIT_COMMITTER_NAME=name,
               GIT_COMMITTER_EMAIL=email, GIT_AUTHOR_DATE=f"@{clock[0]} +0000",
               GIT_COMMITTER_DATE=f"@{clock[0]} +0000")
    r = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True)
    return r

SLUG = '''import re


def slugify(title):
    """'Hello, World!' -> 'hello-world'"""
    return "-".join(re.findall(r"[a-z0-9]+", title.lower()))
'''
TESTS = '''from slug import slugify

assert slugify("Hello, World!") == "hello-world"
assert slugify("  many   spaces ") == "many-spaces"
'''

def commit(who, repo, files, message):
    for name, text in files.items():
        (repo / name).write_text(text)
    git(who, "add", *files, cwd=repo)
    git(who, "commit", "-q", "-m", message, cwd=repo)

def public_names(source):
    return {n.name for n in ast.parse(source).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and not n.name.startswith("_")}

def review(gh, patch):
    """Apply the patch to a fresh clone of main and report on it."""
    work = gh / ("review-" + patch.stem)
    git("mira", "clone", "-q", str(gh / "upstream.git"), str(work), cwd=gh)
    before = public_names((work / "slug.py").read_text())
    applied = git("mira", "am", "-q", "--3way", str(patch), cwd=work).returncode == 0
    if not applied:
        return [("applies cleanly", False, "conflicts with main")]
    message = git("mira", "log", "-1", "--format=%B", cwd=work).stdout.strip()
    subject, _, body = message.partition("\n")
    stat = git("mira", "diff", "--numstat", "HEAD~1", cwd=work).stdout.split("\n")
    files = {}
    for line in filter(None, stat):                  # "added<TAB>removed<TAB>path"
        added, removed, path = line.split("\t")
        files[path] = (int(added), int(removed))
    tests = subprocess.run([sys.executable, "test_slug.py"], cwd=work, capture_output=True, text=True)
    lost = before - public_names((work / "slug.py").read_text())
    first = subject.split()[0].lower()
    return [
        ("applies cleanly", True, ""),
        ("tests pass", tests.returncode == 0,
         re.sub(r" \(/.*\)$", "", tests.stderr.strip().splitlines()[-1]) if tests.returncode else ""),
        ("adds or changes a test", "test_slug.py" in files, ""),
        ("keeps the public API", not lost, f"removes {', '.join(sorted(lost))}" if lost else ""),
        ("small enough to review", sum(a + d for a, d in files.values()) <= 40,
         f"{sum(a for a, _ in files.values())} lines added, {sum(d for _, d in files.values())} removed"),
        ("subject: short, imperative, no full stop", len(subject) <= 50 and not subject.endswith(".")
         and not re.search(r"(ed|ing|es)$", first), repr(subject)),
        ("body says why", len(body.split()) >= 12, f"{len(body.split())} words"),
        ("signed off (DCO)", "Signed-off-by: " in message, ""),
    ]

with tempfile.TemporaryDirectory() as tmp:
    gh = pathlib.Path(tmp).resolve()
    git("mira", "init", "-q", "--bare", "-b", "main", "upstream.git", cwd=gh)
    git("mira", "clone", "-q", "upstream.git", "mira", cwd=gh)
    git("mira", "switch", "-q", "-c", "main", cwd=gh / "mira")
    commit("mira", gh / "mira", {"slug.py": SLUG, "test_slug.py": TESTS}, "Add slugify")
    git("mira", "push", "-q", "origin", "main", cwd=gh / "mira")

    # Issue 12: "Café Société" becomes "caf-soci-t". Two people send patches.
    for who in ("theo", "sam"):
        git(who, "clone", "-q", "upstream.git", who, cwd=gh)
    commit("theo", gh / "theo", {
        "slug.py": SLUG.replace("import re\n", "import re\nimport unicodedata\n").replace(
            '    return "-".join(re.findall(r"[a-z0-9]+", title.lower()))',
            '    folded = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()\n'
            '    return "-".join(re.findall(r"[a-z0-9]+", folded.lower()))'),
        "test_slug.py": TESTS + 'assert slugify("Café Société") == "cafe-societe"   # issue 12\n'},
        "Fold accents before making a slug\n\nAccented letters were dropped, so \"Café Société\" became "
        "\"caf-soci-t\" (issue 12). Decompose the title with NFKD and keep the ASCII part, so it "
        "becomes \"cafe-societe\".\n\nSigned-off-by: Theo Lind <theo@example.org>")
    commit("sam", gh / "sam", {
        "slug.py": "import re, unicodedata\n\n"
                   "def make_slug(t):\n"
                   "    t = unicodedata.normalize('NFKD', t)\n"
                   "    t = t.encode('ascii', 'ignore').decode('ascii')\n"
                   "    t = t.lower().strip()\n"
                   "    t = re.sub(r'[^a-z0-9]+', '-', t)\n"
                   "    return t\n"},
        "fixed the accents bug.")
    for who in ("theo", "sam"):
        out = git(who, "format-patch", "-1", "-o", str(gh / "inbox"), cwd=gh / who).stdout.strip()
        patch = pathlib.Path(out)
        print(f"{PEOPLE[who][0]}'s patch, {patch.name}:")
        for check, ok, note in review(gh, patch):
            print(f"  {'ok  ' if ok else 'FAIL'} {check:42} {note}".rstrip())
