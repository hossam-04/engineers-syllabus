import os, pathlib, re, subprocess, sys, tempfile

ENV = {"PATH": os.environ["PATH"], "HOME": "/home/learner", "LC_ALL": "C",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_AUTHOR_NAME": "Ada Lovelace", "GIT_AUTHOR_EMAIL": "ada@example.org",
       "GIT_COMMITTER_NAME": "Ada Lovelace", "GIT_COMMITTER_EMAIL": "ada@example.org"}
clock = [1772355600]

def git(*args, cwd):
    clock[0] += 60
    env = dict(ENV, GIT_AUTHOR_DATE=f"@{clock[0]} +0000", GIT_COMMITTER_DATE=f"@{clock[0]} +0000")
    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True,
                          check=True).stdout.rstrip()

GOOD = '''import re, unicodedata

def slug(title):
    """Make a web address from a title: "Creme Brulee, 2 Ways!" -> "creme-brulee-2-ways"."""
    plain = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")
'''
BAD = GOOD.replace('    plain = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()\n'
                   '    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")\n',
                   '    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")\n')
CHECK = ('from recipes import slug\n'
         'raise SystemExit(slug("Crème Brûlée, 2 Ways!") != "creme-brulee-2-ways")\n')

with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp); repo = root / "site"; repo.mkdir()
    git("init", "-q", "-b", "main", cwd=repo)
    (repo / "recipes.py").write_text(GOOD); (repo / "list.txt").write_text("")
    git("add", ".", cwd=repo); git("commit", "-q", "-m", "Add slug() for recipe addresses", cwd=repo)
    number = {git("rev-parse", "HEAD", cwd=repo): 1}
    for n in range(2, 41):                             # 39 more commits; number 27 breaks slug()
        if n == 27:
            (repo / "recipes.py").write_text(BAD); message = "Simplify slug()"
        else:
            with (repo / "list.txt").open("a") as f: f.write(f"recipe {n}\n")
            message = f"Add recipe {n}"
        git("commit", "-q", "-am", message, cwd=repo)
        number[git("rev-parse", "HEAD", cwd=repo)] = n
    (root / "check.py").write_text(CHECK)
    (root / "check.sh").write_text(f'#!/bin/sh\nPYTHONPATH=. exec "{sys.executable}" ../check.py\n')
    (root / "check.sh").chmod(0o755)
    run = lambda: subprocess.run(["../check.sh"], cwd=repo, env=ENV, capture_output=True).returncode
    first = git("rev-list", "--max-parents=0", "HEAD", cwd=repo)
    print(f"40 commits. The test (../check.sh) exits with status {run()} at HEAD: something broke.")

    print("1. git bisect run: a binary search over history, with the test deciding good or bad")
    git("bisect", "start", "HEAD", first, cwd=repo)
    git("bisect", "run", "../check.sh", cwd=repo)
    bad = git("rev-parse", "refs/bisect/bad", cwd=repo)
    steps = [l.split()[2:4] for l in git("bisect", "log", cwd=repo).splitlines()
             if l.startswith(("git bisect good ", "git bisect bad "))]
    tried = [f"{number[h]} ({verdict})" for verdict, h in steps]
    print(f"   it tested commits {', '.join(tried[:-1])} and {tried[-1]}")
    print(f"   {len(steps)} tests for 39 suspects; the first bad commit is number {number[bad]}: "
          f"{git('log', '-1', '--format=%h %s', bad, cwd=repo)}")
    git("bisect", "reset", cwd=repo)

    print("2. git log -S: the commits that added or removed a piece of text")
    for line in git("log", "-S", "normalize", "--format=%h %s", cwd=repo).splitlines(): print(f"   {line}")

    print("3. git blame: which commit last changed each line")
    blame = git("blame", "--line-porcelain", "-L", "3,5", "recipes.py", cwd=repo).splitlines()
    commits = [l.split()[0] for l in blame if re.match(r"[0-9a-f]{40} \d+ \d+", l)]
    summaries = [l[len("summary "):] for l in blame if l.startswith("summary ")]
    code = [l[1:] for l in blame if l.startswith("\t")]
    for h, summary, line in zip(commits, summaries, code):
        print(f"   {h[:7]} {summary[:31]:31} | {line}")

    print("4. git revert: a new commit that undoes an old one, without rewriting history")
    git("revert", "--no-edit", bad, cwd=repo)
    print(f"   {git('log', '-1', '--format=%h %s', cwd=repo)}; the test now exits with status {run()}")
