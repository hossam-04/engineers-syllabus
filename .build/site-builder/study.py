# Study tools: full-text search, continue reading, and flashcards. Runs inside build_site.py's
# namespace (VOLS, rd, MONO, DISPLAY, ...), like lib_merge.py.

SEARCH_ROWS = []   # [volume index or -1 for the syllabus, page, anchor, label, heading, text]
CARDS = []         # [id, slug, chapter, kind, front html, back html, anchor, title]
CHAPTERS = {}      # slug -> [[chapter number, title], ...]

BLOCK_TAG = r'</?(?:p|div|li|ul|ol|h\d|section|figure|figcaption|table|tr|td|th|thead|tbody|br|header|footer|details|blockquote|dl|dt|dd|label)\b[^>]*>'
def plain(h):
    h = re.sub(r'<(svg|pre|script|style)\b.*?</\1>', ' ', h, flags=re.S)
    h = re.sub(r'<summary>.*?</summary>', ' ', h, flags=re.S)
    h = re.sub(BLOCK_TAG, ' ', h)                     # blocks separate words; inline tags don't
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', h))).strip()

def slugify(h):
    s = re.sub(r'[^a-z0-9]+', '-', plain(h).lower()).strip('-')
    return s[:48].rstrip('-') or 'section'

def first_text(pattern, s):
    m = re.search(pattern, s, re.S)
    return plain(m.group(1)) if m else ""

def exercise_parts(ex):
    """Split one exercise div into (number, title, prompt html, solution html)."""
    num = first_text(r'<span class="ex-num">(.*?)</span>', ex)
    title = first_text(r'<span class="ex-title">(.*?)</span>', ex)
    head_end = ex.index('</div>', ex.index('<div class="ex-head">')) + len('</div>')
    det = ex.index('<details class="solution">')
    body = ex.index('<div class="sol-body">', det) + len('<div class="sol-body">')
    sol = ex[body:ex.rindex('</div></details>')]
    return num, title, ex[head_end:det].strip(), sol.strip()

def annotate_volume(body, vi, v):
    """Give every section heading and exercise in a volume page an id, add each chapter's
    flashcard link, and collect the volume's search rows and cards."""
    used = set(re.findall(r'\bid="([^"]+)"', body))
    def fresh(base):
        k, n = base, 2
        while k in used: k = f"{base}-{n}"; n += 1
        used.add(k); return k
    page = v["page"]; CHAPTERS[v["slug"]] = []
    for sec in re.findall(r'<section[^>]*\sid="([a-z]+)"[^>]*>(.*?)</section>', body, re.S):
        sid, inner = sec
        SEARCH_ROWS.append([vi, page, sid, "", first_text(r'<h2[^>]*>(.*?)</h2>', inner), plain(inner)])
    def chapter(m):
        open_tag, cid, inner = m.group(1), m.group(2), m.group(3)
        n = int(cid[2:])
        title = first_text(r'<h3>(.*?)</h3>', inner)
        label = f"Ch {n} \u00b7 {title}"
        CHAPTERS[v["slug"]].append([n, title])
        thesis_html = re.search(r'<p class="thesis">(.*?)</p>', inner, re.S).group(1)
        k = 0; first_card = len(CARDS)
        # split at each subsection heading and each end-of-chapter block
        cuts = [mm.start() for mm in re.finditer(r'<h4>|<div class="traps">|<div class="exercises">|<div class="ch-end">', inner)]
        first = cuts[0] if cuts else len(inner)
        lead = re.sub(r'<div class="ch-(?:top|meta)">.*?</div>|<h3>.*?</h3>', ' ', inner[:first], flags=re.S)
        SEARCH_ROWS.append([vi, page, cid, f"Ch {n}", title, plain(lead)])
        out = [inner[:first]]
        for a, b in zip(cuts, cuts[1:] + [len(inner)]):
            seg = inner[a:b]
            if seg.startswith('<h4>'):
                hd = re.match(r'<h4>(.*?)</h4>', seg, re.S).group(1)
                hid = fresh(f"{cid}-{slugify(hd)}")
                seg = f'<h4 id="{hid}">' + seg[4:]
                SEARCH_ROWS.append([vi, page, hid, label, plain(hd), plain(seg[seg.index('</h4>'):])])
            elif seg.startswith('<div class="traps">'):
                tid = fresh(f"{cid}-traps")
                seg = f'<div class="traps" id="{tid}">' + seg[len('<div class="traps">'):]
                SEARCH_ROWS.append([vi, page, tid, label, "Common traps", plain(seg)])
            elif seg.startswith('<div class="exercises">'):
                parts = re.split(r'(?=<div class="exercise">)', seg)
                for j, ex in enumerate(parts):
                    if not ex.startswith('<div class="exercise">'): continue
                    num, et, prompt, sol = exercise_parts(ex)
                    k += 1
                    eid = fresh(f"{cid}-ex{k}")
                    parts[j] = f'<div class="exercise" id="{eid}">' + ex[len('<div class="exercise">'):]
                    SEARCH_ROWS.append([vi, page, eid, label, f"{num} · {et}", plain(prompt) + " " + plain(sol)])
                    CARDS.append([f'{v["slug"]}-{n:02d}-ex{k}', v["slug"], n, "ex", prompt, sol, eid, f"{num} · {et}"])
                seg = "".join(parts)
            elif seg.startswith('<div class="ch-end">'):
                xid = fresh(f"{cid}-end")
                seg = f'<div class="ch-end" id="{xid}">' + seg[len('<div class="ch-end">'):]
                SEARCH_ROWS.append([vi, page, xid, label, "Checklist and further reading", plain(seg)])
            out.append(seg)
        CARDS.insert(first_card, [f'{v["slug"]}-{n:02d}-idea', v["slug"], n, "idea",
                      f'<p class="fc-ask">What is the central idea of <b>{H.escape(title)}</b>?</p>',
                      f'<p>{thesis_html.strip()}</p>', cid, "The central idea"])
        inner = "".join(out)
        cards_here = k + 1
        inner = re.sub(r'(<div class="ch-meta">.*?)(</div>)',
                       lambda mm: mm.group(1) + f'<a class="ch-cards" href="review.html#{v["slug"]}-{n:02d}">'
                                  f'{cards_here} flashcards</a>' + mm.group(2), inner, count=1, flags=re.S)
        return open_tag + inner + '</section>'
    body, nch = re.subn(r'(<section class="chapter[^"]*" id="(ch\d\d)"[^>]*>)(.*?)</section>', chapter, body, flags=re.S)
    assert nch == v["n"], (v["src"], nch)
    return body

