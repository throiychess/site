// Throiy Chess · Analyze your games (beta). Runs fully in the visitor's browser.
// Games: Chess.com Published-Data API / Lichess API. Engine: Stockfish 17.1 lite (GPLv3), single-threaded WASM.
import { Chess } from "/js/chess.js";

const $ = (s, r = document) => r.querySelector(s);
const MAX_FREE = 5, MAX_PREMIUM = 25; let DEPTH = 14;
const isPrem = () => window.__plan === 'premium', maxGames = () => (isPrem() ? MAX_PREMIUM : MAX_FREE);
const VAL = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 };
const NAMES = { p: "pawn", n: "knight", b: "bishop", r: "rook", q: "queen", k: "king" };
const TRAPS = JSON.parse($("#trap-data").textContent);
const ev = (n) => { try { if (window.goatcounter && goatcounter.count) goatcounter.count({ path: n, title: n, event: true }); } catch (e) {} };
const safeUrl = (u) => (/^https:\/\/(www\.chess\.com|lichess\.org)\//.test(String(u)) ? String(u) : "#");
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// ---------- principles (plain words; every one is a test, not a guess) ----------
const P = {
  mate:   { t: "Walked into checkmate", tip: "Before every move, ask: what checks does my opponent have after this? Look at your king first." },
  threat: { t: "Missed the opponent's threat", tip: "Before you move, ask what your opponent's last move wants to do. Answer the threat first, then make your plan." },
  hang:   { t: "Left a piece unprotected", tip: "After choosing a move, check every piece: is it attacked, and is it defended enough? Loose pieces drop off." },
  tactic: { t: "Missed a forcing move (check or capture)", tip: "Scan checks, captures and threats for both sides every move. The strongest move is often forcing." },
  queen:  { t: "Queen out too early", tip: "In the opening, develop knights and bishops first. An early queen gets chased and you lose time." },
  king:   { t: "King safety in the opening", tip: "Castle early and don't move your king by hand in the opening. A king in the middle is a target." },
  twice:  { t: "Same piece moved twice in the opening", tip: "Each opening move should bring a new piece into play. Moving one piece again gives your opponent time." },
  endgame:{ t: "Endgame technique", tip: "In the endgame, activate your king, push passed pawns and trade pieces (not pawns) when you're ahead." },
  other:  { t: "A quiet move that made things worse", tip: "Compare your move with the better one: which pieces does it improve? Ask which of your pieces does the least, and improve that one." },
};

const RULE = { hang: "Loose pieces drop off.", threat: "Answer the threat before you start your plan.", tactic: "Look at checks, captures and threats, for both sides, every move.", mate: "Look at your king first.", queen: "Develop knights and bishops before the queen.", king: "Castle early, keep the king at home.", twice: "Every opening move should bring a new piece into play.", endgame: "In the endgame the king is a fighting piece.", other: "Improve your worst piece." };
const ruleLink = (c) => RULE[c] ? `<a href="/members/#training">Principle: ${RULE[c]}</a> <span class="small">(with examples from your own games)</span>` : "";
const DRILL = {
  mate:   ["Before every move, say the three words out loud: checks, captures, threats. Start with the checks your opponent has.", "Play 5 games with this rule only. Do not worry about the opening."],
  threat: ["After each opponent move, ask: what does it want to do next? Answer that before your own plan.", "In your next 5 games, write down (or say) the opponent's threat before every move."],
  hang:   ["Before you press the move, look at the piece you moved and at all your loose pieces: attacked? defended?", "In your next 5 games, never move without a 'blunder check' of the square you move to."],
  tactic: ["Every move, scan your own checks and captures first, even if they look bad. Then decide.", "Solve 10 tactics puzzles a day for a week, with a time limit of 30 seconds each."],
  queen:  ["In the opening: knights and bishops first, queen later. Count how many pieces you have developed before you move the queen.", "Play 5 games where the queen stays home until move 8."],
  king:   ["Castle by move 10. Do not move the king by hand unless you have to.", "Play 5 games: after move 6, check whether you can castle now."],
  twice:  ["Each opening move brings a new piece into play. Ask: which piece have I not moved yet?", "Play 5 games: do not move the same piece twice before move 8 unless it wins material."],
  endgame:["Activate your king in the endgame and push your passed pawns.", "Practice king and pawn endings for 10 minutes a day."],
  other:  ["Every move, ask in this order: 1) Does my opponent have a check, capture or threat? 2) Do I have one? If both answers are no, use the move to improve your worst piece: the one doing the least.", "In your next 5 games, do this on every move, from move 1. A check, capture or threat comes first. When there is none, improve your worst piece."],
};
// Our own benchmark: 270 Chess.com rapid games (30 per band, Oct 2026), same engine and depth, median pawns lost per move and mean blunders per game.
const BANDS = [{ lo: 0, hi: 600, loss: 0.94, bl: 3.0 }, { lo: 600, hi: 800, loss: 0.78, bl: 2.5 }, { lo: 800, hi: 1000, loss: 0.67, bl: 1.8 }, { lo: 1000, hi: 1200, loss: 0.59, bl: 1.6 },
  { lo: 1200, hi: 1400, loss: 0.54, bl: 0.9 }, { lo: 1400, hi: 1600, loss: 0.44, bl: 1.1 }, { lo: 1600, hi: 2400, loss: 0.38, bl: 0.8 }];
const bandOf = (loss) => { let k = 0, d = 9; BANDS.forEach((b, i) => { const x = Math.abs(b.loss - loss); if (x < d) { d = x; k = i; } }); return k; };
const bandName = (i) => i >= BANDS.length - 1 ? "1600+" : `${BANDS[i].lo}\u2013${BANDS[i].hi}`;
const PHN = { opening: "Opening", middlegame: "Middlegame", endgame: "Endgame" };
// ---------- opponent mode (/opponent/): same analysis, a different report: where to aim ----------
const OPP = /^\/opponent/.test((typeof location !== "undefined" && location.pathname) || "");
const AIM = {
  mate:   { t: "Walks into checkmate", tip: "Keep your pieces pointed at their king. Before each move, look for a check: they often miss the danger." },
  threat: { t: "Misses threats", tip: "Make a threat whenever you can. They often carry on with their own plan and leave it unanswered." },
  hang:   { t: "Leaves pieces unprotected", tip: "Every move, look for a piece of theirs that nothing defends. Attack it, or attack two things at once." },
  tactic: { t: "Misses checks and captures", tip: "Keep the game sharp and keep pieces on the board. The more pieces touch each other, the more they miss." },
  queen:  { t: "Brings the queen out too early", tip: "Develop your knights and bishops by attacking their queen. Every time she has to move, you gain a move." },
  king:   { t: "Leaves the king in the middle", tip: "Castle, then open the centre while their king is still there. Trade a centre pawn and put a rook on the open file." },
  twice:  { t: "Moves the same piece twice in the opening", tip: "Develop a new piece with every move and castle. You will have more pieces in play, so open the position." },
  endgame:{ t: "Loses the thread in the endgame", tip: "Do not be afraid to trade queens. An equal endgame is a good place to beat them." },
  other:  { t: "Drifts in quiet positions", tip: "There is no need to rush. Keep improving your pieces and let them make the quiet mistake." },
};
const PHAIM = { opening: "Develop fast and castle: you can be better before the middlegame starts.", middlegame: "Keep the pieces on the board: that is where they go wrong.", endgame: "Trading down into an endgame is fine against them." };
const third = (t) => String(t || "").replace(/^Your opponent now has/, "The other side now has").replace(/\bYou had\b/g, "They had").replace(/\bYour\b/g, "Their").replace(/\byour\b/g, "their");

// ---------- engine ----------
class Engine {
  constructor(full) { this.w = new Worker(full ? "/js/stockfish/full/stockfish-17.1-single-a496a04.js" : "/js/stockfish/stockfish-17.1-lite-single-03e3232.js"); this.q = Promise.resolve(); this.lis = null;
    this.w.onmessage = (e) => this.lis && this.lis(String(e.data)); }
  cmd(c) { this.w.postMessage(c); }
  wait(pred) { return new Promise((res) => { this.lis = (l) => { if (pred(l)) { this.lis = null; res(l); } }; }); }
  async init() { const p = this.wait((l) => l === "uciok"); this.cmd("uci"); await p; this.cmd("setoption name Hash value 32");
    const r = this.wait((l) => l === "readyok"); this.cmd("isready"); await r; }
  analyse(fen, depth = DEPTH) { // score from White's point of view, in pawns*100; mate as +-(10000 - n)
    return (this.q = this.q.then(() => new Promise((res) => { let score = 0, best = null, pv = []; const white = fen.split(" ")[1] === "w";
      this.lis = (l) => { if (l.startsWith("info") && l.includes(" score ")) { const m = l.match(/score (cp|mate) (-?\d+)/);
          if (m) { let s = +m[2]; if (m[1] === "mate") s = s > 0 ? 10000 - s : -10000 - s; score = white ? s : -s; } const pm = l.match(/ pv (.+)$/); if (pm) pv = pm[1].split(" "); }
        else if (l.startsWith("bestmove")) { best = l.split(" ")[1]; this.lis = null; res({ score, pv, best: best === "(none)" ? null : best }); } };
      this.cmd("position fen " + fen); this.cmd("go depth " + depth); })));
  }
}
let FULL = false; const engines = {};
async function getEngine() { const k = FULL ? "full" : "lite"; if (!engines[k]) { const e = new Engine(FULL); await e.init(); engines[k] = e; } return engines[k]; }

// ---------- fetching games ----------
async function fetchChesscom(user) {
  const a = await fetch(`https://api.chess.com/pub/player/${encodeURIComponent(user.toLowerCase())}/games/archives`);
  if (!a.ok) throw new Error("Player not found on Chess.com.");
  const months = (await a.json()).archives.slice(-2).reverse(); let games = [];
  for (const m of months) { const r = await fetch(m); if (r.ok) games = games.concat((await r.json()).games || []); if (games.length >= 30) break; }
  return games.filter((g) => g.pgn && (g.rules || "chess") === "chess").sort((x, y) => y.end_time - x.end_time).slice(0, 30).map((g) => ({
    pgn: g.pgn, white: g.white.username, black: g.black.username, wres: g.white.result, bres: g.black.result,
    tc: g.time_class, wrat: g.white.rating, brat: g.black.rating, date: new Date(g.end_time * 1000), url: g.url }));
}
async function fetchRatings(site, user) { // current ratings: rapid, blitz, daily, puzzles. Never blocks the report.
  const out = {}; try {
    if (site === "lichess") { const r = await fetch(`https://lichess.org/api/user/${encodeURIComponent(user)}`); if (r.ok) { const p = (await r.json()).perfs || {};
      out.rapid = p.rapid && p.rapid.rating; out.blitz = p.blitz && p.blitz.rating; out.daily = p.correspondence && p.correspondence.rating; out.puzzles = p.puzzle && p.puzzle.rating; } }
    else { const r = await fetch(`https://api.chess.com/pub/player/${encodeURIComponent(user.toLowerCase())}/stats`); if (r.ok) { const j = await r.json(), l = (k) => j[k] && j[k].last && j[k].last.rating;
      out.rapid = l("chess_rapid"); out.blitz = l("chess_blitz"); out.daily = l("chess_daily"); out.puzzles = j.tactics && j.tactics.highest && j.tactics.highest.rating; out.puzzlesBest = true; } }
  } catch (e) {} return out;
}
async function fetchLichess(user) {
  const r = await fetch(`https://lichess.org/api/games/user/${encodeURIComponent(user)}?max=30&clocks=true&pgnInJson=true&perfType=ultraBullet,bullet,blitz,rapid,classical,correspondence`,
    { headers: { Accept: "application/x-ndjson" } });
  if (!r.ok) throw new Error("Player not found on Lichess.");
  const lines = (await r.text()).trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
  return lines.filter((g) => g.variant === "standard" && g.pgn).map((g) => ({
    pgn: g.pgn, white: g.players.white.user ? g.players.white.user.name : "Anonymous", black: g.players.black.user ? g.players.black.user.name : "Anonymous",
    wres: g.winner === "white" ? "win" : g.winner ? "loss" : "draw", bres: g.winner === "black" ? "win" : g.winner ? "loss" : "draw",
    tc: g.speed, wrat: g.players.white.rating, brat: g.players.black.rating, date: new Date(g.createdAt), url: "https://lichess.org/" + g.id }));
}

// ---------- helpers ----------
const clk = (c) => { const m = c && c.match(/\[%clk (\d+):(\d+):(\d+(?:\.\d+)?)\]/); return m ? +m[1] * 3600 + +m[2] * 60 + +m[3] : null; };
const nullMove = (fen) => { const f = fen.split(" "); f[1] = f[1] === "w" ? "b" : "w"; f[3] = "-"; return f.join(" "); };
const uciMove = (chess, u) => { try { return chess.move({ from: u.slice(0, 2), to: u.slice(2, 4), promotion: u[4] || "q" }); } catch (e) { return null; } };
const pov = (s, white) => (white ? s : -s);
const clip = (s) => Math.max(-1000, Math.min(1000, s));
function material(fen) { let w = 0, b = 0, q = false; for (const ch of fen.split(" ")[0]) { const p = ch.toLowerCase(); if (VAL[p] !== undefined && p !== "p" && p !== "k") { if (ch === p) b += VAL[p]; else w += VAL[p]; if (p === "q") q = true; } } return { w, b, q }; }

function trapHit(sans, side) { // side = color the user played
  for (const t of TRAPS) { const line = t.moves.split(" "); const n = t.blunder || line.length; if (sans.length < n) continue;
    let ok = true; for (let i = 0; i < n; i++) if (sans[i] !== line[i]) { ok = false; break; } if (!ok) continue;
    const victim = t.side.startsWith("White") ? "b" : "w"; return { t, fell: victim === side }; }
  return null;
}

// ---------- analysis of one game ----------
async function analyseGame(g, user, progress) {
  const side = g.white.toLowerCase() === user.toLowerCase() ? "w" : g.black.toLowerCase() === user.toLowerCase() ? "b" : null;
  const c = new Chess(); c.loadPgn(g.pgn); const hist = c.history({ verbose: true }); const comments = {}; for (const x of c.getComments()) comments[x.fen] = x.comment;
  const sans = hist.map((h) => h.san); const E = await getEngine();
  const fens = [hist.length ? hist[0].before : c.fen()].concat(hist.map((h) => h.after)); const evals = [];
  for (let i = 0; i < fens.length; i++) { evals.push(await E.analyse(fens[i])); progress(i + 1, fens.length); }
  const moments = []; let lossSum = 0, nMoves = 0, accSum = 0; const moved = {}; const ph = { opening: { n: 0, loss: 0, big: 0 }, middlegame: { n: 0, loss: 0, big: 0 }, endgame: { n: 0, loss: 0, big: 0 } };
  const winPct = (cp) => 50 + 50 * (2 / (1 + Math.exp(-0.00368208 * cp)) - 1); let nBlund = 0, nMist = 0, nInacc = 0;
  for (let i = 0; i < hist.length; i++) {
    const h = hist[i]; if (side && h.color !== side) continue; const white = h.color === "w";
    const before = clip(pov(evals[i].score, white)), after = clip(pov(evals[i + 1].score, white)); const loss = Math.max(0, before - after);
    lossSum += Math.min(loss, 1000); nMoves++;
    const aMove = Math.max(0, Math.min(100, 103.1668 * Math.exp(-0.04354 * Math.max(0, winPct(before) - winPct(after))) - 3.1669)); accSum += aMove;
    const mm = material(h.before); const phase = i < 20 ? "opening" : (!mm.q && mm.w <= 13 && mm.b <= 13) ? "endgame" : "middlegame";
    ph[phase].n++; ph[phase].loss += Math.min(loss, 1000); if (loss >= 120) ph[phase].big++;
    if (loss >= 300) nBlund++; else if (loss >= 150) nMist++; else if (loss >= 60) nInacc++;
    const key = h.piece + h.from; moved[h.to] = (moved[h.from] || 0) + 1; delete moved[h.from];
    const decided = Math.abs(before) > 500 && Math.sign(before) === Math.sign(after) && Math.abs(after) > 300;
    if (loss < 120 || decided) continue;
    // tests
    const best = new Chess(h.before); const bm = evals[i].best ? uciMove(best, evals[i].best) : null;
    const reply = new Chess(h.after); const rm = evals[i + 1].best ? uciMove(reply, evals[i + 1].best) : null;
    let cat = "other", detail = "";
    if (Math.abs(evals[i + 1].score) > 9000 && pov(evals[i + 1].score, white) < 0) { cat = "mate"; detail = rm ? `Your opponent now has a forced mate, starting with ${rm.san}.` : ""; }
    else if (rm && (rm.captured || rm.san.includes("+"))) {
      // was the same reply already possible before your move? (null-move test)
      // null-move test: give the opponent this reply BEFORE your move. A real threat = it also wins (>= 1 pawn) there.
      let existed = false; try { const nm = new Chess(nullMove(h.before)); const t = nm.move({ from: rm.from, to: rm.to, promotion: rm.promotion || "q" });
        if (t && (t.captured || t.san.includes("+"))) { const r2 = await E.analyse(nm.fen()); existed = before - clip(pov(r2.score, white)) >= 100; } } catch (e) {}
      if (existed && h.to !== rm.to) { cat = "threat"; detail = `${rm.san} was already a threat before your move, and your move did not stop it.`; }
      else if (rm.captured && VAL[rm.captured] >= 3) { cat = "hang"; detail = rm.to === h.to ? `Your ${NAMES[h.piece]} on ${h.to} can be taken: ${rm.san}.` : `After your move, ${rm.san} wins your ${NAMES[rm.captured]}.`; }
      else if (bm && (bm.captured || bm.san.includes("+"))) { cat = "tactic"; detail = "You had a stronger move: a check or a capture."; }
    } else if (bm && (bm.captured || bm.san.includes("+")) && loss >= 200) { cat = "tactic"; detail = "You had a stronger move: a check or a capture."; }
    const ply = i + 1, moveNo = Math.floor(i / 2) + 1;
    if (cat === "other" && ply <= 20) {
      if (h.piece === "q" && moveNo <= 8) { cat = "queen"; detail = "The queen came out before your knights and bishops."; }
      else if (h.piece === "k" && !h.flags.includes("k") && !h.flags.includes("q")) { cat = "king"; detail = "Your king moved by hand and can no longer castle."; }
      else if ((moved[h.to] || 0) >= 2 && h.piece !== "p") { cat = "twice"; detail = `Your ${NAMES[h.piece]} moved again instead of developing a new piece.`; }
    }
    if (cat === "other") { const m = material(h.before); if (!m.q && m.w <= 13 && m.b <= 13) { cat = "endgame"; detail = ""; } }
    const prevClock = (() => { for (let j = i - 2; j >= 0; j -= 2) { const t = clk(comments[hist[j].after]); if (t !== null) return t; } return null; })();
    moments.push({ pv: (evals[i + 1].pv || []).slice(0, 3), a: aMove, ply, moveNo, color: h.color, san: h.san, best: bm ? bm.san : null, bFrom: bm ? bm.from : null, bTo: bm ? bm.to : null, loss, cat, detail, fen: h.before, from: h.from, to: h.to,
      clock: g.tc === "daily" || g.tc === "correspondence" ? null : prevClock, before, after });
  }
  const res = side === "w" ? g.wres : g.bres;
  return { g, side, moments, ph, nBlund, nMist, nInacc, nMoves, acc: nMoves ? accSum / nMoves : 0, avgLoss: nMoves ? lossSum / nMoves : 0, trap: side ? trapHit(sans, side) : null, result: res, plies: hist.length };
}

// ---------- drawing ----------
const GLYPH = { k: "♚", q: "♛", r: "♜", b: "♝", n: "♞", p: "♟" };
function boardSVG(fen, from, to, flip, bf, bt) {
  const rows = fen.split(" ")[0].split("/"); let s = `<svg viewBox="0 0 8 8" class="mini" data-flip="${flip ? 1 : 0}" role="img" aria-label="Board position">`;
  for (let r = 0; r < 8; r++) { let f = 0; for (const ch of rows[r]) { if (/\d/.test(ch)) { f += +ch; continue; }
      const x = flip ? 7 - f : f, y = flip ? 7 - r : r; s += `<image href="/img/pieces/${ch === ch.toUpperCase() ? "w" : "b"}${ch.toLowerCase()}.png" x="${x + 0.04}" y="${y + 0.04}" width="0.92" height="0.92"/>`; f++; } }
  const sq = (n) => { const f = n.charCodeAt(0) - 97, r = 8 - +n[1]; return flip ? [7 - f, 7 - r] : [f, r]; };
  let bg = ""; for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) bg += `<rect x="${x}" y="${y}" width="1" height="1" class="${(x + y) % 2 ? "dk" : "lt"}"/>`;
  for (const n of [from, to]) { if (!n) continue; const [x, y] = sq(n); bg += `<rect x="${x}" y="${y}" width="1" height="1" class="hl"/>`; }
  for (const n of [bf, bt]) { if (!n) continue; const [x, y] = sq(n); bg += `<rect x="${x}" y="${y}" width="1" height="1" class="hl2"/>`; }
  if (bf && bt) { const [x1, y1] = sq(bf), [x2, y2] = sq(bt); bg += `<line x1="${x1 + .5}" y1="${y1 + .5}" x2="${x2 + .5}" y2="${y2 + .5}" class="arw"/>`; }
  return s.replace(`role="img" aria-label="Board position">`, `role="img" aria-label="Board position">${bg}`) + "</svg>";
}

