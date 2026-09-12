#!/usr/bin/env python3
"""End-of-day report for Captain's Day. Reads the match list and the day-of state from
board.py (M, LIVE_RESULTS, LIVE_SF) and writes report.html. While matches are still out it
is a projection; once every match is in it becomes the final report."""
import html, os, re, sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(ROOT, 'tools', 'board.py')).read()
NOW = datetime.now(ZoneInfo('Europe/Dublin'))
e = html.escape

def stamp():
    d = NOW.day
    suf = 'th' if 11 <= d % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')
    return NOW.strftime('%A, %B ') + f'{d}{suf} &middot; ' + NOW.strftime('%I:%M %p').lstrip('0')

# ---- data from board.py -------------------------------------------------------------
M = [(t, int(n), a, int(ah), int(ag), b, int(bh), int(bg)) for t, n, a, ah, ag, b, bh, bg in
     re.findall(r'^\s*\("(\d+:\d+)",\s*(\d+),\s*"([^"]+)",(\d+),(\d),\s*"([^"]+)",(\d+),(\d),', SRC, flags=re.M)]
R = {}
for no, body in re.findall(r"^    (\d+): +dict\((.*?)\),", SRC, flags=re.M):
    d = {}
    for k, v in re.findall(r'(\w+)=("?[^,"]+"?)', body):
        d[k] = v.strip('"') if v.startswith('"') else int(v)
    R[int(no)] = d
SF = {n: dict(thru=int(t), pts=int(p)) for n, t, p in
      re.findall(r"^    '([^']+)':\s*dict\(thru=(\d+), pts=(\d+)\)", SRC, flags=re.M)}
GUEST = {a for _, _, a, _, ag, _, _, _ in M if ag} | {b for _, _, _, _, _, b, _, bg in M if bg}

# Shots that decided a hole today (match, hole, who, what) -- kept by hand from the cards.
SHOTS = [
    (12, 7, 'Ben Caughey', 'won it'), (16, 7, 'Collie', 'halved it'), (4, 7, 'Frank', 'halved it'),
    (17, 7, 'Ronnie Flanagan', 'halved it'), (14, 8, 'Kealan', 'won it'),
    (9, 12, 'Johnny McCafferty', 'won it and took the lead'), (3, 7, 'Lochlann', 'won it'),
    (14, 12, 'Kealan', 'won it'), (19, 7, 'Buff', 'halved it'), (1, 7, 'Ger', 'won it'),
    (6, 12, 'Ray McCarron', 'won it'), (2, 7, 'Shay', 'won it'), (9, 15, 'Johnny McCafferty', 'halved it'),
    (5, 15, 'Brendy', 'halved it'), (16, 12, 'Collie', 'won it'), (18, 7, 'Conan', 'won it'),
    (6, 15, 'Ray McCarron', 'halved it'), (19, 12, 'Buff', 'won it'), (17, 12, 'Ronnie Flanagan', 'halved it'),
]

# ---- scoring -------------------------------------------------------------------------
def frac(x):
    w = int(x); h = x - w
    return (str(w) if w else '') + ('&frac12;' if h else '') if h else str(w)

eu_bank = us_bank = 0.0; eu_proj = us_proj = 0.0
done_n = 0
rows = []
for tee, no, a, ah, ag, b, bh, bg in M:
    st = R.get(no)
    if not st:
        rows.append(dict(no=no, a=a, b=b, state='tee', text=f'Not reported', cls='')); continue
    up = st['up']
    if st.get('done'):
        done_n += 1
        if up > 0: eu_bank += 1; who = 'a'; text = f'{a} won {st["res"]}'
        elif up < 0: us_bank += 1; who = 'b'; text = f'{b} won {st["res"]}'
        else: eu_bank += 0.5; us_bank += 0.5; who = ''; text = 'Halved'
        rows.append(dict(no=no, a=a, b=b, state='done', who=who, text=text))
    else:
        thru = st['thru']; left = 18 - thru
        if up > 0: eu_proj += 1; who = 'a'; lead = f'{a} {abs(up)} up'
        elif up < 0: us_proj += 1; who = 'b'; lead = f'{b} {abs(up)} up'
        else: eu_proj += 0.5; us_proj += 0.5; who = ''; lead = 'All square'
        dormie = up and abs(up) == left
        text = f'{lead} thru {thru}' + (' &middot; dormie' if dormie else '')
        rows.append(dict(no=no, a=a, b=b, state='live', who=who, text=text))
