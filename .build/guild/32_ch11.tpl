    <section class="chapter prose" id="ch11" data-ch="11">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 11</span><label class="done-toggle"><input type="checkbox" data-id="ch11"><span class="box"></span>Read</label></div>
        <h3>Status, stakeholders and influence</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">A project that's going well but communicated badly looks like a project in trouble, and one in trouble but communicated well can still be saved. Know who depends on the project and what each of them needs. Write status updates that put the bottom line first, take their colour from the forecast rather than from mood, and ask for decisions by a date. And since a lead rarely has authority over the people a project needs, learn to move them by persuasion, relationships and clear writing.</p>
      </header>

      <h4>Who needs to know</h4>
      <p>A project's stakeholders are everyone who's affected by it, decides something about it, or must do something for it: the sponsor who funds it, the product lead who decides its scope, the partner teams whose systems it touches, the support team who'll answer questions about it, the engineers who build it. They don't all need the same thing. A useful exercise at the start is to list them and sort them by two questions, the grid that management texts attribute to Aubrey Mendelow: how much influence do they have over the project, and how much does it affect them? The sponsor, high on both, needs regular, short updates and early warning. A partner team that must change an API needs to know exactly what you need and by when. Someone affected but with little say needs to be told before the change reaches them, not after.</p>

      <h4>Status updates that get read</h4>
      <p>Most status updates are activity logs: "this week we continued working on the integration and had several meetings". They tell the reader that people were busy, which they assumed, and nothing they need: is it on track, what's the risk, what do you need from me? A useful update answers those in its first two lines, in the order a busy reader needs them. Military writing calls this <b>BLUF</b>, bottom line up front.</p>
      <p>The status colour deserves particular care, because it's the one thing everyone reads. Green, amber and red should come from the forecast, not from the lead's mood or fear of looking bad. One workable rule: <b>green</b> if the P85 forecast meets the committed date, <b>amber</b> if only the median does, and <b>red</b> if the median misses it. A rule makes the colour honest and removes the temptation to report "green" until the week the date is missed, the pattern known as the watermelon project: green outside, red inside. The example writes a week's update from the project's own data, for three audiences.</p>
      __EXAMPLE:ch11_status|status.py &middot; one week's status written from the project's data: the colour from the forecast, and the bottom line first for each audience__
      <figure class="diagram">
        <svg viewBox="0 0 760 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Project data, the open tasks with their ranges, the blockers and the decisions needed, feeds a forecast. The forecast and the data feed three versions of the update. Leadership gets two lines: the colour, the confidence of the date, and the decision needed by a date. Partner teams get what is needed from them and what a delay costs. The team gets the detail: what is done, what is open, and the forecast.">
          __SVG:fig11__
        </svg>
        <figcaption>One set of facts, three readers. The colour and the dates come from the forecast, so the update is honest by construction; each audience gets its own bottom line first.</figcaption>
      </figure>

      <h4>What the example shows</h4>
      <p><b>The colour is red, and that's useful.</b> The project is only 43% likely to ship by its committed day 30, and its median forecast, day 30.5, is just past it. Under the rule, that's red, even though the project is close. A red that early, with three weeks of work left and a clear cause, isn't a failure; it's the update doing its job, a warning while there's still time to act. The same project reported as green "because we're nearly there" would become a surprise in three weeks, which is the thing stakeholders never forgive.</p>
      <p><b>Every audience gets its bottom line, and an ask.</b> Leadership gets two lines: the colour with its probability, and a decision needed from the product lead by day 18, whether to ship without partial refunds if the bank can't support them by day 20. Asking for a decision by a date, before the date at which it matters, is what turns a status report from information into action. Partner teams get the blocker and its cost: if the bank's refunds endpoint holds the work up another week, the median moves from day 30.5 to day 35.5. That's five days for five days, because the blocked task is on the critical path. Saying it in days makes the cost concrete to a team that has other priorities. The team gets the detail, and the reason to finish the bank integration first: it has the widest range.</p>

      <h4>Influence without authority</h4>
      <p>A technical lead usually can't tell anyone outside their own team what to do, and often not inside it either. Projects need other teams to change their systems, review designs, and give up some of their own priorities. The way this happens is persuasion, and persuasion is a skill with a few reliable parts.</p>
      <p><b>Build the relationship before you need it.</b> The partner team you've helped, reviewed for, or simply talked to, will find time for your request; the one that first hears from you when you need something will put it in a queue. <b>Understand what they want.</b> Every team has goals and pressures; a request framed in terms of their goals, "this also removes the manual reconciliation your on-call does every week", moves faster than one framed in yours. <b>Write it down.</b> A short, clear proposal, the problem, the request, the cost and the deadline, can be forwarded to the person who actually decides, and survives being forwarded. And <b>agree before the meeting</b>. Toyota's practice of <i>nemawashi</i>, talking a proposal through with each person affected before the formal decision, means the meeting confirms an agreement instead of starting an argument.</p>
      <p>When persuasion fails and the project is genuinely blocked, <b>escalate well</b>: as a request for a decision, not a complaint. Say what's blocked, what it costs, the options and what you recommend, and copy the other party, so nothing is said behind their back. A good escalation is one the other team would describe as fair. It's how a lead uses the management chain without spending trust.</p>

      <h4>Meetings, briefly</h4>
      <p>A meeting is an expensive way to share information and a good way to make a decision. Hold decision meetings with a written pre-read, so the time goes on the disagreement rather than on explaining the background. Finish by reading back the decisions, the owners and the dates, and send them in writing within the hour. Most "we agreed on this" disputes come from meetings whose decisions weren't written down.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Status updates that are activity logs,</b> with no bottom line and no ask.</li>
          <li><b>Colour from mood,</b> green until the week the date is missed.</li>
          <li><b>Asking for a decision without a deadline,</b> or after the date it matters.</li>
          <li><b>Meeting partner teams for the first time when you need something.</b></li>
          <li><b>Escalating as a complaint,</b> behind the other team's back, instead of as a request for a decision.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 11.1</span><span class="ex-title">Rewrite the update</span></div>
          <p>Rewrite this update for leadership, in two lines: "Good progress this week. The team has been heads-down on the migration and we're working through some issues with the vendor. Should be fine, will keep you posted."</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>You can't, yet, and noticing that is the point: the original contains no facts. To write two honest lines you need the forecast and the vendor issue's cost, so first find them out. Then, for example: "AMBER: 70% likely to finish the migration by 14 November as committed; median forecast 12 November. Need: the vendor to restore API access to our staging account by Wednesday, or the median moves to 19 November; I've asked their account manager and will escalate on Wednesday if it isn't fixed." Each sentence is checkable: a colour from a rule, a probability, a date, a specific blocker with its cost, and what you're doing about it. "Should be fine" became a number, and "keep you posted" became a date for the next action.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 11.2</span><span class="ex-title">An escalation</span></div>
          <p>The bank's integration team still hasn't fixed the refunds endpoint after two weeks. Write the escalation to your director, copying the bank's contact.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">Subject: Decision needed by Friday: refunds launch blocked on the bank's sandbox

