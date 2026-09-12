import html, random, os
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    NOW = datetime.now(ZoneInfo("Europe/Dublin"))
except Exception:
    NOW = datetime.now()
def stamp_full():
    d = NOW.day
    suf = 'th' if 11 <= d % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')
    return NOW.strftime('%A, %B ') + f'{d}{suf} &middot; ' + NOW.strftime('%I:%M %p').lstrip('0')
e = html.escape

# (tee, no, EUR name, EUR hcp, EUR guest, USA name, USA hcp, USA guest, state)
# state for MODE 'live': done+res, or thru+up (up>0 Europe up, <0 USA up, 0 square)
M = [
 ("2:30", 9,  "Govy",18,0,            "Johnny McCafferty",22,0, dict(done=1, up=-1, res="2&1")),
 ("2:30", 5,  "Brendy",14,0,          "Raymond McGloin",13,1,   dict(done=1, up=+1, res="3&2")),
 ("2:40", 7,  "Jamie McCaffrey",17,0, "Blobby",17,0,            dict(done=1, up=0,  res="halved")),
 ("2:40", 14, "Kealan",32,0,          "Mully",24,0,             dict(done=1, up=+1, res="4&3")),
 ("2:50", 12, "Ben Caughey",24,1,     "Andy",22,0,              dict(done=1, up=-1, res="1 up")),
 ("2:50", 15, "Rusty",25,0,           "Sean Conlon",24,0,       dict(done=1, up=+1, res="2&1")),
 ("3:00", 4,  "Frank",12,0,           "Marty",10,0,             dict(thru=16, up=+1)),
 ("3:00", 16, "Hugo",26,0,            "Collie",30,0,            dict(thru=16, up=-2)),
 ("3:10", 6,  "Fintan Flynn",16,1,    "Ray McCarron",19,1,      dict(thru=15, up=0)),
 ("3:10", 17, "Ronnie Flanagan",26,1, "Seamus McKiernan",20,1,  dict(thru=14, up=+3)),
 ("3:20", 3,  "Lochlann",10,0,        "Leo",7,0,                dict(thru=13, up=-1)),
 ("3:20", 18, "Conan",32,0,           "Conor",30,0,             dict(thru=13, up=+2)),
 ("3:30", 2,  "Shay",9,0,             "Jock",7,0,               dict(thru=12, up=0)),
 ("3:30", 19, "Dom",32,0,             "Buff",36,0,              dict(thru=11, up=-2)),
 ("3:40", 1,  "Ger",9,0,              "Diarmuid King",7,1,      dict(thru=10, up=+1)),
 ("3:40", 20, "Johnny McManus",36,0,  "Goof",36,0,              dict(thru=10, up=0)),
 ("3:50", 10, "Ryan McDermott",18,1,  "Caolan Swift",20,1,      dict(thru=9,  up=-1)),
 ("3:50", 11, "Micky",20,0,           "Jimmy",20,0,             dict(thru=8,  up=+2)),
 ("4:00", 8,  "Jonto",17,0,           "Sean McDermott",16,0,    dict(thru=8,  up=+1)),
 ("4:00", 13, "Jamie Teague",24,0,    "Ingy",24,0,              dict(thru=7,  up=0)),
]

frac = lambda v: (f"{int(v)}&frac12;" if v % 1 else str(int(v)))

# ---- players (Stableford) derived from matches ----
def build_players():
    ps = []
    for tee, no, hn, hh, hg, an, ah, ag, s in M:
        thru = 18 if s.get("done") else s["thru"]
        ps.append(dict(name=hn, hcp=hh, guest=hg, team="eu", thru=thru))
        ps.append(dict(name=an, hcp=ah, guest=ag, team="us", thru=thru))
    return ps

def rank_stableford(ps):
    for p in ps:
        p["proj"] = round(p["pts"] * 18 / p["thru"]) if p["thru"] else 0
    ps.sort(key=lambda p: (-p["proj"], -p["pts"], p["name"]))
    # medals to members, spoon to lowest member
    mr = 0
    members = [p for p in ps if not p["guest"]]
    for p in ps:
        p["medal"] = 0
        if not p["guest"]:
            mr += 1
            if mr <= 3:
                p["medal"] = mr
    for p in ps:
        p["spoon"] = bool(members) and (not p["guest"]) and (p is members[-1])
    return ps

def score_stableford(ps):
    rng = random.Random(91221)
    for p in ps:
        rate = min(2.6, max(1.0, rng.gauss(1.92, 0.42)))   # net Stableford points/hole
        p["pts"] = max(0, round(p["thru"] * rate))
    return rank_stableford(ps)

