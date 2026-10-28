# One-page edition. Runs inside build_site.py's namespace (VOLS, rd, augment_syllabus_main, ...).

def main_inner(s):
    m = re.search(r'<main>', s); return s[m.end():s.rindex('</main>')]
def nav_inner(s):
    m = re.search(r'<nav class="rail-nav" id="railnav">', s); return s[m.end():s.index('</nav>', m.end())]
def style_of(s):
    return "\n".join(re.findall(r'<style>(.*?)</style>', s, re.S))

def strip_comments(css): return re.sub(r'/\*.*?\*/', '', css, flags=re.S)
def split_top(css):
    out = []; i = 0; n = len(css)
    while i < n:
        m = re.match(r'\s+', css[i:])
        if m: i += m.end(); continue
        if css[i] == '@':
            brace = css.find('{', i); semi = css.find(';', i)
            if semi != -1 and (brace == -1 or semi < brace):
                out.append(('raw', css[i:semi + 1])); i = semi + 1; continue
        brace = css.find('{', i)
        if brace == -1: break
        depth = 0; j = brace
        while j < n:
            if css[j] == '{': depth += 1
            elif css[j] == '}':
                depth -= 1
                if depth == 0: j += 1; break
            j += 1
        kind = 'at' if css[i] == '@' else 'rule'
        out.append((kind, css[i:brace].strip(), css[brace + 1:j - 1])); i = j
    return out

