// Throiy Chess · Analyze your games (beta). Runs fully in the visitor's browser.
// Games: Chess.com Published-Data API / Lichess API. Engine: Stockfish 17.1 lite (GPLv3), single-threaded WASM.
import { Chess } from "/js/chess.js";

const $ = (s, r = document) => r.querySelector(s);
const MAX_FREE = 5, DEPTH = 14;
const VAL = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 };
const NAMES = { p: "pawn", n: "knight", b: "bishop", r: "rook", q: "queen", k: "king" };
const TRAPS = JSON.parse($("#trap-data").textContent);
const ev = (n) => { try { if (window.goatcounter && goatcounter.count) goatcounter.count({ path: n, title: n, event: true }); } catch (e) {} };
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

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
  other:  { t: "Strategic error", tip: "Compare your move with the better one: which pieces does it improve? Ask what your worst piece is and improve it." },
};

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

// ---------- engine ----------
class Engine {
  constructor() { this.w = new Worker("/js/stockfish/stockfish-17.1-lite-single-03e3232.js"); this.q = Promise.resolve(); this.lis = null;
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
let engine = null;
async function getEngine() { if (!engine) { engine = new Engine(); await engine.init(); } return engine; }

// ---------- fetching games ----------
async function fetchChesscom(user) {
  const a = await fetch(`https://api.chess.com/pub/player/${encodeURIComponent(user.toLowerCase())}/games/archives`);
  if (!a.ok) throw new Error("Player not found on Chess.com.");
  const months = (await a.json()).archives.slice(-2).reverse(); let games = [];
  for (const m of months) { const r = await fetch(m); if (r.ok) games = games.concat((await r.json()).games || []); if (games.length >= 30) break; }
  return games.filter((g) => g.pgn && (g.rules || "chess") === "chess").sort((x, y) => y.end_time - x.end_time).slice(0, 30).map((g) => ({
    pgn: g.pgn, white: g.white.username, black: g.black.username, wres: g.white.result, bres: g.black.result,
    tc: g.time_class, date: new Date(g.end_time * 1000), url: g.url }));
}
async function fetchLichess(user) {
  const r = await fetch(`https://lichess.org/api/games/user/${encodeURIComponent(user)}?max=30&clocks=true&pgnInJson=true&perfType=ultraBullet,bullet,blitz,rapid,classical,correspondence`,
    { headers: { Accept: "application/x-ndjson" } });
  if (!r.ok) throw new Error("Player not found on Lichess.");
  const lines = (await r.text()).trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
  return lines.filter((g) => g.variant === "standard" && g.pgn).map((g) => ({
    pgn: g.pgn, white: g.players.white.user ? g.players.white.user.name : "Anonymous", black: g.players.black.user ? g.players.black.user.name : "Anonymous",
    wres: g.winner === "white" ? "win" : g.winner ? "loss" : "draw", bres: g.winner === "black" ? "win" : g.winner ? "loss" : "draw",
    tc: g.speed, date: new Date(g.createdAt), url: "https://lichess.org/" + g.id }));
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
      else if (bm && (bm.captured || bm.san.includes("+"))) { cat = "tactic"; detail = "You had a forcing move."; }
    } else if (bm && (bm.captured || bm.san.includes("+")) && loss >= 200) { cat = "tactic"; detail = "You had a forcing move."; }
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
  const rows = fen.split(" ")[0].split("/"); let s = `<svg viewBox="0 0 8 8" class="mini" role="img" aria-label="Board position">`;
  for (let r = 0; r < 8; r++) { let f = 0; for (const ch of rows[r]) { if (/\d/.test(ch)) { f += +ch; continue; }
      const x = flip ? 7 - f : f, y = flip ? 7 - r : r; s += `<text x="${x + 0.5}" y="${y + 0.82}" class="${ch === ch.toUpperCase() ? "pw" : "pb"}">${GLYPH[ch.toLowerCase()]}</text>`; f++; } }
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
  try { const games = site === "lichess" ? await fetchLichess(user) : await fetchChesscom(user); state.games = games; ev("analyze-fetch-" + site);
    if (!games.length) { out.innerHTML = '<p class="small">No standard games found in the last months.</p>'; return; }
    out.innerHTML = `<p>Pick up to <strong>${MAX_FREE} games</strong> to analyze. Tip: your losses teach the most.</p><div class="az-list">` +
      games.map((g, i) => { const w = g.white.toLowerCase() === user.toLowerCase(); const opp = w ? g.black : g.white;
        return `<label class="az-g"><input type="checkbox" value="${i}"><span class="res ${fmtRes(g, user).toLowerCase()}">${fmtRes(g, user)}</span>
          <span>${w ? "White" : "Black"} vs <b>${esc(opp)}</b></span><span class="small">${esc(g.tc || "")} · ${g.date.toLocaleDateString()}</span></label>`; }).join("") +
      `</div><button class="btn solid" id="az-go" type="button">Analyze selected games</button><p class="small" id="az-prog" role="status" aria-live="polite"></p>`;
    out.addEventListener("change", (ev2) => { const sel = out.querySelectorAll("input:checked"); if (sel.length > MAX_FREE) { ev2.target.checked = false; } });
    $("#az-go").addEventListener("click", run);
  } catch (err) { out.innerHTML = `<p class="small">${esc(err.message || "Could not fetch games.")}</p>`; }
});

