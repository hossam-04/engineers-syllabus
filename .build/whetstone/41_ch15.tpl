    <section class="chapter prose" id="ch15" data-ch="15">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 15</span><label class="done-toggle"><input type="checkbox" data-id="ch15"><span class="box"></span>Read</label></div>
        <h3>Error messages, docs and good questions</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Most answers are already in front of you: in the error message you skimmed, the manual page, the <code>--help</code> output and the project's documentation. Reading them is a skill. Read tracebacks from the bottom up, decode a synopsis, and search the documentation before the web. When you do need help, a <b>minimal reproduction</b> does half the work: making one often reveals the bug, and when it doesn't, it gets your question answered fast. This chapter reads a traceback properly, then shrinks a failing input automatically to the two lines that matter.</p>
      </header>

      <h4>Read the whole message</h4>
      <p>An error message is a program's best attempt to tell you what went wrong and where, and it's usually right. Read it slowly, all of it, before doing anything else. It names a file, a line, a value, or the thing it expected and what it found instead. When there are many errors, start with the first: compilers and test runners often report one real problem followed by a cascade of consequences. If you search for a message, search for the exact words in quotes, without the parts that are yours, such as your file names, paths and values, which nobody else's copy of the message contains.</p>

      <h4>Tracebacks, from the bottom</h4>
      <p>When a Python program fails, it prints a <b>traceback</b>: the chain of calls that was in progress, with the outermost first and the innermost, where the error happened, last, followed by a final line naming the exception and its message. So read it from the bottom. The last line says <i>what</i> went wrong. The frame just above it says <i>where</i>: the file, line number and function, and the line of code itself. The frames above that say <i>how the program got there</i>. The bug is usually in the lowest frame that belongs to your own code rather than to a library, because libraries mostly fail when given something they shouldn't have been. A traceback containing "During handling of the above exception, another exception occurred" shows two errors, and the first is usually the cause. Other languages differ in layout: Java, for one, prints the exception first and then the frames, innermost first. Learn your language's convention once.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 242" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A Python traceback, annotated. It begins with Traceback, most recent call last. Then three frames, outermost first: the program's main code at line 35, calling average_prices; average_prices at line 11, calling average; and average at line 20, where it divided by the length of the list. The last line reads ZeroDivisionError: division by zero. Arrows mark the reading order: start at the last line, which says what went wrong; the frame above it says where; the frames above that say how the program got there.">
          __SVG:fig15__
        </svg>
        <figcaption>"Most recent call last" means the answer is at the bottom. Read upwards until you reach your own code, and look there first.</figcaption>
      </figure>

      <h4>Manuals, help and documentation</h4>
      <p>Every command-line tool documents itself. <code>man ls</code> opens the manual page. Its sections are always in the same order: NAME, SYNOPSIS, DESCRIPTION and the options, then often EXAMPLES, FILES, ENVIRONMENT and SEE ALSO. Search inside it with <code>/</code>, press <code>n</code> for the next match, and <code>q</code> to quit. <code>man -k word</code> searches the one-line descriptions of every page. Manuals are grouped in numbered sections, so <code>man 1 crontab</code> is the command and <code>man 5 crontab</code> the file format. Most programs also answer <code>--help</code> with a summary, and the community tldr pages give the five commands people actually type. For languages and libraries, read the official documentation, for the version you have. Python's is excellent, and <code>help(thing)</code> shows it from inside Python.</p>
      <p>A <b>synopsis</b> is a compact grammar for a command's arguments. Square brackets mark something optional, a bar separates alternatives, and an ellipsis means "one or more". <code>cp [-R [-H | -L | -P]] [-f | -i | -n] source_file ... target_directory</code> says that <code>-R</code> is optional, and that <code>-H</code>, <code>-L</code> or <code>-P</code> may follow it. It also says that at most one of <code>-f</code>, <code>-i</code> and <code>-n</code> belongs in a command, and that copying several files requires a folder at the end.</p>
      <p>The example takes a short function that averages prices by category from a menu file, and a real menu of about a hundred lines on which it crashes. It reads the traceback from structured data rather than printing it, because the exact layout of tracebacks changes between versions of Python. Then it hands the failing input to <b>delta debugging</b>, Andreas Zeller's algorithm for shrinking a failing input automatically. The algorithm repeatedly removes chunks of the input and keeps any smaller version that still fails, until removing anything at all makes the failure go away.</p>
      __EXAMPLE:ch15_errors|errors.py &middot; a function that crashes on a hundred-line menu, its traceback read from the bottom up, the input shrunk by delta debugging to the two lines that matter, and the bug report that makes possible__

      <h4>What the example shows</h4>
      <p><b>The traceback pointed straight at the cause.</b> Its last line said <code>ZeroDivisionError: division by zero</code>; the frame above, line 20 in <code>average()</code>, showed the division by <code>len(numbers)</code>, so the list was empty. The frame above that, line 11 in <code>average_prices()</code>, showed when <code>average</code> is called: when a new category starts and the previous one is finished. Together they say "a category had no items". Reading only the first line of the traceback would have told you nothing.</p>
      <p><b>Shrinking found the real conditions.</b> Delta debugging needed 30 runs to cut 104 lines down to two, <code>[specials]</code> and <code>[sides]</code>. Neither line fails alone: an empty category followed by another category is the bug, while an empty category at the very end is handled correctly. That's a fact you'd likely never have found by staring at the hundred-line menu, and it's exactly what the fix needs. The bug report in section 3 says in five lines what a confused paragraph and an attached file would otherwise have left the reader to work out. You can shrink by hand the same way, deleting halves of the input or the code and keeping the failure, as exercise 15.3 does.</p>

      <h4>Asking a good question</h4>
      <p>When you've read the message and the documentation and you're still stuck, ask, and make the question easy to answer. Give a <b>minimal, reproducible example</b>: the smallest complete program and input that show the problem, which someone else can run and see fail. Say what you expected and what happened instead, with the exact error copied as text, never a screenshot. Name the versions of everything involved, and list what you've already tried and ruled out. Making that example is itself a debugging technique: in shrinking the problem, you'll often find it. So will explaining it out loud to anyone, or anything, which is why programmers talk of rubber-duck debugging. The same rules apply when the one you ask is an AI assistant. Give it the minimal example and the exact error, and then check its answer, because you have to be able to explain every line you ship.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Reading the first line of a traceback</b> instead of the last.</li>
          <li><b>Searching for an error with your own paths and names in it,</b> which no one else's copy contains.</li>
          <li><b>Screenshots of code or errors,</b> which can't be searched, copied or run.</li>
          <li><b>"It doesn't work",</b> without what you expected, what happened, and what you tried.</li>
          <li><b>Asking before reading,</b> when the answer is in the message or the manual.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 15.1</span><span class="ex-title">Read a synopsis</span></div>
          <p>A Mac's <code>cp</code> manual begins <code>cp [-R [-H | -L | -P]] [-f | -i | -n] [-aclNpSsvXx] source_file target_file</code>. According to it: (a) can you write <code>cp -L a b</code>? (b) <code>cp -f -n a b</code>? (c) <code>cp -R notes backup</code>? (d) What do you need to copy three files at once?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>(a) Not on this line: <code>-L</code> appears only inside the brackets that begin with <code>-R</code>, so it's meant for recursive copies, where it says to follow symbolic links. (b) No: <code>[-f | -i | -n]</code> allows at most one of the three. (c) Yes: <code>-R</code> is optional, and it's the option for copying folders. (d) The page's second form, <code>source_file ... target_directory</code>: any number of files, then an existing folder. One more lesson comes from trying them. The Mac's <code>cp</code> accepted both <code>cp -H a b</code> and <code>cp -f -n a b</code> without complaint. Its description explains why: <code>-H</code>, <code>-L</code> and <code>-P</code> are ignored unless <code>-R</code> is given, and when several of <code>-f</code>, <code>-i</code> and <code>-n</code> are given, the last one wins. A synopsis states the intended grammar, and tools are often more forgiving than it. So read the description too, and never rely on undocumented leniency in a script.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 15.2</span><span class="ex-title">Rewrite the question</span></div>
          <p>Rewrite this as a question someone could answer: "My Python script doesn't work!! I get an error about division. Attached is a screenshot and my menu file. Please help ASAP."</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">average_prices() raises ZeroDivisionError for an empty category followed by another

