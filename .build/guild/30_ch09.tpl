    <div class="part" id="part3">
      <span class="part-num">Part III</span>
      <h2>Leading</h2>
      <p>Four chapters on leading work you can't do alone. Estimating honestly, with ranges and probabilities instead of a single hopeful date. Sequencing a project so its unknowns surface early, while they're cheap. Communicating its state to the people who depend on it, each in the form they need. And mentoring, the deliberate work of making other engineers better, which is the fastest way to find the holes in your own understanding. The syllabus asks you to "lead a project end to end: scoping, sequencing, risk, stakeholders, landing it". This part covers each of those words.</p>
    </div>

    <section class="chapter prose" id="ch09" data-ch="09">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 09</span><label class="done-toggle"><input type="checkbox" data-id="ch09"><span class="box"></span>Read</label></div>
        <h3>Estimating honestly</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">A plan built by adding up each task's most likely duration is very unlikely to be met, because it ignores how much worse things can go than they can go well, and because waiting for parallel work makes every join later. Estimate each task as a range, combine the ranges along the real dependencies, and talk about dates as probabilities. Commit to a date you're 85% likely to meet, find the tasks that decide it, and update the forecast as you learn.</p>
      </header>

      <h4>Why estimates fail</h4>
      <p>Engineers are often told they're bad at estimating, and the evidence agrees: projects routinely take far longer than planned. In 1979, Daniel Kahneman and Amos Tversky named the <b>planning fallacy</b>: people estimate their own tasks by imagining how they'll go, a best-case story, and ignore how similar tasks actually went. But optimism is only part of it. Even an honest estimator, who gives the true most likely duration for every task, produces a plan that's usually late, for two mechanical reasons.</p>
      <p>The first is <b>skew</b>. A task estimated at five days might finish in four if everything goes well, but in ten if the third-party sandbox is broken or the requirements turn out to be ambiguous. Durations can't go much below their most likely value, and can go far above it, so the average is later than the most likely. Add up the most likely values and you've added up numbers that are each below their task's average. The second is <b>merge bias</b>. When a task waits for two others, it waits for the later of the two, and the later of two uncertain things is later than either is likely to be on its own. Every join in a plan pushes the end date out.</p>

      <h4>Ranges, and the graph</h4>
      <p>The cure is to estimate each task as three numbers, best case, most likely and worst case, and to combine them along the dependencies rather than adding them up. That combination is hard by hand and easy by simulation: draw a duration for every task from its range, compute when the project finishes given what waits for what, and repeat thousands of times. The result is a distribution of end dates, from which you read percentiles: <b>P50</b>, the date you're as likely to beat as to miss, and <b>P85</b>, the date you'll meet five times in six.</p>
      <p>The simulation also says which tasks matter. In each run, the <b>critical path</b> is the chain of dependent tasks that determined the end date. A task that's on the critical path in most runs decides the schedule, and it's where to spend attention; a task that's rarely on it can slip without consequence. The example builds a seven-task project, the launch of a checkout feature, and does all of this.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The example's task graph. Design comes first. After design, three paths: migration; API then UI; and API then payments. Load test waits for UI, payments and migration, then launch. The planned critical path, design, API, UI, load test, launch, is highlighted. Payments, with a worst case of 15 days, is marked as on the critical path in 43% of simulated runs.">
          __SVG:fig09__
        </svg>
        <figcaption>The plan's critical path runs through the UI. But the payments integration, with its long worst case, decides the end date in 43% of simulated runs, and the plan never mentions it.</figcaption>
      </figure>
      __EXAMPLE:ch09_schedule|schedule.py &middot; a seven-task launch simulated twenty thousand times: what the plan's date means, which tasks decide the end, and merge bias__

      <h4>What the example shows</h4>
      <p><b>The plan's date is a 2% chance.</b> Adding the most likely durations along the longest chain gives seventeen days, the kind of number that goes in a slide. In the simulation, the project finished by day 17 in only 2% of runs. The median was 22 days and P85 was 25.2. Nobody was pessimistic or careless: every task's most likely value was honest. The plan was wrong because of skew and joins, and it would have been wrong for anyone who made it this way.</p>
      <p><b>The task that decides the date isn't on the plan's critical path.</b> Design, the API, the load test and the launch are on the critical path in every run, as they must be. But the UI was on it in only 57% of runs, and the payments integration, absent from the planned path, decided the end date in 43%. Its most likely four days hide a worst case of fifteen, a third-party sandbox that's usually fine and sometimes not. That's where a lead should look first: start it earlier, prototype against the sandbox in week one, or find a fallback.</p>
      <p><b>Waiting for two things takes longer.</b> One task estimated at six days, best four and worst twelve, had a median of 7.1 days. Waiting for the later of two such tasks had a median of 8.2. Every join in a plan quietly adds time like this, and a plan with many parallel streams merging into one launch adds a lot.</p>

      <h4>Talking about dates</h4>
      <p>Steve McConnell's <i>Software Estimation</i> separates three things that conversations about dates mix up. An <b>estimate</b> is a prediction: what you think will happen, with its uncertainty. A <b>target</b> is a wish: when the business would like it. A <b>commitment</b> is a promise: the date you agree to be held to. Most estimation arguments are a target being presented as an estimate, or an estimate being heard as a commitment. Name which one you're discussing.</p>
      <p>Give estimates as ranges with confidence: "most likely around day 22; 85% confident of day 25". Commit at your P85, not your P50, because a P50 commitment is missed half the time, and repeated misses destroy trust faster than conservative dates. Update the forecast every week as tasks finish and their ranges collapse to actual values. Early in a project the range is wide; it should narrow as you go, and if it doesn't, the project has a problem worth raising now. And when the date you can honestly commit to isn't the target, say so early and offer choices: a later date, less scope, or a different approach. Leaders are trusted for bad news delivered early.</p>

      <h4>Brooks's law</h4>
      <p>Fred Brooks's <i>The Mythical Man-Month</i>, from 1975, states the most famous law of software management: adding people to a late project makes it later. New people need weeks to become productive, and someone who knows the project has to teach them, so the team slows down before it speeds up. And communication grows faster than headcount: with <i>n</i> people there are <i>n</i>(<i>n</i>&minus;1)/2 pairs who may need to stay in sync, three channels for three people, sixty-six for twelve. Brooks called his book's subject "the bearing of a child takes nine months, no matter how many women are assigned". Some work divides well; much doesn't. When a project is late, cutting scope or removing a blocker usually helps more than adding people.</p>

      <h4>Learning from your own record</h4>
      <p>The best correction for the planning fallacy is your own history. Bent Flyvbjerg's <b>reference class forecasting</b>, used for large infrastructure projects, starts from how long similar past projects actually took, not from the details of this one. You can do the same at a small scale: keep a record of each task's estimate and its actual duration. After a few months, the ratio of actual to estimated, perhaps 1.4 on average, with a long tail, tells you how to adjust, and its spread tells you how wide your ranges should be. Teams that keep this record estimate better within a year, not because they become less optimistic but because they calibrate.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Adding up most-likely durations</b> and calling the sum a date.</li>
          <li><b>Committing at P50,</b> and missing half of your commitments.</li>
          <li><b>Ignoring the task with the long worst case,</b> because its most likely value is small.</li>
          <li><b>Treating a target as an estimate,</b> or an estimate as a commitment.</li>
          <li><b>Adding people to a late project,</b> instead of cutting scope or removing a blocker.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 9.1</span><span class="ex-title">The date to commit to</span></div>
          <p>Product asks for the launch "in three weeks", fifteen working days. Using the example's results, write the reply.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>"We can't commit to fifteen days. Even our plan's most optimistic chain is seventeen, and we'd meet that only about one time in fifty. Our honest forecast is a median of 22 working days, and we're 85% confident of 25, so 25 is the date I'd commit to. If three weeks matters, here are the options: we could ship without the load test and launch prep, which saves about three days and adds risk we'd need to agree on; or we could cut the new UI and launch the API for internal use first. The biggest single uncertainty is the payments sandbox; if we prototype against it this week, I expect the range to narrow, and I'll send an updated forecast on Friday." The reply separates the target from the estimate, gives the estimate with its confidence, offers real choices for meeting the target, and promises an update when uncertainty shrinks.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 9.2</span><span class="ex-title">De-risk the decider</span></div>
          <p>A two-day spike against the payments sandbox finds no surprises, cutting the task's worst case from 15 days to 8. Change the example and describe what happens.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">chance of finishing by day 17: 4%
