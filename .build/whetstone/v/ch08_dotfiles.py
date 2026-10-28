import os, pathlib, shutil, subprocess, tempfile

INSTALL = r'''#!/usr/bin/env bash
# install.sh: link each file in this repository to where its program looks for it. Safe to rerun.
set -euo pipefail
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
backup="$HOME/.dotfiles-backup"

link() {   # link() FILE-IN-REPO PATH-UNDER-HOME
  local src="$repo/$1" dst="$HOME/$2"
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    echo "ok          ~/$2"; return
  fi
  mkdir -p "$(dirname "$dst")"
  if [ -e "$dst" ] || [ -L "$dst" ]; then      # something else is there: keep it, never delete it
    mkdir -p "$backup"
    mv "$dst" "$backup/${2//\//_}"
    echo "backed up   ~/$2 to ~/.dotfiles-backup/${2//\//_}"
  fi
  ln -s "$src" "$dst"
  echo "linked      ~/$2 -> $1"
}

link zshrc .zshrc
link gitconfig .gitconfig
link gitignore_global .config/git/ignore
[ -e "$HOME/.gitconfig.local" ] || echo "note: put this machine's email in ~/.gitconfig.local"
'''
FILES = {
    "install.sh": INSTALL,
    "zshrc": 'export EDITOR=vim\nalias gs="git status --short"\n',
    "gitconfig": "[user]\n\tname = Ada Lovelace\n[include]\n\tpath = ~/.gitconfig.local\n"
                 "[init]\n\tdefaultBranch = main\n",
    "gitignore_global": ".DS_Store\n*.swp\n",
    ".gitignore": "*.local\n",
}

def sh(cmd, cwd, env):
    r = subprocess.run([shutil.which("bash"), "--norc", "--noprofile", "-c", cmd], cwd=cwd, env=env,
                       capture_output=True, text=True)
    print(f"$ {cmd}")
    for line in (r.stdout + r.stderr).replace(env["HOME"], "~").splitlines(): print(f"   {line}")

with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp).resolve()
    repo, home = root / "dotfiles", root / "home"; repo.mkdir(); home.mkdir()
    for name, text in FILES.items(): (repo / name).write_text(text)
    (repo / "install.sh").chmod(0o755)
    (home / ".zshrc").write_text("# the old settings this laptop came with\n")
    env = {"PATH": os.environ["PATH"], "HOME": str(home), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1"}

    print("1. The first run links everything, keeping a backup of what was already there")
    sh("dotfiles/install.sh", root, env)
    print("2. A second run changes nothing: running it again is always safe")
    sh("dotfiles/install.sh", root, env)
    for name in (".zshrc", ".gitconfig", ".config/git/ignore"):
        p = home / name
        print(f"   ~/{name:18} -> {pathlib.Path(os.readlink(p)).relative_to(root)}")
    print(f"   the old ~/.zshrc is kept: {(home / '.dotfiles-backup/.zshrc').read_text().strip()!r}")

    print("3. Git reads the linked config, and the include adds settings that never go in the repository")
    (home / ".gitconfig.local").write_text("[user]\n\temail = ada@example.org\n")
    sh("git config --show-origin --get user.name; git config --show-origin --get user.email", root, env)

    print("4. The global ignore file applies in every repository on this machine")
    sh("git init -q project && cd project && touch .DS_Store notes.md && git status --short", root, env)

    print("5. The repository's own .gitignore keeps per-machine files out of it")
    sh("cd dotfiles && git init -q && touch secrets.local && git add -A && git status --short", root, env)
