    <section class="chapter prose" id="ch08" data-ch="08">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 8</span><label class="done-toggle"><input type="checkbox" data-id="ch08"><span class="box"></span>Read</label></div>
        <h3>Dotfiles</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Your tools read their settings from small text files in your home folder, named with a leading dot so they stay out of the way. Kept in a Git repository, with a script that links each one into place, they turn setting up a new laptop from a lost day into ten minutes, and they're the first half of this stage's deliverable. The script has to be safe to run twice, must never destroy what's already there, and the repository, which you'll make public, must never contain a secret.</p>
      </header>

      <h4>What dotfiles are</h4>
      <p>Each program decides where it looks for its settings, and most look in your home folder: <code>~/.zshrc</code> and <code>~/.bashrc</code> for the shells, <code>~/.gitconfig</code> for Git, <code>~/.vimrc</code> for Vim, <code>~/.ssh/config</code> for SSH. Newer programs follow the <b>XDG</b> convention and keep their files under <code>~/.config</code>, so Git also reads <code>~/.config/git/config</code> and <code>~/.config/git/ignore</code>, and Neovim reads <code>~/.config/nvim</code>. A program's manual page lists its files, usually in a section called FILES, which is the place to look when you don't know where a setting lives.</p>

      <h4>What to put in them</h4>
      <p>Start small and grow the files by noticing. Each time you type something long twice, or fix the same annoyance again, add a line, with a comment saying why. A useful first set covers three files. In the shell's: a <code>PATH</code> that includes <code>~/.local/bin</code>, from chapter 7; <code>EDITOR</code>; a long history that's shared between terminals; a few aliases, such as <code>ll</code> for <code>ls -lah</code>; chapter 7's <code>proj</code> function; and a prompt that shows the current Git branch. In Git's: your name, <code>init.defaultBranch</code>, <code>pull.ff only</code>, and an alias like <code>lg = log --graph --oneline --all</code>, which you'll type a thousand times in Part III. In your editor's: whatever you've changed from its defaults. Reading other people's dotfiles on GitHub is a good source of ideas, and copying a stranger's five-hundred-line configuration whole is how you end up with a shell you can't explain.</p>

      <h4>A repository, and links into it</h4>
      <p>Keep the files in one folder, such as <code>~/dotfiles</code>, under Git, named without their dots so they're visible: <code>zshrc</code>, <code>gitconfig</code>. Then make the real locations <b>symbolic links</b> into the repository, as chapter 5 described. Every program reads the repository's file through its link, so editing <code>~/.zshrc</code> edits the tracked file, and <code>git diff</code> shows what you changed. Copying the files into place instead works once, and then the copies and the repository drift apart. An install script makes the links. Tools such as GNU Stow, chezmoi and yadm do the same job with more features. Write your own first, because it's twenty lines and you'll understand every one.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="On the left, the dotfiles repository, which is public: install.sh, zshrc, gitconfig, gitignore_global, and a .gitignore listing star.local. On the right, the home folder: .zshrc, .gitconfig and .config/git/ignore are symbolic links into the repository. The old .zshrc that was already there was moved to .dotfiles-backup, not deleted. .gitconfig.local, holding this machine's email address, is an ordinary file outside the repository, pulled in by an include line in gitconfig.">
          __SVG:fig08__
        </svg>
        <figcaption>The repository holds what you share; the home folder holds links to it, plus anything private to one machine, which the shared files include but never contain.</figcaption>
      </figure>
      <p>The example builds a small repository with an install script and three settings files, and a home folder that already has an old <code>.zshrc</code>. It installs twice, then checks the result the only way that matters: by asking Git what it now reads.</p>
      __EXAMPLE:ch08_dotfiles|dotfiles.py &middot; a dotfiles repository whose install script links each file into place, backing up what was there, run twice, then checked through git config, a global ignore file and the repository's own .gitignore__

      <h4>What the example shows</h4>
      <p><b>The script is safe to run any number of times.</b> On the first run it found a real file at <code>~/.zshrc</code>, moved it into <code>~/.dotfiles-backup</code> and linked the repository's version in its place. The second run found every link already pointing at the right file and changed nothing. That's the check <code>[ "$(readlink "$dst")" = "$src" ]</code>. <code>${2//\//_}</code> replaces each slash in a path with an underscore, so a backup of <code>.config/git/ignore</code> gets a flat, unambiguous name. And the first line, built from <code>BASH_SOURCE</code> and <code>pwd -P</code>, finds the repository's absolute location wherever the script is run from, which exercise 8.1 explains.</p>
      <p><b>Shared settings and private ones stay apart.</b> <code>git config --show-origin</code> showed the name coming from the linked <code>~/.gitconfig</code> and the email from <code>~/.gitconfig.local</code>, which the shared file pulls in with an <code>[include]</code> but which isn't in the repository. That's the pattern for anything that differs between machines or shouldn't be public: a work email, a signing key, a company's proxy. The shell's version is a last line in <code>zshrc</code>, <code>[ -f ~/.zshrc.local ] &amp;&amp; source ~/.zshrc.local</code>. The global ignore file kept <code>.DS_Store</code> out of a brand-new repository without any setup there. In the dotfiles repository itself, <code>*.local</code> in <code>.gitignore</code> kept a stray <code>secrets.local</code> out of the commit.</p>

      <h4>Secrets, and the README</h4>
      <p>A dotfiles repository is meant to be public, so treat everything in it as published. Never commit API tokens, passwords, private SSH keys, <code>~/.netrc</code> or a shell history; keep them in local files, as above, or in your system's keychain or a password manager. Before your first push, and from time to time after, search for anything that looks like a secret, with <code>git grep -iE 'token|secret|passw|api_?key'</code> or a scanner such as gitleaks. Bots search public repositories for keys within minutes of a push, so a leaked key has to be treated as stolen at once, which is what exercise 8.2 is about.</p>
      <p>Then write the <b>README</b> for a stranger who has just cloned it. Say what's in the repository and what each file configures. Give the one command that installs it, say exactly what that command changes and how to undo it, and list the systems you've tried it on. Your future self, setting up a new machine in a hurry, is the stranger.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>A token, key or private detail</b> committed to a public repository.</li>
          <li><b>Copying someone's entire configuration</b> instead of growing your own a line at a time.</li>
          <li><b>An install script that overwrites</b> existing files instead of backing them up.</li>
          <li><b>Links that store a relative path</b> that only works from one folder.</li>
          <li><b>Settings for one system only,</b> such as Homebrew's paths, applied unconditionally on another; check with <code>uname</code>.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 8.1</span><span class="ex-title">Run from anywhere</span></div>
          <p>The install script finds its repository with <code>repo=$(cd "$(dirname "${BASH_SOURCE[0]}")" &amp;&amp; pwd -P)</code>. What goes wrong with the simpler <code>repo=$(dirname "$0")</code>, run as <code>./install.sh</code> from inside the repository?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p><code>dirname "$0"</code> is the folder part of however the script was invoked: run as <code>./install.sh</code>, that's just <code>.</code>. The script then stores <code>./zshrc</code> in the link at <code>~/.zshrc</code>, and as chapter 5 explained, a relative link is read from the link's own folder, so it points at <code>~/zshrc</code>, which doesn't exist. Run that way in a test, the simple version printed <code>linked ~/.zshrc -&gt; zshrc</code> for every file, and every link it made was broken. The correct line moves into the script's folder, so the path doesn't depend on how it was invoked. It then asks for the absolute physical path, with symbolic links resolved: that's <code>pwd -P</code>. <code>BASH_SOURCE[0]</code> is the script's own path even when it's sourced, which <code>$0</code> isn't. The lesson is to check that a script's effects work, here with <code>[ -e ~/.zshrc ]</code>, not just that it ran without complaint.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 8.2</span><span class="ex-title">The token in the repository</span></div>
          <p>You notice that last week you pushed a <code>zshrc</code> containing <code>export GITHUB_TOKEN=ghp_...</code> to your public dotfiles repository. What do you do, in what order?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p><b>First, revoke the token</b>, on GitHub's settings page, and make a new one. Assume it was copied within minutes of the push: bots watch public pushes for exactly this, and nothing you do to the repository can recall a copy. Second, check what the token could reach for anything done with it. Only then clean up. Move the token to a local file such as <code>~/.zshrc.local</code> that the repository ignores. Then remove it from history with <code>git filter-repo --replace-text</code>, which rewrites every commit that contained it, and force-push. Rewriting history is tidy but not protection: forks, clones and caches keep the old commits, which is why revoking comes first. GitHub's secret scanning and push protection catch many token formats, including GitHub's own, before or just after they're pushed. They're worth turning on, and no reason to rely on luck.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 8.3</span><span class="ex-title">An uninstall</span></div>
          <p>Write <code>uninstall.sh</code>, which removes only the links that point into the repository, and puts back anything <code>install.sh</code> backed up.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">#!/usr/bin/env bash
# uninstall.sh: remove the links install.sh made, and put back what it backed up.
set -euo pipefail
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
backup="$HOME/.dotfiles-backup"
unlink_one() {   # unlink_one FILE-IN-REPO PATH-UNDER-HOME
  local src="$repo/$1" dst="$HOME/$2" saved="$backup/${2//\//_}"
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    rm -- "$dst"; echo "removed     ~/$2"
  else
    echo "left alone  ~/$2 (not our link)"; return
  fi
  if [ -e "$saved" ] || [ -L "$saved" ]; then mv -- "$saved" "$dst"; echo "restored    ~/$2"; fi
}
unlink_one zshrc .zshrc
unlink_one gitconfig .gitconfig
unlink_one gitignore_global .config/git/ignore</code></pre>
            <p>It uses the same test as <code>install.sh</code>, so it only removes a link that is exactly the one the installer made. Anything else at that path, including a file someone put there since, is left alone and reported. Tested after an install, with <code>~/.gitconfig</code> then replaced by an ordinary file, it removed the two links, restored the original <code>~/.zshrc</code> from the backup, and left <code>~/.gitconfig</code> untouched. Sharing the list of files between the two scripts, for example in a file both read, would stop them drifting apart as the repository grows.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you find where a program reads its settings, using its manual page?</li>
            <li>Can you keep your dotfiles in a repository and link them into place?</li>
            <li>Can you write an install script that backs up, never overwrites, and is safe to rerun?</li>
            <li>Can you keep per-machine and secret settings out of the repository, and include them anyway?</li>
            <li>Can you say what to do, in order, when a secret has been pushed?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Guide</span><div><a href="https://dotfiles.github.io/">Your unofficial guide to dotfiles on GitHub</a> <span class="by">dotfiles.github.io</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://specifications.freedesktop.org/basedir-spec/latest/">XDG Base Directory Specification</a> <span class="by">freedesktop.org</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning">About secret scanning</a> <span class="by">GitHub Docs</span></div></li>
          </ul>
        </div>
      </div>
    </section>
