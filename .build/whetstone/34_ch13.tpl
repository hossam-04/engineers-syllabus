    <section class="chapter prose" id="ch13" data-ch="13">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 13</span><label class="done-toggle"><input type="checkbox" data-id="ch13"><span class="box"></span>Read</label></div>
        <h3>Remotes, forks and pull requests</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">A <b>remote</b> is another copy of the repository, usually on a server. <code>git fetch</code> copies the commits you don't have and moves your record of the remote's branches. <code>git push</code> sends your commits and asks the other side to move one of its branches, which it agrees to only if nothing would be lost. GitHub builds a way of working on top of that: forks, pull requests, review and issues. This chapter simulates GitHub with plain repositories in a folder, and follows one contribution from the first commit to the merge.</p>
      </header>

      <h4>Remotes, fetch and push</h4>
      <p>When you clone a repository, Git records where it came from as a remote called <code>origin</code>, and <code>git remote -v</code> lists your remotes and their addresses. For each branch on a remote, Git keeps a <b>remote-tracking branch</b>, such as <code>origin/main</code>: a ref recording where that branch was the last time you talked to the server. <code>git fetch</code> downloads any commits you're missing and updates those refs; it never touches your own branches. So <code>origin/main</code> is a snapshot, possibly hours old, and comparisons with it are only as fresh as your last fetch. <code>git pull</code> is a fetch followed by a merge of the remote branch into yours, or a rebase onto it if you've configured that.</p>
      <p><code>git push origin feature</code> sends your commits and asks the remote to move its <code>feature</code> to match yours. The remote refuses unless the move is a fast-forward, meaning your branch already contains everything it has. Otherwise, commits someone else pushed would be lost. When the push is refused, fetch, combine their work with yours, and push again. <code>git push -u origin feature</code> also sets <code>origin/feature</code> as your branch's <b>upstream</b>, after which plain <code>git push</code> and <code>git pull</code> know where to go, and <code>git status</code> says how many commits you're ahead or behind.</p>

      <h4>Forks and pull requests</h4>
      <p>On GitHub, you usually can't push to a project you don't maintain. So you <b>fork</b> it, which makes your own copy of the repository on GitHub's servers, clone your fork, and push branches there. A <b>pull request</b> asks the project's maintainers to merge one of your fork's branches into their repository. Around it, GitHub runs the conversation. Reviewers comment on lines, ask for changes or approve; automated checks run the tests; and every new commit you push to the branch updates the pull request. When it's ready, a maintainer merges it with one of chapter 11's three buttons. Inside a team with write access, people skip the fork and push branches to the main repository directly, but the pull request, the review and the checks are the same. <b>Issues</b> are GitHub's bug reports and discussions. A pull request whose description says <code>Fixes #12</code> closes issue 12 when it's merged.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Four repositories. On GitHub, upstream.git, the project, and fork.git, Ada's copy of it made by the Fork button. On their laptops, Grace's clone of upstream, and Ada's clone of her fork, which has two remotes: origin, her fork, and upstream, the project. The flow is numbered: 1, Ada clones her fork; 2, she pushes her branch fix-typo to her fork; 3, she opens a pull request from fork fix-typo to upstream main; 4, she fetches upstream to bring her branch up to date and force-pushes it with a lease; 5, Grace fetches the branch from the fork, merges it and pushes to upstream; 6, Ada pulls upstream's main and pushes it to her fork, so all copies agree.">
          __SVG:fig13__
        </svg>
        <figcaption>A contribution is a round trip: your branch goes to your fork, the pull request asks the project to take it, and the merged result comes back to you from upstream.</figcaption>
      </figure>
      <p>The example plays both parts. Bare repositories in a temporary folder stand in for GitHub: <code>upstream.git</code> is the project, and <code>fork.git</code> Ada's copy of it, made the way the Fork button does, with a server-side clone. Grace maintains the project; Ada contributes a small fix. Each person has their own name and email, and the clock is fixed, so the commit ids are reproducible.</p>
      __EXAMPLE:ch13_remotes|remotes.py &middot; a project, a fork and two clones on disk: a branch pushed to the fork, a push refused, a rebase onto upstream and a push with a lease, the pull request merged, and the fork brought up to date__

      <h4>What the example shows</h4>
      <p><b>Two remotes, two roles.</b> Ada's clone has <code>origin</code>, her fork, where she can push, and <code>upstream</code>, the project, which she reads from. After <code>push -u</code>, <code>git status -sb</code> showed <code>fix-typo...origin/fix-typo</code>: the branch and its upstream, with nothing ahead or behind.</p>
      <p><b>Pushes that would lose work are refused.</b> While Ada worked, Grace pushed a commit to the project. Ada then tried to push a stray commit on <code>main</code> straight to <code>upstream</code>, and was refused with <code>[rejected] (fetch first)</code>: the remote had a commit she'd never seen, and accepting her push would have discarded it. The example uses <code>--porcelain</code> to print that refusal in a stable, machine-readable form. Ada threw the stray commit away with <code>reset --hard origin/main</code>. To bring her branch up to date, she fetched <code>upstream</code> and rebased <code>fix-typo</code> onto <code>upstream/main</code>. Rebasing rewrote her one commit, so the push to her fork needed <code>--force-with-lease</code>, as exercise 13.2 explains.</p>
      <p><b>The merge and the sync.</b> Grace fetched the branch from Ada's fork, merged it with <code>--no-ff</code>, which always makes a merge commit, and used the message GitHub writes, <code>Merge pull request #1 from ada/fix-typo</code>. Then Ada updated her own <code>main</code> with <code>pull --ff-only</code>, pushed it to her fork, and deleted the merged branch there with the refspec <code>:fix-typo</code>, the same as <code>git push origin --delete fix-typo</code>. All four copies of <code>main</code> ended on the same commit.</p>

      <h4>A good pull request</h4>
      <p>Pull requests are read by busy people, so make them easy to review. Keep each one <b>small and about one thing</b>: a reviewer can check two hundred lines carefully, and two thousand only superficially. Write a description that says what changed and why, how you tested it, and what you're unsure about, with a screenshot for anything visible and a link to the issue it fixes. Open it as a <b>draft</b> when you want early feedback. When reviews come, answer every comment, either with a change or with a reason, and push fixes as new commits so reviewers can see what changed since they last looked. When you review someone else's, be specific and kind, and say which comments must be addressed and which are suggestions.</p>
      <p>To talk to GitHub at all, you need to authenticate. Over SSH, make a key with <code>ssh-keygen -t ed25519</code> and add the public half to your GitHub account; chapter 6 explained the permissions the private half needs. Over HTTPS, use a credential manager or a token, never your password. GitHub's command-line tool, <code>gh</code>, does all of this and more: <code>gh auth login</code>, <code>gh repo fork</code>, <code>gh pr create</code> and <code>gh pr checkout</code> turn most of this chapter into single commands.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b><code>git push --force</code></b> over commits someone else added; use <code>--force-with-lease</code>.</li>
          <li><b>Working on your fork's <code>main</code></b> instead of a branch, so it drifts from the project's.</li>
          <li><b>One enormous pull request</b> that mixes a refactoring, a feature and a fix.</li>
          <li><b>Treating <code>origin/main</code> as current</b> without fetching first.</li>
          <li><b>Pulling with a merge by habit,</b> filling history with "Merge branch 'main'" commits; set <code>pull.ff only</code> or <code>pull.rebase true</code>.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 13.1</span><span class="ex-title">What pull does</span></div>
          <p>You and a colleague both committed to <code>main</code> since you last pulled. Describe what <code>git pull</code> does with the default settings, with <code>pull.ff only</code>, and with <code>pull.rebase true</code>. Which would you put in your dotfiles?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>All three start by fetching. With no setting, recent versions of Git refuse and ask you to choose. Older versions, and <code>pull.rebase false</code>, merge <code>origin/main</code> into your <code>main</code>, making a merge commit that joins two lines of the same branch; on a busy team, history fills with them. With <code>pull.ff only</code>, the pull succeeds only when it's a fast-forward, and otherwise stops so you can decide. With <code>pull.rebase true</code>, your local commits are replayed on top of the colleague's, giving a straight line, which is safe because those commits haven't been pushed yet. A good default for your dotfiles is <code>pull.ff only</code>, which never does anything surprising, plus <code>git pull --rebase</code> when you know you want it. Many people set <code>pull.rebase true</code> instead, which is also a sound choice.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 13.2</span><span class="ex-title">A force with a lease</span></div>
          <p>Your pull request's branch is on your fork. A reviewer pushes a small fix-up commit to it, which GitHub allows when maintainers may edit. Not having fetched, you amend your own commit and push with <code>--force</code>. What happens? What would <code>--force-with-lease</code> have done?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p><code>--force</code> replaces the remote branch with yours, whatever it held, so the reviewer's commit vanishes from the branch. Nothing warns either of you. <code>--force-with-lease</code> replaces it only if the remote branch is still where your <code>origin/</code> ref says it was, the last state you saw. Here it had moved, so the push was refused with <code>[rejected] (stale info)</code> and the fix-up survived. Both outcomes were checked with repositories on disk. Then fetch, look at what changed, rebase onto it, and push again. Note the lease is only as good as your remote-tracking ref: if you fetch and push without looking, it's satisfied. Adding <code>--force-if-includes</code> also checks that your branch actually contains what you fetched. Neither is needed for ordinary pushes, only after rewriting history.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 13.3</span><span class="ex-title">The description</span></div>
          <p>Write the pull request description for Ada's change to the README.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">Reword the README's description of the project

