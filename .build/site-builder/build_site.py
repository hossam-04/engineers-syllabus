import re, json, pathlib, sys, html as H

WS = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else WS / "syllabus-site"
OUT.mkdir(exist_ok=True)
HOST = "software-engineering-study-plan"

# Stage order. slug = storage prefix (kept stable so readers' marks survive republishes).
VOLS = [
  dict(slug="whet",  page="whetstone.html", stage="00", subject="Tools, the shell &amp; learning", name="Whetstone", src="tools-handbook",
       blurb="The tools under every other stage: the shell and its text tools, files and permissions, Git as a data structure, one editor, and how to learn, with every example run against the real tools."),
  dict(slug="prim",  page="primer.html",   stage="01", subject="Programming foundations", name="Primer", src="programming-handbook",
       blurb="Learning to program from the first expression up: functions and recursion, lists and dictionaries, files, tests and the debugger, classes, then a tool, a game and an API client."),
  dict(slug="work",  page="workbench.html", stage="02", subject="Data structures &amp; algorithms", name="Workbench", src="algorithms-handbook",
       blurb="The structures every language hands you, built from nothing and measured: arrays, hash tables, heaps, trees, sorts and sketches, then the problems with no fast answer."),
  dict(slug="comp",  page="compass.html",  stage="03", subject="Mathematics", name="Compass", src="mathematics-handbook",
       blurb="The mathematics an engineer actually uses, from logic, proof and counting to probability, linear algebra and statistics, every result proved and then checked by running code."),
  dict(slug="mill",  page="mill.html",     stage="04", subject="Computer architecture", name="Mill", src="architecture-handbook",
       blurb="A computer built from a single kind of gate up to a CPU that runs real programs, then the caches, pipelines and parallel hardware that decide how fast code runs."),
  dict(slug="loom",  page="loom.html",     stage="05", subject="Operating systems &amp; concurrency", name="Loom", src="operating-systems-handbook",
       blurb="How one machine is shared between many programs: processes, scheduling, locks and the bugs they prevent, virtual memory, file systems that survive a crash, and containers."),
  dict(slug="exch",  page="exchange.html", stage="06", subject="Networking",          name="Exchange", src="networking-handbook",
       blurb="Networking from the top down, from HTTP and TLS through TCP, IP and DNS to CDNs, load balancing and diagnosis."),
  dict(slug="press", page="press.html",    stage="07", subject="Languages &amp; compilers", name="Press", src="compilers-handbook",
       blurb="How a language implementation reads and runs a program: lexers and parsers, type checkers, interpreters and bytecode machines, garbage collection, optimisation and JIT compilation."),
  dict(slug="ledg",  page="ledger.html",   stage="08", subject="Databases",           name="Ledger",   src="databases-handbook",
       blurb="What a database does with your query: pages, B-trees and LSM trees, the planner, transactions and the write-ahead log."),
  dict(slug="craft", page="craft.html",    stage="09", subject="Software craft",      name="Craft",    src="software-craft-handbook",
       blurb="Writing code a team can still change safely in two years, through naming, design, tests, review and debugging."),
  dict(slug="ship",  page="shipyard.html", stage="10", subject="Shipping products",   name="Shipyard", src="shipping-products-handbook",
       blurb="Assembling code into a product strangers use and pay for, from the API and sign-in to releases and launch."),
  dict(slug="fleet", page="fleet.html",    stage="11", subject="Distributed systems", name="Fleet",    src="distributed-systems-handbook",
       blurb="Making many machines behave like one dependable system, and knowing when not to try."),
  dict(slug="watch", page="watch.html",    stage="12", subject="Production &amp; infra", name="Watch", src="production-reliability-handbook",
       blurb="Getting from your laptop to a system that stays up, with packaging, delivery, observability and reliability."),
  dict(slug="cita",  page="citadel.html",  stage="13", subject="Security",            name="Citadel",  src="security-engineering-handbook",
       blurb="Security engineering in depth, across web applications, identity, cryptography and the platform."),
  dict(slug="found", page="foundry.html",  stage="14", subject="AI engineering",      name="Foundry",  src="ai-engineering-handbook",
       blurb="Casting a language model into a feature you can trust, with retrieval, tools and evaluation at the centre."),
  dict(slug="guild", page="guild.html",    stage="15", subject="Mastery",             name="Guild",    src="mastery-handbook",
       blurb="The practices that turn a capable engineer into a senior one: reading papers and code, design documents, estimating, leading, mentoring, the business, and a career that compounds."),
]
NUM_WORDS = {7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen", 16: "Sixteen"}

def rd(f): return (WS / (f + ".html")).read_text(encoding="utf-8")

for v in VOLS:
    s = rd(v["src"])
    v["title"] = re.search(r'<h1[^>]*>(.*?)</h1>', s).group(1)
    meta = dict(re.findall(r'<span class="k">(.*?)</span><span class="v">(.*?)</span>',
                           re.search(r'class="masthead-meta">(.*?)</div>\s*</header>', s, re.S).group(1)))
    v["n"] = int(meta["Chapters"]); v["examples"] = meta["Code examples"]
    v["exercises"] = meta["Exercises"]; v["hours"] = meta["Stage budget"]
    assert v["n"] == len(re.findall(r'<section[^>]*\sid="ch\d\d"', s)), v["src"]
    assert H.unescape(v["title"]).endswith(v["name"]), v["title"]
TOTAL = sum(v["n"] for v in VOLS)
MANIFEST = json.dumps([{"slug": v["slug"], "n": v["n"]} for v in VOLS])
COUNT_WORD = NUM_WORDS[len(VOLS)]
SHELF_LEAD = ("Every one of the sixteen stages has a companion volume" if len(VOLS) == 16
              else f"{COUNT_WORD} of the sixteen stages have a companion volume")

THEME_PRELOAD = ('<script>if(!document.documentElement.lang)document.documentElement.lang="en";try{var t=localStorage.getItem("englibrary.v1.theme");'
                 'if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}catch(e){}</script>')

CONTROLLER = r"""
(function () {
  var CFG = __CFG__;
  var LS = "englibrary.v1.", NS = CFG.ns || "", VOLS = CFG.vols || [];
  function read(k) { try { return window.localStorage.getItem(LS + k); } catch (e) { return null; } }
  function write(k, v) { try { window.localStorage.setItem(LS + k, v); } catch (e) { /* storage unavailable */ } }

  try { if (window.hljs) window.hljs.highlightAll(); } catch (e) { /* plain code is fine */ }

  // Marks are shared by every page of the book: one storage key per chapter or stage.
  var boxes = Array.prototype.slice.call(document.querySelectorAll(".done-toggle input[data-id]"));
  function key(b) { return NS + b.getAttribute("data-id"); }
  var chap = boxes.filter(function (b) { return /(^|-)ch\d\d$/.test(b.getAttribute("data-id")); });
  var stages = boxes.filter(function (b) { return /^s\d\d$/.test(b.getAttribute("data-id")); });

  function bar(pctId, fillId, n, total) {
    var p = document.getElementById(pctId), f = document.getElementById(fillId);
    if (p) p.textContent = n + " / " + total;
    if (f) f.style.width = (total ? (n / total) * 100 : 0) + "%";
  }
  function volRead(v) {
    var n = 0;
    for (var i = 1; i <= v.n; i++) if (read(v.slug + "-ch" + (i < 10 ? "0" : "") + i) === "1") n++;
    return n;
  }
  function refresh() {
    boxes.forEach(function (b) {
      var id = b.getAttribute("data-id");
      var sec = document.getElementById(id);
      var link = document.querySelector('#railnav a[href="#' + id + '"]');
      var stage = b.closest(".stage");
      if (sec) sec.classList.toggle("is-read", b.checked);
      if (link) link.classList.toggle("read", b.checked);
      if (stage) stage.classList.toggle("is-done", b.checked);
    });
    if (chap.length) {
      var n = 0; chap.forEach(function (b) { if (b.checked) n++; });
      bar("pct", "barfill", n, chap.length);
    } else if (VOLS.length) {
      var got = 0, all = 0;
      VOLS.forEach(function (v) { got += volRead(v); all += v.n; });
      bar("pct", "barfill", got, all);
    }
    if (stages.length) {
      var s = 0; stages.forEach(function (b) { if (b.checked) s++; });
      bar("pct-stages", "barfill-stages", s, stages.length);
    }
    VOLS.forEach(function (v) {
      var c = volRead(v);
      Array.prototype.forEach.call(document.querySelectorAll('[data-vol="' + v.slug + '"]'), function (el) {
        var t = el.querySelector(".vm-count"), f = el.querySelector(".vm-fill");
        if (t) t.textContent = c + " / " + v.n + " read";
        if (f) f.style.width = (c / v.n) * 100 + "%";
      });
    });
  }
  boxes.forEach(function (b) {
    if (read(key(b)) === "1") b.checked = true;
    b.addEventListener("change", function () { write(key(b), b.checked ? "1" : "0"); refresh(); });
  });
  window.addEventListener("storage", function (e) {
    if (e.key && e.key.indexOf(LS) !== 0) return;
    boxes.forEach(function (b) { b.checked = read(key(b)) === "1"; });
    refresh();
  });
  refresh();

  // Reset asks for a second click inside the page, because the viewer blocks dialog boxes.
  var reset = document.getElementById("resetbtn");
  if (reset) {
    var label = reset.textContent, timer = null;
    var disarm = function () { clearTimeout(timer); timer = null; reset.textContent = label; reset.classList.remove("armed"); };
    reset.addEventListener("click", function () {
      if (!timer) {
        reset.textContent = CFG.resetAsk || "Click again to clear";
        reset.classList.add("armed");
        timer = setTimeout(disarm, 4000);
        return;
      }
      disarm();
      boxes.forEach(function (b) { b.checked = false; write(key(b), "0"); });
      refresh();
    });
  }

  var root = document.documentElement;
  var stored = read("theme");
  if (stored === "dark" || stored === "light") root.setAttribute("data-theme", stored);
  var tb = document.getElementById("themebtn");
  if (tb) tb.addEventListener("click", function () {
    var now = root.getAttribute("data-theme");
    var dark = now ? now === "dark"
      : (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
    var next = dark ? "light" : "dark";
    root.setAttribute("data-theme", next);
    write("theme", next);
    pressed();
  });
  function pressed() {
    if (!tb) return;
    var now = root.getAttribute("data-theme");
    var dark = now ? now === "dark" : (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
    tb.setAttribute("aria-pressed", dark ? "true" : "false");
    tb.setAttribute("aria-label", "Dark theme");
  }
  pressed();

  var toc = document.querySelector(".toc");
  if (toc && window.matchMedia) {
    var narrow = window.matchMedia("(max-width: 1080px)");
    var syncToc = function () { if (narrow.matches) toc.removeAttribute("open"); else toc.setAttribute("open", ""); };
    syncToc();
    if (narrow.addEventListener) narrow.addEventListener("change", syncToc);
    else if (narrow.addListener) narrow.addListener(syncToc);
  }

  var links = Array.prototype.slice.call(document.querySelectorAll('#railnav a[href^="#"]'));
  var targets = links.map(function (a) { try { return document.querySelector(a.getAttribute("href")); } catch (e) { return null; } });
  if (window.IntersectionObserver) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var i = targets.indexOf(e.target);
        if (i < 0) return;
        links.forEach(function (l) { l.classList.remove("on"); });
        links[i].classList.add("on");
      });
    }, { rootMargin: CFG.spy || "-8% 0px -80% 0px" });
    targets.forEach(function (t) { if (t) io.observe(t); });
  }
})();
"""
SYNC_JS = r"""
// Progress follows the reader between devices. Every page keeps its marks, reading places and
// flashcard schedule in this browser; when the viewer is signed in to Claude, this mirrors them
// into a record only that viewer can read, and merges in what their other devices saved.
(function () {
  var LS = "englibrary.v1.", META = LS + "sync.meta", SKIP = /^(theme$|sync\.)/, TICK = 15000;
  if (!window.claude || typeof window.claude.use !== "function") return;
  function parse(s, d) { try { var v = JSON.parse(s); return v == null ? d : v; } catch (e) { return d; } }
  function local() {
    var out = {};
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (k && k.indexOf(LS) === 0 && !SKIP.test(k.slice(LS.length))) out[k.slice(LS.length)] = localStorage.getItem(k);
      }
    } catch (e) { /* storage unavailable */ }
    return out;
  }
  // meta holds [value, time changed] for every key as of the last merge; a value that differs
  // from it now was changed on this device since then.
  function stamp(meta) {
    var cur = local(), now = Date.now();
    for (var k in cur) if (!meta[k] || meta[k][0] !== cur[k]) meta[k] = [cur[k], now];
    return meta;
  }
  function sortedJSON(o) { var out = {}; Object.keys(o).sort().forEach(function (k) { out[k] = o[k]; }); return JSON.stringify(out); }
  // Flashcards merge card by card, so reviews done on two devices both count. A card's entry is
  // [box, due day]; the later due day wins, and on a tie the side changed most recently.
  function mergeSrs(a, b) {
    var newer = a[1] >= b[1] ? a : b, older = newer === a ? b : a;
    var nv = parse(newer[0], {}), ov = parse(older[0], {}), out = {}, id;
    if (!Object.keys(nv).length) return newer;              // a reset on the newer side wins
    for (id in ov) out[id] = ov[id];
    for (id in nv) if (!out[id] || nv[id][1] >= out[id][1]) out[id] = nv[id];
    return [sortedJSON(out), newer[1]];
  }
  function merge(k, a, b) {
    if (!a) return b; if (!b || a[0] === b[0]) return a;
    if (k === "srs") return mergeSrs(a, b);
    if (k.indexOf("pos.") === 0) return (parse(a[0], {}).t || 0) >= (parse(b[0], {}).t || 0) ? a : b;
    return a[1] >= b[1] ? a : b;
  }
  function mergeAll(meta, remote) {
    var out = {}, k;
    for (k in meta) out[k] = merge(k, meta[k], remote[k]);
    for (k in remote) if (!out[k]) out[k] = remote[k];
    // the list of recent volumes follows the reading places it points to
    if (meta.recent && remote.recent && meta.recent[0] !== remote.recent[0]) {
      var slugs = [];
      for (k in out) if (k.indexOf("pos.") === 0) slugs.push([k.slice(4), parse(out[k][0], {}).t || 0]);
      slugs.sort(function (x, y) { return y[1] - x[1]; });
      out.recent = [JSON.stringify(slugs.slice(0, 16).map(function (x) { return x[0]; })), Math.max(meta.recent[1], remote.recent[1])];
    }
    return out;
  }
  function same(a, b) {
    var k;
    for (k in a) if (!b[k] || b[k][0] !== a[k][0] || b[k][1] !== a[k][1]) return false;
    for (k in b) if (!a[k]) return false;
    return true;
  }
  function fromDoc(d) {
    var out = {};
    ((d && d.entries) || []).forEach(function (e) { if (e && typeof e[0] === "string" && typeof e[1] === "string") out[e[0]] = [e[1], +e[2] || 0]; });
    return out;
  }
  function toDoc(m) { return { v: 1, entries: Object.keys(m).sort().map(function (k) { return [k, m[k][0], m[k][1]]; }) }; }

  var ref = null, remote = {}, writing = false, stopped = false, note = null;
  function say(text) {
    if (!note) {
      var box = document.querySelector(".rail .progress-box"); if (!box) return;
      note = document.createElement("p"); note.className = "sync-note"; box.parentNode.insertBefore(note, box.nextSibling);
    }
    note.textContent = text;
  }
  // Bring what other devices saved into this browser, then tell the page to redraw.
  function pull(doc) {
    remote = fromDoc(doc);
    var meta = stamp(parse(localStorage.getItem(META), {})), merged = mergeAll(meta, remote), changed = false;
    try {
      for (var k in merged) if (localStorage.getItem(LS + k) !== merged[k][0]) { localStorage.setItem(LS + k, merged[k][0]); changed = true; }
      localStorage.setItem(META, JSON.stringify(merged));
    } catch (e) { return; }
    if (changed) {
      try { window.dispatchEvent(new StorageEvent("storage", { key: LS + "sync" })); } catch (e) { /* old browser */ }
      window.dispatchEvent(new CustomEvent("englibrary:sync"));
    }
  }
  // Save this device's changes, at most once a tick and only when something changed.
  function push() {
    if (!ref || writing || stopped) return;
    var meta;
    try { meta = stamp(parse(localStorage.getItem(META), {})); localStorage.setItem(META, JSON.stringify(meta)); } catch (e) { return; }
    var merged = mergeAll(meta, remote);
    if (same(merged, remote)) return;
    writing = true;
    ref.set(toDoc(merged)).then(function () {
      writing = false; remote = merged; say("Progress synced to your account");
    }, function (e) {
      writing = false;
      if (e && (e.code === "invalid_argument" || e.code === "revoked" || e.code === "quota_exceeded" || e.code === "not_granted")) { stopped = true; say("Progress saved in this browser only"); }
    });
  }
  Promise.all([window.claude.use("db"), window.claude.use("user")]).then(function (r) {
    var db = r[0], user = r[1];
    if (!db || !user) return null;
    return user.id().then(function (id) {
      if (!id) return;
      ref = db.doc("data/users/" + id + "/progress");
      var first = function (tries) {
        ref.get().then(function (snap) {
          pull(snap.exists ? snap.data() : null); say("Progress synced to your account"); push();
          ref.onSnapshot(function (s) {
            if (s.metadata.fromCache || s.metadata.hasPendingWrites || writing) return;
            pull(s.exists ? s.data() : null);
          }, function () { /* the timer still saves; a later visit subscribes again */ });
          setInterval(function () { if (document.visibilityState !== "hidden") push(); }, TICK);
          document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") push(); });
          window.addEventListener("pagehide", push);
        }, function (e) {
          if (e && e.code === "unavailable" && tries < 1) setTimeout(function () { first(tries + 1); }, 1500 + Math.random() * 1500);
        });
      };
      first(0);
    });
  }).catch(function () { /* sync is an extra; the page works without it */ });
})();

// Edition downloads go through the viewer's save prompt where it offers one; anywhere else the
// links are plain download links.
(function () {
  var links = document.querySelectorAll("a[data-dl]");
  if (!links.length || !window.claude || typeof window.claude.use !== "function") return;
  var dl = null;
  window.claude.use("downloads").then(function (d) { dl = d; }, function () {});
  Array.prototype.forEach.call(links, function (a) {
    a.addEventListener("click", function (e) {
      if (!dl) return;
      e.preventDefault();
      if (a.classList.contains("busy")) return;
      a.classList.add("busy");
      var done = function () { a.classList.remove("busy"); };
      fetch(a.getAttribute("href")).then(function (r) {
        if (!r.ok) throw { code: "unavailable" };
        return r.blob();
      }).then(function (blob) {
        return dl.save({ filename: a.getAttribute("data-dl"), data: blob });
      }).then(done, function (err) {
        done();
        var code = err && err.code;
        if (code === "declined" || code === "rate_limited") return;
        dl = null; a.click();                       // the viewer can't save it: try the plain link
      });
    });
  });
})();
"""

A11Y_JS = r"""
// Wide code blocks and tables scroll sideways; each one that does gets a keyboard stop and a
// name, so it can be scrolled without a mouse. Rechecked when the window changes size.
(function () {
  // A region's name says what it holds: the example's file name, or the nearest heading.
  function about(el) {
    var fig = el.closest("figure"), file = fig && fig.querySelector(".file");
    if (file) return file.textContent.trim() + (el.classList.contains("out") ? " output" : "");
    var n = el;
    while (n && n !== document.body) {
      var p = n.previousElementSibling;
      while (p) {
        if (/^H[2-5]$/.test(p.tagName)) return p.textContent.trim();
        var h = p.querySelector && p.querySelector("h2, h3, h4, h5");
        if (h && p.tagName !== "FIGURE") return h.textContent.trim();
        p = p.previousElementSibling;
      }
      n = n.parentElement;
    }
    return "";
  }
  function mark() {
    var used = {};
    Array.prototype.forEach.call(document.querySelectorAll("[data-scroll-focus]"), function (el) { used[el.getAttribute("aria-label")] = 1; });
    Array.prototype.forEach.call(document.querySelectorAll("pre, .table-wrap"), function (el) {
      var wide = el.scrollWidth > el.clientWidth, has = el.hasAttribute("data-scroll-focus");
      if (wide && !has && !el.hasAttribute("tabindex")) {
        var base = (el.classList.contains("table-wrap") ? "Table" : "Code") + (about(el) ? ": " + about(el) : ""), name = base, i = 2;
        while (used[name]) name = base + " (" + (i++) + ")";
        used[name] = 1;
        el.setAttribute("tabindex", "0"); el.setAttribute("data-scroll-focus", ""); el.setAttribute("role", "region");
        el.setAttribute("aria-label", name);
      } else if (!wide && has) {
        ["tabindex", "data-scroll-focus", "role", "aria-label"].forEach(function (a) { el.removeAttribute(a); });
      }
    });
  }
  mark();
  // Web fonts and the code highlighter can widen blocks after the first check.
  window.addEventListener("load", mark);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(mark);
  var t = null;
  window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(mark, 200); });
})();
"""

def controller(**cfg):
    cfg.setdefault("vols", json.loads(MANIFEST))
    return CONTROLLER.replace("__CFG__", json.dumps(cfg)) + SYNC_JS + A11Y_JS

MONO = '"IBM Plex Mono", ui-monospace, Menlo, monospace'
DISPLAY = '"Archivo", "Helvetica Neue", Arial, sans-serif'

BASE_CSS = """
/* ===== base for pages served on their own ===== */
:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
body { margin: 0; }
img { max-width: 100%; }
[hidden] { display: none !important; }
"""
LIB_CSS = f"""
/* ===== library navigation ===== */
.lib-nav {{ display: flex; flex-direction: column; gap: 10px; padding-bottom: 18px; border-bottom: 1px solid var(--rule); }}
.lib-home {{ color: var(--ink); text-decoration: none; font-weight: 600; }}
.lib-home:hover {{ color: var(--marine); }}
.lib-vols {{ display: flex; flex-wrap: wrap; gap: 4px 12px; }}
.lib-vols a {{ color: var(--ink-soft); text-decoration: none; border-bottom: 1px solid transparent; }}
.lib-vols a .n {{ color: var(--brass); margin-right: 5px; }}
.lib-vols a:hover {{ color: var(--ink); border-bottom-color: var(--marine); }}
.lib-vols a[aria-current="page"] {{ color: var(--ink); border-bottom-color: var(--marine); font-weight: 600; }}
.tool-btn.armed {{ color: var(--gap); border-color: var(--gap); }}
.vol-pager {{ display: grid; gap: 12px; margin: 72px 0 0; }}
.vol-pager.n3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
.vol-pager.n2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
.vol-pager a {{ display: flex; flex-direction: column; gap: 4px; min-width: 0; padding: 14px 16px; border: 1px solid var(--rule); background: var(--surface); color: var(--ink); text-decoration: none; }}
.vol-pager a:hover {{ border-color: var(--marine); }}
.vol-pager .vp-k {{ font-family: {MONO}; font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase; color: var(--ink-soft); }}
.vol-pager .vp-t {{ font-family: {DISPLAY}; font-weight: 600; font-size: 17px; line-height: 1.25; }}
.vol-pager .vp-next {{ text-align: right; }}
@media (max-width: 640px) {{ .vol-pager.n3, .vol-pager.n2 {{ grid-template-columns: minmax(0, 1fr); }} .vol-pager .vp-next {{ text-align: left; }} }}
a:focus-visible, .tool-btn:focus-visible {{ outline: 2px solid var(--marine); outline-offset: 2px; }}
"""
HUB_CSS = f"""
/* ===== companion volumes ===== */
.vol-list {{ list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }}
.vol-list li {{ border-bottom: 1px solid var(--rule); }}
.vol-row {{ display: grid; grid-template-columns: 64px minmax(0, 1fr) 150px; gap: 6px 24px; align-items: start; padding: 18px 10px; color: var(--ink); text-decoration: none; }}
.vol-row:hover {{ background: var(--surface); }}
.vol-row:hover .vr-title {{ color: var(--marine); }}
.vr-stage {{ display: flex; flex-direction: column; gap: 2px; font-family: {MONO}; }}
.vr-stage .k {{ font-size: 10px; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-soft); }}
.vr-stage b {{ font-size: 22px; font-weight: 600; line-height: 1.1; color: var(--brass); font-variant-numeric: tabular-nums; }}
.vr-main {{ display: flex; flex-direction: column; gap: 4px; min-width: 0; }}
.vr-kicker {{ font-family: {MONO}; font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase; color: var(--ink-soft); }}
.vr-title {{ font-family: {DISPLAY}; font-weight: 700; font-size: 21px; line-height: 1.2; letter-spacing: -.01em; text-wrap: balance; }}
.vr-blurb {{ font-size: 16px; line-height: 1.5; color: var(--ink-mid); max-width: 40em; }}
.vr-meta {{ font-family: {MONO}; font-size: 11.5px; color: var(--ink-soft); font-variant-numeric: tabular-nums; }}
.vol-meter {{ display: flex; flex-direction: column; gap: 6px; padding-top: 4px; font-family: {MONO}; font-size: 11px; color: var(--ink-soft); font-variant-numeric: tabular-nums; }}
.vm-track {{ display: block; height: 4px; background: var(--surface-sunk); overflow: hidden; }}
.vm-fill {{ display: block; height: 100%; width: 0; background: var(--marine); }}
.vol-all {{ display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px 18px; margin-top: 4px; padding: 16px 10px; font-family: {MONO}; font-size: 12px; color: var(--ink-mid); text-decoration: none; }}
.vol-all:hover {{ color: var(--marine); }}
.vol-all b {{ font-weight: 600; color: var(--ink); }}
.companion {{ display: grid; grid-template-columns: minmax(0, 1fr) 160px; gap: 8px 22px; align-items: center; margin: 0 0 24px; max-width: 62ch; padding: 14px 18px; background: var(--surface); border-left: 3px solid var(--marine); color: var(--ink); text-decoration: none; }}
.companion:hover .cp-t {{ color: var(--marine); }}
.cp-main {{ display: flex; flex-direction: column; gap: 3px; min-width: 0; }}
.cp-k {{ font-family: {MONO}; font-size: 10px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--marine); }}
.cp-t {{ font-family: {DISPLAY}; font-weight: 700; font-size: 19px; line-height: 1.2; }}
.cp-m {{ font-family: {MONO}; font-size: 11px; color: var(--ink-soft); font-variant-numeric: tabular-nums; }}
.cp-side {{ display: flex; flex-direction: column; gap: 6px; font-family: {MONO}; font-size: 11px; color: var(--ink-soft); font-variant-numeric: tabular-nums; }}
.cp-go {{ color: var(--ink); font-weight: 600; }}
.tool-btn.armed {{ color: var(--gap); border-color: var(--gap); }}
a:focus-visible, .tool-btn:focus-visible {{ outline: 2px solid var(--marine); outline-offset: 2px; }}
@media (max-width: 640px) {{
  .vol-row {{ grid-template-columns: 48px minmax(0, 1fr); gap: 6px 14px; }}
  .vol-meter {{ grid-column: 2; }}
  .vr-stage b {{ font-size: 18px; }}
  .companion {{ grid-template-columns: minmax(0, 1fr); }}
}}
"""

def vol_meta(v):
    return f'{v["n"]} chapters &middot; {v["examples"]} code examples &middot; {v["exercises"]} exercises &middot; {v["hours"]}'

def shelf_html(href, all_link):
    rows = []
    for v in VOLS:
        rows.append(f'''      <li><a class="vol-row" href="{href(v)}" data-vol="{v["slug"]}">
        <span class="vr-stage"><span class="k">Stage</span><b>{v["stage"]}</b></span>
        <span class="vr-main">
          <span class="vr-kicker">{v["subject"]}</span>
          <span class="vr-title">{v["title"]}</span>
          <span class="vr-blurb">{v["blurb"]}</span>
          <span class="vr-meta">{vol_meta(v)}</span>
        </span>
        <span class="vol-meter"><span class="vm-count">0 / {v["n"]} read</span><span class="vm-track"><span class="vm-fill"></span></span></span>
      </a></li>''')
    return f'''
    <!-- ============ COMPANION VOLUMES ============ -->
    <section id="volumes">
      <h2 class="sec">The companion volumes</h2>
      <div class="prose">
        <p>{SHELF_LEAD}: a book-length study guide with worked examples you can run, exercises with folded solutions, and a checklist and reading list for every chapter. Chapter marks you set in a volume are saved in this browser and counted here.</p>
      </div>
      <ol class="vol-list">
{chr(10).join(rows)}
      </ol>
      {all_link}
    </section>
'''

def companion_html(v, href):
    return (f'\n        <a class="companion" href="{href(v)}" data-vol="{v["slug"]}">'
            f'<span class="cp-main"><span class="cp-k">Companion volume</span><span class="cp-t">{v["title"]}</span>'
            f'<span class="cp-m">{v["n"]} chapters &middot; {v["examples"]} code examples &middot; {v["exercises"]} exercises</span></span>'
            f'<span class="cp-side"><span class="vm-count">0 / {v["n"]} read</span><span class="vm-track"><span class="vm-fill"></span></span>'
            f'<span class="cp-go">Open the volume &rarr;</span></span></a>')

def augment_syllabus_main(main_html, href, all_link):
    i = main_html.index("</header>") + len("</header>")
    main_html = main_html[:i] + "\n" + shelf_html(href, all_link) + main_html[i:]
    for v in VOLS:
        m = re.search(r'<section class="stage" id="s' + v["stage"] + r'"', main_html)
        j = main_html.index("</p>", main_html.index('<p class="stage-why">', m.end())) + len("</p>")
        main_html = main_html[:j] + companion_html(v, href) + main_html[j:]
    return main_html

def libnav(current=None, home_label="&larr; The Engineer's Syllabus", with_vols=True):
    vols = ""
    if with_vols:
        items = "".join(
            f'<a href="{v["page"]}"' + (' aria-current="page"' if v is current else "") +
            f'><span class="n">{v["stage"]}</span>{v["name"]}</a>' for v in VOLS)
        vols = f'\n      <div class="lib-vols">{items}</div>'
    return f'    <nav class="lib-nav" aria-label="The Engineer\'s Syllabus">\n      <a class="lib-home" href="index.html">{home_label}</a>{vols}\n    </nav>\n'

def pager(i):
    cells = []
    if i > 0:
        p = VOLS[i - 1]
        cells.append(f'<a class="vp-prev" href="{p["page"]}"><span class="vp-k">&larr; Stage {p["stage"]}</span><span class="vp-t">{p["title"]}</span></a>')
    cells.append('<a class="vp-home" href="index.html#volumes"><span class="vp-k">All volumes</span><span class="vp-t">The Engineer\'s Syllabus</span></a>')
    if i < len(VOLS) - 1:
        n = VOLS[i + 1]
        cells.append(f'<a class="vp-next" href="{n["page"]}"><span class="vp-k">Stage {n["stage"]} &rarr;</span><span class="vp-t">{n["title"]}</span></a>')
    return f'    <nav class="vol-pager n{len(cells)}" aria-label="Volumes">\n      ' + "\n      ".join(cells) + '\n    </nav>\n\n'

def full_doc(head_inner, body_inner):
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'{head_inner}\n{THEME_PRELOAD}\n</head>\n<body>\n{body_inner}\n</body>\n</html>\n')