CSS = '''
:root {
  --paper:#f9fafd; --sunk:#e8ebf8; --ink:#12163c; --soft:#5b6080; --hair:#d3d8f0;
  --navy:#060545; --home:#1340d0; --away:#e31112; --gold:#e0bd28;
  --band:#060545; --live:#e31112;
  --display:"Barlow Condensed","Arial Narrow",sans-serif;
  --body:"Source Sans 3",system-ui,-apple-system,sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper:#0a0c24; --sunk:#12163a; --ink:#e8eaf6; --soft:#9aa0c4; --hair:#23274f;
  --home:#5a86f5; --away:#ee4a50; --band:#05062e; --live:#ee4a50;
} }
:root[data-theme="dark"] {
  --paper:#0a0c24; --sunk:#12163a; --ink:#e8eaf6; --soft:#9aa0c4; --hair:#23274f;
  --home:#5a86f5; --away:#ee4a50; --band:#05062e; --live:#ee4a50;
}
* { box-sizing:border-box; }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior:smooth; } }
html,body { margin:0; padding:0; }
img { max-width:100%; }
body { background:var(--paper); color:var(--ink); font-family:var(--body);
  line-height:1.4; margin:0 auto; max-width:34rem; padding:0 0 3rem; }
h1,h2,h3 { font-family:var(--display); margin:0; text-transform:uppercase; }
p { margin:0; } ul,ol { list-style:none; margin:0; padding:0; }

.mock { background:var(--gold); color:var(--navy); font-family:var(--display); font-size:0.8rem;
  font-weight:600; letter-spacing:0.12em; padding:0.5rem 1rem; text-align:center; text-transform:uppercase; }
.mock b { font-weight:700; }
.back { align-items:center; color:var(--home); display:inline-flex; font-family:var(--display);
  font-size:0.8rem; font-weight:600; gap:0.25rem; letter-spacing:0.06em; margin:0.55rem 0 0 1rem;
  text-decoration:none; text-transform:uppercase; }
.back:hover, .back:focus-visible { text-decoration:underline; text-underline-offset:0.15em; }

.top { padding:1.1rem 1rem 0.75rem; text-align:center; }
.top h1 { font-size:1.8rem; font-weight:700; letter-spacing:0.08em; line-height:1.1; text-indent:0.08em; }
.top .sub { color:var(--soft); font-family:var(--display); font-size:0.82rem;
  letter-spacing:0.09em; text-indent:0.09em; text-transform:uppercase; }
.top .sub a { color:var(--home); text-decoration:underline; text-underline-offset:0.15em; }
.top .sub a:hover, .top .sub a:focus-visible { text-decoration-thickness:2px; }
#stableford, #cup { scroll-margin-top:0.6rem; }
/* title set above */
.stamp { align-items:center; display:inline-flex; flex-wrap:wrap; gap:0.35rem; justify-content:center; margin-top:0.3rem; }
.dot { background:var(--live); border-radius:50%; height:0.5rem; width:0.5rem; flex:0 0 auto; }
.dot--pre { background:var(--gold); }
@media (prefers-reduced-motion: no-preference) { .dot:not(.dot--pre) { animation:pulse 1.8s ease-in-out infinite; } }
@keyframes pulse { 50% { opacity:0.3; } }
.stamp span { color:var(--live); font-family:var(--display); font-size:0.78rem;
  font-weight:600; letter-spacing:0.1em; text-transform:uppercase; }
.stamp .when { color:var(--soft); }

.hero { background:linear-gradient(100deg,#123bbd 0%,#0b1a5e 42%,#0b1a5e 58%,#c11418 100%); color:#fff; padding:0.9rem 1rem 1rem; }
.hs { align-items:center; display:grid; gap:0.5rem; grid-template-columns:1fr auto 1fr; }
.hs__t { font-family:var(--display); font-size:1.35rem; font-weight:700; letter-spacing:0.06em; line-height:1; text-transform:uppercase; }
.hs__t.eu { color:#dbe4ff; } .hs__t.us { color:#ffd9d9; text-align:right; }
.hs__n { font-family:var(--display); font-variant-numeric:tabular-nums; font-weight:700;
  font-size:3rem; line-height:0.85; margin-top:0.2rem; }
.hs__n.us { text-align:right; }
.hs__dash { color:rgba(255,255,255,0.4); font-family:var(--display); font-size:1.6rem; font-weight:600; }
.bar { background:rgba(255,255,255,0.16); border-radius:999px; height:0.5rem; margin-top:0.85rem;
  overflow:hidden; position:relative; display:flex; }
.bar__e { background:var(--home); height:100%; } .bar__a { background:var(--away); height:100%; margin-left:auto; }
.bar__ctr { background:var(--gold); bottom:-4px; left:50%; position:absolute; top:-4px; width:2.5px; transform:translateX(-1px); }
.cap { color:rgba(255,255,255,0.8); font-size:0.76rem; margin-top:0.55rem; text-align:center; }
.cap b { color:var(--gold); font-weight:700; }

.legend { align-items:center; background:var(--sunk); border-bottom:1px solid var(--hair);
  color:var(--soft); display:flex; flex-wrap:wrap; font-family:var(--display); font-size:0.7rem; gap:0.3rem 0.9rem;
  justify-content:center; letter-spacing:0.1em; padding:0.4rem 1rem; text-transform:uppercase; }
.legend b { align-items:center; display:inline-flex; font-weight:600; gap:0.3rem; }
.legend .pre { letter-spacing:0.1em; }
.chip { border-radius:3px; height:0.7rem; width:0.7rem; }
.chip.eu { background:var(--home); } .chip.us { background:var(--away); }

.cols { color:var(--soft); display:grid; font-family:var(--display); font-size:0.68rem;
  grid-template-columns:1fr 4.4rem 1fr; letter-spacing:0.12em; padding:0.6rem 0 0.25rem; text-transform:uppercase; }
.cols span { padding:0 0.6rem; } .cols b { font-weight:600; text-align:center; } .cols .us { text-align:right; }
.board { border-top:1px solid var(--hair); }
.row { border-bottom:1px solid var(--hair); display:grid; grid-template-columns:1fr 4.4rem 1fr; min-height:2.7rem; }
.side { align-items:center; display:flex; gap:0.4rem; justify-content:space-between; min-width:0; padding:0.4rem 0.6rem; }
.side .nm { font-size:0.9rem; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.side--h .nm { text-align:right; }
.marg { color:var(--soft); flex:0 0 auto; font-family:var(--display); font-size:0.72rem;
  font-variant-numeric:tabular-nums; font-weight:600; letter-spacing:0.04em; text-transform:uppercase; }
.side--h.lead { background:var(--home); color:#fff; } .side--a.lead { background:var(--away); color:#fff; }
.side.lead .marg { color:rgba(255,255,255,0.85); }
.side--h.done.win { background:var(--home); color:#fff; } .side--a.done.win { background:var(--away); color:#fff; }
.side.done.win .marg { color:rgba(255,255,255,0.85); }
.side.done:not(.win):not(.half) { color:var(--soft); }
.side.half { background:transparent; } .side.half .marg { color:var(--soft); }
.mid { background:var(--sunk); border-left:1px solid var(--hair); border-right:1px solid var(--hair);
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:0.05rem; }
.mno { color:var(--soft); font-family:var(--display); font-size:0.6rem; font-weight:600; letter-spacing:0.08em; opacity:0.8; }
.mno::before { content:"MATCH "; }
.st { color:var(--soft); font-family:var(--display); font-size:0.82rem; font-weight:700;
  font-variant-numeric:tabular-nums; letter-spacing:0.02em; text-transform:uppercase; }
.st--done { color:var(--ink); } .st--halved { color:#a9871a; } .st--tee { color:var(--soft); }
.st--f { color:var(--ink); letter-spacing:0.06em; }

.rep { grid-column:1 / -1; padding:0.3rem 0.75rem 0.55rem; }
.rep summary { color:var(--home); cursor:pointer; display:inline-flex; font-family:var(--display); font-size:0.72rem;
  font-weight:600; gap:0.3rem; letter-spacing:0.08em; list-style:none; text-transform:uppercase; }
.rep summary::-webkit-details-marker { display:none; }
.rep summary::after { content:"▾"; } .rep[open] summary::after { content:"▴"; }
.rep summary:hover, .rep summary:focus-visible { text-decoration:underline; text-underline-offset:0.15em; }
.rep p { color:var(--soft); font-size:0.9rem; line-height:1.45; margin-top:0.4rem; }
.rl { background:none; border:0; color:var(--home); cursor:pointer; font-family:var(--display); font-size:0.62rem;
  font-weight:600; letter-spacing:0.08em; margin-top:0.1rem; padding:0; text-transform:uppercase; white-space:nowrap; }
.rl::after { content:" ▾"; } .rl[aria-expanded="true"]::after { content:" ▴"; }
.rl:hover, .rl:focus-visible { text-decoration:underline; text-underline-offset:0.15em; }
.rp { color:var(--soft); font-size:1.05rem; grid-column:1 / -1; line-height:1.5; padding:0.6rem 0.75rem 0.75rem; }
.rp b { color:var(--ink); font-weight:600; }
.rep p b { color:var(--ink); font-weight:600; }
.note { color:var(--soft); font-size:0.82rem; padding:0.8rem 1rem 0; }
.note b { color:var(--ink); font-weight:600; }

/* section head */
.head { align-items:baseline; display:flex; gap:0.6rem; justify-content:space-between; padding:2rem 1rem 0.5rem; }
.head h2 { font-size:1.3rem; font-weight:700; letter-spacing:0.05em; }
.head p { color:var(--soft); font-family:var(--display); font-size:0.8rem; letter-spacing:0.08em;
  text-align:right; text-transform:uppercase; }

/* stableford placeholder */
.sfpre { background:var(--sunk); border-radius:8px; margin:0 1rem; padding:0.9rem 1rem; }
.sfpre p { color:var(--soft); font-size:0.86rem; }
.sfpre p + p { margin-top:0.5rem; }
.sfpre b { color:var(--ink); font-weight:700; }

/* stableford board */
.sh, .sr { align-items:center; display:grid; gap:0.4rem;
  grid-template-columns:1.6rem 1fr 2.1rem 2.1rem 2.6rem; padding:0.34rem 1rem; }
.sh { color:var(--soft); font-family:var(--display); font-size:0.64rem; letter-spacing:0.08em; text-transform:uppercase; }
.sh__k { background:none; border:0; color:inherit; cursor:pointer; font:inherit; letter-spacing:inherit;
  padding:0; text-align:right; text-transform:inherit; white-space:nowrap; width:100%; }
.sh__k.pl { text-align:left; }
.sh__k.b { color:var(--ink); font-weight:700; }
.sh__k:hover, .sh__k:focus-visible { color:var(--ink); }
.sh__k[data-active] { color:var(--ink); }
.sh__k .car { font-size:0.82em; margin-left:0.35em; }
.sp { border-top:1px solid var(--hair); }
.sr { border-bottom:1px solid var(--hair); font-variant-numeric:tabular-nums; }
.sr__i { color:var(--soft); font-family:var(--display); font-weight:600; text-align:right; }
.sr__p { align-items:center; display:flex; gap:0.4rem; min-width:0; }
.sr__dot { border-radius:50%; flex:0 0 auto; height:0.5rem; width:0.5rem; }
.sr__dot.eu { background:var(--home); } .sr__dot.us { background:var(--away); }
.sr__n { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.sr__g { color:var(--soft); font-family:var(--display); font-size:0.6rem; font-weight:600;
  letter-spacing:0.06em; border:1px solid var(--hair); border-radius:3px; padding:0 0.2rem; flex:0 0 auto; }
.sr__f { color:var(--soft); text-align:right; }
.sr__j { font-weight:700; text-align:right; }
.sr--1 { background:rgba(224,189,40,0.18); } .sr--1 .sr__i { color:#a9871a; }
.sr--2, .sr--3 { background:rgba(91,96,128,0.08); }
.sr--spoon { background:rgba(224,189,40,0.10); }
.sr--spoon .sr__i::after { content:" \\1F944"; }
'''

