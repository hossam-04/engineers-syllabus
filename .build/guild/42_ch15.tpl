    <section class="chapter prose" id="ch15" data-ch="15">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 15</span><label class="done-toggle"><input type="checkbox" data-id="ch15"><span class="box"></span>Read</label></div>
        <h3>Finishing things</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">The syllabus calls them the boring virtues: reliability, clear communication, finishing things. They're boring because they're not clever, and they're the reason some engineers are trusted with everything. Finishing has a mathematics, Little's law: at a given rate of completion, the more you have in progress, the longer each thing takes. Starting everything feels productive and makes everything slower. Limit what's in progress, finish before starting, and do what you said you'd do or say early that you won't.</p>
      </header>

      <h4>The boring virtues</h4>
      <p>Ask engineers whom they'd most want on a difficult project and the answers are rarely the most brilliant people they know. They name the ones who do what they say they'll do, who say clearly what's happening, and who finish. Those virtues are boring in the sense that nobody writes papers about them, and they compound: every commitment kept makes the next request to you more likely, and every project finished frees attention for the next. An engineer with modest technical depth and these virtues is often more valuable than a brilliant one without them, and an engineer with both is the one the syllabus is trying to produce.</p>
      <p>The previous chapters covered communication: design documents, status updates, writing in public. This chapter is about finishing, which turns out to have a precise mathematical basis, and about reliability, which is mostly a set of habits.</p>

      <h4>Little's law</h4>
      <p>In 1961, John Little proved a result that holds for almost any stable system where things arrive, wait, get worked on and leave: the average number of items in the system equals the rate at which they finish multiplied by the average time each spends inside. In symbols, <i>L</i> = &lambda;<i>W</i>. It needs no assumptions about the distribution of arrivals or of work, which is why it applies to request queues in a server, cars on a road and tickets on a team's board alike.</p>
      <p>Rearranged, it says something uncomfortable about how teams work: the time each item takes, <i>W</i>, equals the number in progress, <i>L</i>, divided by the rate of finishing, &lambda;. If a team finishes three items a week and has twelve in progress, each takes four weeks on average. Have twenty-four in progress at the same rate, and each takes eight. Starting more work doesn't finish it faster; at a given throughput, it only makes every item take longer. And in practice it lowers throughput too, because people juggling several items lose time switching between them, a cost Gerald Weinberg estimated at about a fifth of a person's time for each additional project they carry.</p>

      <h4>Starting everything, or limiting it</h4>
      <p>The example runs a team of four for two thousand days, with the same stream of requests, 0.75 a day on average, each needing two to six days of focused work, in two ways. In the first, every request is started as soon as it arrives, and people divide their time between everything in progress, losing a little to each extra item they juggle. In the second, the team works on at most four items at once, one each, and the rest wait in a queue until someone is free. Then it checks Little's law for both.</p>
      __EXAMPLE:ch15_flow|flow.py &middot; one team, the same arrivals, two policies: start everything, or limit work in progress to four, with Little's law checked for both__
      <figure class="diagram">
        <svg viewBox="0 0 760 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Average time from asking to done, from the example, split into waiting and being worked on. Start everything: no waiting, 7.1 days in progress, 7.1 days in all, with 5.4 items in progress on average. Limit work in progress to four: 1.7 days waiting in the queue, then 4.5 days in progress, 6.2 days in all, with 3.4 items in progress. Both finish 0.74 items a day.">
          __SVG:fig15__
        </svg>
        <figcaption>Same throughput, same requests. Starting everything removes the queue and makes each item take longer to do; limiting work in progress makes items wait a little before starting, and still finishes them sooner.</figcaption>
      </figure>

      <h4>What the example shows</h4>
      <p><b>Both policies finish the same amount of work,</b> 0.74 items a day, because at this load the team has enough capacity either way. The difference is entirely in how long each item takes.</p>
      <p><b>Starting everything makes everything slower.</b> With every request started at once, 5.4 items are in progress on average, people's attention is divided, and each item takes 7.1 days from start to finish. Limiting work in progress to four, 3.4 items are in progress on average and each takes 4.5 days. Little's law holds for both, to within the noise of the simulation: 5.35 against 0.74 &times; 7.14, and 3.36 against 0.74 &times; 4.51.</p>
      <p><b>Waiting in a queue is faster than starting at once.</b> The surprising number is lead time, from request to done. Under the work-in-progress limit, items wait in the queue for 1.7 days on average before anyone starts them, and they're still finished sooner, 6.2 days against 7.1. Starting a request immediately feels responsive to whoever asked, and it makes their request, and everyone else's, finish later. That's the case behind the Kanban slogan "stop starting, start finishing", and it applies to a person as much as to a team.</p>
      <p>The example's numbers come from invented constants, and the switching cost is deliberately small. Exercise 15.1 shows what happens when the load rises, which is where the difference becomes dramatic.</p>

      <h4>Finishing, personally</h4>
      <p>The same law applies to one engineer's work. Five things in progress, a design document, two reviews, a bug and a migration, means each takes five times as long as it needs to, and the people waiting for each see slow progress on all of them. Keep one main thing, finish it, then take the next. Keep a "not now" list for everything else, which is honest about what's waiting rather than pretending everything is in progress. When an interruption comes, ask whether it's more important than the thing in hand; if it isn't, it goes on the list, with a date if the requester needs one.</p>
      <p>Finishing also means finishing all of it. Chapter 10's last ten percent applies to every task: the pull request isn't done when it's approved but when it's deployed and verified; the bug isn't done when it's fixed but when the reporter knows; the document isn't done until the decision in it is recorded.</p>

      <h4>Reliability</h4>
      <p>Reliability in a person means that what they say will happen does. It's built from small habits. Write down every commitment you make, in one list, so none is forgotten. When you can't keep one, say so as soon as you know, not at the deadline, and offer what you can do instead; a renegotiated commitment costs a little trust, a missed one costs a lot. Follow up: when you ask someone for something, note when you expect it and check then. Close loops: tell people when the thing they asked about is done. Be on time. None of these is hard, which is exactly why doing them consistently is noticed. Over a few years, reliability is what makes people give you the important work, and the important work is what builds a career.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Starting every request at once,</b> to look responsive, and finishing everything later.</li>
          <li><b>Five things in progress,</b> each moving slowly, none finished.</li>
          <li><b>"Done" that isn't:</b> approved but not deployed, fixed but not communicated.</li>
          <li><b>Missing a commitment silently,</b> instead of renegotiating it early.</li>
          <li><b>Commitments kept in your head,</b> where some will be forgotten.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 15.1</span><span class="ex-title">A busier team</span></div>
          <p>Raise the arrival rate to 0.9 a day, by changing the 0.25 in the arrivals line to 0.3. Predict, then run, what happens under each policy.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">                              start everything    limit WIP to 4