UNIQUE_VARS = {'--warn', '--warn-bg', '--shadow'}
def unique_vars(body):
    return {k: v.strip() for k, v in re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', body) if k in UNIQUE_VARS}
def scope_sel(sel, scope='.sa'):
    outp = []
    for p in [x.strip() for x in sel.split(',') if x.strip()]:
        if p in ('html', 'body', ':root'): outp.append(scope)
        elif p == '*': outp.append(scope + ' *')
        elif p.startswith(':root'): outp.append(p.replace(':root', 'html', 1) + ' ' + scope)
        else: outp.append(scope + ' ' + p)
    return ', '.join(outp)
def transform_syllabus_css(css):
    css = strip_comments(css); scoped = []; gvars = {}; gdark = []
    for it in split_top(css):
        if it[0] == 'rule':
            sel, body = it[1], it[2]
            if sel.startswith(':root'):
                uv = unique_vars(body)
                if sel == ':root': gvars.update(uv)
                elif uv: gdark.append(sel + '{' + ''.join(f'{k}:{v};' for k, v in uv.items()) + '}')
                continue
            scoped.append(scope_sel(sel) + '{' + body + '}')
        elif it[0] == 'at':
            pre, inner = it[1], it[2]
            if pre.startswith('@media'):
                inner_out = []
                for jt in split_top(inner):
                    if jt[0] == 'rule':
                        s_, b_ = jt[1], jt[2]
                        if s_.startswith(':root'):
                            uv = unique_vars(b_)
                            if uv: gdark.append(pre + '{' + s_ + '{' + ''.join(f'{k}:{v};' for k, v in uv.items()) + '}}')
                            continue
                        inner_out.append(scope_sel(s_) + '{' + b_ + '}')
                    elif jt[0] == 'at': inner_out.append(jt[1] + '{' + jt[2] + '}')
                    else: inner_out.append(jt[1])
                if inner_out: scoped.append(pre + '{' + ''.join(inner_out) + '}')
            else:
                scoped.append(pre + '{' + inner + '}')
        else:
            scoped.append(it[1])
    return scoped, gvars, gdark

def namespace(main_html, nav_html, slug):
    masks = []
    def mask(m):
        masks.append(m.group(0)); return f"\x00M{len(masks) - 1}\x00"
    masked = re.sub(r'<pre\b.*?</pre>', mask, main_html, flags=re.S)
    masked = re.sub(r'<code\b.*?</code>', mask, masked, flags=re.S)
    defined = set(re.findall(r'\sid="([^"]+)"', masked)) | set(re.findall(r'\bdata-id="([^"]+)"', masked))
    def ren(x): return f"{slug}-{x}"
    def do(txt):
        for pat in (r'(\sid=")([^"]+)(")', r'(\bdata-id=")([^"]+)(")', r'(href="#)([^"]+)(")', r'(url\(#)([^)]+)(\))'):
            txt = re.sub(pat, lambda m: m.group(1) + ren(m.group(2)) + m.group(3) if m.group(2) in defined else m.group(0), txt)
        return txt
    masked = do(masked)
    for k, orig in enumerate(masks):
        masked = masked.replace(f"\x00M{k}\x00", orig)
    return masked, do(nav_html)

net_src = rd("networking-handbook")
host_src = rd(HOST)
scoped, gvars, gdark = transform_syllabus_css(style_of(host_src) + "\n" + HUB_CSS)
# Styles some volumes use that the shared (Exchange) stylesheet lacks: output blocks, maths, appendix
# headings. Any rule whose (media query, selector) the shared sheet doesn't define is carried over, with
# the volume's own ids namespaced the same way its markup is.
net_css = style_of(net_src)
def rule_keys(css):
    keys = set()
    for it in split_top(strip_comments(css)):
        if it[0] == 'rule': keys.add(("", " ".join(it[1].split())))
        elif it[0] == 'at' and it[1].startswith('@media'):
            for jt in split_top(it[2]):
                if jt[0] == 'rule': keys.add((" ".join(it[1].split()), " ".join(jt[1].split())))
    return keys
net_keys = rule_keys(net_css)
extra_rules = []
for v in VOLS:
    vsrc = rd(v["src"])
    vol_ids = set(re.findall(r'\sid="([^"]+)"', vsrc))
    def ns_sel(sel, slug=v["slug"], ids=vol_ids):
        return re.sub(r'#([A-Za-z][\w-]*)', lambda m: f"#{slug}-{m.group(1)}" if m.group(1) in ids else m.group(0), sel)
    for it in split_top(strip_comments(style_of(vsrc))):
        if it[0] == 'rule' and ("", " ".join(it[1].split())) not in net_keys:
            rule = ns_sel(it[1].strip()) + " { " + it[2].strip() + " }"
        elif it[0] == 'at' and it[1].startswith('@media'):
            media = " ".join(it[1].split())
            inner = [jt for jt in split_top(it[2]) if jt[0] == 'rule' and (media, " ".join(jt[1].split())) not in net_keys]
            if not inner: continue
            rule = it[1].strip() + " { " + " ".join(ns_sel(jt[1].strip()) + " { " + jt[2].strip() + " }" for jt in inner) + " }"
        else: continue
        if rule not in extra_rules: extra_rules.append(rule)
EXTRA = """
/* ===== one-page edition ===== */
.sa { display: block; }
.volume { border-top: 3px double var(--rule); margin-top: 76px; padding-top: 6px; }
.vol-rail-op .t { font-weight: 600; }
""" + "\n".join(extra_rules) + "\n"
full_style = (net_css
              + "\n/* ===== syllabus-only variables ===== */\n:root{" + ''.join(f'{k}:{v};' for k, v in gvars.items()) + "}\n"
              + "\n".join(gdark)
              + "\n/* ===== syllabus overview, scoped ===== */\n" + "\n".join(scoped)
              + BASE_CSS + LIB_CSS + EXTRA)

all_link_one = ('<a class="vol-all" href="index.html"><span>Prefer separate pages? Each volume also opens on its own page.</span>'
                '<b>Back to the paged edition &rarr;</b></a>')
syl_main = augment_syllabus_main(main_inner(host_src), lambda v: f'#vol-{v["slug"]}', all_link_one)
syl_nav = nav_inner(host_src)
syl_nav = '\n      <a href="#volumes"><span class="n">&sect;</span><span class="t">Companion volumes</span></a>' + syl_nav

parts = [f'<section class="sa" id="overview">\n{syl_main}\n</section>']
groups = [f'<div class="sep">Overview: the syllabus</div>{syl_nav}']
for v in VOLS:
    s = rd(v["src"])
    nm, nn = namespace(main_inner(s), nav_inner(s), v["slug"])
    parts.append(f'\n<section class="volume" id="vol-{v["slug"]}">\n{nm}\n</section>')
    nn = re.sub(r'<a [^>]*href="#' + v["slug"] + r'-start"[^>]*>.*?</a>\s*', '', nn, flags=re.S)
    nn = re.sub(r'<div class="sep">.*?</div>\s*', '', nn, flags=re.S)
    groups.append(f'<div class="sep">Stage {v["stage"]} &middot; {v["name"]}</div>\n'
                  f'<a class="vol-rail-op" href="#vol-{v["slug"]}"><span class="n">{v["stage"]}</span><span class="t">{v["title"]}</span></a>\n{nn}')

fonts = "\n".join(re.findall(r'<link [^>]+>', net_src.split("<style>")[0])) + "\n" + \
        "\n".join(l for l in re.findall(r'<link rel="stylesheet"[^>]+>', host_src.split("<style>")[0]))
hl = sorted(set(re.findall(r'<script src="[^"]+"></script>', "".join(rd(v["src"]) for v in VOLS))),
            key=lambda t: (0 if t.endswith('highlight.min.js"></script>') else 1, t))
one_js = controller(ns="", resetAsk="Click again to clear all marks")
body = f'''<div class="shell">

  <aside class="rail">
{libnav(with_vols=False)}    <div class="rail-head">One-page edition</div>

    <div class="progress-box">
      <div class="progress-row"><span>Chapters read</span><b id="pct">0 / {TOTAL}</b></div>
      <div class="bar"><span id="barfill"></span></div>
      <div class="progress-row"><span>Stages done</span><b id="pct-stages">0 / 16</b></div>
      <div class="bar"><span id="barfill-stages"></span></div>
    </div>

    <details class="toc" open>
      <summary>Contents &middot; syllabus + {len(VOLS)} volumes</summary>
      <nav class="rail-nav" id="railnav">
{chr(10).join(groups)}
      </nav>
    </details>

    <div class="rail-tools">
      <button class="tool-btn" id="themebtn" type="button">Theme</button>
      <button class="tool-btn" id="resetbtn" type="button">Reset marks</button>
    </div>
  </aside>

  <main>
{chr(10).join(parts)}
  </main>
</div>

{chr(10).join(hl)}
<script>{one_js}</script>'''
head = f"<title>The Engineer's Syllabus (one page)</title>\n{fonts}\n<style>\n{full_style}\n</style>"
(OUT / "all.html").write_text(full_doc(head, body), encoding="utf-8")
print("one-page edition: carried", len(extra_rules), "extra volume rules:", [r.split("{")[0].strip()[:40] for r in extra_rules])
