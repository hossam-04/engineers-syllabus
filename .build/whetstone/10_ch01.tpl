    <div class="part" id="part1">
      <span class="part-num">Part I</span>
      <h2>The shell</h2>
      <p>Four chapters on the program you'll type into for the rest of your career. The shell is a small programming language whose real job is starting other programs and connecting them together. First, how it turns a line you type into a list of arguments, which explains almost every quoting bug. Then the streams and exit codes that let programs cooperate, the four tools that answer most questions about text, and the habits that make a shell script safe to run while you sleep. By the end of this part you can automate a chore and trust the result.</p>
    </div>

    <section class="chapter prose" id="ch01" data-ch="01">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 1</span><label class="done-toggle"><input type="checkbox" data-id="ch01"><span class="box"></span>Read</label></div>
        <h3>The shell as a language</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">The shell is a programming language whose main job is starting other programs. Before it runs a line, it rewrites it: it replaces variables, expands patterns into file names, splits the result into words, and only then hands the program a list of arguments. The program never sees your quotes, your <code>$</code> signs or your <code>*</code>. Almost every surprise in the shell is a surprise about that rewriting, so this chapter shows exactly which list a program receives for each kind of line.</p>
      </header>

      <h4>A command is a list of words</h4>
      <p>Three things are easy to confuse. The <b>terminal</b> is the window: it draws characters and sends your key presses on. The <b>shell</b> is the program running inside it, usually bash or zsh, which reads each line you type and decides what to do with it. And the <b>commands</b> are ordinary programs, <code>ls</code>, <code>grep</code>, <code>git</code>, which the shell starts. When you type <code>ls -l Documents</code>, the shell finds a program called <code>ls</code>, which chapter 7 explains, and starts it with a list of three strings: <code>ls</code>, <code>-l</code> and <code>Documents</code>. That list, called <code>argv</code> in C and <code>sys.argv</code> in Python, is everything the program gets from the line. What <code>-l</code> means is entirely up to <code>ls</code>.</p>
      <p>Programs mostly follow the same conventions for their arguments. Single letters after one dash are options, and can often be combined: <code>ls -l -a</code> is <code>ls -la</code>. Long names take two dashes, as in <code>ls --all</code>. Some options take a value, like <code>head -n 5</code>, and a lone <code>--</code> means "no more options", so <code>rm -- -notes.txt</code> deletes a file whose name begins with a dash. These are conventions, not rules the shell enforces. The shell's own job ends at producing the list.</p>

      <h4>Quoting</h4>
      <p>The shell gives special meaning to a few characters: spaces separate words, <code>$</code> starts a variable or substitution, <code>*</code>, <code>?</code> and <code>[</code> make patterns, and <code>|</code>, <code>&gt;</code>, <code>&lt;</code>, <code>&amp;</code> and <code>;</code> connect or separate commands. Quoting turns those meanings off. Inside <b>single quotes</b>, everything is literal: <code>'$HOME *'</code> is exactly those seven characters. Inside <b>double quotes</b>, spaces and pattern characters are literal, but <code>$</code>, backquotes and backslash still work, so <code>"$HOME"</code> becomes your home folder as one word, however many spaces it contains. A <b>backslash</b> outside quotes makes the next character literal: <code>it\'s</code>. Quotes can be mixed within one word: <code>'single'"double"</code> is one argument, <code>singledouble</code>. The quotes themselves are removed before the program starts, which is why it never sees them.</p>

      <h4>The expansions, in order</h4>
      <p>Before running a line, bash performs a fixed sequence of <b>expansions</b>, and the order explains the surprises. <b>Brace expansion</b> comes first, turning <code>file{1..3}.log</code> into three words. <b>Tilde expansion</b> turns <code>~</code> at the start of a word into your home folder. Then, from left to right, <b>parameter expansion</b> replaces <code>$name</code> and <code>${name}</code> with variables' values, <b>arithmetic expansion</b> computes <code>$((2 + 3 * 4))</code>, and <b>command substitution</b> runs <code>$(command)</code> and puts its output in its place. Only then does <b>word splitting</b> break the results of those three, wherever they weren't in double quotes, at spaces, tabs and newlines. <b>Pathname expansion</b>, usually called globbing, then replaces each word containing <code>*</code>, <code>?</code> or <code>[</code> with the matching file names. Finally, <b>quote removal</b> deletes the quotes.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The line showargs dollar-f star.txt, where f is set to my notes.txt and the folder holds a.txt and b c.txt, passing through the shell's stages. After parameter expansion it reads showargs my notes.txt star.txt. Word splitting breaks it into four words: showargs, my, notes.txt, star.txt. Globbing replaces star.txt with the two matching names, a.txt and b c.txt, which are not split again. Quote removal leaves the final list of five strings handed to the program: showargs, my, notes.txt, a.txt, b c.txt.">
          __SVG:fig01__
        </svg>
        <figcaption>One line, stage by stage. The unquoted <code>$f</code> is split after it's expanded, but file names found by a glob never are: the space in <code>b c.txt</code> survives.</figcaption>
      </figure>
      <p>The best way to learn this is to watch it. The example creates a tiny program, <code>showargs</code>, which prints its arguments one per bracket, so you can see exactly where each word begins and ends. It then runs it through bash in a folder holding <code>a.txt</code>, <code>b c.txt</code> and <code>notes.md</code>, with a variable <code>f</code> holding <code>my notes.txt</code> and another, <code>empty</code>, holding nothing.</p>
      __EXAMPLE:ch01_shell|shell.py &middot; a program that prints its arguments, run through bash with quotes, variables, globs, braces, arithmetic and command substitution, then run with no shell at all__

      <h4>What the example shows</h4>
      <p><b>Unquoted expansions are split, and quoted ones aren't.</b> <code>showargs $f</code> receives two arguments, <code>my</code> and <code>notes.txt</code>, because the value was split at its space. A program given those would look for two files that don't exist. <code>"$f"</code> keeps it whole. An empty variable unquoted disappears altogether, leaving zero arguments, while <code>"$empty"</code> is one empty argument. That difference is why <code>[ $answer = yes ]</code> fails with a strange error when <code>answer</code> is empty: the test receives <code>= yes</code>. The rule that prevents most shell bugs is simple: <b>put double quotes around every expansion</b>, <code>"$var"</code>, <code>"$(command)"</code>, <code>"$@"</code>, unless you can say why you want it split.</p>
      <p><b>Globs match file names, and are expanded after splitting.</b> <code>*.txt</code> became <code>a.txt</code> and <code>b c.txt</code>, sorted, with the space intact: names produced by globbing are never split again. A glob that matches nothing is passed on unchanged, so <code>showargs *.csv</code> received the literal <code>*.csv</code>; that's bash's default, and zsh's default is different: it stops with "no matches found". Quoted, <code>"*.txt"</code> is just text. Section 5 shows the order's sharpest edge: the output of <code>$(printf '*.txt')</code> is the text <code>*.txt</code>, and because substitution happens before globbing, it is then expanded into file names. Command output containing a <code>*</code>, a space or a newline is rewritten unless it's quoted.</p>
      <p><b>Assignments have no spaces.</b> <code>x=5</code> sets a variable. <code>x = 5</code> runs a program called <code>x</code> with arguments <code>=</code> and <code>5</code>, and fails with status 127, "command not found". Putting an assignment before a command, as in <code>x=5 y="a b" showargs</code>, sets them for that one command only, which chapter 7 uses. And the last line shows the other side: when Python's <code>subprocess.run</code> is given a list, there's no shell, so nothing is expanded. <code>*.txt</code> and <code>$HOME</code> arrive exactly as written. When you start programs from your own code, pass a list rather than a string to a shell, and the quoting problems disappear.</p>

      <h4>Globs are not regular expressions</h4>
      <p>Glob patterns look like the regular expressions of chapter 3, and mean different things. In a glob, <code>*</code> matches any run of characters, <code>?</code> exactly one, and <code>[abc]</code> one of a set; the pattern must match the whole name. A <code>*</code> doesn't match a leading dot, so <code>*</code> skips hidden files like <code>.bashrc</code>, and it doesn't cross <code>/</code>, so <code>src/*.py</code> looks in one folder only. To match in every subfolder, zsh understands <code>**/*.py</code> by default, and bash does after <code>shopt -s globstar</code>, which needs bash 4; for anything more, use <code>find</code>, in chapter 3. In a regular expression, by contrast, <code>*</code> means "the previous thing, any number of times", and <code>.</code> means any character.</p>

      <h4>Seeing what the shell will run</h4>
      <p>You never have to guess what a line expands to. <code>set -x</code> makes bash print each command, after expansion, before running it, with a <code>+</code> in front; <code>set +x</code> turns it off. It's the most useful debugging tool the shell has, and it works in scripts too. For a single line, put <code>echo</code> or <code>printf '[%s]\n'</code> in front of a command to see its arguments without running it. Two keyboard habits save hours as well: <b>Tab</b> completes commands and file names, and quotes awkward names for you, and <b>Ctrl-R</b> searches back through the commands you've run before. History is kept in a file, usually <code>~/.bash_history</code> or <code>~/.zsh_history</code>.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Unquoted variables,</b> which break on the first file name with a space and vanish when empty.</li>
          <li><b><code>for f in $(ls)</code>,</b> which splits names at spaces; loop over a glob, <code>for f in *</code>, instead.</li>
          <li><b>Spaces around <code>=</code></b> in an assignment, which turn it into a command.</li>
          <li><b>Expecting <code>*</code> to match hidden files,</b> or an unmatched glob to vanish: bash passes it on unchanged.</li>
          <li><b>Curly quotes</b> pasted from a web page or word processor: <code>&#8220;</code> and <code>&#8221;</code> are ordinary characters to the shell, not quotes.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 1.1</span><span class="ex-title">Predict the list</span></div>
          <p>After <code>a="1 2"; b=""</code>, in a folder with no files whose names start with <code>1</code>, predict what <code>showargs</code> receives from each line: <code>showargs $a$b</code>, <code>showargs "$a""$b"</code>, <code>showargs $b $a</code>, <code>showargs '$a' "\$a"</code>, <code>showargs {x,y}{1,2}</code> and <code>showargs "$a"*</code>.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">showargs $a$b          2 argument(s): [1] [2]
showargs "$a""$b"      1 argument(s): [1 2]
showargs $b $a         2 argument(s): [1] [2]
showargs '$a' "\$a"    2 argument(s): [$a] [$a]
showargs {x,y}{1,2}    4 argument(s): [x1] [x2] [y1] [y2]
showargs "$a"*         1 argument(s): [1 2*]</code></pre>
            <p><code>$a$b</code> is <code>1 2</code> followed by nothing, split into two words. Quoted, <code>"$a""$b"</code> is one word, and the empty <code>"$b"</code> adds nothing to it because it's part of the same word. In <code>$b $a</code> the unquoted empty <code>$b</code> disappears. Single quotes and a backslash both stop expansion. Two brace expressions in one word multiply, giving every combination. In the last line the quoted part isn't split, so the glob is the single pattern <code>1 2*</code>, which matches nothing and is passed on unchanged. Each answer was produced by running the line in bash.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 1.2</span><span class="ex-title">The loop that breaks on spaces</span></div>
          <p>In a folder holding <code>my notes.txt</code> and <code>todo.txt</code>, this loop prints three lines instead of two: <code>for f in $(ls *.txt); do echo "loop got [$f]"; done</code>. Explain why, and write a loop that's correct for any file name, including when there are no matching files.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">for f in *.txt; do
  [ -e "$f" ] || continue        # no match: bash leaves the literal "*.txt"
  echo "loop got [$f]"
done</code></pre>
            <p>The glob <code>*.txt</code> is expanded into two names for <code>ls</code>, which prints them, one per line. But the output of <code>$(ls *.txt)</code> is then split at every space and newline, so <code>my notes.txt</code> becomes two words, and the loop runs three times, with <code>my</code>, <code>notes.txt</code> and <code>todo.txt</code>. Looping over the glob itself gives each name as one word, spaces and all, because names produced by globbing are never split. The <code>[ -e "$f" ]</code> test handles the empty case: with no <code>.txt</code> files, the loop would otherwise run once with the literal <code>*.txt</code>. In bash, <code>shopt -s nullglob</code> makes an unmatched glob expand to nothing instead. And inside the loop, <code>"$f"</code> stays quoted wherever it's used.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 1.3</span><span class="ex-title">The empty variable</span></div>
          <p>In 2015, Steam's installer for Linux ran a line like <code>rm -rf "$STEAMROOT/"*</code>. On some machines <code>STEAMROOT</code> turned out to be empty. What did the line expand to, and how should it have been written?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>With <code>STEAMROOT</code> empty, <code>"$STEAMROOT/"*</code> is the glob <code>/*</code>, every entry at the top of the filesystem. With <code>showargs</code> in place of <code>rm</code>, on the Mac this volume was written on, the line expands to seventeen arguments: <code>-rf</code>, then <code>/Applications</code>, <code>/Library</code>, <code>/System</code>, <code>/Users</code> and every other top-level folder. For an ordinary user, that deleted every file they owned, on every mounted drive, which is what the bug report described. The defences, in order of importance: <code>${STEAMROOT:?}</code> makes the shell stop with an error if the variable is unset or empty, instead of expanding to nothing; <code>set -u</code> at the top of a script makes any unset variable an error, which chapter 4 recommends; and checking a value before using it to delete anything, <code>[ -d "$STEAMROOT" ] || exit 1</code>, catches values that are set but wrong. Running a destructive line with <code>echo</code> in front first would have shown the problem on the developer's machine.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you say exactly which list of arguments a program receives from a line?</li>
            <li>Can you explain the difference between single quotes, double quotes and no quotes?</li>
            <li>Can you name the shell's expansions in order, and say why command output gets globbed?</li>
            <li>Can you use <code>set -x</code> to see what a line really runs?</li>
            <li>Can you write a loop over files that works when names contain spaces?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Course</span><div><a href="https://missing.csail.mit.edu/2020/course-shell/">The Missing Semester: The Shell</a> <span class="by">MIT</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://www.gnu.org/software/bash/manual/html_node/Shell-Expansions.html">Bash Reference Manual: Shell Expansions</a> <span class="by">GNU</span></div></li>
            <li><span class="rkind free">Wiki</span><div><a href="https://mywiki.wooledge.org/BashPitfalls">Bash Pitfalls</a> <span class="by">Greg's Wiki</span></div></li>
          </ul>
        </div>
      </div>
    </section>
