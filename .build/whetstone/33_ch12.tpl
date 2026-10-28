    <section class="chapter prose" id="ch12" data-ch="12">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 12</span><label class="done-toggle"><input type="checkbox" data-id="ch12"><span class="box"></span>Read</label></div>
        <h3>History as a debugging tool</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">A repository's history isn't just a backup. It's the best debugging tool you have for the bug that begins "it used to work". <code>git bisect</code> searches history for the commit that broke something, automatically if you give it a test, and finds it among a thousand commits in ten steps. <code>git log -S</code> finds the commits that added or removed a piece of text, and <code>git blame</code> says which commit last changed each line, which leads to why. All three are only as good as the history they search: small commits, with messages that explain why.</p>
      </header>

      <h4>Reading history</h4>
      <p><code>git log</code> shows commits newest first, and a handful of options turn it into a query. <code>--oneline</code> gives one line per commit, <code>--graph --all</code> draws every branch, <code>-p</code> adds each commit's changes, and <code>--stat</code> lists the files each touched. <code>-n 5</code>, <code>--since=2.weeks</code> and <code>--author=Ada</code> limit it, and <code>-- path</code> at the end limits it to commits that changed one file or folder. <code>git log main..feature</code> lists commits on <code>feature</code> that aren't on <code>main</code>, which is what a pull request contains, and <code>git show</code> displays one commit in full. Put a <code>lg</code> alias for <code>log --graph --oneline --all</code> in your dotfiles and you'll use it every day.</p>

      <h4>Bisect: binary search over history</h4>
      <p>When something worked at an old commit and doesn't now, the commit that broke it is somewhere in between, and checking every one would take as long as there are commits. <code>git bisect</code> does a binary search instead. You mark one commit good and one bad, and Git checks out the commit halfway between them, on a detached <code>HEAD</code>. You test it and say <code>git bisect good</code> or <code>git bisect bad</code>, which throws away half the suspects. Repeat, and after about log<sub>2</sub> of the number of commits, Git names the first bad one: ten steps for a thousand commits, twenty for a million. <code>git bisect reset</code> returns you to where you started.</p>
      <p>Better still, give bisect a command and let it do the testing: <code>git bisect run ./check.sh</code>. Its exit status decides. 0 means good, 125 means "this commit can't be tested, skip it", and any other status from 1 to 127 means bad. Recent versions of Git also stop with an error if the test can't even run, status 126 or 127, on the commit you marked good. That catches a missing or non-executable script before it can blame an innocent commit. But nothing can catch a test that runs and checks the wrong thing.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Forty commits in a row, numbered 1 to 40. Commit 1 is known good and commit 40 bad. Each bisect step tests the middle of the remaining range and keeps the half that contains the change: commit 20 is good, so the suspects are 21 to 40; 30 is bad, leaving 21 to 30; 25 is good, leaving 26 to 30; 27 is bad, leaving 26 and 27; 26 is good, so commit 27 is the first bad commit. Five tests instead of up to thirty-eight.">
          __SVG:fig12__
        </svg>
        <figcaption>Each test halves the suspects. The search needs to know only good or bad for each commit it tests, so a script can answer for you.</figcaption>
      </figure>
      <p>The example builds a small repository with forty commits. The first adds a <code>slug()</code> function that turns a recipe's title into a web address, and commit 27, "Simplify slug()", quietly breaks it for accented letters. A test script checks one title. The example lets <code>bisect run</code> find the culprit, then asks <code>log -S</code> and <code>blame</code> the same question, and undoes the damage with <code>revert</code>.</p>
      __EXAMPLE:ch12_history|history.py &middot; forty commits, one that breaks a function, found by git bisect run with a test script, then by log -S and blame, and undone with revert__

      <h4>What the example shows</h4>
      <p><b>Bisect needed five tests.</b> It tried commit 20, which was good, then 30, bad, 25, good, 27, bad, and 26, good, and concluded that 27 was the first bad commit. That's every possible culprit among 39 suspects, commits 2 to 40, settled in five runs of the test, with no human involved. On a real project, with a test suite that takes minutes, this is the difference between a ten-minute search and an afternoon.</p>
      <p><b>Text search and blame answer different questions.</b> <code>git log -S normalize</code> listed the two commits that changed how many times the word <code>normalize</code> appeared: the one that added it and the one that removed it. Without knowing where the bug was, that found it from a guess about what had changed. <code>git blame</code> on the function gave each line's last commit: the first two lines date from the original, and the broken <code>return</code> line from "Simplify slug()". The example reads blame's machine-readable <code>--line-porcelain</code> output, the right choice for scripts; at a terminal, plain <code>git blame</code> marks lines from the very first commit with a <code>^</code>. Finally, <code>git revert</code> made a new commit that applies the opposite of the bad one, and the test passed again. History wasn't rewritten, so it's safe even after the bad commit has been shared.</p>

      <h4>Searching and blaming well</h4>
      <p><code>-S text</code>, the "pickaxe", finds commits that change the number of occurrences of the text, so it finds where a function was added or deleted, but not where an existing call was edited. For that, <code>-G regex</code> finds commits whose changed lines match. <code>git blame -w</code> ignores changes of whitespace, and <code>-C</code> follows lines that were moved or copied from other files. Large reformatting commits make blame useless for every line they touched. List them in a <code>.git-blame-ignore-revs</code> file, and <code>git blame --ignore-revs-file</code>, or GitHub's blame view, will look past them. Remember what blame is for: a line's commit leads to its message, its pull request and its discussion. That's <i>why</i> the line is the way it is, which is far more useful than who typed it.</p>

      <h4>History worth searching</h4>
      <p>Each of these tools depends on how history was written. When bisect finds a five-line commit that does one thing, the bug is obvious. When it finds a two-thousand-line commit titled "updates", you've learned little. So make <b>small commits that do one thing each</b>, and make sure each one builds and passes the tests, so bisect can test any of them. Write <b>messages that explain why</b>. The first line is a short summary in the imperative, around fifty characters, as in "Simplify slug()", then a blank line, then whatever a reader will need in a year: the reason for the change, what you considered, what it fixes. <code>git commit</code> without <code>-m</code> opens your editor so there's room for that, which is one reason chapter 14 matters.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Huge commits that mix unrelated changes,</b> which bisect can only point at, not explain.</li>
          <li><b>Messages like "fix" or "wip",</b> which tell blame's reader nothing.</li>
          <li><b>Forgetting <code>git bisect reset</code>,</b> and carrying on work on a detached <code>HEAD</code>.</li>
          <li><b>A bisect test that checks the wrong thing,</b> which makes bisect blame an innocent commit.</li>
          <li><b>Undoing a shared commit with <code>reset</code></b> instead of <code>revert</code>.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 12.1</span><span class="ex-title">A thousand commits</span></div>
          <p>A bug appeared somewhere in the last 1,000 commits. About how many tests will bisect need? Some old commits don't build at all; write a <code>bisect run</code> script for a project tested with <code>make test</code> that copes with them.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">#!/bin/sh
