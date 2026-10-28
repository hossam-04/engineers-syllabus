    <section class="chapter prose" id="ch10" data-ch="10">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 10</span><label class="done-toggle"><input type="checkbox" data-id="ch10"><span class="box"></span>Read</label></div>
        <h3>Refs, branches and HEAD</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">A branch is a small file that holds one commit's name, and <code>HEAD</code> is a file that holds the name of the current branch. Committing writes a new commit whose parent is the current one, then moves the current branch forward to it. Almost every other command that seems to rearrange history only moves these names around: switching branches, detaching <code>HEAD</code>, resetting. And nothing you've committed is lost when a name moves, because the reflog remembers everywhere each name has been.</p>
      </header>

      <h4>Names for commits</h4>
      <p>Forty-digit names are for machines. People use <b>refs</b>, named pointers to commits. A branch called <code>main</code> is the file <code>.git/refs/heads/main</code>, which contains one commit's name and a newline: that's all a branch is. Tags live in <code>refs/tags</code>, and chapter 13's remote-tracking branches, like <code>origin/main</code>, in <code>refs/remotes</code>. Git sometimes packs many refs into one file, <code>.git/packed-refs</code>, for speed, and newer versions can store them in a different format altogether. So read refs with <code>git rev-parse main</code> rather than by opening files, as the example does only to show what's there.</p>
      <p>Git understands a small language for naming commits relative to others. <code>HEAD~1</code> is the current commit's parent, and <code>HEAD~3</code> its great-grandparent, following first parents. <code>HEAD^2</code> is a merge's second parent. <code>main@{1}</code> is where <code>main</code> pointed before its last move, from the reflog. Any unambiguous prefix of a commit's name works too, so the seven-digit abbreviations Git prints are enough to type.</p>

      <h4>Committing moves a branch</h4>
      <p><code>HEAD</code> normally contains <code>ref: refs/heads/main</code>, meaning "the current branch is <code>main</code>". When you commit, Git writes a commit whose parent is the commit <code>main</code> points to, then rewrites the file <code>refs/heads/main</code> to hold the new commit's name. No other branch changes. That's the whole of "being on a branch": your next commit will move that name. Making a branch writes one tiny file, so branches cost nothing, and it's normal to make one for every piece of work, however small. <code>git switch name</code> moves <code>HEAD</code> to another branch and updates your files to match its commit. The older <code>git checkout</code> does that too, along with several unrelated things, which is why newer versions of Git split it into <code>switch</code> and <code>restore</code>.</p>

      <h4>Detached HEAD</h4>
      <p><code>HEAD</code> can also hold a commit's name directly, which Git calls a <b>detached HEAD</b>. You get one when you switch to a commit rather than a branch, to look at an old version, and Git puts you in one during a rebase or a bisect. You can commit there, but no branch moves, so the new commits are known only to <code>HEAD</code>. Switch to a branch, and they're no longer reachable from any name. They're not deleted, but they're easy to lose track of, which is why Git warns you when you leave. <code>git switch -c name</code> gives the commits a branch and makes them safe.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 290" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Three stages of the same repository. First, commits A and B, with main pointing at B and HEAD pointing at main; a new branch feature also points at B. Second, after committing C on feature: feature has moved to C, main still points at B, and HEAD points at feature. Third, after detaching HEAD at B and committing D: HEAD points directly at D, whose parent is B, and no branch points at D, so switching back to main leaves it reachable only through the reflog, until a new branch, experiment, is made at it.">
          __SVG:fig10__
        </svg>
        <figcaption>Branches are labels that move when you commit; <code>HEAD</code> says which label moves. A commit with no label pointing at it is only a reflog entry away from being found again.</figcaption>
      </figure>
      <p>The example makes the files visible. It prints the contents of <code>HEAD</code> and of the branch files as it creates a branch, commits on it, detaches <code>HEAD</code>, commits there and switches away, then finds the "lost" commit in the reflog and gives it a name. Last, it moves a branch with <code>reset</code> and moves it back.</p>
      __EXAMPLE:ch10_refs|refs.py &middot; HEAD and branch files read directly while committing, branching, detaching HEAD and switching away, then a lost commit rescued from the reflog, and a reset undone__

      <h4>What the example shows</h4>
      <p><b>A branch is the name of one commit, and it moves.</b> <code>refs/heads/main</code> held <code>c7ebc43f...</code>; making <code>feature</code> wrote a file with the same contents; committing C on <code>feature</code> changed that file and left <code>main</code>'s alone. The graph's labels, <code>(HEAD -&gt; feature)</code> and <code>(main)</code>, are exactly those files drawn on the commits they name.</p>
      <p><b>Unlabelled commits fall out of view, not out of the repository.</b> After detaching at B and committing D, switching back to <code>main</code> left D on no branch, and <code>git log --all</code>, which starts from every ref, no longer showed it. But the reflog for <code>HEAD</code> records each move with the reason, <code>commit: D: an experiment</code> and <code>checkout: moving from ...</code>, and one <code>git branch</code> made D reachable again, joining the graph as a fork from B. Finally, <code>reset --hard</code> moved <code>main</code> back to A, which made B unreachable too. <code>main</code>'s own reflog, <code>87b02ea, c7ebc43, 87b02ea</code>, showed where it had been, and <code>main@{1}</code> put it back.</p>

      <h4>reset, and what really can be lost</h4>
      <p><code>git reset target</code> moves the current branch, along with <code>HEAD</code>, to another commit, and its three modes say what happens to your files. <code>--soft</code> moves only the branch: the undone commit's changes stay staged, ready to be committed again, which is a way to squash several commits into one. <code>--mixed</code>, the default, also resets the index, so the changes stay in your files but unstaged. <code>--hard</code> also overwrites your files to match. That's the one dangerous command in this chapter, because changes you never committed aren't in any object, so no reflog can bring them back. Before a <code>--hard</code> reset, <code>git stash</code> saves uncommitted work as a commit you can restore. For files alone, <code>git restore file</code> discards a file's unstaged changes, and <code>git restore --staged file</code> unstages it.</p>
      <p>Commits themselves are very hard to lose. They stay in the repository as long as a ref or a reflog entry leads to them. Reflog entries are kept for 90 days by default, or 30 for commits that are no longer reachable, and only after that can Git's garbage collection delete them. In practice, if you committed it in the last month, it's still there.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Committing on a detached <code>HEAD</code></b> and switching away without making a branch.</li>
          <li><b><code>git reset --hard</code> with uncommitted changes,</b> the one loss no reflog can undo.</li>
          <li><b>Using <code>reset</code> on commits already pushed;</b> chapter 12's <code>revert</code> undoes them without rewriting history.</li>
          <li><b>Thinking <code>git branch -D</code> deletes the commits;</b> it deletes a name, and prints the commit it pointed to.</li>
          <li><b>Reading <code>.git/refs</code> in scripts</b> instead of asking <code>git rev-parse</code>.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 10.1</span><span class="ex-title">Three kinds of reset</span></div>
          <p>Your last commit added <code>line 2</code> to <code>f.txt</code>. For each of <code>git reset --soft HEAD~1</code>, <code>git reset HEAD~1</code> and <code>git reset --hard HEAD~1</code>, say where the branch points afterwards, what <code>git status</code> shows, and what <code>f.txt</code> contains.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">reset --soft HEAD~1    branch at the first commit   status: M  f.txt (staged)     f.txt: line 1, line 2