REP_JS = """
<script>
(function () {
  document.querySelectorAll('.rl').forEach(function (b) {
    b.addEventListener('click', function () {
      var p = document.getElementById(b.getAttribute('aria-controls'));
      if (!p) return;
      var open = p.hidden;
      p.hidden = !open;
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
})();
</script>
"""

def cup_rows(mode, results=None, reports=None):
    rows = []
    for tee, no, hn, hh, hg, an, ah, ag, s in M:
        st = s if results is None else results.get(no)
        if mode == 'pre' or st is None:
            rows.append(
f'''    <li class="row">
      <div class="side side--h"><span class="marg"></span><span class="nm">{e(hn)}</span></div>
      <div class="mid"><span class="mno">{no}</span><span class="st st--tee">{tee}</span></div>
      <div class="side side--a"><span class="nm">{e(an)}</span><span class="marg"></span></div>
    </li>''')
            continue
        up = st["up"]; done = st.get("done"); hlead = up>0; alead = up<0
        if done:
            res = st["res"]
            mid = '<span class="st st--f">F</span>'
            if res == "halved":
                hmarg=amarg="A/S"; hcls=acls=" done half"
            elif hlead:
                hmarg=res; amarg=""; hcls=" done win"; acls=" done"
            else:
                amarg=res; hmarg=""; hcls=" done"; acls=" done win"
        else:
            thru=st["thru"]; rem=18-thru; mid=f'<span class="st">Thru {thru}</span>'
            dormie=(up!=0 and abs(up)==rem)
            def marg(): return "A/S" if up==0 else ("Dormie" if dormie else f"{abs(up)} Up")
            hmarg = marg() if (hlead or up==0) else ""
            amarg = marg() if (alead or up==0) else ""
            hcls=" lead" if hlead else ""; acls=" lead" if alead else ""
        rep = ''
        if reports and no in reports:
            if done:
                mid += f'<button class="rl" type="button" aria-expanded="false" aria-controls="rep-{no}">Report</button>'
                rep = f'\n      <p class="rp" id="rep-{no}" hidden>{reports[no]}</p>'
        rows.append(
f'''    <li class="row">
      <div class="side side--h{hcls}"><span class="marg">{hmarg}</span><span class="nm">{e(hn)}</span></div>
      <div class="mid"><span class="mno">{no}</span>{mid}</div>
      <div class="side side--a{acls}"><span class="nm">{e(an)}</span><span class="marg">{amarg}</span></div>{rep}
    </li>''')
    return "\n".join(rows)

