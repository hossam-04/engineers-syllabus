    <section class="chapter prose" id="ch14" data-ch="14">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 14</span><label class="done-toggle"><input type="checkbox" data-id="ch14"><span class="box"></span>Read</label></div>
        <h3>Measuring delivery</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">A decade of research on software teams found four measures that predict both speed and stability: how often you deploy, how long a change takes to reach production, how often a deploy causes a failure, and how quickly you recover. They can be computed from data you already have, your Git history and your incident log. Use them to learn, as a team, never to rank individuals, and pair every measure of speed with one of stability, so that improving one can't quietly wreck the other.</p>
      </header>

      <h4>Four keys</h4>
      <p>From 2014, the research programme now called DORA, led by Nicole Forsgren with Jez Humble and Gene Kim, surveyed tens of thousands of engineers about how their teams worked and how their organisations performed. The book that summarised it, <i>Accelerate</i>, published in 2018, identified four measures of software delivery that separated high performers from low:</p>
      <ul>
        <li><b>Deployment frequency:</b> how often the team deploys to production.</li>
        <li><b>Lead time for changes:</b> how long a committed change takes to reach production.</li>
        <li><b>Change failure rate:</b> the share of deploys that cause a failure needing a fix.</li>
        <li><b>Time to restore:</b> how long it takes to recover from such a failure. DORA's recent reports call it failed deployment recovery time.</li>
      </ul>
      <p>The first two measure speed; the last two, stability. The research's most quoted finding is that they don't trade against each other. The teams that deployed most often also had the lowest failure rates and recovered fastest. Speed and stability come from the same practices: small changes, automated testing and deployment, and fast feedback.</p>

      <h4>Computing them from your own history</h4>
      <p>You don't need a vendor's dashboard to know your numbers. Deploys are usually tags or pipeline runs; commits carry timestamps; incidents are in a log or a channel. The example builds a Git repository with six weeks of history, ninety commits, three a day, with deploy tags: for three weeks the team releases once a week, on Friday, and for three weeks it releases every afternoon. An incident log records which deploys caused failures and how long recovery took. The four keys are then computed from the repository itself, using <code>git log</code> between consecutive deploy tags.</p>
      __EXAMPLE:ch14_dora|dora.py &middot; the four DORA metrics computed from a Git history with deploy tags and an incident log, for weekly releases and then daily ones__
      <figure class="diagram">
        <svg viewBox="0 0 760 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The example's four keys, weekly releases against daily releases. Deploys a week: 1 against 5. Lead time, median: 51 hours against 3 hours. Change failure rate: 67% against 13%. Time to restore, median: 4.8 hours against 0.6 hours.">
          __SVG:fig14__
        </svg>
        <figcaption>The same team, the same work, released in smaller batches. Lead time falls because changes stop waiting for the weekly train; failures and recovery improve because each deploy contains less, and less to search when something breaks.</figcaption>
      </figure>

      <h4>What the example shows</h4>
      <p><b>The arithmetic first.</b> Weekly releases bundle fifteen changes into each deploy, and a change committed on Monday morning waits until Friday afternoon, so the median lead time is 51 hours. Releasing daily, three changes go out each afternoon and the median lead time is three hours. That part isn't an assumption: it follows directly from the release schedule and the commit times, and it's the same arithmetic in any team.</p>
      <p><b>The stability numbers come from an invented incident log,</b> so read them for their direction, not their size. Two of the three weekly releases caused incidents, against two of the fifteen daily ones, and the weekly failures took far longer to recover from: 4.8 hours at the median against 0.6. The mechanism behind that direction is real, and it's why the research found what it did. A deploy of fifteen changes has fifteen places a problem could hide; finding which one means bisecting a large batch under pressure, and rolling back undoes all fifteen. A deploy of three changes fails less often, because there's less in it, and when it fails, the culprit is one of three changes written that day by people who still remember them.</p>

      <h4>Goodhart's law</h4>
      <p>The economist Charles Goodhart observed that a statistical regularity tends to collapse once it's used for control; the anthropologist Marilyn Strathern's paraphrase is the one everyone quotes: "when a measure becomes a target, it ceases to be a good measure". Delivery metrics are especially vulnerable. Set a target for deployment frequency and teams deploy empty changes. Rank engineers by commits and they split work into meaningless pieces. Punish change failures and failures stop being reported. Three rules keep the measures honest. Measure <b>teams, never individuals</b>, because software is delivered by teams and individual metrics are both unfair and gamed. <b>Pair speed with stability</b>, always reporting all four together, so that improving one at the expense of another is visible. And use them for <b>learning, not judgement</b>: the question each month is "what's slowing us down, and what would help?", not "who's behind?".</p>

      <h4>Learning from incidents</h4>
      <p>The incident log behind change failure rate is also the richest source of learning a team has, if incidents are examined well. A <b>blameless postmortem</b> asks how the failure happened, not who caused it, on the principle, from safety researchers such as Sidney Dekker, that people's actions made sense to them at the time with the information they had. Find out what that information was, and why it was misleading, and you'll find what to fix: a missing alert, a confusing dashboard, a deploy process that made the mistake easy. Blame finds a person to retrain and leaves the system that tripped them unchanged.</p>
      <p>A useful postmortem has a timeline, the contributing factors, plural, since there's rarely one cause, what went well, and a short list of action items, each with an owner and a date. Then the part most teams skip: check, a month later, that the action items were done. The share of postmortem actions completed is itself a revealing measure of whether a team learns from its incidents or only documents them.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Measuring speed without stability,</b> or the reverse.</li>
          <li><b>Ranking individuals</b> by commits, deploys or tickets closed.</li>
          <li><b>Setting the metric as a target,</b> and getting empty deploys.</li>
          <li><b>Blaming a person for an incident,</b> and leaving the system that tripped them.</li>
          <li><b>Postmortem action items that are never done,</b> or never checked.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 14.1</span><span class="ex-title">Your own lead time</span></div>
          <p>Your team tags each production deploy as <code>deploy-YYYYMMDD-N</code>. Write the commands that print, for the last deploy, how long each commit in it waited between being committed and being deployed.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">last=$(git tag --list 'deploy-*' --sort=-creatordate | sed -n 1p)
