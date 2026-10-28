    <section class="chapter prose" id="ch07" data-ch="07">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 07</span><label class="done-toggle"><input type="checkbox" data-id="ch07"><span class="box"></span>Read</label></div>
        <h3>Trade-offs, argued both ways</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Taste in trade-offs means being able to argue both sides honestly, and then knowing which fact would settle the argument. Write the uncertain inputs as ranges, not single guesses, run the arithmetic over many possible futures, and look for the assumption that swings the answer. That assumption, not the conclusion, is what the debate should be about. And spend that care where a decision is hard to reverse; most aren't.</p>
      </header>

      <h4>Every option costs something</h4>
      <p>An engineering decision with no downside isn't a decision; it's a chore. The real ones trade something for something: latency for consistency, flexibility for simplicity, money for operational burden, speed now for change later. Juniors argue for the option they like. Seniors can state the best case for each option, including the ones they'd vote against, and say under what conditions each would win. The syllabus calls this "taste in trade-offs, which means being able to argue both sides honestly", and it's a learnable skill with a method.</p>
      <p>The method starts by noticing that most trade-off arguments are disguised disagreements about facts. Two engineers arguing "managed service or run our own" usually agree on the costs once they're written down. What they disagree about is a number neither has stated: how fast traffic will grow, how much time running the system would take. Make those numbers explicit, as ranges, and the argument changes from opinion to evidence.</p>

      <h4>Ranges, not points</h4>
      <p>A single estimate, "it'll take a quarter of an engineer to run", hides how unsure you are. A range, "somewhere between 15% and 60% of an engineer", states it, and invites the right question: what would narrow it? Once every uncertain input is a range, the arithmetic is simple: draw one value of each input from its range, compute the cost of each option, and repeat thousands of times. Each repetition is one possible future. The result isn't one number but a distribution: how often each option wins, and by how much.</p>
      <p>This is called Monte Carlo simulation, and it sounds grander than it is. It's twenty lines of Python and a few honest ranges. Douglas Hubbard's <i>How to Measure Anything</i> argues that the ranges themselves are the valuable part: people asked for a 90% range on a quantity they "can't estimate" usually give a perfectly usable one, and the act of giving it shows which inputs are genuinely uncertain.</p>

      <h4>Find the assumption that decides it</h4>
      <p>Not every uncertainty matters equally. Some inputs, however unsure, barely move the answer; one or two decide it. To find them, split the simulated futures by each input, the half where it was low and the half where it was high, and see how much the answer changes between the halves. The input with the biggest swing is the one to argue about, and the one worth paying to measure. Hubbard calls this the value of information: measure what could change the decision, not what's easy to measure.</p>
      <p>The example applies this to a familiar choice: three years of running your own event-streaming cluster against a managed service, with traffic growth, the share of an engineer spent operating it, the number of serious incidents and their cost all given as ranges.</p>
      __EXAMPLE:ch07_tradeoff|tradeoff.py &middot; three years of running our own cluster against a managed service, over twenty thousand possible futures, and which assumption decides it__
      <figure class="diagram">
        <svg viewBox="0 0 760 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A tornado chart from the example. For each assumption, a bar spans the share of futures where managed is cheaper, from the half of futures where the assumption was low to the half where it was high. Traffic growth: 96% when low, 62% when high, a swing of 34 points. Incidents: 68% to 90%, 22 points. Operating time: 69% to 90%, 21 points. Incident cost: 71% to 87%, 16 points. Overall, managed is cheaper in 79% of futures.">
          __SVG:fig07__
        </svg>
        <figcaption>A tornado chart: the widest bar is the assumption that moves the answer most. Here it's traffic growth, so that's the forecast to scrutinise before deciding.</figcaption>
      </figure>

      <h4>What the example shows</h4>
      <p><b>The answer is "managed, probably".</b> The managed service is cheaper in 79% of the simulated futures, with a median three-year cost of $488,000 against $638,000. That's a useful answer, and a more honest one than a single number, because it admits a one-in-five chance of being wrong.</p>
      <p><b>Growth decides it.</b> When traffic growth was in the low half of its range, managed won 96% of the time; in the high half, only 62%. No other input swung the answer by more than 22 points. The table then shows the boundary: running your own wins only if traffic grows two and a half times a year or more and operating it takes little time, or at three times a year. So the right conversation isn't "managed or our own?" in the abstract. It's "how confident are we that traffic will more than double every year for three years?" That's a question the product and finance teams can help answer, which turns an engineering argument into a shared one.</p>
      <p><b>The model is simple on purpose.</b> It leaves out lock-in, the cost of migrating away later, and the learning that running your own brings. Leaving things out is fine if you say so, and the omissions are a good place for the other side's case to start.</p>

      <h4>Arguing the other side</h4>
      <p>Two techniques make it practical. The first is to <b>steelman</b>: write the strongest case for the option you're against, as its best advocate would, before arguing against it. If you can't write a paragraph your opponent would sign, you don't yet understand the trade-off. The second is the <b>pre-mortem</b>, from the psychologist Gary Klein: imagine it's a year later and your chosen option has failed badly, then write down why. People who struggle to criticise a plan they've just agreed to find it easy to explain a failure that has "already happened", and the reasons they give are the risks to plan for.</p>

      <h4>One-way and two-way doors</h4>
      <p>In his 2015 letter to shareholders, Jeff Bezos distinguished two kinds of decision. Some are one-way doors: hard or impossible to reverse, such as choosing a database for a system that will hold years of data, or publishing an API others will build on. These deserve slow, careful analysis. Most decisions are two-way doors: if you're wrong, you walk back through. Treating every decision as a one-way door is how organisations become slow. Part of taste is knowing which kind you face. The managed-service choice is closer to a two-way door than it looks, if you keep your code behind an interface and your data exportable, and making a decision more reversible is often cheaper than analysing it more carefully.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Arguing conclusions</b> when the disagreement is really about an unstated number.</li>
          <li><b>Single-point estimates</b> that hide how uncertain each input is.</li>
          <li><b>Measuring what's easy</b> instead of the assumption that decides the answer.</li>
          <li><b>Straw-manning the other option,</b> so the comparison proves nothing.</li>
          <li><b>Treating every decision as irreversible,</b> and analysing two-way doors for weeks.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 7.1</span><span class="ex-title">If growth were known</span></div>
          <p>Product says traffic will grow between 1.0 and 1.5 times a year. Change the growth range in the example. What happens to the answer and to the swings, and what does that tell you about the decision?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">run our own  3-year cost: median $562k  (80% between $388k and $876k)