def split_page(s):
    k = s.index('<div class="shell">')
    head, body = s[:k], s[k:]
    srcs = re.findall(r'<script src="[^"]+"></script>', body)
    body = re.sub(r'<script src="[^"]+"></script>\s*', '', body)
    body = re.sub(r'<script>.*?</script>\s*', '', body, flags=re.S)
    assert "<script" not in head and head.count("<style>") == 1
    return head.rstrip(), body.rstrip(), srcs

# ---------------- offline editions (built by .build/editions) ----------------
# Artifacts serve PDFs but not EPUBs or ZIPs, so the site offers the print edition only; the
# EPUBs live in the project's editions/ folder.
import shutil
ED = WS / "editions"
def _size(n): return f"{n / 1e6:.1f} MB" if n >= 1e6 else f"{round(n / 1e3)} KB"
EDITIONS = []        # (stage, title, slug, {"epub": (path, size), "pdf": ...})
for _v in [dict(slug="syllabus", name="Syllabus", stage="", title="The Engineer's Syllabus")] + VOLS:
    files = {k: ED / k / f'{_v["name"]}.{k}' for k in ("pdf",)}
    if all(f.exists() for f in files.values()):
        EDITIONS.append((_v["stage"], _v.get("title", "The Engineer's " + _v["name"]), _v["slug"],
                         {k: (f"editions/{f.name}", _size(f.stat().st_size)) for k, f in files.items()}))