prev=$(git tag --list 'deploy-*' --sort=-creatordate | sed -n 2p)
deployed=$(git log -1 --format=%ct "$last")
git log --format='%ct %h %s' "$prev..$last" |
  while read -r committed hash subject; do
    printf '%5.1f h  %s %s\n' "$(echo "($deployed - $committed) / 3600" | bc -l)" "$hash" "$subject"
  done</code></pre>
            <p>The two most recent deploy tags bound the range of commits in the last deploy, <code>git log prev..last</code> lists them with their commit times, and the tag's commit time stands for the deploy time. If tags are created after the commit they point to, use the tag's own date, <code>git for-each-ref --format='%(creatordate:unix)' refs/tags/$last</code>, instead. Two caveats make the number honest. Commit time is when the author committed, which may be long after they started the work, so this measures lead time from commit, as DORA defines it, not from idea. And a merged branch's commits keep their original times, so a branch that sat for a week shows up as a week of lead time, which is exactly the delay worth seeing.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 14.2</span><span class="ex-title">Gaming the target</span></div>
          <p>A director sets a target: every team must deploy at least ten times a week. Predict three ways teams might hit the target without improving anything, and propose a better way to use the measure.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Teams could deploy unchanged code, re-running the pipeline to count a deploy. They could split one change into ten tiny commits deployed separately, which hits the number while adding risk and noise. Or they could deploy to production behind flags that are never turned on, so deploys happen but nothing reaches users. Each hits the target and teaches the organisation nothing. A better use: report all four measures for each team, monthly, without targets, and ask each team what's limiting its lead time. The answers, a slow review queue, a flaky test suite, a manual approval step, point at investments that improve every measure at once. If a target is unavoidable, make it about lead time, the measure that's hardest to game without genuinely shortening the path to production, and always show it beside the change failure rate.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 14.3</span><span class="ex-title">A postmortem outline</span></div>
          <p>Write the outline of a blameless postmortem for the migration that locked the orders table for eleven minutes, from chapter 8.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">Summary: a migration adding a column with a default locked orders for 11 minutes
  at 14:02 on a Tuesday; checkout failed for every customer.
Timeline: 13:55 migration merged; 14:02 deploy starts migration; 14:03 checkout
  error alert; 14:06 on-call joins; 14:09 lock identified; 14:13 migration
  completes on its own; 14:15 recovery confirmed.
Contributing factors:
  - On this database version, adding a column with a default rewrites the table.
  - Migrations run automatically during deploys, at peak hours.
  - The migration review checklist doesn't mention locking.
  - Staging has 1,000 orders, so the rewrite took milliseconds there.
What went well: the alert fired within a minute; on-call found the lock in three.
Actions:
  1. Add lock_timeout to every migration (owner: Ana, 1 Nov).
  2. Add a locking question to the migration checklist (owner: Sam, 25 Oct).
  3. Run large-table migrations outside peak hours, by default (owner: Lee, 8 Nov).
  4. Review in a month that 1 to 3 are done (owner: the author).</code></pre>
            <p>Nothing in it names who wrote the migration, because that's not where the fix is: anyone could have written it, given the checklist, the staging data and the deploy process. The contributing factors are plural and each leads to an action, and the last action is the check that the others were done. That's the difference between a postmortem that changes the system and one that only records the event.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you name the four keys and explain why speed and stability go together?</li>
            <li>Can you compute your team's lead time and deploy frequency from your own history?</li>
            <li>Do you report speed and stability together, for teams, never individuals?</li>
            <li>Do you use the measures for learning rather than targets?</li>
            <li>Are your postmortems blameless, with owned actions that are checked later?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Guide</span><div><a href="https://dora.dev/guides/dora-metrics-four-keys/">DORA's software delivery performance metrics</a> <span class="by">DORA</span></div></li>
            <li><span class="rkind paid">Book</span><div><a href="https://itrevolution.com/product/accelerate/">Accelerate</a> <span class="by">Forsgren, Humble &amp; Kim</span></div></li>
            <li><span class="rkind free">Chapter</span><div><a href="https://sre.google/sre-book/postmortem-culture/">Postmortem Culture: Learning from Failure</a> <span class="by">Google SRE book</span></div></li>
          </ul>
        </div>
      </div>
    </section>
