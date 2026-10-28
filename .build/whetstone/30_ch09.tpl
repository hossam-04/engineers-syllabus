    <div class="part" id="part3">
      <span class="part-num">Part III</span>
      <h2>Git</h2>
      <p>Five chapters on the tool every software team runs on. Git has a reputation for confusing commands, and it earns it, but under the commands is a data structure small enough to draw on a napkin: objects named by their contents, and a few movable names pointing at them. The part builds that structure by hand, then uses it to explain branches, merges, rebases and conflicts. It turns history into a debugging tool, and ends with the workflow of forks and pull requests that collaboration on GitHub runs on. It's the longest part of the stage, so give it the most time.</p>
    </div>

    <section class="chapter prose" id="ch09" data-ch="09">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 9</span><label class="done-toggle"><input type="checkbox" data-id="ch09"><span class="box"></span>Read</label></div>
        <h3>Git's objects</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Git is a store of objects, each named by a hash of its own contents, plus a few names that point into it. A <b>blob</b> is a file's contents, a <b>tree</b> is a folder listing, and a <b>commit</b> is a tree together with its parent commits, an author and a message. Once you see that, Git's behaviour stops being arbitrary. A commit is a snapshot of the whole project, not a list of changes. Identical files are stored once. And changing anything in the past changes the name of every commit after it. This chapter builds all three kinds of object by hand, and gets exactly the names Git does.</p>
      </header>

      <h4>Names made from contents</h4>
      <p>A <b>hash function</b> turns any amount of data into a short, fixed-size number, such that the same input always gives the same number, and the smallest change to the input gives a completely different one. Git uses SHA-1, whose numbers are written as 40 hexadecimal digits, and names every object by the hash of a short header, its type and size, then a zero byte, then its contents. So the name of an object <i>is</i> a summary of what's in it: two people who commit the same file get the same blob name without ever communicating, and if a single bit of a stored object changes, its name no longer matches and Git notices. This is called <b>content addressing</b>. Objects are kept compressed in <code>.git/objects</code>, in a folder named after the first two digits, and later packed together into packfiles to save space.</p>
      <p>In 2017, researchers produced the first two different files with the same SHA-1 hash, at a cost of thousands of years of computing time. Git responded by using a hardened SHA-1 that detects that kind of attack, and it now also supports repositories that use SHA-256 throughout. New repositories still use SHA-1 by default.</p>

      <h4>Blobs, trees and commits</h4>
      <p>A <b>blob</b> holds a file's contents and nothing else: not its name, not its permissions. A <b>tree</b> holds a folder's listing, one entry per name. Each entry has a mode, <code>100644</code> for an ordinary file, <code>100755</code> for an executable one, <code>40000</code> for a subfolder and <code>120000</code> for a symbolic link, then the name, then the id of the blob or tree it refers to. A <b>commit</b> is a few lines of text: the id of the tree for the whole project, the ids of its parent commits, none for the first, two for a merge, then the author and committer with timestamps, a blank line, and the message. A fourth type, the annotated tag, names a commit and adds a message of its own.</p>
      <p>Between your files and a commit sits the <b>index</b>, also called the staging area. <code>git add</code> stores the current contents of a file as a blob, and records its name and id in the index. <code>git commit</code> turns the index into trees, writes a commit pointing at the top tree, and moves the current branch to it, which chapter 10 covers. <code>git status</code> compares three things: the last commit's tree, the index, and the files in your folder, which is why a file can be "staged" and "modified" at once.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Two commits and the objects they name. The second commit, Add opening hours, has the first commit, Start the shop, as its parent. Each commit names a top-level tree, and the two trees are different, because README.md changed: the first tree lists README.md as blob a00621 and the second as blob 9921ce. But both trees list the folder src as the same tree, 5234da, which lists app.py as one blob. Unchanged parts of the project are shared between the snapshots, not copied.">
          __SVG:fig09__
        </svg>
        <figcaption>Every commit is a full snapshot, yet storing one costs only what changed: a new blob, the trees on the path to it, and the commit. Everything else is shared by name.</figcaption>
      </figure>
      <p>The example computes object names in Python the way Git does, with <code>hashlib</code>, and checks each one against Git's own answer. Every commit gets a fixed author and time, so the 40-digit names printed here are the ones you'll get on your machine.</p>
      __EXAMPLE:ch09_objects|objects.py &middot; a blob, a tree and a commit built by hand with SHA-1 and checked against git, then two snapshots sharing what didn't change__

      <h4>What the example shows</h4>
      <p><b>Git's names are just hashes, and you can compute them.</b> The blob for <code>hello</code> and a newline is <code>ce0136...</code> whether you compute it in Python or ask <code>git hash-object</code>, and the file Git stored, decompressed, is exactly the header, a zero byte and the contents. The tree computed by hand, two entries sorted by name with their modes and raw ids, matched <code>git write-tree</code>. The commit was simpler still: four lines of text and a message. Note that <code>cat-file -p</code> prints the folder's mode as <code>040000</code>, padded for display, while the stored tree says <code>40000</code>. Hashing the displayed form would give the wrong answer.</p>
      <p><b>Snapshots share what didn't change.</b> After the README changed, the second commit had a new top tree and a new README blob, but its <code>src</code> folder was the very same tree, <code>5234dadb27</code>, as the first commit's, because nothing in it changed. Adding <code>copy.py</code>, an exact copy of <code>app.py</code>, didn't add an object at all: both names point to one blob. Nine objects hold two complete snapshots: four blobs, three trees and two commits.</p>

      <h4>What follows from the model</h4>
      <p>Several things that puzzle people about Git follow directly. <b>A commit doesn't contain a diff</b>; when you ask for one, Git computes it by comparing two trees. Packfiles do store objects as differences from similar objects, but that's a storage detail, invisible to everything else. <b>Renames aren't recorded</b>: a rename is a blob that disappears from one path and appears at another, and <code>git log --follow</code> and <code>git diff</code> detect it by similarity. <b>Empty folders can't be committed</b>, because a tree lists files and subfolders, and an empty one has nothing to list, which is why projects keep a placeholder file such as <code>.gitkeep</code>. And <b>history can't be edited, only replaced</b>. A commit's name depends on its parent's name, so changing an old commit gives it a new name, which changes its child, and so on to the end, as exercise 9.3 explains.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Thinking a commit stores changes</b> rather than a snapshot of every file.</li>
          <li><b>Expecting Git to track renames or empty folders,</b> which it records neither of.</li>
          <li><b>Committing large binary files</b> that change often: every version is kept for ever. Git LFS is the tool for those.</li>
          <li><b>Expecting <code>git add</code> to stage later edits:</b> it records the contents at that moment.</li>
          <li><b>Editing files under <code>.git</code> by hand,</b> instead of with the commands that keep it consistent.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 9.1</span><span class="ex-title">A hash by hand</span></div>
          <p>Compute the blob id for a file containing <code>hello</code> with no newline at the end, without Git, then check it. Why does <code>echo hello | git hash-object --stdin</code> give a different answer?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-python">import hashlib