# check.sh: tell git bisect whether this commit is good (0), bad (1) or untestable (125)
make > /dev/null 2>&1 || exit 125      # doesn't build: neither good nor bad, so skip it
make test > /dev/null 2>&1 || exit 1   # builds, tests fail: bad
exit 0                                 # builds and passes: good</code></pre>
            <p>About 10, since 2<sup>10</sup> is 1,024: each test halves the suspects. The script turns a build failure into 125, so bisect skips that commit and tests a neighbour instead, rather than wrongly blaming a commit that only failed to build. In a test with a skipped commit in the middle of the range, bisect still named the right first bad commit. Keep the script outside the repository, or untracked, so it doesn't change as bisect checks out old commits, and make it exit 1 for a real failure rather than any status above 127, which would stop the search.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 12.2</span><span class="ex-title">A message for the future</span></div>
          <p>A commit changes the API client's timeout from <code>timeout=30</code> to <code>timeout=30_000</code>, because the library it uses changed from seconds to milliseconds in version 4. Its message is "fixed stuff". Write a better one.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">Give the API client's timeout in milliseconds

Version 4 of the HTTP library takes timeouts in milliseconds instead of
seconds, so after the upgrade our 30-second timeout became 30 ms, and
every request to the slower reports endpoint timed out.

Keep the same 30-second timeout, now written as 30_000.</code></pre>
            <p>The summary says what the commit does, in the imperative, short enough to read in <code>git log --oneline</code>. The body explains what nobody can recover from the change itself: why <code>30</code> became <code>30_000</code>, which would otherwise look like a typo someone might "fix" back. The symptom it cured is there for whoever searches for it, and the last line records that the behaviour was meant to stay the same. Someone who finds this line with blame next year will know not to touch it, which is the point.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 12.3</span><span class="ex-title">Which undo?</span></div>
          <p>Choose the command for each: (a) you've edited a file and want it back as it was in the last commit; (b) your last commit, not yet pushed, has a typo in its message; (c) a commit from last week, already on <code>main</code>, broke production; (d) your last three local commits should have been one.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>(a) <code>git restore file</code>, which throws away the uncommitted edits in that file, for good, so be sure. (b) <code>git commit --amend</code>, which replaces the last commit with a corrected one, fine because nobody else has it yet. (c) <code>git revert &lt;commit&gt;</code>, which adds a new commit that undoes it and changes no existing history, the only safe choice for a commit others have. (d) <code>git reset --soft HEAD~3</code> then <code>git commit</code>, which moves the branch back three commits while keeping all their changes staged, ready to commit as one; <code>git rebase -i HEAD~3</code> does the same with more control. The test in each case is chapter 11's rule: has anyone else got the commit? If so, add a commit; if not, you may replace it.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you query history by file, author, date and branch with <code>git log</code>?</li>
            <li>Can you find the commit that introduced a bug with <code>git bisect</code>, by hand and with <code>run</code>?</li>
            <li>Can you find when a piece of code appeared or disappeared with <code>git log -S</code>?</li>
            <li>Can you use <code>git blame</code> to find why a line is the way it is?</li>
            <li>Can you choose between <code>restore</code>, <code>amend</code>, <code>reset</code> and <code>revert</code>?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Docs</span><div><a href="https://git-scm.com/docs/git-bisect">git bisect</a> <span class="by">The Git project</span></div></li>
            <li><span class="rkind free">Article</span><div><a href="https://cbea.ms/git-commit/">How to Write a Git Commit Message</a> <span class="by">Chris Beams</span></div></li>
            <li><span class="rkind free">Book</span><div><a href="https://git-scm.com/book/en/v2/Git-Tools-Debugging-with-Git">Pro Git: Debugging with Git</a> <span class="by">Scott Chacon &amp; Ben Straub</span></div></li>
          </ul>
        </div>
      </div>
    </section>
