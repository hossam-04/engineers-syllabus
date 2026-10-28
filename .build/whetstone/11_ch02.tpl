    <section class="chapter prose" id="ch02" data-ch="02">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 2</span><label class="done-toggle"><input type="checkbox" data-id="ch02"><span class="box"></span>Read</label></div>
        <h3>Streams, pipes and exit codes</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Every program starts with three open streams, for its input, its output and its error messages, and finishes by returning a small number that says whether it worked. Redirection points those streams at files. A pipe connects one program's output to the next program's input, and the exit status lets the shell decide what to run next. Small programs that each do one thing become powerful through these three mechanisms. Two details cause most of the bugs: redirections are applied from left to right, and a pipeline reports only its last command's status.</p>
      </header>

      <h4>Three streams and a number</h4>
      <p>When a program starts, it inherits three open <b>file descriptors</b>, small numbers that stand for open files: <b>0</b> is standard input, <b>1</b> standard output and <b>2</b> standard error. In a terminal all three are the terminal itself, which is why both output and error messages appear on screen. They're separate so that a program's results and its complaints can go to different places: results into a file or the next program, errors to a person. A well-behaved program writes what it computed to stdout and anything meant for a human, warnings, progress, errors, to stderr.</p>
      <p>When it finishes, every program returns an <b>exit status</b> between 0 and 255. Zero means success, and every other value is some kind of failure; the shell keeps the last one in <code>$?</code>. A few values have conventional meanings: 1 for a general failure, 2 for misuse such as a bad option, 126 for a file that was found but isn't executable, 127 for a command that wasn't found, and 128 plus a signal's number for a program that was killed. That makes 130 a program stopped by Ctrl-C, signal 2, and 141 one killed by <code>SIGPIPE</code>, signal 13, which the example shows. The exit status is the only result every caller checks without reading anything.</p>

      <h4>Redirection</h4>
      <p><code>&gt; file</code> sends stdout to a file, creating it or emptying it first; <code>&gt;&gt; file</code> appends instead; <code>&lt; file</code> reads stdin from a file; and putting a number in front picks the descriptor, so <code>2&gt; errors.txt</code> redirects stderr. <code>2&gt;&amp;1</code> means "make descriptor 2 point wherever descriptor 1 points <i>now</i>". That last word is the whole difficulty. The shell processes redirections from left to right, each one changing a table of where the descriptors point. So <code>&gt; out.txt 2&gt;&amp;1</code> first points 1 at the file, then points 2 at the same place: both go to the file. But <code>2&gt;&amp;1 &gt; out.txt</code> first points 2 at the terminal, where 1 still points, and only then moves 1 to the file: errors stay on the screen. Bash's <code>&amp;&gt; file</code> is shorthand for the first form. <code>/dev/null</code> is a file that discards whatever is written to it.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 306" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Two columns showing the descriptor table as the shell applies redirections from left to right. Left, talk greater-than out.txt 2 greater-than ampersand 1: at the start, 1 and 2 both point to the terminal; after greater-than out.txt, 1 points to out.txt; after 2 greater-than ampersand 1, 2 also points to out.txt, so both lines land in the file. Right, talk 2 greater-than ampersand 1 greater-than out.txt: after 2 greater-than ampersand 1, 2 points to the terminal, where 1 points; after greater-than out.txt, only 1 moves to the file, so stderr still reaches the terminal.">
          __SVG:fig02__
        </svg>
        <figcaption>Redirections edit a table, left to right. <code>2&gt;&amp;1</code> copies where 1 points at that moment, so its position decides where errors go.</figcaption>
      </figure>
      <p>The example uses a tiny program, <code>talk</code>, that writes one line to stdout, one to stderr, and exits with whatever status it's given. For each line, it reports which text reached the terminal's stdout, which reached its stderr, and what ended up in any file.</p>
      __EXAMPLE:ch02_streams|streams.py &middot; one program writing to both streams, run with redirections, pipes, tee, exit statuses, pipefail and PIPESTATUS, set -e and here-documents__

      <h4>Pipes</h4>
      <p>A pipe, <code>a | b</code>, connects <code>a</code>'s stdout to <code>b</code>'s stdin. Only stdout: in section 3, <code>talk | tr a-z A-Z</code> uppercased the stdout line, while the stderr line went around the pipe to the terminal, unchanged. To send both through, redirect first: <code>talk 2&gt;&amp;1 | tr a-z A-Z</code>. <code>tee file</code> copies its input to a file and passes it on, so you can save a stream and keep processing it. Both programs in a pipeline run at the same time, the second reading as the first writes, which is why a pipeline can process a file far larger than memory. It's also why <code>yes | head -n 2</code> finishes: <code>yes</code> prints <code>y</code> for ever, <code>head</code> exits after two lines, and the next write by <code>yes</code> finds no reader and kills it with <code>SIGPIPE</code>. Its status, 141, is in section 5.</p>

      <h4>Exit statuses, conditions and pipefail</h4>
      <p>The shell's conditions are built on exit statuses, not on true and false values. <code>a &amp;&amp; b</code> runs <code>b</code> only if <code>a</code> succeeded, <code>a || b</code> only if it failed, and <code>if command; then</code> runs the branch when the command's status is 0. The <code>[</code> in <code>if [ -f notes.txt ]</code> is itself a command, also called <code>test</code>, which exits 0 or 1. Programs like <code>grep -q</code> exist to be used as conditions: they print nothing and exit 0 if a line matched. One caution: <code>a &amp;&amp; b || c</code> isn't if-then-else, because <code>c</code> also runs when <code>b</code> fails.</p>
      <p>A pipeline's status is the status of its <b>last</b> command. <code>false | true</code> succeeds, which means a failure early in a pipeline, a download that broke halfway, a program that crashed, is silently ignored. <code>set -o pipefail</code> changes the rule: the pipeline fails if any command in it failed. And bash keeps every status from the last pipeline in the array <code>PIPESTATUS</code>: <code>1 0 2</code> in section 5 are the statuses of <code>false</code>, <code>true</code> and <code>talk 2</code>. Like <code>$?</code>, it's overwritten by the next command, so read it immediately.</p>
      <p><code>set -e</code> makes a script exit when a command fails, and it has surprising exceptions. It doesn't apply to commands whose status is being tested, in an <code>if</code>, a <code>while</code>, or on the left of <code>&amp;&amp;</code> or <code>||</code>. And the exemption reaches into functions: in section 6, <code>check</code> was called on the left of <code>||</code>, so inside it <code>false</code> failed and the function carried on as if nothing had happened. <code>set -e</code> is still worth using, as chapter 4 does, but as a safety net. When a failure matters, check it explicitly: <code>cd "$dir" || exit 1</code>.</p>

      <h4>Here-documents</h4>
      <p>A <b>here-document</b> feeds the lines between <code>&lt;&lt;EOF</code> and a line containing just <code>EOF</code> to a command's stdin, which is the cleanest way to write a file or a block of text from a script. Variables and substitutions are expanded inside it, unless the marker is quoted, <code>&lt;&lt;'EOF'</code>, which section 7 shows. Bash also has the here-string, <code>grep x &lt;&lt;&lt; "$text"</code>, which feeds one string as input. Any word can be the marker, and <code>EOF</code> is only a habit.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b><code>cmd 2&gt;&amp;1 &gt; file</code></b> when you meant both streams in the file: put <code>2&gt;&amp;1</code> last.</li>
          <li><b><code>sort data.txt &gt; data.txt</code>,</b> which empties the file: the shell truncates it before <code>sort</code> starts.</li>
          <li><b>Reading <code>$?</code> too late,</b> after another command, even an <code>echo</code>, has replaced it.</li>
          <li><b>Pipelines without <code>pipefail</code>,</b> where an early failure disappears behind a successful last command.</li>
          <li><b>Trusting <code>set -e</code></b> inside functions that are called from a condition.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 2.1</span><span class="ex-title">Where does each line go?</span></div>
          <p>For the example's <code>talk</code>, say what reaches the terminal and what ends up in which file for: <code>talk &gt; log 2&gt;&amp;1</code>, <code>talk 2&gt;&amp;1 &gt; log</code>, <code>talk &amp;&gt; log</code> and <code>talk 2&gt; err &gt; out</code>.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">talk > log 2>&1      terminal: nothing          log: to stdout, to stderr
talk 2>&1 > log      terminal: to stderr        log: to stdout
talk &> log          terminal: nothing          log: to stdout, to stderr
talk 2> err > out    terminal: nothing          out: to stdout   err: to stderr</code></pre>
            <p>Work through the table from left to right. In the second line, <code>2&gt;&amp;1</code> runs while 1 still points at the terminal, so 2 is pointed at the terminal, and the later <code>&gt; log</code> moves only 1. <code>&amp;&gt;</code> is bash's shorthand for <code>&gt; log 2&gt;&amp;1</code>; it doesn't exist in plain <code>sh</code>, so scripts meant for any shell spell it out. The last line sends each stream to its own file, and the order of the two redirections doesn't matter there because neither copies the other. Each answer was checked by running the line.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 2.2</span><span class="ex-title">The file that emptied itself</span></div>
          <p>Someone sorts a list in place with <code>sort names.txt &gt; names.txt</code>, and finds <code>names.txt</code> empty afterwards. Explain what happened, and give two correct ways to do it.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">sort -o names.txt names.txt                          # sort can write over its own input
sort names.txt > names.txt.new && mv names.txt.new names.txt   # works for any command</code></pre>
            <p>Redirections are set up by the shell before the command starts, and <code>&gt;</code> empties its file. So by the time <code>sort</code> opened <code>names.txt</code> to read it, it was already empty, and sorting nothing produced nothing: running the line leaves the file at 0 bytes. <code>sort -o</code> is safe because <code>sort</code> reads all its input before it opens the output. The general pattern, writing to a new file and renaming it over the old one only if the command succeeded, works for any program, and the <code>&amp;&amp;</code> means a failed command leaves the original untouched. The rename is atomic, as chapter 5 explains, so nothing ever sees a half-written file.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 2.3</span><span class="ex-title">The failure that disappeared</span></div>
          <p>A build script runs <code>make 2&gt;&amp;1 | tee build.log</code>, and the job is marked successful even when <code>make</code> fails. Explain why, and fix it two ways: for the whole script, and for this one line.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">set -o pipefail                      # for the whole script: any failure fails the pipeline
make 2>&1 | tee build.log

make 2>&1 | tee build.log            # for one line: check make's own status
status=${PIPESTATUS[0]}
[ "$status" -eq 0 ] || { echo "build failed with status $status" >&2; exit "$status"; }</code></pre>
            <p>The pipeline's status is <code>tee</code>'s, and <code>tee</code> succeeds whenever it can write the log, so <code>make</code>'s failure is lost. With <code>pipefail</code>, the pipeline fails if any part fails: running <code>false | wc -l</code> gives status 0 normally and 1 with <code>pipefail</code>. <code>PIPESTATUS</code> gives each command's status separately, so the script can report <code>make</code>'s own code. It has to be copied straight away, as here, because the next command replaces it. GitHub Actions adds <code>-o pipefail</code> for exactly this reason when a step names <code>bash</code> as its shell, but not when the shell is left to its default; a script shouldn't depend on where it's run.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you name the three standard streams, and say what belongs on each?</li>
            <li>Can you predict where output goes for any order of redirections?</li>
            <li>Can you read an exit status, including 126, 127 and 128 plus a signal?</li>
            <li>Can you make a pipeline fail when any part of it fails?</li>
            <li>Can you say when <code>set -e</code> won't stop a script?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Docs</span><div><a href="https://www.gnu.org/software/bash/manual/html_node/Redirections.html">Bash Reference Manual: Redirections</a> <span class="by">GNU</span></div></li>
            <li><span class="rkind free">Wiki</span><div><a href="https://mywiki.wooledge.org/BashFAQ/105">Why doesn't set -e do what I expected?</a> <span class="by">Greg's Wiki</span></div></li>
            <li><span class="rkind free">Course</span><div><a href="https://missing.csail.mit.edu/2020/shell-tools/">The Missing Semester: Shell Tools and Scripting</a> <span class="by">MIT</span></div></li>
          </ul>
        </div>
      </div>
    </section>
