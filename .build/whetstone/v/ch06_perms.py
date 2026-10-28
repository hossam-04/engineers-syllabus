import os, pathlib, shutil, stat, subprocess, tempfile

if os.geteuid() == 0:
    raise SystemExit("Run this as an ordinary user: root may do almost anything, whatever the bits say.")

def sh(cmd, cwd):
    r = subprocess.run([shutil.which("bash"), "--norc", "--noprofile", "-c", cmd], cwd=cwd,
                       env={"PATH": os.environ["PATH"], "LC_ALL": "C"}, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()

def mode(p): return stat.filemode(os.lstat(p).st_mode)

def attempt(what, cmd, cwd):
    status, out = sh(cmd, cwd)
    if status: result = f"refused (status {status})"
    else: result = "allowed" + (f", printed {out!r}" if out else "")
    print(f"   {what:42} {result}")

print("1. Nine bits: read, write, execute, for the owner, the group, and everyone else")
for bits in (0o644, 0o755, 0o600, 0o750, 0o400):
    who = [stat.filemode(stat.S_IFREG | bits)[i:i + 3] for i in (1, 4, 7)]
    print(f"   {bits:o}  {stat.filemode(stat.S_IFREG | bits)}   "
          f"owner {who[0]}  group {who[1]}  others {who[2]}")

with tempfile.TemporaryDirectory() as tmp:
    d = pathlib.Path(tmp)
    print("2. chmod sets bits by number or by name; umask removes bits from everything you create")
    (d / "plan.txt").write_text("plan\n"); os.chmod(d / "plan.txt", 0o644)
    for change in ("u+x", "go-r", "a+r", "640"):
        sh(f"chmod {change} plan.txt", d)
        print(f"   chmod {change:5} plan.txt   now {mode(d / 'plan.txt')}")
    sh("umask 022; touch a.txt; mkdir a-dir; umask 077; touch b.txt; mkdir b-dir", d)
    for name in ("a.txt", "a-dir", "b.txt", "b-dir"):
        print(f"   created with umask {'022' if name[0] == 'a' else '077'}: {name:6} {mode(d / name)}")

    print("3. On a file, r lets you read it, w lets you change it, x lets you run it")
    (d / "secret.txt").write_text("42\n"); os.chmod(d / "secret.txt", 0o200)
    attempt("cat secret.txt  (mode --w-------)", "cat secret.txt", d)
    (d / "fixed.txt").write_text("v1\n"); os.chmod(d / "fixed.txt", 0o444)
    attempt("append to fixed.txt  (mode r--r--r--)", "echo v2 >> fixed.txt", d)
    (d / "hello.sh").write_text("echo hello from the script\n"); os.chmod(d / "hello.sh", 0o644)
    attempt("./hello.sh  (mode rw-r--r--)", "./hello.sh", d)
    attempt("bash hello.sh  (bash only reads it)", "bash hello.sh", d)

    print("4. On a folder, r lets you list names, w lets you add and remove names, x lets you go in")
    box = d / "box"; box.mkdir(); (box / "note.txt").write_text("inside\n")
    os.chmod(box, 0o600)
    attempt("echo box/*  (mode rw-------: no x)", "echo box/*", d)
    attempt("cat box/note.txt", "cat box/note.txt", d)
    os.chmod(box, 0o300)
    attempt("ls box  (mode -wx------: no r)", "ls box", d)
    attempt("cat box/note.txt, knowing the name", "cat box/note.txt", d)
    os.chmod(box, 0o500)
    attempt("rm box/note.txt  (mode r-x------: no w)", "rm -f box/note.txt", d)
    os.chmod(box, 0o700)
    attempt("rm fixed.txt  (r--r--r--, folder writable)", "rm -f fixed.txt", d)
    os.chmod(d / "secret.txt", 0o600)
