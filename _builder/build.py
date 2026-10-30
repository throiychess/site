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
METRICOOL_HASH = "c6c03fb1179a18aed535c6088bf06fe6"  # Metricool web tracker (brand 7571701); "" = off
DONATE_URL = "https://ko-fi.com/throiychess"           # e.g. a Ko-fi page
NEWSLETTER_URL = "https://assets.mailerlite.com/jsonp/2747354/forms/202502436720478151/subscribe"  # MailerLite form (POST fields[email]); "" = off
PER_PAGE = 12

# ---------------- data ----------------
# Every YouTube Short. id = the part after youtube.com/shorts/ ; date = upload date (YYYY-MM-DD) ; trap = slug of a trap page (optional)
SHORTS = [  # newest first
    dict(id="paGdwe1cYmk", title="Free queen? Mate in 2! Légal's Mate", date="2026-10-27", topic="Légal's Mate",
         desc="White gives away the queen and mates in two moves. The fix: don't grab the queen, take the knight instead."),
    dict(id="fJiePOSCU9I", title="Free rook? Don't take it! Giri vs Abdusattorov", date="2026-10-26", topic="Top game",
         desc="Giri left his rook hanging on purpose. Abdusattorov took it, and White's attack crashed through. Before you grab something, check what your opponent gets.",
         credit="Thumbnail photos: Frans Peeters, CC BY-SA 2.0"),
    dict(id="TsHaDaBUS-c", title="Take my queen! The Stafford Gambit trap", date="2026-10-26", topic="Stafford Gambit",
         desc="Black gives away the queen on purpose. Take it and it's mate in two. The fix: don't pin the knight, just develop and castle."),
    dict(id="G2pqyA0mXF0", title="Don't take the bait! The Fishing Pole Trap", date="2026-10-25", topic="Ruy Lopez",
         desc="Black leaves a knight on g4 as bait. Take it and the h-file opens straight at your king, ending in mate on h1."),
    dict(id="WFRx-dXjOcc", title="Fried Liver Attack: mate in 9 (and how to stop it)", date="2026-10-24", topic="Italian Game",
         desc="White sacrifices a knight to drag Black's king into the open. The fix: don't take back in the center, attack the bishop instead."),
    dict(id="KA_x11CO7Gg", title="Don't fall for this Petrov trap", date="2026-10-22", topic="Petrov Defense",
         desc="Copying White's moves costs Black the queen. The fix: kick the knight away first, then take back the pawn."),
    dict(id="LCSXV_yJs_U", title="Stop the Scholar's Mate (and punish it)", date="2026-10-21", topic="Scholar's Mate",
         desc="Queen and bishop attack one weak square next to your king. Block the queen first, then make her run."),
    dict(id="9EOJdMBaPO4", title="He moved his king on move 5… big mistake", date="2026-10-19", topic="Opening mistakes",
         desc="No castling, a knight fork on f7 and a rook gone. In the opening, castle; don't move your king by hand."),
    dict(id="xF6KVwnOGCY", title="I fell for the oldest trick in chess", date="2026-10-18", topic="Scholar's Mate",
         desc="Queen and bishop against f7. Once they aim at f7, keep defending it."),
]

_feed = os.path.join(ROOT, "youtube.json")
if os.path.exists(_feed):
    _known = {s["id"] for s in SHORTS}
    _new = [v for v in json.load(open(_feed, encoding="utf-8")) if v["id"] not in _known]
    from traps import TRAPS as _TR
    def _norm(x): return x.lower().replace("’", "").replace("'", "")
    for v in _new:  # tidy auto-imported Shorts: the right label, and no title repeated at the start of the text
        _t = next((t for t in _TR if _norm(t["name"]) in _norm(v["title"])), None)
        v["topic"] = v.get("topic") or (_t["name"] if _t else "Top game" if " vs " in _norm(v["title"]) else "Video" if v.get("kind") == "video" else "New Short")
        d = v.get("desc", "")
        if d.startswith(v["title"]): v["desc"] = d[len(v["title"]):].lstrip(" :.-–—!?")
    for s in SHORTS:  # fill missing upload dates from the feed
        f = next((v for v in json.load(open(_feed, encoding="utf-8")) if v["id"] == s["id"]), None)
        if f and not s.get("date"): s["date"] = f["date"]
    SHORTS = sorted(_new + SHORTS, key=lambda s: s.get("date") or "", reverse=True)

LONG_IDS = set()   # ids of long (landscape) videos, in case the feed check misses one
VIDEOS = [s for s in SHORTS if s.get("kind") == "video" or s["id"] in LONG_IDS]
SHORTS = [s for s in SHORTS if s not in VIDEOS]