def dl_link(path, filename, label):
    return f'<a href="{path}" download="{H.escape(filename, quote=True)}" data-dl="{H.escape(filename, quote=True)}">{label}</a>'
def libdl(slug):
    e = next((x for x in EDITIONS if x[2] == slug), None)
    if not e: return ""
    return ('    <div class="lib-dl"><span>Offline</span>' +
            dl_link(e[3]["pdf"][0], e[1] + ".pdf", "PDF") + f' <span class="sz">{e[3]["pdf"][1]}</span></div>\n')
def editions_html():
    if not EDITIONS: return ""
    rows = "".join(
        f'<tr><td><span class="n">{st or "&middot;"}</span>{H.escape(t)}</td>'
        f'<td>{dl_link(f["pdf"][0], t + ".pdf", "PDF")} <span class="sz">{f["pdf"][1]}</span></td></tr>'
        for st, t, _, f in EDITIONS)
    return f"""
    <!-- ============ OFFLINE EDITIONS ============ -->
    <section id="editions">
      <h2 class="sec">Offline editions</h2>
      <div class="prose">
        <p>The syllabus and every volume as a PDF, to read without a connection or to print. Each is laid out on A4 with a contents page, page numbers and bookmarks, and prints every exercise's solution after the exercise. Your marks and flashcards stay here, on the site.</p>
      </div>
      <div class="table-wrap"><table class="eds">
        <thead><tr><th>Book</th><th>PDF, A4</th></tr></thead>
        <tbody>{rows}</tbody>
      </table></div>
    </section>
"""

