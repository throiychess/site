"""ThroiyChess website generator.
python build.py  ->  dist/ (full site for GitHub Pages)  +  preview/ (same site, index without skeleton for a Claude preview)
Add a trap: append to TRAPS (moves + notes per ply), rebuild, push dist/."""
import os, sys, json, shutil, html
sys.path.insert(0, "/home/claude/ext/python-chess")
import chess

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "throiychess.com"
LINKS = [("YouTube", "https://www.youtube.com/@ThroiyChess"), ("TikTok", "https://www.tiktok.com/@throiychess"),
         ("Instagram", "https://www.instagram.com/throiychess")]

TRAPS = [
    dict(slug="fishing-pole-trap", name="Fishing Pole Trap", opening="Ruy Lopez", side="Black sets it",
         hook="Black leaves a knight hanging on g4. Take it, and the h-file opens straight onto your king.",
         moves="e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Ng4 h3 h5 hxg4 hxg4 Nh2 Qh4 f3 g3 Rf2 Nd4 Kf1 gxh2 Ke1 h1=Q+ Bf1 Qxf1+ Kxf1 Qh1#",
         video="https://www.youtube.com/@ThroiyChess/shorts",
         notes={0: ("START", "", "The Fishing Pole starts from a normal Ruy Lopez. Step through the moves."),
                6: ("OPENING", "3…Nf6", "A normal Ruy Lopez. Nothing special yet."),
                7: ("OPENING", "4.O-O", "White castles. The king goes to g1."),
                8: ("OPENING", "4…Ng4", "Black's knight jumps to g4. It looks silly, and that is the point."),
                9: ("FIRST MISTAKE", "5.h3?", "White kicks the knight. Pushing this pawn weakens the king's cover.", ["h3"]),
                10: ("THE BAIT", "5…h5!", "Black ignores the threat and leaves the knight. That's the bait.", ["!g4"]),
                11: ("THE BLUNDER", "6.hxg4??", "A free knight? Taking it is the real blunder.", ["!g4"]),
                12: ("THE OPEN FILE", "6…hxg4", "The h-file is open. The rook on h8 now aims at the king.", ["h8", "!g1"]),
                13: ("THE OPEN FILE", "7.Nh2", "The knight runs away from g4's pawn."),
                14: ("MATE THREAT", "7…Qh4!", "Queen and rook are lined up on the h-file. Qh1 mate is coming.", ["h4", "h8"]),
                15: ("MATE THREAT", "8.f3", "White makes room so the king can escape via f2."),
                16: ("MATE THREAT", "8…g3!", "g3 locks the king in. Now only Rf2 or Re1 stop mate in one, and they only delay it.", ["g3", "!g1"]),
                17: ("NO WAY OUT", "9.Rf2", "The rook covers f2. Black keeps piling on."),
                26: ("CHECKMATE", "13…Qh1#", "The king tried to run, but the attack is too strong. Checkmate on h1.", ["!f1", "h1"])},
         fix=["Don't push the h-pawn when the knight lands on g4. h3 is the first mistake.",
              "Your king hides behind f2, g2 and h2. Keep them home and keep developing.",
              "If the knight is left hanging after …h5, don't take it. The open h-file is worth more than a knight.",
              "As Black it is a cheeky blitz trick. It only works if they bite, so don't count on it."]),
]
OTHER = [("Petrov Trap", "Petrov Defense", "Copying White's moves costs Black the queen. Play 3…d6 first.", "https://www.youtube.com/shorts/KA_x11CO7Gg"),
         ("Fried Liver Attack", "Italian Game", "White sacrifices a knight on f7 and drags the king into the open.", "https://www.youtube.com/@ThroiyChess/shorts")]

