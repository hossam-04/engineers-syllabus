import hashlib, os, pathlib, subprocess, tempfile, zlib

# Fixed names and times, and no personal git settings, so every hash below is the same on any machine.
ENV = {"PATH": os.environ["PATH"], "HOME": "/home/learner", "LC_ALL": "C",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_AUTHOR_NAME": "Ada Lovelace", "GIT_AUTHOR_EMAIL": "ada@example.org",
       "GIT_COMMITTER_NAME": "Ada Lovelace", "GIT_COMMITTER_EMAIL": "ada@example.org"}
clock = [1772355600]                                   # 2026-03-01 09:00 UTC, advanced a minute per commit

def git(*args, cwd, data=None):
    env = dict(ENV, GIT_AUTHOR_DATE=f"@{clock[0]} +0000", GIT_COMMITTER_DATE=f"@{clock[0]} +0000")
    r = subprocess.run(["git", *args], cwd=cwd, env=env, input=data, capture_output=True, check=True)
    return r.stdout.decode().strip()

def commit(message, cwd):
    clock[0] += 60
    git("commit", "-q", "-m", message, cwd=cwd)
    return git("rev-parse", "HEAD", cwd=cwd)

def object_id(kind, body):
    """Every git object is named by the SHA-1 of a header ("blob 6", say), a zero byte, and the body."""
    return hashlib.sha1(f"{kind} {len(body)}".encode() + b"\0" + body).hexdigest()

def tree_id(folder):
    """A tree lists its entries, sorted by name: mode, name, a zero byte, and the entry's id as 20 bytes."""
    entries = []
    for p in folder.iterdir():
        if p.name == ".git": continue
        if p.is_dir(): entries.append((p.name + "/", b"40000", p.name, tree_id(p)))
        else: entries.append((p.name, b"100644", p.name, object_id("blob", p.read_bytes())))
    body = b"".join(mode + b" " + name.encode() + b"\0" + bytes.fromhex(oid)
                    for _, mode, name, oid in sorted(entries))
    return object_id("tree", body)

with tempfile.TemporaryDirectory() as tmp:
    repo = pathlib.Path(tmp)
    git("init", "-q", "-b", "main", cwd=repo)

    print("1. A blob is a file's contents, named by its hash")
    mine = object_id("blob", b"hello\n")
    print(f"   by hand:              {mine}")
    print(f"   git hash-object:      {git('hash-object', '-w', '--stdin', cwd=repo, data=b'hello\n')}")
    stored = repo / ".git" / "objects" / mine[:2] / mine[2:]
    print(f"   stored in .git/objects/{mine[:2]}/{mine[2:8]}..., compressed; inflated it is "
          f"{zlib.decompress(stored.read_bytes())!r}")

    print("2. A tree is a folder listing; a commit names a tree, its parents, an author and a message")
    (repo / "src").mkdir()
    (repo / "README.md").write_text("# Shop\n"); (repo / "src" / "app.py").write_text("print('shop')\n")
    git("add", ".", cwd=repo)
    print(f"   tree by hand:         {tree_id(repo)}")
    print(f"   git write-tree:       {git('write-tree', cwd=repo)}")
    first = commit("Start the shop", repo)
    text = (f"tree {tree_id(repo)}\nauthor Ada Lovelace <ada@example.org> {clock[0]} +0000\n"
            f"committer Ada Lovelace <ada@example.org> {clock[0]} +0000\n\nStart the shop\n")
    print(f"   commit by hand:       {object_id('commit', text.encode())}")
    print(f"   git commit:           {first}")
    print("   git cat-file -p HEAD:")
    for line in git("cat-file", "-p", "HEAD", cwd=repo).splitlines(): print(f"      {line}".rstrip())
    print("   git cat-file -p HEAD^{tree}:")
    for line in git("cat-file", "-p", "HEAD^{tree}", cwd=repo).splitlines(): print(f"      {line}")

    print("3. A new commit is a new snapshot; whatever didn't change is shared, not copied")
    (repo / "README.md").write_text("# Shop\nOpen 9 to 5.\n"); git("add", ".", cwd=repo)
    second = commit("Add opening hours", repo)
    for name, rev in (("first", first), ("second", second)):
        print(f"   {name:6} commit {rev[:10]}  tree {git('rev-parse', rev + '^{tree}', cwd=repo)[:10]}"
              f"  src/ {git('rev-parse', rev + ':src', cwd=repo)[:10]}"
              f"  README.md {git('rev-parse', rev + ':README.md', cwd=repo)[:10]}")
    print(f"   the second commit's parent is the first: {git('rev-parse', 'HEAD^', cwd=repo) == first}")

    print("4. Identical contents are stored once, whatever the file is called")
    count = lambda: git("count-objects", "-v", cwd=repo).splitlines()[0].split()[1]
    before = count()
    (repo / "src" / "copy.py").write_text("print('shop')\n"); git("add", ".", cwd=repo)
    print(f"   objects stored before adding src/copy.py, a copy of app.py: {before}; after: {count()}")
    print(f"   both names point to blob {git('rev-parse', ':src/copy.py', cwd=repo)[:10]}"
          f" = {git('rev-parse', ':src/app.py', cwd=repo)[:10]}")
    kinds = git("cat-file", "--batch-all-objects", "--batch-check=%(objecttype)", cwd=repo).split()
    tally = ", ".join(f"{kinds.count(k)} {k}s" for k in ("blob", "tree", "commit"))
    print(f"   objects in the repository: {tally}")
