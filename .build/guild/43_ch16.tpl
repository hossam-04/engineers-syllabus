    <section class="chapter prose" id="ch16" data-ch="16">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 16</span><label class="done-toggle"><input type="checkbox" data-id="ch16"><span class="box"></span>Read</label></div>
        <h3>A career that compounds</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Skills, reputation, relationships and written work all compound, but only if they accumulate in one direction and you can see them. Keep a few lines a week about what you did and what it changed, because you won't remember, and the people deciding your next opportunity won't either. Work on problems that matter in your area. Build the body of work the stage asks for, slowly and with other people. And keep a pace you can sustain for decades, because the compounding only works if you're still going.</p>
      </header>

      <h4>What compounds</h4>
      <p>Some things in a career grow on themselves. Depth in one area makes the next layer of it easier to learn. A reputation for reliable, clear work brings better projects, which build more reputation. Relationships with people who trust you bring opportunities you'd never have found. And written work, the archive from chapter 8, keeps finding new readers. Other things don't compound: a sequence of unrelated jobs, each started from scratch; work nobody saw or remembers; knowledge that left with the last project. The difference is mostly direction and visibility. Effort that adds to the same pile, and that someone can see, compounds; effort scattered across many piles, or invisible, doesn't.</p>

      <h4>Remembering what you did</h4>
      <p>Memory is a poor record of your own work. Six months later, the incident you resolved, the design you improved, the colleague you taught are a vague sense of having been busy. That matters when the moment comes to describe your work, in a performance review, a promotion case, an interview or a CV, because what you can't remember can't be counted. Julia Evans calls the cure a <b>brag document</b>: a running record of what you did and why it mattered. The name is half a joke; the practice is entirely serious.</p>
      <p>Keep it simple enough to survive. A plain text file, a line or two each week, with the week, what you did, a tag for the kind of work, and, when you have one, the measured result. Five minutes on Friday afternoon is enough. The example takes three months of such a log and turns it into the summaries you'll need: what themes the work fell into, which have evidence, which weeks have nothing written down, and a first draft of the paragraph a review asks for.</p>
      __EXAMPLE:ch16_worklog|worklog.py &middot; three months of a plain-text work log turned into themes, the evidence for each, the gaps, and a first draft for a review__
      <figure class="diagram">
        <svg viewBox="0 0 760 230" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Entries per theme in the example's work log, split into entries with a measured result and without. Mentoring: 4 entries, none measured. Design: 3, 2 measured. Reliability: 3, 2 measured. Writing: 2, 1 measured. Leadership: 1, none measured. Two weeks, 5 and 10, have no entries.">
          __SVG:fig16__
        </svg>
        <figcaption>Three months of work, by theme. The most frequent theme, mentoring, has no measured results; its evidence is an outcome, which is worth writing down as carefully as a number.</figcaption>
      </figure>

      <h4>What the example shows</h4>
      <p><b>The log knows things you'd forget.</b> Twelve entries over twelve weeks show a quarter that combined design work, reliability, writing, leadership and mentoring, with measured results for half of them: a search migration that cut p95 from 2.4 seconds to 240 ms and support complaints from ten a week to one, a fixed export recovering 3,200 rows a night, alerting that caught two incidents before users did, a post with 4,100 readers. Without the log, the review would mention the search migration and little else.</p>
      <p><b>The most frequent theme has no numbers, and that's fine.</b> Mentoring appears four times and never with a measured result. Mentoring rarely produces numbers; its evidence is outcomes in other people. The log's last mentoring entry, "Priya led her first incident review on her own", is the strongest possible evidence of the earlier three, and it's exactly the kind of thing that's forgotten. Write down outcomes like that as carefully as you'd write down a latency figure.</p>
      <p><b>The gaps are the weeks you won't remember.</b> Weeks 5 and 10 have no entries. Perhaps nothing happened; more likely, something did and wasn't written down. The draft paragraph at the end isn't finished prose, but it's a far better start than a blank page the night before a review, and it's assembled entirely from evidence.</p>

      <h4>Kinds of senior work</h4>
      <p>Senior engineers don't all do the same job. Will Larson's <i>Staff Engineer</i> describes four common shapes, which he calls archetypes. The <b>tech lead</b> guides one team's approach and execution. The <b>architect</b> owns the direction and quality of a critical area across teams. The <b>solver</b> goes deep on the hardest problems wherever they arise, one after another. The <b>right hand</b> extends a senior leader's reach across an organisation. Each needs the depth from Part I and the leadership from Part III, in different mixtures. Knowing which shape suits you, and which your organisation needs, makes the path less mysterious; the work log's themes are often a good first hint.</p>

      <h4>Working on important problems</h4>
      <p>In 1986, Richard Hamming gave a talk at Bell Labs called "You and Your Research", about why some scientists do great work and most don't. Its most famous moment is a question he used to ask colleagues at lunch: what are the most important problems in your field, and why aren't you working on them? Most people, he observed, could name the important problems and had a reason not to be working on any of them. The question translates directly to engineering. What are the problems in your area that, if solved, would matter most to your company, your field or the people who use your systems? Are any of them yours? You don't need to work on the most important problem every day. But a career that never touches one compounds slowly, whatever its effort.</p>

      <h4>The body of work</h4>
      <p>The stage's deliverable, described in the appendix, is "a body of work rather than a project": a maintained open-source contribution, a written archive others cite, and at least one system in production that other engineers depend on and you didn't build alone. Each part compounds in its own way. The contribution builds depth and a public record of judgement, through chapter 5's ladder. The archive builds reputation and keeps teaching, through chapter 8's habit. The production system builds the most valuable credibility of all, having built something real with other people that kept working. None of the three can be finished quickly, and none needs to be. Start all three, small, and let them grow together for years.</p>

      <h4>A pace you can sustain</h4>
      <p>Compounding needs time, and time needs you to still be doing the work. Burnout isn't dedication taken to its limit; it's the end of the compounding, often for years. Protect sleep, holidays and a life outside work, deliberately, as a professional obligation to your future self. Careers have seasons: some years are for intense learning or a demanding project, some for family or health, and a long career has room for both. The engineers who reach real mastery are rarely the ones who worked hardest for two years. They're the ones who kept going, steadily, in one direction, for twenty.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Relying on memory</b> to describe a year of your own work.</li>
          <li><b>Recording only numbers,</b> and losing the outcomes in other people.</li>
          <li><b>Scattering effort</b> across unrelated areas, so nothing compounds.</li>
          <li><b>Never asking Hamming's question,</b> and never touching an important problem.</li>
          <li><b>A pace you can't sustain,</b> which ends the compounding entirely.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 16.1</span><span class="ex-title">Start the log</span></div>
          <p>Write the last four weeks of your work log from memory, then check it against your commits, calendar and chat history. What did memory leave out?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">git log --author="$(git config user.email)" --since=4.weeks --format='%ad %s' --date=short
