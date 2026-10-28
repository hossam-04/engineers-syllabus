    <section class="chapter prose" id="ch04" data-ch="04">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 04</span><label class="done-toggle"><input type="checkbox" data-id="ch04"><span class="box"></span>Read</label></div>
        <h3>Reading production code</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">The source of the tools you use every day is the most accurate documentation they have, and reading it is how level 2 becomes level 3. But nobody reads a large codebase from the first line. Map it first: its files, its entry points, its dependencies, its history. Then trace what actually runs for one real call, because the code you read and the code that runs are not always the same. And then fix something in it, which is the fastest way to understand any of it.</p>
      </header>

      <h4>Why read the source</h4>
      <p>Documentation describes what the authors intended; source code describes what happens. When they disagree, the code wins, and the disagreements are exactly the cases you need to know about: the edge where a timeout isn't enforced, the default that's different from the one in the manual, the fast path that skips a check. Every expert you admire in an area has read the code at its centre. Linus Torvalds' "use the source, Luke" is a joke, and also the most practical advice in this volume.</p>
      <p>Production code teaches something papers can't: what a design looks like after ten years of bug reports. The paper describes the idea; the code shows the idea plus every special case that real users found. Reading the special cases, and the commit messages that explain them, is how you learn which parts of a design are fragile.</p>

      <h4>Map before you read</h4>
      <p>Approach a codebase the way you'd approach a city: get a map before walking the streets. Four questions, each answered with a tool rather than by reading.</p>
      <ul>
        <li><b>What's here, and how big is it?</b> List the files and count their lines. A thousand-line file in a project of hundred-line files is where the complexity lives.</li>
        <li><b>Where does it start?</b> Find the entry points: <code>main</code>, the public API, the request handler, the <code>__all__</code> of a Python package. Everything else is reached from these.</li>
        <li><b>Who depends on whom?</b> Draw the import graph. A module everything imports is the foundation; one that imports everything is the glue.</li>
        <li><b>What changes, and why?</b> <code>git log --format= --name-only | sort | uniq -c | sort -rn | head</code> lists the most-changed files, which are usually the ones that matter and the ones that hurt. <code>git log -L</code> and <code>git blame</code> show why a line is the way it is.</li>
      </ul>
      <p>The tests are part of the map. A project's test suite is a list of the behaviours its authors cared enough to pin down, written as runnable examples. Reading the tests for a function before the function is often faster than reading the function.</p>

      <h4>Trace what runs</h4>
      <p>A map shows what could run. A trace shows what does, for one concrete input. Debuggers, profilers and logging all give traces; in Python, <code>sys.setprofile</code> lets a few lines of code record every function call, which is what the example uses on the standard library's <code>json</code> package. Tracing first, then reading only the functions on the path, turns a codebase of thousands of lines into a few dozen that matter for your question.</p>
      __EXAMPLE:ch04_codemap|codemap.py &middot; the json package mapped with the ast module, then one call to json.dumps traced, with and without its C accelerator__
      <figure class="diagram">
        <svg viewBox="0 0 760 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Two call paths for one json.dumps call. With the accelerator, the default: dumps calls JSONEncoder.encode, which calls iterencode, which hands the work to c_make_encoder from the C module _json, and no more Python runs. With the accelerator off: the same three calls, then _make_iterencode builds a pure Python encoder whose nested generators _iterencode, _iterencode_dict and _iterencode_list do the work, 49 Python-level calls in all.">
          __SVG:fig04__
        </svg>
        <figcaption>The same call, two paths. By default the encoding happens in C, and most of encoder.py's Python never runs; switch the accelerator off and that Python does the work. Both produce the same output, which is what CPython's tests check.</figcaption>
      </figure>

      <h4>What the example shows</h4>
      <p><b>The map comes first and costs nothing.</b> Six modules, about 1,400 lines in all, with the work split between <code>encoder.py</code> and <code>decoder.py</code>, and <code>decoder.py</code> leaning on <code>scanner.py</code>. The seven names in <code>__all__</code> are the whole public surface. That's enough to know where to look for any question about the package, before reading a single function body.</p>
      <p><b>The code you read isn't always the code that runs.</b> The trace of <code>json.dumps</code> found only three Python calls, then nothing: the encoding itself ran in C, in the <code>_json</code> module, which <code>encoder.py</code> imports if it can. Someone reading <code>_make_iterencode</code>, the most interesting function in the file, would be reading code that, in an ordinary run, never executes. Switch the accelerator off, as CPython's own tests do, and the same call made 49 Python-level calls through eight distinct functions, with identical output. The count is high because each time a generator resumes it counts as a call, and the pure-Python encoder is a tree of nested generators.</p>
      <p>This pattern, a readable implementation with a fast one beside it, is common: Python's <code>heapq</code>, <code>datetime</code> and <code>decimal</code> do it too, as do many libraries in other languages. When a fast path exists, the slow one is usually the specification, and the tests check that the two agree. Knowing which one runs is part of reading the code.</p>

      <h4>Reading strategies that work</h4>
      <p><b>Start from a question.</b> "Where does this library decide to retry?" gives you a search term, a trace to run and a place to stop. "Understand this library" gives you nothing. <b>Follow one request end to end.</b> For a web framework, a database or a message broker, pick one operation and trace it from the socket to the disk and back; most of the architecture is on that path. <b>Keep a map document</b> as you go: the modules, their roles, the path you traced, the surprises. It's your notes for the next time, and, cleaned up, it's documentation the project probably lacks.</p>
      <p>Read the history of the lines that puzzle you. A strange condition in a function is usually a bug fix, and <code>git log -S 'that condition'</code> finds the commit that added it, whose message, linked issue or review thread explains the case it handles. That's the special-case knowledge that makes level 3.</p>

      <h4>Then fix something</h4>
      <p>The syllabus asks you to read the source of a tool you use daily "and fix something in one". Fixing is the fastest way in because it forces every step: reproduce the bug, find the code responsible, understand it well enough to change it safely, write a test that fails before and passes after, and explain the change to a maintainer who knows the code better than you do. Start with a bug you've actually hit, or a "good first issue" in a project you use. A one-line fix with a good test and a clear explanation teaches more about a codebase than a week of reading. Chapter 5 is about the rest of that journey.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Reading from the first line of the first file,</b> without a map or a question.</li>
          <li><b>Reading code that never runs,</b> such as the pure-Python fallback beside a C accelerator.</li>
          <li><b>Skipping the tests,</b> the clearest statement of what the code is meant to do.</li>
          <li><b>Ignoring the history,</b> when the commit message explains the strange line.</li>
          <li><b>Reading without ever changing anything,</b> so understanding is never tested.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 4.1</span><span class="ex-title">Map another package</span></div>
          <p>Point the example's mapping half at the standard library's <code>http</code> package. What are its modules, which is the largest, and where would you start reading to find out how <code>http.server</code> parses a request line?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Replace <code>json</code> with <code>http</code> in the import and the <code>pathlib.Path(...).parent</code> line. The package is small: <code>__init__.py</code> with the <code>HTTPStatus</code> enum, <code>client.py</code>, <code>cookiejar.py</code>, <code>cookies.py</code> and <code>server.py</code>, with <code>cookiejar.py</code> and <code>client.py</code> the largest. For request parsing, the map points straight at <code>server.py</code>'s <code>BaseHTTPRequestHandler</code>, and within it <code>parse_request</code>, which splits the request line into method, path and version and rejects malformed ones. A trace confirms it: run a tiny <code>HTTPServer</code> in a thread, make one request with <code>urllib</code>, and profile the handler; <code>handle_one_request</code> calls <code>parse_request</code>, then the <code>do_GET</code> method. Two minutes of mapping and one trace replace an hour of reading.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 4.2</span><span class="ex-title">Where the change happens</span></div>
          <p>In a Git repository you work in, list the ten most-changed files of the last year. What do you learn, and what would you do with it?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">git log --since=1.year --format= --name-only | grep . | sort | uniq -c | sort -rn | head</code></pre>
            <p>The list usually shows three kinds of file. Some are configuration and dependency files that change with every release, which you can ignore. Some are the genuine centre of the product, the module every feature touches; that's where to read first and where a new engineer most needs a map. And some are files that change often because they're fragile: the same function patched again and again. Those are candidates for the refactoring <i>The Engineer's Craft</i> describes, and combining change frequency with complexity, a long, deeply nested file that changes weekly, is the method Adam Tornhill calls finding hotspots. Bring the list to your team: it's evidence, not opinion, about where the code hurts.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 4.3</span><span class="ex-title">How both paths are tested</span></div>
          <p>CPython ships two JSON encoders, one in C and one in Python. Find out how its test suite makes sure both are tested and give the same results.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>In CPython's source, <code>Lib/test/test_json/__init__.py</code> imports the package twice with <code>import_helper.import_fresh_module</code>: once with <code>_json</code> blocked, giving a pure-Python <code>pyjson</code>, and once with <code>_json</code> fresh, giving <code>cjson</code>. It then defines two mixin classes, <code>PyTest</code> and <code>CTest</code>, that point a test at one or the other, and most test classes are written once and inherited by both, so every test runs against both implementations. If the C accelerator isn't available, the C half is skipped. It's a pattern worth copying in your own code whenever you keep a fast path beside a simple one: one set of tests, run against both, so they can't drift apart. And it's the kind of thing you only learn by reading the tests, because the documentation doesn't mention it.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you map an unfamiliar codebase, files, entry points, imports and history, in under an hour?</li>
            <li>Can you trace which functions run for one real call, and read only those?</li>
            <li>Do you check whether a fast path means the code you're reading doesn't run?</li>
            <li>Do you read the tests and the commit history of puzzling code?</li>
            <li>Have you fixed something, with a test, in a tool you use every day?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Book</span><div><a href="https://aosabook.org/en/">The Architecture of Open Source Applications</a> <span class="by">ed. Brown &amp; Wilson</span></div></li>
            <li><span class="rkind free">Guide</span><div><a href="https://devguide.python.org/">Python Developer's Guide</a> <span class="by">the CPython core team</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://git-scm.com/docs/git-log">git log, including -S and -L</a> <span class="by">Git</span></div></li>
          </ul>
        </div>
      </div>
    </section>