With Python 3.13, this function, from our menu tool, crashes on a menu where
a category has no items yet:

    average_prices("[specials]\n[sides]")

Expected: no entry for "specials" (or None), and no crash.
Actual:   ZeroDivisionError: division by zero, in average(), called from
          average_prices() at the line that closes the previous category.

An empty category at the end of the menu works. I think the final check
"if category is not None and prices" is missing where a new category
starts, but I'm not sure whether skipping the category or recording None
is the expected behaviour. Which do the callers rely on?</code></pre>
            <p>The title states the problem in a line, so the right person recognises it. The two-line reproduction replaces the screenshot and the whole menu file, and anyone can paste it and see the error. Expected and actual are stated separately, with the exact message as text. The version is given. And the last paragraph shows what you've worked out and asks the one thing you can't decide alone, which is the question that gets answered. "ASAP" is gone: urgency is yours, and a good question is the fastest way to an answer.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 15.3</span><span class="ex-title">Shrink it by hand</span></div>
          <p>A 40-line script that loads a configuration file and processes some records fails with <code>KeyError: 'region'</code>, deep inside a library call. Describe how to cut it down to a minimal reproduction.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Work like delta debugging, by hand, and run the script after every change to make sure it still fails the same way. First make the failure independent of everything outside the script: replace the configuration file and the records with literal values copied into the code, so that it fails on any machine. Then delete half of what's left, the code or the data, and run it. If it still fails, keep the deletion; if not, put it back and try the other half, or a smaller piece. Replace each function call you don't suspect by the value it returns. Stop when every remaining line is needed for the failure. Usually you finish with three or four lines and a single record, often one with no <code>region</code> field. By then you can see whether the library expects the field, which its documentation will say, or your code should have supplied it. Commit the starting point first, so you can always get back to it.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you read a traceback from the bottom, and find the frame to look at first?</li>
            <li>Can you find an answer in a manual page, using its sections and its search?</li>
            <li>Can you decode a synopsis's brackets, bars and ellipses?</li>
            <li>Can you shrink a failing program or input to a minimal reproduction?</li>
            <li>Can you write a question with a reproduction, expected and actual results, and what you tried?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Guide</span><div><a href="https://stackoverflow.com/help/minimal-reproducible-example">How to create a Minimal, Reproducible Example</a> <span class="by">Stack Overflow</span></div></li>
            <li><span class="rkind free">Book</span><div><a href="https://www.debuggingbook.org/html/DeltaDebugger.html">The Debugging Book: Reducing Failure-Inducing Inputs</a> <span class="by">Andreas Zeller</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://www.chiark.greenend.org.uk/~sgtatham/bugs.html">How to Report Bugs Effectively</a> <span class="by">Simon Tatham</span></div></li>
          </ul>
        </div>
      </div>
    </section>
