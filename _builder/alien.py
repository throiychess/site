"""Alien Gambit learn + practice section (/alien-gambit/).
All lines and numbers come from alien_data.json (Stockfish 17.1, depth 16, white point of view, centipawns)
and are re-checked for legality / mate claims every build (verify())."""
import json, os, html
import chess

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(ROOT, "alien_data.json"), encoding="utf8"))
BASE4 = "e4 c6 d4 d5 Nc3 dxe4 Nxe4 Nf6"
BASE5 = BASE4 + " Ng5"
e = html.escape

def _board(line):
    b = chess.Board(); last = None
    for s in line.split():
        m = b.push_san(s); last = {"from": chess.square_name(m.from_square), "to": chess.square_name(m.to_square)}
    return b, last

def _fmt(line):
    out = []; n = 1; w = True
    for s in line.split():
        out.append(("%d.%s" % (n, s)) if w else s)
        if not w: n += 1
        w = not w
    return " ".join(out)

def _fmt_from(line, start):
    """moves from ply index `start` (0-based), numbered, e.g. '5.Ng5 Bf5 6.Bc4 h6'"""
    out = []
    for i, s in enumerate(line.split()):
        if i < start: continue
        n = i // 2 + 1
        out.append(("%d.%s" % (n, s)) if i % 2 == 0 else (s if out else "%d...%s" % (n, s)))
    return " ".join(out)

def _pawns(cp):
    return ("+" if cp >= 0 else "−") + "%.1f" % (abs(cp) / 100.0)

def _label(cp):
    return "Winning" if cp >= 300 else "Big plus for you" if cp >= 150 else "Better for you" if cp >= 50 else "About equal" if cp > -50 else "Black a bit better"

CH = [
 (BASE4, "The set-up", "info", "Normal opening",
  "This is the Caro-Kann. Black just chased your knight with <b>4...Nf6</b>. Most players retreat. You will not."),
 (BASE5, "The alien move: 5.Ng5", "idea", "The idea",
  "The knight jumps again, straight at the f7 pawn. It looks odd, hence the name. The point: Black must now find an accurate answer, and many natural moves lose fast."),
 (BASE5 + " Bf5 Bc4", "Key position: 5...Bf5 6.Bc4", "idea", "Key position",
  "Black develops the bishop, you bring yours. Now both bishop and knight aim at <b>f7</b>. Black has only two safe moves here: <b>6...e6</b> and <b>6...Bg6</b>. Anything else walks into trouble."),
 (BASE5 + " Bf5 Bc4 Nbd7 Bxf7", "Trap: 6...Nbd7?? 7.Bxf7#", "trap", "Checkmate",
  "The natural developing move is a blunder. The bishop takes on f7, the knight on g5 protects it, and the king has nowhere to go. <b>Checkmate in 7 moves.</b>"),
 (BASE5 + " Bf5 Bc4 e6", "Black's best: 6...e6", "safe", "Good defence",
  "If Black finds this, calm down and just develop (for example 7.Ne2). The computer prefers Black by about a quarter of a pawn. You still have the better practical chances."),
 (BASE5 + " Be6 Nxe6", "Trap: 5...Be6? 6.Nxe6", "trap", "Wins material",
  "Black blocks the f-file with the bishop and your knight simply takes it. Stockfish says about +3 for you."),
 (BASE5 + " Nh5 Bc4", "Trap: 5...Nh5? 6.Bc4", "trap", "Wins big",
  "The knight run to h5 leaves f7 too weak. After 6.Bc4 Stockfish says about +5 for you."),
 (BASE5 + " h6 N5f3", "Careful: 5...h6 6.N5f3", "warn", "Do not sacrifice",
  "Do not play 6.Nxf7?. Black just takes with the king (Kxf7) and you are in trouble (about −2). Without the bishop on c4 the sacrifice does not work. Play the calm 6.N5f3 instead."),
]

def chapters():
    out = []
    for line, title, kind, tag, text in CH:
        b, last = _board(line)
        out.append({"title": title, "kind": kind, "tag": tag, "text": text, "fen": b.fen(), "last": last, "sanline": _fmt(line)})
    return out

PR = [  # (key in quiz/b1/b2, why)
 ("quiz.q1", "<b>Nxf7</b> forks the queen and the rook, and the king cannot take because the bishop guards f7."),
 ("quiz.q2", "<b>Bxf7</b> is checkmate."),
 ("quiz.q3", "<b>Bxf7+</b> drags the king out and Black's position falls apart."),
 ("quiz.q4", "<b>Nxf7</b> is clearly the best. Slow moves give Black time to breathe."),
 ("quiz.q5", "<b>Nxe6</b> wins the bishop that blocked the way."),
 ("quiz.q6", "<b>Qxg4</b> takes the bishop for free."),
 ("b1.Kd7", "The king walked into the open. Attack with <b>Nxf7</b> or <b>Bc4</b>."),
 ("b1.Nh5", "<b>Bc4</b> piles up on f7 and Black cannot hold it together."),
 ("b1.e5", "<b>Bc4</b> adds the second attacker on f7."),
 ("b1.h6", "Do not sacrifice here. <b>N5f3</b> is calm and keeps the balance."),
 ("b2.Qd7", "Check first: <b>Bxf7+</b> wins big."),
]

