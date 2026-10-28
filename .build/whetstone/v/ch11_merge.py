import os, pathlib, subprocess, tempfile

ENV = {"PATH": os.environ["PATH"], "HOME": "/home/learner", "LC_ALL": "C",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_AUTHOR_NAME": "Ada Lovelace", "GIT_AUTHOR_EMAIL": "ada@example.org",
       "GIT_COMMITTER_NAME": "Ada Lovelace", "GIT_COMMITTER_EMAIL": "ada@example.org"}
clock = [1772355600]

def git(*args, cwd, check=True):
    clock[0] += 60                                     # every command happens a minute after the last
    env = dict(ENV, GIT_AUTHOR_DATE=f"@{clock[0]} +0000", GIT_COMMITTER_DATE=f"@{clock[0]} +0000")
    r = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=check)
    return r.stdout.rstrip() if check else r

def edit(repo, branch, line, text, message):
    """Switch to a branch, replace one line of menu.txt, and commit."""
    git("switch", "-q", branch, cwd=repo)
    lines = (repo / "menu.txt").read_text().splitlines(); lines[line - 1] = text
    (repo / "menu.txt").write_text("\n".join(lines) + "\n")
    git("commit", "-q", "-am", message, cwd=repo)

def version(repo, rev): return git("show", f"{rev}:menu.txt", cwd=repo).splitlines()

def graph(repo):
    for line in git("log", "--graph", "--format=%h %s%d", "main", cwd=repo).splitlines():
        print(f"      {line}".rstrip())

with tempfile.TemporaryDirectory() as tmp:
    repo = pathlib.Path(tmp); git("init", "-q", "-b", "main", cwd=repo)
    (repo / "menu.txt").write_text("Soup\nBread\nSalad\nPasta\nCake\nTea\nWater\n")
    git("add", ".", cwd=repo); git("commit", "-q", "-m", "Base menu", cwd=repo)
    for b in ("lunch", "dinner", "drinks"): git("branch", b, cwd=repo)
    edit(repo, "lunch", 2, "Sourdough", "Lunch: sourdough")
    edit(repo, "main", 5, "Lemon cake", "Main: lemon cake")

    print("1. A merge compares each side with the merge base, the last commit both sides share")
    base = git("merge-base", "main", "lunch", cwd=repo)
    print(f"   merge base of main and lunch: {base[:7]} {git('log', '-1', '--format=%s', base, cwd=repo)}")
    b, ours, theirs = version(repo, base), version(repo, "main"), version(repo, "lunch")
    git("merge", "-q", "--no-edit", "lunch", cwd=repo)
    result = (repo / "menu.txt").read_text().splitlines()
    print(f"   {'line':5}{'base':12}{'main (ours)':14}{'lunch (theirs)':16}{'rule':24}merged")
    for i, (x, o, t, m) in enumerate(zip(b, ours, theirs, result), 1):
        rule = "nobody changed it" if o == t == x else "only theirs changed" if o == x else \
               "only ours changed" if t == x else "both, the same way" if o == t else "both: conflict"
        print(f"   {i:<5}{x:12}{o:14}{t:16}{rule:24}{m}")

    print("2. A conflict: both sides changed the same line in different ways")
    edit(repo, "dinner", 2, "Garlic bread", "Dinner: garlic bread")
    git("switch", "-q", "main", cwd=repo)
    r = git("merge", "--no-edit", "dinner", cwd=repo, check=False)
    print(f"   git merge dinner exits with status {r.returncode}; unmerged: "
          f"{git('diff', '--name-only', '--diff-filter=U', cwd=repo)}")
    for line in (repo / "menu.txt").read_text().splitlines()[:7]: print(f"      {line}")
    resolved = ["Soup", "Sourdough or garlic bread", "Salad", "Pasta", "Lemon cake", "Tea", "Water"]
    (repo / "menu.txt").write_text("\n".join(resolved) + "\n")
    git("add", "menu.txt", cwd=repo); git("commit", "-q", "--no-edit", cwd=repo)
    print("   resolved by hand, added, committed:"); graph(repo)

    print("3. When one side has no new commits, merging just moves the branch forward")
    git("switch", "-q", "-c", "tea", cwd=repo); edit(repo, "tea", 6, "Mint tea", "Tea: mint")
    git("switch", "-q", "main", cwd=repo); git("merge", "-q", "--ff-only", "tea", cwd=repo)
    same = git("rev-parse", "main", cwd=repo) == git("rev-parse", "tea", cwd=repo)
    print(f"   main and tea are now the same commit: {same}")

    print("4. A rebase replays commits on a new base: same changes, new commits, new ids")
    git("switch", "-q", "drinks", cwd=repo)
    for drink in ("Lemonade", "Coffee"):
        with (repo / "menu.txt").open("a") as f: f.write(drink + "\n")
        git("commit", "-q", "-am", f"Drinks: {drink.lower()}", cwd=repo)
    before = git("rev-list", "--reverse", "main..drinks", cwd=repo).split()
    git("rebase", "-q", "main", cwd=repo)
    after = git("rev-list", "--reverse", "main..drinks", cwd=repo).split()
    def patch(rev):                                    # the lines a commit removes and adds
        diff = git("show", "--format=", "-U0", rev, cwd=repo).splitlines()
        return [l for l in diff if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    for old, new in zip(before, after):
        print(f"   {git('log', '-1', '--format=%s', new, cwd=repo):18} {old[:7]} -> {new[:7]}   "
              f"same change: {patch(old) == patch(new)}")
    git("switch", "-q", "main", cwd=repo); git("merge", "-q", "--ff-only", "drinks", cwd=repo)
    print("   then main fast-forwards to it, and history stays a straight line from the merge:")
    graph(repo)
