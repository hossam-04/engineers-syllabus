import os, pathlib, posixpath, shutil, subprocess, tempfile

def sh(cmd, cwd):
    """Run a shell command; the rest of the example inspects what it did with Python's os module."""
    r = subprocess.run([shutil.which("bash"), "--norc", "--noprofile", "-c", cmd], cwd=cwd,
                       env={"PATH": os.environ["PATH"], "LC_ALL": "C"}, capture_output=True, text=True)
    print(f"$ {cmd}" + (f"   (exit status {r.returncode})" if r.returncode else ""))
    for line in r.stdout.splitlines(): print(f"   {line}")

def describe(d, *names):
    """For each name: what kind of entry it is, which inode it names, and how many names that inode has."""
    inodes = {}
    for name in names:
        p = d / name
        if p.is_symlink():
            target = os.readlink(p)
            state = "works" if p.exists() else "is broken: nothing at that path"
            print(f"   {name:12} symbolic link to {target!r}, which {state}")
        elif p.exists():
            st = p.stat(); label = inodes.setdefault(st.st_ino, chr(ord("A") + len(inodes)))
            print(f"   {name:12} file, inode {label}, {st.st_nlink} name(s), "
                  f"contains {p.read_text().strip()!r}")
        else:
            print(f"   {name:12} does not exist")

print("1. A path is directions through the tree; . is here, .. is one level up")
for cwd, path in [("/home/learner/project", "notes.txt"), ("/home/learner/project", "../data/./in.csv"),
                  ("/home/learner/project", "/etc/hosts"), ("/", "home/learner/../../tmp")]:
    print(f"   from {cwd:22} {path:24} is {posixpath.normpath(posixpath.join(cwd, path))}")

with tempfile.TemporaryDirectory() as tmp:
    d = pathlib.Path(tmp)
    print("2. A hard link is a second name for the same inode; a symbolic link is a file holding a path")
    sh("echo 'version 1' > notes.txt; ln notes.txt hard.txt; ln -s notes.txt soft.txt", d)
    describe(d, "notes.txt", "hard.txt", "soft.txt")
    sh("echo 'version 2' > hard.txt", d)
    describe(d, "notes.txt", "soft.txt")

    print("3. Renaming changes a name, not the file; symbolic links follow names, so they can break")
    sh("mv notes.txt renamed.txt", d)
    describe(d, "renamed.txt", "hard.txt", "soft.txt")
    sh("rm renamed.txt", d)
    describe(d, "hard.txt", "soft.txt")

    print("4. A relative link is resolved from the folder the link is in, not from where you made it")
    (d / "dotfiles").mkdir(); (d / "home").mkdir(); (d / "dotfiles" / "zshrc").write_text("# my settings\n")
    sh("ln -s dotfiles/zshrc home/.zshrc; ln -s ../dotfiles/zshrc home/.zshrc-fixed", d)
    describe(d / "home", ".zshrc", ".zshrc-fixed")

    print("5. Deleting removes a name; the data is freed only when no name and no open file refers to it")
    log = open(d / "big.log", "w"); log.write("x" * 1_000_000); log.flush()
    sh("rm big.log; ls big.log 2> /dev/null || echo 'no such name any more'", d)
    st = os.fstat(log.fileno())
    print(f"   but the program that opened it still has it: {st.st_size:,} bytes, {st.st_nlink} names")
    log.close()
