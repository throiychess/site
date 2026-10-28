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

// ---------- engine ----------
class Engine {
  constructor() { this.w = new Worker("/js/stockfish/stockfish-17.1-lite-single-03e3232.js"); this.q = Promise.resolve(); this.lis = null;
    this.w.onmessage = (e) => this.lis && this.lis(String(e.data)); }
  cmd(c) { this.w.postMessage(c); }
  wait(pred) { return new Promise((res) => { this.lis = (l) => { if (pred(l)) { this.lis = null; res(l); } }; }); }
  async init() { const p = this.wait((l) => l === "uciok"); this.cmd("uci"); await p; this.cmd("setoption name Hash value 32");
    const r = this.wait((l) => l === "readyok"); this.cmd("isready"); await r; }
  analyse(fen, depth = DEPTH) { // score from White's point of view, in pawns*100; mate as +-(10000 - n)
    return (this.q = this.q.then(() => new Promise((res) => { let score = 0, best = null; const white = fen.split(" ")[1] === "w";
      this.lis = (l) => { if (l.startsWith("info") && l.includes(" score ")) { const m = l.match(/score (cp|mate) (-?\d+)/);
          if (m) { let s = +m[2]; if (m[1] === "mate") s = s > 0 ? 10000 - s : -10000 - s; score = white ? s : -s; } }
        else if (l.startsWith("bestmove")) { best = l.split(" ")[1]; this.lis = null; res({ score, best: best === "(none)" ? null : best }); } };
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
  const moments = []; let lossSum = 0, nMoves = 0; const moved = {};
  for (let i = 0; i < hist.length; i++) {
    const h = hist[i]; if (side && h.color !== side) continue; const white = h.color === "w";
    const before = clip(pov(evals[i].score, white)), after = clip(pov(evals[i + 1].score, white)); const loss = Math.max(0, before - after);
    lossSum += Math.min(loss, 1000); nMoves++;
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
    moments.push({ ply, moveNo, color: h.color, san: h.san, best: bm ? bm.san : null, loss, cat, detail, fen: h.before, from: h.from, to: h.to,
      clock: g.tc === "daily" || g.tc === "correspondence" ? null : prevClock, before, after });
  }
  const res = side === "w" ? g.wres : g.bres;
  return { g, side, moments, avgLoss: nMoves ? lossSum / nMoves : 0, trap: side ? trapHit(sans, side) : null, result: res, plies: hist.length };
}

// ---------- drawing ----------
const GLYPH = { k: "♚", q: "♛", r: "♜", b: "♝", n: "♞", p: "♟" };
function boardSVG(fen, from, to, flip) {
  const rows = fen.split(" ")[0].split("/"); let s = `<svg viewBox="0 0 8 8" class="mini" role="img" aria-label="Board position">`;
  for (let r = 0; r < 8; r++) { let f = 0; for (const ch of rows[r]) { if (/\d/.test(ch)) { f += +ch; continue; }
      const x = flip ? 7 - f : f, y = flip ? 7 - r : r; s += `<text x="${x + 0.5}" y="${y + 0.82}" class="${ch === ch.toUpperCase() ? "pw" : "pb"}">${GLYPH[ch.toLowerCase()]}</text>`; f++; } }
  const sq = (n) => { const f = n.charCodeAt(0) - 97, r = 8 - +n[1]; return flip ? [7 - f, 7 - r] : [f, r]; };
  let bg = ""; for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) bg += `<rect x="${x}" y="${y}" width="1" height="1" class="${(x + y) % 2 ? "dk" : "lt"}"/>`;
  for (const n of [from, to]) { if (!n) continue; const [x, y] = sq(n); bg += `<rect x="${x}" y="${y}" width="1" height="1" class="hl"/>`; }
  return s.replace(`role="img" aria-label="Board position">`, `role="img" aria-label="Board position">${bg}`) + "</svg>";
}

// ---------- UI ----------
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

function report(results) {
  const all = results.flatMap((r) => r.moments.map((m) => ({ ...m, r }))); const cnt = {}; for (const m of all) cnt[m.cat] = (cnt[m.cat] || 0) + 1;
  const order = Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a]); const max = Math.max(1, ...Object.values(cnt));
  const late = all.filter((m) => m.clock !== null && m.clock < 30).length;
  let h = `<h2>Your report</h2><p>${results.length} game${results.length > 1 ? "s" : ""} analyzed for <b>${esc(state.user)}</b>. We found <b>${all.length}</b> moment${all.length === 1 ? "" : "s"} where the evaluation dropped by more than a pawn.</p>`;
  if (order.length) {
    const top = order[0];
    h += `<div class="az-top"><span class="eyebrow">Train this first</span><h3>${P[top].t}</h3><p>${P[top].tip}</p></div>`;
    h += `<div class="az-bars">` + order.map((c) => `<div class="az-bar"><span>${P[c].t}</span><i style="width:${(100 * cnt[c]) / max}%"></i><b>${cnt[c]}</b></div>`).join("") + `</div>`;
  } else h += `<div class="az-top"><h3>Clean games!</h3><p>No big drops in these games. Try a few losses to find what to train.</p></div>`;
  if (late) h += `<p class="small">⏱ ${late} of these moments came with less than 30 seconds on your clock. Part of the fix may be using your time earlier in the game.</p>`;
  for (const r of results) if (r.trap) h += `<div class="az-trap">${r.trap.fell ? "🪤 You fell for the" : "🎯 You set the"} <a href="/traps/${r.trap.t.slug}/?utm_source=analyze&amp;utm_campaign=${r.trap.t.slug}">${esc(r.trap.t.name)}</a>${r.trap.fell ? ". Here's how to avoid it next time." : ". Nice!"}</div>`;
  h += `<h2>Key moments</h2>`;
  for (const m of all.sort((a, b) => b.loss - a.loss).slice(0, 12)) {
    const opp = m.r.side === "w" ? m.r.g.black : m.r.g.white;
    h += `<div class="az-m">${boardSVG(m.fen, m.from, m.to, m.r.side === "b")}<div><span class="eyebrow">${P[m.cat].t}</span>
      <h3>Move ${m.moveNo}${m.color === "w" ? "." : "…"}${esc(m.san)} <span class="small">vs ${esc(opp)}</span></h3>
      <p>${m.detail ? esc(m.detail) + " " : ""}${m.best ? `Better was <b>${esc(m.best)}</b>.` : ""}</p>
      <p class="small">Evaluation for you: ${(m.before / 100).toFixed(1)} → ${(m.after / 100).toFixed(1)}${m.clock !== null ? ` · ${Math.round(m.clock)} s on your clock` : ""} · <a href="${esc(m.r.g.url)}" target="_blank" rel="noopener">open game</a></p>
      <p class="small"><b>Principle:</b> ${P[m.cat].tip}</p></div></div>`;
  }
  h += `<div class="az-cta"><h3>Want this every week?</h3><p>We're building a personal coach: weekly reports, puzzles from your own mistakes and progress over time. Join the list and get early access.</p><a class="btn solid" href="/free/?utm_source=analyze&amp;utm_campaign=analyze">Get early access + the free cheat sheet</a></div>`;
  $("#az-report").innerHTML = h; $("#az-report").scrollIntoView({ behavior: "smooth" }); ev("analyze-report");
}