from traps import TRAPS  # the trap library lives in _builder/traps.py (one entry per trap page)
# library cards for lessons that have a Short but no playable page yet: (name, opening, text, short id or None)
OTHER = []  # extra cards for traps that have no page yet: (name, opening, hook, short id)

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
.card .cardimg{display:block;width:calc(100% + 44px);max-width:none;height:auto;aspect-ratio:1;object-fit:cover;margin:-22px -22px 8px;border-bottom:1px solid var(--line)}
a.card:hover .cardimg{filter:brightness(1.06)}
.card.soon{border-left-color:var(--line)}
/* shorts */
.shorts{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.short{display:grid;gap:10px;align-content:start;min-width:0}
.short h3{font-size:16px;line-height:1.3}
.short p{margin:0;color:var(--mute);font-size:14px}
.share{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;font-size:13px;margin-top:2px}
.share a,.share button{color:var(--mute);background:none;border:0;padding:0;font:inherit;cursor:pointer;text-decoration:underline;text-underline-offset:3px}
.share a:hover,.share button:hover{color:var(--gold)}.simple+.share,.pagehead+.share{margin:-12px 0 26px;font-size:14px}.share .sh-native{color:var(--gold);font-weight:700;text-decoration:none}
.short .label{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.short .credit{font-size:12px;opacity:.8}
.simple{background:var(--panel);border-left:4px solid var(--gold);padding:18px 22px;margin:0 0 32px;max-width:72ch;display:grid;gap:6px}
.simple p{margin:0;font-size:18px;line-height:1.5}
.vid{position:relative;aspect-ratio:9/16;width:100%;max-width:100%;background:var(--panel);overflow:hidden}
.vid.wide{aspect-ratio:16/9}
.videos{display:grid;grid-template-columns:repeat(2,1fr);gap:24px}
nav.links a.support{color:var(--gold)}
.supportbar{border:1px solid var(--line);padding:22px 24px;display:flex;gap:14px 24px;align-items:center;justify-content:space-between;flex-wrap:wrap;margin:8px 0 48px}
.supportbar p{margin:0;color:var(--mute)}.supportbar strong{color:var(--ink)}
.kofi{width:100%;max-width:460px;height:712px;border:0;background:#f9f9f9;display:block}
.newsletter{display:grid;grid-template-columns:1fr 1fr;gap:18px 32px;align-items:center;border:1px solid var(--line);border-radius:14px;padding:22px 24px;margin:40px 0 0}
.newsletter p{margin:6px 0 0;color:var(--mute)}
form.nl{display:flex;flex-wrap:wrap;gap:10px}.nl input[type=email]{box-sizing:border-box;min-width:0}.newsletter>*{min-width:0}form.nl input[type=email]{flex:1 1 220px;padding:12px 14px;border-radius:10px;border:1px solid var(--line);background:transparent;color:inherit;font:inherit}
form.nl .nl-msg{flex-basis:100%;margin:0}.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
@media (max-width:860px){.newsletter{grid-template-columns:1fr}}
.newsletter{background:var(--gold);color:var(--on-gold);border:0}.newsletter strong{font-size:20px}.newsletter p{color:rgba(20,17,11,.78)}
.newsletter form.nl input[type=email]{border:2px solid var(--on-gold);color:var(--on-gold);background:rgba(255,255,255,.35)}.newsletter form.nl input::placeholder{color:rgba(20,17,11,.6)}
.newsletter .btn.solid,.az-cta .btn.solid{background:var(--on-gold);color:var(--gold);border-color:var(--on-gold)}.newsletter a{color:var(--on-gold)}
.promo{background:var(--gold);color:var(--on-gold);font-weight:700;font-size:15px}.promo .wrap{display:flex;align-items:center;justify-content:center;gap:8px 16px;flex-wrap:wrap;padding-block:9px;position:relative}
.promo a{color:var(--on-gold);text-decoration:underline;text-underline-offset:3px;font-weight:900}.promo-x{position:absolute;right:0;top:50%;transform:translateY(-50%);background:none;border:0;color:var(--on-gold);font-size:22px;line-height:1;cursor:pointer;padding:6px 10px}
@media (max-width:560px){.promo{font-size:14px}.promo .wrap{padding-right:34px;justify-content:flex-start}}

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
@media (max-width:700px){.videos{grid-template-columns:1fr}}
@media (max-width:900px){.shorts{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr 1fr}}
@media (max-width:860px){.hero,.player,.twocol{grid-template-columns:1fr}.hero{padding-block:32px}.breaking{grid-template-columns:1fr;gap:14px}.about{grid-template-columns:1fr}.about img{width:150px}}
@media (max-width:560px){.grid{grid-template-columns:1fr}.brand img{height:46px}.brand{font-size:19px}nav.links{gap:0 18px;flex-wrap:nowrap;overflow-x:auto;width:100%;scrollbar-width:none;-webkit-overflow-scrolling:touch;mask-image:linear-gradient(90deg,#000 88%,transparent);-webkit-mask-image:linear-gradient(90deg,#000 88%,transparent)}nav.links::-webkit-scrollbar{display:none}nav.links a{white-space:nowrap;padding-block:8px}html{scroll-padding-top:120px}}
@media (prefers-reduced-motion:no-preference){.btn,.card{transition:background .15s,filter .15s}}
"""
e = html.escape

GOOGLE_LOGIN = True  # set True after enabling the Google provider in Supabase
TURNSTILE_SITEKEY = "0x4AAAAAAFso4wm5naB8oZGB"  # public Cloudflare Turnstile site key (secret lives in Supabase Auth > Attack Protection)

def csp(path=""):
    conn = ["'self'"] + (["https://api.web3forms.com"] if WEB3FORMS_KEY else []) + ([f"https://{ANALYTICS}.goatcounter.com"] if ANALYTICS else []) + (["https://assets.mailerlite.com"] if NEWSLETTER_URL else []) + ["https://api.chess.com", "https://lichess.org", "https://ytxrrmvszifvtdyilezn.supabase.co"] + (["https://tracker.metricool.com"] if METRICOOL_HASH else [])
    scr = ["'self'", "'unsafe-inline'"] + (["https://gc.zgo.at"] if ANALYTICS else []) + (["https://tracker.metricool.com"] if METRICOOL_HASH else [])
    img = "img-src 'self' data:" + (" https://tracker.metricool.com" if METRICOOL_HASH else "")
    hc = path.startswith("/members") and TURNSTILE_SITEKEY
    gg = path.startswith("/members") and GOOGLE_LOGIN
    if gg: scr += ["https://accounts.google.com"]; conn += ["https://accounts.google.com"]
    if hc: scr += ["https://challenges.cloudflare.com"]
    return (f"default-src 'self'; {img}; style-src 'self' 'unsafe-inline'{' https://accounts.google.com/gsi/style' if gg else ''}; font-src 'self'; "
            f"script-src {' '.join(scr)}; connect-src {' '.join(conn)}; frame-src https://www.youtube-nocookie.com https://ko-fi.com{' https://challenges.cloudflare.com' if hc else ''}{' https://accounts.google.com' if gg else ''}; "
            "form-action 'self' https://api.web3forms.com" + (" https://assets.mailerlite.com" if NEWSLETTER_URL else "") + "; base-uri 'self'; object-src 'none'")

def page(path, title, desc, body, jsonld=None, og_image="/img/og.jpg", ogtype="website"):
    url = SITE + path
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    gc = (f'<script data-goatcounter="https://{ANALYTICS}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>' if ANALYTICS else "")
    if METRICOOL_HASH:  # official Metricool loader snippet
        gc += ('<script>function loadScript(a){var b=document.getElementsByTagName("head")[0],c=document.createElement("script");'
               'c.type="text/javascript",c.src="https://tracker.metricool.com/resources/be.js",c.onreadystatechange=a,c.onload=a,b.appendChild(c)}'
               'loadScript(function(){beTracker.t({hash:"' + METRICOOL_HASH + '"})});</script>')
    if path.startswith("/members"): gc = ""  # no third-party scripts where auth codes appear in the URL
    elif path.startswith("/analyze"): gc = gc.split("<script>function loadScript")[0]  # keep GoatCounter only
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<meta http-equiv="Content-Security-Policy" content="{csp(path)}"><meta name="referrer" content="strict-origin-when-cross-origin">'
            f'<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">'
            f'<link rel="icon" href="/img/favicon.png"><link rel="apple-touch-icon" href="/img/logo-small.png"><meta name="theme-color" content="#0e0d0b">'
            f'<meta property="og:site_name" content="{NAME}"><meta property="og:type" content="{ogtype}"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}{og_image}">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<link rel="preload" href="/fonts/Inter-Black.woff" as="font" type="font/woff" crossorigin>'
            + ('<meta name="robots" content="noindex,nofollow">' if path == '/members/' else '')
            + f'<style>{CSS}</style>{ld}{gc}</head><body>{body}{SCRIPT}<script src="/js/fb.js" defer></script></body></html>')

def promo_bar(active):
    if active == "Free": return ""
    return ('<div class="promo"><div class="wrap"><span>Free: 10 Opening Traps cheat sheet + quiz, made for your phone.</span>'
            '<a data-ev="promo-bar-click" href="/free/?utm_source=site&amp;utm_campaign=promo-bar">Get it free &rarr;</a>'
            '<button class="promo-x" type="button" aria-label="Close" onclick="try{sessionStorage.setItem(\'promo\',1)}catch(e){}this.closest(\'.promo\').remove()">&times;</button></div></div>'
            '<script>try{if(sessionStorage.getItem("promo"))document.querySelector(".promo").remove()}catch(e){}</script>')
NAVG = [("Watch", [("Shorts", "/shorts/"), ("Videos", "/videos/"), ("Top games", "/#top-games")]),
        ("Train", [("Traps", "/traps/"), ("Analyze", "/analyze/")]),
        ("About", [("About", "/#about"), ("Contact", "/contact/")]), ("Support", "/support/")]
NAV = [(n, u) for g, x in NAVG for (n, u) in (x if isinstance(x, list) else [(g, x)])]
_KEY = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3M14 9l2 2"/></svg>'
NAV_CSS = """<style>
nav.links{overflow:visible!important;-webkit-mask-image:none!important;mask-image:none!important;width:auto!important;flex-wrap:nowrap!important;gap:0 22px!important;align-items:center}
.ddb{font:inherit;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);background:none;border:0;cursor:pointer;padding:8px 0}
.ddb::after{content:"";display:inline-block;width:5px;height:5px;border:solid currentColor;border-width:0 2px 2px 0;transform:rotate(45deg);margin:0 0 3px 8px}
.dd{position:relative}.dd:hover .ddb,.dd.cur .ddb,.dd.open .ddb{color:var(--gold)}
.ddm{display:none;position:absolute;top:100%;left:-14px;min-width:200px;padding:8px;background:#17150f;border:1px solid var(--line);border-radius:14px;box-shadow:0 18px 40px rgba(0,0,0,.5);z-index:5}
.dd:hover .ddm,.dd:focus-within .ddm,.dd.open .ddm{display:block}
.ddm a{display:block;padding:10px 12px!important;border-radius:9px;white-space:nowrap}.ddm a:hover{background:#221d10}
.burger{display:none;background:none;border:1px solid var(--line);border-radius:10px;color:var(--ink);padding:9px 12px;font:inherit;font-weight:700;font-size:13px;letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
nav.links a.cta{background:var(--gold);color:var(--on-gold);border-radius:99px;padding:8px 18px!important;font-weight:800}nav.links a.cta:hover{filter:brightness(1.08);color:var(--on-gold)}
.acct{display:flex;align-items:center;margin-left:4px}
nav.links a.login{display:inline-flex;align-items:center;gap:8px;border:1px solid #4a3d1c;border-radius:99px;padding:6px 14px 6px 10px!important;color:var(--gold)}
nav.links a.login svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.acct-in{display:none}[data-in="1"] .acct-in{display:block}[data-in="1"] nav.links a.acct-out{display:none!important}
.avab{width:46px;height:46px;border-radius:50%;border:2px solid #7c87a8;background:#2b2f3a;color:var(--gold);font-size:30px;line-height:1;cursor:pointer;display:grid;place-items:center;padding:0}
.acct-in .ddm{left:auto;right:0;min-width:210px;top:calc(100% + 12px);background:#2b2f3a;border:1px solid #4b5163;padding:10px}.acct-in .ddm::before{content:"";position:absolute;left:0;right:0;top:-14px;height:14px}.acct-in .ddm::after{content:"";position:absolute;top:-7px;right:17px;width:12px;height:12px;background:#2b2f3a;border-left:1px solid #4b5163;border-top:1px solid #4b5163;transform:rotate(45deg)}.acct-in .ddm a{color:#c9cfdd}.acct-in .ddm a:hover{background:#383d4b;color:#fff}.acct-in .ddm a.out{color:#f0a294}
@media(max-width:860px){.burger{display:block}header.top .wrap{flex-wrap:wrap}
nav.links{display:none!important;order:3;width:100%!important;flex-direction:column;align-items:stretch!important;gap:2px!important;padding:4px 0 14px}
nav.links.open{display:flex!important}
.ddb{pointer-events:none;font-size:11.5px;color:#7d745f;padding:12px 0 2px;text-align:left}.ddb::after{display:none}
.ddm{display:block;position:static;background:none;border:0;box-shadow:none;padding:0;min-width:0}
.ddm a,nav.links>a{padding:11px 4px!important;font-size:15px!important}
nav.links a.cta{order:-2;text-align:center;margin:6px 0 4px;padding:13px 18px!important;font-size:15px!important}
.acct{order:-1;margin:0 0 4px;display:block}nav.links a.login{width:100%;justify-content:center;padding:11px!important}
.acct-in .ddb{display:none}.acct-in .ddm{position:static;display:block;border-top:1px solid var(--line);border-radius:0;padding-top:8px;background:none;border-left:0;border-right:0;border-bottom:0;margin-top:0}.acct-in .ddm::before,.acct-in .ddm::after{display:none}.acct-in .ddm a{color:var(--mute)}.acct-in .avab{display:none}
.acct-in{width:100%}}
</style>"""
NAV_JS = """<script>(function(){var h=document.querySelector("header.top"),n=h.querySelector("nav.links"),b=h.querySelector(".burger"),i=false,a="";
try{var k=Object.keys(localStorage).filter(function(x){return/^sb-.*-auth-token$/.test(x)})[0];if(k){var s=JSON.parse(localStorage.getItem(k));i=!!(s&&s.refresh_token)}a=localStorage.getItem("tc_av")||""}catch(e){}
if(i){document.documentElement.setAttribute("data-in","1");h.querySelectorAll('a[href="/analyze/"]').forEach(function(x){x.setAttribute("href","/members/#analyze")});var g=h.querySelector(".avab");if(g&&a)g.textContent=a}
b.addEventListener("click",function(){var o=n.classList.toggle("open");b.setAttribute("aria-expanded",o)});
h.querySelectorAll(".ddb,.avab").forEach(function(x){x.addEventListener("click",function(e){var d=x.closest(".dd,.acct-in"),o=d.classList.contains("open");h.querySelectorAll(".open").forEach(function(y){if(y!==n)y.classList.remove("open")});if(!o)d.classList.add("open");x.setAttribute("aria-expanded",!o);e.stopPropagation()})});
document.addEventListener("click",function(){h.querySelectorAll(".dd.open,.acct-in.open").forEach(function(y){y.classList.remove("open")})});
document.addEventListener("keydown",function(e){if(e.key==="Escape"){h.querySelectorAll(".dd.open,.acct-in.open").forEach(function(y){y.classList.remove("open")});n.classList.remove("open")}})})();</script>"""
def _nl(n, u, active):
    cls = " class=support" if n == "Support" else ""
    return f'<a href="{u}"{cls}{" aria-current=page" if n == active else ""}>{n}</a>'
def _nav_html(active):
    out = []
    for g, x in NAVG:
        if isinstance(x, list):
            cur = " cur" if any(n == active for n, _ in x) else ""
            out.append(f'<div class="dd{cur}"><button type="button" class="ddb" aria-haspopup="true" aria-expanded="false">{g}</button><div class="ddm">' + "".join(_nl(n, u, active) for n, u in x) + '</div></div>')
        else:
            out.append(_nl(g, x, active))
    out.append(f'<a class="cta" href="/improve/"{" aria-current=page" if active == "Improve" else ""}>Improve</a>')
    out.append('<div class="acct"><a class="login acct-out" href="/members/">' + _KEY + 'Log in</a>'
               '<div class="dd acct-in"><button type="button" class="avab" aria-haspopup="true" aria-expanded="false" aria-label="Your account">&#9823;&#xFE0E;</button><div class="ddm">'
               '<a href="/members/#overview">Overview</a><a href="/members/#analyze">Analyze</a><a href="/members/#reports">My reports</a><a href="/members/#earn">Share &amp; earn</a><a href="/members/#profile">Profile</a><a class="out" href="/members/#logout">Log out</a></div></div></div>')
    return "".join(out)
def header(active=""):
    return promo_bar(active) + NAV_CSS + ('<header class="top"><div class="wrap"><a class="brand" href="/" aria-label="Throiy Chess home"><img src="/img/logo-small.png" width="96" height="161" alt="">'
            '<span>THROIY<b>CHESS</b></span></a><button class="burger" type="button" aria-controls="mainnav" aria-expanded="false">Menu</button><nav class="links" id="mainnav" aria-label="Main">'
            + _nav_html(active) + '</nav></div></header>') + NAV_JS

def support_bar():
    return ('<div class="wrap"><div class="supportbar"><p><strong>Enjoying the lessons?</strong> They stay free. A small tip keeps new traps coming every day.</p>'
            '<a class="btn solid" href="/support/">Support Throiy Chess</a></div></div>') if DONATE_URL else ""

def newsletter():
    if not NEWSLETTER_URL: return ""
    return ('<div class="wrap"><div class="newsletter"><div><strong>One trap a week in your inbox.</strong>'
            '<p>The best trap of the week, explained in plain words. Free, no spam, unsubscribe in one click.</p></div>'
            f'<form class="nl" action="{e(NEWSLETTER_URL)}" method="post" target="_blank">'
            '<label class="sr" for="nl-email">E-mail address</label>'
            '<input id="nl-email" type="email" name="fields[email]" placeholder="Your e-mail" autocomplete="email" required>'
            '<input type="hidden" name="ml-submit" value="1"><input type="hidden" name="anticsrf" value="true">'
            '<div class="hp" aria-hidden="true"><input type="text" name="nl_website" tabindex="-1" autocomplete="off"></div>'
            '<button class="btn solid" type="submit">Subscribe</button>'
            '<p class="nl-msg small" role="status" aria-live="polite"></p></form></div></div>')

def footer(band=True, nl=True):
    ext = " ".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in LINKS)
    return ((newsletter() if nl else "") + (support_bar() if band else "") + f'<footer><div class="wrap"><span>© {datetime.date.today().year} Throiy Chess · Quick chess lessons, every day</span>'
            f'<nav aria-label="Footer">{ext}<a href="/support/">Support</a><a href="/contact/">Contact</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a></nav></div></footer>')

# click-to-load YouTube (no request to YouTube until the visitor presses play)
SCRIPT = """<script>
function gcEv(n){try{if(window.goatcounter&&goatcounter.count)goatcounter.count({path:n,title:n,event:true})}catch(e){}}
document.addEventListener("click",function(ev){var d=ev.target.closest("[data-ev]");if(d)gcEv(d.dataset.ev);var a=ev.target.closest("a[href]");if(a){if(a.host&&a.host!==location.host)gcEv("out-"+a.host.replace(/^www\\./,""));else if(a.pathname==="/support/")gcEv("click-support");}var y=ev.target.closest("button[data-yt]");if(y)gcEv("play-"+y.dataset.yt);var sh=ev.target.closest(".share button");if(sh)gcEv("share-"+(sh.dataset.app||(sh.classList.contains("sh-native")?"native":"copy")))});
window.addEventListener("blur",function(){var f=document.activeElement;if(f&&f.tagName==="IFRAME"&&f.src.indexOf("ko-fi.com")>-1&&!window.kfC){window.kfC=1;gcEv("kofi-panel-click")}});
document.addEventListener("click",function(ev){var b=ev.target.closest("button[data-yt]");if(!b)return;var f=document.createElement("iframe");
f.src="https://www.youtube-nocookie.com/embed/"+b.dataset.yt+"?autoplay=1&rel=0&playsinline=1";f.title=b.dataset.title||"YouTube Short";
f.allow="autoplay; encrypted-media; picture-in-picture";f.allowFullscreen=true;f.referrerPolicy="strict-origin-when-cross-origin";b.replaceWith(f)});
document.addEventListener("click",function(ev){var b=ev.target.closest(".share button");if(!b)return;var w=b.closest(".share"),u=w.dataset.url,t=w.dataset.text;
var app=b.dataset.app,m=w.querySelector(".sh-msg");
if((b.classList.contains("sh-native")||app)&&navigator.share&&matchMedia("(pointer:coarse)").matches){navigator.share({title:t,url:u}).catch(function(){});return}
if(b.classList.contains("sh-native")&&navigator.share){navigator.share({title:t,url:u}).catch(function(){});return}
(navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(function(){m.textContent=app?"Link copied. Paste it in your "+app+" story, bio or DM.":"Link copied!";setTimeout(function(){m.textContent=""},4000)}).catch(function(){prompt("Copy this link:",u)})});
document.addEventListener("submit",function(ev){var fm=ev.target;if(!fm.matches("form.nl"))return;ev.preventDefault();var m=fm.querySelector(".nl-msg");
if(fm.nl_website&&fm.nl_website.value)return;var d=new FormData(fm);d.delete("nl_website");m.textContent="Sending…";
fetch(fm.action,{method:"POST",body:d}).then(function(r){return r.json()}).then(function(j){if(j&&j.success){fm.querySelector("input[type=email]").value="";
gcEv(fm.dataset.ev||"newsletter-signup");if(fm.dataset.msg){m.textContent=fm.dataset.msg;}else if(fm.dataset.dl){gcEv("cheatsheet-signup");m.innerHTML='You&#39;re in! <a class="btn solid" data-ev="cheatsheet-open" href="'+fm.dataset.dl+'" target="_blank" rel="noopener">Open the cheat sheet (PDF)</a>';}else{m.textContent="You're in! The next trap lands in your inbox.";}}else{m.textContent="That didn't work. Check the address and try again.";}})
.catch(function(){gcEv("newsletter-signup-newtab");if(fm.dataset.dl){m.innerHTML='Almost there: confirm in the new tab, then <a data-ev="cheatsheet-open" href="'+fm.dataset.dl+'" target="_blank" rel="noopener">open the cheat sheet</a>.';}else{m.textContent="Opening the sign-up in a new tab…";}fm.submit();})});
</script>"""
THUMBS = os.path.join(ROOT, "src", "img", "yt")
def fetch_thumbs(items):
    """Self-hosted thumbnails (no request to YouTube until play).
    Own designs: commit src/img/yt/<id>.jpg (no .auto marker) -> never touched.
    Missing ones are downloaded from YouTube at build time and marked <id>.auto; auto ones from the last 21 days
    are refreshed every run, so a thumbnail changed on YouTube shows up on the site too.
    Shorts: YouTube's custom thumbnail is maxresdefault (landscape, letterboxed) -> the 9:16 middle is cut out."""
    import urllib.request, io, datetime
    os.makedirs(THUMBS, exist_ok=True)
    today = datetime.date.today()
    def get(name, vid):
        try:
            d = urllib.request.urlopen(f"https://i.ytimg.com/vi/{vid}/{name}", timeout=15).read()
            return d if len(d) > 2000 else None
        except Exception: return None
    for s in items:
        p = os.path.join(THUMBS, s["id"] + ".jpg"); auto = p[:-4] + ".auto"
        if os.path.exists(p) and not os.path.exists(auto): continue          # own design
        if os.path.exists(p):
            try: age = (today - datetime.date.fromisoformat(s.get("date") or "2000-01-01")).days
            except ValueError: age = 999
            if age > 21: continue
        data = None
        if s.get("kind") == "video":
            data = get("maxresdefault.jpg", s["id"]) or get("hqdefault.jpg", s["id"])
        else:
            mx = get("maxresdefault.jpg", s["id"])
            if mx:
                try:
                    from PIL import Image
                    im = Image.open(io.BytesIO(mx)).convert("RGB"); w, h = im.size; cw = int(h * 9 / 16)
                    im = im.crop(((w - cw) // 2, 0, (w - cw) // 2 + cw, h)); b = io.BytesIO(); im.save(b, "JPEG", quality=88); data = b.getvalue()
                except Exception: data = None
            data = data or get("oar2.jpg", s["id"]) or get("hqdefault.jpg", s["id"])
        if data:
            open(p, "wb").write(data); open(auto, "w").write("auto-fetched from YouTube; delete this file to keep the image as an own design\n")

def thumb_style(s):
    if not os.path.exists(os.path.join(THUMBS, s["id"] + ".jpg")): return ""
    return (f' style="background-image:linear-gradient(180deg,rgba(14,13,11,0) 55%,rgba(14,13,11,.85)),url(/img/yt/{e(s["id"])}.jpg);'
            'background-size:cover;background-position:center"')

from urllib.parse import quote
def share_bar(url, text):
    """Share links without third-party scripts: native share sheet on phones, plus plain links."""
    u, t = quote(url, safe=""), quote(text, safe="")
    return (f'<div class="share" data-url="{e(url)}" data-text="{e(text)}"><button type="button" class="sh-native">Share</button>'
            f'<a href="https://wa.me/?text={t}%20{u}" target="_blank" rel="noopener" aria-label="Share on WhatsApp">WhatsApp</a>'
            f'<a href="https://www.facebook.com/sharer/sharer.php?u={u}" target="_blank" rel="noopener" aria-label="Share on Facebook">Facebook</a>'
            f'<a href="https://twitter.com/intent/tweet?url={u}&amp;text={t}" target="_blank" rel="noopener" aria-label="Share on X">X</a>'
            '<button type="button" class="sh-app" data-app="Instagram">Instagram</button><button type="button" class="sh-app" data-app="TikTok">TikTok</button>'
            '<button type="button" class="sh-copy">Copy link</button><span class="sh-msg small" role="status" aria-live="polite"></span></div>')

def _nm(x): return x.lower().replace("’", "").replace("'", "")
def trap_short(t):
    """The Short that belongs to a trap: the explicit id, otherwise the newest Short whose title names the trap."""
    return next((s for s in SHORTS if s["id"] == t.get("short")), None) or next((s for s in SHORTS if _nm(t["name"]) in _nm(s["title"])), None)

def short_url(s):
    t = next((t for t in TRAPS if (trap_short(t) or {}).get("id") == s["id"]), None)
    return f"{SITE}/traps/{t['slug']}/" if t else f"{SITE}/shorts/#s-{s['id']}"

def short_card(s):
    cr = f'<p class="small credit">{e(s["credit"])}</p>' if s.get("credit") else ""
    return (f'<article class="short" id="s-{e(s["id"])}"><div class="vid"><button type="button" data-yt="{e(s["id"])}" data-title="{e(s["title"])}" aria-label="Play: {e(s["title"])}"{thumb_style(s)}>'
            f'<span class="play"></span><small>Plays from YouTube. Pressing play loads YouTube.</small></button></div>'
            f'<span class="label">{e(s.get("topic", ""))}</span><h3>{e(s["title"])}</h3><p>{e(s.get("desc", ""))}</p>{cr}{share_bar(short_url(s), s["title"])}</article>')

def video_ld(s):
    if not s.get("date"): return None
    return {"@context": "https://schema.org", "@type": "VideoObject", "name": s["title"], "description": s.get("desc", s["title"]),
            "uploadDate": (s["date"] if "T" in s["date"] else s["date"] + "T12:00:00+01:00"), "thumbnailUrl": f"https://i.ytimg.com/vi/{s['id']}/hqdefault.jpg",
            "embedUrl": f"https://www.youtube-nocookie.com/embed/{s['id']}", "contentUrl": (f"https://www.youtube.com/watch?v={s['id']}" if s.get("kind") == "video" else f"https://www.youtube.com/shorts/{s['id']}")}

ORG = {"@context": "https://schema.org", "@type": "Organization", "name": NAME, "alternateName": ["ThroiyChess", "Throiy"], "slogan": "Chess traps and lessons, explained fast", "url": SITE, "logo": SITE + "/img/logo.png",
       "sameAs": [u for _, u in LINKS], "description": TAGLINE}

# ---------------- pages ----------------
HOME_TRAPS = 6
def trap_img(t):
    return f"/img/traps/{t['slug']}.jpg" if os.path.exists(os.path.join(ROOT, "src", "img", "traps", t["slug"] + ".jpg")) else None

def trap_card(t):
    im = trap_img(t)
    pic = f'<img class="cardimg" src="{im}" width="720" height="720" loading="lazy" alt="Key position of the {e(t["name"])}">' if im else ""
    return (f'<a class="card" href="/traps/{t["slug"]}/">{pic}<div class="meta"><span class="label">{e(t["opening"])}</span></div>'
            f'<h3>{e(t["name"])}</h3><p>{e(t["hook"])}</p><span class="go">Play through the trap →</span></a>')

def traps_index():
    body = header("Traps") + f'''<main class="wrap"><div class="pagehead"><span class="eyebrow">Trap library</span>
<h1 class="page">Learn the trap. Then the fix.</h1><p>{len(TRAPS)} opening traps, each explained in plain words first, then move by move on the board.</p></div>
<div class="grid">{"".join(trap_card(t) for t in TRAPS)}</div><div style="height:56px"></div></main>''' + footer()
    return "/traps/", page("/traps/", "Trap library · Throiy Chess", f"{len(TRAPS)} chess opening traps explained in plain words, with the fix for each.", body)

def home():
    cards = "".join(trap_card(t) for t in TRAPS[:HOME_TRAPS])
    for n, o, h, sid in OTHER:
        href = f"https://www.youtube.com/shorts/{sid}" if sid else LINKS[0][1] + "/shorts"
        cards += (f'<a class="card soon" href="{href}" target="_blank" rel="noopener"><div class="meta"><span class="label">{e(o)}</span></div>'
                  f'<h3>{e(n)}</h3><p>{e(h)}</p><span class="go">Watch the Short →</span></a>')
    latest = "".join(short_card(s) for s in SHORTS[:4])
    _top = [s for s in SHORTS if s.get("topic") == "Top game"]
    top_cards = (f'<div class="sechead" style="margin-top:28px"><div><span class="eyebrow">Top games</span><h2>The best moments from elite chess.</h2></div><a class="btn" href="/shorts/">All Shorts →</a></div>'
                 f'<div class="shorts">{"".join(short_card(s) for s in _top[:4])}</div>') if _top else ""
    body = header() + f'''<main>
<div class="wrap hero"><div class="copy"><span class="eyebrow">Throiy Chess · Lessons &amp; Games</span>
<h1>Stop falling for <em>chess traps.</em></h1>
<p class="lead">Opening traps, mating patterns and the best moments from top games. Each one explained in under a minute.</p>
<div class="btns"><a class="btn solid" href="/shorts/">Watch the Shorts</a><a class="btn" href="#traps">Browse the traps</a></div></div>
<div class="ticks"><img src="/img/fishing-pole-board.jpg" width="720" height="720" alt="Final position of the Fishing Pole Trap: Black's queen mates on h1"><i class="t1"></i><i class="t2"></i></div></div>
<section id="shorts"><div class="wrap"><div class="sechead"><div><span class="eyebrow">Latest Shorts</span><h2>One lesson a day, under a minute.</h2></div>
<a class="btn" href="/shorts/">All Shorts →</a></div><div class="shorts">{latest}</div></div></section>
<section id="traps"><div class="wrap"><div class="sechead"><div><span class="eyebrow">Trap library</span><h2>Learn the trap. Then learn the fix.</h2>
<p>Every trap ends with the mate. Every lesson ends with how to avoid it. Step through the moves on the board.</p></div>
<a class="btn" href="/traps/">All {len(TRAPS)} traps →</a></div>
<div class="grid">{cards}</div></div></section>
<section id="top-games"><div class="wrap"><div class="breaking"><span class="live">Top games</span><div><h3>Clutch Chess: Champions Showdown · 27–29 October</h3>
<p>Nakamura, Caruana, Praggnanandhaa and Sindarov play rapid chess. We break down the sharpest moment of each day in a Short.</p></div></div>{top_cards}</div></section>
<section id="about"><div class="wrap about"><img src="/img/avatar-thumbs_up.png" width="220" height="220" alt="Throiy, illustrated, giving a thumbs up">
<div><span class="eyebrow">About</span><h2>Hi, I'm Throiy.</h2><p>I'm a chess player sharing what I wish I'd known sooner. Short, clear lessons you can use in your next game. A new one every day on YouTube, TikTok, Instagram and Facebook.</p>
<div class="btns" style="margin-top:18px">''' + "".join(f'<a class="btn" href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in LINKS) + \
        ('<a class="btn solid" href="/support/">Support the channel</a>' if DONATE_URL else "") + '''</div></div></div></section>
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
    assert b.is_checkmate() or not t.get("mate", True), t["slug"]
    notes = {k: dict(label=v[0], tag=v[1], text=v[2], marks=(v[3] if len(v) > 3 else [])) for k, v in t["notes"].items()}
    mv_html = ""
    for i, p in enumerate(plies[1:], 1):
        if i % 2: mv_html += f'<span>{(i + 1) // 2}.</span>'
        mv_html += f'<button type="button" data-p="{i}">{e(p["san"])}</button>'
    data = json.dumps(dict(plies=plies, notes=notes))
    fix = "".join(f"<li><span>{e(x)}</span></li>" for x in t["fix"])
    sh = trap_short(t)
    side = (short_card(sh) if sh else
            f'<div class="card"><span class="label">Watch</span><h3>The {e(t["name"])} as a Short</h3><p>All lessons are on YouTube, TikTok and Instagram.</p>'
            f'<a class="go" href="{LINKS[0][1]}/shorts" target="_blank" rel="noopener">Watch on YouTube →</a></div>')
    path = f'/traps/{t["slug"]}/'
    body = header("Traps") + f'''<main class="wrap"><div class="crumb"><a href="/traps/">Trap library</a> / {e(t["name"])}</div>
<div class="pagehead" style="padding-top:18px"><span class="eyebrow">{e(t["opening"])} · {e(t["side"])}</span><h1 class="page">{e(t["name"])}</h1><p>{e(t["hook"])}</p></div>
{f'<div class="simple"><span class="eyebrow">In plain words</span><p>{e(t["simple"])}</p></div>' if t.get("simple") else ""}
{share_bar(SITE + f'/traps/{t["slug"]}/', t["name"] + ": " + t["hook"])}
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
           "mainEntityOfPage": SITE + path, "image": SITE + (trap_img(t) or "/img/og.jpg")}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Trap library", "item": SITE + "/traps/"},
        {"@type": "ListItem", "position": 2, "name": t["name"], "item": SITE + path}]}
    return path, page(path, f'{t["name"]}: moves, mate and how to avoid it · Throiy Chess', t["hook"] + " Step through every move on the board.", body,
                      [art, crumbs] + ([video_ld(sh)] if sh and video_ld(sh) else []), og_image=trap_img(t) or "/img/og.jpg", ogtype="article")

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
    if CONTACT_EMAIL:
        u, d = CONTACT_EMAIL.split("@")
        mail = (f'<p class="small">Or e-mail us: <a id="ml" href="/contact/">{e(u)} [at] {e(d.replace(".", " [dot] "))}</a></p>'
                f'<script>(function(){{var a=document.getElementById("ml"),m=["{e(u)}","{e(d)}"].join("@");a.textContent=m;a.href="mailto:"+m}})();</script>')
    else: mail = ""
    body = header("Contact") + f'''<main class="wrap"><div class="pagehead"><span class="eyebrow">Contact</span><h1 class="page">Say hi.</h1>
<p>A question, a trap you want explained, or a collaboration? Send a message.</p></div>
<div class="twocol" style="padding-bottom:64px"><div>{form}{mail}</div><aside><img src="/img/avatar-thumbs_up.png" width="300" height="300" alt="Throiy, illustrated, giving a thumbs up" style="width:100%;max-width:260px;height:auto"></aside></div></main>''' + footer()
    return "/contact/", page("/contact/", "Contact · Throiy Chess", "Get in touch with Throiy Chess: questions, trap requests and collaborations.", body)

def privacy():
    body = header() + f'''<main class="wrap"><div class="pagehead"><span class="eyebrow">Privacy</span><h1 class="page">Privacy statement</h1>
<p>Short version: no cookies, no tracking, and we never sell your data.</p></div>
<div class="prose" style="padding-bottom:64px">
<h2>Who we are</h2><p>Throiy Chess is a chess education channel from the Netherlands. This statement covers {DOMAIN}.</p>
<h2>Visiting the site</h2><p>This site sets no cookies. An account is optional: if you log in, your login session is kept in your browser's local storage on this device. Our hosting provider processes your IP address to deliver the pages and keep them secure.{" Visits are counted with cookie-free tools (GoatCounter" + (" and Metricool" if METRICOOL_HASH else "") + ") that store no personal data." if ANALYTICS else ""}</p>
<h2>Videos</h2><p>Videos come from YouTube and only load when you press play. From then on, YouTube (Google) receives your IP address and may set cookies under its own privacy policy.</p>
<h2>Contact</h2><p>When you send a message, we receive your name, e-mail address and message. We use them only to reply, and delete them within a year.</p>
{"<h2>Newsletter</h2><p>If you subscribe, your e-mail address is stored by our mailing service MailerLite (EU). We use it only to send the newsletter. Every e-mail has an unsubscribe link, and we delete your address when you unsubscribe.</p>" if NEWSLETTER_URL else ""}
<h2>Members (optional account)</h2><p>If you create an account, we store your e-mail address, the profile details you enter, the social channels you say you follow, and the analysis reports you choose to save. They are stored with our database provider Supabase in the EU (Frankfurt) and are visible only to you and us. We use them to show your progress and for nothing else. You can delete saved reports yourself on your members page; you can delete your whole account yourself with one button on your members page.</p>
<h2>Support</h2><p>Tips are handled by Ko-fi on its own payment page, under its own privacy policy. We see your name and message if you leave them, never your payment details.</p>
<h2>Your rights</h2><p>Ask us via the <a href="/contact/">contact page</a> what we hold about you, or to correct or delete it. You can also complain to the Dutch Data Protection Authority (Autoriteit Persoonsgegevens).</p>
<p class="small">Last updated: {datetime.date.today().strftime("%d %B %Y")}</p></div></main>''' + footer()
    return "/privacy/", page("/privacy/", "Privacy · Throiy Chess", "How Throiy Chess handles your data: no cookies, no tracking.", body)

def video_card(s):
    return (f'<article class="short" id="v-{e(s["id"])}"><div class="vid wide"><button type="button" data-yt="{e(s["id"])}" data-title="{e(s["title"])}" aria-label="Play: {e(s["title"])}"{thumb_style(s)}>'
            f'<span class="play"></span><small>Plays from YouTube. Pressing play loads YouTube.</small></button></div>'
            f'<h3>{e(s["title"])}</h3><p>{e(s.get("desc", ""))}</p>{share_bar(SITE + "/videos/#v-" + s["id"], s["title"])}</article>')

def videos_page():
    if VIDEOS: inner = f'<div class="videos">{"".join(video_card(v) for v in VIDEOS)}</div>'
    else: inner = ('<div class="supportbar"><p><strong>First long video: 10 Opening Traps Every Beginner Must Know.</strong> '
                   'Premieres on YouTube on 28 October and appears here automatically.</p>'
                   f'<a class="btn solid" href="{LINKS[0][1]}" target="_blank" rel="noopener">Subscribe on YouTube</a></div>')
    body = header("Videos") + f'''<main class="wrap"><div class="pagehead"><span class="eyebrow">Videos</span>
<h1 class="page">The full lessons.</h1><p>Longer videos that go deeper: several traps in one go, with the setup, the bait, the punishment and the fix. For quick lessons, see the <a href="/shorts/">Shorts</a>.</p></div>
{inner}<div style="height:48px"></div></main>''' + footer()
    return "/videos/", page("/videos/", "Videos · Throiy Chess", "Full-length Throiy Chess videos: opening traps and how to avoid them, explained step by step.",
                            body, [v for v in map(video_ld, VIDEOS) if v])

def support_page():
    body = header("Support") + f'''<main class="wrap"><div class="pagehead"><span class="eyebrow">Support</span>
<h1 class="page">Keep the lessons free.</h1><p>Every Short and every trap page on this site is free, without ads on the site and without a paywall. If they helped you win a game (or stop losing one), you can say thanks with a small tip.</p></div>
<div class="twocol" style="padding-bottom:64px"><div class="prose">
<h2>Why support?</h2>
<p>Each lesson takes hours: finding the trap, checking every move with a chess engine, writing and recording the voice-over, and building the animation on our own board. Tips pay for the tools and hosting, and buy time to make more.</p>
<h2>How it works</h2>
<p>Choose an amount in the panel and pay with card or PayPal. The payment runs through Ko-fi, so we never see your payment details. A one-off tip is enough; no account needed.</p>
<p>Prefer the full page? <a href="{DONATE_URL}" target="_blank" rel="noopener">Open Ko-fi in a new tab</a>.</p>
<h2>Free ways to help</h2>
<p>Subscribe on <a href="{LINKS[0][1]}" target="_blank" rel="noopener">YouTube</a>, share a Short with a chess friend, or comment with the trap you want explained next. It all helps the channel grow.</p>
<h2>Coming later</h2>
<p>Memberships with extra lessons and courses. <a href="/contact/">Tell us</a> what you would want in them.</p>
</div><aside><iframe class="kofi" src="{DONATE_URL}/?hidefeed=true&amp;widget=true&amp;embed=true&amp;preview=true" title="Support Throiy Chess on Ko-fi" loading="lazy"></iframe></aside></div></main>''' + footer(band=False)
    return "/support/", page("/support/", "Support · Throiy Chess", "Support Throiy Chess with a small tip and keep the chess lessons free.", body)

def free_page():
    body = header("Free") + f'''<main class="wrap"><div class="twocol" style="padding:40px 0 64px;align-items:center"><div class="prose">
<span class="eyebrow">Free download</span>
<h1 class="page">10 Opening Traps: the cheat sheet</h1>
<p>The ten traps every beginner meets, on one PDF. For each trap: what happens in plain words, the exact move where it goes wrong, and how not to fall for it.</p>
<ul><li>Scholar's Mate, Légal's Mate, Fried Liver, Fishing Pole</li><li>Blackburne Shilling, Stafford, Englund, Elephant, Lasker, Siberian</li><li>Every line checked with a chess engine</li></ul>
<p>Enter your e-mail and the download appears right away. You also get one trap a week in your inbox. Unsubscribe in one click.</p>
<form class="nl" data-dl="/free/10-opening-traps-cheat-sheet.pdf" action="{e(NEWSLETTER_URL)}" method="post" target="_blank">
<label class="sr" for="free-email">E-mail address</label>
<input id="free-email" type="email" name="fields[email]" placeholder="Your e-mail" autocomplete="email" required>
<input type="hidden" name="ml-submit" value="1"><input type="hidden" name="anticsrf" value="true">
<div class="hp" aria-hidden="true"><input type="text" name="nl_website" tabindex="-1" autocomplete="off"></div>
<button class="btn solid" type="submit">Send me the cheat sheet</button>
<p class="nl-msg small" role="status" aria-live="polite"></p></form>
<p class="small">We use MailerLite (EU) to send the e-mails and use your address for nothing else. Unsubscribe in one click and we delete it. <a href="/privacy/">Privacy</a></p>
</div><aside><img src="/free/cheat-sheet-cover.png" width="540" height="960" alt="Cover of the 10 Opening Traps cheat sheet" style="width:100%;max-width:340px;margin:0 auto;display:block;height:auto;border-radius:14px;border:2px solid #d9a93d"></aside></div></main>''' + footer(band=False, nl=False)
    return "/free/", page("/free/", "Free: 10 Opening Traps Cheat Sheet · Throiy Chess", "Free PDF: the ten opening traps every beginner meets, in plain words, with the fix for each one.", body)

AZ_CSS = """.az-form{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}.az-form select,.az-form input{padding:13px 14px;border-radius:10px;border:1px solid #3a352c;background:#16140f;color:inherit;font:inherit}
.az-form input{flex:1;min-width:200px}.az-list{display:grid;gap:8px;margin:14px 0 18px}.az-g{display:grid;grid-template-columns:auto 64px 1fr auto;gap:12px;align-items:center;padding:11px 14px;border:1px solid #2c2820;border-radius:12px;cursor:pointer}
.az-g:has(input:checked){border-color:#d9a93d;background:#1b1813}.res{font-weight:800;font-size:13px}.res.won{color:#7fc27a}.res.lost{color:#e07a6a}.res.draw{color:#bdb6a8}
.az-top{border:1px solid #d9a93d;border-radius:14px;padding:18px 20px;margin:18px 0}.az-bars{display:grid;gap:8px;margin:12px 0 18px}.az-bar{display:grid;grid-template-columns:minmax(150px,260px) 1fr 30px;gap:10px;align-items:center;font-size:14px}
.az-bar i{display:block;height:12px;border-radius:6px;background:#d9a93d}.az-trap{padding:12px 16px;border-radius:12px;background:#1b1813;margin:10px 0}
.az-m{display:grid;grid-template-columns:200px 1fr;gap:18px;padding:16px 0;border-top:1px solid #2c2820}.az-m h3{margin:4px 0 6px}
svg.mini{width:200px;height:200px;border-radius:8px}svg.mini .lt{fill:#e9dcc0}svg.mini .dk{fill:#b38b5d}svg.mini .hl{fill:#d9a93d;opacity:.55}
svg.mini text{font-size:.82px;text-anchor:middle;font-family:"DejaVu Sans","Segoe UI Symbol",serif}svg.mini .pw{fill:#fff;stroke:#1d1b17;stroke-width:.03}svg.mini .pb{fill:#1d1b17}
.az-cta{border-radius:14px;background:#1b1813;padding:20px;margin:26px 0 40px}.az-follow{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px}.az-follow .btn{flex:1 1 0;min-width:0;justify-content:center;text-align:center;padding-inline:8px}.az-replay{margin:8px 10px 4px 0;padding:6px 12px;font-size:13px}.mform{display:flex;flex-wrap:wrap;gap:10px;align-items:center}.mform input{flex:1 1 200px;padding:12px 14px;border-radius:10px;border:1px solid var(--line);background:transparent;color:inherit;font:inherit}.newsletter .mform input{border:2px solid var(--on-gold);color:var(--on-gold);background:rgba(255,255,255,.35)}.m-soc{display:grid;grid-template-columns:1fr 92px 112px;gap:10px;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)}.m-soc>.small{grid-column:2 / 4;text-align:right}.m-soc .btn{margin:0;width:100%;justify-content:center;text-align:center;padding-inline:6px}.m-row{display:grid;grid-template-columns:90px 1fr auto;gap:4px 12px;align-items:center;padding:11px 14px;border:1px solid #2c2820;border-radius:12px}.m-row .small:nth-child(3){grid-column:2}.m-row .btn{grid-column:3;grid-row:1/3;padding:6px 12px;font-size:13px}.az-pro{border:2px solid #d9a93d;border-radius:14px;padding:18px 20px;margin:24px 0}.az-tips{padding-left:22px}.az-tips li{margin:8px 0}.az-what{border-left:3px solid #d9a93d;padding:4px 0 4px 14px;margin:14px 0}.az-score{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:14px 0}.az-score div{border:1px solid #2c2820;border-radius:12px;padding:12px 8px;text-align:center}.az-score b{display:block;font-size:26px;color:#d9a93d}.az-score span{font-size:12px;color:#bdb6a8}.az-ph{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0}.az-ph div{border:1px solid #2c2820;border-radius:12px;padding:12px;text-align:center}.az-ph .worst{border-color:#d9a93d;background:#1b1813}.az-ph b{display:block;font-size:24px}.az-ph span{font-weight:700}.az-ph small{color:#bdb6a8;font-size:12px}.az-gm{display:grid;gap:8px;margin:10px 0 18px}.az-gm a{display:grid;grid-template-columns:60px 1fr;gap:4px 12px;padding:11px 14px;border:1px solid #2c2820;border-radius:12px;text-decoration:none;color:inherit}.az-gm a .small{grid-column:2}.az-plan{display:grid;gap:12px;margin:10px 0 18px}.az-plan>div:not(:last-child){border:1px solid #2c2820;border-radius:12px;padding:14px 16px}svg.mini .hl2{fill:#4fae6b;opacity:.55}svg.mini .arw{stroke:#4fae6b;stroke-width:.14;stroke-linecap:round;opacity:.9}@media (max-width:560px){.az-score{grid-template-columns:repeat(2,1fr)}}.az-cta{background:var(--gold);color:var(--on-gold)}.az-cta p{color:rgba(20,17,11,.82)}.az-cta .az-follow .btn{border:2px solid var(--on-gold);color:var(--on-gold);font-weight:800}.az-cta hr{border:0;border-top:1px solid #2c2820;margin:20px 0}@media (max-width:560px){.az-m{grid-template-columns:1fr}.az-g{grid-template-columns:auto 52px 1fr}.az-g .small{grid-column:2/-1}}"""

def _tdata():
    tdata = []
    for t in TRAPS:
        bl = [int(k) for k, v in t.get("notes", {}).items() if "BLUNDER" in v[0] or "MISTAKE" in v[0] or "GREED" in v[0]]
        tdata.append({"slug": t["slug"], "name": t["name"], "moves": t["moves"], "side": t["side"], "blunder": max(bl) if bl else None})
    return tdata

def analyze_page():
    tdata = _tdata()
    body = header("Analyze") + f'''<style>{AZ_CSS}</style><main class="wrap" style="max-width:900px"><div class="pagehead"><span class="eyebrow">Beta · free</span>
<h1 class="page">Analyze your games</h1><p>Enter a Chess.com or Lichess username, pick up to 5 games, and see <b>which chess principles</b> cost you the most points, in plain words. Any player works: yours, a friend's, or a grandmaster's.</p></div>
<form class="az-form" id="az-form"><label class="sr" for="az-site">Site</label><select id="az-site"><option value="chesscom">Chess.com</option><option value="lichess">Lichess</option></select>
<label class="sr" for="az-user">Username</label><input id="az-user" placeholder="Username" autocomplete="off" required><button class="btn solid" type="submit">Find games</button></form>
<div id="az-games"></div><div id="az-report"></div>
<p class="small" style="margin:30px 0 50px">The analysis runs in your own browser with Stockfish 17.1 (GPLv3, <a href="https://github.com/official-stockfish/Stockfish" target="_blank" rel="noopener">source</a>). We don't store your games. Games are loaded from the public Chess.com and Lichess APIs. Throiy Chess is not affiliated with Chess.com or Lichess. A beta: the engine runs at a light depth, so treat single numbers as a guide.</p>
</main><script type="application/json" id="trap-data">{json.dumps(tdata)}</script>{SB_SCRIPTS}<script type="module" src="/js/analyze.js"></script>''' + footer(band=False)
    return "/analyze/", page("/analyze/", "Free chess game analyzer: find your biggest mistakes · Throiy Chess", "Free chess game analyzer for Chess.com and Lichess. Find the mistakes that cost you the most points, see your rating band and get a simple training plan. No sign-up.", body)

WAITLIST_URL = "https://assets.mailerlite.com/jsonp/2747354/forms/202754728493319697/subscribe"  # MailerLite form -> group "Improvement waitlist" (double opt-in)
SB_SCRIPTS = '<script src="/js/vendor/supabase-2.117.3.js"></script>'
MEM_CSS = """
.mw{max-width:1120px}
.mhero{padding:46px 0 10px}.mhero h1{font-size:clamp(36px,6vw,64px);line-height:1.02;margin:10px 0 14px}.mhero p{color:var(--mute);max-width:640px;font-size:19px;margin:0}
.mgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:16px;margin:30px 0}
.mcard{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px 20px 18px;position:relative}
.mcard h3{margin:12px 0 6px;font-size:19px}.mcard p{margin:0;color:var(--mute);font-size:15.5px;line-height:1.5}
.mico{width:40px;height:40px;border-radius:11px;background:#221d10;border:1px solid #3a3118;display:grid;place-items:center;color:var(--gold)}
.mico svg{width:21px;height:21px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.mbadge{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:3px 9px;border-radius:99px;border:1px solid var(--line);color:var(--mute)}
.mbadge.free{color:#9fd5a5;border-color:#2c4a30}.mbadge.pro{color:var(--on-gold);background:var(--gold);border-color:var(--gold)}
.mcard .mbadge{position:absolute;top:18px;right:18px}
.mlogin{margin:26px 0 8px!important;display:grid!important;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr)!important;gap:14px 40px;align-items:center}.mlogin .mlr{min-width:0}.mlogin .mform{flex-wrap:wrap;gap:10px}.mlogin .mform input{flex:1;min-width:0}.mlogin .mform .btn{white-space:nowrap}.mlogin .mdiv{margin:12px 0}
@media(max-width:820px){.mlogin{grid-template-columns:minmax(0,1fr)!important}.mlogin .mform{flex-wrap:wrap}}
.mlogin{padding:28px!important}.mgbtn[hidden]{display:none}.mdiv{display:flex;align-items:center;gap:12px;margin:18px 0 14px;color:#5b4a1d;font-size:12.5px;font-weight:700;text-transform:uppercase;letter-spacing:.14em}.mdiv::before,.mdiv::after{content:"";flex:1;height:1px;background:rgba(20,17,11,.28)}.mlogin .mform{max-width:none}
.mapp{display:grid;grid-template-columns:232px minmax(0,1fr);gap:34px;padding:30px 0 60px;align-items:start}
.mapp[hidden]{display:none}.mapp>div{min-width:0}section.mview{border:0;padding-block:0}
.mnav{position:sticky;top:96px;display:flex;flex-direction:column;gap:4px}
.mnav a{display:flex;align-items:center;gap:12px;padding:11px 14px;border-radius:12px;text-decoration:none;color:var(--mute);font-weight:600;font-size:16px}
.mnav a svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none}
.mnav a:hover{color:var(--ink);background:var(--panel)}
.mnav a[aria-current=page]{color:var(--gold);background:var(--panel2);box-shadow:inset 3px 0 0 var(--gold)}
.mnav .mbadge{margin-left:auto;font-size:10px;padding:2px 7px}
.mwho{margin:14px 0 0;padding:14px;border-top:1px solid var(--line);font-size:14px;color:var(--mute)}.mwho b{color:var(--ink);display:block;overflow:hidden;text-overflow:ellipsis}
.mview h2{margin:0 0 6px;font-size:clamp(26px,4vw,36px)}.mview>.lead{color:var(--mute);margin:0 0 24px;max-width:620px}
.mstats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:0 0 22px}
.mstat{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px}.mstat b{display:block;font-size:28px;line-height:1.1}.mstat span{font-size:13.5px;color:var(--mute)}
.mpromo{background:linear-gradient(135deg,#e9c97f,#d8b25c);color:var(--on-gold);border-radius:18px;padding:24px;margin:0 0 22px}
.mpromo h3{margin:0 0 6px;font-size:22px;color:var(--on-gold)}.mpromo p{margin:0 0 14px;color:#3b3118}.mpromo .btn{background:var(--on-gold);color:var(--gold);border-color:var(--on-gold)}
.mnext{display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px;margin:0 0 22px}
.mnext p{margin:0;color:var(--mute)}.mnext b{color:var(--ink)}
.mcourse{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.mlock{display:flex;align-items:center;gap:8px;margin-top:14px;font-size:13.5px;color:var(--mute)}
.mlock svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.8}
.msteps{counter-reset:s;display:grid;gap:12px;margin:0 0 24px;padding:0;list-style:none}
.msteps li{counter-increment:s;display:flex;gap:14px;align-items:flex-start;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px}
.msteps li::before{content:counter(s);flex:none;width:30px;height:30px;border-radius:50%;background:var(--gold);color:var(--on-gold);font-weight:800;display:grid;place-items:center}
.mcmp{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:16px;overflow:hidden;margin:0 0 20px;background:var(--panel)}
.mcmp th,.mcmp td{padding:13px 16px;text-align:left;border-bottom:1px solid var(--line);font-size:15.5px}.mcmp tr:last-child td{border-bottom:0}
.mcmp th{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);background:var(--panel2)}.mcmp th:last-child,.mcmp td:last-child{color:var(--gold)}
.mcmp td:nth-child(n+2),.mcmp th:nth-child(n+2){text-align:center;width:22%}
.mfoot{font-size:13.5px;color:var(--mute);margin-top:34px;border-top:1px solid var(--line);padding-top:16px}
.mava{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:50%;background:#221d10;border:1px solid #4a3d1c;color:var(--gold);font-size:19px;line-height:1;vertical-align:middle;margin-right:8px}.mava.big{width:64px;height:64px;font-size:36px;margin:0}
.mlv{display:flex;gap:16px;align-items:center}.mlv b{font-size:22px}.mflame{font-size:40px;line-height:1}.mlv>div{flex:1;min-width:0}
.mbar{height:8px;border-radius:99px;background:#2a2417;margin:8px 0 6px;overflow:hidden}.mbar i{display:block;height:100%;background:var(--gold);border-radius:99px}
.mtwo{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;margin:0 0 22px}
.mavs{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 26px}.mavb{width:54px;height:54px;border-radius:14px;background:var(--panel);border:1px solid var(--line);color:var(--ink);font-size:28px;cursor:pointer}.mavb:hover{border-color:var(--gold)}.mavb.on{border-color:var(--gold);color:var(--gold);box-shadow:0 0 0 2px #4a3d1c}
.mbdgs{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin:8px 0 26px}.mbdg{border:1px dashed var(--line);border-radius:12px;padding:12px 14px;opacity:.6}.mbdg b{display:block}.mbdg.on{opacity:1;border:1px solid #4a3d1c;background:#1c1810}.mbdg.on b{color:var(--gold)}
.mview h3{margin:26px 0 8px}.mview .az-cta{display:none}
.mcharts{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;margin:0 0 20px}.mchart{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:14px 14px 6px}
.mch{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:4px}.mch span{font-size:14px;color:var(--mute)}.mch .up{color:#9fd5a5}.mch .down{color:#e08a7c}
.mchart svg{width:100%;height:auto;display:block}.mchart line{stroke:#2c271d}.mchart text{fill:#a59a83;font-size:15px}.mchart polyline{fill:none;stroke:var(--gold);stroke-width:2.5;stroke-linejoin:round}.mchart circle{fill:#17150f;stroke:var(--gold);stroke-width:2}.mchart circle.last{fill:var(--gold)}
.mgbtn{display:block;width:100%;margin:0 0 10px;background:#fff;color:#1b1b1b;border:0;border-radius:10px;padding:12px;font:inherit;font-weight:700;cursor:pointer}
@media(max-width:860px){.mapp{grid-template-columns:1fr;gap:14px;padding-top:14px}.mnav{position:static;flex-direction:row;overflow-x:auto;gap:6px;padding-bottom:6px;scrollbar-width:none;margin:0 -16px;padding-inline:16px}
.mnav::-webkit-scrollbar{display:none}.mnav a{white-space:nowrap;padding:9px 13px;background:var(--panel)}.mnav .mbadge,.mwho{display:none}.mcmp th,.mcmp td{padding:11px 9px;font-size:14px}}
"""
_ICO = {
 "home": '<path d="M3 11l9-8 9 8M5 10v10h14V10"/>', "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
 "book": '<path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2zM4 21V5M8 7h7"/>', "puzzle": '<path d="M9 3h5v3a2 2 0 104 0V3h3v6h-3a2 2 0 100 4h3v8H9v-3a2 2 0 10-4 0v3H3v-8h3a2 2 0 100-4H3V3z" transform="scale(.9) translate(1.3 1.3)"/>',
 "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>', "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
 "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>', "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M12 12l7-7"/>', "gift": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M5 12v9h14v-9M12 8c-2-4-6-4-5-1s5 1 5 1zM12 8c2-4 6-4 5-1s-5 1-5 1z"/>', "flame": '<path d="M12 3c1 4 5 5 5 10a5 5 0 01-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-4 0-6 1-9z"/>', "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 118 0v3"/>',
}
def _ic(k): return f'<svg viewBox="0 0 24 24" aria-hidden="true">{_ICO[k]}</svg>'
def _feat(k, t, d, tag): return f'<div class="mcard"><span class="mbadge {tag[0]}">{tag[1]}</span><div class="mico">{_ic(k)}</div><h3>{t}</h3><p>{d}</p></div>'
_FREE, _PRO = ("free", "Free"), ("pro", "Premium")
_FEATS = "".join([
 _feat("chart", "Saved reports and progress", "Every analysis you run while logged in is kept. Watch your pawns lost per move go down over time.", _FREE),
 _feat("target", "Know your level", "See which rating band your play matches and which habit holds you back most.", _FREE),
 _feat("bolt", "Deeper analysis, any number of games", "A stronger engine looking deeper, across all your games instead of five.", _PRO),
 _feat("puzzle", "Puzzles made from your mistakes", "Pattern recognition wins games. We build puzzles from the patterns you miss in your own games.", _PRO),
 _feat("book", "Courses by rating band", "Clear lessons and exercises, ordered so you always know the next step. Like a coach in your pocket.", _PRO),
 _feat("star", "First in line", "Waitlist members hear first and get their first in-depth analysis free.", _FREE),
])
_NAV = [("overview", "home", "Overview", ""), ("analyze", "target", "Analyze", ""), ("reports", "chart", "My reports", ""), ("training", "book", "Training", '<span class="mbadge">Soon</span>'),
        ("puzzles", "puzzle", "Puzzles", '<span class="mbadge">Soon</span>'), ("earn", "gift", "Share & earn", ""), ("plan", "star", "Premium", ""), ("profile", "user", "Profile", "")]
_NAVH = "".join(f'<a href="#{k}" data-v="{k}">{_ic(i)}<span>{t}</span>{bd}</a>' for k, i, t, bd in _NAV)
_COURSES = [("Stop hanging pieces", "The 3-second check before every move. Ends most blunders at every level.", "Foundations"),
            ("Opening traps that win material", "Ten traps with the mistakes that trigger them. The free kit is the first taste.", "Foundations"),
            ("Tactics patterns", "Forks, pins, skewers and discovered attacks, trained until you see them at once.", "Core"),
            ("Think every move", "A simple routine for every move: check, capture, threat, then improve your worst piece.", "Core"),
            ("Endgames you will meet", "The positions that decide real games, in the order you need them.", "Advanced"),
            ("Convert a won position", "Turn an advantage into a win without giving it back.", "Advanced")]
_COURSEH = "".join(f'<div class="mcard"><span class="mbadge pro">Premium</span><div class="mico">{_ic("book")}</div><h3>{t}</h3><p>{d}</p><div class="mlock">{_ic("lock")} {lv} &middot; opens with the program</div></div>' for t, d, lv in _COURSES)
_CMP = "".join(f"<tr><td>{a}</td><td>{x}</td><td>{y}</td></tr>" for a, x, y in [
  ("Free analyzer (5 games)", "&#10003;", "&#10003;"), ("Saved reports + progress chart", "&#10003;", "&#10003;"), ("10 Opening Traps kit", "&#10003;", "&#10003;"),
  ("Any number of games", "&ndash;", "&#10003;"), ("Deeper engine analysis", "&ndash;", "&#10003;"), ("Puzzles from your own mistakes", "&ndash;", "&#10003;"), ("Courses by rating band", "&ndash;", "&#10003;")])
_CMPT = '<table class="mcmp"><thead><tr><th>What you get</th><th>Free</th><th>Premium</th></tr></thead><tbody>' + _CMP + '</tbody></table>'

def members_page():
    body = header("Members") + f'''<style>{AZ_CSS}{MEM_CSS}</style><main class="wrap mw">
<div id="m-login"><div class="mhero"><span class="eyebrow">Members</span><h1>Fix what costs you games.</h1><p>Your own page with your reports, your progress and, soon, training built from your mistakes. Free to join, no password.</p></div>
<div class="mgrid">{_FEATS}</div>
<div class="newsletter mlogin"><div><strong>Log in or create your free account</strong><p>Enter your e-mail address. We send a link; opening it confirms the address and logs you in.</p></div>
<div class="mlr">{('<div id="m-gid" style="margin:4px 0 0;min-height:44px;color-scheme:light"></div><button class="mgbtn" type="button" id="m-google" hidden>Continue with Google</button><div class="mdiv">or with e-mail</div>' if GOOGLE_LOGIN else '')}<form class="mform" id="m-form"><label class="sr" for="m-mail">E-mail address</label><input id="m-mail" type="email" placeholder="Your e-mail" autocomplete="email" required maxlength="200"><button class="btn solid" type="submit">Send me a login link</button><div id="m-hc" style="flex-basis:100%"></div><p class="small" id="m-msg" role="status" aria-live="polite" style="flex-basis:100%;margin:0"></p></form></div></div>
</div>
<div id="m-app" class="mapp" hidden>
<div><nav class="mnav" aria-label="Members">{_NAVH}<div class="mwho"><span class="mava" id="m-ava">&#9823;&#xFE0E;</span><span class="small">Logged in as</span><b id="m-email"></b><button class="btn" type="button" id="m-out" style="margin-top:10px">Log out</button></div></nav></div>
<div>
<section class="mview" data-view="overview"><h2 id="m-hello">Welcome</h2><p class="lead">Your Throiy Chess home. Everything you saved and what to do next.</p>
<div class="mstats" id="m-stats"></div><div class="mnext" id="m-next"></div>
<div class="mpromo"><h3>The improvement program is coming</h3><p>Deeper analysis, puzzles made from your own mistakes and courses by rating band. Join the waitlist and get your first in-depth analysis free.</p><a class="btn" href="/improve/">Join the waitlist</a></div>
</section>
<section class="mview" data-view="analyze" hidden><h2>Analyze games</h2><p class="lead">Standard analysis: pick a site and username, choose up to 5 games. Your report is saved here automatically.</p>
<div class="mcard" style="margin:0 0 20px;padding-right:110px"><span class="mbadge pro">Premium</span><div class="mico">{_ic("bolt")}</div><h3>Advanced analysis</h3><p>A deeper engine, up to 25 games at once, trends per pattern over time and puzzles made from your mistakes. Opens with the improvement program.</p><p style="margin-top:12px"><a class="btn" href="#plan">See what Premium gives you</a></p></div>
<form class="az-form" id="az-form"><label class="sr" for="az-site">Site</label><select id="az-site"><option value="chesscom">Chess.com</option><option value="lichess">Lichess</option></select>
<label class="sr" for="az-user">Username</label><input id="az-user" placeholder="Username" autocomplete="off" required><button class="btn solid" type="submit">Find games</button></form>
<div id="az-games"></div><div id="az-report"></div>
<p class="small" style="margin:24px 0 10px">The analysis runs in your own browser with Stockfish 17.1. Games are loaded from the public Chess.com and Lichess APIs.</p></section>
<section class="mview" data-view="reports" hidden><h2>My reports</h2><p class="lead">Every report you ran while logged in. Run another one every week or two to see your progress.</p><div id="m-charts"></div><div id="m-list"><p class="small">Loading…</p></div><p style="margin-top:18px"><a class="btn solid" href="#analyze">Analyze new games</a></p></section>
<section class="mview" data-view="training" hidden><h2>Training</h2><p class="lead">Courses by rating band, with exercises after every lesson. They open with the improvement program. Until then, start with the free kit.</p>
<div class="mnext"><p><b>Free now:</b> the 10 Opening Traps, with a quiz made for your phone.</p><a class="btn solid" href="/traps/">Open the traps</a></div><div class="mcourse">{_COURSEH}</div></section>
<section class="mview" data-view="puzzles" hidden><h2>Puzzles</h2><p class="lead">Pattern recognition is what makes you win. Your puzzles come from your own games, so you train exactly what you miss.</p>
<ol class="msteps"><li><span><b>You analyze your games.</b><br><span class="small">The same free analyzer you use now.</span></span></li><li><span><b>We find the patterns you miss.</b><br><span class="small">Forks, pins, loose pieces: whatever cost you the most.</span></span></li><li><span><b>You train on puzzles built from them.</b><br><span class="small">Short sessions, a score and a streak.</span></span></li></ol>
<div class="mpromo"><h3>Opens with the improvement program</h3><p>Join the waitlist and be first in.</p><a class="btn" href="/improve/">Join the waitlist</a></div></section>
<section class="mview" data-view="earn" hidden><h2>Share &amp; earn</h2><p class="lead">Collect points, keep your streak and unlock badges. Rewards grow as the program grows.</p>
<div class="mtwo"><div class="mcard" id="m-level"></div><div class="mcard" id="m-streak"></div></div>
<h3>Your avatar</h3><div class="mavs" id="m-av"></div>
<h3>Badges</h3><div class="mbdgs" id="m-badges"></div>
<h3>Follow Throiy Chess</h3><div id="m-soc"></div><p class="small" id="m-socmsg"></p>
<h3>Coming rewards</h3><div class="mnext"><p>Avatar frames and a badge next to your name, a free in-depth analysis when the program starts, and a free month for friends you invite. Points you collect now count.</p></div>
</section>
<section class="mview" data-view="plan" hidden><h2>Premium</h2><p class="lead">Free gets you the analyzer and your progress. Premium goes deeper and builds training around you.</p>
{_CMPT}
<div class="mpromo"><h3>Premium opens soon</h3><p>Price and start date follow at launch. Waitlist members hear first and get their first in-depth analysis free.</p><a class="btn" href="/improve/">Join the waitlist</a></div></section>
<section class="mview" data-view="profile" hidden><h2>Profile</h2><p class="lead">Add your usernames so the analyzer is one click away.</p>
<form class="mform" id="m-prof"><label class="sr" for="m-name">Name</label><input id="m-name" placeholder="Name (optional)" maxlength="60"><label class="sr" for="m-cc">Chess.com username</label><input id="m-cc" placeholder="Chess.com username" maxlength="40"><label class="sr" for="m-li">Lichess username</label><input id="m-li" placeholder="Lichess username" maxlength="40"><button class="btn solid" type="submit">Save</button><span class="small" id="m-pmsg"></span></form>
<div class="mfoot">Your data is stored in the EU and visible only to you and us. <a href="/privacy/">Privacy</a> &middot; <a href="/terms/">Terms</a><p style="margin:14px 0 0"><button class="btn" type="button" id="m-del">Delete my account and all my data</button> <span class="small" id="m-delmsg"></span></p></div></section>
</div></div></main>{SB_SCRIPTS}{('<script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit" async defer></script><script>window.TS_KEY="' + TURNSTILE_SITEKEY + '"</script>') if TURNSTILE_SITEKEY else ''}{('<script src="https://accounts.google.com/gsi/client" async defer></script><script>window.G_ID="794037102761-cb6a8qinqp5n98ptggid81ep1ji2b0q9.apps.googleusercontent.com"</script>') if GOOGLE_LOGIN else ''}<script type="application/json" id="trap-data">{json.dumps(_tdata())}</script><script src="/js/members.js"></script><script type="module" src="/js/analyze.js"></script>''' + footer(band=False, nl=False)
    return "/members/", page("/members/", "Members · Throiy Chess", "Log in to save your analysis reports and track your progress.", body)

def improve_page():
    body = header("Improve") + f'''<main class="wrap"><div class="pagehead"><span class="eyebrow">Coming soon · waitlist</span>
<h1 class="page">The Throiy Chess improvement program</h1>
<p>The free analyzer finds your biggest mistakes in 5 games. The program goes further: a stronger engine looking deeper, all your games, and training built from your own mistakes.</p></div>
<style>{MEM_CSS}</style><div class="twocol" style="padding-bottom:40px"><div class="prose"><h2>What you get</h2>
<ul><li><b>Deeper analysis</b> with a stronger engine and more depth, so the better move is also the right one</li><li><b>Any number of games</b>, not just 5</li><li><b>Puzzles made for you</b>: pattern recognition is what makes you win, so we build puzzles from the patterns you miss in your own games</li><li><b>Progress you can see</b>: score per session, streaks, and pawns lost per move over time</li><li><b>A rating guide</b>: which rating band your play matches, and what moves you up</li></ul>
<p class="small">Price and start date are not set yet. Waitlist members hear first, and get the first analysis free.</p></div>
<div><div class="newsletter" style="margin:0;grid-template-columns:1fr"><div><strong>Join the waitlist</strong><p>One confirmation mail to check your address. No spam, unsubscribe in one click.</p></div>
<form class="nl" data-ev="waitlist-signup" data-msg="Almost done! Check your inbox and confirm your address to join the waitlist." action="{e(WAITLIST_URL)}" method="post" target="_blank">
<label class="sr" for="wl-email">E-mail address</label>
<input id="wl-email" type="email" name="fields[email]" placeholder="Your e-mail" autocomplete="email" required>
<input type="hidden" name="ml-submit" value="1"><input type="hidden" name="anticsrf" value="true">
<div class="hp" aria-hidden="true"><input type="text" name="nl_website" tabindex="-1" autocomplete="off"></div>
<button class="btn solid" type="submit">Join the waitlist</button>
<p class="nl-msg small" role="status" aria-live="polite"></p></form></div></div></div>
<h2 style="margin-top:20px">Free and Premium</h2><div class="mgrid">{_FEATS}</div>{_CMPT}<div style="height:50px"></div></main>''' + footer(band=False, nl=False)
    return "/improve/", page("/improve/", "Improve your chess: deeper analysis, puzzles and courses · Throiy Chess", "Join the waitlist for the Throiy Chess improvement program: deeper game analysis, puzzles made from your own mistakes and courses by rating band.", body)

def terms():
    body = header() + f'''<main class="wrap"><div class="pagehead"><span class="eyebrow">Terms</span><h1 class="page">Terms of use</h1><p>Short and plain. By using {DOMAIN} you agree to these terms.</p></div>
<div class="prose" style="padding-bottom:64px">
<h2>What this is</h2><p>Throiy Chess offers free chess lessons and tools. The site and the analyzer are in beta and provided as they are, without guarantees.</p>
<h2>The analyzer and reports</h2><p>Reports come from a chess engine at a light depth and are a guide, not advice you must follow. Rating bands and accuracy are our own estimates from our own sample of games. They are not an official rating and not comparable with the numbers on Chess.com or Lichess. Throiy Chess is not affiliated with Chess.com or Lichess. Use the analyzer only on games you may analyze; we do not store the games you load.</p>
<h2>Your account</h2><p>An account is optional and free. You are responsible for the e-mail address you sign in with. We set limits on how many reports you can save to keep the service fast for everyone. You can delete your account and all saved data yourself on your members page at any time. We may remove accounts that abuse the service.</p>
<h2>Our content</h2><p>The videos, texts, images and tools on this site are the work of Throiy Chess. You may share links and short quotes with a credit. Please do not copy complete pages or videos. Player photos are used under their open licences, with credit.</p>
<h2>Liability</h2><p>To the extent the law allows, Throiy Chess is not liable for damage that results from using the site or the analyzer. Dutch law applies.</p>
<h2>Questions</h2><p>Use the <a href="/contact/">contact page</a>.</p>
<p class="small">Last updated: {datetime.date.today().strftime("%d %B %Y")}</p></div></main>''' + footer()
    return "/terms/", page("/terms/", "Terms of use · Throiy Chess", "Terms of use for the Throiy Chess site, analyzer and member accounts.", body)

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
    lines += [f"- [{v['title']}](https://www.youtube.com/watch?v={v['id']}): {v.get('desc', '')}" for v in VIDEOS]
    lines += ["", "## Channels"] + [f"- [{n}]({u})" for n, u in LINKS] + ["", "## Optional", f"- [Support]({SITE}/support/)", f"- [Contact]({SITE}/contact/)", f"- [Privacy]({SITE}/privacy/)"]
    return "\n".join(lines) + "\n"

def build():
    d = os.environ.get("OUT_DIR") or os.path.join(ROOT, "dist"); shutil.rmtree(d, ignore_errors=True) if not os.environ.get("OUT_DIR") else None
    fetch_thumbs(SHORTS + VIDEOS)
    shutil.copytree(os.path.join(ROOT, "src"), d, dirs_exist_ok=True)
    pages = [("/", home())] + shorts_pages() + [videos_page()] + [traps_index()] + [trap_page(t) for t in TRAPS] + [support_page(), contact(), privacy(), free_page(), analyze_page(), members_page(), improve_page(), terms()]
    for path, htm in pages:
        p = os.path.join(d, path.strip("/"), "index.html") if path != "/" else os.path.join(d, "index.html")
        os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(htm)
    open(os.path.join(d, "404.html"), "w").write(notfound())
    today = datetime.date.today().isoformat()
    open(os.path.join(d, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>\n" for p, _ in pages if p != "/members/") + "</urlset>\n")
    open(os.path.join(d, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /m/\nDisallow: /members/\n\nSitemap: {SITE}/sitemap.xml\n")
    open(os.path.join(d, "llms.txt"), "w").write(llms_txt())
    open(os.path.join(d, "CNAME"), "w").write(DOMAIN + "\n"); open(os.path.join(d, ".nojekyll"), "w").write("")
    print("built", len(pages), "pages")

if __name__ == "__main__":
    build()