// ---------- UI ----------
let SHOWN = [];
let state = { games: [], user: "", site: "chesscom" };
function fmtRes(g, user) { const w = g.white.toLowerCase() === user.toLowerCase(); const r = w ? g.wres : g.bres;
  return r === "win" ? "Won" : ["agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient", "draw"].includes(r) ? "Draw" : "Lost"; }

$("#az-form").addEventListener("submit", async (e) => {
  e.preventDefault(); const user = $("#az-user").value.trim(); const site = $("#az-site").value; if (!user) return;
  state = { games: [], user, site }; const out = $("#az-games"); out.innerHTML = '<p class="small">Fetching games…</p>'; $("#az-report").innerHTML = "";
  try { const games = site === "lichess" ? await fetchLichess(user) : await fetchChesscom(user); state.games = games; state.ratings = {}; fetchRatings(site, user).then((r) => { state.ratings = r; }); ev("analyze-fetch-" + site);
    if (!games.length) { out.innerHTML = '<p class="small">No standard games found in the last months.</p>'; return; }
    out.innerHTML = `<p>Pick up to <strong>${maxGames()} games</strong> to analyze. ${OPP ? "Tip: their losses show the most." : "Tip: your losses teach the most."}</p>${isPrem() ? '<p class="small"><label>Detail: <select id="az-depth"><option value="14">Standard (fast)</option><option value="18">Deeper (about 4x slower, finds more)</option><option value="full">Strongest (desktop only, 79 MB download once)</option></select></label></p>' : '<p class="small">&#128274; Want up to 25 games and deeper analysis? <a href="/members/#plan">See Premium</a>.</p>'}<div class="az-chips" id="az-chips"><button type="button" class="on" data-f="all">All</button><button type="button" data-f="lost">Lost</button><button type="button" data-f="won">Won</button><button type="button" data-f="draw">Draw</button></div><div class="az-list">` +
      games.map((g, i) => { const w = g.white.toLowerCase() === user.toLowerCase(); const opp = w ? g.black : g.white;
        return `<label class="az-g" data-r="${fmtRes(g, user).toLowerCase()}"><input type="checkbox" value="${i}"><span class="res ${fmtRes(g, user).toLowerCase()}">${fmtRes(g, user)}</span>
          <span>${w ? "White" : "Black"} vs <b>${esc(opp)}</b></span><span class="small">${esc(g.tc || "")} · ${g.date.toLocaleDateString()}</span></label>`; }).join("") +
      `</div><button class="btn" id="az-more" type="button"></button> <button class="btn solid" id="az-go" type="button">Analyze selected games</button><p class="small" id="az-prog" role="status" aria-live="polite"></p>`;
    out.addEventListener("change", (ev2) => { const sel = out.querySelectorAll("input:checked"); if (sel.length > maxGames()) { ev2.target.checked = false; } });
    $("#az-go").addEventListener("click", run);
    let shown = 8, flt = "all"; const rows = [...out.querySelectorAll(".az-g")], more = $("#az-more"), chips = $("#az-chips");
    const apply = () => { let hit = 0; rows.forEach((r) => { const ok = flt === "all" || r.dataset.r === flt; if (ok) { hit++; r.style.display = hit <= shown ? "" : "none"; } else r.style.display = "none"; });
      const left = hit - shown; more.style.display = left > 0 ? "" : "none"; more.textContent = "Show " + Math.min(8, left) + " more (" + left + " left)"; };
    more.addEventListener("click", () => { shown += 8; apply(); });
    chips.addEventListener("click", (e2) => { const b = e2.target.closest("button"); if (!b) return; flt = b.dataset.f; shown = 8; [...chips.children].forEach((x) => x.classList.toggle("on", x === b)); apply(); });
    apply();
  } catch (err) { out.innerHTML = `<p class="small">${esc(err.message || "Could not fetch games.")}</p>`; }
});