The refunds endpoint in the bank's sandbox has returned 501 since 3 October
(their ticket 4471). Our launch is committed for 14 November; every week this
stays open moves our forecast by a week, and we're now amber.

Options:
1. Ask the bank's account team to prioritise the ticket. (Recommended; I've
   attached the reproduction their engineers asked for.)
2. Launch full refunds through the bank's portal, recorded in our admin screen,
   and add API refunds when the endpoint works. Two days of work, no date risk.
3. Move the launch date.

I recommend 1 and 2 together: ask for the fix, and build the fallback now so the
date doesn't depend on it. Copying Priya at the bank, who has been helpful and
is waiting on her own platform team.</code></pre>
            <p>The subject says what's needed and by when. The body states the facts and their cost in dates, gives real options with a recommendation, and is fair to the other party, who is copied and credited. The director can decide in two minutes, and nobody at the bank has reason to feel ambushed. Notice that the recommended plan removes the dependency rather than only pushing on it: good escalations usually include a way to stop needing the escalation.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 11.3</span><span class="ex-title">A stakeholder map</span></div>
          <p>List the stakeholders of the refunds project, sort them by influence and by how much the project affects them, and say what each needs from you and how often.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">High influence, much affected:
  product lead      the forecast and decisions with deadlines; weekly, two lines
  finance director  how refunds are reconciled and reported; at the design review,
                    and before launch
High influence, little affected:
  engineering director  colour and risks; weekly summary, early warning of red
  security team     the fraud rules' design; review in week 2, sign-off before launch
Little influence, much affected:
  support team      what customers will see and how to answer; training before launch
  the bank's team   exactly what we need and by when; whenever blocked, with a
                    reproduction
  on-call engineers runbook and alerts; handover in the last week</code></pre>
            <p>The map shows who'd be surprised if you forgot them, which is its real purpose. The support team and on-call engineers have little say in the project but will live with its results, so they need early, practical information; the security and finance teams can stop the launch, so their reviews belong in the plan with dates, not as a last-week surprise. Revisit the map at each phase, because stakeholders change as a project moves from design to launch.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Do you know your project's stakeholders, and what each needs from you?</li>
            <li>Does your status update put the bottom line first, with an ask and a date?</li>
            <li>Does the colour come from the forecast, by a stated rule?</li>
            <li>Do you build relationships with partner teams before you need them?</li>
            <li>Do you escalate as a request for a decision, with options and the other party copied?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind paid">Book</span><div><a href="https://www.oreilly.com/library/view/the-staff-engineers/9781098118723/">The Staff Engineer's Path</a> <span class="by">Tanya Reilly</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://lethain.com/work-on-what-matters/">Work on what matters</a> <span class="by">Will Larson</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://hbr.org/2016/11/how-to-write-email-with-military-precision">How to Write Email with Military Precision</a> <span class="by">Kabir Sehgal, Harvard Business Review</span></div></li>
          </ul>
        </div>
      </div>
    </section>
