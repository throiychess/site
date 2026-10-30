// Members extras: goals (free), insights / weekly plan / puzzles from your own mistakes (premium). Runs after members.js says m-ready.
(function () {
  var $ = function (s) { return document.querySelector(s); };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var prem = function () { return window.__plan === "premium"; };
  var prof = null, rows = [], PZ = [], cur = null, selSq = null, sess = { n: 0, ok: 0 };
  var DAY = 864e5, BOX = [1, 3, 7, 14, 30], DAILY = 10, fOpen = null;
  var PRINC = {
    hang: ["Loose pieces drop off.", "Before you press the move, check every piece: is it attacked, is it defended enough? Do it for the piece you just moved first."],
    threat: ["Answer the threat before you start your plan.", "After every opponent move ask one question: what does that move want to do next?"],
    tactic: ["Look at checks, captures and threats, for both sides, every move.", "The strongest move is often forcing. If you skip the forcing moves you miss both your chances and their threats."],
    mate: ["Look at your king first.", "Before every move ask: what checks does my opponent have after this? Mates start with checks."],
    queen: ["Develop knights and bishops before the queen.", "An early queen gets chased and every chase gives your opponent a free developing move."],
    king: ["Castle early, keep the king at home.", "A king in the middle of the board becomes a target when the position opens."],
    twice: ["Every opening move should bring a new piece into play.", "Moving the same piece again before development is done gives your opponent time."],
    endgame: ["In the endgame the king is a fighting piece.", "Activate the king, push passed pawns and trade pieces, not pawns, when you are ahead."],
    other: ["Improve your worst piece.", "When there is no check, capture or threat, use the move to bring the piece that does the least into play."]
  };
  var NAME = function (k) { var P = (window.__azP || {}).P || {}; return P[k] ? P[k].t : k; };
  var lock = function (t) { return '<div class="mnext"><p>&#128274; ' + t + '</p><a class="btn solid" href="#plan">See Premium</a></div>'; };

  function load() {
    var sb = window.__sb; prof = window.__profile; if (!sb || !prof) return;
    sb.from("analyses").select("id,created_at,accuracy,avg_loss,blunders,games,band,top_leak,report").order("created_at", { ascending: false }).limit(30).then(function (r) {
      rows = r.data || []; buildPuz(); drawGoal(); drawIns(); drawPlan(); drawPuz(); drawShare(); drawPrinc(); drawOpen();
    });
  }
  window.addEventListener("m-ready", load); window.addEventListener("az-saved", function () { setTimeout(load, 600); });

  // ---------- goals (free) ----------
  var METRICS = { avg_loss: ["Pawns lost per move", true, 2], bl: ["Blunders per game", true, 1], accuracy: ["Accuracy", false, 0] };
  function val(row, m) { return m === "bl" ? Number(row.blunders) / Math.max(1, Number(row.games)) : Number(row[m]); }
  function drawGoal() {
    var box = $("#m-goal"); if (!box) return; var g = prof.goal;
    if (!rows.length) { box.innerHTML = "<h3>Your goal</h3><p class=\"small\">Run your first report, then set a goal and watch it move.</p>"; return; }
    if (g && METRICS[g.m]) {
      var mm = METRICS[g.m], now = val(rows[0], g.m), lo = mm[1], pr = lo ? (g.start - now) / (g.start - g.target) : (now - g.start) / (g.target - g.start), pc = Math.max(0, Math.min(100, Math.round(pr * 100))), done = lo ? now <= g.target : now >= g.target;
      box.innerHTML = "<h3>Your goal</h3><p><b>" + esc(mm[0]) + "</b>: " + g.start.toFixed(mm[2]) + " &rarr; <b>" + g.target.toFixed(mm[2]) + "</b> (now " + now.toFixed(mm[2]) + ")</p><div class=\"mbar\"><i style=\"width:" + pc + "%\"></i></div><p class=\"small\">" + (done ? "Goal reached. Set a new one." : pc + "% there. Run a fresh report after your next games.") + "</p><button class=\"btn\" type=\"button\" id=\"g-new\">Change goal</button>";
      $("#g-new").addEventListener("click", function () { prof.goal = null; drawGoal(); }); return;
    }
    box.innerHTML = "<h3>Set a goal</h3><p class=\"small\">Pick one thing to improve. We track it with every report you save.</p><div class=\"mform\" style=\"margin-top:10px\"><label class=\"sr\" for=\"g-m\">Metric</label><select id=\"g-m\"><option value=\"bl\">Fewer blunders per game</option><option value=\"avg_loss\">Fewer pawns lost per move</option><option value=\"accuracy\">Higher accuracy</option></select><label class=\"sr\" for=\"g-p\">Amount</label><select id=\"g-p\"><option value=\"10\">10% better</option><option value=\"20\" selected>20% better</option><option value=\"30\">30% better</option><option value=\"50\">50% better</option></select><button class=\"btn solid\" type=\"button\" id=\"g-set\">Set goal</button></div>";
    $("#g-set").addEventListener("click", function () {
      var m = $("#g-m").value, p = +$("#g-p").value / 100, s = val(rows[0], m), t = METRICS[m][1] ? s * (1 - p) : Math.min(99, s + (100 - s) * p * 0.5 + s * p * 0.1);
      var goal = { m: m, start: s, target: t, created: new Date().toISOString() };
      window.__sb.from("profiles").update({ goal: goal }).eq("id", prof.id).then(function (r) { if (!r.error) { prof.goal = goal; drawGoal(); } });
    });
  }

  // ---------- insights (premium) ----------
  function spark(v) { if (v.length < 2) return ""; var lo = Math.min.apply(0, v), hi = Math.max.apply(0, v), W = 90, H = 24; if (hi === lo) hi = lo + 1;
    return '<svg viewBox="0 0 ' + W + " " + H + '" class="mspark" aria-hidden="true"><polyline points="' + v.map(function (x, i) { return (i * (W - 4) / (v.length - 1) + 2).toFixed(1) + "," + (H - 3 - (x - lo) / (hi - lo) * (H - 6)).toFixed(1); }).join(" ") + '"/></svg>'; }
  function drawIns() {
    var box = $("#m-ins"); if (!box) return;
    if (!prem()) { box.innerHTML = lock("Premium adds trends per pattern, your openings, where in the game you lose points and how time pressure hurts you."); return; }
    var chron = rows.slice().reverse().filter(function (r) { return r.report && r.report.cats; });
    if (!chron.length) { box.innerHTML = "<h3>Insights</h3><p class=\"small\">Run a new report: from now on we save patterns, openings and time data, and this section fills up.</p>"; return; }
    var h = "<h3>Patterns over time</h3><div class=\"mtbl\">", all = {};
    chron.forEach(function (r) { Object.keys(r.report.cats).forEach(function (k) { all[k] = (all[k] || 0) + r.report.cats[k]; }); });
    Object.keys(all).sort(function (a, b) { return all[b] - all[a]; }).slice(0, 5).forEach(function (k) {
      var v = chron.map(function (r) { return (r.report.cats[k] || 0) / Math.max(1, r.games); }), a = v[0], z = v[v.length - 1];
      h += "<div class=\"m-row\"><span><b>" + esc(NAME(k)) + "</b></span>" + spark(v) + "<span class=\"small\">" + a.toFixed(1) + " &rarr; " + z.toFixed(1) + " per game " + (chron.length > 1 ? (z < a ? "<b class=\"up\">better</b>" : z > a ? "<b class=\"down\">worse</b>" : "") : "") + "</span></div>"; });
    h += "</div>";
    var op = {}; chron.forEach(function (r) { (r.report.openings || []).forEach(function (o) { var d = op[o.o] = op[o.o] || { g: 0, w: 0, l: 0, d: 0, b: 0 }; d.g++; d.b += o.b || 0; if (o.r === "Won") d.w++; else if (o.r === "Lost") d.l++; else d.d++; }); });
    var names = Object.keys(op).sort(function (a, b) { return op[b].g - op[a].g; }).slice(0, 6);
    if (names.length) { h += "<h3>Your openings</h3><div class=\"mtbl\">"; var worst = null; names.forEach(function (n) { if (op[n].g >= 2 && (!worst || op[n].b / op[n].g > op[worst].b / op[worst].g)) worst = n; });
      names.forEach(function (n) { var d = op[n]; h += "<div class=\"m-row\"><span><b>" + esc(n) + "</b>" + (n === worst && d.b ? " <span class=\"mbadge pro\" style=\"position:static\">Trouble spot</span>" : "") + "</span><span class=\"small\">" + d.g + " game" + (d.g > 1 ? "s" : "") + " &middot; " + d.w + "W " + d.d + "D " + d.l + "L</span><span class=\"small\">" + (d.b / d.g).toFixed(1) + " blunders/game</span></div>"; }); h += "</div>"; }
    var ph = { opening: [0, 0, 0], middlegame: [0, 0, 0], endgame: [0, 0, 0] }; chron.forEach(function (r) { var p = r.report.phases; if (p) Object.keys(ph).forEach(function (k) { if (p[k]) { ph[k][0] += p[k].n; ph[k][1] += p[k].loss; ph[k][2] += p[k].big; } }); });
    var pk = Object.keys(ph).filter(function (k) { return ph[k][0] > 0; });
    if (pk.length) { var lm = pk.map(function (k) { return ph[k][1] / ph[k][0] / 100; }), mx = Math.max.apply(0, lm), top = pk[lm.indexOf(mx)];
      h += "<h3>Where you lose points</h3><div class=\"az-bars\">" + pk.map(function (k, i) { return "<div class=\"az-bar\"><span>" + k[0].toUpperCase() + k.slice(1) + "</span><i style=\"width:" + (100 * lm[i] / mx) + "%\"></i><b>" + lm[i].toFixed(2) + "</b></div>"; }).join("") + "</div><p class=\"small\">Pawns lost per move in each phase. Most are lost in your <b>" + top + "</b>.</p>"; }
    var kn = 0, lw = 0; chron.forEach(function (r) { var t = r.report.lc; if (t) { kn += t.known; lw += t.low; } });
    if (kn >= 5) h += "<h3>Time pressure</h3><p><b>" + Math.round(100 * lw / kn) + "%</b> of your mistakes came with under 30 seconds on your clock (" + lw + " of " + kn + "). " + (lw / kn > 0.3 ? "Time is costing you games: play a little faster in the opening and keep a reserve for the middlegame." : "Your mistakes are mostly not about the clock: they come from the position.") + "</p>";
    box.innerHTML = h;
  }

  // ---------- openings (premium): what you play, where it goes wrong, train the positions ----------
  var TRAPS = []; try { TRAPS = JSON.parse(($("#trap-data") || {}).textContent || "[]"); } catch (e) {}
  function trapFor(name) { var n = name.toLowerCase().replace(/['\u2019]s?/g, ""); for (var i = 0; i < TRAPS.length; i++) { var w = TRAPS[i].name.toLowerCase().replace(/['\u2019]s?/g, "").split(" ")[0]; if (w.length > 4 && n.indexOf(w) > -1) return TRAPS[i]; } return null; }
  function drawOpen() {
    var box = $("#m-open"); if (!box) return;
    if (!prem()) { box.innerHTML = lock("Premium shows the openings you play, how they score, and trains the positions where you went wrong."); return; }
    var op = {}; rows.forEach(function (r) { ((r.report && r.report.openings) || []).forEach(function (o) { var d = op[o.o] = op[o.o] || { g: 0, w: 0, l: 0, d: 0, b: 0 }; d.g++; d.b += o.b || 0; if (o.r === "Won") d.w++; else if (o.r === "Lost") d.l++; else d.d++; }); });
    var names = Object.keys(op).sort(function (a, b) { return op[b].g - op[a].g; }).slice(0, 8);
    if (!names.length) { box.innerHTML = "<h3>Your openings</h3><p class=\"small\">Run a new report and your openings show up here, with a trainer for the positions you got wrong.</p>"; return; }
    box.innerHTML = "<h3>Your openings</h3><p class=\"small\">Learn the first 8 moves and the plan that follows. Start with the opening you play most.</p>" + names.map(function (n) { var d = op[n], k = PZ.filter(function (p) { return p.o === n && p.n <= 12; }).length, t = trapFor(n);
      return "<div class=\"mcard\" style=\"margin:10px 0\"><b>" + esc(n) + "</b><p class=\"small\" style=\"margin:4px 0\">" + d.g + " game" + (d.g > 1 ? "s" : "") + " &middot; " + d.w + "W " + d.d + "D " + d.l + "L &middot; " + (d.b / d.g).toFixed(1) + " blunders per game</p><p style=\"margin:6px 0 0\">" + (k ? "<button class=\"btn solid\" type=\"button\" data-open=\"" + esc(n) + "\">Train " + k + " opening position" + (k > 1 ? "s" : "") + " from your games</button> " : "<span class=\"small\">No costly opening mistakes saved for this one yet.</span> ") + (t ? "<a class=\"btn\" href=\"/traps/" + esc(t.slug) + "/\">Related trap: " + esc(t.name) + "</a>" : "") + "</p></div>"; }).join("");
  }
  function drawPrinc() {
    var box = $("#m-princ"); if (!box) return; var keys = Object.keys(PRINC);
    box.innerHTML = "<h3>Principles</h3><p class=\"small\">Short rules behind your reports. Each one links to a pattern we find in your games.</p>" + keys.map(function (k) { return "<div class=\"mplan\" style=\"cursor:default\"><span><b>" + esc(PRINC[k][0]) + "</b><br>" + esc(PRINC[k][1]) + "<br><span class=\"small\">Pattern: " + esc(NAME(k)) + " &middot; Source: Throiy Chess</span></span></div>"; }).join("");
  }

  // ---------- share card ----------
  function drawShare() {
    var box = $("#m-share"); if (!box) return; if (!rows.length) { box.innerHTML = ""; return; }
    var last = rows[0], first = rows[rows.length - 1], n = rows.length, acc = Number(last.accuracy), al = Number(last.avg_loss), bl = Number(last.blunders) / Math.max(1, Number(last.games)), d = n > 1 ? (al - Number(first.avg_loss)) / Number(first.avg_loss) : null;
    box.innerHTML = "<h3>Share your progress</h3><p class=\"small\">A card with your numbers. It shows no name or username.</p><canvas id=\"sh-cv\" width=\"1080\" height=\"1350\" style=\"width:100%;max-width:360px;border-radius:14px;border:1px solid var(--line)\"></canvas><p style=\"margin-top:10px\"><button class=\"btn solid\" type=\"button\" id=\"sh-dl\">Download image</button> <button class=\"btn\" type=\"button\" id=\"sh-share\" hidden>Share</button></p>";
    var c = $("#sh-cv").getContext("2d"), F = "Inter, system-ui, -apple-system, Segoe UI, sans-serif", gold = "#e3c073";
    var g = c.createLinearGradient(0, 0, 0, 1350); g.addColorStop(0, "#17140d"); g.addColorStop(1, "#0b0a08"); c.fillStyle = g; c.fillRect(0, 0, 1080, 1350);
    c.strokeStyle = "#4a3d1c"; c.lineWidth = 4; c.strokeRect(40, 40, 1000, 1270);
    c.fillStyle = gold; c.font = "800 44px " + F; c.fillText("THROIY CHESS", 90, 130); c.font = "600 30px " + F; c.fillStyle = "#a59a83"; c.fillText("My chess progress", 90, 180);
    c.fillStyle = "#efe8d8"; c.font = "800 190px " + F; var big = d === null ? al.toFixed(2) : (d <= 0 ? "\u2212" : "+") + Math.abs(Math.round(d * 100)) + "%"; c.fillText(big, 90, 470);
    c.font = "700 44px " + F; c.fillStyle = d !== null && d <= 0 ? "#7fd29b" : gold; c.fillText(d === null ? "pawns lost per move" : "pawns lost per move since my first report", 90, 540);
    var tiles = [[acc.toFixed(0) + "%", "accuracy"], [bl.toFixed(1), "blunders per game"], [String(n), n > 1 ? "reports" : "report"]];
    tiles.forEach(function (t, i) { var x = 90 + i * 315; c.fillStyle = "#1d1a13"; c.fillRect(x, 650, 290, 220); c.fillStyle = gold; c.font = "800 84px " + F; c.fillText(t[0], x + 24, 770); c.fillStyle = "#a59a83"; c.font = "600 28px " + F; c.fillText(t[1], x + 24, 825); });
    if (last.band) { c.fillStyle = "#efe8d8"; c.font = "700 40px " + F; c.fillText("My play looks like: " + String(last.band).slice(0, 14), 90, 960); }
    c.fillStyle = "#a59a83"; c.font = "600 34px " + F; c.fillText("Analyzed in my own browser with Stockfish.", 90, 1040);
    c.fillStyle = gold; c.fillRect(90, 1150, 900, 110); c.fillStyle = "#14110b"; c.font = "800 40px " + F; c.fillText("Analyze your games free: throiychess.com", 120, 1218);
    if (navigator.canShare && navigator.share) $("#sh-share").hidden = false;
  }
  function shareNative() { var cv = $("#sh-cv"); if (!cv) return; cv.toBlob(function (b) { try { var f = new File([b], "throiy-chess-progress.png", { type: "image/png" }); if (navigator.canShare && navigator.canShare({ files: [f] })) navigator.share({ files: [f], title: "My chess progress", text: "Analyze your games free: throiychess.com" }).catch(function () {}); } catch (e) {} }); }

  // ---------- weekly plan ----------
  function wk() { var d = new Date(), j = new Date(d.getFullYear(), 0, 1); return d.getFullYear() + "-" + Math.ceil(((d - j) / DAY + j.getDay() + 1) / 7); }
  function drawPlan() {
    var box = $("#m-plan"); if (!box) return;
    if (!prem()) { box.innerHTML = lock("Premium gives you a weekly plan: your top 3 leaks, one exercise each, checked off as you go."); return; }
    var c = {}, any = false; rows.slice(0, 3).forEach(function (r) { var k = r.report && r.report.cats; if (k) { any = true; Object.keys(k).forEach(function (x) { c[x] = (c[x] || 0) + k[x]; }); } });
    if (!any) { box.innerHTML = "<h3>Your plan this week</h3><p class=\"small\">Run a new report and your plan appears here.</p>"; return; }
    var top = Object.keys(c).sort(function (a, b) { return c[b] - c[a]; }).slice(0, 3), D = (window.__azP || {}).DRILL || {}, key = "tc_plan_" + wk(), done = {};
    try { done = JSON.parse(localStorage.getItem(key) || "{}"); } catch (e) {}
    box.innerHTML = "<h3>Your plan this week</h3><p class=\"small\">Based on your last reports. Tick each one when you did it.</p>" + top.map(function (k, i) { var d = D[k] || ["", ""]; return "<label class=\"mplan\"><input type=\"checkbox\" data-k=\"" + esc(k) + "\"" + (done[k] ? " checked" : "") + "><span><b>" + (i + 1) + ". " + esc(NAME(k)) + "</b><br>" + esc(d[0]) + "<br><span class=\"small\">" + esc(d[1]) + "</span>" + (PRINC[k] ? "<br><span class=\"small\"><b>Principle:</b> " + esc(PRINC[k][0]) + "</span>" : "") + "</span></label>"; }).join("") + "<p class=\"small\">Next week, run a new report to see if the numbers moved.</p>";
    box.onchange = function (e) { var t = e.target; if (t.dataset && t.dataset.k) { done[t.dataset.k] = t.checked; try { localStorage.setItem(key, JSON.stringify(done)); } catch (x) {} } };
  }

  // ---------- puzzles from own mistakes ----------
  function buildPuz() { var seen = {}; PZ = []; rows.forEach(function (r) { ((r.report && r.report.puz) || []).forEach(function (p) { var k = p.f.split(" ").slice(0, 4).join(" ") + p.bf + p.bt; if (!seen[k]) { seen[k] = 1; p.key = k; PZ.push(p); } }); }); }
  function stateOf(p) { return ((prof.puz || {})[p.key]) || { b: 0, d: 0 }; }
  function daily(inc) { var k = "tc_daily", d = new Date().toISOString().slice(0, 10), o = {}; try { o = JSON.parse(localStorage.getItem(k) || "{}"); } catch (e) {} if (o.d !== d) o = { d: d, n: 0 }; if (inc) { o.n += inc; try { localStorage.setItem(k, JSON.stringify(o)); } catch (e) {} } return o.n; }
  function pool() { return fOpen ? PZ.filter(function (p) { return p.o === fOpen && p.n <= 12; }) : PZ; }
  function nextP() { var now = Date.now(), due = pool().filter(function (p) { return stateOf(p).d <= now; }); if (!due.length) return null; due.sort(function (a, b) { return stateOf(a).b - stateOf(b).b || b.l - a.l; }); return due[0]; }
  function pieceAt(fen, sq) { var rows8 = fen.split(" ")[0].split("/"), f = sq.charCodeAt(0) - 97, r = 8 - +sq[1], x = 0; for (var i = 0; i < rows8[r].length; i++) { var ch = rows8[r][i]; if (/\d/.test(ch)) { x += +ch; continue; } if (x === f) return ch; x++; } return null; }
  function board(p, sel, reveal) {
    var flip = p.c === "b", svg = window.__azBoard(p.f, sel, null, flip, reveal ? p.bf : null, reveal ? p.bt : null), ov = "";
    for (var y = 0; y < 8; y++) for (var x = 0; x < 8; x++) { var f = flip ? 7 - x : x, rk = flip ? y + 1 : 8 - y; ov += '<rect x="' + x + '" y="' + y + '" width="1" height="1" fill="transparent" data-sq="' + String.fromCharCode(97 + f) + rk + '" style="cursor:pointer"/>'; }
    return svg.replace("</svg>", ov + "</svg>");
  }
  function drawPuz() {
    var box = $("#m-puz"); if (!box) return; var st = $("#m-puz-static");
    if (!prem()) { if (st) st.hidden = false; box.innerHTML = lock(PZ.length ? "You already have <b>" + PZ.length + " puzzle" + (PZ.length > 1 ? "s" : "") + "</b> waiting from your own games. Premium unlocks them." : "Premium turns the mistakes in your reports into puzzles you train until you get them right."); return; }
    if (st) st.hidden = true;
    if (!PZ.length) { box.innerHTML = "<p>No puzzles yet. Analyze a few of your games (use Premium to analyze up to 25) and every costly mistake becomes a puzzle here.</p><a class=\"btn solid\" href=\"#analyze\">Analyze my games</a>"; return; }
    cur = nextP(); selSq = null;
    if (!cur && fOpen && !pool().length) { box.innerHTML = "<p class=\"small\"><button class=\"btn\" type=\"button\" data-clear=\"1\">Show all puzzles</button></p><p>No saved positions for this opening yet.</p>"; return; }
    if (!cur) { var nxt = Math.min.apply(0, pool().concat(PZ.length ? [] : []).map(function (p) { return stateOf(p).d; })), dd = Math.max(1, Math.ceil((nxt - Date.now()) / DAY)); box.innerHTML = (fOpen ? "<p class=\"small\"><button class=\"btn\" type=\"button\" data-clear=\"1\">Show all puzzles</button></p>" : "") + "<div class=\"mnext\"><p><b>All caught up.</b> " + pool().length + " puzzles done for now. The next one is due in " + dd + " day" + (dd > 1 ? "s" : "") + ". Run a new report for new puzzles.</p><a class=\"btn solid\" href=\"#analyze\">Analyze new games</a></div>"; return; }
    var left = pool().filter(function (p) { return stateOf(p).d <= Date.now(); }).length, dn = daily(0);
    box.innerHTML = (fOpen ? "<p class=\"small\">Opening trainer: <b>" + esc(fOpen) + "</b> <button class=\"btn\" type=\"button\" data-clear=\"1\">Show all puzzles</button></p>" : "") + "<div class=\"mbar\"><i style=\"width:" + Math.min(100, dn * 100 / DAILY) + "%\"></i></div><p class=\"small\">Today's set: " + Math.min(dn, DAILY) + " of " + DAILY + (dn >= DAILY ? " &middot; <b class=\"up\">done, great work</b>. Keep going if you like." : "") + " &middot; " + left + " due &middot; this session " + sess.ok + "/" + sess.n + "</p><p><b>" + (cur.c === "w" ? "White" : "Black") + " to move.</b> This is from your own game, move " + cur.n + ". Find the best move: tap the piece, then the square.</p><div class=\"mpz\" id=\"pz-b\">" + board(cur, null, false) + "</div><p id=\"pz-msg\" role=\"status\" aria-live=\"polite\"></p>";
  }
  function answer(ok) {
    var s = stateOf(cur), b = ok ? Math.min(BOX.length - 1, s.b + 1) : 0, d = Date.now() + (ok ? BOX[b] : 0.2) * DAY, puz = Object.assign({}, prof.puz || {}); puz[cur.key] = { b: b, d: d }; prof.puz = puz; sess.n++; if (ok) sess.ok++; daily(1);
    window.__sb.from("profiles").update({ puz: puz }).eq("id", prof.id);
  }
  document.addEventListener("click", function (e) {
    var t = e.target, sq = t.getAttribute && t.getAttribute("data-sq"), pb = $("#pz-b");
    if (t.id === "pz-next") { drawPuz(); return; }
    var op = t.closest && t.closest("[data-open]"); if (op) { fOpen = op.dataset.open; location.hash = "#puzzles"; drawPuz(); return; }
    if (t.closest && t.closest("[data-clear]")) { fOpen = null; drawPuz(); return; }
    if (t.id === "sh-dl") { var cv = $("#sh-cv"); if (cv) { var a = document.createElement("a"); a.download = "throiy-chess-progress.png"; a.href = cv.toDataURL("image/png"); a.click(); } return; }
    if (t.id === "sh-share") { shareNative(); return; }
    if (!sq || !cur || !pb || !pb.contains(t) || pb.dataset.done) return;
    var pc = pieceAt(cur.f, sq), mine = pc && (cur.c === "w" ? pc === pc.toUpperCase() : pc === pc.toLowerCase());
    if (!selSq || mine) { if (!mine) return; selSq = sq; pb.innerHTML = board(cur, sq, false); return; }
    var ok = selSq === cur.bf && sq === cur.bt; pb.dataset.done = "1"; answer(ok);
    pb.innerHTML = board(cur, null, true);
    $("#pz-msg").innerHTML = (ok ? "<b class=\"up\">Correct.</b> " : "<b class=\"down\">Not this one.</b> ") + "The best move was <b>" + esc(cur.b) + "</b>. In your game you played " + esc(cur.s) + ".<br><button class=\"btn solid\" type=\"button\" id=\"pz-next\" style=\"margin-top:10px\">Next puzzle</button>";
  });
})();