async function run() {
  const idx = [...document.querySelectorAll("#az-games input:checked")].map((x) => +x.value); if (!idx.length) return;
  { const dsel = $("#az-depth"); const dv = isPrem() && dsel ? dsel.value : "14"; FULL = dv === "full"; DEPTH = FULL ? 16 : +dv || 14; }
  $("#az-go").disabled = true; const prog = $("#az-prog"); prog.textContent = "Loading the analysis tool ("+(FULL ? "79 MB, once; this can take a minute" : "7 MB, once")+")…"; ev("analyze-run");
  const results = [];
  for (let k = 0; k < idx.length; k++) {
    const g = state.games[idx[k]];
    results.push(await analyseGame(g, state.user, (a, b) => { prog.textContent = `Game ${k + 1} of ${idx.length}: checking move ${a} of ${b}…`; }));
  }
  prog.textContent = "Done."; $("#az-go").disabled = false; report(results);
}

document.addEventListener("click", (e0) => { const bt = e0.target.closest(".az-replay"); if (!bt || bt.disabled) return; const m = SHOWN[+bt.dataset.i]; if (!m) return;
  const box = bt.closest(".az-m"), svg = () => box.querySelector("svg.mini"), orig = svg().outerHTML; bt.disabled = true; ev("analyze-replay");
  const c = new Chess(m.fen), seq = [m.from + m.to + (m.promo || "")].concat(m.pv); const lab = (i) => i === 0 ? (OPP ? "Their move" : "Your move") : (OPP ? "The best reply" : "Opponent's best reply") + (i > 1 ? " and the line continues" : ""); let i = 0;
  const msg = box.querySelector(".az-rp") || bt.insertAdjacentElement("afterend", Object.assign(document.createElement("span"), { className: "az-rp small" })) || box.querySelector(".az-rp");
  const step = () => { if (i >= seq.length) { setTimeout(() => { svg().outerHTML = orig; box.querySelector(".az-rp").textContent = ""; bt.disabled = false; }, 1600); return; }
    const u = seq[i]; let mv = null; try { mv = c.move({ from: u.slice(0, 2), to: u.slice(2, 4), promotion: u[4] || "q" }); } catch (e) {}
    if (!mv) { svg().outerHTML = orig; bt.disabled = false; return; }
    svg().outerHTML = boardSVG(c.fen(), mv.from, mv.to, mSide(m) === "b"); box.querySelector(".az-rp").textContent = ` ${lab(i)}: ${mv.san}`; i++; setTimeout(step, 1300); };
  step(); });
