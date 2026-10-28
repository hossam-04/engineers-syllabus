import os, pathlib, shutil, subprocess, tempfile

# A tiny program that writes one line to each output stream and exits with the status it's given.
TALK = '#!/bin/sh\necho "to stdout"\necho "to stderr" >&2\nexit "${1:-0}"\n'

def show(script, cwd, env):
    """Run a script with bash and report where each piece of text ended up."""
    for f in cwd.glob("*.txt"): f.unlink()
    r = subprocess.run([shutil.which("bash"), "--norc", "--noprofile", "-c", script],
                       cwd=cwd, env=env, capture_output=True, text=True)
    first, *rest = script.splitlines()
    print(f"   $ {first}" + "".join(f"\n   > {line}" for line in rest))
    places = [("the terminal's stdout", r.stdout), ("the terminal's stderr", r.stderr)]
    places += [(f"file {f.name}", f.read_text()) for f in sorted(cwd.glob("*.txt"))]
    for place, text in places:
        if text: print(f"     {place + ':':24}" + " | ".join(text.splitlines()))
    if r.returncode: print(f"     {'the script exited with:':24}status {r.returncode}")

with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp); (root / "bin").mkdir(); (root / "work").mkdir()
    tool = root / "bin" / "talk"; tool.write_text(TALK); tool.chmod(0o755)
    env = {"PATH": f"{root / 'bin'}:{os.environ['PATH']}", "HOME": "/home/learner", "LC_ALL": "C"}
    work = root / "work"

    print("1. Every program starts with three streams: 0 stdin, 1 stdout, 2 stderr")
    for s in ["talk", "talk > out.txt", "talk 2> /dev/null"]: show(s, work, env)

    print("2. Redirections are applied left to right, and 2>&1 means 'make 2 point where 1 points now'")
    for s in ["talk > out.txt 2>&1", "talk 2>&1 > out.txt"]: show(s, work, env)

    print("3. A pipe connects stdout only; stderr goes around it unless you redirect it")
    for s in ["talk | tr a-z A-Z", "talk 2>&1 | tr a-z A-Z", "talk 2>&1 | tee all.txt | grep -c std"]:
        show(s, work, env)

    print("4. Every command exits with a status: 0 means success, anything else is a failure")
    for s in ['talk 3 2> /dev/null; echo "status $?"',
              "talk 3 > /dev/null 2>&1 && echo worked || echo failed",
              'if grep -q needle /dev/null; then echo found; else echo "not found, status $?"; fi']:
        show(s, work, env)

    print("5. A pipeline's status is its last command's, unless pipefail is set")
    for s in ['false | true; echo "status $?"', 'set -o pipefail; false | true; echo "status $?"',
              'false | true | talk 2 > /dev/null 2>&1; echo "statuses ${PIPESTATUS[*]}"',
              'yes | head -n 2; echo "statuses ${PIPESTATUS[*]}"']:
        show(s, work, env)

    print("6. set -e stops at the first failure, except inside a condition, however deep")
    for s in ['set -e; false; echo "never printed"',
              'set -e\ncheck() { false; echo "check carried on after false"; }\n'
              'check || echo "check failed"']:
        show(s, work, env)

    print("7. A here-document feeds lines to stdin; quoting the marker turns expansion off")
    for s in ["name=Ada\ncat <<EOF\nHello, $name\nEOF", "name=Ada\ncat <<'EOF'\nHello, $name\nEOF"]:
        show(s, work, env)