def stableford_section(mode, live_sf=None):
    if mode == 'pre':
        return '<div class="head" id="stableford"><h2>The Stableford</h2><p>Individual net</p></div>'
    ps = build_players()
    if live_sf is not None:
        ps = [p for p in ps if p["name"] in live_sf]
        for p in ps:
            p["thru"] = live_sf[p["name"]]["thru"]
            p["pts"] = live_sf[p["name"]]["pts"]
        ps = rank_stableford(ps)
    else:
        ps = score_stableford(ps)
    rows = []
    for i, p in enumerate(ps, 1):
        cls = ""
        if p["medal"] == 1: cls = " sr--1"
        elif p["medal"] in (2,3): cls = " sr--2"
        if p["spoon"]: cls += " sr--spoon"
        g = '<span class="sr__g">Guest</span>' if p["guest"] else ''
        rows.append(
f'''    <li class="sr{cls}" data-rank="{i}" data-name="{e(p['name'])}" data-thru="{p['thru']}" data-pts="{p['pts']}" data-proj="{p['proj']}"><span class="sr__i">{i}</span>'''
f'''<span class="sr__p"><span class="sr__dot {p['team']}"></span><span class="sr__n">{e(p['name'])}</span>{g}</span>'''
f'''<span class="sr__f">{p['thru']}</span>'''
f'''<span class="sr__j">{p['pts']}</span><span class="sr__f">{p['proj']}</span></li>''')
    return f'''<div class="head" id="stableford"><h2>The Stableford</h2><p>Individual net</p></div>
<div class="sh"><button type="button" class="sh__k" data-k="rank" aria-label="Sort by position">#</button><button type="button" class="sh__k pl" data-k="name">Player</button><button type="button" class="sh__k" data-k="thru">Thru</button><button type="button" class="sh__k b" data-k="pts">Pts</button><button type="button" class="sh__k" data-k="proj">Proj</button></div>
<ol class="sp">
{chr(10).join(rows)}
</ol>
<p class="note"><b>Proj</b> stretches each card to eighteen holes at its current rate and the table is
ranked on it, highest first &mdash; groups are at different holes, so points-so-far are not yet
comparable.{(' <b>' + str(len(ps)) + ' of 40</b> players on the board so far.') if live_sf is not None else ''}</p>'''


SORT_JS = """<script>
(function () {
  var sp = document.querySelector('.sp');
  var head = document.querySelector('.sh');
  if (!sp || !head) return;
  var rows = [].slice.call(sp.querySelectorAll('.sr'));
  var state = { k: 'proj', dir: 'desc' };
  function val(li, k) {
    if (k === 'name') return li.getAttribute('data-name').toLowerCase();
    return parseFloat(li.getAttribute('data-' + k));
  }
  function apply() {
    var k = state.k, dir = state.dir === 'asc' ? 1 : -1;
    rows.slice().sort(function (a, b) {
      var va = val(a, k), vb = val(b, k);
      if (va < vb) return -dir;
      if (va > vb) return dir;
      return parseFloat(a.getAttribute('data-rank')) - parseFloat(b.getAttribute('data-rank'));
    }).forEach(function (li) { sp.appendChild(li); });
    head.querySelectorAll('.sh__k').forEach(function (btn) {
      var old = btn.querySelector('.car'); if (old) old.remove();
      btn.removeAttribute('data-active');
      if (btn.getAttribute('data-k') === k) {
        btn.setAttribute('data-active', '');
        var s = document.createElement('span');
        s.className = 'car';
        s.textContent = dir === 1 ? '▲' : '▼';
        btn.appendChild(s);
      }
    });
  }
  head.querySelectorAll('.sh__k').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var k = btn.getAttribute('data-k');
      var def = (k === 'name' || k === 'rank') ? 'asc' : 'desc';
      if (state.k === k) state.dir = state.dir === 'asc' ? 'desc' : 'asc';
      else { state.k = k; state.dir = def; }
      apply();
    });
  });
  apply();
})();
</script>"""