managed      3-year cost: median $317k  (80% between $269k and $389k)
managed is cheaper in 99% of 20,000 simulated futures
(every assumption now swings the answer by 1 point or less)</code></pre>
            <p>With growth pinned to the slow end, the managed service wins in 99% of futures, and no other assumption matters: operating time and incidents, which looked important before, now swing the answer by a point. Narrowing the one input that decided the question settled it. That's the value of information in practice: one conversation with product, about one number, was worth more than any further engineering analysis. If they'd said 2.5 to 3.5 times a year instead, managed would win in only a third of futures, and running your own would become the default. Either way, the forecast, not the technology, made the decision.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 7.2</span><span class="ex-title">Steelman the loser</span></div>
          <p>Write the strongest one-paragraph case for running your own cluster, as someone who believes in it would.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>"Event streaming is becoming the backbone of our platform, and we'll depend on it for a decade. The managed service's price scales with throughput, so our bill grows with our success, and our traffic doubled last year. Running it ourselves costs more now and less later, and the crossover comes sooner than the model's median suggests if growth continues. It also builds expertise we'll need anyway: when something goes wrong in the managed service at 3 a.m., we're waiting on someone else's support queue, unable to see inside it. And the model leaves out lock-in: the longer we use a provider's proprietary features, the more expensive leaving becomes. We should pay the learning cost while we're small." A good steelman uses the model's own blind spots, growth, lock-in and control, rather than ignoring the model. Writing it shows exactly which assumptions the managed option depends on, and those become the questions to check before committing.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 7.3</span><span class="ex-title">A pre-mortem</span></div>
          <p>It's two years later, and the move to the managed service is widely seen as a mistake. Write the three most likely reasons, and what you'd do now about each.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>First, the bill grew faster than the model said, because traffic tripled after a new product launch. Now: set a cost alert at twice the projected monthly bill, and agree in advance the traffic level at which we'd re-run the analysis. Second, we built on the provider's proprietary connectors, and leaving would take a quarter. Now: put a thin interface between our services and the stream, use only the open protocol, and test an export once a year. Third, a provider outage took us down for a day, and we couldn't do anything but wait. Now: decide which consumers must keep working during an outage, buffer their input locally, and read the provider's incident history before signing. Each reason became a cheap precaution taken today, which is what a pre-mortem is for. None of them argues for not choosing the managed service; they make the choice safer and more reversible.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Do you write uncertain inputs as ranges, and say how sure you are?</li>
            <li>Can you find which assumption swings a decision, and focus the argument there?</li>
            <li>Can you steelman the option you're against?</li>
            <li>Do you run pre-mortems on important decisions?</li>
            <li>Do you tell one-way doors from two-way doors, and make decisions more reversible when you can?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind paid">Book</span><div><a href="https://www.howtomeasureanything.com/">How to Measure Anything</a> <span class="by">Douglas Hubbard</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://hbr.org/2007/09/performing-a-project-premortem">Performing a Project Premortem</a> <span class="by">Gary Klein, Harvard Business Review</span></div></li>
            <li><span class="rkind free">Letter</span><div><a href="https://s2.q4cdn.com/299287126/files/doc_financials/annual/2015-Letter-to-Shareholders.PDF">2015 Letter to Shareholders</a> <span class="by">Jeff Bezos</span></div></li>
          </ul>
        </div>
      </div>
    </section>
