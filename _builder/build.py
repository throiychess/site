"""ThroiyChess website generator (static, for GitHub Pages on throiychess.com).

    python build.py   ->  dist/   (copy dist/ to the repo root and push)

Add content in the data section: SHORTS (every YouTube Short), TRAPS (playable trap pages).
Settings: WEB3FORMS_KEY (contact form), ANALYTICS (GoatCounter code), DONATE_URL."""
import os, sys, json, shutil, html, math, datetime
sys.path.insert(0, "/home/claude/ext/python-chess")  # local; in GitHub Actions chess comes from pip
import chess

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "throiychess.com"; SITE = f"https://{DOMAIN}"
NAME = "Throiy Chess"
TAGLINE = "Opening traps, mating patterns and top games, explained fast."
LINKS = [("YouTube", "https://www.youtube.com/@ThroiyChess"), ("TikTok", "https://www.tiktok.com/@throiychess"),
         ("Instagram", "https://www.instagram.com/throiychess"), ("Facebook", "https://www.facebook.com/throiychess")]
WEB3FORMS_KEY = "a10fa119-63ca-43b3-8ef5-2b7aa106d669"        # access key from web3forms.com, sent to the contact e-mail address
CONTACT_EMAIL = "info@throiychess.com"      # e.g. "info@throiychess.com" once the mailbox exists
ANALYTICS = "throiychess"            # GoatCounter code, e.g. "throiychess" -> https://throiychess.goatcounter.com
DONATE_URL = "https://ko-fi.com/throiychess"           # e.g. a Ko-fi page
PER_PAGE = 12

# ---------------- data ----------------
# Every YouTube Short. id = the part after youtube.com/shorts/ ; date = upload date (YYYY-MM-DD) ; trap = slug of a trap page (optional)
SHORTS = [  # newest first
    dict(id="fJiePOSCU9I", title="Free rook? Don't take it! Giri vs Abdusattorov", date="2026-10-26", topic="Top game · European Club Cup",
         desc="Giri left his rook hanging on purpose. Abdusattorov took it, and 19.Nf5! 20.Qg5! decided the game. Before you grab material, check what your opponent gets."),
    dict(id="TsHaDaBUS-c", title="Take my queen! The Stafford Gambit trap", date="2026-10-26", topic="Stafford Gambit",
         desc="After 6.Bg5?? Nxe4! 7.Bxd8?? Bxf2+ 8.Ke2 Bg4# it's mate. The fix: don't play Bg5, just develop and castle."),
    dict(id="G2pqyA0mXF0", title="Don't take the bait! The Fishing Pole Trap", date="2026-10-25", topic="Ruy Lopez",
         desc="Black leaves a knight on g4 as bait. Take it and the h-file opens straight at your king, ending in mate on h1."),
    dict(id="WFRx-dXjOcc", title="Fried Liver Attack: mate in 9 (and how to stop it)", date="2026-10-24", topic="Italian Game",
         desc="After 5…Nxd5? 6.Nxf7! the black king is dragged out. The fix: don't recapture on d5, play 5…Na5! instead."),
    dict(id="KA_x11CO7Gg", title="Don't fall for this Petrov trap", date=None, topic="Petrov Defense",
         desc="After 3…Nxe4? 4.Qe2! the knight is pinned and Nc6+ wins the queen. The fix: play 3…d6 first."),
    dict(id="LCSXV_yJs_U", title="Stop the Scholar's Mate (and punish it)", date=None, topic="Scholar's Mate",
         desc="Block with g6, defend f7 with Nf6, then hit the queen with Nd4. Early queen? Develop and make her run."),
    dict(id="9EOJdMBaPO4", title="He moved his king on move 5… big mistake", date=None, topic="Opening mistakes",
         desc="No castling, a knight fork on f7 and a rook gone. In the opening, castle; don't move your king by hand."),
    dict(id="xF6KVwnOGCY", title="I fell for the oldest trick in chess", date=None, topic="Scholar's Mate",
         desc="Queen and bishop against f7. Once they aim at f7, keep defending it."),
]

_feed = os.path.join(ROOT, "youtube.json")
if os.path.exists(_feed):
    _known = {s["id"] for s in SHORTS}
    _new = [v for v in json.load(open(_feed, encoding="utf-8")) if v["id"] not in _known]
    for s in SHORTS:  # fill missing upload dates from the feed
        f = next((v for v in json.load(open(_feed, encoding="utf-8")) if v["id"] == s["id"]), None)
        if f and not s.get("date"): s["date"] = f["date"]
    SHORTS = sorted(_new + SHORTS, key=lambda s: s.get("date") or "", reverse=True)