async function run() {
  const idx = [...document.querySelectorAll("#az-games input:checked")].map((x) => +x.value); if (!idx.length) return;
  $("#az-go").disabled = true; const prog = $("#az-prog"); prog.textContent = "Loading the engine (7 MB, once)…"; ev("analyze-run");
  const results = [];
  for (let k = 0; k < idx.length; k++) {
    const g = state.games[idx[k]];
    results.push(await analyseGame(g, state.user, (a, b) => { prog.textContent = `Game ${k + 1} of ${idx.length}: position ${a} of ${b}…`; }));
  }
  prog.textContent = "Done."; $("#az-go").disabled = false; report(results);
}

document.addEventListener("click", (e0) => { const bt = e0.target.closest(".az-replay"); if (!bt || bt.disabled) return; const m = SHOWN[+bt.dataset.i]; if (!m) return;
  const box = bt.closest(".az-m"), svg = () => box.querySelector("svg.mini"), orig = svg().outerHTML; bt.disabled = true; ev("analyze-replay");
  const c = new Chess(m.fen), seq = [m.from + m.to + (m.promo || "")].concat(m.pv); const lab = (i) => i === 0 ? "Your move" : "Opponent's best reply" + (i > 1 ? " and the line continues" : ""); let i = 0;
  const msg = box.querySelector(".az-rp") || bt.insertAdjacentElement("afterend", Object.assign(document.createElement("span"), { className: "az-rp small" })) || box.querySelector(".az-rp");
  const step = () => { if (i >= seq.length) { setTimeout(() => { svg().outerHTML = orig; box.querySelector(".az-rp").textContent = ""; bt.disabled = false; }, 1600); return; }
    const u = seq[i]; let mv = null; try { mv = c.move({ from: u.slice(0, 2), to: u.slice(2, 4), promotion: u[4] || "q" }); } catch (e) {}
    if (!mv) { svg().outerHTML = orig; bt.disabled = false; return; }
    svg().outerHTML = boardSVG(c.fen(), mv.from, mv.to, m.r.side === "b"); box.querySelector(".az-rp").textContent = ` ${lab(i)}: ${mv.san}`; i++; setTimeout(step, 1300); };
  step(); });