reset HEAD~1           branch at the first commit   status:  M f.txt (unstaged)   f.txt: line 1, line 2
reset --hard HEAD~1    branch at the first commit   status: clean                 f.txt: line 1</code></pre>
            <p>All three move the branch identically; they differ in how much else they reset. In <code>git status --short</code>, the first column is the index and the second your files: an <code>M</code> in the first column means the change is staged, and in the second, that it's only in your folder. Each line was checked on a fresh repository. In all three cases the undone commit is still reachable through the reflog, so even the <code>--hard</code> reset here could be undone with <code>git reset --hard HEAD@{1}</code>. What it would destroy for good is any edit to <code>f.txt</code> that hadn't been committed.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 10.2</span><span class="ex-title">The deleted branch</span></div>
          <p>You ran <code>git branch -D feature</code> on the wrong branch, which had a week of unmerged commits. Get it back.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">git branch -D feature
# Deleted branch feature (was 6f8d2ca).     <- the commit it pointed to
git branch feature 6f8d2ca                  # recreate the name; the commits were never deleted

# if that message has scrolled away, the reflog of HEAD remembers being on the branch:
git reflog | grep -m 1 'moving from feature'
git log -1 HEAD@{3}                         # inspect a candidate before recreating the branch</code></pre>
            <p>Deleting a branch deletes the 41-byte file, nothing else. Git even prints the commit it pointed to, so the quickest fix is to recreate the name at that commit. If the message is gone, <code>HEAD</code>'s reflog has an entry from each time you switched away from the branch, and the commit you were on at that moment is the branch's tip, or close to it. Inspect the candidate with <code>git log</code> before recreating the branch.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 10.3</span><span class="ex-title">Tildes and carets</span></div>
          <p>On <code>main</code>, commits A then B; a branch <code>side</code> starts at A and adds S; then <code>side</code> is merged into <code>main</code>. Name the commits that <code>HEAD^</code>, <code>HEAD^2</code>, <code>HEAD~1</code>, <code>HEAD~2</code> and <code>HEAD^2~1</code> refer to.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">HEAD^      B    the merge's first parent: what main pointed to before the merge
HEAD^2     S    the merge's second parent: the branch that was merged in
HEAD~1     B    one step back, following first parents
HEAD~2     A    two steps back, following first parents
HEAD^2~1   A    the second parent, then one step back from it</code></pre>
            <p><code>^</code> chooses among a commit's parents; <code>~</code> walks back through first parents. They only differ at merges, which have two. The first parent is always the branch you were on when you merged, so following <code>~</code> from the tip of <code>main</code> walks <code>main</code>'s own history and skips the details of every merged branch. That's what <code>git log --first-parent</code> shows, and why merge commits, chapter 11's subject, keep a readable summary of a project. Running <code>git log -1 --format=%s</code> on each of the five confirms the answers.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you say what a branch, a tag and <code>HEAD</code> each contain?</li>
            <li>Can you explain what moves when you commit, and what doesn't?</li>
            <li>Can you recognise a detached <code>HEAD</code>, and keep commits made there?</li>
            <li>Can you find and rescue an unreachable commit with the reflog?</li>
            <li>Can you choose between <code>reset --soft</code>, <code>--mixed</code>, <code>--hard</code> and <code>restore</code>?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Book</span><div><a href="https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell">Pro Git: Branches in a Nutshell</a> <span class="by">Scott Chacon &amp; Ben Straub</span></div></li>
            <li><span class="rkind free">Practice</span><div><a href="https://learngitbranching.js.org/">Learn Git Branching</a> <span class="by">Peter Cottle</span></div></li>
            <li><span class="rkind free">Book</span><div><a href="https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified">Pro Git: Reset Demystified</a> <span class="by">Scott Chacon &amp; Ben Straub</span></div></li>
          </ul>
        </div>
      </div>
    </section>