def index_syllabus(main_html):
    for sid, inner in re.findall(r'<section class="stage" id="(s\d\d)"[^>]*>(.*?)</section>', main_html, re.S):
        SEARCH_ROWS.append([-1, "index.html", sid, f"Stage {sid[1:]}", first_text(r'<h3>(.*?)</h3>', inner), plain(inner)])
    for sid, inner in re.findall(r'<section id="([a-z]+)"[^>]*>(.*?)</section>', main_html, re.S):
        SEARCH_ROWS.append([-1, "index.html", sid, "", first_text(r'<h2[^>]*>(.*?)</h2>', inner), plain(inner)])

STUDY_VOLS = [{"slug": v["slug"], "name": v["name"], "page": v["page"], "stage": v["stage"],
               "title": H.unescape(v["title"])} for v in VOLS]

def libstudy():
    return ('    <div class="lib-study">\n'
            '      <button class="lib-search" type="button" data-search-open><span>Search the syllabus</span><kbd>/</kbd></button>\n'
            '      <a class="lib-cards" href="review.html">Flashcards</a>\n'
            '    </div>\n')

RESUME_SECTION = ('\n    <section id="resume" class="resume" hidden aria-label="Continue reading"></section>\n')

STUDY_CSS = f"""
/* ===== study tools: search, continue reading, flashcards ===== */
.lib-dl {{ display: flex; align-items: baseline; gap: 10px; margin-top: 8px; font-family: {MONO}; font-size: 11px; color: var(--ink-soft); }}
.lib-dl span {{ letter-spacing: .1em; text-transform: uppercase; font-size: 10px; }}
.lib-dl a, table.eds a {{ color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--rule); font-family: {MONO}; font-size: 12px; font-weight: 600; letter-spacing: .04em; }}
.lib-dl a:hover, table.eds a:hover {{ color: var(--marine); border-bottom-color: var(--marine); }}
a[data-dl].busy {{ opacity: .5; cursor: progress; }}
table.eds {{ min-width: 0; }}
table.eds td:first-child .n {{ display: inline-block; min-width: 2.4em; font-family: {MONO}; font-size: 11.5px; color: var(--brass); }}
table.eds .sz {{ font-family: {MONO}; font-size: 11px; color: var(--ink-soft); margin-left: 6px; }}
table.eds tr.all td {{ font-weight: 600; border-top: 1px solid var(--rule); }}
.sync-note {{ margin: 8px 0 0; font-family: {MONO}; font-size: 10.5px; letter-spacing: .02em; color: var(--ink-soft); }}
.lib-study {{ display: flex; gap: 6px; align-items: stretch; }}
.lib-search {{ flex: 1; display: flex; justify-content: space-between; align-items: center; gap: 8px; min-width: 0;
  font: inherit; font-size: 11.5px; color: var(--ink-soft); background: var(--surface); border: 1px solid var(--rule);
  padding: 6px 9px; cursor: pointer; text-align: left; }}
.lib-search:hover {{ border-color: var(--marine); color: var(--ink); }}
.lib-search kbd, .sr-keys kbd {{ font: inherit; font-size: 10px; border: 1px solid var(--rule); padding: 0 5px; color: var(--ink-soft); background: var(--paper); }}
.lib-cards {{ display: flex; align-items: center; font-size: 11.5px; padding: 6px 9px; border: 1px solid var(--rule);
  color: var(--ink-soft); text-decoration: none; }}
.lib-cards:hover, .lib-cards[aria-current="page"] {{ border-color: var(--marine); color: var(--ink); }}
.ch-meta .ch-cards {{ color: var(--marine); text-decoration: none; border-bottom: 1px solid transparent; }}
.ch-meta .ch-cards:hover {{ border-bottom-color: var(--marine); }}

.sr-overlay {{ position: fixed; inset: 0; z-index: 50; background: rgba(10, 12, 16, .45); display: flex;
  justify-content: center; align-items: flex-start; padding: 7vh 16px 16px; }}
.sr-panel {{ width: 100%; max-width: 720px; max-height: 84vh; display: flex; flex-direction: column;
  background: var(--paper); border: 1px solid var(--rule); box-shadow: 0 18px 50px rgba(0, 0, 0, .28); }}
.sr-top {{ display: flex; gap: 10px; align-items: center; padding: 12px 14px; border-bottom: 1px solid var(--rule); }}
.sr-input {{ flex: 1; min-width: 0; font-family: {MONO}; font-size: 16px; color: var(--ink); background: transparent;
  border: 0; outline: 0; padding: 4px 0; }}
.sr-close {{ font-family: {MONO}; font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--ink-soft);
  background: transparent; border: 1px solid var(--rule); padding: 4px 8px; cursor: pointer; }}
.sr-opts {{ display: flex; flex-wrap: wrap; gap: 6px 16px; justify-content: space-between; padding: 8px 14px;
  font-family: {MONO}; font-size: 11px; color: var(--ink-soft); border-bottom: 1px solid var(--rule-soft); }}
.sr-opts label {{ display: flex; gap: 6px; align-items: center; cursor: pointer; }}
.sr-keys {{ display: flex; gap: 10px; }}
.sr-list {{ list-style: none; margin: 0; padding: 0; overflow-y: auto; }}
.sr-item {{ display: flex; flex-direction: column; gap: 3px; padding: 11px 14px; color: var(--ink); text-decoration: none;
  border-bottom: 1px solid var(--rule-soft); }}
.sr-item[aria-selected="true"], .sr-item:hover {{ background: var(--surface); }}
.sr-item[aria-selected="true"] {{ box-shadow: inset 3px 0 0 var(--marine); }}
.sr-where {{ font-family: {MONO}; font-size: 10.5px; letter-spacing: .08em; text-transform: uppercase; color: var(--ink-soft); }}
.sr-where b {{ color: var(--brass); font-weight: 600; }}
.sr-title {{ font-family: {DISPLAY}; font-weight: 600; font-size: 16px; line-height: 1.3; }}
.sr-snip {{ font-size: 14.5px; line-height: 1.5; color: var(--ink-mid); }}
.sr-item mark {{ background: var(--marine-sunk); color: inherit; padding: 0 1px; }}
.sr-status {{ padding: 16px 14px; font-family: {MONO}; font-size: 12px; color: var(--ink-soft); }}

.resume-bar {{ position: fixed; z-index: 40; left: 50%; bottom: 16px; transform: translateX(-50%);
  width: max-content; max-width: calc(100% - 32px); display: flex; align-items: center; gap: 12px;
  padding: 10px 12px 10px 16px; background: var(--paper); border: 1px solid var(--rule); border-left: 3px solid var(--marine);
  box-shadow: 0 10px 30px rgba(0, 0, 0, .18); font-family: {MONO}; font-size: 12px; color: var(--ink-mid); }}
.resume-bar .rb-text {{ min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.resume-bar .rb-text b {{ color: var(--ink); font-weight: 600; }}
.resume-bar button {{ font: inherit; font-size: 11px; letter-spacing: .06em; text-transform: uppercase; cursor: pointer;
  padding: 5px 10px; border: 1px solid var(--rule); background: transparent; color: var(--ink-soft); flex: none; }}
.resume-bar .rb-go {{ background: var(--marine); border-color: var(--marine); color: var(--paper); }}

.resume {{ margin: 40px 0 0; }}
.resume-main {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 6px 22px; align-items: center; max-width: 62ch;
  padding: 16px 18px; background: var(--surface); border-left: 3px solid var(--marine); color: var(--ink); text-decoration: none; }}
.resume-main:hover .rs-t {{ color: var(--marine); }}
.rs-k {{ font-family: {MONO}; font-size: 10px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--marine); }}
.rs-t {{ font-family: {DISPLAY}; font-weight: 700; font-size: 19px; line-height: 1.25; }}
.rs-m {{ font-family: {MONO}; font-size: 11.5px; color: var(--ink-soft); }}
.rs-go {{ font-family: {MONO}; font-size: 11.5px; font-weight: 600; color: var(--ink); white-space: nowrap; }}
.resume-more {{ display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 10px; font-family: {MONO}; font-size: 11.5px; color: var(--ink-soft); }}
.resume-more a {{ color: var(--ink-mid); text-decoration: none; border-bottom: 1px solid var(--rule); }}
.resume-more a:hover {{ color: var(--marine); border-bottom-color: var(--marine); }}
@media (max-width: 640px) {{ .resume-main {{ grid-template-columns: minmax(0, 1fr); }} .sr-keys {{ display: none; }} }}
"""