TRAPS = [
    dict(slug="fishing-pole-trap", name="Fishing Pole Trap", opening="Ruy Lopez", side="Black sets it", short="G2pqyA0mXF0",
         hook="Black leaves a knight hanging on g4. Take it, and the h-file opens straight onto your king.",
         intro="The Fishing Pole Trap is a sneaky idea for Black in the Ruy Lopez (1.e4 e5 2.Nf3 Nc6 3.Bb5 Nf6 4.O-O Ng4). "
               "After 5.h3 h5! the knight on g4 is offered as bait. If White takes it with 6.hxg4??, the h-file opens "
               "and Black's queen and rook deliver mate on h1.",
         moves="e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Ng4 h3 h5 hxg4 hxg4 Nh2 Qh4 f3 g3 Rf2 Nd4 Kf1 gxh2 Ke1 h1=Q+ Bf1 Qxf1+ Kxf1 Qh1#",
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
# library cards for lessons that have a Short but no playable page yet: (name, opening, text, short id or None)
OTHER = [("Petrov Trap", "Petrov Defense", "Copying White's moves costs Black the queen. Play 3…d6 first.", "KA_x11CO7Gg"),
         ("Fried Liver Attack", "Italian Game", "White sacrifices a knight on f7 and drags the king into the open.", "WFRx-dXjOcc")]

# ---------------- style ----------------
CSS = """
@font-face{font-family:Inter;font-weight:400;font-display:swap;src:url(/fonts/Inter-Regular.woff) format("woff")}
@font-face{font-family:Inter;font-weight:600;font-display:swap;src:url(/fonts/Inter-SemiBold.woff) format("woff")}
@font-face{font-family:Inter;font-weight:700;font-display:swap;src:url(/fonts/Inter-Bold.woff) format("woff")}
@font-face{font-family:Inter;font-weight:800;font-display:swap;src:url(/fonts/Inter-ExtraBold.woff) format("woff")}
@font-face{font-family:Inter;font-weight:900;font-display:swap;src:url(/fonts/Inter-Black.woff) format("woff")}
:root{--bg:#0e0d0b;--panel:#17150f;--panel2:#1d1a13;--line:#2c271d;--ink:#efe8d8;--mute:#a59a83;--gold:#e3c073;--red:#e2442f;--on-gold:#14110b;
--sq-l:#c4ac80;--sq-d:#7e6542;--font:Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color-scheme:dark}
*{box-sizing:border-box}
html{scroll-padding-top:96px}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:17px;line-height:1.6;margin:0}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:30;background:var(--bg)}
a{color:var(--gold)}
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible{outline:2px solid var(--gold);outline-offset:3px}
.wrap{max-width:1080px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:rgba(14,13,11,.92);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px 20px;padding-block:10px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--ink);font-weight:900;font-size:22px;letter-spacing:.02em;line-height:1}
.brand img{height:56px;width:auto}
.brand b{color:var(--gold);font-weight:600;letter-spacing:.42em;font-size:13px;display:block;margin-top:5px}
nav.links{display:flex;gap:6px 18px;flex-wrap:wrap}
nav.links a{color:var(--mute);text-decoration:none;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding-block:6px}
nav.links a:hover,nav.links a[aria-current]{color:var(--gold)}
.eyebrow{font-size:13px;font-weight:600;letter-spacing:.24em;text-transform:uppercase;color:var(--gold)}
h1,h2,h3{text-wrap:balance;margin:0}
h1{font-weight:900;font-size:clamp(40px,7vw,76px);line-height:1;letter-spacing:-.025em;text-transform:uppercase}
h1 em{font-style:normal;color:var(--gold)}
h1.page{font-size:clamp(36px,6vw,60px)}
h2{font-weight:800;font-size:clamp(26px,3.4vw,36px);line-height:1.1;letter-spacing:-.01em}
h3{font-weight:800;font-size:20px;line-height:1.25}
.lead{color:var(--mute);font-size:19px;max-width:40ch;margin:0}
.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:48px;align-items:center;padding-block:56px}
.hero>*{min-width:0}
.hero .copy{display:grid;gap:22px;justify-items:start}
.ticks{position:relative;padding:12px}
.ticks::before,.ticks::after,.ticks>.t1,.ticks>.t2{content:"";position:absolute;width:34px;height:34px;border-color:var(--gold);border-style:solid;pointer-events:none}
.ticks::before{left:0;top:0;border-width:4px 0 0 4px}.ticks::after{right:0;top:0;border-width:4px 4px 0 0}
.ticks>.t1{left:0;bottom:0;border-width:0 0 4px 4px}.ticks>.t2{right:0;bottom:0;border-width:0 4px 4px 0}
.ticks img{display:block;width:100%;height:auto}
.btns{display:flex;gap:10px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;padding:11px 18px;font-weight:700;font-size:15px;text-decoration:none;border:1px solid var(--gold);color:var(--gold);letter-spacing:.03em;background:none;cursor:pointer;font-family:var(--font)}
.btn.solid{background:var(--gold);color:var(--on-gold)}
.btn:hover{filter:brightness(1.12)}
section{padding-block:56px;border-top:1px solid var(--line)}
.pagehead{display:grid;gap:14px;padding-block:44px 34px}
.pagehead p{color:var(--mute);margin:0;max-width:60ch;font-size:19px}
.sechead{display:flex;justify-content:space-between;align-items:end;gap:16px;flex-wrap:wrap;margin-bottom:28px}
.sechead>div{display:grid;gap:8px}
.sechead p{color:var(--mute);margin:0;max-width:56ch}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.card{background:var(--panel);border-left:4px solid var(--gold);padding:22px 22px 20px;display:grid;gap:10px;align-content:start;text-decoration:none;color:var(--ink);min-width:0}
.card .meta{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.tag{background:var(--gold);color:var(--on-gold);font-weight:900;font-size:12px;padding:3px 8px;letter-spacing:.04em}
.label{font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--mute)}
.card p{margin:0;color:var(--mute);font-size:15.5px}
.card .go{font-weight:700;font-size:14px;color:var(--gold);margin-top:4px}
a.card:hover{background:var(--panel2)}
.card.soon{border-left-color:var(--line)}
/* shorts */
.shorts{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.short{display:grid;gap:10px;align-content:start;min-width:0}
.short h3{font-size:16px;line-height:1.3}
.short p{margin:0;color:var(--mute);font-size:14px}
.vid{position:relative;aspect-ratio:9/16;width:100%;max-width:100%;background:var(--panel);overflow:hidden}
.vid iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.vid button{position:absolute;inset:0;width:100%;height:100%;border:0;cursor:pointer;color:var(--ink);font-family:var(--font);
 background:linear-gradient(180deg,rgba(14,13,11,.15),rgba(14,13,11,.85)),repeating-conic-gradient(var(--sq-d) 0 25%,var(--sq-l) 0 50%) 0 0/25% 14.0625%;
 display:grid;place-items:center;padding:14px}
.vid button span.play{width:64px;height:64px;border-radius:50%;background:var(--gold);display:grid;place-items:center;box-shadow:0 6px 24px rgba(0,0,0,.5)}
.vid button span.play::before{content:"";margin-left:5px;border-left:20px solid var(--on-gold);border-top:12px solid transparent;border-bottom:12px solid transparent}
.vid button small{position:absolute;left:12px;right:12px;bottom:12px;font-size:11.5px;color:var(--mute);line-height:1.35;text-align:left}
.vid button:hover span.play{filter:brightness(1.1)}
.pager{display:flex;gap:8px;justify-content:center;margin-top:36px;flex-wrap:wrap}
.pager a,.pager span{padding:8px 14px;border:1px solid var(--line);text-decoration:none;color:var(--mute);font-weight:700;font-variant-numeric:tabular-nums}
.pager span{background:var(--gold);color:var(--on-gold);border-color:var(--gold)}
.breaking{display:grid;grid-template-columns:auto 1fr;gap:28px;align-items:center;background:var(--panel);padding:28px}
.breaking>*{min-width:0}
.live{font-weight:900;font-size:13px;letter-spacing:.2em;color:var(--bg);background:var(--red);padding:6px 10px;text-transform:uppercase;white-space:nowrap}
.breaking p{margin:6px 0 0;color:var(--mute)}
.about{display:grid;grid-template-columns:220px 1fr;gap:36px;align-items:center}
.about>*{min-width:0}
.about img{width:220px;max-width:100%;height:auto}
.about p{max-width:60ch;color:var(--mute);margin:10px 0 0}
footer{border-top:1px solid var(--line);padding-block:30px;color:var(--mute);font-size:14px}
footer .wrap{display:flex;justify-content:space-between;gap:12px 24px;flex-wrap:wrap}
footer nav{display:flex;gap:6px 16px;flex-wrap:wrap}
footer a{color:var(--mute)}
/* trap page */
.crumb{font-size:14px;color:var(--mute);padding-top:28px}
.crumb a{color:var(--mute)}
.player{display:grid;grid-template-columns:minmax(0,560px) minmax(0,1fr);gap:36px;align-items:start}
.player>*{min-width:0}
.board{display:grid;grid-template-columns:repeat(8,1fr);aspect-ratio:1;width:100%;max-width:100%;user-select:none}
.sq{position:relative;aspect-ratio:1}
.sq.l{background:var(--sq-l)}.sq.d{background:var(--sq-d)}
.sq.hl::before{content:"";position:absolute;inset:0;background:rgba(240,200,90,.42)}
.sq.mk::after{content:"";position:absolute;inset:6%;border-radius:50%;border:4px solid #fff;box-shadow:0 0 0 3px #14120f,inset 0 0 0 2px #14120f;z-index:2}
.sq.mk.red::after{border-color:var(--red);box-shadow:0 0 0 3px #fff}
.sq img{position:absolute;inset:2%;width:96%;height:96%;z-index:1}
.sq .co{position:absolute;font-size:11px;font-weight:700;z-index:3;line-height:1}
.sq .rk{left:3px;top:3px}.sq .fl{right:3px;bottom:2px}
.sq.l .co{color:var(--sq-d)}.sq.d .co{color:var(--sq-l)}
.ctrl{display:flex;gap:8px;margin-top:14px}
.ctrl button{flex:1;background:var(--panel);color:var(--ink);border:1px solid var(--line);padding:10px 0;font-size:16px;font-weight:700;cursor:pointer;font-family:var(--font)}
.ctrl button:hover{border-color:var(--gold);color:var(--gold)}
.note{background:var(--panel);border-top:4px solid var(--gold);padding:22px;display:grid;gap:10px}
.note .meta{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.note p{margin:0;font-size:19px;line-height:1.45;font-weight:600}
.moves{display:flex;flex-wrap:wrap;gap:4px 2px;margin-top:20px;font-variant-numeric:tabular-nums;font-size:15px}
.moves button{background:none;border:0;color:var(--mute);font:inherit;padding:3px 6px;cursor:pointer}
.moves button.on{background:var(--gold);color:var(--on-gold);font-weight:800}
.moves span{color:#6f6656;padding:3px 0 3px 6px}
.prose{max-width:68ch;color:var(--ink)}
.prose p{margin:0 0 14px}
.prose h2{font-size:24px;margin:30px 0 10px}
.fix{display:grid;gap:14px;padding:0;margin:0;list-style:none;counter-reset:f}
.fix li{display:grid;grid-template-columns:28px 1fr;gap:12px;max-width:70ch}
.fix li::before{counter-increment:f;content:counter(f);font-weight:900;color:var(--gold);font-size:20px;line-height:1.4}
.hint{color:var(--mute);font-size:14px;margin-top:10px}
.twocol{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:44px;align-items:start}
.twocol>*{min-width:0}
/* form */
form.contact{display:grid;gap:18px;max-width:620px}
.field{display:grid;gap:6px}
.field label{font-weight:700;font-size:14px;letter-spacing:.04em}
.field input,.field textarea{background:var(--panel);border:1px solid var(--line);color:var(--ink);font:inherit;padding:12px 14px;width:100%}
.field textarea{min-height:160px;resize:vertical}
.field input:focus,.field textarea:focus{border-color:var(--gold)}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.status{font-weight:600;margin:0}
.status.err{color:var(--red)}
.small{font-size:14px;color:var(--mute)}
@media (max-width:900px){.shorts{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr 1fr}}
@media (max-width:860px){.hero,.player,.twocol{grid-template-columns:1fr}.hero{padding-block:32px}.breaking{grid-template-columns:1fr;gap:14px}.about{grid-template-columns:1fr}.about img{width:150px}}
@media (max-width:560px){.grid{grid-template-columns:1fr}.brand img{height:46px}.brand{font-size:19px}nav.links{gap:4px 14px}html{scroll-padding-top:130px}}
@media (prefers-reduced-motion:no-preference){.btn,.card{transition:background .15s,filter .15s}}
"""
e = html.escape

def csp():
    conn = ["'self'"] + (["https://api.web3forms.com"] if WEB3FORMS_KEY else []) + ([f"https://{ANALYTICS}.goatcounter.com"] if ANALYTICS else [])
    scr = ["'self'", "'unsafe-inline'"] + (["https://gc.zgo.at"] if ANALYTICS else [])
    return ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self'; "
            f"script-src {' '.join(scr)}; connect-src {' '.join(conn)}; frame-src https://www.youtube-nocookie.com; "
            "form-action 'self' https://api.web3forms.com; base-uri 'self'; object-src 'none'")

def page(path, title, desc, body, jsonld=None, og_image="/img/og.jpg", ogtype="website"):
    url = SITE + path
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    gc = (f'<script data-goatcounter="https://{ANALYTICS}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>' if ANALYTICS else "")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<meta http-equiv="Content-Security-Policy" content="{csp()}"><meta name="referrer" content="strict-origin-when-cross-origin">'
            f'<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">'
            f'<link rel="icon" href="/img/favicon.png"><link rel="apple-touch-icon" href="/img/logo-small.png"><meta name="theme-color" content="#0e0d0b">'
            f'<meta property="og:site_name" content="{NAME}"><meta property="og:type" content="{ogtype}"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}{og_image}">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<link rel="preload" href="/fonts/Inter-Black.woff" as="font" type="font/woff" crossorigin>'
            f'<style>{CSS}</style>{ld}{gc}</head><body>{body}{SCRIPT}</body></html>')