# ---------------- study tools: search, continue reading, flashcards ----------------
exec(compile(open(pathlib.Path(__file__).parent / "study.py").read(), "study.py", "exec"))

# ---------------- volume pages ----------------
for i, v in enumerate(VOLS):
    head, body, srcs = split_page(rd(v["src"]))
    assert body.count('<aside class="rail">') == 1 and body.count('<footer class="colophon">') == 1
    body = annotate_volume(body, i, v)
    body = body.replace('<aside class="rail">', '<aside class="rail">\n' + libnav(current=v) + libstudy() + libdl(v["slug"]), 1)
    body = body.replace('<footer class="colophon">', pager(i) + '    <footer class="colophon">', 1)
    head = head + f"\n<style>{BASE_CSS}{LIB_CSS}{STUDY_CSS}</style>"
    js = controller(ns=v["slug"] + "-", resetAsk="Click again to clear")
    sjs = study_js(mode="vol", slug=v["slug"], page=v["page"])
    (OUT / v["page"]).write_text(full_doc(head, body + "\n\n" + "\n".join(srcs) + f"\n<script>{js}</script>\n<script>{sjs}</script>"), encoding="utf-8")

# ---------------- one-page edition (all.html) ----------------
exec(compile(open(pathlib.Path(__file__).parent / "lib_merge.py").read(), "lib_merge.py", "exec"))
ALL_MB = (OUT / "all.html").stat().st_size / 1e6