REVIEW_CSS = f"""
/* ===== flashcards page ===== */
.rv-stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px; margin: 28px 0 0; max-width: 720px;
  background: var(--rule); border: 1px solid var(--rule); }}
.rv-stats div {{ display: flex; flex-direction: column; gap: 2px; padding: 12px 14px; background: var(--surface); }}
.rv-stats .k {{ font-family: {MONO}; font-size: 10px; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-soft); }}
.rv-stats b {{ font-family: {DISPLAY}; font-size: 24px; font-weight: 700; line-height: 1.1; font-variant-numeric: tabular-nums; }}
.rv-bar {{ display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; justify-content: space-between; max-width: 720px;
  margin: 22px 0 12px; font-family: {MONO}; font-size: 12px; color: var(--ink-soft); }}
.rv-bar select {{ font: inherit; color: var(--ink); background: var(--surface); border: 1px solid var(--rule); padding: 5px 8px; }}
.rv-mode {{ max-width: 720px; margin: 0 0 12px; padding: 10px 14px; background: var(--marine-sunk); font-family: {MONO};
  font-size: 12px; color: var(--ink); display: flex; gap: 12px; justify-content: space-between; flex-wrap: wrap; }}
.rv-mode a {{ color: var(--marine); }}
.fc {{ max-width: 720px; background: var(--surface); border: 1px solid var(--rule); }}
.fc-meta {{ display: flex; flex-wrap: wrap; gap: 4px 14px; justify-content: space-between; padding: 10px 18px;
  border-bottom: 1px solid var(--rule-soft); font-family: {MONO}; font-size: 11px; color: var(--ink-soft); }}
.fc-meta b {{ color: var(--brass); font-weight: 600; }}
.fc-meta a {{ color: var(--ink-soft); }}
.fc-body {{ padding: 6px 22px 18px; }}
.fc-title {{ font-family: {DISPLAY}; font-weight: 700; font-size: 20px; line-height: 1.25; margin: 14px 0 4px; }}
.fc-ask {{ font-size: 19px; }}
.fc-back {{ margin-top: 16px; padding: 4px 0 0 16px; border-left: 2px solid var(--ok); }}
.fc-body pre {{ overflow-x: auto; }}
.fc-actions {{ display: flex; flex-wrap: wrap; gap: 8px; padding: 14px 18px; border-top: 1px solid var(--rule-soft); }}
.fc-btn {{ font-family: {MONO}; font-size: 12px; letter-spacing: .04em; cursor: pointer; padding: 9px 14px; min-width: 7.5em;
  display: flex; flex-direction: column; align-items: flex-start; gap: 1px; color: var(--ink); background: var(--paper);
  border: 1px solid var(--rule); }}
.fc-btn small {{ font-size: 10.5px; color: var(--ink-soft); }}
.fc-btn:hover {{ border-color: var(--marine); }}
.fc-btn.primary {{ background: var(--marine); border-color: var(--marine); color: var(--paper); }}
.fc-btn.primary small {{ color: var(--paper); opacity: .8; }}
.fc-btn.again {{ border-color: var(--gap); }}
.fc-btn:focus-visible {{ outline: 2px solid var(--marine); outline-offset: 2px; }}
.fc-empty {{ max-width: 720px; padding: 22px; background: var(--surface); border: 1px solid var(--rule); }}
.fc-empty p {{ margin: 0 0 10px; }}
.rv-deck {{ max-width: 860px; }}
.rv-deck details {{ border-bottom: 1px solid var(--rule); }}
.rv-deck summary {{ display: flex; gap: 12px; justify-content: space-between; align-items: baseline; padding: 12px 6px; cursor: pointer;
  font-family: {MONO}; font-size: 12px; color: var(--ink-soft); }}
.rv-deck summary b {{ font-family: {DISPLAY}; font-size: 16px; color: var(--ink); font-weight: 600; }}
.rv-deck summary .n {{ color: var(--brass); margin-right: 8px; }}
.rv-ch {{ display: grid; grid-template-columns: 34px minmax(0, 1fr) auto auto; gap: 4px 14px; align-items: center;
  padding: 7px 6px; border-top: 1px solid var(--rule-soft); font-family: {MONO}; font-size: 11.5px; color: var(--ink-soft); }}
.rv-ch .t {{ font-family: "Source Serif 4", Georgia, serif; font-size: 15px; color: var(--ink); }}
.rv-ch .st {{ font-variant-numeric: tabular-nums; white-space: nowrap; }}
.rv-ch .acts {{ display: flex; gap: 6px; }}
.rv-ch .acts a, .rv-ch .acts button {{ font: inherit; font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase; cursor: pointer;
  padding: 3px 8px; border: 1px solid var(--rule); background: transparent; color: var(--ink-soft); text-decoration: none; white-space: nowrap; }}
.rv-ch .acts a:hover, .rv-ch .acts button:hover {{ border-color: var(--marine); color: var(--ink); }}
.rv-ch.in .t::after {{ content: " \\2022"; color: var(--ok); }}
@media (max-width: 640px) {{
  .rv-stats {{ grid-template-columns: minmax(0, 1fr); }}
  .rv-ch {{ grid-template-columns: 28px minmax(0, 1fr); }}
  .rv-ch .st, .rv-ch .acts {{ grid-column: 2; }}
  .fc-body {{ padding: 4px 16px 16px; }}
}}
"""