eu_tot = eu_bank + eu_proj; us_tot = us_bank + us_proj
out_n = len(M) - done_n
final = out_n == 0

ps = [dict(name=n, thru=v['thru'], pts=v['pts'], guest=n in GUEST) for n, v in SF.items()]
for p in ps: p['proj'] = round(p['pts'] * 18 / p['thru']) if p['thru'] else 0
ps.sort(key=lambda p: (-p['proj'], -p['pts'], p['name']))
members = [p for p in ps if not p['guest']]
medals = members[:3]; spoon = members[-1] if members else None
guests_top = [p for p in ps if p['guest']][:3]
complete = sum(1 for p in ps if p['thru'] == 18)

def result_word():
    if eu_tot > us_tot: return 'Europe'
    if us_tot > eu_tot: return 'USA'
    return 'Tie'

# ---- page ----------------------------------------------------------------------------
CSS = '''
:root { --paper:#f9fafd; --sunk:#e8ebf8; --ink:#12163c; --soft:#5b6080; --hair:#d3d8f0; --navy:#060545;
  --home:#1340d0; --away:#e31112; --gold:#e0bd28; --live:#e31112;
  --display:"Barlow Condensed","Arial Narrow",sans-serif; --body:"Source Sans 3",system-ui,-apple-system,sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --paper:#0a0c24; --sunk:#12163a; --ink:#e8eaf6;
  --soft:#9aa0c4; --hair:#23274f; --home:#5a86f5; --away:#ee4a50; --live:#ee4a50; } }
:root[data-theme="dark"] { --paper:#0a0c24; --sunk:#12163a; --ink:#e8eaf6; --soft:#9aa0c4; --hair:#23274f;
  --home:#5a86f5; --away:#ee4a50; --live:#ee4a50; }
* { box-sizing:border-box; } html,body { margin:0; padding:0; }
body { background:var(--paper); color:var(--ink); font-family:var(--body); line-height:1.45; margin:0 auto; max-width:34rem; padding:0 0 3rem; }
h1,h2,h3 { font-family:var(--display); margin:0; text-transform:uppercase; } p { margin:0; } ul,ol { list-style:none; margin:0; padding:0; }
.back { align-items:center; color:var(--home); display:inline-flex; font-family:var(--display); font-size:0.8rem; font-weight:600; gap:0.25rem;
  letter-spacing:0.06em; margin:0.55rem 0 0 1rem; text-decoration:none; text-transform:uppercase; }
.back:hover { text-decoration:underline; }
.top { padding:1.1rem 1rem 0.75rem; text-align:center; }
.top h1 { font-size:1.8rem; font-weight:700; letter-spacing:0.08em; line-height:1.1; }
.top .sub { color:var(--soft); font-family:var(--display); font-size:0.82rem; letter-spacing:0.09em; text-transform:uppercase; }
.stamp { align-items:center; display:inline-flex; flex-wrap:wrap; gap:0.35rem; justify-content:center; margin-top:0.3rem; }
.stamp span { color:var(--soft); font-family:var(--display); font-size:0.78rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; }
.proj { background:var(--gold); color:var(--navy); font-family:var(--display); font-size:0.8rem; font-weight:600; letter-spacing:0.12em;
  padding:0.5rem 1rem; text-align:center; text-transform:uppercase; }
.hero { background:linear-gradient(100deg,#123bbd 0%,#0b1a5e 42%,#0b1a5e 58%,#c11418 100%); color:#fff; padding:0.9rem 1rem 1rem; }
.hs { align-items:center; display:grid; gap:0.5rem; grid-template-columns:1fr auto 1fr; }
.hs__t { font-family:var(--display); font-size:1.35rem; font-weight:700; letter-spacing:0.06em; line-height:1; text-transform:uppercase; }
.hs__t.eu { color:#dbe4ff; } .hs__t.us { color:#ffd9d9; text-align:right; }
.hs__n { font-family:var(--display); font-variant-numeric:tabular-nums; font-weight:700; font-size:3rem; line-height:0.85; margin-top:0.2rem; }
.hs__n.us { text-align:right; } .hs__dash { color:rgba(255,255,255,0.4); font-family:var(--display); font-size:1.6rem; font-weight:600; }
.cap { color:rgba(255,255,255,0.8); font-size:0.76rem; margin-top:0.55rem; text-align:center; } .cap b { color:var(--gold); font-weight:700; }
.head { align-items:baseline; display:flex; gap:0.6rem; justify-content:space-between; padding:1.8rem 1rem 0.5rem; }
.head h2 { font-size:1.3rem; font-weight:700; letter-spacing:0.05em; }
.head p { color:var(--soft); font-family:var(--display); font-size:0.8rem; letter-spacing:0.08em; text-align:right; text-transform:uppercase; }
.lede { padding:0 1rem; font-size:0.95rem; } .lede + .lede { margin-top:0.6rem; }
.lede b { font-weight:700; }
.mt { border-top:1px solid var(--hair); }
.mr { border-bottom:1px solid var(--hair); display:grid; grid-template-columns:3.2rem 1fr; align-items:center; padding:0.4rem 1rem; gap:0.5rem; font-size:0.9rem; }
.mr .no { color:var(--soft); font-family:var(--display); font-size:0.66rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; }
.mr .who { display:flex; flex-wrap:wrap; gap:0.2rem 0.5rem; align-items:baseline; }
.mr .nm { font-weight:600; } .mr .v { color:var(--soft); font-size:0.8rem; }
.mr .res { color:var(--soft); font-family:var(--display); font-size:0.78rem; font-weight:600; letter-spacing:0.04em; text-transform:uppercase; width:100%; }
.mr.eu .res { color:var(--home); } .mr.us .res { color:var(--away); } .mr.half .res { color:#a9871a; }
.mr.live .res::before { content:"\\25B8 "; }
.pod { display:grid; gap:0.5rem; grid-template-columns:repeat(3,1fr); padding:0 1rem; }
.pd { background:var(--sunk); border-radius:8px; padding:0.7rem 0.6rem; text-align:center; }
.pd .m { font-family:var(--display); font-size:0.7rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:var(--soft); }
.pd .n { font-weight:700; font-size:0.95rem; margin-top:0.15rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.pd .s { color:var(--soft); font-size:0.78rem; } .pd .s b { color:var(--ink); }
.pd--1 { background:rgba(224,189,40,0.28); } .pd--spoon { background:rgba(224,189,40,0.12); margin:0.5rem 1rem 0; }
.li { padding:0 1rem; } .li li { border-bottom:1px solid var(--hair); font-size:0.88rem; padding:0.4rem 0; display:flex; gap:0.6rem; }
.li .h { color:var(--soft); font-family:var(--display); font-size:0.7rem; font-weight:600; letter-spacing:0.06em; text-transform:uppercase; flex:0 0 5.2rem; padding-top:0.15rem; }
.note { color:var(--soft); font-size:0.82rem; padding:0.8rem 1rem 0; } .note b { color:var(--ink); font-weight:600; }
'''