def build(mode, out, mock, results=None, sf=None, when=None, reports=None):
    # scores
    real = results is not None
    pe = pa = 0.0; done_n = live_n = eu_up = us_up = sq_n = 0
    for row in M:
        no_ = row[1]; ts = row[8]
        st = ts if results is None else results.get(no_)
        if st and st.get("done"):
            done_n += 1
            u = st["up"]
            if u>0: pe+=1
            elif u<0: pa+=1
            else: pe+=.5; pa+=.5
        elif st:                         # in-progress matches project at their current standing
            live_n += 1
            u = st["up"]
            if u>0: pe+=1; eu_up+=1
            elif u<0: pa+=1; us_up+=1
            else: pe+=.5; pa+=.5; sq_n+=1
    out_n = live_n                       # matches actually out on the course
    if mode=='pre': pe=pa=0.0
    TARGET=10.5; tick=TARGET/20*100; tickU=100-tick
    pe_pct=pe/20*100; pa_pct=pa/20*100

    if mode=='pre':
        stamp='<span class="dot dot--pre" aria-hidden="true"></span><span>First tee 2:30 PM</span><span class="when">Saturday, September 12th</span>'
        cap='Twenty singles &middot; lead past the gold centre line &mdash; <b>10&frac12; wins</b>'
        legend='<span class="pre">Draw set &mdash; scores go live on the day</span>'
        note='This board goes live when the first match tees off at <b>2:30 PM Saturday</b>.'
    else:
        whenstr = when or ('Saturday, September 12th &middot; 5:34 PM' if mock else stamp_full())
        stamp=f'<span class="dot" aria-hidden="true"></span><span>Live</span><span class="when">{whenstr}</span>'
        cap='Projected now &middot; lead past the gold centre line &mdash; <b>10&frac12; of 20 wins</b>'
        legend=(f'<b><span class="chip eu"></span>Europe up {eu_up}</b>'
                f'<b><span class="chip us"></span>USA up {us_up}</b>'
                f'<span>A/S {sq_n}</span>'
                f'<span>{done_n} in &middot; {out_n} out</span>')
        note=''

    state = 'live' if mode=='live' else 'pre'
    mockbar = ('<div class="mock"><b>Example board</b> &middot; sample scores, not a real result</div>' if mock else '')
    cupnote = f'<p class="note">{note}</p>' if note else ''
    if real:
        sf_html = stableford_section(mode, live_sf=sf) if sf else stableford_section('pre')
    else:
        sf_html = stableford_section(mode)

    HTML=f'''<title>Captain&rsquo;s Day &mdash; {'Example' if mock else 'Live'} Board</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="board-state" content="{state}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Sans+3:wght@400;600;700&display=swap">
<style>{CSS}</style>
{mockbar}
<a class="back" href="/">&larr; Draw sheet</a>
<header class="top">
  <h1>Captain&rsquo;s Day &mdash; Live</h1>
  <p class="sub"><a href="#cup">Singles Matchplay</a> &middot; <a href="#stableford">Stableford</a></p>
  <p class="stamp">{stamp}</p>
</header>

<div class="hero" id="cup">
  <div class="hs">
    <div><div class="hs__t eu">Europe</div><div class="hs__n">{frac(pe)}</div></div>
    <div class="hs__dash">&ndash;</div>
    <div><div class="hs__t us">USA</div><div class="hs__n us">{frac(pa)}</div></div>
  </div>
  <div class="bar">
    <div class="bar__e" style="width:{pe_pct:.1f}%"></div>
    <div class="bar__a" style="width:{pa_pct:.1f}%"></div>
    <div class="bar__ctr" aria-hidden="true"></div>
  </div>
  <p class="cap">{cap}</p>
</div>

<div class="legend">{legend}</div>

<div class="cols"><span>Europe</span><b>&nbsp;</b><span class="us">USA</span></div>
<ul class="board">
{cup_rows(mode, results, reports)}
</ul>
{cupnote}

{sf_html}
'''
    HTML += SORT_JS
    if reports:
        HTML += REP_JS
    open(out,'w',encoding='utf-8').write(HTML)
    print(f"{out}  mode={mode} mock={mock}  EUR {frac(pe)} v USA {frac(pa)}  {len(HTML)} bytes")

