# A hostile environment for running examples: another hash seed, temp folder and time zone, and a
# HOME whose git and shell settings would change the output of any example that doesn't isolate itself.
import os

def hostile_env(root):
    home = root / "home"; home.mkdir()
    (home / ".gitconfig").write_text("[init]\n\tdefaultBranch = trunk\n[user]\n\tname = Somebody Else\n"
                                     "\temail = else@example.org\n[color]\n\tui = always\n[core]\n\tpager = cat\n"
                                     "[commit]\n\tgpgsign = false\n[advice]\n\tdetachedHead = true\n")
    (home / ".bashrc").write_text('echo "bashrc ran" >&2\nalias ls="ls -F"\n')
    benv = root / "bash_env.sh"; benv.write_text('echo "BASH_ENV ran"\n')
    tmp = root / "tmp with space"; tmp.mkdir()
    env = dict(os.environ, HOME=str(home), TMPDIR=str(tmp), TZ="Asia/Kolkata", PYTHONHASHSEED="4242",
               CDPATH="/", BASH_ENV=str(benv), GREP_COLOR="1;32", COLUMNS="37", LINES="5", EDITOR="false",
               GIT_PAGER="cat", PAGER="cat", LESS="-R")
    return env
