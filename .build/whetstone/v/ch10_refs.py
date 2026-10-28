import os, pathlib, subprocess, tempfile

ENV = {"PATH": os.environ["PATH"], "HOME": "/home/learner", "LC_ALL": "C",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_AUTHOR_NAME": "Ada Lovelace", "GIT_AUTHOR_EMAIL": "ada@example.org",
       "GIT_COMMITTER_NAME": "Ada Lovelace", "GIT_COMMITTER_EMAIL": "ada@example.org"}
clock = [1772355600]

def git(*args, cwd):
    env = dict(ENV, GIT_AUTHOR_DATE=f"@{clock[0]} +0000", GIT_COMMITTER_DATE=f"@{clock[0]} +0000")
    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True,
                          check=True).stdout.rstrip()

def commit(message, cwd):
    clock[0] += 60
    with (cwd / "log.txt").open("a") as f: f.write(message + "\n")
    git("add", "log.txt", cwd=cwd); git("commit", "-q", "-m", message, cwd=cwd)
    return git("rev-parse", "--short", "HEAD", cwd=cwd)

def files(repo, *names):
    for name in names:
        text = (repo / ".git" / name).read_text().strip()
        if not text.startswith("ref:"): text = text[:12] + "... (40 hex digits)"
        print(f"   .git/{name:18} contains: {text}")

def graph(repo):
    for line in git("log", "--all", "--graph", "--format=%h %s%d", cwd=repo).splitlines():
        print(f"      {line}".rstrip())

with tempfile.TemporaryDirectory() as tmp:
    repo = pathlib.Path(tmp); git("init", "-q", "-b", "main", cwd=repo)
    a = commit("A: first", repo); b = commit("B: second", repo)

    print("1. A branch is a file holding a commit's id; HEAD is a file naming the current branch")
    files(repo, "HEAD", "refs/heads/main")
    print("2. Making a branch writes one small file; nothing is copied")
    git("branch", "feature", cwd=repo); files(repo, "refs/heads/feature")
    print("3. A commit moves the current branch, and only that one")
    git("switch", "-q", "feature", cwd=repo); c = commit("C: on feature", repo)
    files(repo, "HEAD", "refs/heads/feature", "refs/heads/main"); graph(repo)

    print("4. Detached HEAD: HEAD holds a commit id instead of a branch name")
    git("switch", "-q", "--detach", b, cwd=repo); files(repo, "HEAD")
    d = commit("D: an experiment", repo)
    git("switch", "-q", "main", cwd=repo)
    print(f"   back on main, D ({d}) is on no branch, so log --all no longer shows it:"); graph(repo)

    print("5. The reflog records every move of HEAD, so D can still be found and given a name")
    for line in git("reflog", "--format=%h %gs", cwd=repo).splitlines()[:4]: print(f"      {line}")
    git("branch", "experiment", d, cwd=repo); graph(repo)

    print("6. reset moves the current branch to another commit; the reflog can move it back")
    git("reset", "-q", "--hard", a, cwd=repo)
    print(f"   after reset --hard {a}, main is at {git('rev-parse', '--short', 'main', cwd=repo)}; "
          f"main's reflog: {', '.join(git('reflog', 'main', '--format=%h', cwd=repo).split())}")
    git("reset", "-q", "--hard", "main@{1}", cwd=repo)
    lines = len((repo / "log.txt").read_text().splitlines())
    print(f"   after reset --hard main@{{1}}, main is at {git('rev-parse', '--short', 'main', cwd=repo)} "
          f"again, and log.txt has {lines} lines")