# Example match write-ups for the mock page. Four or five sentences each, matching the mock
# states above. The live page does not use these.
MOCK_REPORTS = {
    9:  "Johnny took this one <b>2&amp;1</b> and never trailed after the turn. Govy won the 2nd and 4th to lead early, but Johnny&rsquo;s shot at the 7th squared it and his 4 at the 8th put him ahead. A scratched 10th from Govy made it two, and the pair traded halves down the back nine. Johnny&rsquo;s shot at the 15th saved a half when Govy had a par, and a 5 at the 17th closed it out.",
    5:  "Brendy beat Raymond <b>3&amp;2</b> in the day&rsquo;s tidiest match. Level after six, Brendy won the 7th, 8th and 10th with three pars in four holes. Raymond pulled one back at the 12th but bogeyed the 13th and 14th to go three down. A half at the 16th was all Brendy needed, and both cards finished well into the thirties.",
    7:  "Jamie and Blobby played off the same mark and finished exactly where they started, <b>all square</b>. Jamie led twice on the front nine and Blobby squared it each time within a hole. Blobby went 1 up at the 14th, Jamie birdied the 16th to level, and neither man blinked over the last two. Half a point each, and the fairest result on the board.",
    14: "Kealan used his eight shots to great effect and beat Mully <b>4&amp;3</b>. Mully led after a scrappy first three, then Kealan&rsquo;s shots at the 6th, 7th and 8th turned a deficit into a two-hole lead. A net birdie at the 12th made it three and Mully&rsquo;s double at the 14th ended it. Kealan scratched the 15th and 18th but by then it did not matter.",
    12: "Andy edged Ben <b>1 up</b> in a match that turned on the last three holes. Ben, a guest off 24, led by two after nine and was still 1 up standing on the 16th tee. Andy won the 16th with a par, halved the 17th, and holed from six feet for a 4 at the last to win it. Ben had the better Stableford card and the worse afternoon.",
    15: "Rusty beat Sean <b>2&amp;1</b> with a back nine he will talk about for a while. Sean led by two after five, but Rusty won the 8th and 9th to square it at the turn. Pars at the 12th and 14th put Rusty two ahead, and his shot at the 15th halved a hole Sean had won on gross. A halved 17th finished it.",
    4:  "Frank leads Marty <b>1 up with two to play</b> in the low-handicap match of the day. Marty was 2 up after four before Frank won three in a row from the 5th. Marty&rsquo;s birdie at the 11th squared it and Frank&rsquo;s shot at the 15th put him back ahead. Both have played the back nine in level par gross, and the 17th will decide whether Frank is dormie.",
    16: "Collie is <b>2 up with two to play</b> on Hugo and needs only a half to win. Collie&rsquo;s four shots have been the story: one halved the 7th, one won the 12th and one halved the 15th. Hugo won the 13th and 14th to get within one but a double at the 16th cost him. Collie is dormie and Hugo has to win both remaining holes to halve.",
    6:  "Fintan and Ray are <b>all square with three to play</b>. Fintan was 3 up after nine, then Ray won the 12th on his shot and the 13th and 14th on gross. Ray&rsquo;s shot at the 15th halved that hole when Fintan had a par. This is a guests&rsquo; match and it will be decided on the 18th green.",
    17: "Ronnie leads Seamus <b>3 up with four to play</b>. Seamus won the 1st and 2nd, then Ronnie&rsquo;s six shots kicked in: three of them won holes outright between the 6th and the 12th. Seamus birdied the 13th to get one back and Ronnie replied with a net birdie at the 14th. A half at the 15th makes Ronnie dormie.",
    3:  "Leo is <b>1 up on Lochlann with five to play</b>. The pair traded the lead four times on the front nine, with Lochlann&rsquo;s shot winning the 7th and Leo&rsquo;s eagle at the 11th putting him ahead. Lochlann squared it at the 12th with his second shot of the day. Leo&rsquo;s par at the 13th restored his lead and Lochlann still has a shot to come at the 15th.",
    18: "Conan leads Conor <b>2 up with five to play</b> in the highest-scoring match on the course. Neither man scored at the 1st or 2nd. Conan&rsquo;s shot at the 7th won it, Conor took the 8th and 10th, and Conan won the 11th, 12th and 13th in a row. Conan has one more shot at the 15th.",
    2:  "Shay and Jock are <b>all square with six to play</b>. Shay was 3 up after seven, with his shot winning the 7th, before Jock won the 8th, 9th and 10th on gross. Shay&rsquo;s eagle at the 11th put him back ahead and Jock&rsquo;s birdie at the 12th squared it again. Shay&rsquo;s last shot comes at the 15th.",
    19: "Buff leads Dom <b>2 up with seven to play</b>, which nobody predicted after the front nine. Dom was 3 up at the turn. Buff&rsquo;s shot halved the 7th and won the 12th, and he has won the 9th, 10th and 11th on gross too. Buff has one shot left, at the 15th, and Dom has not scored a point since the 5th.",
    1:  "Ger leads Diarmuid <b>1 up with eight to play</b>. Diarmuid went 3 up with pars at the 2nd, 3rd and 4th. Ger&rsquo;s shot won the 7th, his par won the 8th, and his birdie at the 10th squared it. Ger took the lead with a 4 at the par-5 11th, and his second shot is at the 15th.",
    20: "Johnny and Goof are <b>all square with eight to play</b>. Goof was 3 up after seven, winning four holes to Johnny&rsquo;s one. Johnny won the 8th, 9th and 10th in a row, the 10th with a net 2. Both men get two shots on every hole, so every hole is live.",
    10: "Caolan leads Ryan <b>1 up at the turn</b>. Ryan was 2 up after four. Caolan won the 5th, and her par at the 7th, helped by a shot, gave her the lead. Ryan squared it at the 8th and Caolan won the 9th with a 5 to Ryan&rsquo;s 6.",
    11: "Micky leads Jimmy, the USA captain, <b>2 up after eight</b>. Jimmy won the 1st with a par, then Micky won the 3rd, 4th and 5th. Jimmy&rsquo;s 5 at the 7th, a net 3, won a hole back. Micky&rsquo;s 4 at the 8th restored the two-hole lead and Jimmy has ten holes to find a way back.",
    8:  "Jonto, the Europe captain, leads Sean <b>1 up after eight</b>. Sean won the 1st and 4th, Jonto the 2nd and 6th. Jonto scratched the 5th, Sean scratched the 7th, and the 8th was halved in sixes. Jonto&rsquo;s one shot is at the 15th and this one looks like going all the way.",
    13: "Jamie and Ingy are <b>all square after seven</b>. Ingy won the 1st with a 5 to a 10 and Jamie&rsquo;s 4 at the 2nd squared it. Jamie went 1 up at the 4th, Ingy won the 5th and 6th, and Jamie&rsquo;s 6 at the 7th, a net 4, levelled it again. Both play off 24 and nobody has led by more than one.",
}

