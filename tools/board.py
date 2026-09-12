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

def cup_rows(mode, results=None):
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
        rows.append(
f'''    <li class="row">
      <div class="side side--h{hcls}"><span class="marg">{hmarg}</span><span class="nm">{e(hn)}</span></div>
      <div class="mid"><span class="mno">{no}</span>{mid}</div>
      <div class="side side--a{acls}"><span class="nm">{e(an)}</span><span class="marg">{amarg}</span></div>
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

def build(mode, out, mock, results=None, sf=None, when=None):
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
{cup_rows(mode, results)}
</ul>
{cupnote}

{sf_html}
'''
    HTML += SORT_JS
    open(out,'w',encoding='utf-8').write(HTML)
    print(f"{out}  mode={mode} mock={mock}  EUR {frac(pe)} v USA {frac(pa)}  {len(HTML)} bytes")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- day-of controls: flip LIVE_ON to True on the first card, edit LIVE_RESULTS as cards come in ----
LIVE_ON = True
# RULE (agreed on the day): each hole is decided by the players' Stableford points for
# that hole, off full handicap on the Yellow stroke index. Higher points wins the hole,
# equal points halves it. up > 0 Europe ahead, up < 0 USA ahead, 0 all square.
# match no -> dict(thru=N, up=U) in progress, or dict(done=1, up=U, res="3&2") finished.
LIVE_RESULTS = {
    9:  dict(thru=7, up=+2),   # Govy v Johnny McCafferty -- Govy 2 up thru 7
    5:  dict(thru=6, up=+1),   # Brendy v Raymond McGloin -- Brendy 1 up thru 6
    7:  dict(thru=6, up=0),    # Jamie McCaffrey v Blobby -- A/S thru 6
    14: dict(thru=6, up=-1),   # Kealan v Mully -- Mully 1 up thru 6
    16: dict(thru=4, up=-3),   # Hugo v Collie -- Collie 3 up thru 4
    15: dict(thru=6, up=0),    # Rusty v Sean Conlon -- A/S thru 6
    12: dict(thru=6, up=+1),   # Ben Caughey v Andy -- Ben 1 up thru 6
    6:  dict(thru=6, up=+2),   # Fintan Flynn v Ray McCarron -- Fintan 2 up thru 6
    4:  dict(thru=4, up=+2),   # Frank v Marty -- Frank 2 up thru 4
    17: dict(thru=6, up=-4),   # Ronnie Flanagan v Seamus McKiernan -- Seamus 4 up thru 6
    3:  dict(thru=3, up=0),    # Lochlann v Leo -- A/S thru 3
    18: dict(thru=3, up=+1),   # Conan v Conor -- Conan 1 up thru 3
    19: dict(thru=3, up=0),    # Dom v Buff -- A/S thru 3
    1:  dict(thru=2, up=-1),   # Ger v Diarmuid King -- Diarmuid 1 up thru 2
    20: dict(thru=2, up=0),    # Johnny McManus v Goof -- A/S thru 2
    2:  dict(thru=3, up=+2),   # Shay v Jock -- Shay 2 up thru 3
    13: dict(thru=2, up=0),    # Jamie Teague v Ingy -- A/S thru 2
    8:  dict(thru=2, up=+1),   # Jonto v Sean McDermott -- Jonto 1 up thru 2
}

# player name (exactly as in M) -> dict(thru=holes played, pts=net Stableford points so far),
# computed off each player's full handicap on the Yellow stroke index. Missing = no card yet.
LIVE_SF = {
    'Govy':              dict(thru=7, pts=12),
    'Johnny McCafferty': dict(thru=7, pts=10),  # scratched the 1st and 5th; net eagle 7th
    'Fintan Flynn':      dict(thru=6, pts=12),
    'Ray McCarron':      dict(thru=6, pts=7),   # scratched 5th, 6th
    'Frank':             dict(thru=4, pts=9),
    'Marty':             dict(thru=4, pts=7),
    'Ronnie Flanagan':   dict(thru=6, pts=4),   # scratched 1st-3rd and 6th
    'Seamus McKiernan':  dict(thru=6, pts=14),
    'Lochlann':          dict(thru=3, pts=7),
    'Leo':               dict(thru=3, pts=7),
    'Conan':             dict(thru=3, pts=3),
    'Conor':             dict(thru=3, pts=2),
    'Dom':               dict(thru=3, pts=5),
    'Buff':              dict(thru=3, pts=3),
    'Ger':               dict(thru=2, pts=3),
    'Diarmuid King':     dict(thru=2, pts=4),
    'Johnny McManus':    dict(thru=2, pts=3),
    'Goof':              dict(thru=2, pts=3),
    'Shay':              dict(thru=3, pts=9),
    'Jock':              dict(thru=3, pts=5),
    'Jamie Teague':      dict(thru=2, pts=2),
    'Ingy':              dict(thru=2, pts=3),
    'Jonto':             dict(thru=2, pts=1),
    'Sean McDermott':    dict(thru=2, pts=0),
    'Brendy':            dict(thru=6, pts=11),
    'Raymond McGloin':   dict(thru=6, pts=10),
    'Jamie McCaffrey':   dict(thru=6, pts=8),
    'Blobby':            dict(thru=6, pts=8),
    'Kealan':            dict(thru=6, pts=6),   # scratched 6th
    'Mully':             dict(thru=6, pts=7),
    'Hugo':              dict(thru=4, pts=3),
    'Collie':            dict(thru=4, pts=7),
    'Rusty':             dict(thru=6, pts=6),
    'Sean Conlon':       dict(thru=6, pts=6),
    'Ben Caughey':       dict(thru=6, pts=13),
    'Andy':              dict(thru=6, pts=8),
}

if LIVE_ON:
    build('live', os.path.join(ROOT, 'live.html'), False, results=LIVE_RESULTS, sf=LIVE_SF)
else:
    build('pre',  os.path.join(ROOT, 'live.html'), False)
build('live', os.path.join(ROOT, 'mock.html'), True)
