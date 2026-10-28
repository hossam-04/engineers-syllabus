    <section class="chapter prose" id="ch04" data-ch="04">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 4</span><label class="done-toggle"><input type="checkbox" data-id="ch04"><span class="box"></span>Read</label></div>
        <h3>Scripts that don't break</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">A shell script is the cheapest automation there is: the commands you'd type, saved in a file. It's also the easiest to get dangerously wrong, because the shell carries on after errors, splits what it shouldn't and deletes what it's told. A handful of habits make the difference. Stop at the first failure, check the arguments, show what you'd do before doing it, never overwrite or delete without checking, clean up however the script ends, and make it safe to run twice. This chapter writes the kind of script the stage asks for, one that tidies a downloads folder, and puts it through its paces.</p>
      </header>

      <h4>A script is a file of commands</h4>
      <p>A script starts with a <b>shebang</b> line, <code>#!/usr/bin/env bash</code>, which tells the system which program runs the file. <code>env</code> finds <code>bash</code> on your <code>PATH</code>, which matters on a Mac. Its <code>/bin/bash</code> is version 3.2, first released in 2006, kept because later versions use a licence Apple won't ship, so a newer bash, if you install one, lives elsewhere. Make the file executable with <code>chmod +x tidy</code>, and run it as <code>./tidy</code>, or put it in a folder on your <code>PATH</code>, such as <code>~/.local/bin</code>, and run it by name. <code>bash tidy</code> works without the execute bit, because then bash only reads the file.</p>
      <p>Inside, <code>$1</code>, <code>$2</code> and so on are the arguments, <code>$#</code> is how many there are, and <code>"$@"</code> is all of them, each kept as a separate word: it's the only correct way to pass a script's arguments on to another command. <code>shift</code> drops the first. For options, the built-in <code>getopts</code> handles <code>-n</code>, combined flags like <code>-nv</code> and options with values. A <b>function</b> is a named group of commands, <code>name() { ...; }</code>, called like any command, with its own <code>$1</code> and so on. A function's <code>return</code> sets its exit status, like a program's. To give back a value, it prints it, and the caller captures it with <code>$(name args)</code>. <code>local</code> keeps a variable inside the function instead of overwriting one outside.</p>

      <h4>Strict mode</h4>
      <p>Put <code>set -euo pipefail</code> near the top of every script. <code>-e</code> exits at the first command that fails, with the exceptions chapter 2 listed, instead of carrying on with the next line. <code>-u</code> makes using an unset variable an error, which turns a typo like <code>$flie</code>, or chapter 1's empty <code>$STEAMROOT</code>, into a stop instead of an empty string. <code>pipefail</code> makes a pipeline fail when any part of it does. Together they mean a script that hits something unexpected stops, and stopping is almost always the right thing for a script that runs without anyone watching. When you expect a command might fail, say so explicitly, with <code>|| true</code> or an <code>if</code>. And <code>${1:-}</code> reads a possibly missing argument without upsetting <code>-u</code>.</p>

      <h4>Failing well, and never destroying data</h4>
      <p>A script should fail the way a good program does. Messages go to stderr, with <code>&gt;&amp;2</code>, so they don't mix with output. Wrong usage prints a usage line and exits with status 2. Any other failure exits non-zero with a message that names the problem and the value that caused it: <code>tidy: no such folder: Nowhere</code>, not <code>error</code>. Check everything the script relies on before it starts changing things.</p>
      <p>Then make destruction hard. Offer a <b>dry run</b> that prints what would happen, and use it first. Move rather than delete, and never overwrite: <code>mv -n</code> refuses to replace an existing file, and choosing a free name first, as the example's <code>free_name</code> does, means the refusal never comes up. Write new files under a temporary name and rename them into place only when complete, so nothing ever sees half a file. Before anything like <code>rm -rf "$dir"</code>, check that <code>$dir</code> is set, exists and is what you think it is. Finally, make the script <b>idempotent</b>, safe to run any number of times. Run twice, it should find nothing left to do rather than doing it all again or failing halfway.</p>

      <h4>Locks and cleanup</h4>
      <p>Two copies of a script working on the same files at once, perhaps from a timer and from you, will trip over each other. A lock prevents it, and <code>mkdir</code> makes a good one. Creating a folder either succeeds or fails, in one indivisible step, so exactly one copy can create <code>.tidy.lock</code> and the others see that it exists. The lock must be removed however the script ends, and that's what <code>trap</code> is for. <code>trap 'rmdir "$lock"' EXIT</code> runs its command when the script exits: normally, through <code>set -e</code> after an error, or after Ctrl-C. Only <code>kill -9</code>, which nothing can catch, skips it. The same pattern deletes temporary files made with <code>mktemp</code>.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 310" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The path through the tidy script. Check the arguments: wrong, print the usage line and exit with status 2. Check the folder exists: missing, print an error and exit 1. Take the lock with mkdir: already held, exit 1. Set the trap to remove the lock on exit. For each file at the top of the folder, choose a category and a free name, then print the plan in a dry run or move the file. At the end, exit 0, and the trap removes the lock, as it would after an error or Ctrl-C.">
          __SVG:fig04__
        </svg>
        <figcaption>Check first, then change. Every way out before the lock leaves nothing behind; every way out after it passes through the trap.</figcaption>
      </figure>
      <p>The example writes <code>tidy</code>, a script that sorts the files at the top of a folder into <code>images</code>, <code>documents</code>, <code>archives</code> and <code>other</code> by their extension. Then it runs it on a downloads folder in every way that matters: wrongly, as a dry run, for real, a second time, on a missing folder, and while another run holds the lock. The script is written for bash 3.2, so it runs unchanged on a Mac and on Linux.</p>
      __EXAMPLE:ch04_script|script.py &middot; a script that tidies a downloads folder, with strict mode, getopts, a dry run, no overwriting, a mkdir lock and a trap, run seven ways__

      <h4>What the example shows</h4>
      <p><b>It stops before doing harm.</b> With no folder, it printed its usage line to stderr and exited with status 2; with a missing folder, a precise message and status 1; with the lock already taken, it refused rather than racing the other run. None of those runs changed anything, because every check comes before the first move. <code>${1%/}</code> removes a trailing slash, so <code>tidy Downloads/</code> works too: the shell's Tab completion adds that slash, so users will type it.</p>
      <p><b>The plan and the run agree, and nothing is lost.</b> The dry run printed exactly the seven moves the real run then made. The report that was already in <code>documents</code> kept its name, and the new one became <code>report (1).pdf</code>. The subfolder <code>projects</code> was skipped because the loop only moves plain files. The order, capital letters first, is the C locale's byte order, the same everywhere. A second run found nothing to tidy, and no lock was left behind. Category names come from a <code>case</code> statement rather than an associative array, because those need bash 4.</p>

      <h4>Testing a script, and knowing when to stop</h4>
      <p>Test scripts like any program. <code>bash -n script</code> checks the syntax without running anything, and <code>bash -x script</code> traces every command, as chapter 1's <code>set -x</code> does. <b>ShellCheck</b> reads a script and points out unquoted variables, useless <code>cat</code>s, <code>cd</code>s without error handling and dozens of other known mistakes. Run it on everything you write. Tests can be shell scripts too, with a framework such as bats, or a Python program like the example, which builds a folder, runs the script and checks the result.</p>
      <p>Shell is the right language for gluing programs together and the wrong one for nearly everything else. Google's style guide for shell puts the line at about a hundred lines, or any non-trivial control flow. Past that point, or once you need data structures, arithmetic on anything but whole numbers, JSON, or careful error handling, rewrite it in Python: its <code>subprocess</code>, <code>pathlib</code> and <code>shutil</code> modules do everything a script does, without the quoting.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>No <code>set -u</code>,</b> so a misspelt variable silently expands to nothing.</li>
          <li><b><code>cd somewhere</code> without <code>|| exit</code>,</b> so the rest of the script runs in the wrong folder.</li>
          <li><b>Parsing the output of <code>ls</code></b> instead of looping over a glob.</li>
          <li><b>Results and messages on the same stream,</b> so another program can't use the results.</li>
          <li><b>Bash 4 features,</b> like associative arrays and <code>${x,,}</code>, in a script that must run on a Mac's bash 3.2.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 4.1</span><span class="ex-title">An undo</span></div>
          <p>Make <code>tidy</code> keep a record of its moves, and write <code>untidy FOLDER</code>, which puts every file back where it came from, newest move first.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash"># in tidy, after the mv:
printf '%s\t%s\n' "$dest/$target" "$name" >> "$folder/.tidy-log"

#!/usr/bin/env bash
# untidy: undo tidy's moves in FOLDER, newest first, using the log tidy kept.
set -euo pipefail
folder=${1:?usage: untidy FOLDER}
log="$folder/.tidy-log"
[ -f "$log" ] || { echo "untidy: nothing to undo in $folder" >&2; exit 1; }
awk '{ line[NR] = $0 } END { for (i = NR; i > 0; i--) print line[i] }' "$log" |
while IFS=$'\t' read -r moved original; do
  mv -n -- "$folder/$moved" "$folder/$original" && echo "restored: $original"
done
rm -- "$log"</code></pre>
            <p>Each line of the log holds the new and old names, separated by a tab, which file names almost never contain. The <code>awk</code> program reverses the lines, because GNU's <code>tac</code> and BSD's <code>tail -r</code> each exist on only one system. Undoing newest first matters when one name was used twice. <code>IFS=$'\t' read -r</code> splits each line at the tab only, and <code>-r</code> keeps backslashes as they are. Run on a folder with three files, <code>tidy</code> moved them, <code>untidy</code> restored all three, and a second <code>untidy</code> said there was nothing to undo. The empty <code>images</code> and <code>documents</code> folders stay behind; removing them only if they're empty, with <code>rmdir</code>, would be a careful improvement. A name containing a newline would still break the log, which is the honest limit of line-based records.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 4.2</span><span class="ex-title">Find the bugs</span></div>
          <p>List everything wrong with this script, which compresses old logs, and rewrite it.</p>
          <pre><code class="language-bash">#!/bin/bash