CSS = """
:root{--bg:#0e0d0b;--panel:#17150f;--line:#2c271d;--ink:#efe8d8;--mute:#a59a83;--gold:#e3c073;--gold-deep:#b8964d;--red:#e2442f;
--sq-l:#c4ac80;--sq-d:#7e6542;--display:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;--body:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.6;margin:0}
a{color:var(--gold)}
a:focus-visible,button:focus-visible{outline:2px solid var(--gold);outline-offset:3px}
.wrap{max-width:1080px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header.top{border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-block:14px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:800;letter-spacing:.02em}
.brand img{height:38px;width:auto}
.brand b{color:var(--gold);font-weight:600;letter-spacing:.32em;font-size:12px;display:block;line-height:1}
nav.links{display:flex;gap:18px;flex-wrap:wrap}
nav.links a{color:var(--mute);text-decoration:none;font-size:14px;font-weight:600;letter-spacing:.06em;text-transform:uppercase}
nav.links a:hover{color:var(--gold)}
.eyebrow{font-size:13px;font-weight:600;letter-spacing:.24em;text-transform:uppercase;color:var(--gold)}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0}
h1{font-weight:900;font-size:clamp(40px,7vw,76px);line-height:1;letter-spacing:-.025em;text-transform:uppercase}
h1 em{font-style:normal;color:var(--gold)}
h2{font-weight:800;font-size:clamp(26px,3.4vw,36px);line-height:1.1;letter-spacing:-.01em}
h3{font-weight:800;font-size:21px;line-height:1.2}
.lead{color:var(--mute);font-size:19px;max-width:34ch}
.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:48px;align-items:center;padding-block:64px 56px}
.hero>*{min-width:0}
.hero .copy{display:grid;gap:22px;justify-items:start}
.ticks{position:relative;padding:12px}
.ticks::before,.ticks::after,.ticks>.t1,.ticks>.t2{content:"";position:absolute;width:34px;height:34px;border-color:var(--gold);border-style:solid;pointer-events:none}
.ticks::before{left:0;top:0;border-width:4px 0 0 4px}.ticks::after{right:0;top:0;border-width:4px 4px 0 0}
.ticks>.t1{left:0;bottom:0;border-width:0 0 4px 4px}.ticks>.t2{right:0;bottom:0;border-width:0 4px 4px 0}
.ticks img{display:block;width:100%;height:auto}
.btns{display:flex;gap:10px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;padding:11px 18px;font-weight:700;font-size:15px;text-decoration:none;border:1px solid var(--gold);color:var(--gold);letter-spacing:.03em}
.btn.solid{background:var(--gold);color:#14110b}
.btn:hover{filter:brightness(1.1)}
section{padding-block:56px;border-top:1px solid var(--line)}
.sechead{display:flex;justify-content:space-between;align-items:end;gap:16px;flex-wrap:wrap;margin-bottom:28px}
.sechead p{color:var(--mute);margin:6px 0 0;max-width:52ch}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.card{background:var(--panel);border-left:4px solid var(--gold);padding:22px 22px 20px;display:grid;gap:10px;align-content:start;text-decoration:none;color:var(--ink);min-width:0}
.card .meta{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.tag{background:var(--gold);color:#14110b;font-weight:900;font-size:12px;padding:3px 8px;letter-spacing:.04em}
.label{font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--mute)}
.card p{margin:0;color:var(--mute);font-size:15.5px}
.card .go{font-weight:700;font-size:14px;color:var(--gold);margin-top:4px}
a.card:hover{background:#1d1a13}
.card.soon{border-left-color:var(--line)}
.breaking{display:grid;grid-template-columns:auto 1fr;gap:28px;align-items:center;background:var(--panel);padding:28px}
.breaking>*{min-width:0}
.live{font-weight:900;font-size:13px;letter-spacing:.2em;color:var(--bg);background:var(--red);padding:6px 10px;text-transform:uppercase;white-space:nowrap}
.breaking p{margin:6px 0 0;color:var(--mute)}
.about{display:grid;grid-template-columns:200px 1fr;gap:32px;align-items:center}
.about>*{min-width:0}
.about img{width:200px;max-width:100%;height:auto}
.about p{max-width:60ch;color:var(--mute);margin:10px 0 0}
footer{border-top:1px solid var(--line);padding-block:28px;color:var(--mute);font-size:14px}
footer .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
/* trap page */
.crumb{font-size:14px;color:var(--mute);padding-top:28px}
.crumb a{color:var(--mute)}
.traphead{display:grid;gap:14px;padding-block:18px 30px}
.traphead p{color:var(--mute);margin:0;max-width:60ch;font-size:19px}
.player{display:grid;grid-template-columns:minmax(0,560px) minmax(0,1fr);gap:36px;align-items:start}
.player>*{min-width:0}
.board{display:grid;grid-template-columns:repeat(8,1fr);aspect-ratio:1;width:100%;max-width:100%;position:relative;user-select:none}
.sq{position:relative;aspect-ratio:1}
.sq.l{background:var(--sq-l)}.sq.d{background:var(--sq-d)}
.sq.hl::before{content:"";position:absolute;inset:0;background:rgba(240,200,90,.42)}
.sq.mk::after{content:"";position:absolute;inset:6%;border-radius:50%;border:4px solid #fff;box-shadow:0 0 0 3px #14120f,inset 0 0 0 2px #14120f}
.sq.mk.red::after{border-color:var(--red);box-shadow:0 0 0 3px #fff}
.sq img{position:absolute;inset:2%;width:96%;height:96%;z-index:1}
.sq .co{position:absolute;font-size:11px;font-weight:700;z-index:2;line-height:1}
.sq .rk{left:3px;top:3px}.sq .fl{right:3px;bottom:2px}
.sq.l .co{color:var(--sq-d)}.sq.d .co{color:var(--sq-l)}
.ctrl{display:flex;gap:8px;margin-top:14px}
.ctrl button{flex:1;background:var(--panel);color:var(--ink);border:1px solid var(--line);padding:10px 0;font-size:16px;font-weight:700;cursor:pointer;font-family:var(--body)}
.ctrl button:hover{border-color:var(--gold);color:var(--gold)}
.note{background:var(--panel);border-top:4px solid var(--gold);padding:22px;display:grid;gap:10px}
.note .meta{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.note p{margin:0;font-size:19px;line-height:1.45;font-weight:600}
.moves{display:flex;flex-wrap:wrap;gap:4px 2px;margin-top:20px;font-variant-numeric:tabular-nums;font-size:15px}
.moves button{background:none;border:0;color:var(--mute);font:inherit;padding:3px 6px;cursor:pointer}
.moves button.on{background:var(--gold);color:#14110b;font-weight:800}
.moves span{color:#6f6656;padding:3px 0 3px 6px}
.fix{display:grid;gap:14px;padding:0;margin:0;list-style:none;counter-reset:f}
.fix li{display:grid;grid-template-columns:28px 1fr;gap:12px;max-width:70ch}
.fix li::before{counter-increment:f;content:counter(f);font-weight:900;color:var(--gold);font-size:20px;line-height:1.4}
.hint{color:var(--mute);font-size:14px;margin-top:10px}
@media (max-width:860px){.hero,.player{grid-template-columns:1fr}.grid{grid-template-columns:1fr}.hero{padding-block:36px}.breaking{grid-template-columns:1fr;gap:14px}.about{grid-template-columns:1fr}.about img{width:140px}}
@media (prefers-reduced-motion:no-preference){.btn,.card{transition:background .15s,filter .15s}}
"""
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap">'
e = html.escape