STUDY_JS = r"""
(function () {
  var CFG = __CFG__;
  var LS = "englibrary.v1.", VOLS = CFG.vols, bySlug = {};
  VOLS.forEach(function (v, i) { v.i = i; bySlug[v.slug] = v; });
  function read(k) { try { return window.localStorage.getItem(LS + k); } catch (e) { return null; } }
  function write(k, v) { try { window.localStorage.setItem(LS + k, v); } catch (e) { /* storage unavailable */ } }
  function readJSON(k, d) { try { var v = JSON.parse(read(k)); return v == null ? d : v; } catch (e) { return d; } }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function ago(t) {
    var m = Math.round((Date.now() - t) / 60000);
    if (m < 2) return "just now";
    if (m < 60) return m + " minutes ago";
    var h = Math.round(m / 60); if (h < 24) return h + (h === 1 ? " hour ago" : " hours ago");
    var d = Math.round(h / 24); return d + (d === 1 ? " day ago" : " days ago");
  }

  // The pages scroll smoothly, which is pleasant for a short hop but never arrives across a
  // whole volume, so a programmatic jump turns it off for the moment it takes.
  function jump(id) {
    var el = document.getElementById(id); if (!el) return false;
    var root = document.documentElement, prev = root.style.scrollBehavior;
    if (location.hash !== "#" + id) history.pushState(null, "", "#" + id);
    root.style.scrollBehavior = "auto"; el.scrollIntoView(); window.scrollBy(0, -16);
    root.style.scrollBehavior = prev;
    return true;
  }

  // ---------- search ----------
  var ov = null, input, list, status, only, rows = null, loading = false, hits = [], sel = 0, timer = null;
  function buildOverlay() {
    if (ov) return;
    ov = document.createElement("div");
    ov.className = "sr-overlay"; ov.hidden = true;
    ov.innerHTML =
      '<div class="sr-panel" role="dialog" aria-modal="true" aria-label="Search the syllabus">' +
      '<div class="sr-top"><input class="sr-input" type="search" placeholder="Search every volume" aria-label="Search" autocomplete="off" spellcheck="false">' +
      '<button class="sr-close" type="button">Esc</button></div>' +
      '<div class="sr-opts">' + (CFG.slug ? '<label><input type="checkbox" class="sr-only"> Only ' + esc(bySlug[CFG.slug].name) + '</label>' : '<span>All volumes and the syllabus</span>') +
      '<span class="sr-keys"><span><kbd>&uarr;</kbd> <kbd>&darr;</kbd> to move</span><span><kbd>Enter</kbd> to open</span></span></div>' +
      '<div class="sr-status" aria-live="polite"></div><ul class="sr-list" role="listbox"></ul></div>';
    document.body.appendChild(ov);
    input = ov.querySelector(".sr-input"); list = ov.querySelector(".sr-list");
    status = ov.querySelector(".sr-status"); only = ov.querySelector(".sr-only");
    ov.addEventListener("click", function (e) { if (e.target === ov) closeSearch(); });
    ov.addEventListener("keydown", function (e) {
      if (e.key !== "Tab") return;
      var f = Array.prototype.filter.call(ov.querySelectorAll("input, button, a[href]"), function (x) { return x.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    ov.querySelector(".sr-close").addEventListener("click", closeSearch);
    input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(run, 90); });
    if (only) only.addEventListener("change", run);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!hits.length) return;
        sel = (sel + (e.key === "ArrowDown" ? 1 : hits.length - 1)) % hits.length; mark();
      } else if (e.key === "Enter") {
        var a = list.querySelector('[aria-selected="true"]');
        if (a) { e.preventDefault(); go(a); }
      }
    });
    list.addEventListener("click", function (e) {
      var a = e.target.closest("a"); if (!a) return;
      e.preventDefault(); go(a);
    });
  }
  function go(a) {
    closeSearch();
    var href = a.getAttribute("href"), hash = href.slice(href.indexOf("#"));
    if (href.split("#")[0] === CFG.page && jump(hash.slice(1))) return;
    location.href = href;
  }
  var opener = null;
  function openSearch() {
    if (ov && !ov.hidden) return;
    opener = document.activeElement;
    buildOverlay(); ov.hidden = false; document.documentElement.style.overflow = "hidden";
    input.focus(); input.select(); load(); run();
  }
  function closeSearch() {
    if (!ov || ov.hidden) return;
    ov.hidden = true; document.documentElement.style.overflow = "";
    if (opener && opener.focus && document.contains(opener)) opener.focus();   // back to where the reader was
    opener = null;
  }
  function load() {
    if (rows || loading) return;
    loading = true; status.textContent = "Loading the index\u2026";
    var s = document.createElement("script");
    s.src = "search-index.js";
    s.onload = function () {
      rows = (window.ENG_SEARCH || []).map(function (r) {
        return { r: r, t: r[4].toLowerCase(), x: r[5].toLowerCase(), l: r[3].toLowerCase() };
      });
      loading = false; run();
    };
    s.onerror = function () { loading = false; status.textContent = "The search index could not be loaded. Try again in a moment."; };
    document.head.appendChild(s);
  }
  function count(hay, term, cap) {
    var n = 0, i = hay.indexOf(term);
    while (i >= 0 && n < cap) { n++; i = hay.indexOf(term, i + term.length); }
    return n;
  }
  // 2 = the term stands as a whole word somewhere, 1 = it starts a word, 0 = only inside words
  function wordAt(hay, term) {
    var i = hay.indexOf(term), best = 0;
    while (i >= 0) {
      if (i === 0 || /[^a-z0-9]/.test(hay.charAt(i - 1))) {
        var after = hay.charAt(i + term.length);
        if (!after || /[^a-z0-9]/.test(after)) return 2;
        best = 1;
      }
      i = hay.indexOf(term, i + 1);
    }
    return best;
  }
  function run() {
    if (!ov || ov.hidden) return;
    var q = input.value.trim().toLowerCase();
    if (!rows) { list.innerHTML = ""; return; }
    var terms = q.split(/\s+/).filter(function (t) { return t.length > 0; });
    if (!terms.length || q.length < 2) {
      hits = []; list.innerHTML = "";
      status.textContent = "Type a word or phrase. Every chapter, exercise and solution is searched.";
      return;
    }
    var mine = only && only.checked ? bySlug[CFG.slug].i : null, scored = [];
    for (var i = 0; i < rows.length; i++) {
      var e = rows[i], score = 0, ok = true;
      if (mine !== null && e.r[0] !== mine) continue;
      for (var j = 0; j < terms.length; j++) {
        var t = terms[j], n = count(e.x, t, 6), wt = e.t.indexOf(t) >= 0 ? wordAt(e.t, t) + 1 : 0;
        var wx = n ? wordAt(e.x, t) : 0, wl = e.l.indexOf(t) >= 0 ? wordAt(e.l, t) : 0;
        if (!wt && !n && !wl) { ok = false; break; }
        if (t.length <= 2 && wt < 3 && wx < 2 && wl < 2) { ok = false; break; }   // short words must stand alone
        score += [0, 4, 9, 16][wt] + (n ? 2 + n : 0) + [0, 1, 3][wx] + [0, 2, 5][wl];
      }
      if (!ok) continue;
      if (terms.length > 1) { if (e.t.indexOf(q) >= 0) score += 24; else if (e.x.indexOf(q) >= 0) score += 10; }
      if (CFG.slug && e.r[0] === bySlug[CFG.slug].i) score += 2;
      scored.push([score, i]);
    }
    scored.sort(function (a, b) { return b[0] - a[0] || a[1] - b[1]; });
    var total = scored.length;
    hits = scored.slice(0, 40).map(function (s) { return rows[s[1]]; });
    sel = 0;
    status.textContent = total ? (total > 40 ? "Best 40 of " + total + " matches" : total + (total === 1 ? " match" : " matches"))
                               : "Nothing matches every word. Try fewer or shorter words.";
    list.innerHTML = hits.map(function (e, k) {
      var r = e.r, v = r[0] >= 0 ? VOLS[r[0]] : null;
      var where = v ? "<b>" + esc(v.stage) + "</b> " + esc(v.name) + (r[3] ? " &middot; " + esc(r[3]) : "")
                    : "<b>Syllabus</b>" + (r[3] ? " &middot; " + esc(r[3]) : "");
      return '<li><a class="sr-item" role="option" id="sr-' + k + '" href="' + esc(r[1] + "#" + r[2]) + '">' +
        '<span class="sr-where">' + where + '</span><span class="sr-title">' + hl(r[4], terms) + '</span>' +
        '<span class="sr-snip">' + snippet(r[5], e.x, terms) + '</span></a></li>';
    }).join("");
    mark();
  }
  function mark() {
    Array.prototype.forEach.call(list.querySelectorAll(".sr-item"), function (a, k) {
      a.setAttribute("aria-selected", k === sel ? "true" : "false");
      if (k === sel) { input.setAttribute("aria-activedescendant", a.id); a.scrollIntoView({ block: "nearest" }); }
    });
  }
  function hl(text, terms) {
    var low = text.toLowerCase(), out = "", i = 0;
    while (i < text.length) {
      var best = -1, len = 0;
      for (var j = 0; j < terms.length; j++) {
        var p = low.indexOf(terms[j], i);
        if (p >= 0 && (best < 0 || p < best || (p === best && terms[j].length > len))) { best = p; len = terms[j].length; }
      }
      if (best < 0) { out += esc(text.slice(i)); break; }
      out += esc(text.slice(i, best)) + "<mark>" + esc(text.slice(best, best + len)) + "</mark>";
      i = best + len;
    }
    return out;
  }
  function snippet(text, low, terms) {
    var at = -1;
    terms.forEach(function (t) { var p = low.indexOf(t); if (p >= 0 && (at < 0 || p < at)) at = p; });
    if (at < 0) at = 0;
    var a = Math.max(0, at - 70), b = Math.min(text.length, at + 170);
    if (a > 0) { var sp = text.indexOf(" ", a); if (sp > 0 && sp < at) a = sp + 1; }
    if (b < text.length) { var sb = text.lastIndexOf(" ", b); if (sb > at) b = sb; }
    return (a > 0 ? "&hellip; " : "") + hl(text.slice(a, b), terms) + (b < text.length ? " &hellip;" : "");
  }
  Array.prototype.forEach.call(document.querySelectorAll("[data-search-open]"), function (b) {
    b.addEventListener("click", openSearch);
  });
  document.addEventListener("keydown", function (e) {
    var tag = (e.target && e.target.tagName) || "";
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(tag) || (e.target && e.target.isContentEditable);
    if (e.key === "Escape" && ov && !ov.hidden) { e.preventDefault(); closeSearch(); return; }
    if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) { e.preventDefault(); openSearch(); return; }
    if (e.key === "/" && !typing && !e.metaKey && !e.ctrlKey && !e.altKey) { e.preventDefault(); openSearch(); }
  });

  // ---------- continue reading: a volume remembers where you were ----------
  if (CFG.mode === "vol") {
    var marks = Array.prototype.slice.call(document.querySelectorAll(
      "main > section[id], main section.chapter, main section.chapter h4[id]"));
    var label = function (el) {
      var ch = el.closest("section.chapter");
      if (!ch) { var h2 = el.querySelector("h2"); return h2 ? h2.textContent : ""; }
      var base = "Ch " + parseInt(ch.getAttribute("data-ch") || ch.id.slice(2), 10) + " \u00b7 " + ch.querySelector("h3").textContent;
      return el.tagName === "H4" ? base + " \u203a " + el.textContent : base;
    };
    var saved = readJSON("pos." + CFG.slug, null), last = null, pending = null;
    var current = function () {
      var line = window.innerHeight * 0.3, cur = null;
      for (var i = 0; i < marks.length; i++) { if (marks[i].getBoundingClientRect().top <= line) cur = marks[i]; else if (cur) break; }
      return cur;
    };
    var save = function () {
      pending = null;
      var el = current(); if (!el || el.id === last) return;
      last = el.id;
      write("pos." + CFG.slug, JSON.stringify({ a: el.id, l: label(el), t: Date.now() }));
      var rec = readJSON("recent", []).filter(function (s) { return s !== CFG.slug && bySlug[s]; });
      rec.unshift(CFG.slug); write("recent", JSON.stringify(rec.slice(0, 16)));
    };
    var bar = null, startY = window.scrollY;
    var hideBar = function () { if (bar) { bar.remove(); bar = null; } };
    window.addEventListener("scroll", function () {
      if (!pending) pending = setTimeout(save, 600);
      if (bar && Math.abs(window.scrollY - startY) > window.innerHeight * 1.5) hideBar();
    }, { passive: true });
    var flush = function () { if (pending) { clearTimeout(pending); save(); } };
    window.addEventListener("pagehide", flush);
    document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") flush(); });
    var target = saved && saved.a !== "start" ? document.getElementById(saved.a) : null;
    if (!location.hash && target) {
      bar = document.createElement("div");
      bar.className = "resume-bar"; bar.setAttribute("role", "region"); bar.setAttribute("aria-label", "Continue reading");
      bar.innerHTML = '<span class="rb-text">Continue at <b>' + esc(saved.l) + '</b></span>' +
        '<button class="rb-go" type="button">Resume</button><button class="rb-x" type="button" aria-label="Dismiss">&times;</button>';
      document.body.appendChild(bar);
      bar.querySelector(".rb-go").addEventListener("click", function () {
        hideBar(); last = null; jump(saved.a);
      });
      bar.querySelector(".rb-x").addEventListener("click", hideBar);
    }
  }

  // ---------- continue reading: the hub shows the latest places ----------
  if (CFG.mode === "hub") {
    var showResume = function () {
    var box = document.getElementById("resume");
    var places = readJSON("recent", []).map(function (s) {
      var p = readJSON("pos." + s, null); return p && bySlug[s] ? { v: bySlug[s], p: p } : null;
    }).filter(Boolean);
    if (box && places.length) {
      var top = places[0];
      var html = '<a class="resume-main" href="' + esc(top.v.page + "#" + top.p.a) + '">' +
        '<span><span class="rs-k">Continue reading</span><br><span class="rs-t">' + esc(top.v.title) + '</span><br>' +
        '<span class="rs-m">' + esc(top.p.l) + ' &middot; ' + esc(ago(top.p.t)) + '</span></span>' +
        '<span class="rs-go">Resume &rarr;</span></a>';
      if (places.length > 1) html += '<div class="resume-more"><span>Also open:</span>' + places.slice(1, 5).map(function (x) {
        return '<a href="' + esc(x.v.page + "#" + x.p.a) + '" title="' + esc(x.p.l) + '">' + esc(x.v.stage + " " + x.v.name) + '</a>';
      }).join("") + '</div>';
      box.innerHTML = html; box.hidden = false;
    }
    };
    showResume();
    window.addEventListener("englibrary:sync", showResume);
  }
})();
"""

