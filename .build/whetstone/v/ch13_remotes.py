import os, pathlib, subprocess, tempfile

# Bare repositories in a temporary folder stand in for GitHub: "upstream" is the project, "fork" is
# the contributor's copy of it. Grace maintains the project; Ada contributes.
BASE = {"PATH": os.environ["PATH"], "HOME": "/home/learner", "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
PEOPLE = {"grace": ("Grace Hopper", "grace@example.org"), "ada": ("Ada Lovelace", "ada@example.org")}
clock = [1772355600]

def git(who, *args, cwd, check=True):
    clock[0] += 60
    name, email = PEOPLE[who]
    env = dict(BASE, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email, GIT_COMMITTER_NAME=name,
               GIT_COMMITTER_EMAIL=email, GIT_AUTHOR_DATE=f"@{clock[0]} +0000",
               GIT_COMMITTER_DATE=f"@{clock[0]} +0000")
    r = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True)
    if check and r.returncode: raise SystemExit(r.stderr)
    return r.stdout.rstrip() if check else r

def change(who, repo, name, text, message):
    (repo / name).write_text(text)
    git(who, "add", name, cwd=repo); git(who, "commit", "-q", "-m", message, cwd=repo)

def graph(who, repo, *revs):
    hide = "--decorate-refs-exclude=refs/remotes/*/HEAD"    # newer gits add these; older ones don't
    for line in git(who, "log", "--graph", "--format=%h %an: %s%d", hide, *revs, cwd=repo).splitlines():
        print(f"      {line}".rstrip())

with tempfile.TemporaryDirectory() as tmp:
    gh = pathlib.Path(tmp).resolve()
    print("1. Grace creates the project; Ada forks it on GitHub and clones her fork")
    git("grace", "init", "-q", "--bare", "-b", "main", "upstream.git", cwd=gh)
    git("grace", "clone", "-q", "upstream.git", "grace", cwd=gh)
    grace, ada = gh / "grace", gh / "ada"
    git("grace", "switch", "-q", "-c", "main", cwd=grace)
    change("grace", grace, "README.md", "# Recipes\nA small recipe site.\n", "Start the project")
    git("grace", "push", "-q", "origin", "main", cwd=grace)
    git("ada", "clone", "-q", "--bare", "upstream.git", "fork.git", cwd=gh)      # what the Fork button does
    git("ada", "clone", "-q", "fork.git", "ada", cwd=gh)
    git("ada", "remote", "add", "upstream", str(gh / "upstream.git"), cwd=ada)
    for line in git("ada", "remote", "-v", cwd=ada).splitlines():
        name, rest = line.split("\t"); url, kind = rest.rsplit(" ", 1)      # paths may contain spaces
        print(f"   Ada's remote {name:8} is {pathlib.Path(url).name} {kind}")

    print("2. Ada works on a branch and pushes it to her fork; that's what a pull request is opened from")
    git("ada", "switch", "-q", "-c", "fix-typo", cwd=ada)
    change("ada", ada, "README.md", "# Recipes\nA small site for recipes.\n", "Fix the README's wording")
    git("ada", "push", "-q", "-u", "origin", "fix-typo", cwd=ada)
    print(f"   {git('ada', 'status', '-sb', cwd=ada).splitlines()[0]}")

    print("3. Meanwhile Grace pushes to the project; a push that would lose her commit is refused")
    change("grace", grace, "CONTRIBUTING.md", "Open a pull request.\n", "Add contributing notes")
    git("grace", "push", "-q", "origin", "main", cwd=grace)
    git("ada", "switch", "-q", "main", cwd=ada)
    change("ada", ada, "notes.txt", "todo\n", "A commit made on main by mistake")
    r = git("ada", "push", "--porcelain", "upstream", "main", cwd=ada, check=False)
    print(f"   git push upstream main: status {r.returncode}, "
          f"{[l for l in r.stdout.splitlines() if l.startswith('!')][0].split(chr(9))[-1]}")
    git("ada", "reset", "-q", "--hard", "origin/main", cwd=ada)

    print("4. Ada brings her branch up to date: fetch upstream, rebase onto it, force-push with a lease")
    git("ada", "fetch", "-q", "upstream", cwd=ada)
    git("ada", "switch", "-q", "fix-typo", cwd=ada); git("ada", "rebase", "-q", "upstream/main", cwd=ada)
    git("ada", "push", "-q", "--force-with-lease", "origin", "fix-typo", cwd=ada)
    graph("ada", ada, "fix-typo")

    print("5. Grace reviews and merges the pull request: a merge commit on the project's main")
    git("grace", "fetch", "-q", str(gh / "fork.git"), "fix-typo", cwd=grace)
    git("grace", "merge", "-q", "--no-ff", "-m", "Merge pull request #1 from ada/fix-typo", "FETCH_HEAD",
        cwd=grace)
    git("grace", "push", "-q", "origin", "main", cwd=grace)
    graph("grace", grace, "main")

    print("6. Ada syncs: update her main from upstream, push it to her fork, delete the merged branch")
    git("ada", "switch", "-q", "main", cwd=ada)
    git("ada", "pull", "-q", "--ff-only", "upstream", "main", cwd=ada)
    git("ada", "push", "-q", "origin", "main", ":fix-typo", cwd=ada)     # ":name" deletes a remote branch
    git("ada", "branch", "-q", "-D", "fix-typo", cwd=ada)
    same = {git("ada", "rev-parse", r, cwd=gh / repo) for repo, r in
            (("upstream.git", "main"), ("fork.git", "main"), ("ada", "main"), ("grace", "main"))}
    refs = git("ada", "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", cwd=ada).split()
    branches = [r.split("/", 2)[2] for r in refs if not r.endswith("/HEAD")]
    print(f"   all four copies of main are the same commit: {len(same) == 1}")
    print(f"   Ada's branches and remote-tracking branches: {', '.join(branches)}")
