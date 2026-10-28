    <div class="part" id="part4">
      <span class="part-num">Part IV</span>
      <h2>The long game</h2>
      <p>Four chapters on what makes the rest last. The business: what your company sells, what it costs, and where engineering moves the numbers, so you can choose work by its value. Measurement: the four delivery metrics that research ties to better outcomes, computed from your own history. Finishing: why limiting work in progress makes everything faster, and the other boring virtues that make people trust you. And a career that compounds: the written record, the body of work and the sustainable pace that turn years into expertise.</p>
    </div>

    <section class="chapter prose" id="ch13" data-ch="13">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 13</span><label class="done-toggle"><input type="checkbox" data-id="ch13"><span class="box"></span>Read</label></div>
        <h3>Learning the business</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Every engineering choice is also a business choice, and the engineers who are trusted with the biggest ones can say what their work is worth in the business's own units. Learn a handful of numbers: revenue, margin, what a customer is worth, what drives churn, what infrastructure costs per unit of work. Then price projects in money, write the assumption beside each number, and rank them by value per week of effort. It won't be precise. It will be arguable, which is far better than unspoken.</p>
      </header>

      <h4>Why an engineer needs the numbers</h4>
      <p>The syllabus asks you to "learn the business: what your company sells, what it costs, where engineering moves the number". There's a practical reason. Senior engineers spend much of their time choosing what to work on, and arguing for it. "This would be cleaner" persuades other engineers. "This saves $110,000 a year and pays for itself in six weeks" persuades everyone, including the people who decide budgets. The second argument needs the numbers, and engineers who have them get a different kind of hearing.</p>
      <p>The numbers also change what you think good engineering is. Reliability matters because downtime makes customers leave, not because uptime is a virtue. Performance matters where it changes conversion or cost, and hardly at all elsewhere. Once you see which numbers your work moves, the trade-offs in chapter 7 get much easier to argue.</p>

      <h4>The handful of numbers</h4>
      <p>A product business, at its simplest, runs on a few quantities. <b>Revenue</b>, and how it's earned: subscriptions, usage, transactions, advertising. <b>Gross margin</b>: the share of revenue left after the costs of serving customers, which for a software product are mostly infrastructure and support. <b>Churn</b>: the share of customers who leave each month. <b>Lifetime value</b>: what a customer is worth over their whole time as a customer, roughly the margin they bring each month divided by the churn rate. <b>Conversion</b>: the share of trials or visitors who become paying customers. And for an engineer, <b>unit cost</b>: what one request, one invoice or one gigabyte costs to serve.</p>
      <p>You can learn your company's versions of these in a week if you ask. Finance teams are usually delighted that an engineer wants to understand the model. Public companies publish most of them in their annual reports. And the pricing page, the support queue and an hour with a salesperson teach the parts no spreadsheet shows: what customers actually buy, and what makes them angry.</p>

      <h4>Pricing engineering work</h4>
      <p>With those numbers, an engineering project can be priced in the same currency as every other business decision. The example does it for a small invoicing product, 4,000 paying teams at $49 a month, and three candidate projects: making checkout faster, caching invoice PDFs, and fixing the bulk-invoice failures that exit surveys blame for some churn. Each project's value comes from one assumption, written beside it in the code, where anyone can see it and argue with it.</p>
      __EXAMPLE:ch13_economics|economics.py &middot; the unit economics of a small invoicing product, an outage priced two ways, and three projects ranked by value per week of effort__
      <figure class="diagram">
        <svg viewBox="0 0 760 230" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Value per engineer-week of effort for the three projects, from the example. Cache invoice PDFs: $36,480 a week, paying back in 5.7 weeks. Faster checkout: $27,200 a week, payback 7.6 weeks. Fix bulk-invoice failures: $10,200 a week, payback 20.4 weeks.">
          __SVG:fig13__
        </svg>
        <figcaption>Ranked by value per week of effort, the smallest project comes first. Every week it waits costs the most, which is what the ranking measures.</figcaption>
      </figure>

      <h4>What the example shows</h4>
      <p><b>A customer is worth about $1,360.</b> With a 69% gross margin and 2.5% of customers leaving each month, the average customer stays 40 months and brings $1,360 of margin over that time. That single number makes the rest computable: anything that keeps a customer, or wins one, is worth about that much.</p>
      <p><b>An outage costs less in refunds than in leaving.</b> Customers pay $272 for each hour of service, so a four-hour outage refunded in full costs $1,089. If the same outage makes 1% of customers decide to leave, it costs $54,400 in lifetime margin, fifty times as much. That's why reliability work is worth far more than its "lost minutes" suggest, and why the right way to argue for it is through churn, not uptime percentages.</p>
      <p><b>The smallest project goes first.</b> Faster checkout is worth the most per year, $163,200, but takes six engineer-weeks. Caching invoice PDFs is worth less, $109,440, but takes three, so its value per week of effort, $36,480, is the highest, and it pays for itself in under six weeks. The bulk-invoice fix, at $10,200 a week of effort, comes last despite fixing a real customer pain. Ranking by value per week of effort is a simple form of what Don Reinertsen calls weighted shortest job first: since every week a valuable project waits is value lost, do first the work that delivers the most value per unit of time it occupies the team.</p>
      <p><b>Every figure is an assumption.</b> The conversion gain comes from one A/B test; the PDF share of the cloud bill from one month's invoice; the churn share from exit surveys. Writing each assumption beside its number, as the code does, is the point: it turns "I think checkout matters more" into "your A/B test may be optimistic, so let's check it", which is an argument that can be settled.</p>

      <h4>The cost of delay</h4>
      <p>Reinertsen's <i>The Principles of Product Development Flow</i> makes a claim worth remembering: if you quantify only one thing, quantify the cost of delay. It's the value lost for each week a piece of work isn't done, and it's what the ranking above really compares. Teams that don't quantify it make prioritisation decisions by volume and seniority, and routinely delay their most valuable work behind their loudest. Cost of delay also makes the case for small batches and finishing things, the subject of chapter 15: a project half done delivers nothing, so every week spent on two projects at once delays the value of both.</p>

      <h4>Speaking the business's language</h4>
      <p>Translate engineering work into the business's units: money, risk and time. Technical debt is interest: "our build takes twenty minutes, and with thirty engineers it costs about $660,000 a year in waiting", rather than "the build is slow". Reliability is churn and revenue at risk. Security is the expected cost of a breach, and the deals lost without a compliance certificate. Performance is conversion and infrastructure cost. None of these needs to be precise. A rough number with its assumption stated is enough to start a real conversation, and it's how engineering work competes fairly for time with everything else a business could do.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Arguing for work by elegance</b> to people who decide by value.</li>
          <li><b>Pricing outages in lost minutes</b> instead of customers who leave.</li>
          <li><b>Ranking by total value,</b> ignoring how long each project occupies the team.</li>
          <li><b>Precise-looking numbers with hidden assumptions,</b> which nobody can check.</li>
          <li><b>Never asking finance for the model,</b> and guessing at the numbers that matter.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 13.1</span><span class="ex-title">The A/B test was optimistic</span></div>
          <p>A re-run of the A/B test shows faster checkout raises conversion by half a point, not one. What happens to its value and to the ranking?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Its value halves, from $163,200 a year to $81,600, and its value per week of effort from $27,200 to $13,600. The ranking doesn't change: caching PDFs at $36,480 a week still goes first, checkout second, the bulk-invoice fix third at $10,200. But checkout's lead over the bulk fix has shrunk from nearly three times its value to a third more, so one more change in an assumption, say the exit surveys undercounting the bulk-invoice failures, could reorder them. That's the useful result. It shows which comparison is close, and therefore which assumption is worth checking before committing six weeks of work. It's chapter 7's method applied to prioritisation: find the assumption that decides it.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 13.2</span><span class="ex-title">The slow build, in money</span></div>
          <p>Thirty engineers each run the full build about six times a day, and it takes twenty minutes. Estimate what it costs a year, and what cutting it to eight minutes would be worth, stating your assumptions.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Thirty engineers, six runs a day and twenty minutes a run is 3,600 minutes, sixty hours of waiting a day. Assume half of it is genuinely lost, since people do other things during some builds but lose focus switching back: thirty hours a day. Over about 220 working days that's 6,600 hours a year, and at a loaded cost of $100 an hour, about $660,000 a year. Cutting the build to eight minutes removes 60% of the wait, worth about $400,000 a year. Even if the "half lost" assumption is generous and the true figure is a quarter, it's $200,000 a year, enough to justify several engineer-months of build work. State each assumption, the runs a day, the share lost and the hourly cost, so that someone can change the one they doubt and see whether the conclusion survives. It usually does, which is why build speed is one of the easiest engineering investments to justify.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 13.3</span><span class="ex-title">Questions for finance</span></div>
          <p>Write the five questions you'd ask your company's finance team to learn the numbers that matter for your area.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">1. How do we make money: what share is subscription, usage, transactions, services?