REVIEW_JS = r"""
(function () {
  var DATA = window.ENG_CARDS, LS = "englibrary.v1.";
  var root = document.getElementById("review");
  if (!DATA || !root) { if (root) root.innerHTML = '<div class="fc-empty"><p>The flashcards could not be loaded. Reload the page to try again.</p></div>'; return; }
  function read(k) { try { return window.localStorage.getItem(LS + k); } catch (e) { return null; } }
  function write(k, v) { try { window.localStorage.setItem(LS + k, v); } catch (e) { /* storage unavailable */ } }
  function readJSON(k, d) { try { var v = JSON.parse(read(k)); return v == null ? d : v; } catch (e) { return d; } }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function pad(n) { return (n < 10 ? "0" : "") + n; }

  // Leitner boxes: a card moves up a box each time you know it, back to the first when you don't.
  var DAYS = [0, 1, 3, 7, 16, 35, 80], NEW_PER_DAY = 20;
  function today() { var d = new Date(); return Math.floor((d.getTime() - d.getTimezoneOffset() * 60000) / 864e5); }
  var vols = DATA.vols, bySlug = {}, cards = DATA.cards.map(function (c) {
    return { id: c[0], slug: c[1], ch: c[2], kind: c[3], front: c[4], back: c[5], anchor: c[6], title: c[7] };
  });
  vols.forEach(function (v) { bySlug[v.slug] = v; v.titles = {}; v.chapters.forEach(function (c) { v.titles[c[0]] = c[1]; }); });
  var state = readJSON("srs", {}), added = readJSON("srs-added", {});
  function chKey(slug, ch) { return slug + "-" + pad(ch); }
  function isRead(slug, ch) { return read(slug + "-ch" + pad(ch)) === "1"; }
  function inDeck(slug, ch) { return isRead(slug, ch) || added[chKey(slug, ch)] === 1; }
  function newToday() { var d = readJSON("srs-day", null); return d && d.d === today() ? d.n : 0; }
  function bumpNew() { write("srs-day", JSON.stringify({ d: today(), n: newToday() + 1 })); }
  function saveState() { write("srs", JSON.stringify(state)); }

  var filter = read("srs-filter") || "", queue = [], cur = null, shown = false, mode = null, done = 0;
  var el = {
    stats: document.getElementById("rv-stats"), filter: document.getElementById("rv-filter"),
    modebar: document.getElementById("rv-mode"), card: document.getElementById("rv-card"), deck: document.getElementById("rv-deck")
  };
  el.filter.innerHTML = '<option value="">All volumes</option>' + vols.map(function (v) {
    return '<option value="' + v.slug + '">' + esc(v.stage + " \u00b7 " + v.name) + '</option>';
  }).join("");
  if (!bySlug[filter]) filter = "";
  el.filter.value = filter;
  el.filter.addEventListener("change", function () { filter = el.filter.value; write("srs-filter", filter); mode = null; start(); });

  function pool() { return cards.filter(function (c) { return (!filter || c.slug === filter) && inDeck(c.slug, c.ch); }); }
  function counts() {
    var t = today(), due = 0, fresh = 0, learnt = 0;
    pool().forEach(function (c) { var s = state[c.id]; if (!s) fresh++; else { learnt++; if (s[1] <= t) due++; } });
    return { due: due, fresh: fresh, learnt: learnt, newLeft: Math.max(0, NEW_PER_DAY - newToday()) };
  }
  function shuffle(a) { for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), x = a[i]; a[i] = a[j]; a[j] = x; } return a; }
  function start() {
    var t = today();
    if (mode) {
      queue = cards.filter(function (c) { return c.slug === mode.slug && c.ch === mode.ch; });
    } else {
      var p = pool();
      var due = shuffle(p.filter(function (c) { return state[c.id] && state[c.id][1] <= t; }))
        .sort(function (a, b) { return state[a.id][1] - state[b.id][1]; });
      var fresh = p.filter(function (c) { return !state[c.id]; }).slice(0, Math.max(0, NEW_PER_DAY - newToday()));
      queue = due.concat(fresh);
    }
    done = 0; next();
  }
  function next() { cur = queue.shift() || null; shown = false; render(); }
  function when(days) { return days <= 0 ? "again today" : days === 1 ? "tomorrow" : "in " + days + " days"; }
  function outcome(c, r) {
    var s = state[c.id], box = s ? s[0] : 0;
    if (r === 0) return 1;
    return Math.min(DAYS.length - 1, Math.max(1, box + r));
  }
  function rate(r) {
    if (!cur || !shown) return;
    var c = cur, wasNew = !state[c.id], box = outcome(c, r);
    state[c.id] = [box, today() + (r === 0 ? 0 : DAYS[box])];
    saveState();
    if (wasNew && !mode) bumpNew();
    if (r === 0 && !mode) queue.splice(Math.min(3, queue.length), 0, c);
    done++; next(); stats(); deck();
  }
  function stats() {
    var k = counts();
    el.stats.innerHTML = '<div><span class="k">Due now</span><b>' + k.due + '</b></div>' +
      '<div><span class="k">New today</span><b>' + Math.min(k.fresh, k.newLeft) + '</b></div>' +
      '<div><span class="k">Learnt</span><b>' + k.learnt + '</b></div>';
  }
  function cardMeta(c) {
    var v = bySlug[c.slug];
    return '<div class="fc-meta"><span><b>' + esc(v.stage) + '</b> ' + esc(v.name) + ' &middot; Ch ' + c.ch + ' &middot; ' +
      esc(v.titles[c.ch] || "") + '</span><a href="' + esc(v.page + "#" + c.anchor) + '">Open in the chapter &rarr;</a></div>';
  }
  function render() {
    if (mode) {
      var mv = bySlug[mode.slug];
      el.modebar.hidden = false;
      el.modebar.innerHTML = '<span>Studying Ch ' + mode.ch + ' &middot; ' + esc(mv.titles[mode.ch] || "") + ' (' + mv.name + ')</span>' +
        '<a href="#" data-leave>Back to daily review</a>';
    } else el.modebar.hidden = true;
    if (!cur) {
      var k = counts(), msg;
      if (mode) msg = '<p><b>Chapter done.</b> Its cards are now in your deck and come back on their schedule.</p>';
      else if (!k.learnt && !k.fresh) msg = '<p><b>Your deck is empty.</b> Cards join it when you mark a chapter <i>Read</i> in a volume, or when you add a chapter below.</p><p>Each chapter brings its central idea and every exercise, with the solution on the back.</p>';
      else if (k.fresh && !k.newLeft) msg = '<p><b>That\'s today\'s ' + NEW_PER_DAY + ' new cards.</b> New cards are rationed so reviews never pile up. Come back tomorrow, or study a chapter below.</p>';
      else msg = '<p><b>' + (done ? "Done for now." : "Nothing is due.") + '</b> ' + nextDue() + '</p>';
      el.card.innerHTML = '<div class="fc-empty">' + msg + '</div>';
      return;
    }
    var c = cur, head = c.kind === "idea" ? "The central idea" : c.title;
    var html = '<div class="fc">' + cardMeta(c) + '<div class="fc-body"><div class="fc-title">' + esc(head) + '</div>' + c.front;
    if (shown) html += '<div class="fc-back">' + c.back + '</div>';
    html += '</div><div class="fc-actions">';
    if (!shown) html += '<button class="fc-btn primary" type="button" data-show>Show answer<small>Space</small></button>';
    else {
      var opts = [[0, "Again", "again"], [1, "Good", ""], [2, "Easy", ""]];
      html += opts.map(function (o) {
        var b = outcome(c, o[0]), days = o[0] === 0 ? 0 : DAYS[b];
        return '<button class="fc-btn ' + o[2] + '" type="button" data-rate="' + o[0] + '">' + o[1] + '<small>' + (o[0] + 1) + ' &middot; ' + when(days) + '</small></button>';
      }).join("");
    }
    html += '</div></div>';
    el.card.innerHTML = html;
    if (window.hljs) Array.prototype.forEach.call(el.card.querySelectorAll("pre code"), function (b) {
      try { window.hljs.highlightElement(b); } catch (e) { /* plain code is fine */ }
    });
    // keep keyboard users on the card: focus its main button unless they are using a control elsewhere
    var btn = el.card.querySelector(shown ? "[data-rate='1']" : "[data-show]");
    var away = document.activeElement && document.activeElement !== document.body && !el.card.contains(document.activeElement);
    if (btn && !away) btn.focus({ preventScroll: true });
  }
  function nextDue() {
    var t = today(), soon = null;
    pool().forEach(function (c) { var s = state[c.id]; if (s && s[1] > t && (soon === null || s[1] < soon)) soon = s[1]; });
    return soon === null ? "Mark more chapters read, or study one below." : "The next cards are due " + when(soon - t) + ".";
  }
  el.card.addEventListener("click", function (e) {
    if (e.target.closest("[data-show]")) { shown = true; render(); }
    var r = e.target.closest("[data-rate]"); if (r) rate(parseInt(r.getAttribute("data-rate"), 10));
  });
  el.modebar.addEventListener("click", function (e) {
    if (e.target.closest("[data-leave]")) { e.preventDefault(); history.replaceState(null, "", location.pathname + location.search); mode = null; start(); }
  });
  document.addEventListener("keydown", function (e) {
    var tag = (e.target && e.target.tagName) || "";
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(tag) || e.metaKey || e.ctrlKey || e.altKey || !cur) return;
    if (document.querySelector(".sr-overlay:not([hidden])")) return;
    if (!shown && (e.key === " " || e.key === "Enter")) { e.preventDefault(); shown = true; render(); }
    else if (shown && (e.key === "1" || e.key === "2" || e.key === "3")) { e.preventDefault(); rate(parseInt(e.key, 10) - 1); }
  });

  function deck() {
    var t = today();
    var open = {}; Array.prototype.forEach.call(el.deck.querySelectorAll("details[open]"), function (d) { open[d.getAttribute("data-vol")] = 1; });
    el.deck.innerHTML = vols.map(function (v) {
      var tot = 0, inn = 0, rows = v.chapters.map(function (c) {
        var cs = cards.filter(function (x) { return x.slug === v.slug && x.ch === c[0]; });
        var learnt = 0, due = 0;
        cs.forEach(function (x) { var s = state[x.id]; if (s) { learnt++; if (s[1] <= t) due++; } });
        var rd = isRead(v.slug, c[0]), ad = added[chKey(v.slug, c[0])] === 1, here = rd || ad;
        tot += cs.length; if (here) inn += cs.length;
        var act = '<a href="#' + chKey(v.slug, c[0]) + '">Study</a>';
        if (!rd) act += '<button type="button" data-toggle="' + chKey(v.slug, c[0]) + '">' + (ad ? "Remove" : "Add") + '</button>';
        return '<div class="rv-ch' + (here ? " in" : "") + '"><span>' + pad(c[0]) + '</span><span class="t">' + esc(c[1]) + '</span>' +
          '<span class="st">' + learnt + ' / ' + cs.length + ' learnt' + (due ? ' &middot; ' + due + ' due' : '') + (rd ? ' &middot; read' : '') + '</span>' +
          '<span class="acts">' + act + '</span></div>';
      }).join("");
      return '<details data-vol="' + v.slug + '"' + (open[v.slug] ? " open" : "") + '><summary><span><span class="n">' + esc(v.stage) + '</span><b>' +
        esc(v.name) + '</b></span><span>' + inn + ' of ' + tot + ' cards in your deck</span></summary>' + rows + '</details>';
    }).join("");
  }
  el.deck.addEventListener("click", function (e) {
    var b = e.target.closest("[data-toggle]"); if (!b) return;
    var k = b.getAttribute("data-toggle");
    if (added[k] === 1) delete added[k]; else added[k] = 1;
    write("srs-added", JSON.stringify(added)); deck(); stats(); if (!cur && !mode) start();
  });

  var reset = document.getElementById("rv-reset");
  if (reset) {
    var label = reset.textContent, armed = null;
    reset.addEventListener("click", function () {
      if (!armed) { reset.textContent = "Click again to clear"; reset.classList.add("armed"); armed = setTimeout(function () { armed = null; reset.textContent = label; reset.classList.remove("armed"); }, 4000); return; }
      clearTimeout(armed); armed = null; reset.textContent = label; reset.classList.remove("armed");
      state = {}; added = {}; saveState(); write("srs-added", "{}"); write("srs-day", "null"); mode = null; start(); stats(); deck();
    });
  }
  function fromHash() {
    var m = /^#([a-z]+)-(\d\d)$/.exec(location.hash);
    mode = m && bySlug[m[1]] ? { slug: m[1], ch: parseInt(m[2], 10) } : null;
    if (mode && !isRead(mode.slug, mode.ch)) { added[chKey(mode.slug, mode.ch)] = 1; write("srs-added", JSON.stringify(added)); }
    start(); stats(); deck();
    if (mode) window.scrollTo(0, 0);
  }
  // Another device's reviews arrived: take the merged schedule, and refill the queue unless a card is open.
  window.addEventListener("englibrary:sync", function () {
    state = readJSON("srs", {}); added = readJSON("srs-added", {});
    if (!cur || !shown) start();
    stats(); deck();
  });
  window.addEventListener("hashchange", fromHash);
  window.addEventListener("storage", function (e) { if (e.key && e.key.indexOf(LS) === 0 && e.key.indexOf(LS + "srs") !== 0) { stats(); deck(); } });
  fromHash();
})();
"""