gh pr list --author @me --state merged --search "merged:>=$(date -v-28d +%F)"</code></pre>
            <p>The first command lists your commits of the last four weeks; the second, if you use GitHub's command-line tool, your merged pull requests (on Linux, use <code>date -d '28 days ago' +%F</code>). Compare them, and your calendar, with what you wrote. Memory usually keeps the big, recent item and loses three kinds of work: the small fixes that each took an afternoon, the help you gave other people, reviews, debugging sessions, answered questions, and the meetings where something got decided because you'd prepared. Those last two are often the most valuable work a senior engineer does and the least visible. Add what you find, then keep the log going from now on, every Friday. Four weeks reconstructed from records is a lesson in why five minutes a week is cheaper.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 16.2</span><span class="ex-title">Which shape fits</span></div>
          <p>Using your log, or the example's, decide which of Larson's four archetypes the work looks most like, and what you'd do to move towards another if you wanted to.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>The example's log looks like a tech lead growing towards an architect. The search migration, led from design document to full rollout with platform and support, is tech-lead work; the design documents, the postmortem and the public writing about the migration show influence beyond one team, the start of an architect's role in search. To move further towards architect, the next step would be owning the direction of search across teams: writing the multi-year plan for it, reviewing other teams' designs that touch it, and becoming the person consulted before search decisions rather than after. To move towards solver instead, the log would need more of the reliability entries, hard problems in unfamiliar parts of the system. The archetypes aren't boxes; they're a vocabulary for deciding, with your manager, what kind of work to seek next.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 16.3</span><span class="ex-title">Hamming's question</span></div>
          <p>Write down the three most important problems in your area, at your company or in the field, and for each, why you aren't working on it.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>For an engineer whose area is databases at a growing company, perhaps: the primary database will run out of headroom in eighteen months and nobody owns the plan; restoring from backup has never been tested at full size; and the field is moving to separating storage from compute, which nobody on the team understands yet. The honest reasons not to be working on them are usually some of these: "it's not my job", "it's too big", "someone senior owns it", "I don't know enough yet". Each has a small first step. Write the one-page analysis of the headroom problem and send it to your manager. Run a full-size restore test on a weekend's staging environment. Read the two papers behind the storage–compute separation and write a summary for the team. Hamming's point was not that you should drop everything for the biggest problem, but that you should know what it is, and that small steps towards it, taken regularly, are how people end up doing the important work.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Do you keep a work log, every week, with results and outcomes?</li>
            <li>Can you describe the last six months of your work, with evidence, in ten minutes?</li>
            <li>Do you know which kind of senior work suits you, and which your organisation needs?</li>
            <li>Can you name the important problems in your area, and is one of them yours?</li>
            <li>Have you started all three parts of the body of work, and is your pace sustainable?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Essay</span><div><a href="https://jvns.ca/blog/brag-documents/">Get your work recognized: write a brag document</a> <span class="by">Julia Evans</span></div></li>
            <li><span class="rkind free">Guide</span><div><a href="https://staffeng.com/guides/staff-archetypes/">Staff archetypes</a> <span class="by">Will Larson</span></div></li>
            <li><span class="rkind free">Talk</span><div><a href="https://www.cs.virginia.edu/~robins/YouAndYourResearch.html">You and Your Research</a> <span class="by">Richard Hamming, 1986</span></div></li>
          </ul>
        </div>
      </div>
    </section>