P50 20.9 days   P85 23.7 days   P95 25.3 days
on the critical path: ui 90%, payments 10%</code></pre>
            <p>P85 improves by a day and a half, from 25.2 to 23.7, from narrowing one task's range, without making anything faster. And the critical path changes character: payments now decides the date in only 10% of runs, and the UI in 90%, so attention should move to the UI. That's the pattern of a well-led project: find the task whose uncertainty decides the date, spend a little to shrink it, and re-run the forecast to see where the risk went. Notice also what didn't change much: the chance of the plan's seventeen days is still only 4%. Reducing uncertainty makes dates more predictable; it doesn't make optimistic plans come true.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 9.3</span><span class="ex-title">Your own multiplier</span></div>
          <p>Design a lightweight record for your team's estimates and actuals, and say what you'd compute from it after three months.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Add three fields to each task in your tracker: the best, likely and worst estimate in days, recorded when the task is started, and the actual duration, recorded when it's done. Nothing else; the habit has to survive busy weeks. After three months, compute for each task where its actual fell relative to its range: below best, between best and likely, between likely and worst, or beyond worst. If estimates are calibrated, about half the actuals land above the likely value and only a few beyond the worst. If a third land beyond the worst, your ranges are too narrow; widen the worst cases. Also compute the median ratio of actual to likely: a value of 1.3 says your "likely" is consistently optimistic by about 30%, which you can now correct for, honestly and with evidence. Share the results with the team without blame; the goal is calibration, not accountability.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Do you estimate tasks as ranges, and combine them along the real dependencies?</li>
            <li>Can you explain why a sum of most-likely durations is usually late?</li>
            <li>Do you commit at P85, and update the forecast as tasks finish?</li>
            <li>Do you find the tasks that decide the end date, and de-risk them first?</li>
            <li>Do you keep a record of estimates against actuals, and use it?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind paid">Book</span><div><a href="https://www.informit.com/store/mythical-man-month-essays-on-software-engineering-anniversary-9780201835953">The Mythical Man-Month</a> <span class="by">Fred Brooks</span></div></li>
            <li><span class="rkind paid">Book</span><div><a href="https://www.microsoftpressstore.com/store/software-estimation-demystifying-the-black-art-9780735605350">Software Estimation: Demystifying the Black Art</a> <span class="by">Steve McConnell</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://jacobian.org/series/estimation/">Estimating software projects</a> <span class="by">Jacob Kaplan-Moss</span></div></li>
          </ul>
        </div>
      </div>
    </section>