The README described the project as "A small recipe site.", which can be
read as a site for small recipes. "A small site for recipes" says what we
mean: the site is small, not the recipes.

Only README.md changes; there's no code or test change.

Fixes #3</code></pre>
            <p>The title is a summary a maintainer can scan in a list of pull requests. The body says what changed and why, in a sentence each, because even a one-line change needs its reason. It also tells the reviewer what not to look for, here no code or tests, which saves them checking. The last line links the issue, which GitHub will close when the change is merged. For a larger change, add how you tested it, what you're unsure about, and screenshots of anything visible. The same discipline as chapter 12's commit messages, one level up.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you explain what <code>fetch</code>, <code>pull</code> and <code>push</code> each change, and what remote-tracking branches are?</li>
            <li>Can you explain why a push is refused, and what to do about it?</li>
            <li>Can you contribute to a project through a fork: branch, push, pull request, update, sync?</li>
            <li>Can you write a pull request that's easy to review, and respond to a review well?</li>
            <li>Can you set up SSH keys or a token to push to GitHub?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Book</span><div><a href="https://git-scm.com/book/en/v2/GitHub-Contributing-to-a-Project">Pro Git: Contributing to a Project on GitHub</a> <span class="by">Scott Chacon &amp; Ben Straub</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests">About pull requests</a> <span class="by">GitHub Docs</span></div></li>
            <li><span class="rkind free">Guide</span><div><a href="https://google.github.io/eng-practices/review/">Code Review Developer Guide</a> <span class="by">Google</span></div></li>
          </ul>
        </div>
      </div>
    </section>
