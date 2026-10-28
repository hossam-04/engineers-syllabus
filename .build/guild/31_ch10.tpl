    <section class="chapter prose" id="ch10" data-ch="10">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 10</span><label class="done-toggle"><input type="checkbox" data-id="ch10"><span class="box"></span>Read</label></div>
        <h3>Leading a project</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">Leading a project end to end means owning its outcome, not its code: what's in scope, in what order the work happens, what could kill it, and whether it really lands. Most of the skill is in the order. Do the work that could change the plan first, while little has been built on top of it, and do the comfortable work later. The same project, sequenced risk first, discovers its bad news weeks earlier and throws away far less.</p>
      </header>

      <h4>What leading means</h4>
      <p>A technical lead on a project is rarely the person who writes the most code. They're the person who makes sure the project succeeds: that it's solving the right problem, that the plan is realistic, that the risks are known and handled, that the people who depend on it know what's happening, and that it actually finishes. Tanya Reilly's <i>The Staff Engineer's Path</i> describes this as holding the whole project in your head, so that nothing important is nobody's job. The syllabus lists the parts: scoping, sequencing, risk, stakeholders and landing it. This chapter covers all but stakeholders, which have chapter 11.</p>

      <h4>Scoping</h4>
      <p>Start by writing down what "done" means, in a sentence a stakeholder would agree with: "customers can refund an order from the admin screen, and the money reaches their card within a week". Then find the smallest version of the project that achieves it, and list everything else as explicitly out of scope, in the design document's non-goals. Every project grows during its life, and most of the growth is reasonable on its own; the scope list is what lets you say "that's a good idea for phase two" without an argument.</p>
      <p>Keep a <b>cut list</b> from the start: the parts you'd drop first if the project ran late, agreed with the stakeholders in advance. Agreeing to cuts when nobody is under pressure is easy. Agreeing to them in the last week, with the date slipping, is a negotiation nobody wins.</p>

      <h4>Sequencing</h4>
      <p>Most project plans order work by what's comfortable or what's logically first: build the data model, then the screens, then the reports, and leave the integrations and the hard questions until the pieces they connect exist. That ordering has a hidden cost. The hard questions, will the bank's API support refunds, will the risk team accept rules instead of a model, are the ones whose answers can change the plan, and every week they wait, more work is built on assumptions that might be wrong.</p>
      <p>The alternative is to <b>sequence by risk</b>: of the tasks you can start, do first the one with the most uncertainty per day of work, so bad news arrives while it's still cheap. Two techniques sharpen it. A <b>spike</b> is a short, throwaway experiment that answers one question, two days of prototype calls against the bank's sandbox, before committing to the work that depends on the answer. A <b>walking skeleton</b>, Alistair Cockburn's term, is the thinnest end-to-end version of the system, every component present but barely functional, built first so that integration problems appear in week one instead of the last week. The example measures what sequencing is worth.</p>
      __EXAMPLE:ch10_sequence|sequence.py &middot; one project of eight tasks, three of them hiding serious unknowns, run in three orders twenty thousand times__
      <figure class="diagram">
        <svg viewBox="0 0 760 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Two timelines of the same eight tasks. Comfortable first: data model, email templates, admin screens, reporting, migration of old data, then the risky fraud rules and bank API integration near the end, then the load test; the first surprise surfaces around day 33. Riskiest first: the bank API integration and fraud rules come first, then the data model, migration, reporting, email templates, admin screens and the load test; the first surprise surfaces around day 7. A two-day spike before everything moves it to day 2.">
          __SVG:fig10__
        </svg>
        <figcaption>Same work, different order. Put the tasks that could change the plan first, and bad news arrives in week one or two instead of week seven, before most of the work that it would invalidate exists.</figcaption>
      </figure>

      <h4>What the example shows</h4>
      <p><b>Something will probably go wrong.</b> The eight tasks each have a chance of revealing a problem that changes the plan, mostly small, but the bank integration has a 35% chance and the fraud rules 20%. Together, at least one goes badly 66% of the time. That's realistic for a project with external dependencies, and it means the plan should assume a surprise, not hope to avoid one.</p>
      <p><b>The order decides what the surprise costs.</b> Comfortable first, the median first surprise came on day 33 of 44, after most of the work was done, and on average 12.5 days of work were thrown away. Riskiest first, respecting the real dependencies, it came on day 7, and the average waste fell to 5.5 days. That's a week of work saved per project, from nothing but the order of the same tasks, plus five extra weeks to react to bad news while there's still room to.</p>
      <p><b>A spike buys time, more than it saves work.</b> Two days of prototypes against the two riskiest unknowns moved the first surprise from day 7 to day 2 while saving little more work. What it bought was knowing early. On a real project, knowing in week one that the bank doesn't support partial refunds means the product decision, cut the feature or change the design, happens while the team is still flexible, which is usually worth more than the days.</p>

      <h4>Managing risk, on purpose</h4>
      <p>Keep a <b>risk register</b>: a short list, reviewed weekly, of what could go wrong. Each entry has a description, a rough likelihood and impact, an owner, the mitigation, and a <b>trigger</b>, the observable sign that the risk is happening. "Bank sandbox doesn't support refunds; likely; high impact; owner Ana; mitigation: spike in week 1, fallback of manual refunds; trigger: the refund endpoint returns an error after a day of trying." Ten lines like that, kept current, are worth more than a hundred-row spreadsheet nobody reads.</p>
      <p>For a risky project, decide <b>kill criteria</b> before starting: the results that would mean stopping or changing course. "If the spike shows the bank can't support refunds through its API, we stop and propose manual refunds instead." Decided in advance, a kill criterion is a plan. Decided afterwards, under the weight of the work already done, it's a fight against the sunk-cost fallacy, which usually wins.</p>

      <h4>Landing it</h4>
      <p>Projects die in their last ten percent. The feature works, the team's attention moves on, and what's left, migrating the last customers, deleting the old code path and its feature flag, writing the runbook, handing over to the team that will own it, never quite happens. The old and new systems then run side by side for years, and the project's real benefit, simplicity, never arrives. A project is done when the old path is gone, the documentation is written, the on-call team knows how to run it, and the success measure from the scope has been checked. Plan that work explicitly, with dates, from the start.</p>
      <p>Then close it properly. Tell everyone who depended on it that it's finished and what changed. Hold a short retrospective, what to repeat and what to change, while memories are fresh. And thank the people who did the work, by name, where their managers can see it. Landing a project well is what makes people want to work on your next one.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Ordering work by comfort,</b> so the questions that could change the plan are answered last.</li>
          <li><b>No agreed cut list,</b> so scope negotiations happen in the final week.</li>
          <li><b>A risk register that's written once and never read again.</b></li>
          <li><b>No kill criteria,</b> so a failing project continues on sunk cost.</li>
          <li><b>Declaring victory at launch,</b> with the old path, the flag and the handover still undone.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 10.1</span><span class="ex-title">When rework is cheap</span></div>
          <p>Predict what happens to the three orders' waste if a change of plan throws away only 10% of the work done, rather than 50%. Then check it by changing <code>REWORK</code>. What does this tell you about when sequencing matters?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Every order's waste shrinks to a fifth, since waste is proportional to <code>REWORK</code>: about 2.5 days comfortable first and 1.1 days riskiest first. The first-surprise days don't change at all, because the order of the tasks hasn't changed. So the work saved by sequencing scales with how much a surprise invalidates. When the components are independent and a change of plan touches little else, order hardly matters for waste. When everything is built on an early assumption, a data model, an integration, an API contract, it matters a lot. But the time to react to bad news still favours risky-first, whatever the rework rate: learning on day 7 rather than day 33 leaves time to change course, which is often the bigger benefit and the one the waste figure doesn't measure.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 10.2</span><span class="ex-title">Kill criteria</span></div>
          <p>Write kill criteria for the refunds project, to be agreed with stakeholders before work starts.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">We stop, or return to stakeholders with a new proposal, if:
