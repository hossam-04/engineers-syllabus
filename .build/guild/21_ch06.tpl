    <section class="chapter prose" id="ch06" data-ch="06">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 06</span><label class="done-toggle"><input type="checkbox" data-id="ch06"><span class="box"></span>Read</label></div>
        <h3>Design documents</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">A design document is how a senior engineer changes a system before writing the code: by thinking it through in writing, and letting sceptical colleagues find the flaws while they're cheap. A good one says what it proposes in its first paragraph, puts numbers on its goals, admits what it won't do, shows the alternatives it rejected and why, and says how it will roll out and roll back. Most weak documents fail the same few checks, and this chapter automates them.</p>
      </header>

      <h4>What a design document is for</h4>
      <p>A design document does three jobs. It's a tool for <b>thinking</b>: writing the design down forces the vague parts into the open, and many designs change, or die, while the document is being written. It's a tool for <b>agreement</b>: the people whose systems the change touches can object before a line of code depends on the design, when changing it costs an afternoon rather than a quarter. And it's a <b>record</b>: a year later, when someone asks why the system works this way, the document answers, alternatives and all.</p>
      <p>Not every change needs one. A design document earns its cost when a change is hard to reverse, crosses team boundaries, or has several plausible approaches. A one-week change inside your own service, with an obvious design, needs a good pull request description instead. The test is simple: if someone could reasonably say "why didn't you just...?" after it's built, write the document first.</p>

      <h4>The shape of a good one</h4>
      <p>Templates vary between companies, but the strong ones share a shape, because each section answers a question a reviewer will otherwise ask.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The sections of a design document, each paired with the reviewer's question it answers. The first paragraph: what are you proposing, in two sentences? Context: why now, with what evidence? Goals and non-goals: how will we know it worked, and what is out of scope? Proposal: how does it work? Alternatives considered: why not the obvious other approaches, including doing nothing? Risks: what could go wrong, and what will you do about it? Rollout: how does it ship, and how do we undo it? Open questions: what is still undecided?">
          __SVG:fig06__
        </svg>
        <figcaption>Every section exists because a reviewer will ask its question anyway. Answer them in the document and the review discusses the design instead.</figcaption>
      </figure>
      <p>Two sections do most of the work and are most often missing. <b>Non-goals</b> prevent the scope argument: "personalised ranking is a separate project" stops a reviewer asking why the design doesn't handle it, and stops the project growing to include it. <b>Alternatives considered</b> is where a document earns trust. A proposal with no alternatives reads as the first idea its author had; one that shows two alternatives, each tested or priced, and explains why it lost, reads as a decision. Always include doing nothing, with its cost, because it's the alternative a sceptical manager is weighing.</p>

      <h4>Writing for sceptical readers</h4>
      <p>The syllabus asks for documents that "survive contact with sceptical senior engineers". Sceptics aren't obstacles; they're the cheapest testing your design will ever get. Write for them. Put the proposal in the first paragraph, so nobody has to read four pages to find out what you want. Replace adjectives with numbers: not "search is slow" but "p95 is 2.4 seconds at 40 queries a second". State your assumptions where they can be attacked. And anticipate the obvious objection in the text: if everyone will ask "why not just add an index?", answer it in the alternatives section before they do.</p>
      <p>Keep it short. A design document that takes an hour to read gets skimmed; one that takes fifteen minutes gets read. Move detail into appendices, and link to the prototype rather than describing it. Diagrams help when they show the change, the new box and the arrows that move, not the whole system.</p>

      <h4>A first-pass reviewer</h4>
      <p>Most weak documents fail the same mechanical checks, long before anyone argues with the design: no stated proposal, goals without numbers, adjectives where measurements should be, no alternatives, risks with no mitigation, a rollout with no way back. The example runs those checks on two drafts of the same document, a search migration, the first as a first draft often looks and the second after revision.</p>
      __EXAMPLE:ch06_designdoc|designdoc.py &middot; the questions a sceptical reviewer asks first, run on a weak draft and a revised one__

      <h4>What the example shows</h4>
      <p><b>The weak draft fails before the design is discussed.</b> Forty-nine words produce eight notes: six missing sections, no stated proposal, and four sentences whose only content is adjectives: slow, faster, scalable, robust, easy, significantly, seamless. A reviewer handed this document has nothing to agree or disagree with. "Make search much faster" can't be wrong, which is exactly why it isn't useful.</p>
      <p><b>The revised draft gives the reviewer something to argue with.</b> It states the proposal and its headline number in the first paragraph, gives a measurable goal three times today's peak load, rules two things out of scope, prices two alternatives and the cost of doing nothing, gives each risk a mitigation, and has a rollout whose rollback is a flag. Its one note is a false alarm: "the slow queries are prefix matches" uses "slow" to identify which queries, not to make a claim. That's worth remembering. A check like this is a checklist, not a judge. It finds what's missing; it can't tell you whether the design is good. That's what the sceptical humans are for.</p>

      <h4>Running the review</h4>
      <p>Send the document to the right readers, not everyone: the owners of every system it touches, someone who will use the result, and at least one person you expect to disagree. Give them a few days to comment in the document, where each objection gets a thread and an answer. Hold a meeting only if threads remain unresolved, and spend it only on those. Record the decision and its date at the top, so readers know whether they're reading a proposal or a plan.</p>
      <p>Decisions outlive their documents, and documents go stale as designs change during building. Two habits help. Update the document when the design changes, or mark it superseded with a link to its replacement. And for the individual decisions inside it, keep short architecture decision records, the format Michael Nygard proposed: a title, the context, the decision and its consequences, one decision per file, numbered, never edited after acceptance, only superseded. A folder of them is the history of why your system is the way it is.</p>

      <h4>Surviving contact</h4>
      <p>The hardest part of a design review isn't technical. When a reviewer finds a real flaw, the right response is thanks, because they just saved you weeks. Separate the design from yourself: the goal is the best design, not your design. Change your mind visibly when the evidence says so, and say what changed it; colleagues trust engineers who can be persuaded far more than ones who can't. And when a decision goes against you after a fair hearing, commit to it fully. "Disagree and commit" works only if the commitment is real, and nothing damages a team's trust faster than someone quietly building the design they lost.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Burying the proposal on page four,</b> after the history of the problem.</li>
          <li><b>Goals without numbers,</b> so nobody can tell later whether it worked.</li>
          <li><b>No alternatives,</b> or straw-man alternatives built only to lose.</li>
          <li><b>A rollout with no rollback,</b> for a change that will need one.</li>
          <li><b>Defending the design instead of testing it,</b> and treating sceptics as opponents.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 6.1</span><span class="ex-title">Goals with numbers</span></div>
          <p>The weak draft's only goal is "make it much faster and more scalable". Rewrite it as two or three goals a reviewer could check after launch.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">- p95 search latency under 300 ms, measured over a week at peak traffic.