# ---------------- hub (main page; the publisher adds the skeleton) ----------------
host = rd(HOST)
hk = host.index('<div class="shell">')
hhead, hbody = host[:hk], host[hk:]
hbody = re.sub(r'<script>.*?</script>\s*', '', hbody, flags=re.S)
assert "<script" not in hbody
index_syllabus(hbody)
assert hbody.count('<aside class="rail">') == 1
hbody = hbody.replace('<aside class="rail">', '<aside class="rail">\n' + libstudy(), 1)
hhead = hhead.replace("</style>", HUB_CSS + STUDY_CSS + "</style>", 1) + "\n" + THEME_PRELOAD + "\n"
old_prog = re.search(r'<div class="progress-box">.*?</div>\s*</div>', hbody, re.S).group(0)
new_prog = (f'<div class="progress-box">\n      <div class="progress-row"><span>Chapters read</span><b id="pct">0 / {TOTAL}</b></div>\n'
            '      <div class="bar"><span id="barfill"></span></div>\n'
            '      <div class="progress-row"><span>Stages done</span><b id="pct-stages">0 / 16</b></div>\n'
            '      <div class="bar"><span id="barfill-stages"></span></div>\n    </div>')
hbody = hbody.replace(old_prog, new_prog, 1)
hbody = hbody.replace('<nav class="rail-nav" id="railnav">',
                      '<nav class="rail-nav" id="railnav">\n      <a href="#volumes"><span class="n">§</span><span>Companion volumes</span></a>'
                      + ('\n      <a href="#editions"><span class="n">§</span><span>Offline editions</span></a>' if EDITIONS else ''), 1)