def practice():
    out = []
    for key, why in PR:
        g, k = key.split("."); it = DATA[g][k]
        b, last = _board(it["line"])
        assert b.fen() == it["fen"] or b.fen().split(" ")[0] == it["fen"].split(" ")[0], key
        ms = [{"san": m["san"], "cp": m["cp"]} for m in it["moves"]]
        out.append({"title": "After " + _fmt_from(it["line"], 8) + ". Your move.", "fen": b.fen(), "last": last, "moves": ms, "why": why})
    return out

def replies():
    res = {}
    for k, base in (("r5", BASE5), ("r6", BASE5 + " Bf5 Bc4")):
        rows = []
        for san, cp, best in DATA["replies"][k]:
            rows.append({"san": san, "cp": cp, "best": best, "label": _label(cp) + " (" + _pawns(cp) + ")" if cp < 90000 else "Checkmate"})
        res[k] = rows
    return res

def verify():
    for line, *_ in CH: _board(line)
    b, _l = _board(BASE5 + " Bf5 Bc4 Nbd7 Bxf7"); assert b.is_checkmate()
    for g in ("quiz", "b1", "b2"):
        for k, it in DATA[g].items():
            b, _l = _board(it["line"])
            for m in it["moves"]: b.parse_san(m["san"])
    # every best-move claim in the replies tables must be legal in its position
    for k, base in (("r5", BASE5), ("r6", BASE5 + " Bf5 Bc4")):
        for san, cp, best in DATA["replies"][k]:
            b, _l = _board(base); b.push_san(san)
            if best: b.parse_san(best)

def data():
    verify()
    return {"chapters": chapters(), "practice": practice(), "replies": replies()}

def stats():
    r = DATA["replies"]["r5"]
    n = len(r); win = [x for x in r if x[1] >= 100]; eq = [x for x in r if abs(x[1]) < 50]; sol = [x[0] for x in r if x[1] <= 0]
    return n, len(win), sol