- Sustain 120 queries a second, three times today's peak, with p95 still under 300 ms
  in a load test.
- Product changes appear in search results within 60 seconds of the write.</code></pre>
            <p>Each goal has a metric, a threshold and a way to measure it, so after launch it's simply true or false. "Faster" became a latency at a percentile; "scalable" became a throughput with the latency still holding, which is what scalability actually means for a user. The freshness goal wasn't in the original at all; writing measurable goals often exposes requirements nobody had stated, and freshness is exactly the property a search index can quietly break.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 6.2</span><span class="ex-title">The alternatives section</span></div>
          <p>Write the alternatives section the weak draft lacks, for a proposal to move search to Elasticsearch.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">## Alternatives considered
- Do nothing. Complaints grow with traffic, about 8% a month; at that rate,
  p95 passes 4 s within a year.
- Tune the existing Postgres queries with trigram indexes. A one-day test cut p95
  to 900 ms: a real improvement, but three times the goal, and it doesn't help
  typo tolerance.
- A managed search service. Meets every goal with the least operational work, at
  about $4,100 a month against $900 for running our own; worth revisiting if the
  search index's on-call load turns out higher than we expect.</code></pre>
            <p>Each alternative is real, measured or priced, and says why it lost, and the last one even says what would make it win. That's what turns "we will move to Elasticsearch" into a decision a reviewer can evaluate. Note that the cheapest alternative, tuning Postgres, was actually tried. A one-day experiment that rules out the obvious alternative is worth more to a document than any amount of argument.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 6.3</span><span class="ex-title">Answer the sceptic</span></div>
          <p>A senior reviewer comments on the revised draft: "This is a lot of new infrastructure. Have you profiled the slow queries? I suspect an index fixes most of it." Write the reply.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Thank them, and answer with evidence: "Good question, and you're partly right. We profiled the twenty slowest query shapes last month. Eight were missing an index; we added those and p95 for exact matches fell to 180 ms, which is already shipped. The rest are prefix and typo-tolerant matches, and the best index we found, trigram, brings them to 900 ms, still three times the goal. The numbers are in the alternatives section and the profile is linked there. If you see something we missed in it, I'd much rather find out now." The reply concedes what's true, shows the work, points at the evidence, and invites a further challenge. It treats the reviewer as a collaborator testing the design, which is what they are. And if the profile hadn't been done, the right reply is "no, and we should; I'll do it before we go further."</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Does your document say what it proposes in its first paragraph?</li>
            <li>Are its goals measurable, and its non-goals stated?</li>
            <li>Does it show real alternatives, including doing nothing, and why each lost?</li>
            <li>Does every risk have a mitigation, and the rollout a way back?</li>
            <li>Do you send it to someone you expect to disagree, and thank them when they do?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Essay</span><div><a href="https://www.industrialempathy.com/posts/design-docs-at-google/">Design Docs at Google</a> <span class="by">Malte Ubl</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions">Documenting Architecture Decisions</a> <span class="by">Michael Nygard</span></div></li>
            <li><span class="rkind free">Course</span><div><a href="https://developers.google.com/tech-writing">Technical Writing</a> <span class="by">Google for Developers</span></div></li>
          </ul>
        </div>
      </div>
    </section>