function openingName(pgn) {
  const h = (k) => { const m = pgn.match(new RegExp('\\[' + k + ' "([^"]*)"\\]')); return m ? m[1] : ""; };
  let n = h("Opening"); if (!n) { const u = h("ECOUrl"); if (u) n = decodeURIComponent(u.split("/openings/")[1] || "").replace(/-/g, " ").replace(/\s\d.*$/, ""); }
  if (!n) return "Unknown opening"; n = n.split(":")[0].split(",")[0].trim(); return n.split(" ").slice(0, 4).join(" ").slice(0, 40) || "Unknown opening";
}
function extras(L) {
  const openings = L.results.map((r) => ({ o: openingName(r.g.pgn || ""), s: r.side, r: fmtRes(r.g, state.user), m: r.moments.length, b: r.nBlund }));
  const phases = { opening: { n: 0, loss: 0, big: 0 }, middlegame: { n: 0, loss: 0, big: 0 }, endgame: { n: 0, loss: 0, big: 0 } };
  let known = 0, low = 0; const pool = [];
  for (const r of L.results) { for (const k of Object.keys(phases)) { const p = r.ph[k]; phases[k].n += p.n; phases[k].loss += Math.round(p.loss); phases[k].big += p.big; }
    for (const m of r.moments) { if (m.clock != null) { known++; if (m.clock < 30) low++; } if (m.loss >= 150 && m.bFrom && m.best) pool.push({ o: openingName(r.g.pgn || ""), f: m.fen, c: m.color, b: m.best, bf: m.bFrom, bt: m.bTo, s: m.san, k: m.cat, l: Math.round(m.loss), n: m.moveNo }); } }
  pool.sort((a, b) => b.l - a.l);
  return { openings, phases, lc: { known, low }, puz: pool.slice(0, 40) };
}
async function saveReport() {
  const box = $("#az-save"); if (!box) return; const L = window.__azLast; const sbc = window.supabase ? (window.__sb = window.__sb || window.supabase.createClient("https://ytxrrmvszifvtdyilezn.supabase.co", "sb_publishable_nARSIxN5aKJghUK745Frdw_QbXhdf29", { auth: { persistSession: true, detectSessionInUrl: false } })) : null; if (!sbc) return;
  const { data } = await sbc.auth.getSession();
  if (!data.session) { box.innerHTML = `<p class="small">&#128190; <a href="/members/?utm_source=analyze">Log in</a> (free, no password) to save this ${OPP ? "scouting report and open it again before your game" : "report and track your progress over time"}.</p>`; return; }
  const rep = { ...extras(L), ...(OPP ? { kind: "opponent" } : {}), depth: DEPTH, cats: L.cnt, moments: SHOWN.map((m) => ({ n: m.moveNo, c: m.color, san: m.san, best: m.best, cat: m.cat, loss: Math.round(m.loss), fen: m.fen })) };
  const { error } = await sbc.from("analyses").insert({ site: state.site, username: state.user.slice(0, 40), games: L.results.length, accuracy: +L.acc.toFixed(1), avg_loss: +(L.lossNow / 100).toFixed(3), blunders: L.nB, mistakes: L.nM, inaccuracies: L.nI,
    band: bandName(L.bNow), top_leak: L.order[0] ? (OPP ? AIM : P)[L.order[0]].t : null, report: rep });
  box.innerHTML = error ? `<p class="small">${/limit/i.test(error.message || "") ? "You reached the limit of saved reports. Delete older ones on your members page." : "Could not save this report."}</p>` : `<p class="small">&#10003; Saved to your <a href="/members/#reports">reports</a>${OPP ? ", under Scouted opponents" : ""}.</p>`; if (!error) { ev(OPP ? "opponent-report-saved" : "analyze-report-saved"); window.dispatchEvent(new Event("az-saved")); }
}
function ratingsLine(cur, latest) {
  const R = state.ratings || {}, parts = [["Rapid", R.rapid], ["Blitz", R.blitz], ["Daily", R.daily], [R.puzzlesBest ? "Puzzles (best)" : "Puzzles", R.puzzles]].filter((x) => x[1]);
  if (parts.length) return `<p>${OPP ? "Their" : "Your"} ratings: ${parts.map(([n, v]) => `${esc(n)} <b>${Number(v) || 0}</b>`).join(" &middot; ")}</p>`;
  return cur ? `<p>${OPP ? "Their" : "Your"} current rating: <b>${Number(cur) || 0}</b> (${esc(latest.g.tc || "")}).</p>` : "";
}
const SAY = (cp) => cp >= 700 ? "winning" : cp >= 300 ? "clearly better" : cp >= 120 ? "a bit better" : cp > -120 ? "about equal" : cp > -300 ? "a bit worse" : cp > -700 ? "clearly worse" : "close to lost";
const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;
const ICON = { mate: "👑", threat: "⚠️", hang: "🎁", tactic: "⚡", queen: "👸", king: "🏰", twice: "🔁", endgame: "🏁", other: "💤" };
const mSide = (m) => m.side || m.r.side, mOpp = (m) => m.opp || (m.r.side === "w" ? m.r.g.black : m.r.g.white), mUrl = (m) => m.url || m.r.g.url;
function momentHtml(m, mi) { // one card: board on top, what was played vs what was better, one line why, one button
  const a = SAY(m.before), b = SAY(m.after), who = OPP ? "They" : "You";
  const change = a === b ? "" : `From ${a} to ${b}.`;
  return `<div class="az-m"><span class="dk-chip c-${m.cat}">${ICON[m.cat]} ${(OPP ? AIM : P)[m.cat].t}</span>${boardSVG(m.fen, m.from, m.to, mSide(m) === "b", m.bFrom, m.bTo)}
    <div class="dk-mv"><span class="bad">✕ ${who} played <b>${esc(m.san)}</b></span>${m.best ? `<span class="good">✓ Better: <b>${esc(m.best)}</b></span>` : ""}</div>
    <p class="dk-1">${m.detail ? esc(OPP ? third(m.detail) : m.detail) + " " : ""}${change}${m.clock !== null && m.clock !== undefined && m.clock < 60 ? ` ⏱ ${Math.round(m.clock)} seconds left.` : ""}</p>
    <p class="dk-act">${m.pv && m.pv.length ? `<button class="btn solid az-replay" type="button" data-i="${mi}">▶ Play it</button>` : ""}<a class="small" href="${esc(safeUrl(mUrl(m)))}" target="_blank" rel="noopener">Move ${m.moveNo} vs ${esc(mOpp(m))} ↗</a></p></div>`;
}
function deck(slides) { const S = slides.filter(Boolean);
  return `<div class="dk" id="az-deck"><div class="dk-bar"><i style="width:${100 / S.length}%"></i></div><div class="dk-n"><button class="dk-p" type="button" aria-label="Previous" disabled>‹</button><span class="dk-d">${S.map((x, i) => `<i class="${i ? "" : "on"}"></i>`).join("")}</span><button class="dk-x btn solid" type="button">Next ›</button></div>
    <div class="dk-t" tabindex="0">${S.map((x, i) => `<section class="dk-s ${x.c || ""}" data-n="${i}">${x.h}</section>`).join("")}</div><p class="dk-hint small">Swipe, or tap Next</p></div>`; }
