import os, pathlib, shutil, subprocess, tempfile

def sh(cmd, cwd, env, args=()):
    r = subprocess.run([shutil.which("bash"), "--norc", "--noprofile", *args, "-c", cmd], cwd=cwd, env=env,
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return r.stdout.replace(str(cwd), "$DEMO").rstrip("\n"), r.returncode

def show(cmd, cwd, env, args=()):
    out, status = sh(cmd, cwd, env, args)
    first, *rest = cmd.splitlines()
    print(f"   $ {first}" + "".join(f"\n   > {line}" for line in rest))
    for line in out.splitlines(): print(f"     {line}")
    if status: print(f"     (exit status {status}" + (": command not found)" if status == 127 else ")"))

with tempfile.TemporaryDirectory() as tmp:
    demo = pathlib.Path(tmp).resolve()
    for folder, text in (("bin1", "greet from bin1"), ("bin2", "greet from bin2")):
        (demo / folder).mkdir(); tool = demo / folder / "greet"
        tool.write_text(f"#!/bin/sh\necho '{text}'\n"); tool.chmod(0o755)
    (demo / "sub").mkdir()
    (demo / "setup.sh").write_text('export GREETING=hello\ncd sub\n')
    base = {"PATH": os.environ["PATH"], "HOME": "/home/learner", "LC_ALL": "C"}
    print("($DEMO stands for the example's temporary folder)")

    print("1. PATH is a list of folders; the shell runs the first matching program it finds")
    show('PATH="$DEMO/bin1:$DEMO/bin2:$PATH"; greet', demo, dict(base, DEMO=str(demo)))
    show('PATH="$DEMO/bin2:$DEMO/bin1:$PATH"; greet; type -a greet', demo, dict(base, DEMO=str(demo)))
    show("greet", demo, base)
    show("type cd export greet", demo, dict(base, PATH=f"{demo}/bin1:{base['PATH']}"))

    print("2. A child process gets a copy of the exported variables; changes never flow back up")
    show('x=1; bash -c \'echo "child sees x=[$x]"\'', demo, base)
    show('export x=1; bash -c \'echo "child sees x=[$x]"\'', demo, base)
    show('x=2 bash -c \'echo "child sees x=[$x]"\'; echo "the shell still has x=[$x]"', demo, base)
    show("export x=1; bash -c 'x=99; cd /'; echo \"x=$x, still in $PWD\"", demo, base)

    print("3. Running a script starts a child; sourcing it runs its lines in this shell")
    show('bash setup.sh; echo "GREETING=[$GREETING], in $PWD"', demo, base)
    show('. ./setup.sh; echo "GREETING=[$GREETING], in $PWD"', demo, base)

    print("4. Which startup files bash reads depends on how it was started")
    home = demo / "home"; home.mkdir()
    for name in (".bash_profile", ".bashrc", ".profile"):
        (home / name).write_text(f"echo '   (bash read ~/{name})'\n")
    env = dict(base, HOME=str(home))
    for label, args in (("a script: neither login nor interactive", []),
                        ("a login shell (bash -l)", ["-l"]), ("an interactive shell (bash -i)", ["-i"]),
                        ("an interactive login shell, like a new terminal on macOS", ["-l", "-i"])):
        out = subprocess.run([shutil.which("bash"), *args, "-c", "true"], env=env, cwd=demo,
                             capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
        print(f"   {label}:\n{out.rstrip() or '   (no startup files)'}")