def study_js(**cfg):
    cfg.setdefault("vols", STUDY_VOLS)
    return STUDY_JS.replace("__CFG__", json.dumps(cfg))

def write_study_files(OUT):
    """search-index.js and cards.js, loaded by the pages; review.html, the flashcards page."""
    (OUT / "search-index.js").write_text("window.ENG_SEARCH=" + json.dumps(SEARCH_ROWS, separators=(",", ":")) + ";\n", encoding="utf-8")
    vols = [{"slug": v["slug"], "name": v["name"], "stage": v["stage"], "page": v["page"], "chapters": CHAPTERS[v["slug"]]} for v in VOLS]
    (OUT / "cards.js").write_text("window.ENG_CARDS=" + json.dumps({"vols": vols, "cards": CARDS}, separators=(",", ":")) + ";\n", encoding="utf-8")
    head, _, srcs = split_page(rd("tools-handbook"))
    head = re.sub(r'<title>.*?</title>', "<title>Flashcards</title>", head, count=1, flags=re.S)
    head = re.sub(r'<meta name="description"[^>]*>', '<meta name="description" content="Spaced-repetition flashcards for The Engineer\'s Syllabus.">', head, count=1)
    head += f"\n<style>{BASE_CSS}{LIB_CSS}{STUDY_CSS}{REVIEW_CSS}</style>"
    n_ex = sum(1 for c in CARDS if c[3] == "ex"); n_idea = len(CARDS) - n_ex
    body = f'''<div class="shell">
  <aside class="rail">
{libnav()}{libstudy().replace('href="review.html"', 'href="review.html" aria-current="page"')}    <div class="rail-head">Flashcards</div>
    <div class="progress-box">
      <div class="progress-row"><span>Chapters read</span><b id="pct">0 / {TOTAL}</b></div>
      <div class="bar"><span id="barfill"></span></div>
    </div>
    <div class="rail-tools">
      <button class="tool-btn" id="themebtn" type="button">Theme</button>
      <button class="tool-btn" id="rv-reset" type="button">Reset schedule</button>
    </div>
  </aside>
  <main>
    <header class="masthead">
      <span class="eyebrow">Study tools &middot; The Engineer's Syllabus</span>
      <h1>Flashcards</h1>
      <p class="standfirst">Recall beats rereading. Every chapter in the {COUNT_WORD.lower()} volumes has cards: its central idea, and each of its exercises with the solution on the back, {len(CARDS):,} cards in all. A chapter's cards join your deck when you mark it read. Say how well you knew each answer and the card comes back just before you would forget it.</p>
    </header>
    <section id="review" aria-label="Review">
      <div class="rv-stats" id="rv-stats"></div>
      <div class="rv-bar"><label>Deck <select id="rv-filter" aria-label="Which volumes to review"></select></label>
        <span>Keys: <b>Space</b> shows the answer, <b>1</b> <b>2</b> <b>3</b> rate it</span></div>
      <div class="rv-mode" id="rv-mode" hidden></div>
      <div id="rv-card"></div>
    </section>
    <section id="deck" class="prose">
      <h2 class="sec">Your deck</h2>
      <p>Chapters marked with a dot are in your deck. Add any chapter to start learning it before you read it, or study one chapter on its own; studying a chapter adds it. A card you know moves up a box and waits longer, 1, 3, 7, 16, 35 then 80 days; one you miss goes back to the first box. At most 20 new cards a day, so reviews never pile up. Your schedule is kept in this browser only.</p>
    </section>
    <div class="rv-deck" id="rv-deck"></div>
  </main>
</div>'''
    js = controller(ns="", resetAsk="Click again to clear")
    page = full_doc(head, body + "\n\n" + "\n".join(srcs) + '\n<script src="cards.js"></script>' +
                    f"\n<script>{js}</script>\n<script>{study_js(mode='review', page='review.html')}</script>\n<script>{REVIEW_JS}</script>")
    (OUT / "review.html").write_text(page, encoding="utf-8")
    return n_idea, n_ex