vol_links = "".join(f'\n      <a href="{v["page"]}"><span class="n">{v["stage"]}</span><span>{v["name"]}</span></a>' for v in VOLS)
anchor = re.search(r'<a href="#entry">.*?</a>', hbody).group(0)
hbody = hbody.replace(anchor, anchor + '\n      <div class="sep">Volumes</div>' + vol_links +
                      '\n      <a href="all.html"><span class="n">§</span><span>One-page edition</span></a>', 1)
mi = hbody.index("<main>") + len("<main>"); me = hbody.rindex("</main>")
all_link_hub = (f'<a class="vol-all" href="all.html"><span>Prefer one long page? The syllabus and all {COUNT_WORD.lower()} volumes together, about {ALL_MB:.1f} MB.</span>'
                f'<b>Open the one-page edition &rarr;</b></a>')
hbody = hbody[:mi] + augment_syllabus_main(hbody[mi:me], lambda v: v["page"], all_link_hub) + hbody[me:]
hbody = hbody.replace('\n    <!-- ============ COMPANION VOLUMES ============ -->', RESUME_SECTION + '\n    <!-- ============ COMPANION VOLUMES ============ -->', 1)
assert 'id="resume"' in hbody
if EDITIONS:
    _vs = hbody.index('<section id="volumes">'); _ve = hbody.index('</section>', _vs) + len('</section>')
    hbody = hbody[:_ve] + "\n" + editions_html() + hbody[_ve:]
