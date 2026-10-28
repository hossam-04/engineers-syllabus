import os, pathlib, re, shutil, subprocess, tempfile

# A tiny program that prints the arguments it receives, each in brackets so spaces are visible.
SHOWARGS = '#!/bin/sh\nprintf "%d argument(s):" "$#"\nfor a in "$@"; do printf " [%s]" "$a"; done\necho\n'

def bash(line, cwd, env):
    """Run one line with bash, after a fixed prelude, and return what it printed."""
    prelude = 'f="my notes.txt"; empty=""\n'
    r = subprocess.run([shutil.which("bash"), "--norc", "--noprofile", "-c", prelude + line],
                       cwd=cwd, env=env, capture_output=True, text=True)
    if r.returncode:
        why = re.search(r"([^:\n]+: command not found)", r.stderr)
        return f"exit status {r.returncode}" + (f': "{why.group(1).strip()}"' if why else "")
    return r.stdout.rstrip("\n")

with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp)
    (root / "bin").mkdir(); (root / "demo").mkdir()
    tool = root / "bin" / "showargs"; tool.write_text(SHOWARGS); tool.chmod(0o755)
    for name in ("a.txt", "b c.txt", "notes.md"): (root / "demo" / name).write_text("")
    env = {"PATH": f"{root / 'bin'}:{os.environ['PATH']}", "HOME": "/home/learner", "LC_ALL": "C"}

    groups = {
        "1. The shell splits a line into words at unquoted spaces; quotes keep spaces in": [
            "showargs hello   world", 'showargs "hello   world"',
            "showargs it\\'s \"say \\\"hi\\\"\" 'a\\nb'"],
        "2. $name is replaced, then split again unless it's in double quotes": [
            "showargs $f", 'showargs "$f"', "showargs $empty", 'showargs "$empty"',
            "showargs 'single $HOME' \"double $HOME\""],
        "3. Globs are matched against file names; a glob that matches nothing is left alone": [
            "showargs *.txt", "showargs *.csv", 'showargs "*.txt"'],
        "4. Other expansions: tilde, braces, arithmetic, command substitution": [
            'showargs ~/notes "~/notes"', "showargs file{1..3}.log {red,green}-pen",
            "showargs $((2 + 3 * 4))",
            "showargs $(printf 'one   two')", 'showargs "$(printf \'one   two\')"'],
        "5. The order matters: a substitution's result is split and then globbed": [
            "showargs $(printf '*.txt')"],
        "6. Spaces around = make it a command, not an assignment": [
            "x = 5", 'x=5 y="a b"; showargs $x "$y"'],
    }
    for title, lines in groups.items():
        print(title)
        for line in lines:
            print(f"   $ {line}\n     {bash(line, root / 'demo', env)}")

    print("7. Without a shell there is no expansion: the program gets the list exactly as given")
    r = subprocess.run([str(tool), "*.txt", "my notes.txt", "$HOME"], cwd=root / "demo",
                       env=env, capture_output=True, text=True)
    print(f"   subprocess.run(['showargs', '*.txt', 'my notes.txt', '$HOME'])\n     {r.stdout.strip()}")