data = b"hello"
print(hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest())   # b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0</code></pre>
            <p>The header is the type, a space, the size in bytes as decimal digits, and a zero byte; then come the contents. <code>printf hello | git hash-object --stdin</code> agrees: <code>b6fc4c62...</code>. <code>echo</code> adds a newline, so it hashes six bytes, not five, and gets the example's <code>ce013625...</code>. One invisible character changes the whole name, which is the point of a hash. It's also why a file whose only change is a newline at the end, or Windows line endings, counts as changed to Git.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 9.2</span><span class="ex-title">What a rename costs</span></div>
          <p>In a repository with one committed file, <code>a.txt</code>, you run <code>git mv a.txt b.txt</code> and commit. Which new objects does that create?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Exactly two: a new tree, which lists <code>b.txt</code> instead of <code>a.txt</code>, and a new commit pointing at it. No new blob, because the contents didn't change, and a blob has no name in it. Listing every object before and after, with <code>git cat-file --batch-all-objects --batch-check</code>, shows one tree and one commit added. In a deep folder structure, a rename also creates new trees for each folder on the path from the file up to the top, since each of their listings changes. So does an edit, which is why a commit of a one-line change in a large project is still cheap.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 9.3</span><span class="ex-title">Why history can't be changed</span></div>
          <p>A branch has three commits, A, B and C. You fix a typo in A's message. What happens to B and C, and why does that matter if someone else already has them?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>A's message is part of A's contents, so the fixed commit has a new name, A'. B's contents include its parent's name, which is now A' instead of A, so B must be rewritten as B', with a new name, and C likewise as C'. Changing one commit renames every commit after it. That chain is what makes Git's history trustworthy: a commit's name vouches for the whole history behind it, so two repositories that agree on one name agree on everything before it. It's also what makes rewriting shared history disruptive. Anyone who already has A, B and C still has them, and from Git's point of view your A', B', C' are unrelated new commits. Their next merge will join both copies together, with the same changes appearing twice. Chapter 11's rule follows: rewrite only commits nobody else has.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you explain how Git names an object, and compute a blob's name yourself?</li>
            <li>Can you say what a blob, a tree and a commit each contain?</li>
            <li>Can you explain the index, and what <code>git add</code> and <code>git commit</code> each write?</li>
            <li>Can you explain why identical files and unchanged folders cost nothing extra?</li>
            <li>Can you explain why changing an old commit changes every commit after it?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Book</span><div><a href="https://git-scm.com/book/en/v2/Git-Internals-Git-Objects">Pro Git: Git Objects</a> <span class="by">Scott Chacon &amp; Ben Straub</span></div></li>
            <li><span class="rkind free">Article</span><div><a href="https://jwiegley.github.io/git-from-the-bottom-up/">Git from the Bottom Up</a> <span class="by">John Wiegley</span></div></li>
            <li><span class="rkind free">Article</span><div><a href="https://shattered.io/">SHAttered: the first SHA-1 collision</a> <span class="by">CWI Amsterdam &amp; Google</span></div></li>
          </ul>
        </div>
      </div>
    </section>
