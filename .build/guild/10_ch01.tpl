    <div class="part" id="part1">
      <span class="part-num">Part I</span>
      <h2>Depth</h2>
      <p>Four chapters on going deep in one area. First, what expertise is and how to choose where to build it, honestly, with an eye on how fragile the choice is. Then the two best ways into any area: its founding papers, read by building their core ideas small enough to run, and its production code, read with a map and a trace rather than from the first line down. By the end of this part you have an area, a reading list, and a method for each.</p>
    </div>

    <section class="chapter prose" id="ch01" data-ch="01">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 01</span><label class="done-toggle"><input type="checkbox" data-id="ch01"><span class="box"></span>Read</label></div>
        <h3>What mastery is</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Expertise isn't one more subject to study. It's three things that grow together: depth in an area you chose, taste built from having been wrong, and the ability to make other engineers better. The first is the one you can plan. Pick the area deliberately, go several levels deeper than your team needs, and expect it to take years rather than months. This chapter is about choosing well, and about knowing how fragile your choice is.</p>
      </header>

      <h4>Depth, taste and leverage</h4>
      <p>Every stage before this one taught breadth: enough of each layer to work across all of them. That's the foundation, and it's what makes an engineer reliable. What makes one exceptional is different. When the database is losing writes at three in the morning, or a design review needs someone who has seen this exact failure before, teams don't call the person who knows a little of everything. They call the person who knows one thing all the way down.</p>
      <p>That depth is the first part of expertise. The second is <b>taste</b>: a sense of which designs will age well and which will hurt, which risks are real and which are noise. Taste isn't mysterious. It's a large store of cases, most of them mistakes, yours and other people's, compressed into fast judgement. The third is <b>leverage</b>: the ability to make that judgement useful to others, through review, design documents, mentoring and writing. An expert whose knowledge stays in their head helps one project at a time. One who can teach it changes how a whole organisation builds.</p>
      <p>This volume covers all three. Part I is about depth: choosing an area and reading your way into it, through papers and production code. Part II is about working in the open, where taste is built and tested: open source, design documents, trade-offs and public writing. Part III is about leading: estimation, sequencing, communication and mentoring. Part IV is about the long game: the business, measurement, finishing things and a career that compounds.</p>

      <h4>Three levels deeper</h4>
      <p>The syllabus asks you to go "three levels deeper than your team needs", which needs unpacking. Think of knowing a technology at four levels. At level 1 you can <b>use</b> it: write the queries, call the API, follow the guide. At level 2 you can <b>configure and debug</b> it: tune it, read its logs, explain why it's slow. At level 3 you know its <b>internals and failure modes</b>: how it stores data, what it does under partition or overload, which of its guarantees are weaker than they sound. At level 4 you can <b>change</b> it: fix bugs in its source, contribute features, or build a smaller version yourself and explain every trade-off you made.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 320" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A T shape. Across the top, a row of sixteen cells for the sixteen stages of the syllabus: breadth. Below one cell, stage 08 databases, a column goes four levels down: 1 use it, 2 configure and debug it, 3 know its internals and failure modes, 4 change it. A dashed line after level 2 marks what most teams need. Levels 3 and 4, below the line, are where you're the one people call.">
          __SVG:fig01__
        </svg>
        <figcaption>Breadth across every stage, depth in one. Most teams need levels 1 and 2 of everything they use; the expert is the person who has gone past the dashed line in one area.</figcaption>
      </figure>
      <p>Most teams need level 1 of most of what they use and level 2 of a few things. "Three levels deeper" means being at level 3 or 4 in something your team relies on, so that you're the person who can answer the questions nobody else can. It doesn't mean ignoring everything else. The T shape, broad across the top and deep in one place, is the usual picture, and the breadth matters: depth in databases is worth far more to someone who also understands the network, the operating system and the product than to someone who doesn't.</p>

      <h4>Choosing where to go deep</h4>
      <p>The hub's tracks, backend and distributed systems, platform, AI engineering, low-level systems, product and frontend, and security, are broad families. Inside each are areas narrow enough to master: storage engines, consensus and replication, query planning, cryptographic engineering, rendering performance. Choose an area, not a track. Four questions help.</p>
      <ul>
        <li><b>Leverage:</b> how often do your team's hardest problems land in this area? Depth that your work uses every week compounds; depth that your work never touches decays.</li>
        <li><b>Curiosity:</b> would you read about it on a free weekend, for years? Mastery takes a decade of attention, and only genuine interest survives that long.</li>
        <li><b>Adjacency:</b> how much of what you already know carries over? An area next to your strengths gets you to level 3 sooner, and the early progress keeps you going.</li>
        <li><b>Demand:</b> how many teams, anywhere, need a deep expert in it? This matters less than people think, because real depth in almost anything is rare, but it matters.</li>
      </ul>
      <p>None of these is decisive on its own, and the honest way to combine them is to write them down, weight them, and then ask how much your answer depends on numbers you guessed. The example does exactly that, for a backend engineer on a payments team weighing five areas.</p>
      __EXAMPLE:ch01_track|track.py &middot; five candidate areas scored against four criteria, then tested for how fragile the winner is__

      <h4>What the example shows</h4>
      <p><b>The weights matter less than you'd expect.</b> Databases wins, two points ahead of distributed systems, and it stays the winner over wide ranges of every weight. Leverage could fall from 3 to 1.5, or curiosity rise from 3 to 4.5, before security overtook it. Arguing about whether curiosity deserves a weight of 3 or 4 is mostly wasted breath.</p>
      <p><b>The scores matter more.</b> A single point, databases' leverage at 4 instead of 5, or its curiosity at 2 instead of 3, hands the win to distributed systems. That's the useful output. It tells you the decision is a near tie between two areas, decided by two judgements you could check. Is the team's hardest work really in the database? Spend a week reading database internals and see whether your curiosity score holds up. A decision matrix is worth less for its answer than for showing you which question to go and answer.</p>
      <p>And notice what didn't come close: machine-learning infrastructure, with the highest demand of all, came last, because nothing in this engineer's work or experience touches it. Demand without leverage or adjacency makes for a slow, lonely start.</p>

      <h4>How long it takes</h4>
      <p>Peter Norvig's essay <i>Teach Yourself Programming in Ten Years</i> borrows a finding from research on expertise in chess, music and sport: world-class performance takes about ten years of deliberate practice, and there's no known shortcut. Engineering is no different. That sounds discouraging until you notice what it implies: if you start now and keep going, you'll have it, and most people never start. A useful level 3 in one area takes perhaps two years of steady effort alongside a job, and level 4 several more.</p>
      <p>The effort needs a shape, or it dissolves into reading whatever crosses your feed. Chapter 16 of <i>The Engineer's Whetstone</i> covers deliberate practice; here, the concrete version is a standing list of the next three things you'll read or build in your area, renewed whenever one is done. The rest of Part I is about two of the best sources: the papers that founded your area, and the production code that implements it.</p>

      <h4>Taste comes from being wrong</h4>
      <p>Taste grows from cases, and the most instructive cases are your own mistakes, but only if you notice them. Memory is generous to its owner: a year later, you'll remember having been fairly sure the migration would be risky, whatever you actually said. The cure is a <b>decision journal</b>. Before a decision that matters, write a few lines: what you decided, what you expected to happen, how confident you were, and what would prove you wrong. Months later, read it back. The surprises are the lessons, and they're the raw material of taste.</p>
      <p>Other people's mistakes count too, and they're cheaper. Postmortems, published incident reports, design documents that describe a rejected alternative and why: read them in your area as you'd read case law. Over time you'll find you can predict the failure before reading how it ended. That's what taste is.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Specialising before you have breadth,</b> so the depth has nothing to connect to.</li>
          <li><b>Choosing by demand alone,</b> an area that's popular but that your work never touches.</li>
          <li><b>Staying at level 2 everywhere,</b> because each new tool feels like progress.</li>
          <li><b>Treating a decision matrix's answer as the decision,</b> rather than as a pointer to what to check.</li>
          <li><b>Remembering your judgement as better than it was,</b> because nothing was written down at the time.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 1.1</span><span class="ex-title">Score your own areas</span></div>
          <p>Change the example's areas, scores and weights to your own. Which area wins, and what's the smallest single change that would make the runner-up win? What would you do in the next month to find out whether that change is true?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Your numbers are yours, but the shape of a good answer is the same. Suppose storage engines beat stream processing by three points, and the smallest flip is your curiosity about storage engines dropping by one. Then the next month's task is a test of that score: read the first four chapters of <i>Database Internals</i> and one paper, LSM trees or a B-tree variant, and notice whether you look forward to it. If the flip were leverage instead, the test would be different: list the last ten hard problems your team hit and count how many were really storage problems. Either way, the exercise turns a vague career question into a small experiment with an answer. If no single change flips the result, the decision isn't close, and you can stop deliberating and start.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 1.2</span><span class="ex-title">Describe level 3</span></div>
          <p>Pick a technology your team uses every day. Write down three things someone at level 3 would know about it that someone at level 2 wouldn't.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>For PostgreSQL, for example. At level 2 you can read <code>EXPLAIN ANALYZE</code> and add an index. At level 3 you know, first, that an <code>UPDATE</code> writes a whole new row version and leaves the old one for vacuum, so a table updated constantly bloats, and a long-running transaction anywhere stops vacuum from reclaiming it. Second, that the planner's row estimates come from sampled statistics with an independence assumption, so correlated columns produce wild misestimates that no index fixes. Third, that <code>synchronous_commit</code>, <code>fsync</code> and replication settings decide what a "committed" transaction survives, and that the defaults trade some of that for speed. Each of these is a failure mode, not a feature, which is the mark of level 3: you know how it breaks. If your three items read like documentation of features, push further.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 1.3</span><span class="ex-title">A decision journal entry</span></div>
          <p>Write a decision journal entry for a technical decision you're facing this month, in no more than eight lines.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">2026-10-23  Decision: add a read replica for reporting, rather than a separate warehouse.
