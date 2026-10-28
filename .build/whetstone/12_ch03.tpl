    <section class="chapter prose" id="ch03" data-ch="03">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 3</span><label class="done-toggle"><input type="checkbox" data-id="ch03"><span class="box"></span>Read</label></div>
        <h3>Searching and transforming text</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Most of what you'll want to ask a computer is already written down somewhere as text: in logs, configuration files, code and exported data. Four tools answer most of those questions. <code>find</code> chooses files, <code>grep</code> chooses lines, <code>sed</code> rewrites lines, and <code>awk</code> computes over the fields of each line. With <code>sort</code>, <code>uniq</code>, <code>cut</code> and <code>head</code> between them, a pipeline of five short commands answers questions that would take a page of code. A little knowledge of regular expressions makes all of them more precise. This chapter questions a web server's log and a project folder.</p>
      </header>

      <h4>Regular expressions in ten minutes</h4>
      <p>A <b>regular expression</b> is a pattern that matches text. Most characters match themselves. A <code>.</code> matches any one character; <code>[abc]</code> matches one of a set, <code>[^abc]</code> anything outside it, and <code>[0-9]</code> a range. <code>^</code> and <code>$</code> anchor the pattern to the start and end of the line. Repetition applies to the thing just before it: <code>*</code> means zero or more, <code>+</code> one or more, <code>?</code> zero or one, and <code>{2,4}</code> between two and four. Parentheses group, and <code>|</code> means "or", so <code>^(GET|POST) /api/</code> matches lines that start with either word followed by <code>/api/</code>. A backslash makes a special character ordinary: <code>\.</code> is a real dot. Matching is <b>greedy</b>: <code>".*"</code> on <code>"a" and "b"</code> matches the whole thing, not just <code>"a"</code>, because <code>.*</code> takes as much as it can.</p>
      <p>There are two dialects, and that causes confusion. <b>Basic</b> regular expressions, the default for <code>grep</code> and <code>sed</code>, treat <code>+</code>, <code>?</code>, <code>|</code>, <code>()</code> and <code>{}</code> as ordinary characters unless they have a backslash. <b>Extended</b> regular expressions, which you get with <code>grep -E</code> and <code>sed -E</code> and which <code>awk</code> always uses, give them their special meaning directly. Use <code>-E</code> everywhere and you only have to remember one. Named classes like <code>[[:digit:]]</code> and <code>[[:space:]]</code> work in both, and in every locale. Chapter 1's globs are a different language: there <code>*</code> means "anything" by itself.</p>

      <h4>grep chooses lines, find chooses files</h4>
      <p><code>grep pattern file</code> prints the lines that match. The options you'll use constantly are <code>-i</code> to ignore case, <code>-v</code> for lines that don't match, <code>-c</code> to count them, <code>-n</code> to show line numbers, <code>-o</code> to print only the matching part, <code>-w</code> to match whole words, <code>-F</code> to treat the pattern as plain text, and <code>-r</code> to search a whole folder, with <code>-l</code> to list only the files. Like every good tool it reports through its exit status too: 0 if something matched, 1 if nothing did, 2 for an error, which is what makes <code>grep -q</code> useful in conditions.</p>
      <p><code>find</code> walks a folder tree and tests each file against an expression. <code>-name '*.py'</code> matches names by glob, and must be quoted, or the shell expands it first. <code>-type f</code> chooses files and <code>-type d</code> folders. <code>-mtime +30</code> means last modified more than 30 days ago, and <code>-size +10M</code> bigger than ten megabytes. Tests are combined with an implied "and", or with <code>-o</code> for "or". <code>-prune</code> stops <code>find</code> from going into a folder, which is how you skip <code>node_modules</code> or <code>.git</code>. The default action is to print the path. <code>-exec command {} +</code> runs a command on the files it found, with as many names per run as fit, and <code>-delete</code> deletes them.</p>

      <h4>sed rewrites lines, awk computes over fields</h4>
      <p><code>sed</code>, the stream editor, applies editing commands to each line as it passes through. Almost all of its use is substitution: <code>s/old/new/</code> replaces the first match on each line, <code>s/old/new/g</code> every match, and parentheses in the pattern capture text that <code>\1</code>, <code>\2</code> put back in the replacement. A command can be limited to some lines by number, <code>3,5s/a/b/</code>, or by pattern, <code>/ERROR/s/a/b/</code>. With <code>-n</code>, <code>sed</code> prints nothing unless told to with <code>p</code>, so <code>sed -n '/404/p'</code> behaves like <code>grep</code>.</p>
      <p><code>awk</code> is a small programming language for tables of text. It splits each line into fields, <code>$1</code>, <code>$2</code> and so on to <code>$NF</code>, the last one, at runs of spaces or at the separator given with <code>-F</code>. A program is a list of <code>pattern {action}</code> rules: the action runs on lines that match the pattern, and a missing pattern matches every line. <code>BEGIN</code> and <code>END</code> rules run before the first line and after the last. Variables need no declaring, start at zero or empty, and can be associative arrays, so <code>{n[$1]++}</code> counts lines by their first field. <code>awk</code> was written in 1977 by Aho, Weinberger and Kernighan, whose initials give it its name, and their book about it was updated in 2023.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 270" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The pipeline that finds the three busiest client addresses, drawn as four stages with the data between them. The access log has 48 lines. awk, counting lines by their first field, prints six lines in no particular order, such as 4 203.0.113.90, 19 203.0.113.7 and 2 198.51.100.5. sort, by count from highest and then by address, puts them in order: 19 203.0.113.7, 13 198.51.100.23, 8 192.0.2.41, 4 203.0.113.90, 2 192.0.2.200 and 2 198.51.100.5. head -n 3 keeps the first three.">
          __SVG:fig03__
        </svg>
        <figcaption>A pipeline is a query: each stage narrows or reshapes the data and hands it on. The middle stages see six lines, not 48, and none of them needs to know where the data came from.</figcaption>
      </figure>
      <p>The example builds a web server's access log of 48 requests, each line holding the client's address, the time, the request, the status, the bytes sent and the milliseconds taken, plus a small project folder. Then it answers questions with one pipeline each.</p>
      __EXAMPLE:ch03_text|text.py &middot; a web server log and a project folder questioned with grep, cut, sort, uniq, awk, sed, find and xargs__

      <h4>What the example shows</h4>
      <p><b>Each tool does one job, and the pipeline does the rest.</b> <code>cut -d ' ' -f 1,7,9,11</code> picks fields by number from lines separated by single spaces, which is how it pulled the address, path, status and time from each server error. <code>grep -o</code> printed just the <code>/api/...</code> part of each line, ready for counting. <code>uniq -c</code> counts runs of identical <i>adjacent</i> lines, which is why it always follows a <code>sort</code>. It also pads its counts differently on macOS and Linux, so the example passes them through <code>awk '{print $1, $2}'</code> to print the same everywhere. That's a habit worth having for any output another program will read.</p>
      <p><b>awk does the arithmetic.</b> <code>n[$1]++</code> counted requests per address, and the <code>END</code> rule printed the totals, in an order <code>awk</code> doesn't promise, so <code>sort -k1,1nr -k2,2</code> put them in order: numerically by count, highest first, and by address when counts tie, so the result never depends on chance. In <code>$NF + 0 &gt; 1400</code>, adding zero turned <code>1698ms</code> into the number 1698, because <code>awk</code> reads the leading digits of a string as its numeric value. The averages per status class came from two arrays and a <code>printf</code>, which formats numbers exactly as C's <code>printf</code> does.</p>
      <p><b>Names with spaces need care.</b> <code>xargs</code> reads names from its input and runs a command on them, but by default it splits its input at spaces, so <code>./old notes.tmp</code> became two names, <code>./old</code> and <code>notes.tmp</code>, neither of which exists. The file survived. <code>find -print0</code> ends each name with a zero byte, the one character a file name can't contain, and <code>xargs -0</code> splits only there. <code>find . -name '*.tmp' -exec rm {} +</code> avoids the problem entirely, by never turning names into text.</p>

      <h4>GNU, BSD and portability</h4>
      <p>Linux comes with the GNU versions of these tools, and macOS with the BSD ones. They agree on everything in this chapter's example, and differ in the corners. <code>sed -i</code> edits a file in place on Linux, while macOS needs <code>sed -i ''</code>. <code>grep -P</code>, for Perl-style patterns, is GNU-only, as are many long options. <code>stat</code> and <code>date</code> take completely different flags. Scripts that must run on both should stick to the options POSIX defines, the standard both follow, or check which system they're on. On a Mac, Homebrew's <code>coreutils</code>, <code>gnu-sed</code> and <code>grep</code> packages install the GNU versions with a <code>g</code> in front, <code>gsed</code> and <code>ggrep</code>, if you want Linux behaviour. Two modern tools are worth installing anywhere: <code>rg</code> (ripgrep), a much faster <code>grep -r</code> that skips files ignored by Git, and <code>jq</code>, which does for JSON what <code>awk</code> does for columns.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b><code>find . -name *.py</code> unquoted,</b> which the shell expands before <code>find</code> sees it.</li>
          <li><b><code>uniq</code> without <code>sort</code>,</b> which only merges duplicates that happen to be adjacent.</li>
          <li><b>An unescaped <code>.</code></b> in a pattern, matching any character: <code>grep 2026.03</code> also matches <code>2026503</code>.</li>
          <li><b><code>sed -i</code> in a script</b> that must run on both macOS and Linux.</li>
          <li><b>Feeding names to plain <code>xargs</code></b> or to <code>for f in $(find ...)</code>, which split them at spaces.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 3.1</span><span class="ex-title">Six commands</span></div>
          <p>In 1986, Jon Bentley asked Donald Knuth to write a program that prints the most common words in a text, and Doug McIlroy reviewed the result. Knuth's answer was ten pages of carefully documented Pascal; McIlroy's review included a six-command pipeline that did the same job. Write that pipeline: print the ten most frequent words in <code>story.txt</code>, ignoring case and punctuation, and explain each stage.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">tr -cs 'A-Za-z' '\n' < story.txt |   # every run of non-letters becomes one newline: a word per line
  tr 'A-Z' 'a-z' |                     # lower case, so "The" and "the" are the same word
  sort |                               # identical words become adjacent
  uniq -c |                            # count each run of identical lines
  sort -rn |                           # highest count first
  head -n 10                           # keep the top ten</code></pre>
            <p><code>-c</code> makes <code>tr</code> act on characters <i>not</i> in the set, and <code>-s</code> squeezes each run of them into a single newline. On the two sentences "The cat sat on the mat. The dog sat on the log. A cat and a dog: the best of friends, or the worst? The end." it puts <code>the</code> first with 7, then a five-way tie at 2. Ties come out in reverse alphabetical order, <code>sat</code>, <code>on</code>, <code>dog</code>, <code>cat</code>, <code>a</code>, because <code>-r</code> also reverses <code>sort</code>'s final whole-line comparison. McIlroy's point wasn't that Knuth's program was bad. It was that reusable tools, composed, solve most such problems in minutes, and that the pipeline is easy to change: <code>sort -rn</code> to <code>sort -n</code> gives the rarest words instead.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 3.2</span><span class="ex-title">A pattern that means what it says</span></div>
          <p>A file contains the lines <code>2026-03-14</code>, <code>2026503914</code>, <code>2026.03.14</code> and <code>meeting 2026-03-14 at 9</code>. How many lines does <code>grep -c '2026.03'</code> count? Write patterns that match lines consisting of exactly one date in the form <code>2026-03-14</code>, and lines that contain one anywhere.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">grep -c '2026.03' dates.txt                          # 4: the dot matches any character