function deckInit() { const dk = $("#az-deck"); if (!dk || !dk.querySelector) return; const t = dk.querySelector(".dk-t"), ss = [...t.children], dots = [...dk.querySelectorAll(".dk-d i")], nx = dk.querySelector(".dk-x"), pv = dk.querySelector(".dk-p"), bar = dk.querySelector(".dk-bar i"); let cur = 0;
  const go = (k) => { k = Math.max(0, Math.min(ss.length - 1, k)); t.scrollTo({ left: ss[k].offsetLeft - t.offsetLeft, behavior: "smooth" }); };
  const upd = () => { let k = 0, best = 1e9; ss.forEach((x, i) => { const d = Math.abs(x.offsetLeft - t.offsetLeft - t.scrollLeft); if (d < best) { best = d; k = i; } }); if (k === cur && dots[k].className) return; cur = k; dots.forEach((d, i) => { d.className = i === k ? "on" : ""; }); pv.disabled = k === 0; nx.style.visibility = k === ss.length - 1 ? "hidden" : ""; bar.style.width = (100 * (k + 1)) / ss.length + "%"; if (k) dk.classList.add("moved"); if (k === ss.length - 1) ev((OPP ? "opponent" : "analyze") + "-deck-end"); };
  t.addEventListener("scroll", () => requestAnimationFrame(upd), { passive: true }); nx.addEventListener("click", () => go(cur + 1)); pv.addEventListener("click", () => go(cur - 1));
  dk.addEventListener("click", (e) => { const g = e.target.closest("[data-go]"); if (g) go(+g.dataset.go); }); }
const phaseBar = (phs, worst) => `<div class="dk-ph">` + Object.keys(PHN).map((k) => `<div class="${k === worst ? "worst" : ""}"><b>${phs[k].big}</b><span>${PHN[k]}</span></div>`).join("") + `</div>`;
const numbersHtml = (V, you) => { const T = you ? "your" : "their"; let d = `<p class="small"><b>Big mistake:</b> a move that loses a piece or more. <b>Mistake:</b> loses a pawn or two. <b>Small slip:</b> a smaller loss. <b>Accuracy:</b> how close ${T} moves were to the best ones. It is our own estimate, so do not compare it with Chess.com or Lichess.</p>`;
  d += `<div class="az-score"><div><b>${V.acc.toFixed(0)}%</b><span>Accuracy</span></div><div><b>${V.nB}</b><span>Big mistakes</span></div><div><b>${V.nM}</b><span>Mistakes</span></div><div><b>${V.nI}</b><span>Small slips</span></div><div><b>${V.w}-${V.d}-${V.l}</b><span>Won-drawn-lost</span></div></div>`;
  d += `<p>In these games ${you ? "you" : "they"} played like players rated about <b>${bandName(V.band)}</b> (our own sample of 270 Chess.com rapid games). A guide, not an official rating.</p>`;
  d += `<h4>Game by game</h4><div class="az-gm">` + V.games.map((g) => `<a href="${esc(safeUrl(g.url))}" target="_blank" rel="noopener"><span class="res ${g.res.toLowerCase()}">${g.res}</span><span>${g.side === "w" ? "White" : "Black"} vs <b>${esc(g.opp)}</b></span><span class="small">${g.acc.toFixed(0)}% accuracy${g.tp ? ` · costliest move: ${esc(g.tp)}` : " · no big mistakes"}</span></a>`).join("") + `</div>`;
  const max = Math.max(1, ...Object.values(V.cnt)); if (V.order.length) d += `<h4>All weak points</h4><div class="az-bars">` + V.order.map((c) => `<div class="az-bar"><span>${ICON[c]} ${(you ? P : AIM)[c].t}</span><i style="width:${(100 * V.cnt[c]) / max}%"></i><b>${V.cnt[c]}</b></div>`).join("") + `</div>`;
  return d; };
