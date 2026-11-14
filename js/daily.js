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
  var q = new URLSearchParams(location.search), N = dayNum(), P, practice = false, tries = 0, done = false, sel = null, busy = false, cur, lastMv = "";
  var B = $("dtb"), sqs = {};

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
      d.classList.remove("sel", "tg"); d.classList.toggle("hl", !!uci && (uci.slice(0, 2) === n || uci.slice(2, 4) === n));
      var c = cur[n]; if (c) { var im = document.createElement("img"); im.alt = ""; im.draggable = false; im.src = "/img/pieces/" + (c === c.toUpperCase() ? "w" : "b") + c.toLowerCase() + ".png"; d.appendChild(im); }
    });
  }
  function mine(n) { var c = cur[n]; return c && ((c === c.toUpperCase()) === (P.victim === "w")); }
  function movesFrom(n) { return P.moves.filter(function (m) { return m.u.slice(0, 2) === n; }); }
  function clearSel() { Object.keys(sqs).forEach(function (n) { sqs[n].classList.remove("sel", "tg"); }); sel = null; }

  B.addEventListener("click", function (e) {
    if (done || busy) return; var d = e.target.closest(".sq"); if (!d) return; var n = d.dataset.n;
    if (sel && d.classList.contains("tg")) {
      var c = P.moves.filter(function (m) { return m.u.slice(0, 2) === sel && m.u.slice(2, 4) === n; });
      var mv = c.filter(function (m) { return m.u.length === 4 || m.u[4] === "q"; })[0] || c[0]; clearSel(); if (mv) play(mv); return;
    }
    clearSel();
    if (mine(n) && movesFrom(n).length) { sel = n; d.classList.add("sel"); movesFrom(n).forEach(function (m) { sqs[m.u.slice(2, 4)].classList.add("tg"); }); }
  });

  function msg(kind, head, text) { var m = $("dtm"); m.className = "dtmsg " + kind; m.innerHTML = "<b>" + head + "</b>" + (text ? "<span>" + text + "</span>" : ""); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function pips() { var h = ""; for (var i = 1; i <= 3; i++) h += '<i class="' + (i <= tries ? "u" : "") + '"></i>'; $("dtt").innerHTML = h + "<span>Try " + Math.min(tries + 1, 3) + " of 3</span>"; }
  function again() { busy = false; draw(P.fen, P.last); pips(); msg("", "Your move.", "Tap a piece, then tap where it goes."); $("dta").hidden = true; }

  function play(mv) {
    busy = true; tries++; pips(); draw(mv.f, mv.u); if (tries === 1) ev("daily-start" + (practice ? "-practice" : ""));
    if (mv.v === "good" || mv.v === "ok") {
      setTimeout(function () { finish(true, mv); }, 500);
    } else if (mv.v === "bait") {
      msg("bad", "You took the bait.", "Watch what happens.");
      var i = 1; (function step() { if (i < P.line.length) { draw(P.line[i].f, P.line[i].u); i++; setTimeout(step, 950); } else setTimeout(function () { miss("That is the " + esc(P.name) + ".", P.mate ? "It ends in checkmate." : "It costs you material."); }, 500); })();
    } else {
      setTimeout(function () { if (mv.rf) draw(mv.rf, mv.ru); miss("Not the trap, but there is a much better move.", mv.rs ? "Your opponent answers " + esc(mv.rs) + "." : ""); }, 650);
    }
  }
  function miss(head, text) {
    if (tries >= 3) { finish(false); return; }
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
    if (!win) draw(P.fen, P.last);
    var head = win ? "You survived the " + esc(P.name) + "." : "The " + esc(P.name) + " got you this time.";
    var sub = win ? (mv && mv.s !== P.best ? (mv.v === "ok" ? "Your move " + esc(mv.s) + " holds, but " + esc(P.best) + " is stronger." : "Your move " + esc(mv.s) + " works. The engine's first choice is " + esc(P.best) + ".") : "You found the best move: " + esc(P.best) + ".")
      : "A safe move was " + esc(P.best) + ".";
    msg(win ? "good" : "bad", head, sub);
    var fx = P.fix.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("");
    var st = practice ? "" : '<div class="dtstat"><div><b>#' + N + '</b><span>Daily Trap</span></div><div><b>' + (r.w ? r.t + "/3" : "X/3") + '</b><span>tries</span></div><div><b>' + (s.streak || 1) + '</b><span>day streak</span></div><div><b>' + (s.best || 1) + '</b><span>best streak</span></div></div>';
    var sh = P.short ? '<button type="button" class="btn" data-yt="' + esc(P.short) + '" data-title="' + esc(P.name) + '">Watch the 1-minute lesson</button>' : "";
    $("dtr").innerHTML = st + '<h2>How not to fall for it</h2><ol class="fix">' + fx.replace(/<li>/g, "<li><span>").replace(/<\/li>/g, "</span></li>") + "</ol>"
      + '<div class="btns">' + (practice ? "" : '<button type="button" class="btn solid" id="dtsh">Share my result</button>')
      + '<a class="btn' + (practice ? " solid" : "") + '" href="/traps/' + P.slug + '/" data-ev="daily-trap-page">Step through the whole trap</a>' + sh + "</div>"
      + '<p class="small" id="dtshm" role="status" aria-live="polite"></p>'
      + (practice ? '<p><a class="go" href="/today/">Play today\'s Daily Trap &rarr;</a></p>' : '<p class="dtnext">A new trap every day. <span id="dtcd"></span></p>')
      + '<div class="card" style="margin-top:18px"><span class="label">Your own games</span><h3>Which traps do you fall for?</h3><p>Enter your Chess.com or Lichess name and see where your games go wrong. Free, runs in your browser.</p><a class="go" href="/analyze/?utm_source=site&amp;utm_campaign=daily" data-ev="daily-analyze">Analyze my games free &rarr;</a></div>';
    $("dtr").hidden = false;
    var b = $("dtsh"); if (b) b.onclick = function () {
      var t = "ThroiyChess Daily Trap #" + N + "\n" + (r.w ? "✅ Survived in " + r.t + "/3" : "❌ It got me") + " · 🔥 " + (s.streak || 1) + "-day streak\nCan you survive it?", u = "https://throiychess.com/today/";
      ev("daily-share");
      if (navigator.share && matchMedia("(pointer:coarse)").matches) { navigator.share({ text: t, url: u }).catch(function () {}); return; }
      (navigator.clipboard ? navigator.clipboard.writeText(t + "\n" + u) : Promise.reject()).then(function () { $("dtshm").textContent = "Copied. Paste it in a chat or a story."; }).catch(function () { prompt("Copy your result:", t + " " + u); });
    };
    var cd = $("dtcd"); if (cd) { var n = new Date(), m = new Date(n.getFullYear(), n.getMonth(), n.getDate() + 1), mins = Math.round((m - n) / 6e4); cd.textContent = "Next one in " + Math.floor(mins / 60) + " h " + (mins % 60) + " min."; }
    try { $("dtr").scrollIntoView({ behavior: "smooth", block: "nearest" }); } catch (e) {}
  }

  fetch("/js/daily-data.json").then(function (r) { return r.json(); }).then(function (all) {
    var by = {}; all.forEach(function (x) { by[x.slug] = x; });
    var t = q.get("t"), L = C.order.length, slug;
    if (t && by[t]) { practice = true; slug = t; } else slug = C.schedule[iso(new Date())] || C.order[(((N - 1) % L) + L) % L];
    P = by[slug] || all[0];
    var side = P.victim === "w" ? "White" : "Black";
    $("dte").textContent = (practice ? "Practice" : "Daily Trap #" + N) + " · " + P.opening;
    $("dth").textContent = practice ? "Can you survive this trap?" : "Can you survive today's trap?";
    $("dtp").innerHTML = "You play <b>" + side + "</b>." + (P.lastsan ? " Your opponent just played <b>" + esc(P.lastsan) + "</b>." : "") + " One tempting move walks into a trap. Find a safe move. You get 3 tries.";
    buildBoard(P.victim === "b"); draw(P.fen, P.last); pips(); msg("", "Your move.", "Tap a piece, then tap where it goes.");
    $("dta").onclick = again;
    var s = load();
    if (!practice && s.res && s.res[N]) { done = true; tries = s.res[N].t; pips(); result(!!s.res[N].w, null, s); if (s.res[N].w) msg("good", "You already survived today's trap.", "Come back tomorrow for the next one."); }
    root.classList.add("ready");
  }).catch(function () { msg("bad", "The trap did not load.", "Check your connection and reload the page."); });
})();