2. What's our gross margin, and how much of the cost of serving customers is
   infrastructure, and how much is support?
3. What's monthly churn, and what do we know about why customers leave?
4. What is a customer worth over their lifetime, and what does it cost to win one?
5. Which of these numbers is the company most worried about this year?</code></pre>
            <p>The first four give you the model; the fifth tells you where the attention and budget will go, which is where engineering work that moves that number will be valued most. Ask for the numbers as ranges if exact figures are confidential; for prioritisation, the order of magnitude is what matters. And offer something back: explain what drives the infrastructure bill, which finance teams often find opaque. A relationship with finance is one of the most useful a senior engineer can have.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Do you know how your company makes money, its margin, churn and what a customer is worth?</li>
            <li>Do you know the unit cost of what your systems do?</li>
            <li>Can you price a project in money, with its assumption written beside the number?</li>
            <li>Do you rank work by value per week of effort, the cost of delay?</li>
            <li>Do you argue for reliability through churn, and for technical debt as interest?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind paid">Book</span><div><a href="https://www.goodreads.com/book/show/6278270-the-principles-of-product-development-flow">The Principles of Product Development Flow</a> <span class="by">Donald Reinertsen</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://blackswanfarming.com/cost-of-delay/">Cost of Delay</a> <span class="by">Black Swan Farming</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://lethain.com/work-on-what-matters/">Work on what matters</a> <span class="by">Will Larson</span></div></li>
          </ul>
        </div>
      </div>
    </section>
