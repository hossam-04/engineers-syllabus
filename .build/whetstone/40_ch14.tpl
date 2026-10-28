    <div class="part" id="part4">
      <span class="part-num">Part IV</span>
      <h2>Learning the craft</h2>
      <p>Three chapters on the skills underneath every other one. The editor where you'll spend more working hours than anywhere else, and how to make it disappear from your attention. Error messages and documentation, which answer most questions before you ask anyone, and how to ask well when they don't. And the science of learning itself: why rereading feels productive and isn't, and what to do instead. The last chapter can be read at any time, and pays off most if you read it first.</p>
    </div>

    <section class="chapter prose" id="ch14" data-ch="14">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 14</span><label class="done-toggle"><input type="checkbox" data-id="ch14"><span class="box"></span>Read</label></div>
        <h3>One editor, to fluency</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Your editor is where you'll spend more working hours than anywhere else, so learning one deeply pays back every day. Fluency means moving without the mouse, opening any file or symbol in a keystroke, editing many places at once, and letting the editor understand your code well enough to rename a function safely. Pick one editor and practise it deliberately, the way chapter 16 describes. Under its best features are simple algorithms, and this chapter builds three of them: fuzzy file finding, search across files, and a rename that knows what each name refers to.</p>
      </header>

      <h4>Pick one, and go deep</h4>
      <p>The choice matters much less than the depth. Visual Studio Code is the most widely used, free, and extensible for any language. JetBrains' editors, such as PyCharm, understand code most deeply out of the box. Vim and its descendant Neovim are modal editors, controlled entirely from the keyboard, steep to learn and very fast once learned, and available on every server. Emacs is a world of its own. Choose one, use it for everything, and give it a year. Whatever you choose, learn enough Vim to survive: it's what opens when Git wants a commit message on a machine you've never configured. <code>i</code> starts typing, Escape stops, <code>:wq</code> saves and quits, <code>:q!</code> quits without saving. Then set <code>EDITOR</code> in your dotfiles to the editor you chose.</p>

      <h4>What fluency means</h4>
      <p>Fluency is a list of things you can do without thinking. You can open any file by typing a few letters of its name, jump to any function or class by name, go to a definition and back again, and list every reference to a name. You can search the whole project, with a regular expression and a filter by file type, and replace across it after reviewing each change. You can put a cursor on many lines at once, or select every occurrence of a word and type once, rename a symbol everywhere it's used, and format a file on save. You can use the built-in terminal, the Git view to stage single hunks and see blame, and the debugger. The <b>command palette</b>, which finds any command by typing part of its name and shows its shortcut, is the key that unlocks the rest: when you don't know how to do something, ask the palette, and note the shortcut it shows you.</p>
      <p>Learn the actions in small batches, by practice, not by reading lists. Each week, choose three to five things you do often and slowly, learn their keys, and make yourself use them even when it's slower at first; after a week they're habits. Vim has a built-in thirty-minute course, <code>vimtutor</code>. VS Code publishes a one-page shortcut reference for each system. Time a common task, such as finding and renaming a function, before and after a week of practice, and you'll see why the investment pays.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 270" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The query mdl matched against the path src/shop/models/data_loader.py. The m matches the start of the word models, the d the start of data, and the l the start of loader: each is at the start of a word, worth a large bonus, and the d and l are in the file name, worth a little more. Letters skipped between matches cost a little. The total, 28.1, ranks the file first; tests/test_models.py scores 15.5, because its d and l are in the middle of a word.">
          __SVG:fig14__
        </svg>
        <figcaption>Fuzzy finding rewards letters that start words, which is why typing the initials of a path finds a file faster than typing its name.</figcaption>
      </figure>

      <h4>Under the features</h4>
      <p><b>Fuzzy finding</b> scores every file path against the letters you've typed, in order, with gaps allowed, and shows the best first. Letters that start a word, after a <code>/</code>, <code>_</code>, <code>-</code> or <code>.</code>, are worth most, letters right after the previous match a lot, and letters in the file name rather than the folders a little more; letters skipped in between cost a little. The example finds the best alignment of the query in each path, the way fzf and VS Code do. <b>Search across files</b> is a scan of every line of every file, as chapter 3's <code>grep -rn</code>; ripgrep and the editors that use it make it fast by searching files in parallel and skipping those Git ignores. <b>Rename</b> is the one that needs real understanding. To rename a function, an editor has to know which uses of the name refer to that function, and which are a different variable, a string, or an attribute that happens to share it.</p>
      __EXAMPLE:ch14_editor|editor.py &middot; a fuzzy file finder that scores letters at word starts, a search across files, and three ways to rename a function, only one of them correct__

      <h4>What the example shows</h4>
      <p><b>Initials find files.</b> <code>mdl</code> picked <code>src/shop/models/data_loader.py</code> because its three letters start three words; the same letters in the middle of <code>test_models.py</code> scored about half as much. <code>tmod</code> found the one test file with <code>t</code>, <code>m</code>, <code>o</code>, <code>d</code> at word starts. And <code>ord</code> gave a near tie between three files, which is the honest answer to an ambiguous query: type one more letter. Exercise 14.3 tunes the scorer to break that tie the way most people would want.</p>
      <p><b>Text replacement doesn't understand code.</b> Replacing every <code>total</code> with <code>grand_total</code> changed all four lines that contain it, so it renamed the class attribute <code>Receipt.total</code>, which is a different thing. It also turned the variable <code>totals</code> into <code>grand_totals</code> and changed the printed text <code>"total:"</code>. Whole-word replacement, <code>\btotal\b</code>, spared <code>totals</code> but still broke the other two. The rename that walked Python's syntax tree changed exactly three places: the definition and the two calls. It knew that <code>total = 0</code> inside the class body defines something new, and that a string is not a name. Every version still compiles, which is the danger: the wrong renames produce working code that does the wrong thing.</p>

      <h4>Language servers</h4>
      <p>Editors used to need separate support for every language. The <b>Language Server Protocol</b>, published by Microsoft in 2016, split the job in two. A language server, such as pyright or basedpyright for Python, rust-analyzer for Rust or gopls for Go, understands one language: it parses your project, resolves names, and answers questions. Any editor that speaks the protocol can ask them: complete this, where is this defined, what refers to it, rename it, what's wrong with this line. That's why Neovim and VS Code can offer the same rename, and why setting up the language server is the most valuable configuration step for any language you use. Add a formatter, such as ruff or black for Python or Prettier for the web, and a linter that runs as you type, and the editor catches whole classes of mistakes before you run anything. Put the project's settings in the repository, for instance in an <code>.editorconfig</code> file for indentation and line endings, so everyone's editor agrees.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Switching editors every few months,</b> and never getting past the basics of any.</li>
          <li><b>Renaming with find-and-replace</b> across a project, instead of the editor's rename.</li>
          <li><b>Hunting through menus</b> instead of asking the command palette.</li>
          <li><b>Not knowing how to leave Vim</b> when Git opens it for a commit message.</li>
          <li><b>Installing dozens of extensions at once;</b> add one when you've felt the need for it.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 14.1</span><span class="ex-title">Your ten actions</span></div>
          <p>List the ten things you do most often in your editor, find the keyboard shortcut for each, and plan how to make them habits over two weeks.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">VS Code, default keys (Cmd on a Mac, Ctrl on Windows and Linux)