hub_js = controller(ns="", resetAsk="Click again to clear", spy="-10% 0px -75% 0px")
hub_doc = hhead + hbody.rstrip() + f"\n\n<script>{hub_js}</script>\n<script>{study_js(mode='hub', page='index.html')}</script>\n"
# The publisher serves the main page with a charset, but keep its markup ASCII so the
# file also renders correctly when opened directly. Raw-text elements must already be ASCII.
for _tag, _body in re.findall(r'<(style|script)\b[^>]*>(.*?)</\1>', hub_doc, re.S):
    assert _body.isascii(), "non-ASCII inside <" + _tag + ">"
(OUT / "index.html").write_text(hub_doc.encode("ascii", "xmlcharrefreplace").decode("ascii"), encoding="utf-8")
N_IDEA, N_EX = write_study_files(OUT)
if EDITIONS:
    (OUT / "editions").mkdir(exist_ok=True)
    for _, _, _, f in EDITIONS:
        shutil.copy2(ED / "pdf" / pathlib.Path(f["pdf"][0]).name, OUT / f["pdf"][0])
    print(f"editions: {len(EDITIONS)} books, {len(list((OUT / 'editions').iterdir()))} files")
print(f"study: {len(SEARCH_ROWS)} search entries, {N_IDEA} idea cards, {N_EX} exercise cards")
print("built:", ", ".join(sorted(p.name for p in OUT.glob("*.html"))))
STORAGE_NOTES = {
    "Your chapter marks are stored in this browser only. Nothing is sent anywhere.":
        "Your chapter marks are saved in this browser and, when you're signed in to Claude, in your account too, so they follow you to your other devices. Nobody else can see them.",
    "Your stage marks are stored in this browser only. Nothing is sent anywhere.":
        "Your stage marks are saved in this browser and, when you're signed in to Claude, in your account too, so they follow you to your other devices. Nobody else can see them.",
    "The marks are kept in this browser only.":
        "The marks are saved in this browser and, when you're signed in to Claude, in your account too.",
    "Your schedule is kept in this browser only.":
        "Your schedule is saved in this browser and, when you're signed in to Claude, in your account, so it follows you between devices.",
}
A11Y_CSS = (".skip-link{position:absolute;left:12px;top:-80px;z-index:200;padding:9px 14px;background:var(--ink);color:var(--paper);"
            "font-family:" + MONO.replace('"', "'") + ";font-size:13px;text-decoration:none}.skip-link:focus{top:12px}"
            ".lib-vols a{display:inline-flex;align-items:center;min-height:24px}"
            "[data-scroll-focus]:focus-visible{outline:2px solid var(--marine);outline-offset:2px}"
            ".track h3{font-size:18px;margin-bottom:4px}"
            ".rail-nav .sep{opacity:1}.rail-nav a{min-height:24px;box-sizing:border-box}main:focus{outline:none}")