const followHtml = `<div class="az-follow"><a class="btn" data-ev="analyze-follow-youtube" href="https://www.youtube.com/@ThroiyChess?sub_confirmation=1" target="_blank" rel="noopener">YouTube</a><a class="btn" data-ev="analyze-follow-instagram" href="https://www.instagram.com/throiychess" target="_blank" rel="noopener">Instagram</a><a class="btn" data-ev="analyze-follow-tiktok" href="https://www.tiktok.com/@throiychess" target="_blank" rel="noopener">TikTok</a></div>`;
function viewModel(results) { // everything a report needs, small enough to save
  const all = results.flatMap((r, ri) => r.moments.map((m) => ({ ...m, r, ri }))); const cnt = {}; for (const m of all) cnt[m.cat] = (cnt[m.cat] || 0) + 1;
  const order = Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a]), n = results.length; const sum = (f) => results.reduce((a, r) => a + f(r), 0); const nm = sum((r) => r.nMoves) || 1;
  const outc = (r) => fmtRes(r.g, state.user); const w = results.filter((r) => outc(r) === "Won").length, l = results.filter((r) => outc(r) === "Lost").length;
  const phs = {}; for (const k of Object.keys(PHN)) { phs[k] = { n: 0, big: 0, loss: 0 }; for (const r of results) { phs[k].n += r.ph[k].n; phs[k].loss += Math.round(r.ph[k].loss); phs[k].big += r.ph[k].big; } }
  const worst = Object.keys(PHN).filter((k) => phs[k].n >= 5 && phs[k].big > 0).sort((a, b) => phs[b].loss / phs[b].n - phs[a].loss / phs[a].n)[0] || null;
  const top12 = all.slice().sort((a, b) => b.loss - a.loss).slice(0, 12);
  const moments = top12.map((m) => ({ fen: m.fen, from: m.from, to: m.to, bFrom: m.bFrom, bTo: m.bTo, san: m.san, best: m.best, cat: m.cat, moveNo: m.moveNo, color: m.color, detail: m.detail, before: Math.round(m.before), after: Math.round(m.after), clock: m.clock, pv: m.pv, loss: Math.round(m.loss), side: m.r.side, opp: m.r.side === "w" ? m.r.g.black : m.r.g.white, url: m.r.g.url }));
  const lossNow = sum((r) => r.avgLoss * r.nMoves) / nm;
  return { user: state.user, n, total: all.length, cnt, order, late: all.filter((m) => m.clock !== null && m.clock < 30).length, phs, worst, acc: sum((r) => r.acc * r.nMoves) / nm, nB: sum((r) => r.nBlund), nM: sum((r) => r.nMist), nI: sum((r) => r.nInacc), w, d: n - w - l, l, band: bandOf(lossNow / 100), lossNow,
    traps: results.filter((r) => r.trap).map((r) => ({ slug: r.trap.t.slug, name: r.trap.t.name, fell: r.trap.fell })),
    games: results.map((r) => { const tp = r.moments.slice().sort((a, b) => b.loss - a.loss)[0]; return { res: outc(r), side: r.side, opp: r.side === "w" ? r.g.black : r.g.white, acc: r.acc, url: r.g.url, tp: tp ? `${tp.moveNo}${tp.color === "w" ? "." : "…"}${tp.san}` : null }; }), moments };
}
function oppView(V, savedAt) {
  const top = V.order[0], n = V.n, who = esc(V.user), based = `Based on ${plural(n, "game")}`; SHOWN = V.moments; const first3 = SHOWN.slice(0, 3).map((m, i) => i), rest = SHOWN.slice(3).map((m, i) => i + 3);
  const S = [];
  if (top) S.push({ c: "hero", h: `<span class="dk-k">🎯 Scouting <b>${who}</b> · ${based.toLowerCase()}</span><p class="dk-q">Their biggest weak point</p><div class="dk-big c-${top}"><span>${ICON[top]}</span>${AIM[top].t}</div><span class="dk-pill">Seen ${V.cnt[top]}× in ${plural(n, "game")}</span><div class="dk-tip"><b>How to use it</b>${AIM[top].tip}</div>${first3.length ? `<button class="btn solid" type="button" data-go="1">See it on the board ›</button>` : ""}` });
  else S.push({ c: "hero", h: `<span class="dk-k">🎯 Scouting <b>${who}</b> · ${based.toLowerCase()}</span><div class="dk-big"><span>🧼</span>No clear weak point yet</div><div class="dk-tip"><b>Try this</b>Pick a few of their losses. That is where the weak points show.</div>` });
  first3.forEach((i) => S.push({ h: momentHtml(SHOWN[i], i) }));
  const more = V.order.slice(1, 3);
  if (more.length) S.push({ h: `<p class="dk-q">${more.length === 1 ? "One more weak point" : "Two more weak points"}</p>` + more.map((c) => `<div class="dk-tile c-${c}"><span class="ti">${ICON[c]}</span><div><b>${AIM[c].t}</b> <i>${V.cnt[c]}×</i><p>${AIM[c].tip}</p></div></div>`).join("") });
  if (top && (V.worst || V.late >= 2 || V.traps.length)) S.push({ h: `<p class="dk-q">When they slip</p>${phaseBar(V.phs, V.worst)}${V.worst ? `<p class="dk-1">Most costly moves: the <b>${PHN[V.worst].toLowerCase()}</b>. ${PHAIM[V.worst]}</p>` : ""}${V.late >= 2 ? `<div class="dk-tile"><span class="ti">⏱</span><div><b>Weak under time pressure</b> <i>${V.late}×</i><p>Play at a steady pace. When their clock runs low, the mistakes come.</p></div></div>` : ""}` +
    V.traps.map((t) => `<div class="dk-tile"><span class="ti">${t.fell ? "🪤" : "🎯"}</span><div><b>${t.fell ? "Fell for the" : "Sets the"} ${esc(t.name)}</b><p><a href="/traps/${t.slug}/?utm_source=opponent&amp;utm_campaign=${t.slug}">${t.fell ? "Learn it and set it yourself ›" : "Learn the fix before you play them ›"}</a></p></div></div>`).join("") });
  S.push({ c: "end", h: `<div class="dk-ic">♟️</div><p class="dk-q">You are ready</p><ul class="dk-ck">${top ? `<li>Watch for: <b>${AIM[top].t.toLowerCase()}</b></li>` : ""}<li>Play your normal game</li><li>${plural(n, "game")} ${n === 1 ? "shows" : "show"} a pattern, not a promise</li></ul>${pracItems().length ? `<button class="btn solid" type="button" data-prac>🧩 Practice punishing their mistakes</button><a class="small" data-ev="opponent-cta-analyze" href="/analyze/?utm_source=opponent&amp;utm_campaign=opponent">Or check my own games ›</a>` : `<a class="btn solid" data-ev="opponent-cta-analyze" href="/analyze/?utm_source=opponent&amp;utm_campaign=opponent">Now check my own games</a>`}<div class="az-save" id="az-save">${savedAt ? `<p class="small">Saved report from ${new Date(savedAt).toLocaleDateString()}. <a href="/opponent/">Scout again ›</a></p>` : ""}</div>` });
  PRAC = null; let h = `<h2 class="sr">Scouting report</h2>` + deck(S) + `<div id="az-prac"></div>`;
  if (rest.length) h += `<details class="az-det"><summary>${rest.length} more moment${rest.length === 1 ? "" : "s"}</summary><div class="dk-more">${rest.map((i) => momentHtml(SHOWN[i], i)).join("")}</div></details>`;
  h += `<details class="az-det"><summary>All the numbers</summary>${numbersHtml(V, false)}</details>${followHtml}<div id="az-fb"></div>`;
  $("#az-report").innerHTML = h; deckInit();
}
// ---------- practice: the costly positions as puzzles, on a board you can tap ----------
let PRAC = null;
function pracItems() { const out = [];
  for (const m of SHOWN) { if (out.length >= 5) break;
    if (!OPP) { if (m.bFrom && m.bTo && m.loss >= 150) out.push({ fen: m.fen, flip: mSide(m) === "b", from: m.bFrom, to: m.bTo, base: m.before, q: `You played <b>${esc(m.san)}</b> here. Find the better move.` }); continue; }
    const u = m.pv && m.pv[0]; if (!u || m.loss < 150) continue; const c = new Chess(m.fen); let ok = null; try { ok = c.move({ from: m.from, to: m.to, promotion: "q" }); } catch (e) {} if (!ok) continue;
    out.push({ fen: c.fen(), flip: mSide(m) === "w", from: u.slice(0, 2), to: u.slice(2, 4), base: -m.after, last: [m.from, m.to], q: `They just played <b>${esc(m.san)}</b>. Punish it.` }); }
  return out; }
function pracDraw(msg, cls, hl) { const it = PRAC.items[PRAC.i], last = PRAC.i === PRAC.items.length - 1, white = PRAC.fen.split(" ")[1] === "w"; hl = hl || it.last || [];
  $("#az-prac").innerHTML = `<div class="pr-card"><div class="pr-top"><span class="dk-q">🧩 Practice ${PRAC.i + 1} / ${PRAC.items.length}</span><span class="dk-pill">✓ ${PRAC.ok}</span></div><p class="dk-1">${it.q}</p>
    <div class="pr-b">${boardSVG(PRAC.fen, hl[0], hl[1], it.flip, PRAC.sel, null)}</div><p class="pr-msg ${cls || ""}" role="status">${msg || (white ? "White" : "Black") + " to move. Tap a piece, then tap where it goes."}</p>
    <div class="pr-act">${PRAC.done ? `<button class="btn solid" type="button" data-pr="next">${last ? "Finish ›" : "Next position ›"}</button>` : `<button class="btn" type="button" data-pr="hint">💡 Hint</button><button class="btn" type="button" data-pr="show">Show answer</button>`}</div></div>`; }
function pracStart() { const items = pracItems(); if (!items.length) return; PRAC = { items, i: 0, ok: 0, sel: null, done: false, fen: items[0].fen, shown: false }; pracDraw(); $("#az-prac").scrollIntoView({ behavior: "smooth", block: "start" }); ev((OPP ? "opponent" : "analyze") + "-practice-start"); }
function pracSolve(byUser, mv) { const it = PRAC.items[PRAC.i], c = new Chess(it.fen); let m = null; try { m = c.move(mv || { from: it.from, to: it.to, promotion: "q" }); } catch (e) {} if (!m) return;
  PRAC.done = true; PRAC.sel = null; PRAC.fen = c.fen(); if (byUser) PRAC.ok++; pracDraw(byUser ? `✓ Correct: ${esc(m.san)}` : `The move was ${esc(m.san)}.`, byUser ? "ok" : "", [m.from, m.to]); }