def hero():
    lead = 'Europe' if eu_tot > us_tot else ('USA' if us_tot > eu_tot else 'Level')
    cap = (f'Final &middot; <b>{frac(eu_bank)}</b> &ndash; <b>{frac(us_bank)}</b> from 20 matches'
           if final else
           f'<b>{frac(eu_bank)}</b> &ndash; <b>{frac(us_bank)}</b> banked from {done_n} matches &middot; {out_n} still out, counted at their current standing')
    return f'''<div class="hero">
<div class="hs"><div><div class="hs__t eu">Europe</div><div class="hs__n">{frac(eu_tot)}</div></div>
<div class="hs__dash">&ndash;</div>
<div><div class="hs__t us">USA</div><div class="hs__n us">{frac(us_tot)}</div></div></div>
<p class="cap">{cap}</p></div>'''

def match_rows():
    out = []
    for r in sorted(rows, key=lambda r: r['no']):
        cls = r['state'] + (' eu' if r.get('who') == 'a' else ' us' if r.get('who') == 'b' else ' half' if r['state'] != 'tee' else '')
        out.append(f'<li class="mr {cls}"><span class="no">Match {r["no"]}</span><span class="who">'
                   f'<span class="nm">{e(r["a"])}</span><span class="v">v</span><span class="nm">{e(r["b"])}</span>'
                   f'<span class="res">{r["text"]}</span></span></li>')
    return '<ol class="mt">' + ''.join(out) + '</ol>'