ALIEN_CSS = """
.al-hero{background:linear-gradient(160deg,var(--tint),var(--panel2));border-bottom:1px solid var(--line3);padding:34px 0 0}
.al-pills{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}.al-pills span{font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;padding:5px 11px;border-radius:999px;border:1px solid var(--line3);color:var(--gold);background:var(--panel)}
.al-hero h1{font-size:clamp(34px,7vw,56px);line-height:1.05;margin:0 0 10px;font-weight:900}.al-hero .al-mv{font-size:clamp(15px,2.4vw,19px);color:var(--mute);margin:0 0 20px;font-weight:600}
.al-cta{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:26px}.al-cta .btn{padding:15px 26px;font-size:17px}
.al-tabs{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;margin:0 -4px}.al-tabs::-webkit-scrollbar{display:none}
.al-tab{flex:none;padding:13px 18px;border:0;border-bottom:3px solid transparent;background:none;color:var(--mute);font:inherit;font-weight:700;font-size:15px;cursor:pointer}.al-tab.on{color:var(--ink);border-bottom-color:var(--gold)}
.al-panel{padding:28px 0 56px}.al-panel[hidden]{display:none}
.al-card{border:1px solid var(--line2);border-radius:18px;background:var(--panel);padding:20px;margin:0 0 22px}
.al-card h2{margin:0 0 12px;font-size:22px}.al-seg{display:inline-flex;border:1px solid var(--line3);border-radius:999px;overflow:hidden;margin:0 0 14px}.al-seg button{padding:7px 16px;border:0;background:none;color:var(--mute);font:inherit;font-weight:700;font-size:14px;cursor:pointer}.al-seg button.on{background:var(--gold);color:var(--on-gold)}
.al-pts{list-style:none;padding:0;margin:0;display:grid;gap:12px}.al-pts li{display:flex;gap:12px;align-items:flex-start;line-height:1.45}.al-pts i{font-style:normal;font-size:24px;line-height:1.2;flex:none;width:30px;text-align:center}
.al-grid{display:grid;grid-template-columns:minmax(0,520px) minmax(0,1fr);gap:28px;align-items:start}@media(max-width:820px){.al-grid{grid-template-columns:1fr}}
.al-pl{display:flex;align-items:center;gap:10px;padding:6px 2px;font-weight:700;font-size:15px}.al-pl i{width:14px;height:14px;border-radius:50%;border:2px solid var(--gold);flex:none}.al-pl i.w{background:var(--ink)}.al-pl i.b{background:#222}.al-pl small{font-weight:500;color:var(--mute)}
.al-bd{display:grid;grid-template-columns:repeat(8,1fr);width:100%;aspect-ratio:1;border-radius:10px;overflow:hidden;touch-action:manipulation;user-select:none}
.al-sq{position:relative;display:flex;align-items:center;justify-content:center}.al-sq.l{background:var(--sq-l)}.al-sq.d{background:var(--sq-d)}.al-sq img{width:92%;height:92%;pointer-events:none}.al-sq.lm:after{content:"";position:absolute;inset:0;background:rgba(227,192,115,.42)}.al-sq.sel:after{content:"";position:absolute;inset:0;background:rgba(63,174,106,.55)}
.al-tag{display:inline-block;font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;border-radius:999px;padding:5px 12px;border:1px solid var(--line3);margin:0 0 10px}.al-tag.t-trap{border-color:#3fae6a;color:#6fd08f}.al-tag.t-warn{border-color:#e2442f;color:#ff8f7d}.al-tag.t-safe{border-color:#e39a2f;color:#ffc56b}
.al-txt h3{margin:0 0 8px;font-size:22px}.al-txt p{margin:0 0 12px}.al-mvs{font-size:14px;color:var(--mute);background:var(--panel2);border-radius:10px;padding:10px 12px;margin:12px 0}
.al-nav{display:flex;align-items:center;gap:12px;justify-content:space-between;margin-top:14px}.al-nav .btn{flex:1;justify-content:center;margin:0}.al-nav .btn:disabled{opacity:.35;cursor:default}#al-count{font-size:13px;color:var(--mute)}.al-dots{display:flex;gap:6px;justify-content:center;margin:12px 0 0}.al-dots i{width:8px;height:8px;border-radius:50%;background:var(--line3)}.al-dots i.on{width:22px;border-radius:4px;background:var(--gold)}
.al-rep{list-style:none;padding:0;margin:0;display:grid;gap:6px}.al-rep li{display:grid;grid-template-columns:62px 90px 1fr auto;gap:10px;align-items:center;padding:7px 10px;border-radius:10px;background:var(--panel2);font-size:14px}.al-rep b{font-size:16px}.al-rep .bar{height:8px;border-radius:4px;background:var(--line2);overflow:hidden}.al-rep .bar i{display:block;height:100%;background:var(--mute)}.al-rep .k-win .bar i,.al-rep .k-good .bar i{background:#3fae6a}.al-rep .k-bad .bar i{background:#e2442f}.al-rep .k-eq .bar i{background:#e39a2f}.al-rep em{font-style:normal;color:var(--gold);font-weight:700;font-size:13px}.al-rep .lab{grid-column:3/5;font-size:13px;color:var(--mute);margin-top:-6px}
@media(max-width:560px){.al-rep li{grid-template-columns:54px 1fr auto}.al-rep .bar{display:none}.al-rep .lab{grid-column:1/4;margin:0}}
.al-hud{display:flex;justify-content:space-between;align-items:center;margin:0 0 10px;font-weight:800}#al-hearts{color:#e2442f;letter-spacing:.1em}
.al-msg{min-height:3em;margin:12px 0;font-size:16px}.al-msg.ok{color:#6fd08f}.al-msg.bad{color:#ff8f7d}
.al-faq details{border:1px solid var(--line2);border-radius:12px;padding:12px 16px;margin:0 0 10px;background:var(--panel)}.al-faq summary{cursor:pointer;font-weight:700}.al-faq p{margin:10px 0 0}
.al-note{font-size:13px;color:var(--mute)}
"""