async function pracTap(sq) { if (!PRAC || PRAC.done || PRAC.busy) return; const it = PRAC.items[PRAC.i], c = new Chess(it.fen), pc = c.get(sq), turn = it.fen.split(" ")[1];
  if (!PRAC.sel || (pc && pc.color === turn)) { PRAC.sel = pc && pc.color === turn ? sq : null; pracDraw(PRAC.sel ? "Now tap the square it goes to." : ""); return; }
  const from = PRAC.sel; let m = null; try { m = c.move({ from, to: sq, promotion: "q" }); } catch (e) {} PRAC.sel = null;
  if (!m) { pracDraw("That piece cannot go there. Try again.", "bad"); return; }
  if (from === it.from && sq === it.to) return pracSolve(true);
  const E = engines.lite || engines.full;
  if (E) { PRAC.busy = true; pracDraw("Checking your move…"); let good = false; try { const r = await E.analyse(c.fen()); good = it.base - clip(pov(r.score, turn === "w")) < 70; } catch (e) {} PRAC.busy = false; if (good) return pracSolve(true, { from, to: sq, promotion: "q" }); }
  pracDraw(`${esc(m.san)} is not the move. Try again, or tap Hint.`, "bad"); }
document.addEventListener("click", (e) => { if (e.target.closest("[data-prac]")) return pracStart(); if (!PRAC) return; const b = e.target.closest("[data-pr]");
  if (b) { const it = PRAC.items[PRAC.i]; if (b.dataset.pr === "hint") { PRAC.sel = it.from; pracDraw("This piece makes the move. Where does it go?"); }
    else if (b.dataset.pr === "show") pracSolve(false);
    else if (PRAC.i < PRAC.items.length - 1) { PRAC.i++; PRAC.sel = null; PRAC.done = false; PRAC.fen = PRAC.items[PRAC.i].fen; pracDraw(); }
    else { const n = PRAC.items.length, k = PRAC.ok; PRAC = null; ev((OPP ? "opponent" : "analyze") + "-practice-done"); $("#az-prac").innerHTML = `<div class="pr-card end"><div class="dk-ic">${k === n ? "🏆" : "🏁"}</div><p class="dk-q">${k} of ${n} found</p><p class="dk-1">${OPP ? "That is how you punish them. Now find your own weak point." : "Play 5 new games, then come back and see what changed."}</p><div class="pr-act">${OPP ? `<a class="btn solid" data-ev="opponent-cta-analyze" href="/analyze/?utm_source=opponent&amp;utm_campaign=opponent">Check my own games</a>` : `<button class="btn solid" type="button" data-prac>↻ Practice again</button><a class="btn" data-ev="analyze-cta-free" href="/free/?utm_source=analyze&amp;utm_campaign=analyze">Free trap cheat sheet</a>`}</div></div>`; }
    return; }
  const svg = e.target.closest("#az-prac svg.mini"); if (!svg) return; const r = svg.getBoundingClientRect(), x = Math.min(7, Math.max(0, Math.floor(((e.clientX - r.left) / r.width) * 8))), y = Math.min(7, Math.max(0, Math.floor(((e.clientY - r.top) / r.height) * 8))), fl = svg.dataset.flip === "1";
  pracTap("abcdefgh"[fl ? 7 - x : x] + (fl ? y + 1 : 8 - y)); });
function getSb() { return window.supabase ? (window.__sb = window.__sb || window.supabase.createClient("https://ytxrrmvszifvtdyilezn.supabase.co", "sb_publishable_nARSIxN5aKJghUK745Frdw_QbXhdf29", { auth: { persistSession: true, detectSessionInUrl: false } })) : null; }
async function saveOpp(V) { const box = $("#az-save"), sbc = getSb(); if (!box || !sbc) return; const { data } = await sbc.auth.getSession();
  if (!data.session) { box.innerHTML = `<p class="small">💾 <a href="/members/?utm_source=opponent">Log in</a> (free) to keep this report and open it again before your game.</p>`; return; }
  const { error } = await sbc.from("analyses").insert({ site: state.site, username: String(V.user).slice(0, 40), games: V.n, accuracy: +V.acc.toFixed(1), avg_loss: +(V.lossNow / 100).toFixed(3), blunders: V.nB, mistakes: V.nM, inaccuracies: V.nI, band: bandName(V.band), top_leak: V.order[0] ? AIM[V.order[0]].t : null, report: { kind: "opponent", depth: DEPTH, cats: V.cnt, v: V } });
  box.innerHTML = error ? `<p class="small">${/limit/i.test(error.message || "") ? "You reached the limit of saved reports. Delete older ones on your members page." : "Could not save this report."}</p>` : `<p class="small">✓ Saved. Open it any time under <a href="/members/#reports">Scouted opponents</a>.</p>`; if (!error) { ev("opponent-report-saved"); window.dispatchEvent(new Event("az-saved")); } }
async function openSaved() { const id = new URLSearchParams(location.search || "").get("r"); if (!OPP || !id || !/^[0-9a-f-]{36}$/i.test(id)) return; const box = $("#az-report"), sbc = getSb(); if (!sbc) return; box.innerHTML = `<p class="small">Opening your saved report…</p>`;
  const { data: s } = await sbc.auth.getSession(); if (!s.session) { box.innerHTML = `<p>Log in to open your saved report.</p><p><a class="btn solid" href="/members/">Log in</a></p>`; return; }
  const { data, error } = await sbc.from("analyses").select("created_at,username,site,report").eq("id", id).maybeSingle();
  if (error || !data || !data.report || !data.report.v) { box.innerHTML = `<p>This saved report could not be opened. <a href="/opponent/">Scout again ›</a></p>`; return; }
  state.user = data.username; state.site = data.site; oppView(data.report.v, data.created_at); box.scrollIntoView({ behavior: "smooth" }); ev("opponent-report-opened"); }
function oppReport(results) { const V = viewModel(results); oppView(V); saveOpp(V);
  try { if (window.tcFeedback) window.tcFeedback.inline($("#az-fb"), "opponent-report", "Was this report useful?", { games: V.n, depth: DEPTH, prem: isPrem() }); } catch (e) {} $("#az-report").scrollIntoView({ behavior: "smooth" }); ev("opponent-report"); }