go to file                 Cmd/Ctrl+P
command palette            Cmd/Ctrl+Shift+P
go to definition           F12
find all references        Shift+F12
rename symbol              F2
search in all files        Cmd/Ctrl+Shift+F
select next occurrence     Cmd/Ctrl+D
extra cursor               Option/Alt+Click
show or hide the terminal  Ctrl+`
comment out a line         Cmd/Ctrl+/</code></pre>
            <p>That's a typical list for VS Code; your ten will depend on your work, which is why making the list yourself matters. Watch yourself for a day and note what you do with the mouse or do slowly. For the plan, take five in the first week and five in the second, write them on a card next to your screen, and when you catch yourself reaching for the mouse, undo and do it with the keys. Each takes a few days to become automatic. Every editor lets you change its keys, but learn the defaults first, because they're what tutorials, colleagues and other machines use. In Vim, the equivalents of the first few come from plugins such as fzf or Telescope, and from the language server: <code>gd</code> to go to a definition, <code>gr</code> for references in many setups.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 14.2</span><span class="ex-title">The right tool for each edit</span></div>
          <p>Which editor feature fits each task? (a) Rename a function used in 40 files. (b) Add a comma to the end of 12 consecutive lines. (c) Change <code>http://</code> to <code>https://</code> in every YAML file in the project. (d) Swap the two arguments of every call to <code>move(a, b)</code>.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>(a) <b>Rename symbol</b>, F2 in VS Code, which uses the language server to change only real references, as the example showed. (b) <b>Multiple cursors</b>: put a cursor on each of the twelve lines, by column selection or by adding cursors line by line, press End, type the comma once. (c) <b>Search and replace across files</b>, with the file filter set to <code>*.yml,*.yaml</code>. Review each match before replacing, because some may be URLs that shouldn't change, such as a local server without HTTPS. Commit just before, so <code>git diff</code> shows exactly what changed. (d) This one has no perfect tool. A regular-expression replacement such as <code>move\((\w+), (\w+)\)</code> to <code>move($2, $1)</code> handles simple arguments, but breaks on arguments that are themselves calls with commas inside. Some languages' tools offer a "change signature" refactoring that does it properly. Whichever you use, run the tests afterwards. The general rule is the example's: the more an edit depends on meaning rather than text, the more you want a tool that understands the code.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 14.3</span><span class="ex-title">Break the tie</span></div>
          <p>For the query <code>ord</code>, the example's scorer ranked <code>tests/test_order_detail.py</code> just above <code>src/shop/models/order.py</code>. Change the scoring so that a match at the very start of the file name wins, and shorter paths win near-ties.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-python">def better(query, path):
    hit = fuzzy(query, path)                     # the example's scorer
    if not hit: return None
    score, at = hit
    if at[0] == path.rfind("/") + 1: score += 10  # the query starts the file name
    return score - 0.1 * len(path), at           # and shorter paths win near-ties</code></pre>
            <p>With those two changes, <code>ord</code> ranks <code>src/shop/models/order.py</code> first, then <code>views/order_detail.py</code>, then the test file, which is what someone typing <code>ord</code> most likely wants. The other queries keep their order: <code>mdl</code> still finds <code>data_loader.py</code>, and <code>tmod</code> the test file. Real editors combine more signals still, such as files you opened recently and files near the one you're in. Ranking is a design decision, not a fact, and the right test is whether the file you wanted appears first, on the queries people really type.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you open any file and jump to any symbol in your editor without the mouse?</li>
            <li>Can you go to a definition, find all references, and rename a symbol safely?</li>
            <li>Can you search and replace across a project with a regular expression and a file filter?</li>
            <li>Can you edit many places at once with multiple cursors?</li>
            <li>Can you exit Vim, and have you set <code>EDITOR</code> to the editor you chose?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Course</span><div><a href="https://missing.csail.mit.edu/2020/editors/">The Missing Semester: Editors (Vim)</a> <span class="by">MIT</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://code.visualstudio.com/docs/editing/codebasics">VS Code: Basic Editing</a> <span class="by">Microsoft</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://microsoft.github.io/language-server-protocol/">The Language Server Protocol</a> <span class="by">Microsoft</span></div></li>
          </ul>
        </div>
      </div>
    </section>