grep -cE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' dates.txt    # 1: a whole line that is just a date
grep -cE '[0-9]{4}-[0-9]{2}-[0-9]{2}' dates.txt      # 2: a date anywhere in the line</code></pre>
            <p>All four lines match the first pattern: the dot matched a <code>-</code>, a <code>5</code> and a <code>.</code>, and the fourth line contains <code>2026-03</code>. To match a literal dot, write <code>\.</code>, or use <code>grep -F</code> for plain text. The anchors make the second pattern describe the whole line. Without them, as in the third, the pattern can match anywhere, so it also finds the date inside the meeting line. Neither pattern checks that the date is real: <code>2026-13-99</code> matches too. Regular expressions are good at shape and bad at meaning, so once you've found candidates, check them with a real date parser.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 3.3</span><span class="ex-title">Rename a whole tree</span></div>
          <p>Rename every <code>.jpeg</code> file under <code>pics</code>, in any subfolder, to <code>.jpg</code>, without breaking on names with spaces and without overwriting a file that already exists.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">find pics -type f -name '*.jpeg' -exec sh -c '
  for f do
    mv -n -- "$f" "${f%.jpeg}.jpg"
  done' sh {} +</code></pre>
            <p><code>find</code> hands the names straight to a small shell script, never as text to be split, so spaces are safe; <code>{} +</code> passes as many as fit at once, and the <code>sh</code> after the script fills <code>$0</code>, so the names arrive as <code>"$@"</code>, which <code>for f do</code> loops over. <code>${f%.jpeg}</code> removes the suffix, <code>mv -n</code> refuses to overwrite, and <code>--</code> protects names that start with a dash. Run on a tree with <code>a.jpeg</code>, <code>2025 trip/beach day.jpeg</code>, <code>2025 trip/b.JPEG</code> and <code>c.jpg</code>, it renamed the first two and left <code>b.JPEG</code> alone: <code>-name</code> is case-sensitive. <code>-iname</code> would find it, but then the suffix to strip could be any mix of cases. Try such a command with <code>echo</code> in front of <code>mv</code> first, and look at the list before letting it run.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you write an extended regular expression with classes, anchors, groups and repetition?</li>
            <li>Can you find files by name, type, size and age, skipping folders you don't want?</li>
            <li>Can you count, rank and summarise a log with <code>sort</code>, <code>uniq</code> and <code>awk</code>?</li>
            <li>Can you rewrite text with <code>sed</code> substitutions and capture groups?</li>
            <li>Can you process file names safely with <code>-print0</code>, <code>xargs -0</code> or <code>-exec ... {} +</code>?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Course</span><div><a href="https://missing.csail.mit.edu/2020/data-wrangling/">The Missing Semester: Data Wrangling</a> <span class="by">MIT</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://www.gnu.org/software/gawk/manual/html_node/Getting-Started.html">The GNU Awk User's Guide: Getting Started</a> <span class="by">GNU</span></div></li>
            <li><span class="rkind free">Guide</span><div><a href="https://github.com/jlevy/the-art-of-command-line">The Art of Command Line</a> <span class="by">Joshua Levy and contributors</span></div></li>
          </ul>
        </div>
      </div>
    </section>
