/* Daily Trap (/today/). Data: /js/daily-data.json (built from _builder/daily_data.json, every move checked with Stockfish 17.1).
   Config: window.DT = {start:"YYYY-MM-DD", order:[slugs], schedule:{"YYYY-MM-DD":slug}}. State: localStorage "tc_daily". */
(function () {
  var C = window.DT, root = document.getElementById("dt"); if (!C || !root) return;
  var $ = function (id) { return document.getElementById(id); };
  function ev(n) { try { if (window.gcEv) gcEv(n); } catch (e) {} }
  function iso(d) { return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); }
  function dayNum() { var s = C.start.split("-"), a = new Date(+s[0], s[1] - 1, +s[2]), n = new Date(); n = new Date(n.getFullYear(), n.getMonth(), n.getDate()); return Math.round((n - a) / 864e5) + 1; }
  function load() { try { return JSON.parse(localStorage.getItem("tc_daily")) || {}; } catch (e) { return {}; } }
  function save(s) { try { localStorage.setItem("tc_daily", JSON.stringify(s)); } catch (e) {} }
  var q = new URLSearchParams(location.search), N = dayNum(), P, practice = false, tries = 0, lost = 0, done = false, sel = null, busy = false, cur, lastMv = "";
  var B = $("dtb"), sqs = {}, PZ = null, started = 0, hl = 0, justDragged = 0, drag = null;

  function buildBoard(flip) {
    B.innerHTML = ""; sqs = {};
    for (var i = 0; i < 64; i++) {
      var r = flip ? Math.floor(i / 8) : 7 - Math.floor(i / 8), f = flip ? 7 - (i % 8) : i % 8, n = "abcdefgh"[f] + (r + 1);
      var d = document.createElement("div"); d.className = "sq " + ((r + f) % 2 ? "l" : "d"); d.dataset.n = n;
      if (i % 8 === 0) { var c = document.createElement("span"); c.className = "co rk"; c.textContent = r + 1; d.appendChild(c); }
      if (i >= 56) { var c2 = document.createElement("span"); c2.className = "co fl"; c2.textContent = "abcdefgh"[f]; d.appendChild(c2); }
      B.appendChild(d); sqs[n] = d;
    }
  }
  function parse(fen) { var m = {}; fen.split("/").forEach(function (row, i) { var f = 0; for (var k = 0; k < row.length; k++) { var ch = row[k]; if (/\d/.test(ch)) f += +ch; else { m["abcdefgh"[f] + (8 - i)] = ch; f++; } } }); return m; }
  function draw(fen, uci) {
    cur = parse(fen); lastMv = uci || "";
    Object.keys(sqs).forEach(function (n) {
      var d = sqs[n], old = d.querySelector("img"); if (old) old.remove();
      d.classList.remove("sel", "tg", "hint", "dsrc"); d.classList.toggle("hl", !!uci && (uci.slice(0, 2) === n || uci.slice(2, 4) === n));
      var c = cur[n]; if (c) { var im = document.createElement("img"); im.alt = ""; im.draggable = false; im.src = "/img/pieces/" + (c === c.toUpperCase() ? "w" : "b") + c.toLowerCase() + ".png"; d.appendChild(im); }
    });
  }
  function mine(n) { var c = cur[n]; return c && ((c === c.toUpperCase()) === (P.victim === "w")); }
  function movesFrom(n) {
    if (PZ) return PZ.g.moves({ square: n, verbose: true }).map(function (m) { return { u: m.from + m.to + (m.promotion || "") }; });
    return P.moves.filter(function (m) { return m.u.slice(0, 2) === n; });
  }
  function clearSel() { Object.keys(sqs).forEach(function (n) { sqs[n].classList.remove("sel", "tg"); }); sel = null; }

  function doMove(n) {
    var c = movesFrom(sel).filter(function (m) { return m.u.slice(2, 4) === n; });
    var mv = c.filter(function (m) { return m.u.length === 4 || m.u[4] === "q"; })[0] || c[0]; clearSel(); if (mv) { if (PZ) pzPlay(mv.u); else play(mv); }
  }
  B.addEventListener("click", function (e) {
    if (justDragged) return;
    if (done || busy) return; var d = e.target.closest(".sq"); if (!d) return; var n = d.dataset.n;
    if (sel && d.classList.contains("tg")) { doMove(n); return; }
    clearSel();
    if (mine(n) && movesFrom(n).length) { sel = n; d.classList.add("sel"); movesFrom(n).forEach(function (m) { sqs[m.u.slice(2, 4)].classList.add("tg"); }); }
  });
  /* drag and drop (mouse and finger); tap-tap keeps working */
  B.addEventListener("pointerdown", function (e) {
    if (done || busy || (e.pointerType === "mouse" && e.button !== 0)) return; var d = e.target.closest(".sq"); if (!d) return; var n = d.dataset.n;
    if (!(mine(n) && movesFrom(n).length)) return;
    drag = { n: n, x: e.clientX, y: e.clientY, on: false, g: null };
  });
  document.addEventListener("pointermove", function (e) {
    if (!drag) return;
    if (!drag.on) {
      if (Math.abs(e.clientX - drag.x) + Math.abs(e.clientY - drag.y) < 8) return;
      drag.on = true; clearSel(); sel = drag.n; var src = sqs[drag.n]; src.classList.add("sel", "dsrc"); movesFrom(drag.n).forEach(function (m) { sqs[m.u.slice(2, 4)].classList.add("tg"); });
      var im = src.querySelector("img"), g = document.createElement("img"), w = src.getBoundingClientRect().width * 1.15;
      g.src = im ? im.src : ""; g.alt = ""; g.className = "dtghost"; g.style.width = w + "px"; g.style.height = w + "px"; document.body.appendChild(g); drag.g = g;
    }
    drag.g.style.left = e.clientX + "px"; drag.g.style.top = e.clientY + "px"; e.preventDefault();
  }, { passive: false });
  function endDrag(e, cancel) {
    if (!drag) return; var D = drag; drag = null; if (!D.on) return;
    if (D.g) D.g.remove(); justDragged = 1; setTimeout(function () { justDragged = 0; }, 60);
    var el = cancel ? null : document.elementFromPoint(e.clientX, e.clientY), d = el && el.closest ? el.closest(".sq") : null;
    if (d && B.contains(d) && d.classList.contains("tg")) doMove(d.dataset.n); else clearSel();
    Object.keys(sqs).forEach(function (k) { sqs[k].classList.remove("dsrc"); });
  }
  document.addEventListener("pointerup", function (e) { endDrag(e, false); });
  document.addEventListener("pointercancel", function (e) { endDrag(e, true); });

  /* goal banner above the board, hearts, hint */
  function goal(title, side, step) {
    $("dth").textContent = title; PZT = title;
    $("dtg").innerHTML = '<strong>' + esc(title) + '</strong><span class="sd ' + side + '" aria-hidden="true"></span><span>' + (side === "w" ? "White" : "Black") + ' to move</span>' + (step ? '<span class="pr">' + esc(step) + '</span>' : "");
  }
  var PZT = "";
  function hintMove() {
    if (PZ) {
      var G = PZ.g, p = PZ.p;
      if (PZ.step === 0) return p.line[0].slice(0, 4);
      var ms = G.moves({ verbose: true }).filter(function (m) { return pzMates(G, m.from + m.to + (m.promotion || "")); });
      return ms.length ? ms[0].from + ms[0].to : p.line[2].slice(0, 4);
    }
    var g = P.moves.filter(function (m) { return m.v === "good"; }), m = g.filter(function (m) { return m.s === P.best; })[0] || g[0] || P.moves.filter(function (m) { return m.v === "ok"; })[0];
    return m && m.u.slice(0, 4);
  }
  function showHint() {
    Object.keys(sqs).forEach(function (k) { sqs[k].classList.remove("hint"); });
    if (!hl || done) return; var u = hintMove(); if (!u) return;
    sqs[u.slice(0, 2)].classList.add("hint"); if (hl > 1) sqs[u.slice(2, 4)].classList.add("hint");
  }
  function updHint() {
    var b = $("dthint"); if (!b) return;
    if (done) { b.hidden = true; return; }
    b.hidden = false; b.disabled = lost >= 2 || hl >= 2;
    b.textContent = hl >= 2 ? "\uD83D\uDCA1 Hint used" : lost >= 2 ? "No hint on your last heart" : hl === 1 ? "\uD83D\uDCA1 Show where (-1 \u2665)" : "\uD83D\uDCA1 Hint (-1 \u2665)";
  }
  function begin() { if (started) return; started = 1; ev((PZ ? "daily-puzzle-start" : "daily-start") + (practice ? "-practice" : "")); }
  $("dthint").onclick = function () {
    if (done || busy || lost >= 2 || hl >= 2) return; if (!hintMove()) return;
    begin(); hl++; clearSel();
    if (PZ) lost++; else { tries++; lost = tries; }
    pips(); showHint(); updHint(); ev("daily-hint-" + hl);
    msg("", hl === 1 ? "Hint: move the blue piece." : "Hint: it goes to the blue square.", "Hints cost a heart.");
  };

  function msg(kind, head, text) { var m = $("dtm"); m.className = "dtmsg " + kind; m.innerHTML = "<b>" + head + "</b>" + (text ? "<span>" + text + "</span>" : ""); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function pips() { var h = ""; for (var i = 1; i <= 3; i++) h += '<b class="' + (i <= lost ? "u" : "") + '" aria-hidden="true">&#9829;</b>'; var left = 3 - lost; $("dtt").setAttribute("aria-label", left + " of 3 hearts left"); $("dtt").innerHTML = h + "<span>" + (left === 1 ? "Last heart" : left + " hearts left") + "</span>"; updHint(); }
  function hearts(n) { var h = ""; for (var i = 0; i < 3; i++) h += i < n ? "\u2764\uFE0F" : "\uD83D\uDDA4"; return h; }
  function again() { busy = false; draw(P.fen, P.last); pips(); showHint(); msg("", "Your move.", "Tap or drag a piece."); $("dta").hidden = true; }

  function play(mv) {
    busy = true; tries++; pips(); draw(mv.f, mv.u); begin();
    if (mv.v === "good" || mv.v === "ok") {
      setTimeout(function () { finish(true, mv); }, 500);
    } else if (mv.v === "bait") {
      lost = tries; pips(); msg("bad", "You took the bait. You lose a heart.", "Watch what happens.");
      var i = 1; (function step() { if (i < P.line.length) { draw(P.line[i].f, P.line[i].u); i++; setTimeout(step, 950); } else setTimeout(function () { miss("That is the " + esc(P.name) + ".", P.mate ? "It ends in checkmate." : "It costs you material."); }, 500); })();
    } else {
      lost = tries; pips(); setTimeout(function () { if (mv.rf) draw(mv.rf, mv.ru); miss("Not the trap, but there is a much better move.", mv.rs ? "Your opponent answers " + esc(mv.rs) + "." : ""); }, 650);
    }
  }
  function miss(head, text) {
    if (lost >= 3) { finish(false); return; }
    msg("bad", head, text); busy = true; $("dta").hidden = false;
  }
  function finish(win, mv) {
    done = true; busy = false; $("dta").hidden = true;
    var s = load();
    if (!practice) {
      s.res = s.res || {};
      if (!s.res[N]) {
        s.streak = (s.last === N - 1 ? (s.streak || 0) + 1 : 1); s.last = N; s.best = Math.max(s.best || 0, s.streak);
        s.res[N] = { t: tries, w: win ? 1 : 0, s: P.slug }; var ks = Object.keys(s.res); if (ks.length > 60) delete s.res[ks[0]];
        save(s); ev(win ? "daily-win-" + tries : "daily-fail");
      }
    } else ev(win ? "daily-practice-win" : "daily-practice-fail");
    result(win, mv, s);
  }
  function result(win, mv, s) {
    var r = (s.res && s.res[N]) || { t: tries, w: win ? 1 : 0 };
    if (!win) draw(P.fen, P.last); updHint();
    var head = win ? "You survived the " + esc(P.name) + "." : "The " + esc(P.name) + " got you this time.";
    var sub = win ? (mv && mv.s !== P.best ? (mv.v === "ok" ? "Your move " + esc(mv.s) + " holds, but " + esc(P.best) + " is stronger." : "Your move " + esc(mv.s) + " works. A better move is " + esc(P.best) + ".") : "You found the best move: " + esc(P.best) + ".")
      : "A safe move was " + esc(P.best) + ".";
    msg(win ? "good" : "bad", head, sub);
    var fx = P.fix.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("");
    var st = practice ? "" : '<div class="dtstat"><div><b>#' + N + '</b><span>Daily Trap</span></div><div><b>' + (r.w ? (4 - r.t) + "/3" : "0/3") + '</b><span>hearts left</span></div><div><b>' + (s.streak || 1) + '</b><span>day streak</span></div><div><b>' + (s.best || 1) + '</b><span>best streak</span></div></div>';
    var sh = P.short ? '<button type="button" class="btn" data-yt="' + esc(P.short) + '" data-title="' + esc(P.name) + '">Watch the 1-minute lesson</button>' : "";
    $("dtr").innerHTML = st + '<h2>How not to fall for it</h2><ol class="fix">' + fx.replace(/<li>/g, "<li><span>").replace(/<\/li>/g, "</span></li>") + "</ol>"
      + '<div class="btns">' + (practice ? "" : '<button type="button" class="btn solid" id="dtsh">Share my result</button>')
      + '<a class="btn' + (practice ? " solid" : "") + '" href="/traps/' + P.slug + '/" data-ev="daily-trap-page">Step through the whole trap</a>' + sh + "</div>"
      + '<p class="small" id="dtshm" role="status" aria-live="polite"></p>'
      + (practice ? '<p><a class="go" href="/today/">Play today\'s Daily Trap &rarr;</a></p>' : '<p class="dtnext">A new trap every day. <span id="dtcd"></span></p>')
      + '<div class="card" style="margin-top:18px"><span class="label">Your own games</span><h3>Which traps do you fall for?</h3><p>Enter your Chess.com or Lichess name and see where your games go wrong. Free, runs in your browser.</p><a class="go" href="/analyze/?utm_source=site&amp;utm_campaign=daily" data-ev="daily-analyze">Analyze my games free &rarr;</a></div>';
    $("dtr").hidden = false;
    var b = $("dtsh"); if (b) b.onclick = function () {
      var t = "ThroiyChess Daily Trap #" + N + "\n" + (r.w ? "Survived " + hearts(4 - r.t) : "It got me " + hearts(0)) + " · 🔥 " + (s.streak || 1) + "-day streak\nCan you survive it?", u = "https://throiychess.com/today/";
      ev("daily-share");
      if (navigator.share && matchMedia("(pointer:coarse)").matches) { navigator.share({ text: t, url: u }).catch(function () {}); return; }
      (navigator.clipboard ? navigator.clipboard.writeText(t + "\n" + u) : Promise.reject()).then(function () { $("dtshm").textContent = "Copied. Paste it in a chat or a story."; }).catch(function () { prompt("Copy your result:", t + " " + u); });
    };
    var cd = $("dtcd"); if (cd) { var n = new Date(), m = new Date(n.getFullYear(), n.getMonth(), n.getDate() + 1), mins = Math.round((m - n) / 6e4); cd.textContent = "Next one in " + Math.floor(mins / 60) + " h " + (mins % 60) + " min."; }
    try { $("dtr").scrollIntoView({ behavior: "smooth", block: "nearest" }); } catch (e) {}
  }

  /* ---------- Daily Puzzle (Lichess puzzle database, CC0). Needs /js/chess.js for legal moves. ---------- */
  var LESSON = {
    mateIn2: "Checkmate in two: find a move that leaves the king no way out, whatever it answers. Before you move, list every check you have.",
    backRankMate: "The king on the back rank is boxed in by its own pawns. One rook or queen check can end the game. Check your own back rank too.",
    fork: "A fork is one piece attacking two things at once. Your opponent can only save one.",
    pin: "A pin freezes a piece, because moving it would expose something more valuable behind it. Look for pieces that cannot move.",
    hangingPiece: "A hanging piece has no protection. Before every move, ask yourself: what is not defended?",
    discoveredAttack: "Move one piece and the piece behind it suddenly attacks. You make two threats with one move.",
    trappedPiece: "A trapped piece has no safe square left. Attack it and it cannot escape.",
    skewer: "A skewer attacks a valuable piece. When it moves away, you win the piece behind it.",
    opening: "Early in the game, tactics decide a lot. Look for checks, captures and threats before your opponent has finished developing."
  };
  function fb(f) { return f.split(" ")[0]; }
  function daysBetween(a, b) { var x = a.split("-"), y = b.split("-"); return Math.round((new Date(+y[0], y[1] - 1, +y[2]) - new Date(+x[0], x[1] - 1, +x[2])) / 864e5); }
  function pzMates(g, u) { var t = new PZ.C(g.fen()); try { t.move({ from: u.slice(0, 2), to: u.slice(2, 4), promotion: u[4] || "q" }); } catch (e) { return false; } return t.isCheckmate(); }
  function startPuzzle(p, Chess) {
    P = { victim: p.side, slug: "pz-" + p.id }; PZ = { p: p, C: Chess, g: new Chess(p.fen), step: 0, last: p.last };
    var mate = p.theme === "mateIn2", title = mate ? "Checkmate in 2" : "Find the best move"; PZ.title = title;
    $("dte").textContent = practice ? "Practice puzzle" : "Daily Puzzle #" + N;
    $("dtp").innerHTML = "Your opponent just played <b>" + esc(p.lastsan) + "</b>.";
    buildBoard(p.side === "b"); draw(fb(p.fen), p.last); goal(title, p.side, "Move 1 of 2"); pips(); msg("", title + ": your move.", "Tap or drag a piece. Move 1 of 2.");
  }
  function pzWrong() {
    lost++; pips(); var G = PZ.g;
    if (lost >= 3) { setTimeout(function () { pzFinish(false); }, 500); return; }
    msg("bad", "Not that one. You lose a heart.", "Look for a stronger move. Checks and captures first.");
    setTimeout(function () { draw(fb(G.fen()), PZ.last); busy = false; showHint(); }, 800);
  }
  function pzPlay(u) {
    busy = true; begin();
    var G = PZ.g, p = PZ.p, u4 = u.slice(0, 4), ok;
    if (PZ.step === 0) ok = p.ok1[u] !== undefined || p.ok1[u4] !== undefined || pzMates(G, u); else ok = u4 === p.line[2] || pzMates(G, u);
    if (!ok) { var T = new PZ.C(G.fen()); try { T.move({ from: u.slice(0, 2), to: u.slice(2, 4), promotion: u[4] || "q" }); draw(fb(T.fen()), u4); } catch (e) {} pzWrong(); return; }
    var rep = PZ.step === 0 ? (p.ok1[u] !== undefined ? p.ok1[u] : p.ok1[u4]) : null;
    G.move({ from: u.slice(0, 2), to: u.slice(2, 4), promotion: u[4] || "q" }); PZ.last = u4; draw(fb(G.fen()), u4);
    if (G.isCheckmate() || PZ.step === 1 || !rep) { setTimeout(function () { pzFinish(true); }, 500); return; }
    msg("good", "Good move! Move 1 of 2 done.", "Your opponent answers. Now find move 2."); hl = 0; updHint(); goal(PZ.title, p.side, "Move 2 of 2");
    setTimeout(function () { G.move({ from: rep.slice(0, 2), to: rep.slice(2, 4), promotion: rep[4] || "q" }); PZ.last = rep.slice(0, 4); draw(fb(G.fen()), PZ.last); PZ.step = 1; busy = false; msg("", PZ.title + ": your move.", "Find move 2 of 2."); }, 750);
  }
  function pzFinish(win) {
    done = true; busy = false; tries = win ? lost + 1 : 3; var s = load();
    if (!practice) {
      s.res = s.res || {};
      if (!s.res[N]) {
        s.streak = (s.last === N - 1 ? (s.streak || 0) + 1 : 1); s.last = N; s.best = Math.max(s.best || 0, s.streak);
        s.res[N] = { t: tries, w: win ? 1 : 0, s: P.slug, k: "p" }; var ks = Object.keys(s.res); if (ks.length > 60) delete s.res[ks[0]];
        save(s); ev(win ? "daily-puzzle-win-" + tries : "daily-puzzle-fail");
      }
    } else ev(win ? "daily-puzzle-practice-win" : "daily-puzzle-practice-fail");
    pzResult(win, s);
  }
  function pzResult(win, s) {
    var p = PZ.p, r = (s.res && s.res[N]) || { t: tries, w: win ? 1 : 0 };
    if (!win) draw(fb(p.fen), p.last); updHint();
    var line = p.sans.join(", ");
    msg(win ? "good" : "bad", win ? "Solved!" : "Not this time.", (win ? "The main line is " : "The solution was ") + esc(line) + ".");
    var st = practice ? "" : '<div class="dtstat"><div><b>#' + N + '</b><span>Daily Puzzle</span></div><div><b>' + (r.w ? (4 - r.t) + "/3" : "0/3") + '</b><span>hearts left</span></div><div><b>' + (s.streak || 1) + '</b><span>day streak</span></div><div><b>' + (s.best || 1) + '</b><span>best streak</span></div></div>';
    $("dtr").innerHTML = st + '<h2>What to remember</h2><ol class="fix"><li><span>' + esc(LESSON[p.theme] || LESSON.opening) + '</span></li></ol>'
      + '<div class="btns">' + (practice ? "" : '<button type="button" class="btn solid" id="dtsh">Share my result</button>') + '<a class="btn' + (practice ? " solid" : "") + '" href="/traps/" data-ev="daily-puzzle-traps">Step through the traps</a></div>'
      + '<p class="small" id="dtshm" role="status" aria-live="polite"></p>'
      + (practice ? '<p><a class="go" href="/today/">Play today\'s Daily &rarr;</a></p>' : '<p class="dtnext">A new one every day. <span id="dtcd"></span></p>')
      + '<div class="card" style="margin-top:18px"><span class="label">Your own games</span><h3>Where do your games go wrong?</h3><p>Enter your Chess.com or Lichess name and see your biggest leaks. Free, runs in your browser.</p><a class="go" href="/analyze/?utm_source=site&amp;utm_campaign=daily" data-ev="daily-analyze">Analyze my games free &rarr;</a></div>';
    $("dtr").hidden = false;
    var b = $("dtsh"); if (b) b.onclick = function () {
      var t = "ThroiyChess Daily Puzzle #" + N + "\n" + (r.w ? "Solved " + hearts(4 - r.t) : "Not this time " + hearts(0)) + " \u00b7 \uD83D\uDD25 " + (s.streak || 1) + "-day streak\nCan you solve it?", u = "https://throiychess.com/today/";
      ev("daily-puzzle-share");
      if (navigator.share && matchMedia("(pointer:coarse)").matches) { navigator.share({ text: t, url: u }).catch(function () {}); return; }
      (navigator.clipboard ? navigator.clipboard.writeText(t + "\n" + u) : Promise.reject()).then(function () { $("dtshm").textContent = "Copied. Paste it in a chat or a story."; }).catch(function () { prompt("Copy your result:", t + " " + u); });
    };
    var cd = $("dtcd"); if (cd) { var n = new Date(), m = new Date(n.getFullYear(), n.getMonth(), n.getDate() + 1), mins = Math.round((m - n) / 6e4); cd.textContent = "Next one in " + Math.floor(mins / 60) + " h " + (mins % 60) + " min."; }
    try { $("dtr").scrollIntoView({ behavior: "smooth", block: "nearest" }); } catch (e) {}
  }
  function runPuzzle(spec) {
    var Z = C.pz, cs = Z.c, need = spec.id ? fetch("/js/dp/index.json").then(function (r) { return r.json(); }).then(function (ix) { if (ix[spec.id] === undefined) throw 0; return ix[spec.id]; }) : Promise.resolve(Math.floor(spec.idx / cs));
    Promise.all([need.then(function (k) { return fetch("/js/dp/" + k + ".json").then(function (r) { return r.json(); }).then(function (arr) { return spec.id ? arr.filter(function (x) { return x.id === spec.id; })[0] : arr[spec.idx % cs]; }); }), import("/js/chess.js")]).then(function (a) {
      var p = a[0]; if (!p) throw 0;
      startPuzzle(p, a[1].Chess); $("dta").onclick = null;
      var s = load();
      if (!practice && s.res && s.res[N] && s.res[N].k === "p") { done = true; tries = s.res[N].t; lost = s.res[N].w ? tries - 1 : 3; pips(); pzResult(!!s.res[N].w, s); if (s.res[N].w) msg("good", "You already solved today's puzzle.", "Come back tomorrow for the next one."); }
      root.classList.add("ready");
    }).catch(function () { msg("bad", "The puzzle did not load.", "Check your connection and reload the page."); });
  }
  (function () {
    var pp = q.get("p"), tq = q.get("t"), today = iso(new Date());
    if (pp && /^[A-Za-z0-9]{3,8}$/.test(pp)) { practice = true; runPuzzle({ id: pp }); window.__pz = 1; return; }
    if (!tq && C.pz && !C.schedule[today]) { var d = daysBetween(C.pz.frm, today); if (d >= 0 && d % 2 === 0) { window.__pz = 1; runPuzzle({ idx: (d / 2) % C.pz.n }); } }
  })();

  if (!window.__pz) fetch("/js/daily-data.json").then(function (r) { return r.json(); }).then(function (all) {
    var by = {}; all.forEach(function (x) { by[x.slug] = x; });
    var t = q.get("t"), L = C.order.length, slug;
    if (t && by[t]) { practice = true; slug = t; } else slug = C.schedule[iso(new Date())] || C.order[(((N - 1) % L) + L) % L];
    P = by[slug] || all[0];
    $("dte").textContent = (practice ? "Practice" : "Daily Trap #" + N) + " \u00b7 " + P.opening;
    $("dtp").innerHTML = (P.lastsan ? "Your opponent just played <b>" + esc(P.lastsan) + "</b>. " : "") + "One tempting move is a trap.";
    buildBoard(P.victim === "b"); draw(P.fen, P.last); goal("Find the safe move", P.victim, ""); pips(); msg("", "Find the safe move.", "Tap or drag a piece.");
    $("dta").onclick = again;
    var s = load();
    if (!practice && s.res && s.res[N]) { done = true; tries = s.res[N].t; lost = s.res[N].w ? tries - 1 : 3; pips(); result(!!s.res[N].w, null, s); if (s.res[N].w) msg("good", "You already survived today's trap.", "Come back tomorrow for the next one."); }
    root.classList.add("ready");
  }).catch(function () { msg("bad", "The trap did not load.", "Check your connection and reload the page."); });
})();
