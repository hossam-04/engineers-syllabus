    <section class="chapter prose" id="ch16" data-ch="16">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 16</span><label class="done-toggle"><input type="checkbox" data-id="ch16"><span class="box"></span>Read</label></div>
        <h3>How to learn</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">How you study matters as much as how long. Rereading and highlighting feel productive and produce little. Decades of experiments point to three things that work far better. Testing yourself beats reviewing. Spreading reviews out over days and weeks beats massing them. And practising a skill at the edge of your ability, with feedback, beats repeating what you can already do. This chapter explains why, uses a small model of forgetting to show what spacing buys, and builds the scheduler flashcard programs use.</p>
      </header>

      <h4>Why rereading fails</h4>
      <p>Reading a chapter a second time feels like learning, because everything is familiar: you recognise each idea as it comes. But recognising is not recalling. The test that matters is whether you can produce the idea when you need it, with the book closed, and familiarity says little about that. Psychologists call the mistake an illusion of fluency, and it's why students who reread and highlight are often confident and wrong about what they know. The remedy is to make study feel more like the test. That's harder, and the difficulty is the point: the effort of retrieving something is what strengthens it.</p>

      <h4>Retrieval practice</h4>
      <p>In a well-known experiment by Henry Roediger and Jeffrey Karpicke, published in 2006, students studied short prose passages. Some reread a passage several times; others read it once and then tried to write down what they remembered. Five minutes later, the rereaders remembered slightly more. Two days and a week later, the students who had tested themselves remembered much more. Later experiments found retrieval practice beating rereading, note-taking and concept mapping across subjects and ages. The practical forms are simple. Close the book and write what you remember, then check. Use flashcards that ask a question. Explain an idea aloud as if teaching it. And, throughout this volume, predict what a command will print before you run it, which is retrieval with immediate feedback.</p>

      <h4>Spacing</h4>
      <p>In the 1880s, Hermann Ebbinghaus learned lists of nonsense syllables and measured how much he'd forgotten after various delays. The result was the first <b>forgetting curve</b>: steep at first, then flattening. He also found that reviewing a list again, after a delay, made the next curve shallower. A century of later work confirmed it as the <b>spacing effect</b>. A 2006 review by Nicholas Cepeda and colleagues, pooling hundreds of experiments, found that the same total study time, spread over separate sessions, is remembered far better than when it's massed into one. The best gap grows with how long you want to remember. To keep something for a year, review it at intervals of weeks, not minutes. Cramming works, after a fashion, for tomorrow's test, and leaves almost nothing a month later.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Chance of recall from day 0 to day 90 in the chapter's model. Without review, the curve falls fast: below half within ten days, and to about 10 percent by day 90. With reviews on days 1, 3, 7, 14 and 28, each review lifts recall back to 100 percent, and each following curve falls more slowly than the one before; after the last review on day 28, recall is still about 74 percent at day 90.">
          __SVG:fig16__
        </svg>
        <figcaption>Each review resets the curve and flattens it. Five reviews in the first month leave most of what was learned still recallable two months later; none leaves almost nothing.</figcaption>
      </figure>
      <p>The example turns those findings into a small model. Its forgetting curve has the shape modern schedulers use, and a review strengthens a memory more the closer it was to being forgotten. It compares five plans for 200 facts learned on the same day, each reviewed only during the first month, and then follows one fact under the scheduling rule that flashcard programs use. Its numbers come from invented constants, so read them for their shape, not as measurements.</p>
      __EXAMPLE:ch16_learning|learning.py &middot; a small model of forgetting, used to compare no review, cramming, fixed spacing, Leitner boxes and a 90 percent rule, then one fact's growing gaps between reviews__

      <h4>What the example shows</h4>
      <p><b>Cramming adds almost nothing.</b> Four more passes on the evening of learning raised recall two months later from 13% to 15%. In the model, as in life, reviewing what you can recall easily barely strengthens it, because there's no effort of retrieval. The same number of reviews spread across the month, on days 1, 3, 7, 14 and 28, raised it to 81%.</p>
      <p><b>Scheduling by need does slightly better, with less work.</b> Leitner boxes, Sebastian Leitner's 1970s system of moving cards between boxes reviewed at doubling intervals, gave 83% from 4.9 reviews per fact. Reviewing each fact just as its predicted recall falls to 90%, which is what modern schedulers do, gave 86% from 4.8. They spend reviews where they're needed, often on facts about to be forgotten and rarely on secure ones. Under that rule, one fact's gaps between reviews grew from one day to three, six, fifteen, thirty-nine and ninety-eight: six reviews in half a year left it stable for the best part of a year. This is the real promise of spaced repetition: remembering something for years costs a few minutes in total.</p>

      <h4>Flashcards that work</h4>
      <p>A spaced-repetition program does the scheduling for you. <b>Anki</b> is free, open source and runs everywhere, and since 2023 includes the FSRS scheduler, which fits a memory model to your own review history and targets 90% recall by default, the rule the example used. The program is the easy part; the cards decide whether it works. Make each card ask one thing, as a question you have to answer from memory, in your own words. Ask why and when, not just what: "Why must <code>cd</code> be a shell builtin?" teaches more than "What is <code>cd</code>?". Use cloze deletions, blanks in a sentence, for syntax, such as "<code>find . -name '*.py' -____ rm {} +</code>". Add cards as you learn, review every day, about fifteen minutes, and delete cards that annoy you. For this stage, good material is anything you've looked up twice: options, Git concepts, regular-expression syntax, exit statuses.</p>

      <h4>Deliberate practice</h4>
      <p>Facts are only part of it; most of this stage is skills, and skills are learned by practice of a particular kind. Anders Ericsson's studies of expert performers, beginning with violinists in 1993, distinguished <b>deliberate practice</b> from doing the activity. It has a specific goal just beyond what you can do now, immediate feedback, full attention, and repetition with refinement. Playing through pieces you already know isn't it, and neither is typing commands you already know. Learn Git Branching is deliberate practice for Git: each level is a precise goal, the graph shows you instantly whether you reached it, and you can repeat a level until it's fluent. So is solving an exercise in this volume a second time, a week later, from memory.</p>
      <p>Two more findings are worth knowing. <b>Interleaving</b>, mixing different kinds of problems in one session instead of practising one kind at a time, feels worse and works better, because each problem makes you first decide which tool it needs. Doug Rohrer and Kelli Taylor showed it with mathematics problems in 2007. And Robert Bjork's <b>desirable difficulties</b> sums up the chapter: the conditions that make practice feel harder, testing, spacing, interleaving, are the ones that make learning last. If studying feels easy, check that you're not just rereading.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>Rereading and highlighting</b> as the main way of studying.</li>
          <li><b>Cramming,</b> which serves tomorrow and forgets next month.</li>
          <li><b>Watching tutorials without doing the exercises,</b> which builds recognition, not skill.</li>
          <li><b>Flashcards that are too big,</b> "Explain Git", or that only ask you to recognise an answer.</li>
          <li><b>Practising only what you're already good at,</b> because it feels like progress.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 16.1</span><span class="ex-title">Ten cards</span></div>
          <p>Write ten flashcards for chapters 1 to 3 of this volume, and say what makes each a good card.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">Q: What does a program receive from the line  showargs $f  when f="my notes.txt"?