Why: reporting queries are 40% of primary CPU; a replica takes a week, a warehouse a quarter.
Expect: primary CPU down to about 55% at peak within two weeks of the switch.
Confidence: 70%.
I'm wrong if: replica lag makes the finance team's end-of-day report unusable,
              or CPU stays above 70% because the real cost was something else.
Alternatives rejected: query tuning only (tried, saved 10%); a warehouse (too slow to deliver).
Review on: 2026-12-01.</code></pre>
            <p>The entry is short enough that you'll actually write it, and specific enough to be checked: a number, a confidence, a date, and the evidence that would prove it wrong. The "I'm wrong if" line is the most valuable, because it's the one memory rewrites. When you review it in December, record what happened in one line beneath it. After a year of entries, read them all in one sitting: your recurring errors, perhaps always underestimating migration time, or overrating new tools, become obvious, and that's the start of taste.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you name the area you're going deep in, and say why it beat the alternatives?</li>
            <li>Can you describe what level 3 and level 4 mean for it, concretely?</li>
            <li>Do you know which of your judgements your choice depends on, and how you'd test them?</li>
            <li>Do you have a standing list of the next three things to read or build?</li>
            <li>Do you keep a decision journal, and review it?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Guides</span><div><a href="https://staffeng.com/guides/">Staff Engineer: guides</a> <span class="by">Will Larson</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://norvig.com/21-days.html">Teach Yourself Programming in Ten Years</a> <span class="by">Peter Norvig</span></div></li>
            <li><span class="rkind free">Talk</span><div><a href="https://www.cs.virginia.edu/~robins/YouAndYourResearch.html">You and Your Research</a> <span class="by">Richard Hamming, 1986</span></div></li>
          </ul>
        </div>
      </div>
    </section>
