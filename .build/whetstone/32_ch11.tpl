    <section class="chapter prose" id="ch11" data-ch="11">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 11</span><label class="done-toggle"><input type="checkbox" data-id="ch11"><span class="box"></span>Read</label></div>
        <h3>Merging, rebasing and conflicts</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Merging combines two lines of work by comparing each with the last commit they share, the <b>merge base</b>. A change made on only one side is taken. A place changed on both sides, in different ways, is a <b>conflict</b>: Git can't know which you meant, so it marks the spot and asks you. Rebasing does something else: it replays your commits on top of the other line of work, as new commits with new names. Both can produce the same files. They differ in the history they leave behind, and in who gets hurt when they're used on commits other people already have.</p>
      </header>

      <h4>Two lines of work</h4>
      <p>Two branches that have each gained commits since they last agreed have <b>diverged</b>. The commit they last agreed on is their merge base, which <code>git merge-base main lunch</code> finds by walking back through both histories. If one side has no commits of its own, there's nothing to combine: merging just moves the branch forward to the other's tip, a <b>fast-forward</b>, and no merge commit is made. Otherwise Git performs a <b>three-way merge</b> and records the result in a <b>merge commit</b>, which has two parents and so keeps both histories.</p>

      <h4>The three-way merge</h4>
      <p>For each part of each file, Git looks at three versions: the merge base, ours (the branch you're on) and theirs (the one being merged in). The rule is simple. If neither side changed it, keep it. If only one side changed it, take that side's version: the other side's version is just the old one. If both sides made the same change, take it once. If both changed it differently, it's a conflict. Comparing with the base is what makes this work. With only the two tips, Git couldn't tell "I changed this line" from "you changed it", and every difference would be a question. Git first lines the versions up with a diff, so it works on <b>hunks</b>, runs of changed lines, rather than line numbers, and inserted or deleted lines don't throw it off. Changes that touch or sit right next to each other count as the same hunk, so two edits on neighbouring lines conflict even though they don't overlap.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="On the left, a merge. The merge base, Base menu, has two children: Main: lemon cake on main, and Lunch: sourdough on lunch. A merge commit has both as parents, and its menu takes line 2 from lunch, because only lunch changed it, and line 5 from main, because only main changed it. On the right, a rebase. The branch drinks has two commits, lemonade and coffee, made on top of an older commit. Rebasing onto main replays them as new commits, lemonade prime and coffee prime, on top of main's tip, with new ids; the old commits are left behind, unreferenced, and history becomes a straight line.">
          __SVG:fig11__
        </svg>
        <figcaption>A merge joins two histories with a commit that has two parents. A rebase rewrites one history so it starts later: the same changes, as new commits.</figcaption>
      </figure>
      <p>The example works on a seven-line menu. Two branches change different lines and merge cleanly, then a third changes the same line as one of them and conflicts. A fourth moves forward without a merge commit, and two last commits are rebased onto <code>main</code>. Each command happens a minute after the last, so every id is reproducible.</p>
      __EXAMPLE:ch11_merge|merge.py &middot; a clean three-way merge laid out line by line, a conflict and its markers resolved by hand, a fast-forward, and a rebase with its new commit ids__

      <h4>What the example shows</h4>
      <p><b>The rule, line by line.</b> The table in section 1 is the three-way merge made visible. Line 2 changed only on <code>lunch</code>, so it was taken from <code>lunch</code>; line 5 changed only on <code>main</code>, so it stayed; everything else agreed. Git's merged file matched the rule on every line, and Git asked nothing.</p>
      <p><b>A conflict is a question Git leaves in the file.</b> Since the merge base, <code>main</code> had changed line 2 to <code>Sourdough</code>, and <code>dinner</code> had changed it to <code>Garlic bread</code>. <code>git merge</code> exited with status 1 and listed <code>menu.txt</code> as unmerged. In the file, between <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD</code> and <code>=======</code> is our version, and between that and <code>&gt;&gt;&gt;&gt;&gt;&gt;&gt; dinner</code> theirs; everything outside the markers merged normally. Resolving means editing the file into what it should be, here a line that keeps both ideas, then <code>git add</code> and <code>git commit</code>, which made the merge commit. The graph shows both merges, each with two parents.</p>
      <p><b>A rebase makes new commits.</b> <code>tea</code> was made from <code>main</code>'s tip, so merging it was a fast-forward: <code>main</code> moved to the same commit, with no merge commit. <code>drinks</code> had been started from the very first commit. Rebasing it onto <code>main</code> replayed its two commits on top of <code>main</code>'s tip. Each came out with a new id, because its parent and its tree changed, as chapter 9 predicted, but the lines each one added and removed were exactly the same. The old commits still exist, unreferenced, until the reflog lets them go. Afterwards <code>main</code> fast-forwarded to <code>drinks</code>, and the newest part of history is a straight line.</p>

      <h4>Resolving conflicts well</h4>
      <p>A conflict means two people had different intentions for the same lines, so resolve it by understanding both, not by picking a side. <code>git log --merge -p file</code> shows the commits on each side that touched the file. Setting <code>merge.conflictStyle</code> to <code>zdiff3</code> adds a third section to each conflict, the base version, so you can see what each side changed rather than just what each side ended with. It's the most useful Git setting few people know, and belongs in your dotfiles. Once the file is right, run the tests before committing, because a merge can be textually clean and still wrong: one side renames a function while the other adds a new call to it. If it gets confusing, <code>git merge --abort</code> or <code>git rebase --abort</code> puts everything back as it was. <code>git diff --check</code> catches leftover markers before you commit them.</p>

      <h4>Merge or rebase?</h4>
      <p>Both are good tools for different jobs. <b>Rebase your own work</b> to keep it current and tidy before you share it. Replaying your unpushed commits on top of the latest <code>main</code> means your eventual merge is simple, and an interactive rebase, <code>git rebase -i</code>, lets you reorder, combine and reword them first. <b>Merge to combine shared work</b>, because a merge adds a commit and changes none. And follow the one rule that matters: <b>never rebase commits that other people already have.</b> To them, your rebased commits are new and unrelated, and their next pull brings in both versions. <code>git pull --rebase</code> is safe, because it only replays the local commits you haven't pushed.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Committing conflict markers;</b> <code>git diff --check</code> finds them.</li>
          <li><b>Rebasing a branch that others have pulled,</b> which duplicates its commits for everyone.</li>
          <li><b>Resolving by taking one side wholesale</b> without reading what the other side changed.</li>
          <li><b>Long-lived branches</b> that drift until merging them takes days; integrate often.</li>
          <li><b>Forgetting that <code>--abort</code> exists,</b> and improvising in the middle of a merge.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 11.1</span><span class="ex-title">Apply the rule</span></div>
          <p>For each of five lines, far enough apart that their changes don't touch, give the merged result or say it conflicts: (1) base <code>a</code>, ours <code>a</code>, theirs <code>b</code>; (2) base <code>x</code>, ours <code>y</code>, theirs <code>y</code>; (3) base <code>p</code>, ours <code>q</code>, theirs <code>r</code>; (4) all three <code>m</code>; (5) base <code>k</code>, ours deleted the line, theirs <code>k</code>.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>(1) <code>b</code>: only theirs changed it. (2) <code>y</code>: both made the same change, which is taken once. (3) A conflict: both changed it, differently. (4) <code>m</code>: nobody changed it. (5) The line is deleted: only ours changed it, and a deletion is a change like any other. <code>git merge-file</code>, which runs Git's three-way merge on three files, agrees on all five, with a single conflict on line 3. Case 5 surprises people. If theirs had edited line <code>k</code> while ours deleted it, that would be a conflict, because Git can't know whether the edit matters more than the deletion.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 11.2</span><span class="ex-title">The rebase that hurt</span></div>
          <p>You pushed a branch, a colleague pulled it and built on it, and then you rebased the branch onto the latest <code>main</code> and force-pushed. What happens when your colleague next pulls, and how should each of you recover?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Your colleague's commits sit on top of your <i>old</i> commits, A, B and C, while the branch on the server now holds new ones, A', B' and C', with the same changes and different ids. A plain <code>git pull</code> merges the two histories, so their branch now contains every change twice, once in each set of commits. Any of them that touched the same lines conflicts with its own copy. To recover, your colleague should replay only their own commits onto the new branch: <code>git pull --rebase</code> usually manages that by itself, because it recognises commits whose changes are already upstream and skips them; failing that, <code>git rebase --onto origin/branch C</code> moves exactly the commits after your old C. The lesson for you is the rule: once a branch is shared, add commits to it, or ask first. If you do need to replace a shared branch's history, push with <code>--force-with-lease</code>, chapter 13's safer force, and tell everyone who has it.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 11.3</span><span class="ex-title">Three buttons</span></div>
          <p>A pull request has three commits. GitHub offers to merge it with a merge commit, to squash and merge, or to rebase and merge. What does <code>main</code>'s history look like after each?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p><b>Create a merge commit:</b> the three commits, unchanged and with their ids, plus a merge commit whose second parent is the last of them. <code>git log --first-parent main</code> shows one entry for the whole pull request, and the details are one level down. <b>Squash and merge:</b> one new commit on <code>main</code> containing all three commits' changes together, with the pull request's title as its message; the original three aren't in <code>main</code>'s history at all. <b>Rebase and merge:</b> the three commits replayed onto <code>main</code> as new commits with new ids, in a straight line, with no merge commit. Squashing gives the tidiest history and loses the steps, which matters to chapter 12's <code>bisect</code> if a pull request was large. Merging keeps everything, and rebasing keeps the steps without the merge. Teams pick one and say so in their contributing guide.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you find the merge base of two branches, and say when a merge will fast-forward?</li>
            <li>Can you apply the three-way rule to predict a merge's result?</li>
            <li>Can you read conflict markers, resolve them by understanding both sides, and finish or abort the merge?</li>
            <li>Can you explain why a rebased commit has a new id but the same change?</li>
            <li>Can you say when to merge, when to rebase, and which commits must never be rebased?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Book</span><div><a href="https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging">Pro Git: Basic Branching and Merging</a> <span class="by">Scott Chacon &amp; Ben Straub</span></div></li>
            <li><span class="rkind free">Book</span><div><a href="https://git-scm.com/book/en/v2/Git-Branching-Rebasing">Pro Git: Rebasing</a> <span class="by">Scott Chacon &amp; Ben Straub</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://git-scm.com/docs/git-merge#_how_conflicts_are_presented">git merge: how conflicts are presented</a> <span class="by">The Git project</span></div></li>
          </ul>
        </div>
      </div>
    </section>