# Real match write-ups for the live page, keyed by match number. Only finished matches are
# rendered; add one here when a match is entered as done.
LIVE_REPORTS = {
    2:  "Shay beat Jock <b>4&amp;3</b> and turned in the best member card of the day. He was 3 up after seven, his shot winning the 7th, before Jock won the 8th, 9th and 10th on gross to square it. Shay&rsquo;s eagle 3 at the par-5 11th put him back in front and he never looked back, winning the 12th, 14th and 15th. He finished on 37 points with a birdie at the 17th; Jock&rsquo;s birdie at the last gave him 31.",
    3:  "Leo beat Lochlann <b>1 up</b> on the 18th green in the match of the day. The lead changed hands four times on the front nine, Lochlann&rsquo;s shot winning the 7th and Leo&rsquo;s eagle at the 11th answering it. Leo went 2 up when Lochlann scratched the 15th, Lochlann won the 16th and birdied the 17th to square it, and Leo birdied the last to win. Both men finished on 35 points.",
    4:  "Frank beat Marty <b>4&amp;3</b> in the low-handicap match. Frank was 5 up after ten holes, his birdie at the 9th the pick of them, with his shot at the 7th halving a hole Marty had won on gross. Marty won the 12th and birdied the 14th to get back to 3 down, but Frank&rsquo;s 7 at the 15th still beat an 8. Frank finished on 35 points, Marty on 34 with a birdie at the last.",
    5:  "Brendy beat Raymond <b>3&amp;1</b> and was never behind after the 3rd. Two up at the turn, he lost the 10th, then won the 12th and a par at the 13th made it three. His shot at the 15th halved a hole Raymond had won on gross and left him dormie. Raymond took the 16th, Brendy&rsquo;s par at the 17th closed it. Brendy 32 points, Raymond 28.",
    6:  "Fintan beat Ray <b>1 up</b> at the last after leading by three at the turn. Ray&rsquo;s shot won him the 12th, pars at the 13th and 14th squared it, and his shot at the 15th halved that hole when Fintan had a par. Fintan won the 16th, Ray&rsquo;s par at the 17th levelled it again, and Fintan&rsquo;s par at the 18th won it. Fintan finished on 34 points, Ray on 32.",
    7:  "Jamie beat Blobby <b>3&amp;1</b>. Level after nine holes of swapping the lead, Jamie went 3 up when Blobby ran up a 10 at the 11th and a 6 at the 12th. Blobby won the 14th and 16th but Jamie won the 15th between them and was dormie with two to play. A 5 to a 6 at the 17th finished it. Jamie 27 points, Blobby 26.",
    8:  "Sean beat Jonto, the Europe captain, <b>5&amp;4</b>. Sean&rsquo;s 3 at the 6th, a net eagle, put him 3 up, and though he scratched the 7th the next four holes were halved. Jonto scratched the 5th and the 12th, and Sean&rsquo;s 5s at the 13th and 14th ended it with four to play. Jonto never got to use his one shot at the 15th.",
    9:  "Govy and Johnny <b>halved</b> after one of the day&rsquo;s great escapes. Johnny&rsquo;s shot at the 12th put him ahead and his shot at the 15th saved a half when Govy had a par. A 5 at the 16th made Johnny dormie two up. Govy then won the 17th with an 8 to a 9 and the 18th with a 6 to an 8 to steal the half. Both finished on 29 points.",
    12: "Ben beat Andy <b>7&amp;6</b>, the biggest margin of the day. Ben was 4 up at the turn, his shot winning the 7th, then took the 10th, 11th and 12th to end it with six to play. He kept going and finished on 35 points, the best guest card. Andy finished on 23.",
    13: "Ingy beat Jamie <b>6&amp;4</b>. Jamie led once, after the 4th, before Ingy won the 5th, 6th, 7th and 8th in a row and added the 9th, 10th and 11th to go 6 up. Jamie won the 12th, the 13th was halved, and Ingy&rsquo;s 6 at the 14th closed it out. Ingy was on 20 points through 16.",
    14: "Mully beat Kealan <b>4&amp;2</b>. Mully was 3 up after Kealan scratched the 6th, then Kealan&rsquo;s shots at the 7th and 8th won both holes to cut it to one. Mully&rsquo;s 3 at the 10th and 5 at the 11th restored the lead, Kealan&rsquo;s shot won the 12th, and Mully&rsquo;s net 3 at the 14th made it two again. Kealan scratched the 15th and Mully&rsquo;s 6 at the 16th finished it. Mully 26 points, Kealan 23.",
    15: "Sean beat Rusty <b>2 up</b> by winning the last three holes. Rusty was 2 up at the turn and 1 up with three to play after his shot won the 15th. Sean&rsquo;s 7 at the 16th squared it, his 7 at the 17th put him ahead, and his 6 at the last sealed it. Both finished on 19 points.",
    16: "Collie beat Hugo <b>3&amp;1</b>, and his shots did the work. Collie&rsquo;s shot halved the 7th, won the 12th and halved the 15th. Hugo won the 9th, 10th, 13th and 14th on gross but never got level. Collie&rsquo;s 6 at the 16th made him dormie and his 7 at the 17th beat an 8. Hugo 17 points, Collie 18.",
    17: "Seamus beat Ronnie <b>7&amp;6</b>. Ronnie scratched seven of the first ten holes, and Seamus&rsquo;s 2 at the 2nd and pars at the 6th, 8th and 9th had him 7 up at the 10th. Ronnie&rsquo;s shots halved the 7th and the 12th, and the 12th ended it. Seamus was on 26 points through 12.",
    18: "Conan beat Conor <b>3&amp;2</b> in a match neither man led by more than two. Nobody scored at the 1st or 2nd. Conan&rsquo;s shot won the 7th, the lead swapped through the 8th, 9th and 10th, and Conan&rsquo;s 7s at the 11th and 12th put him 2 up. His shot halved the 15th after Conor won the 14th, and his 8 at the 16th beat a 13 to finish it. Conan 19 points, Conor 22.",
    19: "Dom beat Buff <b>2&amp;1</b>, having been 4 up after eleven and 1 up after sixteen. Buff&rsquo;s shot halved the 7th and won the 12th, and he won the 14th, 15th and 16th on the trot, the 15th on his last shot. Dom&rsquo;s 7 at the 17th against a 10 ended the comeback. Dom 17 points, Buff 6.",
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- day-of controls: flip LIVE_ON to True on the first card, edit LIVE_RESULTS as cards come in ----
LIVE_ON = True
# RULE: proper singles matchplay on gross. The higher handicapper receives 100% of the
# handicap difference, one shot per hole on the hardest holes (the shots printed on the
# cards); the lower handicapper plays off scratch. Lower net wins the hole, level halves.
# up > 0 Europe ahead, up < 0 USA ahead, 0 all square.
# match no -> dict(thru=N, up=U) in progress, or dict(done=1, up=U, res="3&2") finished.
LIVE_RESULTS = {
    9:  dict(done=1, up=0, res="halved"),  # Govy v Johnny McCafferty -- halved (Govy won 17th and 18th from dormie down)
    5:  dict(done=1, up=+3, res="3&1"),  # Brendy v Raymond McGloin -- Brendy won 3&1
    7:  dict(done=1, up=+3, res="3&1"),  # Jamie McCaffrey v Blobby -- Jamie won 3&1
    14: dict(done=1, up=-4, res="4&2"),  # Kealan v Mully -- Mully won 4&2
    16: dict(done=1, up=-3, res="3&1"),  # Hugo v Collie -- Collie won 3&1 (Collie's shots halved 7th and 15th, won 12th)
    15: dict(done=1, up=-2, res="2 up"),  # Rusty v Sean Conlon -- Sean won 2 up (won 16th, 17th, 18th)
    12: dict(done=1, up=+7, res="7&6"),  # Ben Caughey v Andy -- Ben won 7&6
    6:  dict(done=1, up=+1, res="1 up"),  # Fintan Flynn v Ray McCarron -- Fintan won 1 up (won the 18th)
    4:  dict(done=1, up=+4, res="4&3"),  # Frank v Marty -- Frank won 4&3
    17: dict(done=1, up=-7, res="7&6"),  # Ronnie Flanagan v Seamus McKiernan -- Seamus won 7&6
    3:  dict(done=1, up=-1, res="1 up"),  # Lochlann v Leo -- Leo won 1 up (won the 18th)
    18: dict(done=1, up=+3, res="3&2"),  # Conan v Conor -- Conan won 3&2 (Conan's shots won 7th, halved 15th)
    19: dict(done=1, up=+2, res="2&1"),  # Dom v Buff -- Dom won 2&1 (Buff won 14th-16th; Buff's shots halved 7th, won 12th and 15th)
    1:  dict(thru=16, up=0),   # Ger v Diarmuid King -- A/S thru 16 (Ger's shots won the 7th and 15th; Ger won 14th-16th)
    20: dict(thru=15, up=+1),  # Johnny McManus v Goof -- Johnny 1 up thru 15
    2:  dict(done=1, up=+4, res="4&3"),  # Shay v Jock -- Shay won 4&3
    13: dict(done=1, up=-6, res="6&4"),  # Jamie Teague v Ingy -- Ingy won 6&4
    8:  dict(done=1, up=-5, res="5&4"),  # Jonto v Sean McDermott -- Sean won 5&4
    10: dict(thru=14, up=+1),  # Ryan McDermott v Caolan Swift -- Ryan 1 up thru 14
    11: dict(thru=9, up=-2),   # Micky v Jimmy -- Jimmy 2 up thru 9
}

# player name (exactly as in M) -> dict(thru=holes played, pts=net Stableford points so far),
# computed off each player's full handicap on the Yellow stroke index. Missing = no card yet.
LIVE_SF = {
    'Govy':              dict(thru=18, pts=29),   # scratched 10th
    'Johnny McCafferty': dict(thru=18, pts=29),   # scratched 1st, 5th
    'Fintan Flynn':      dict(thru=18, pts=34),
    'Ray McCarron':      dict(thru=18, pts=32),   # scratched 5th, 6th
    'Frank':             dict(thru=18, pts=35),
    'Marty':             dict(thru=18, pts=34),
    'Ronnie Flanagan':   dict(thru=12, pts=8),   # scratched 1-3, 6, 8-10
    'Seamus McKiernan':  dict(thru=12, pts=26),
    'Lochlann':          dict(thru=18, pts=35),   # scratched 15th
    'Leo':               dict(thru=18, pts=35),
    'Conan':             dict(thru=18, pts=19),
    'Conor':             dict(thru=18, pts=22),   # scratched 17th
    'Dom':               dict(thru=18, pts=17),
    'Buff':              dict(thru=18, pts=6),
    'Ger':               dict(thru=16, pts=28),
    'Diarmuid King':     dict(thru=16, pts=27),
    'Johnny McManus':    dict(thru=15, pts=19),
    'Goof':              dict(thru=15, pts=19),
    'Shay':              dict(thru=18, pts=37),
    'Jock':              dict(thru=18, pts=31),
    'Jamie Teague':      dict(thru=16, pts=10),
    'Ingy':              dict(thru=16, pts=20),
    'Jonto':             dict(thru=14, pts=13),   # scratched 5th, 12th
    'Sean McDermott':    dict(thru=14, pts=20),   # scratched 7th
    'Ryan McDermott':    dict(thru=14, pts=19),
    'Caolan Swift':      dict(thru=14, pts=23),
    'Micky':             dict(thru=9, pts=9),
    'Jimmy':             dict(thru=9, pts=17),
    'Brendy':            dict(thru=18, pts=32),
    'Raymond McGloin':   dict(thru=18, pts=28),
    'Jamie McCaffrey':   dict(thru=18, pts=27),
    'Blobby':            dict(thru=18, pts=26),
    'Kealan':            dict(thru=18, pts=23),   # scratched 6th, 15th
    'Mully':             dict(thru=18, pts=26),
    'Hugo':              dict(thru=18, pts=17),
    'Collie':            dict(thru=18, pts=18),
    'Rusty':             dict(thru=18, pts=19),
    'Sean Conlon':       dict(thru=18, pts=19),
    'Ben Caughey':       dict(thru=18, pts=35),
    'Andy':              dict(thru=18, pts=23),
}

if LIVE_ON:
    build('live', os.path.join(ROOT, 'live.html'), False, results=LIVE_RESULTS, sf=LIVE_SF, reports=LIVE_REPORTS)
else:
    build('pre',  os.path.join(ROOT, 'live.html'), False)
build('live', os.path.join(ROOT, 'mock.html'), True, reports=MOCK_REPORTS)