def podium():
    lab = ['Gold', 'Silver', 'Bronze']
    cards = []
    for i, p in enumerate(medals):
        s = f'<b>{p["pts"]}</b> pts' + ('' if p['thru'] == 18 else f' thru {p["thru"]} &middot; proj {p["proj"]}')
        cards.append(f'<div class="pd pd--{i+1}"><div class="m">{lab[i]}</div><div class="n">{e(p["name"])}</div><div class="s">{s}</div></div>')
    sp = ''
    if spoon:
        s = f'<b>{spoon["pts"]}</b> pts' + ('' if spoon['thru'] == 18 else f' thru {spoon["thru"]} &middot; proj {spoon["proj"]}')
        sp = f'<div class="pd pd--spoon"><div class="m">Wooden Spoon &#x1F944;</div><div class="n">{e(spoon["name"])}</div><div class="s">{s}</div></div>'
    g = ', '.join(f'{e(p["name"])} {p["pts"]}' + ('' if p['thru'] == 18 else f' thru {p["thru"]}') for p in guests_top)
    return f'<div class="pod">{"".join(cards)}</div>{sp}<p class="note">Medals and the spoon are for members. Best of the guests: {g}.</p>'

def shots():
    byno = {no: (a, b) for _, no, a, _, _, b, _, _ in M}
    items = ''.join(f'<li><span class="h">M{no} &middot; {h}th</span><span>{e(who)}&rsquo;s shot {what}.</span></li>'
                    for no, h, who, what in SHOTS)
    return f'<ul class="li">{items}</ul><p class="note"><b>{len(SHOTS)}</b> holes so far decided by a handicap shot. The 7th, stroke index 2, accounts for {sum(1 for x in SHOTS if x[1]==7)} of them.</p>'

lede1 = (f'<p class="lede"><b>{result_word()}</b> ' + ('win the Cup' if final else 'lead the projection') +
         f' <b>{frac(eu_tot)} &ndash; {frac(us_tot)}</b>. ' +
         (f'{done_n} matches are in and {out_n} are still on the course; each of those is counted at its current standing, with all-square matches split.' if not final else
          'Every match is in.') + '</p>')
close_n = sum(1 for no, st in R.items() if not st.get('done') and abs(st['up']) <= 1)
sq_n = sum(1 for no, st in R.items() if not st.get('done') and st['up'] == 0)
lede2 = (f'<p class="lede">{close_n} matches are within a hole and {sq_n} are all square, so the number above will move. '
         'A projection is not a result: a match that is one up with three to play is a point on this page and nothing on the day.</p>') if not final else ''

page = f'''<title>Captain&rsquo;s Day &mdash; Report</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Sans+3:wght@400;600;700&display=swap">
<style>{CSS}</style>
<a class="back" href="/live">&larr; Live board</a>
<div class="top"><h1>Captain&rsquo;s Day &mdash; {'Report' if final else 'Projected Report'}</h1>
<p class="sub">Mulligan&rsquo;s Bar Golf Society &middot; Clones GC</p>
<p class="stamp"><span>{'Final' if final else 'Projection'}</span><span>&middot;</span><span>{stamp()}</span></p></div>
{'' if final else '<div class="proj">Projected &middot; matches still out are counted at their current standing</div>'}
{hero()}
<div class="head"><h2>The Cup</h2><p>{'Final' if final else 'As it stands'}</p></div>
{lede1}{lede2}
<div class="head"><h2>Every match</h2><p>{done_n} in &middot; {out_n} out</p></div>
{match_rows()}
<div class="head"><h2>The Stableford</h2><p>{complete} of {len(ps)} cards complete</p></div>
{podium()}
<div class="head"><h2>Where the shots mattered</h2><p>Stroke index at work</p></div>
{shots()}
<p class="note">Generated from the live board data. Re-run <b>tools/report.py</b> when the last card is in and this page becomes the final report.</p>
'''
open(os.path.join(ROOT, 'report.html'), 'w').write(page)
print('report.html', 'FINAL' if final else 'PROJECTED', frac(eu_tot), frac(us_tot), 'medals', [p['name'] for p in medals], 'spoon', spoon and spoon['name'])