NAV = [("Shorts", "/shorts/"), ("Traps", "/#traps"), ("Top games", "/#top-games"), ("About", "/#about"), ("Contact", "/contact/")]
def header(active=""):
    return ('<header class="top"><div class="wrap"><a class="brand" href="/" aria-label="Throiy Chess home"><img src="/img/logo-small.png" width="96" height="161" alt="">'
            '<span>THROIY<b>CHESS</b></span></a><nav class="links" aria-label="Main">'
            + "".join(f'<a href="{u}"{" aria-current=page" if n == active else ""}>{n}</a>' for n, u in NAV) + '</nav></div></header>')

def footer():
    ext = " ".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in LINKS)
    return (f'<footer><div class="wrap"><span>© {datetime.date.today().year} Throiy Chess · Quick chess lessons, every day</span>'
            f'<nav aria-label="Footer">{ext}<a href="/contact/">Contact</a><a href="/privacy/">Privacy</a></nav></div></footer>')

# click-to-load YouTube (no request to YouTube until the visitor presses play)
SCRIPT = """<script>
document.addEventListener("click",function(ev){var b=ev.target.closest("button[data-yt]");if(!b)return;var f=document.createElement("iframe");
f.src="https://www.youtube-nocookie.com/embed/"+b.dataset.yt+"?autoplay=1&rel=0&playsinline=1";f.title=b.dataset.title||"YouTube Short";
f.allow="autoplay; encrypted-media; picture-in-picture";f.allowFullscreen=true;f.referrerPolicy="strict-origin-when-cross-origin";b.replaceWith(f)});
</script>"""
def short_card(s):
    return (f'<article class="short"><div class="vid"><button type="button" data-yt="{e(s["id"])}" data-title="{e(s["title"])}" aria-label="Play: {e(s["title"])}">'
            f'<span class="play"></span><small>Plays from YouTube. Pressing play loads YouTube.</small></button></div>'
            f'<span class="label">{e(s.get("topic", ""))}</span><h3>{e(s["title"])}</h3><p>{e(s.get("desc", ""))}</p></article>')