def page(title, desc, body, rel, full=True):
    head = (f'<title>{e(title)}</title><meta name="claude:viewport-fit-sides" content="cover">'
            f'<meta name="description" content="{e(desc)}"><link rel="icon" href="{rel}img/favicon.png">'
            f'<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">'
            f'<meta property="og:image" content="https://{DOMAIN}/img/fishing-pole-board.jpg">{FONTS}<style>{CSS}</style>')
    if not full: return head + body
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'{head}</head><body>{body}</body></html>')

def header(rel):
    return (f'<header class="top"><div class="wrap"><a class="brand" href="{rel}index.html"><img src="{rel}img/logo-small.png" alt="">'
            f'<span>THROIY<b>CHESS</b></span></a><nav class="links"><a href="{rel}index.html#traps">Traps</a><a href="{rel}index.html#top-games">Top games</a>'
            + "".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in LINKS) + '</nav></div></header>')

def footer():
    return ('<footer><div class="wrap"><span>© ThroiyChess · Quick chess lessons, every day</span><span>'
            + " · ".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in LINKS) + '</span></div></footer>')

def home(full):
    cards = "".join(
        f'<a class="card" href="traps/{t["slug"]}/index.html"><div class="meta"><span class="label">{e(t["opening"])}</span></div>'
        f'<h3>{e(t["name"])}</h3><p>{e(t["hook"])}</p><span class="go">Play through the trap →</span></a>' for t in TRAPS)
    cards += "".join(
        f'<a class="card soon" href="{u}" target="_blank" rel="noopener"><div class="meta"><span class="label">{e(o)}</span></div>'
        f'<h3>{e(n)}</h3><p>{e(h)}</p><span class="go">Watch the Short →</span></a>' for n, o, h, u in OTHER)
    body = header("") + f'''<main>
<div class="wrap hero"><div class="copy"><span class="eyebrow">Throiy Chess · Lessons &amp; Games</span>
<h1>Stop falling for <em>chess traps.</em></h1>
<p class="lead">Opening traps, mating patterns and the best moments from top games. Each one explained in under a minute.</p>
<div class="btns"><a class="btn solid" href="{LINKS[0][1]}" target="_blank" rel="noopener">Watch on YouTube</a><a class="btn" href="#traps">Browse the traps</a></div></div>
<div class="ticks"><img src="img/fishing-pole-board.jpg" width="720" height="720" alt="Final position of the Fishing Pole Trap: Black's queen mates on h1"><i class="t1"></i><i class="t2"></i></div></div>
<section id="traps"><div class="wrap"><div class="sechead"><div><span class="eyebrow">Trap library</span><h2>Learn the trap. Then learn the fix.</h2>
<p>Every trap ends with the mate. Every lesson ends with how to avoid it. Step through the moves on the board.</p></div></div>
<div class="grid">{cards}</div></div></section>
<section id="top-games"><div class="wrap"><div class="breaking"><span class="live">Top games</span><div><h3>Clutch Chess: Champions Showdown · 27–29 October</h3>
<p>Nakamura, Caruana, Praggnanandhaa and Sindarov play rapid chess. We break down the sharpest moment of each day in a Short.</p></div></div></div></section>
<section id="about"><div class="wrap about"><img src="img/avatar-thinking.png" width="200" height="200" alt="Throiy, illustrated, thinking about a move">
<div><span class="eyebrow">About</span><h2>Hi, I'm Throiy.</h2><p>I'm a chess player sharing what I wish I'd known sooner. Short, clear lessons you can use in your next game. A new one every day on YouTube, TikTok and Instagram.</p>
<div class="btns" style="margin-top:18px">''' + "".join(f'<a class="btn" href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in LINKS) + '''</div></div></div></section>
</main>''' + footer()
    return page("Throiy Chess", "Opening traps, mating patterns and top games, explained fast. A new chess lesson every day.", body, "", full)

def trap_page(t):
    b = chess.Board(); plies = [dict(fen=b.board_fen(), san="", fr=None, to=None)]
    for san in t["moves"].split():
        mv = b.parse_san(san); b.push(mv)
        plies.append(dict(fen=b.board_fen(), san=san, fr=chess.square_name(mv.from_square), to=chess.square_name(mv.to_square)))
    assert b.is_checkmate()
    notes = {k: dict(label=v[0], tag=v[1], text=v[2], marks=(v[3] if len(v) > 3 else [])) for k, v in t["notes"].items()}
    mv_html = ""
    for i, p in enumerate(plies[1:], 1):
        if i % 2: mv_html += f'<span>{(i + 1) // 2}.</span>'
        mv_html += f'<button type="button" data-p="{i}">{e(p["san"])}</button>'
    data = json.dumps(dict(plies=plies, notes=notes))
    fix = "".join(f"<li><span>{e(x)}</span></li>" for x in t["fix"])
    body = header("../../") + f'''<main class="wrap"><div class="crumb"><a href="../../index.html#traps">Trap library</a> / {e(t["name"])}</div>
<div class="traphead"><span class="eyebrow">{e(t["opening"])} · {e(t["side"])}</span><h1>{e(t["name"])}</h1><p>{e(t["hook"])}</p></div>
<div class="player"><div><div class="board" id="board" aria-label="Chess board"></div>
<div class="ctrl"><button type="button" id="first" aria-label="Start position">⏮</button><button type="button" id="prev" aria-label="Previous move">◀</button>
<button type="button" id="next" aria-label="Next move">▶</button><button type="button" id="last" aria-label="Final position">⏭</button></div>
<p class="hint">Tip: use the arrow keys.</p></div>
<div><div class="note" aria-live="polite"><div class="meta"><span class="label" id="nl"></span><span class="tag" id="nt"></span></div><p id="nx"></p></div>
<div class="moves" id="moves">{mv_html}</div>
<div class="btns" style="margin-top:24px"><a class="btn solid" href="{t["video"]}" target="_blank" rel="noopener">Watch the Short</a></div></div></div>
<section style="margin-top:56px"><span class="eyebrow">The fix</span><h2 style="margin:8px 0 22px">How not to fall for it</h2><ol class="fix">{fix}</ol></section>
</main>''' + footer() + '<script>const D=' + data + ''';
const P="../../img/pieces/",B=document.getElementById("board");let cur=0;
const sqs=[];for(let r=7;r>=0;r--)for(let f=0;f<8;f++){const d=document.createElement("div");const n="abcdefgh"[f]+(r+1);d.className="sq "+((r+f)%2?"l":"d");d.dataset.n=n;
if(f===0){const c=document.createElement("span");c.className="co rk";c.textContent=r+1;d.appendChild(c)}
if(r===0){const c=document.createElement("span");c.className="co fl";c.textContent="abcdefgh"[f];d.appendChild(c)}B.appendChild(d);sqs.push(d)}
function parse(fen){const m={};fen.split("/").forEach((row,i)=>{let f=0;for(const ch of row){if(/\\d/.test(ch))f+=+ch;else{m["abcdefgh"[f]+(8-i)]=ch;f++}}});return m}
function note(i){let k=i;while(k>=0&&!D.notes[k])k--;return D.notes[k]}
function show(i){cur=Math.max(0,Math.min(D.plies.length-1,i));const p=D.plies[cur],m=parse(p.fen),n=note(cur);const mk=(D.notes[cur]&&D.notes[cur].marks)||[];
sqs.forEach(d=>{const s=d.dataset.n;d.classList.toggle("hl",s===p.fr||s===p.to);d.classList.toggle("mk",mk.includes(s)||mk.includes("!"+s));d.classList.toggle("red",mk.includes("!"+s));
const old=d.querySelector("img");if(old)old.remove();const c=m[s];if(c){const im=document.createElement("img");im.alt=c;im.src=P+(c===c.toUpperCase()?"w":"b")+c.toLowerCase()+".png";d.appendChild(im)}});
document.getElementById("nl").textContent=n.label;const t=document.getElementById("nt");t.textContent=n.tag;t.hidden=!n.tag;document.getElementById("nx").textContent=n.text;
document.querySelectorAll("#moves button").forEach(b=>b.classList.toggle("on",+b.dataset.p===cur))}
document.getElementById("first").onclick=()=>show(0);document.getElementById("prev").onclick=()=>show(cur-1);
document.getElementById("next").onclick=()=>show(cur+1);document.getElementById("last").onclick=()=>show(D.plies.length-1);
document.getElementById("moves").onclick=e=>{const b=e.target.closest("button");if(b)show(+b.dataset.p)};
document.addEventListener("keydown",e=>{if(e.key==="ArrowRight")show(cur+1);if(e.key==="ArrowLeft")show(cur-1)});
show(0);</script>'''
    return page(f'{t["name"]} · Throiy Chess', t["hook"], body, "../../")

def build():
    for out, full in (("dist", True), ("preview", False)):
        d = os.path.join(ROOT, out); shutil.rmtree(d, ignore_errors=True); shutil.copytree(os.path.join(ROOT, "src"), d)
        open(os.path.join(d, "index.html"), "w").write(home(full))
        for t in TRAPS:
            os.makedirs(os.path.join(d, "traps", t["slug"]), exist_ok=True)
            open(os.path.join(d, "traps", t["slug"], "index.html"), "w").write(trap_page(t))
    open(os.path.join(ROOT, "dist", "CNAME"), "w").write(DOMAIN + "\n")
    open(os.path.join(ROOT, "dist", ".nojekyll"), "w").write("")
    print("built")

if __name__ == "__main__":
    build()