function report(results) {
  if (OPP) return oppReport(results); // saved with report.kind = "opponent", so it never mixes with your own progress
  const all = results.flatMap((r, ri) => r.moments.map((m) => ({ ...m, r, ri }))); const cnt = {}; for (const m of all) cnt[m.cat] = (cnt[m.cat] || 0) + 1;
  const order = Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a]); const max = Math.max(1, ...Object.values(cnt));
  const late = all.filter((m) => m.clock !== null && m.clock < 30).length;
  const sum = (f) => results.reduce((a, r) => a + f(r), 0); const nm = sum((r) => r.nMoves) || 1;
  const acc = sum((r) => r.acc * r.nMoves) / nm, nB = sum((r) => r.nBlund), nM = sum((r) => r.nMist), nI = sum((r) => r.nInacc);
  const outc = (r) => fmtRes(r.g, state.user); const wins = results.filter((r) => outc(r) === "Won").length, losses = results.filter((r) => outc(r) === "Lost").length, draws = results.length - wins - losses;
  const top3 = results.map((r, ri) => all.filter((m) => m.ri === ri).sort((x, y) => y.loss - x.loss)[0]).filter(Boolean);
  const accFix = (sum((r) => r.acc * r.nMoves) + top3.reduce((a, m) => a + (100 - m.a), 0)) / nm, lossNow = sum((r) => r.avgLoss * r.nMoves) / nm, lossFix = (sum((r) => r.avgLoss * r.nMoves) - top3.reduce((a, m) => a + Math.min(m.loss, 1000), 0)) / nm;
  const bNow = bandOf(lossNow / 100), bFix = bandOf(lossFix / 100), bNext = Math.min(BANDS.length - 1, bNow + 1), blPer = nB / results.length;
  const latest = results.slice().sort((x, y) => y.g.date - x.g.date)[0]; const cur = latest && latest.side ? (latest.side === "w" ? latest.g.wrat : latest.g.brat) : null;
  const nTop = top3.length, n = results.length;
  const phs = {}; for (const k of Object.keys(PHN)) { phs[k] = { n: 0, loss: 0, big: 0 }; for (const r of results) { phs[k].n += r.ph[k].n; phs[k].loss += r.ph[k].loss; phs[k].big += r.ph[k].big; } }
  const worst = Object.keys(PHN).filter((k) => phs[k].n >= 5).sort((a, b) => phs[b].loss / phs[b].n - phs[a].loss / phs[a].n)[0];
  const top = order[0];
  SHOWN = all.slice().sort((a, b) => b.loss - a.loss).slice(0, 12).sort((a, b) => a.ri - b.ri || a.ply - b.ply);
  const rank = SHOWN.map((m, i) => i).sort((x, y) => SHOWN[y].loss - SHOWN[x].loss), first3 = rank.slice(0, 3), rest = rank.slice(3);
  const V = viewModel(results); const S = [], nx = order[1] && cnt[order[1]] ? order[1] : null;
  if (top) S.push({ c: "hero", h: `<span class="dk-k">🔍 <b>${esc(state.user)}</b> · ${plural(n, "game")} · ${all.length} costly move${all.length === 1 ? "" : "s"}</span><p class="dk-q">Fix this first</p><div class="dk-big c-${top}"><span>${ICON[top]}</span>${P[top].t}</div><span class="dk-pill">${cnt[top]}× in ${plural(n, "game")}</span><div class="dk-tip"><b>Do this</b>${DRILL[top][0]}</div>${first3.length ? `<button class="btn solid" type="button" data-go="1">See it on the board ›</button>` : ""}` });
  else S.push({ c: "hero", h: `<span class="dk-k">🔍 <b>${esc(state.user)}</b> · ${plural(n, "game")}</span><div class="dk-big"><span>🧼</span>Clean games!</div><div class="dk-tip"><b>Try this</b>Pick a few of your losses to find what to train.</div>` });
  first3.forEach((i) => S.push({ h: momentHtml(SHOWN[i], i) }));
  if (top && nTop) S.push({ h: `<p class="dk-q">What it is worth</p><div class="dk-gain"><div><b>${acc.toFixed(0)}%</b><span>accuracy now</span></div><i>→</i><div class="up"><b>${accFix.toFixed(0)}%</b><span>without ${nTop === 1 ? "your biggest mistake" : "the biggest mistake per game"}</span></div></div>${bFix > bNow ? `<p class="dk-1">That is the level of players rated about <b>${bandName(bFix)}</b>. Today: ${bandName(bNow)}.</p>` : ""}${phaseBar(V.phs, V.worst)}${V.worst ? `<p class="dk-1">Most costly moves: the <b>${PHN[V.worst].toLowerCase()}</b>.</p>` : ""}` });
  if (top) S.push({ c: "end", h: `<div class="dk-ic">✅</div><p class="dk-q">What next?</p><ul class="dk-ck"><li>${DRILL[top][1]}</li><li>Come back with 5 new games. We show you what changed.</li>${nx ? `<li>Next habit: <b>${P[nx].t.toLowerCase()}</b></li>` : ""}</ul>` + results.filter((r) => r.trap).map((r) => `<div class="dk-tile"><span class="ti">${r.trap.fell ? "🪤" : "🎯"}</span><div><b>${r.trap.fell ? "You fell for the" : "You set the"} ${esc(r.trap.t.name)}</b><p><a href="/traps/${r.trap.t.slug}/?utm_source=analyze&amp;utm_campaign=${r.trap.t.slug}">${r.trap.fell ? "See how to avoid it ›" : "See the full trap ›"}</a></p></div></div>`).join("") + `${pracItems().length ? `<button class="btn solid" type="button" data-prac>🧩 Practice these positions</button>` : `<a class="btn solid" data-ev="analyze-cta-free" href="/free/?utm_source=analyze&amp;utm_campaign=analyze">Get the free trap cheat sheet</a>`}<div class="az-save" id="az-save"></div>` });
  PRAC = null; let h = `<h2 class="sr">Your report</h2>` + deck(S) + `<div id="az-prac"></div>`;
  if (rest.length) h += `<details class="az-det"><summary>${rest.length} more moment${rest.length === 1 ? "" : "s"}</summary><div class="dk-more">${rest.map((i) => momentHtml(SHOWN[i], i)).join("")}</div></details>`;
  if (!top) h += `<div class="az-save" id="az-save"></div>`;
  let d = `<p class="small"><b>Big mistake:</b> a move that loses a piece or more. <b>Mistake:</b> a move that loses a pawn or two. <b>Small slip:</b> a smaller loss. <b>Accuracy:</b> how close your moves were to the best ones (100% would be perfect). It is our own estimate, so compare moves, not percentages with Chess.com or Lichess.</p>`;
  d += `<div class="az-score"><div><b>${acc.toFixed(0)}%</b><span>Accuracy</span></div><div><b>${nB}</b><span>Big mistakes</span></div><div><b>${nM}</b><span>Mistakes</span></div><div><b>${nI}</b><span>Small slips</span></div><div><b>${wins}-${draws}-${losses}</b><span>Won-drawn-lost</span></div></div>`;
  d += `${ratingsLine(cur, latest)}<p>Your play looks like players rated about <b>${bandName(bNow)}</b>. That comes from our own sample of 270 Chess.com rapid games (30 per rating band). A guide, not an official rating${n < 3 ? ". Analyze 3 to 5 games for a steadier estimate" : ""}.</p>`;
  d += bNow < BANDS.length - 1 ? `<p>Players rated about ${bandName(bNext)} make about ${BANDS[bNext].bl.toFixed(1)} big mistakes per game. You made ${blPer.toFixed(1)}. Big mistakes are the fastest way up: before every move, check their checks, captures and threats.</p>` : `<p>Players in your band make about ${BANDS[bNow].bl.toFixed(1)} big mistakes per game and you made ${blPer.toFixed(1)}. Keep the 3-second check (checks, captures, threats) before every move.</p>`;
  d += `<h4>Where in the game</h4><div class="az-ph">` + Object.keys(PHN).map((k) => `<div class="${k === worst ? "worst" : ""}"><span>${PHN[k]}</span><b>${phs[k].big}</b><small>costly move${phs[k].big === 1 ? "" : "s"}<br>in ${phs[k].n} moves</small></div>`).join("") + `</div>`;
  d += `<h4>Game by game</h4><div class="az-gm">` + results.map((r) => { const opp = r.side === "w" ? r.g.black : r.g.white; const tp = r.moments.slice().sort((a, b) => b.loss - a.loss)[0];
    return `<a href="${esc(safeUrl(r.g.url))}" target="_blank" rel="noopener"><span class="res ${outc(r).toLowerCase()}">${outc(r)}</span><span>${r.side === "w" ? "White" : "Black"} vs <b>${esc(opp)}</b></span><span class="small">${r.acc.toFixed(0)}% accuracy${tp ? ` · costliest move: ${tp.moveNo}${tp.color === "w" ? "." : "…"}${esc(tp.san)}` : " · no big mistakes"}</span></a>`; }).join("") + `</div>`;
  if (order.length) d += `<h4>What kind of mistakes</h4><div class="az-bars">` + order.map((c) => `<div class="az-bar"><span>${P[c].t}</span><i style="width:${(100 * cnt[c]) / max}%"></i><b>${cnt[c]}</b></div>`).join("") + `</div>`;
  if (order[1]) d += `<h4>A second habit, for later</h4><div class="az-plan"><p><b>${P[order[1]].t}:</b> ${DRILL[order[1]][0]}</p></div>`;
  if (late) d += `<p class="small">⏱ ${late} of these moves came with less than 30 seconds on your clock. Part of the fix may be using your time earlier in the game.</p>`;
  if (DEPTH > 14) d += `<p class="small">Analyzed in extra depth (${DEPTH}). The rating guide was made with the standard setting, so treat that comparison as approximate.</p>`;
  h += `<details class="az-det"><summary>All the numbers</summary>${d}</details>`;
  h += followHtml;
  h += '<div id="az-fb"></div>';
  window.__azLast = { acc, lossNow, nB, nM, nI, bNow, order, cnt, results, SHOWN };
  $("#az-report").innerHTML = h; deckInit(); saveReport(); try { if (window.tcFeedback) window.tcFeedback.inline($("#az-fb"), "analysis-report", "Was this report useful?", { games: results.length, depth: DEPTH, prem: isPrem() }); } catch (e) {} $("#az-report").scrollIntoView({ behavior: "smooth" }); ev("analyze-report");
}

window.__azP = { P, DRILL }; window.__azBoard = boardSVG;
if (/[?&]bench=1/.test(location.search)) window.__az = { analyseGame };
openSaved();
window.__azReady = true; window.dispatchEvent(new Event("az-ready"));