1. The week-1 spike shows the bank's API can't issue refunds to cards.
   -> Propose manual refunds through the bank's portal, with an admin-screen record.
2. The risk team won't accept rule-based fraud checks by the end of week 2.
   -> Pause until a model-based approach is scoped; don't build rules they'll reject.
3. The P85 forecast passes the end of the quarter at any weekly review.
   -> Cut to the agreed minimum: full refunds only, no partial refunds, no reporting.</code></pre>
            <p>Each criterion is observable, has a date or a trigger, and says what happens next, so it's a decision made in advance rather than a vague warning. The third is the most important and the least common: a schedule kill criterion connects the forecast from chapter 9 to an action, so a slipping date triggers the cut list automatically instead of a debate. Agree these with the stakeholders in the kickoff, and write them in the design document.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 10.3</span><span class="ex-title">A walking skeleton</span></div>
          <p>Describe the walking skeleton for the refunds project: what does it contain, and what would you learn from building it in the first week?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>One button on the admin screen that refunds a hard-coded test order in full, through every real component: the admin screen calls the refund API, which writes a refund record, calls the bank's sandbox, waits for its webhook, updates the record and sends the customer an email from the real template. No validation, no partial refunds, no fraud rules, no reporting. Building it in week one tests every integration point at once: authentication to the bank, the webhook arriving through your network, the email sender, the deployment pipeline for the new service. Problems found there would otherwise have surfaced only when the polished components were connected near the end. After that, each week fleshes out one part of the skeleton, and the system works end to end the whole time, which also makes the status report in chapter 11 much easier to write honestly.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Is "done" written down in a sentence stakeholders agree with, with a cut list?</li>
            <li>Is the work sequenced so the questions that could change the plan are answered first?</li>
            <li>Do you use spikes and a walking skeleton to surface problems early?</li>
            <li>Do you keep a short risk register with triggers, and agreed kill criteria?</li>
            <li>Does your plan include landing: the old path removed, documentation, handover?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind paid">Book</span><div><a href="https://www.oreilly.com/library/view/the-staff-engineers/9781098118723/">The Staff Engineer's Path</a> <span class="by">Tanya Reilly</span></div></li>
            <li><span class="rkind free">Guide</span><div><a href="https://staffeng.com/guides/">Staff Engineer: guides</a> <span class="by">Will Larson</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://hbr.org/2007/09/performing-a-project-premortem">Performing a Project Premortem</a> <span class="by">Gary Klein</span></div></li>
          </ul>
        </div>
      </div>
    </section>