finished per day                     0.07              0.88
average in progress                723.16              4.00
cycle time (start->done)           275.40 days         4.50 days
lead time (asked->done)            275.40 days        47.54 days</code></pre>
            <p>Starting everything collapses. At 90% of capacity, the switching cost of juggling many items pushes the team's real capacity below the arrival rate, so work arrives faster than it's finished, the pile in progress grows, more switching makes the team slower still, and throughput falls to almost nothing. The "average in progress" figure isn't an average of anything stable: run the simulation twice as long and it roughly doubles. Little's law no longer balances, because it only applies to a stable system, and this one isn't. With the limit, the team keeps finishing 0.88 items a day, each still takes 4.5 days to do, and the queue absorbs the load: lead time grows to about seven weeks, which is a real problem, but a visible and manageable one. The limit turns overload from a collapse into a queue, and a queue tells you exactly how much work to stop accepting.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 15.2</span><span class="ex-title">Your own work in progress</span></div>
          <p>List everything you currently have in progress, including reviews and promises. Apply Little's law to it, and decide what to finish, what to put on a "not now" list, and what to hand back.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>A typical list is longer than expected: two features, three reviews, a bug, a design document, a promise to look at someone's slow query, an interview loop. Suppose it's nine items, and you finish about three a week. Then by Little's law each takes about three weeks, and the people waiting for the review or the query see nothing for most of that time. Sort them. Finish the small, nearly-done ones first, the reviews and the slow query, this week, because each frees someone else. Pick one main item, the feature or the document, and work on it until it's done. Put the others on a "not now" list, and tell the people waiting when you expect to start, which is far better for them than slow, invisible progress. Hand back anything you can't start for a month, so someone else can. Repeat the audit monthly; the list grows back.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 15.3</span><span class="ex-title">Renegotiating a commitment</span></div>
          <p>You promised a partner team an API by Friday. On Tuesday you realise it won't be ready until the following Wednesday. Write the message.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">Hi Priya, a heads-up on the refunds API I promised for Friday: it won't be ready
until next Wednesday. Pagination turned out to need a schema change I hadn't
expected. Two options, whichever helps you more:
1. On Friday I can give you the endpoint without pagination, which works for
   up to 100 refunds, and add pagination on Wednesday.
2. Or the complete API on Wednesday.
Tell me which, and I'll make it happen. Sorry for the change; I wanted you to
know today rather than on Friday.</code></pre>
            <p>It's sent on Tuesday, the moment you knew, which gives them three days to adjust their own plans. It gives the new date, the reason in one sentence, and options that let them choose what matters to them; often a partial delivery on the original date is what they actually need. It doesn't over-apologise or bury the news. A message like this costs a little trust, and builds more than it costs, because it shows that your dates mean something: when you say Friday, Friday is either true or you'll say so early.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you state Little's law, and use it on a team's board or your own list?</li>
            <li>Does your team limit work in progress, and finish before starting?</li>
            <li>Do you have one main thing, and a "not now" list for the rest?</li>
            <li>Is "done" really done: deployed, verified and communicated?</li>
            <li>Do you write down your commitments, and renegotiate early when you can't keep one?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind paid">Book</span><div><a href="https://www.goodreads.com/book/show/6278270-the-principles-of-product-development-flow">The Principles of Product Development Flow</a> <span class="by">Donald Reinertsen</span></div></li>
            <li><span class="rkind paid">Book</span><div><a href="https://itrevolution.com/product/making-work-visible/">Making Work Visible</a> <span class="by">Dominica DeGrandis</span></div></li>
            <li><span class="rkind free">Paper</span><div><a href="https://pubsonline.informs.org/doi/10.1287/opre.9.3.383">A Proof for the Queuing Formula: L = &lambda;W</a> <span class="by">John D. C. Little, 1961</span></div></li>
          </ul>
        </div>
      </div>
    </section>