A: Two arguments, "my" and "notes.txt": the unquoted expansion is split.
Q: Why does  sort data.txt > data.txt  leave an empty file?
A: The shell truncates data.txt for the redirection before sort starts reading it.
Q: In what order are these applied:  cmd > out.txt 2>&1 ?   Where does stderr go?
A: Left to right: 1 to out.txt, then 2 to where 1 points: both go to out.txt.
Q: What's a pipeline's exit status by default, and what changes it?
A: The last command's; set -o pipefail makes it fail if any command failed.
Q: What does exit status 127 mean? And 126? And 130?
A: Command not found; found but not executable; killed by SIGINT (128 + 2).
Q: Why does uniq need sorted input?
A: It only merges duplicate lines that are adjacent.
Q: Fill in:  find . -name '*.tmp' -____ | xargs -0 rm
A: print0
Q: In a regular expression, what does . match? How do you match a real dot?
A: Any one character; \. (or grep -F for plain text).
Q: In awk, what are $1, $NF and NR?
A: The first field, the last field, and the current line's number.
Q: When does set -e not stop a script after a failing command?
A: When the command's status is being tested: in an if, a while, or beside && or ||.</code></pre>
            <p>Each card asks one thing, and most ask why or when, not just what, so that recalling the answer exercises understanding. They're questions you must answer from memory, not statements to recognise. The answers are short enough to check in a second. The fill-in card trains a detail that's easy to forget and expensive to get wrong. Write your own cards in your own words, rather than copying these: making the card is the first act of retrieval, and you'll remember your phrasing better than anyone else's.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 16.2</span><span class="ex-title">A week of deliberate practice</span></div>
          <p>Plan a week of deliberate practice to make Part III's Git operations fluent, at about thirty minutes a day.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>Day 1: Learn Git Branching's introduction levels, then repeat any level you needed hints for until you can do it without them. Day 2: in a scratch repository, recreate from memory the graph in chapter 10's example, a branch, a detached commit, a rescue from the reflog, checking with <code>git log --graph --all</code> after each step. Day 3: the "moving work around" levels, rebase and cherry-pick, and then make a conflict on purpose and resolve it twice, once by merging and once by rebasing. Day 4: interleave, with a mixed set of five small tasks, such as undoing a pushed commit, splitting a commit, recovering a deleted branch, bisecting a planted bug and fixing a commit message. Choosing the right command for each is half the exercise. Day 5: time yourself on day 4's set, then do it again without looking anything up. Each session has a specific goal, immediate feedback from the graph or the test, and a difficulty just past where you are. When a task becomes easy, replace it with a harder one. And put the facts you had to look up on flashcards.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 16.3</span><span class="ex-title">Earlier or later?</span></div>
          <p>The example reviewed each fact when its predicted recall fell to 90%. Predict what happens to the number of reviews, and to recall at day 90, if the rule is 97% instead, or 80%.</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">review when recall falls to   reviews per fact   recall at day 90   strength gained per review