def video_ld(s):
    if not s.get("date"): return None
    return {"@context": "https://schema.org", "@type": "VideoObject", "name": s["title"], "description": s.get("desc", s["title"]),
            "uploadDate": s["date"], "thumbnailUrl": f"https://i.ytimg.com/vi/{s['id']}/hqdefault.jpg",
            "embedUrl": f"https://www.youtube-nocookie.com/embed/{s['id']}", "contentUrl": f"https://www.youtube.com/shorts/{s['id']}"}

ORG = {"@context": "https://schema.org", "@type": "Organization", "name": NAME, "url": SITE, "logo": SITE + "/img/logo.png",
       "sameAs": [u for _, u in LINKS], "description": TAGLINE}

# ---------------- pages ----------------
def home():
    cards = "".join(
        f'<a class="card" href="/traps/{t["slug"]}/"><div class="meta"><span class="label">{e(t["opening"])}</span></div>'
        f'<h3>{e(t["name"])}</h3><p>{e(t["hook"])}</p><span class="go">Play through the trap →</span></a>' for t in TRAPS)
    for n, o, h, sid in OTHER:
        href = f"https://www.youtube.com/shorts/{sid}" if sid else LINKS[0][1] + "/shorts"
        cards += (f'<a class="card soon" href="{href}" target="_blank" rel="noopener"><div class="meta"><span class="label">{e(o)}</span></div>'
                  f'<h3>{e(n)}</h3><p>{e(h)}</p><span class="go">Watch the Short →</span></a>')
    latest = "".join(short_card(s) for s in SHORTS[:4])
    body = header() + f'''<main>
<div class="wrap hero"><div class="copy"><span class="eyebrow">Throiy Chess · Lessons &amp; Games</span>
<h1>Stop falling for <em>chess traps.</em></h1>
<p class="lead">Opening traps, mating patterns and the best moments from top games. Each one explained in under a minute.</p>
<div class="btns"><a class="btn solid" href="/shorts/">Watch the Shorts</a><a class="btn" href="#traps">Browse the traps</a></div></div>
<div class="ticks"><img src="/img/fishing-pole-board.jpg" width="720" height="720" alt="Final position of the Fishing Pole Trap: Black's queen mates on h1"><i class="t1"></i><i class="t2"></i></div></div>
<section id="shorts"><div class="wrap"><div class="sechead"><div><span class="eyebrow">Latest Shorts</span><h2>One lesson a day, under a minute.</h2></div>
<a class="btn" href="/shorts/">All Shorts →</a></div><div class="shorts">{latest}</div></div></section>
<section id="traps"><div class="wrap"><div class="sechead"><div><span class="eyebrow">Trap library</span><h2>Learn the trap. Then learn the fix.</h2>
<p>Every trap ends with the mate. Every lesson ends with how to avoid it. Step through the moves on the board.</p></div></div>
<div class="grid">{cards}</div></div></section>
<section id="top-games"><div class="wrap"><div class="breaking"><span class="live">Top games</span><div><h3>Clutch Chess: Champions Showdown · 27–29 October</h3>
<p>Nakamura, Caruana, Praggnanandhaa and Sindarov play rapid chess. We break down the sharpest moment of each day in a Short.</p></div></div></div></section>
<section id="about"><div class="wrap about"><img src="/img/avatar-thumbs_up.png" width="220" height="220" alt="Throiy, illustrated, giving a thumbs up">
<div><span class="eyebrow">About</span><h2>Hi, I'm Throiy.</h2><p>I'm a chess player sharing what I wish I'd known sooner. Short, clear lessons you can use in your next game. A new one every day on YouTube, TikTok, Instagram and Facebook.</p>
<div class="btns" style="margin-top:18px">''' + "".join(f'<a class="btn" href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in LINKS) + \
        (f'<a class="btn solid" href="{DONATE_URL}" target="_blank" rel="noopener">Support the channel</a>' if DONATE_URL else "") + '''</div></div></div></section>
</main>''' + footer()
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE, "description": TAGLINE}
    return page("/", "Throiy Chess · Chess traps and lessons, explained fast", TAGLINE + " A new chess lesson every day.", body,
                [ORG, site_ld] + [v for v in map(video_ld, SHORTS[:4]) if v])

def shorts_pages():
    n = max(1, math.ceil(len(SHORTS) / PER_PAGE)); out = []
    for i in range(n):
        items = SHORTS[i * PER_PAGE:(i + 1) * PER_PAGE]
        path = "/shorts/" if i == 0 else f"/shorts/page/{i + 1}/"
        pager = ""
        if n > 1:
            pager = '<nav class="pager" aria-label="Pages">' + "".join(
                f'<span aria-current="page">{k + 1}</span>' if k == i else f'<a href="{"/shorts/" if k == 0 else f"/shorts/page/{k + 1}/"}">{k + 1}</a>' for k in range(n)) + "</nav>"
        body = header("Shorts") + f'''<main class="wrap"><div class="pagehead"><span class="eyebrow">All Shorts{f" · page {i + 1}" if i else ""}</span>
<h1 class="page">Every lesson, in one place.</h1><p>Opening traps, named mates and top-game moments. Press play to watch here, or follow along on YouTube.</p></div>
<div class="shorts">{"".join(short_card(s) for s in items)}</div>{pager}
<div class="btns" style="justify-content:center;margin:40px 0 56px"><a class="btn solid" href="{LINKS[0][1]}" target="_blank" rel="noopener">Subscribe on YouTube</a></div></main>''' + footer()
        out.append((path, page(path, f"All Shorts{f' (page {i + 1})' if i else ''} · Throiy Chess", "Every Throiy Chess Short: opening traps, mating patterns and top-game moments, each under a minute.",
                               body, [v for v in map(video_ld, items) if v])))
    return out

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
    sh = next((s for s in SHORTS if s["id"] == t.get("short")), None)
    side = (short_card(sh) if sh else
            f'<div class="card"><span class="label">Watch</span><h3>The {e(t["name"])} as a Short</h3><p>All lessons are on YouTube, TikTok and Instagram.</p>'
            f'<a class="go" href="{LINKS[0][1]}/shorts" target="_blank" rel="noopener">Watch on YouTube →</a></div>')
    path = f'/traps/{t["slug"]}/'
    body = header("Traps") + f'''<main class="wrap"><div class="crumb"><a href="/#traps">Trap library</a> / {e(t["name"])}</div>
<div class="pagehead" style="padding-top:18px"><span class="eyebrow">{e(t["opening"])} · {e(t["side"])}</span><h1 class="page">{e(t["name"])}</h1><p>{e(t["hook"])}</p></div>
<div class="player"><div><div class="board" id="board" role="img" aria-label="Chess board showing the {e(t["name"])}"></div>
<div class="ctrl"><button type="button" id="first" aria-label="Start position">⏮</button><button type="button" id="prev" aria-label="Previous move">◀</button>
<button type="button" id="next" aria-label="Next move">▶</button><button type="button" id="last" aria-label="Final position">⏭</button></div>
<p class="hint">Tip: use the arrow keys.</p></div>
<div><div class="note" aria-live="polite"><div class="meta"><span class="label" id="nl"></span><span class="tag" id="nt"></span></div><p id="nx"></p></div>
<div class="moves" id="moves">{mv_html}</div></div></div>
<section style="margin-top:56px"><div class="twocol"><div class="prose"><span class="eyebrow">The trap</span><h2>How the {e(t["name"])} works</h2><p>{e(t["intro"])}</p>
<h2>How not to fall for it</h2><ol class="fix">{fix}</ol></div><aside>{side}</aside></div></section>
</main>''' + footer() + '<script>const D=' + data + ''';
const P="/img/pieces/",B=document.getElementById("board");let cur=0;
const sqs=[];for(let r=7;r>=0;r--)for(let f=0;f<8;f++){const d=document.createElement("div");const n="abcdefgh"[f]+(r+1);d.className="sq "+((r+f)%2?"l":"d");d.dataset.n=n;
if(f===0){const c=document.createElement("span");c.className="co rk";c.textContent=r+1;d.appendChild(c)}
if(r===0){const c=document.createElement("span");c.className="co fl";c.textContent="abcdefgh"[f];d.appendChild(c)}B.appendChild(d);sqs.push(d)}
function parse(fen){const m={};fen.split("/").forEach((row,i)=>{let f=0;for(const ch of row){if(/\\d/.test(ch))f+=+ch;else{m["abcdefgh"[f]+(8-i)]=ch;f++}}});return m}
function note(i){let k=i;while(k>=0&&!D.notes[k])k--;return D.notes[k]}
function show(i){cur=Math.max(0,Math.min(D.plies.length-1,i));const p=D.plies[cur],m=parse(p.fen),n=note(cur);const mk=(D.notes[cur]&&D.notes[cur].marks)||[];
sqs.forEach(d=>{const s=d.dataset.n;d.classList.toggle("hl",s===p.fr||s===p.to);d.classList.toggle("mk",mk.includes(s)||mk.includes("!"+s));d.classList.toggle("red",mk.includes("!"+s));
const old=d.querySelector("img");if(old)old.remove();const c=m[s];if(c){const im=document.createElement("img");im.alt="";im.src=P+(c===c.toUpperCase()?"w":"b")+c.toLowerCase()+".png";d.appendChild(im)}});
document.getElementById("nl").textContent=n.label;const t=document.getElementById("nt");t.textContent=n.tag;t.hidden=!n.tag;document.getElementById("nx").textContent=n.text;
document.querySelectorAll("#moves button").forEach(b=>b.classList.toggle("on",+b.dataset.p===cur))}
document.getElementById("first").onclick=()=>show(0);document.getElementById("prev").onclick=()=>show(cur-1);
document.getElementById("next").onclick=()=>show(cur+1);document.getElementById("last").onclick=()=>show(D.plies.length-1);
document.getElementById("moves").onclick=e=>{const b=e.target.closest("button");if(b)show(+b.dataset.p)};
document.addEventListener("keydown",e=>{if(e.target.closest("input,textarea"))return;if(e.key==="ArrowRight")show(cur+1);if(e.key==="ArrowLeft")show(cur-1)});
show(0);</script>'''
    art = {"@context": "https://schema.org", "@type": "Article", "headline": f'{t["name"]}: how it works and how to avoid it',
           "description": t["hook"], "about": [t["opening"], "chess opening trap"], "author": {"@type": "Organization", "name": NAME, "url": SITE},
           "publisher": {"@type": "Organization", "name": NAME, "logo": {"@type": "ImageObject", "url": SITE + "/img/logo.png"}},
           "mainEntityOfPage": SITE + path, "image": SITE + "/img/og.jpg"}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Trap library", "item": SITE + "/#traps"},
        {"@type": "ListItem", "position": 2, "name": t["name"], "item": SITE + path}]}
    return path, page(path, f'{t["name"]}: moves, mate and how to avoid it · Throiy Chess', t["hook"] + " Step through every move on the board.", body,
                      [art, crumbs] + ([video_ld(sh)] if sh and video_ld(sh) else []), ogtype="article")

def contact():
    active = bool(WEB3FORMS_KEY)
    form = f'''<form class="contact" id="cf" action="https://api.web3forms.com/submit" method="POST" novalidate>
<input type="hidden" name="access_key" value="{e(WEB3FORMS_KEY or "")}"><input type="hidden" name="subject" value="New message via throiychess.com">
<div class="hp" aria-hidden="true"><label for="botcheck">Leave empty</label><input type="checkbox" name="botcheck" id="botcheck" tabindex="-1"></div>
<div class="field"><label for="name">Name</label><input id="name" name="name" autocomplete="name" required maxlength="100"></div>
<div class="field"><label for="email">E-mail</label><input id="email" name="email" type="email" autocomplete="email" required maxlength="200"></div>
<div class="field"><label for="topic">Subject</label><input id="topic" name="topic" maxlength="150" placeholder="Question, idea for a trap, collaboration…"></div>
<div class="field"><label for="message">Message</label><textarea id="message" name="message" required maxlength="5000"></textarea></div>
<p class="small">We only use your details to answer your message. See the <a href="/privacy/">privacy statement</a>.</p>
<div><button class="btn solid" type="submit" id="send">Send message</button></div><p class="status" id="st" role="status"></p></form>
<script>(function(){{var f=document.getElementById("cf"),st=document.getElementById("st"),active={str(active).lower()};
f.addEventListener("submit",async function(ev){{ev.preventDefault();st.className="status";
if(!f.name.value.trim()||!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(f.email.value)||!f.message.value.trim()){{st.className="status err";st.textContent="Please fill in your name, a valid e-mail address and a message.";return}}
if(!active){{st.className="status err";st.textContent="The contact form opens soon. Until then, send us a message on Instagram (@throiychess).";return}}
var b=document.getElementById("send");b.disabled=true;st.textContent="Sending…";
try{{var r=await fetch(f.action,{{method:"POST",headers:{{"Accept":"application/json"}},body:new FormData(f)}});var j=await r.json();
if(j.success){{f.reset();st.textContent="Thanks! Your message has been sent. We usually reply within a few days."}}else throw 0}}
catch(x){{st.className="status err";st.textContent="Sending failed. Please try again later, or message us on Instagram (@throiychess)."}}b.disabled=false}})}})();</script>'''
    mail = f'<p class="small">Or e-mail us: <strong>{e(CONTACT_EMAIL)}</strong></p>' if CONTACT_EMAIL else ""
    body = header("Contact") + f'''<main class="wrap"><div class="pagehead"><span class="eyebrow">Contact</span><h1 class="page">Say hi.</h1>
<p>A question, a trap you want explained, or a collaboration? Send a message.</p></div>
<div class="twocol" style="padding-bottom:64px"><div>{form}{mail}</div><aside><img src="/img/avatar-thumbs_up.png" width="300" height="300" alt="Throiy, illustrated, giving a thumbs up" style="width:100%;max-width:260px;height:auto"></aside></div></main>''' + footer()
    return "/contact/", page("/contact/", "Contact · Throiy Chess", "Get in touch with Throiy Chess: questions, trap requests and collaborations.", body)

def privacy():
    body = header() + f'''<main class="wrap"><div class="pagehead"><span class="eyebrow">Privacy</span><h1 class="page">Privacy statement</h1>
<p>Short version: this site does not use cookies, does not track you across sites and does not sell anything about you.</p></div>
<div class="prose" style="padding-bottom:64px">
<h2>Who we are</h2><p>Throiy Chess is a chess education channel. This website ({DOMAIN}) is run by Throiy Chess from the Netherlands.</p>
<h2>What this site stores</h2><p>Nothing in your browser. There are no cookies and no login. The site is hosted on GitHub Pages; like every web server, GitHub processes your IP address to deliver the pages and to protect the service.</p>
<h2>Videos</h2><p>Shorts are shown from YouTube in privacy-enhanced mode. Nothing is loaded from YouTube until you press play. When you do, YouTube (Google) receives your IP address and may set its own cookies, under Google's privacy policy.</p>
<h2>Contact form</h2><p>If you send a message, we receive your name, e-mail address and message through our form service (Web3Forms) by e-mail. We use them only to reply, and delete them when they are no longer needed, at the latest after one year.</p>
<h2>Statistics</h2><p>{("We count visits with GoatCounter, without cookies and without storing personal data, to see which lessons are useful." if ANALYTICS else "We do not run visitor statistics at the moment. If we add them, we will use a cookie-free tool and update this statement.")}</p>
<h2>Your rights</h2><p>You can ask us what we hold about you, and ask us to correct or delete it, via the <a href="/contact/">contact page</a>. You can also file a complaint with the Dutch Data Protection Authority (Autoriteit Persoonsgegevens).</p>
<p class="small">Last updated: {datetime.date.today().strftime("%d %B %Y")}</p></div></main>''' + footer()
    return "/privacy/", page("/privacy/", "Privacy · Throiy Chess", "How Throiy Chess handles your data: no cookies, no tracking.", body)

def notfound():
    body = header() + '''<main class="wrap"><div class="pagehead"><span class="eyebrow">404</span><h1 class="page">That square is empty.</h1>
<p>The page you were looking for doesn't exist (anymore).</p><div class="btns"><a class="btn solid" href="/">Back to the homepage</a><a class="btn" href="/shorts/">All Shorts</a></div></div></main>''' + footer()
    return page("/404.html", "Page not found · Throiy Chess", "Page not found.", body)

def llms_txt():
    lines = [f"# {NAME}", "", f"> {TAGLINE} Short chess lessons (YouTube Shorts, TikTok, Instagram, Facebook) about opening traps, "
             "how to avoid them, named mating patterns, and key moments from recent top-level games.", "",
             "## Trap lessons"]
    lines += [f"- [{t['name']}]({SITE}/traps/{t['slug']}/): {t['hook']} Opening: {t['opening']}. Moves: {t['moves']}" for t in TRAPS]
    lines += ["", "## Videos", f"- [All Shorts]({SITE}/shorts/)"] + [f"- [{s['title']}](https://www.youtube.com/shorts/{s['id']}): {s.get('desc', '')}" for s in SHORTS]
    lines += ["", "## Channels"] + [f"- [{n}]({u})" for n, u in LINKS] + ["", "## Optional", f"- [Contact]({SITE}/contact/)", f"- [Privacy]({SITE}/privacy/)"]
    return "\n".join(lines) + "\n"

def build():
    d = os.environ.get("OUT_DIR") or os.path.join(ROOT, "dist"); shutil.rmtree(d, ignore_errors=True) if not os.environ.get("OUT_DIR") else None
    shutil.copytree(os.path.join(ROOT, "src"), d, dirs_exist_ok=True)
    pages = [("/", home())] + shorts_pages() + [trap_page(t) for t in TRAPS] + [contact(), privacy()]
    for path, htm in pages:
        p = os.path.join(d, path.strip("/"), "index.html") if path != "/" else os.path.join(d, "index.html")
        os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(htm)
    open(os.path.join(d, "404.html"), "w").write(notfound())
    today = datetime.date.today().isoformat()
    open(os.path.join(d, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>\n" for p, _ in pages) + "</urlset>\n")
    open(os.path.join(d, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /m/\n\nSitemap: {SITE}/sitemap.xml\n")
    open(os.path.join(d, "llms.txt"), "w").write(llms_txt())
    open(os.path.join(d, "CNAME"), "w").write(DOMAIN + "\n"); open(os.path.join(d, ".nojekyll"), "w").write("")
    print("built", len(pages), "pages")

if __name__ == "__main__":
    build()