VOL_NAME = {v["slug"]: v["name"] for v in VOLS}
def toggle_name(m):
    slug, ch, st = m.group(2), m.group(3), m.group(4)
    if st: label = f"Stage {st} done"
    else: label = (f"{VOL_NAME.get(slug, slug)}, chapter {int(ch)} read" if slug else f"Chapter {int(ch)} read")
    return m.group(1) + f' aria-label="{label}">'
def accessible(t, name):
    t = re.sub(r'(<input type="checkbox" data-id="(?:([a-z]+)-)?(?:ch(\d\d)|s(\d\d))")>', toggle_name, t)
    t = t.replace("<main>", '<main id="content" tabindex="-1">', 1)   # focusable, so the skip link moves focus too
    skip = f'<style>{A11Y_CSS}</style><a class="skip-link" href="#content">Skip to content</a>\n'
    k = t.find('<div class="shell">')
    t = t[:k] + skip + t[k:] if k >= 0 else t.replace('<main id="content"', skip + '<main id="content"', 1)
    if name in ("index.html", "all.html"):                       # both carry the syllabus's tracks
        t = re.sub(r'(<div class="track">\s*)<h4>(.*?)</h4>', r'\1<h3>\2</h3>', t, flags=re.S)
    return t
for p in sorted(OUT.glob("*.html")):
    t = p.read_text(encoding="utf-8")
    for a, b in STORAGE_NOTES.items(): t = t.replace(a, b)
    t = accessible(t, p.name)
    assert 'id="content"' in t and 'class="skip-link"' in t, p.name
    assert not any(a in t for a in STORAGE_NOTES), p.name
    p.write_text(t, encoding="utf-8")
for p in sorted(OUT.glob("*.html")): print(f"  {p.name:14} {p.stat().st_size:>10,} bytes")