97%                                 11.6                 83%                  x1.45
90%                                  4.8                 78%                  x2.50
80%                                  2.8                 65%                  x4.00</code></pre>
            <p>Reviewing earlier, at 97%, gives somewhat better recall, but at more than twice the work, because a review of something you recall easily strengthens it only a little. Reviewing later, at 80%, saves reviews, because each one strengthens more, but more facts are forgotten in between, and a forgotten fact starts again from one day. The figures come from running the example's model with each rule, so they show the trade-off rather than predict your memory. Real schedulers face the same trade-off, which is why Anki's FSRS lets you choose the recall you want and defaults to 90%, a reasonable balance between effort and forgetting.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you explain why rereading feels effective and isn't?</li>
            <li>Can you use retrieval practice in your own study: closed-book recall, questions, prediction?</li>
            <li>Can you explain the spacing effect, and why cramming fails a month later?</li>
            <li>Can you write good flashcards, and keep a daily review habit?</li>
            <li>Can you design deliberate practice for a skill, with a goal, feedback and rising difficulty?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind paid">Book</span><div><a href="https://www.hup.harvard.edu/books/9780674729018">Make It Stick: The Science of Successful Learning</a> <span class="by">Brown, Roediger &amp; McDaniel</span></div></li>
            <li><span class="rkind free">Essay</span><div><a href="https://augmentingcognition.com/ltm.html">Augmenting Long-term Memory</a> <span class="by">Michael Nielsen</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://docs.ankiweb.net/background.html">Anki Manual: Background</a> <span class="by">Ankitects</span></div></li>
          </ul>
        </div>
      </div>
    </section>