function report(results) {
  const all = results.flatMap((r, ri) => r.moments.map((m) => ({ ...m, r, ri }))); const cnt = {}; for (const m of all) cnt[m.cat] = (cnt[m.cat] || 0) + 1;
  const order = Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a]); const max = Math.max(1, ...Object.values(cnt));
  const late = all.filter((m) => m.clock !== null && m.clock < 30).length;
  const sum = (f) => results.reduce((a, r) => a + f(r), 0); const nm = sum((r) => r.nMoves) || 1;
  const acc = sum((r) => r.acc * r.nMoves) / nm, nB = sum((r) => r.nBlund), nM = sum((r) => r.nMist), nI = sum((r) => r.nInacc);
  const outc = (r) => fmtRes(r.g, state.user); const wins = results.filter((r) => outc(r) === "Won").length, losses = results.filter((r) => outc(r) === "Lost").length, draws = results.length - wins - losses;
  const top3 = results.map((r, ri) => all.filter((m) => m.ri === ri).sort((x, y) => y.loss - x.loss)[0]).filter(Boolean);
  const accFix = (sum((r) => r.acc * r.nMoves) + top3.reduce((a, m) => a + (100 - m.a), 0)) / nm, lossNow = sum((r) => r.avgLoss * r.nMoves) / nm, lossFix = (sum((r) => r.avgLoss * r.nMoves) - top3.reduce((a, m) => a + Math.min(m.loss, 1000), 0)) / nm;
  const bNow = bandOf(lossNow / 100), bFix = bandOf(lossFix / 100), bNext = Math.min(BANDS.length - 1, bNow + 1), blPer = nB / results.length;
  const whatIf = top3.length ? `<div class="az-what"><p><b>What if you had found the better move in the biggest mistake of each game?</b> Accuracy about <b>${accFix.toFixed(0)}%</b> instead of ${acc.toFixed(0)}%, and <b>${(lossFix / 100).toFixed(2)}</b> instead of ${(lossNow / 100).toFixed(2)} pawns lost per move.</p>
    <p><b>Improve your rating with this:</b> your play looks like players rated about <b>${bandName(bNow)}</b>. ${bFix > bNow ? `With those mistakes fixed it looks like players rated about <b>${bandName(bFix)}</b>.` : `Players rated about ${bandName(bNext)} lose ${BANDS[bNext].loss.toFixed(2)} pawns per move on average; you lose ${(lossNow / 100).toFixed(2)}.`}</p>
    <p class="small">Based on our own sample of 270 Chess.com rapid games (30 per rating band), analyzed with the same engine. A guide, not an official rating${results.length < 3 ? ". Analyze 3 to 5 games for a steadier estimate" : ""}.</p></div>` : "";
  const tip3 = bNow < BANDS.length - 1 ? `Players rated about ${bandName(bNext)} make about ${BANDS[bNext].bl.toFixed(1)} blunders per game (moves that lose 3+ pawns). You made ${blPer.toFixed(1)}. Blunders are the fastest way up: before every move, check their checks, captures and threats.` : `Players in your band make about ${BANDS[bNow].bl.toFixed(1)} blunders per game and you made ${blPer.toFixed(1)}. Keep the 3-second check (checks, captures, threats) before every move.`;
  let h = `<h2>Your report</h2><p>${results.length} game${results.length > 1 ? "s" : ""} analyzed for <b>${esc(state.user)}</b>. We found <b>${all.length}</b> moment${all.length === 1 ? "" : "s"} where the evaluation dropped by more than a pawn.</p>`;
  h += `<div class="az-score"><div><b>${acc.toFixed(0)}%</b><span>Accuracy (our estimate)</span></div><div><b>${(sum((r) => r.avgLoss * r.nMoves) / nm / 100).toFixed(2)}</b><span>Pawns lost per move</span></div><div><b>${nB}</b><span>Blunders</span></div><div><b>${nM}</b><span>Mistakes</span></div><div><b>${nI}</b><span>Inaccuracies</span></div><div><b>${wins}-${draws}-${losses}</b><span>Won-drawn-lost</span></div></div>${whatIf}<p class="small">Accuracy here is our own estimate at a light engine depth. It is not on the same scale as the Chess.com or Lichess accuracy, so compare moves, not percentages.</p>`;
  // phases
  const phs = {}; for (const k of Object.keys(PHN)) { phs[k] = { n: 0, loss: 0, big: 0 }; for (const r of results) { phs[k].n += r.ph[k].n; phs[k].loss += r.ph[k].loss; phs[k].big += r.ph[k].big; } }
  const worst = Object.keys(PHN).filter((k) => phs[k].n >= 5).sort((a, b) => phs[b].loss / phs[b].n - phs[a].loss / phs[a].n)[0];
  h += `<h3>Where you lose points</h3><div class="az-ph">` + Object.keys(PHN).map((k) => `<div class="${k === worst ? "worst" : ""}"><span>${PHN[k]}</span><b>${phs[k].n ? (phs[k].loss / phs[k].n / 100).toFixed(2) : "–"}</b><small>pawns lost per move<br>${phs[k].big} big drop${phs[k].big === 1 ? "" : "s"} in ${phs[k].n} moves</small></div>`).join("") + `</div>`;
  if (worst) h += `<p class="small">Your biggest leak: the <b>${PHN[worst].toLowerCase()}</b>. That is where your moves cost the most on average.</p>`;
  // per game
  h += `<h3>Game by game</h3><div class="az-gm">` + results.map((r) => { const opp = r.side === "w" ? r.g.black : r.g.white; const top = r.moments.slice().sort((a, b) => b.loss - a.loss)[0];
    return `<a href="${esc(r.g.url)}" target="_blank" rel="noopener"><span class="res ${outc(r).toLowerCase()}">${outc(r)}</span><span>${r.side === "w" ? "White" : "Black"} vs <b>${esc(opp)}</b></span><span class="small">${r.acc.toFixed(0)}% accuracy${top ? ` · biggest drop: move ${top.moveNo}${top.color === "w" ? "." : "…"}${esc(top.san)}` : " · no big drops"}</span></a>`; }).join("") + `</div>`;
  if (order.length) {
    const top = order[0];
    h += `<div class="az-top"><span class="eyebrow">Train this first</span><h3>${P[top].t}</h3><p>${P[top].tip}</p></div>`;
    h += `<div class="az-bars">` + order.map((c) => `<div class="az-bar"><span>${P[c].t}</span><i style="width:${(100 * cnt[c]) / max}%"></i><b>${cnt[c]}</b></div>`).join("") + `</div>`;
  } else h += `<div class="az-top"><h3>Clean games!</h3><p>No big drops in these games. Try a few losses to find what to train.</p></div>`;
  if (order.length) { h += `<h3>Your 5-game training plan</h3><div class="az-plan">` + order.slice(0, 2).map((c, i) => `<div><span class="eyebrow">Focus ${i + 1}: ${P[c].t}</span><p><b>Habit:</b> ${DRILL[c][0]}</p><p><b>Practice:</b> ${DRILL[c][1]}</p></div>`).join("") + `<p class="small">Play your next 5 games with only these two focuses, then analyze them again here and compare. The free cheat sheet has a 3-second check and a quiz that train exactly this.</p></div>`; }
  if (late) h += `<p class="small">⏱ ${late} of these moments came with less than 30 seconds on your clock. Part of the fix may be using your time earlier in the game.</p>`;
  for (const r of results) if (r.trap) h += `<div class="az-trap">${r.trap.fell ? "🪤 You fell for the" : "🎯 You set the"} <a href="/traps/${r.trap.t.slug}/?utm_source=analyze&amp;utm_campaign=${r.trap.t.slug}">${esc(r.trap.t.name)}</a>${r.trap.fell ? ". Here's how to avoid it next time." : ". Nice!"}</div>`;
  h += `<h2>Key moments</h2><p class="small">On the boards: gold = the move you played, green = the better move.</p>`;
  SHOWN = all.slice().sort((a, b) => b.loss - a.loss).slice(0, 12).sort((a, b) => a.ri - b.ri || a.ply - b.ply);
  for (const [mi, m] of SHOWN.entries()) {
    const opp = m.r.side === "w" ? m.r.g.black : m.r.g.white;
    h += `<div class="az-m">${boardSVG(m.fen, m.from, m.to, m.r.side === "b", m.bFrom, m.bTo)}<div><span class="eyebrow">${P[m.cat].t}</span>${m.pv && m.pv.length ? `<button class="btn az-replay" type="button" data-i="${mi}">&#9654; Replay what happens</button>` : ""}
      <h3>Move ${m.moveNo}${m.color === "w" ? "." : "…"}${esc(m.san)} <span class="small">vs ${esc(opp)}</span></h3>
      <p>${m.detail ? esc(m.detail) + " " : ""}${m.best ? `Better was <b>${esc(m.best)}</b>.` : ""}</p>
      <p class="small">Evaluation for you: ${(m.before / 100).toFixed(1)} → ${(m.after / 100).toFixed(1)}${m.clock !== null ? ` · ${Math.round(m.clock)} s on your clock` : ""} · <a href="${esc(m.r.g.url)}" target="_blank" rel="noopener">open game</a></p>
      <p class="small"><b>Principle:</b> ${P[m.cat].tip}</p></div></div>`;
  }
  { const t1 = order.length ? `Your most common leak: <b>${P[order[0]].t.toLowerCase()}</b> (${cnt[order[0]]} time${cnt[order[0]] > 1 ? "s" : ""} in ${results.length} game${results.length > 1 ? "s" : ""}). ${P[order[0]].tip}` : "No big leaks found. Keep doing what you do and analyze a few losses.";
    const tips = { opening: "Your opening costs you the most. Play the same opening for a month, know its first 8 moves, and develop knights and bishops before the queen.", middlegame: "Your middlegame costs you the most. When the position gets busy, slow down: list your opponent's forcing moves (checks, captures, threats) before you choose.", endgame: "Your endgame costs you the most. Practice king and pawn endings 10 minutes a day: activate the king, push passed pawns." };
    h += `<h3>3 top tips for you</h3><ol class="az-tips"><li>${t1}</li><li>${worst ? tips[worst] : "Analyze more games to see which phase costs you most."}</li><li>${tip3}</li></ol>`; }
  h += `<div class="az-pro"><span class="eyebrow">Go deeper</span><h3>Want a more in-depth analysis?</h3><p>This report uses a light engine and 5 games. Join the improvement program: a stronger engine looking deeper, all your games, your own mistakes as puzzles, and your progress over time.</p><a class="btn solid" data-ev="analyze-cta-improve" href="/improve/?utm_source=analyze&amp;utm_campaign=improve">Join the waitlist</a></div>`;
  h += `<div class="az-cta"><h3>Keep improving</h3><p>This report is advice based on your own games. Next step: learn the 10 opening traps every beginner meets. Get the free cheat sheet, plus one trap a week in your inbox.</p><a class="btn solid" data-ev="analyze-cta-free" href="/free/?utm_source=analyze&amp;utm_campaign=analyze">Get the free cheat sheet</a><hr><h3>Learn one trap a day</h3><p>Under-a-minute lessons on traps, patterns and the mistakes we all make. Follow Throiy Chess:</p><div class="az-follow"><a class="btn" data-ev="analyze-follow-youtube" href="https://www.youtube.com/@ThroiyChess?sub_confirmation=1" target="_blank" rel="noopener">YouTube</a><a class="btn" data-ev="analyze-follow-instagram" href="https://www.instagram.com/throiychess" target="_blank" rel="noopener">Instagram</a><a class="btn" data-ev="analyze-follow-tiktok" href="https://www.tiktok.com/@throiychess" target="_blank" rel="noopener">TikTok</a></div></div>`;
  $("#az-report").innerHTML = h; $("#az-report").scrollIntoView({ behavior: "smooth" }); ev("analyze-report");
}

if (/[?&]bench=1/.test(location.search)) window.__az = { analyseGame };