backup_dir=$1
cd $backup_dir
for f in $(ls *.log); do
  gzip $f
done
rm -rf $backup_dir/old/*
echo "done"</code></pre>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">#!/usr/bin/env bash
set -euo pipefail
[ "$#" -eq 1 ] || { echo "usage: compress-logs FOLDER" >&2; exit 2; }
backup_dir=$1
[ -d "$backup_dir/old" ] || { echo "compress-logs: no old/ in $backup_dir" >&2; exit 1; }
cd -- "$backup_dir"
for f in *.log; do
  [ -e "$f" ] || continue
  gzip -- "$f"
done
find old -mindepth 1 -delete      # empty old/, here and only here
echo "done" >&2</code></pre>
            <p>The original has no strict mode, so it carries on after any failure. With no argument, <code>backup_dir</code> is empty and <code>cd $backup_dir</code> goes to your home folder; with a missing folder, <code>cd</code> fails and the script continues in whatever folder it was started from. <code>$(ls *.log)</code> splits names at spaces, and the unquoted <code>$f</code> splits them again. Worst, with an empty <code>backup_dir</code>, the <code>rm</code> line becomes <code>rm -rf /old/*</code>, and with a relative path like <code>logs</code> it points at <code>logs/old</code> <i>inside</i> the folder it has already moved into. The rewrite checks its argument and the folder before changing anything, uses paths relative to the folder it has entered, quotes everything, and deletes with <code>find old -mindepth 1 -delete</code>, which can only touch <code>old</code>'s contents. The message goes to stderr, and in a script run by a timer it could be dropped entirely.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 4.3</span><span class="ex-title">Shell or Python?</span></div>
          <p>For each task, decide whether to write a shell script or a Python program, and say why: (a) run the tests, then the linter, and deploy only if both pass; (b) rename photos to the date they were taken, read from inside each file; (c) call a web API every hour, retry when it fails, and save one field of the JSON reply.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p><b>(a) Shell.</b> It's pure glue: three programs in order, each decision made by an exit status. <code>set -euo pipefail</code> followed by the three commands, each on its own line, is the whole script, and anything else would be longer. <b>(b) Python.</b> The date is inside the image's metadata, which needs a library to read, and the renaming needs care with collisions and time zones that shell makes awkward. Shell could call a tool like <code>exiftool</code>, but by the time it handles a missing date and two photos taken in the same second, it's past the point where shell is clear. <b>(c) Python</b>, using the standard library's <code>urllib</code> and <code>json</code>, or <code>requests</code>. Retrying with a delay that grows, telling a timeout from an error, and reading JSON are all things shell does badly. <code>curl</code> and <code>jq</code> can do a simple version, but error handling is where the shell version always grows a hundred lines. The rule: when you find yourself fighting the shell's quoting or reaching for its arrays, switch.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you write a script with a shebang, strict mode, a usage message and <code>getopts</code>?</li>
            <li>Can you pass arguments on correctly with <code>"$@"</code>, and return values from functions?</li>
            <li>Can you add a dry run, avoid overwriting files, and make a script safe to run twice?</li>
            <li>Can you take a lock with <code>mkdir</code> and clean up with <code>trap ... EXIT</code>?</li>
            <li>Can you check a script with ShellCheck, <code>bash -n</code> and <code>bash -x</code>, and say when to switch to Python?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Tool</span><div><a href="https://www.shellcheck.net/">ShellCheck: finds bugs in your shell scripts</a> <span class="by">Vidar Holen</span></div></li>
            <li><span class="rkind free">Guide</span><div><a href="https://google.github.io/styleguide/shellguide.html">Shell Style Guide</a> <span class="by">Google</span></div></li>
            <li><span class="rkind free">Wiki</span><div><a href="https://mywiki.wooledge.org/BashGuide">The Bash Guide</a> <span class="by">Greg's Wiki</span></div></li>
          </ul>
        </div>
      </div>
    </section>