def alien_page(page, header, footer):
    n, nwin, sol = stats()
    solid = ", ".join(sol)
    short_simple = ('<ul class="al-pts">'
        '<li><i>♞</i><span>You play <b>5.Ng5</b> after 1.e4 c6 2.d4 d5 3.Nc3 dxe4 4.Nxe4 Nf6. The knight attacks f7.</span></li>'
        '<li><i>⚡</i><span>Many natural replies lose quickly. Example: <b>6...Nbd7?? 7.Bxf7#</b> is checkmate.</span></li>'
        '<li><i>✅</i><span>Learn the traps, then practice until you spot them at once.</span></li></ul>')
    short_adv = ('<ul class="al-pts">'
        '<li><i>1</i><span>After 5.Ng5 Black has <b>%d</b> legal moves. In our Stockfish check <b>%d</b> of them give White at least +1.0.</span></li>'
        '<li><i>2</i><span>Black holds the balance only with %s. With best play Black is slightly better (roughly 0.1 to 0.3 of a pawn), so this is a practical weapon, not a refutation of the Caro-Kann.</span></li>'
        '<li><i>3</i><span>The sacrifice <b>Nxf7</b> works only when your bishop already stands on c4. Without it, Kxf7 refutes it.</span></li>'
        '<li><i>4</i><span>All numbers: Stockfish 17.1, depth 16, re-checked at depth 22, from White\'s point of view.</span></li></ul>') % (n, nwin, solid)
    body = header("Train") + f"""<main>
<section class="al-hero"><div class="wrap">
<div class="al-pills"><span>Opening trap</span><span>Caro-Kann</span><span>Checked with Stockfish</span></div>
<h1>Alien Gambit</h1>
<p class="al-mv">1.e4 c6 2.d4 d5 3.Nc3 dxe4 4.Nxe4 Nf6 5.Ng5!?</p>
<div class="al-cta"><a class="btn solid" href="#learn" data-go="learn">Start learning</a><a class="btn" href="#practice" data-go="practice">Practice</a></div>
<div class="al-tabs" role="tablist"><button class="al-tab on" data-t="short" role="tab">In short</button><button class="al-tab" data-t="learn" role="tab">Learn</button><button class="al-tab" data-t="replies" role="tab">Black's replies</button><button class="al-tab" data-t="practice" role="tab">Practice</button><button class="al-tab" data-t="faq" role="tab">Questions</button></div>
</div></section>
<div class="wrap">
<section class="al-panel" id="short">
<div class="al-card"><h2>The opening in short</h2><div class="al-seg"><button class="on" data-m="s">Simple</button><button data-m="a">Advanced</button></div>
<div data-lv="s">{short_simple}</div><div data-lv="a" hidden>{short_adv}</div></div>
<p><a class="btn solid" href="#learn" data-go="learn">Start learning &rarr;</a></p></section>
<section class="al-panel" id="learn" hidden><div class="al-card"><div class="al-grid"><div>
<div class="al-pl"><i class="b"></i>Black <small>Caro-Kann player</small></div><div id="al-learn-board"></div><div class="al-pl"><i class="w"></i>White <small>You</small></div></div>
<div class="al-txt"><span id="al-learn-tag" class="al-tag"></span><h3 id="al-learn-title"></h3><p id="al-learn-text"></p><div class="al-mvs" id="al-learn-moves"></div>
<div class="al-nav"><button class="btn" id="al-prev" type="button">&larr; Back</button><span id="al-count"></span><button class="btn solid" id="al-next" type="button">Next &rarr;</button></div><div class="al-dots" id="al-dots"></div></div></div></div>
<p><a class="btn solid" href="#practice" data-go="practice">Now practice &rarr;</a></p></section>
<section class="al-panel" id="replies" hidden><div class="al-card"><h2>What can Black play on move 5?</h2><p class="al-note">Bar = how good it is for you. On the right: your best answer. Stockfish 17.1, depth 16.</p><ul class="al-rep" data-r="r5"></ul></div>
<div class="al-card"><h2>After 5...Bf5 6.Bc4: Black's options</h2><ul class="al-rep" data-r="r6"></ul></div></section>
<section class="al-panel" id="practice" hidden><div class="al-card"><div class="al-grid"><div><div class="al-hud"><span id="al-hearts"></span><span id="al-score"></span></div><div id="al-pq-board"></div></div>
<div class="al-txt" id="al-prac"><h3 id="al-pq-title">Loading</h3><p class="al-msg" id="al-pq-msg"></p><button class="btn solid" id="al-pq-next" type="button" hidden>Next position</button><p class="al-note">You play White. 3 hearts. Find the strongest move.</p></div></div></div></section>
<section class="al-panel al-faq" id="faq" hidden>
<details open><summary>Is the Alien Gambit sound?</summary><p>No. With best play Black is slightly better. It works because many natural replies lose quickly, and because Black has to know the exact defence.</p></details>
<details><summary>Why bring the bishop to c4 first?</summary><p>The bishop and the knight together hit f7. Without the bishop, Nxf7 simply loses a piece to Kxf7.</p></details>
<details><summary>What if Black plays 5...h6?</summary><p>Do not sacrifice. Retreat with 6.N5f3 and play a normal game.</p></details>
<p class="al-note">All moves and numbers in this section were checked with Stockfish 17.1 (depth 16, re-checked at depth 22; the numbers moved by at most about 0.3 of a pawn and no move changed from good to bad). They are centipawns from White's point of view.</p></section>
</div></main>
<script src="/js/alien.js" defer></script>""" + footer()
    return "/alien-gambit/", page("/alien-gambit/", "Alien Gambit: learn and practice | Throiy Chess", "Learn the Alien Gambit step by step and practice the traps. Every line checked with Stockfish.", f"<style>{ALIEN_CSS}</style>" + body, noindex=True)
