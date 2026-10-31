(function () {
  var MARK = {};
  try { MARK = JSON.parse(localStorage.getItem("tc_marks") || "{}"); } catch (e) { MARK = {}; }
  function save() { try { localStorage.setItem("tc_marks", JSON.stringify(MARK)); } catch (e) {} }
  function paint() {
    [].forEach.call(document.querySelectorAll("[data-mk]"), function (b) {
      var p = b.getAttribute("data-mk").split(":"), on = (MARK[p[1]] || "").indexOf(p[0]) >= 0;
      b.classList.toggle("on", on); b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }
  var run = null;
  document.addEventListener("click", function (ev) {
    var t = ev.target.closest && ev.target.closest("[data-mk]"); if (!t) return;
    var p = t.getAttribute("data-mk").split(":"), c = MARK[p[1]] || "";
    MARK[p[1]] = c.indexOf(p[0]) >= 0 ? c.replace(p[0], "") : c + p[0]; save(); paint(); if (run) run(true);
  });
  paint();

  /* interactive example boards: same board and pieces as the trap pages */
  var SQN = "abcdefgh", CHJ = null, CHP = null;
  function loadChess() { return CHP || (CHP = import("/js/chess.js").then(function (m) { CHJ = m.Chess; return CHJ; })); }
  function parseFen(fen) { var m = {}; fen.split(" ")[0].split("/").forEach(function (row, i) { var f = 0; row.split("").forEach(function (ch) { if (/\d/.test(ch)) f += +ch; else { m[SQN[f] + (8 - i)] = ch; f++; } }); }); return m; }
  var ENG = null;
  function engine(cb) {
    if (ENG) return ENG.ok ? cb(ENG) : ENG.q.push(cb);
    var w = new Worker("/js/stockfish/stockfish-17.1-lite-single-03e3232.js");
    ENG = { w: w, lis: null, ok: false, q: [cb] };
    w.onmessage = function (e) { var l = String(e.data); if (l === "readyok" && !ENG.ok) { ENG.ok = true; ENG.q.splice(0).forEach(function (f) { f(ENG); }); } else if (ENG.lis) ENG.lis(l); };
    w.postMessage("uci"); w.postMessage("setoption name Hash value 16"); w.postMessage("isready");
  }
  function say(v, mate) {
    if (mate !== null) return (mate > 0 ? "White" : "Black") + " has a forced mate";
    var a = Math.abs(v); if (a < 25) return "The position is about equal";
    return (v > 0 ? "White" : "Black") + (a < 60 ? " is slightly better" : a < 130 ? " is clearly better" : a < 250 ? " is much better" : " is winning");
  }
  function nice(fen, uci) { var b = parseFen(fen), p = b[uci.slice(0, 2)] || "", t = b[uci.slice(2, 4)], P = p.toUpperCase(); return (P === "P" ? "" : P) + uci.slice(0, 2) + (t ? "x" : "-") + uci.slice(2, 4) + (uci[4] ? "=" + uci[4].toUpperCase() : ""); }
  var BOXES = [], ACTIVE = null;
  [].forEach.call(document.querySelectorAll(".xb"), function (box) {
    var m = JSON.parse(box.getAttribute("data-m")), bd = box.querySelector(".xbd"), mvbox = box.querySelector(".xbm"), out = box.querySelector(".xbv"), eb = box.querySelector(".eng"), rs = box.querySelector(".xbr");
    var S = { f: m.f.slice(), u: m.u.slice(), s: m.s.slice(), cur: m.at, div: 99 }, on = false, tok = 0, sel = null, legal = [], sqs = {}, bar, barn, fillEl;
    var st = m.start.split(" "), startWhite = st[1] === "w", startNo = +st[5] || 1;
    bd.innerHTML = "<div class=\"evb\" hidden><i></i><b></b></div><div class=\"board\"></div>";
    var B = bd.querySelector(".board"); bar = bd.querySelector(".evb"); fillEl = bar.querySelector("i"); barn = bar.querySelector("b");
    for (var r = 7; r >= 0; r--) for (var f = 0; f < 8; f++) { (function (r, f) { var d = document.createElement("div"), n = SQN[f] + (r + 1); d.className = "sq " + ((r + f) % 2 ? "l" : "d"); d.dataset.n = n;
      if (f === 0) { var c = document.createElement("span"); c.className = "co rk"; c.textContent = r + 1; d.appendChild(c); }
      if (r === 0) { var c2 = document.createElement("span"); c2.className = "co fl"; c2.textContent = SQN[f]; d.appendChild(c2); }
      d.addEventListener("click", function () { ACTIVE = api; clickSq(n); }); B.appendChild(d); sqs[n] = d; })(r, f); }
    function pills() {
      var h = ""; S.s.forEach(function (s, i) { var w = (i % 2 === 0) === startWhite, no = startNo + Math.floor((i + (startWhite ? 0 : 1)) / 2), num = w ? no + "." : (i === 0 ? no + "..." : "");
        h += "<button type=\"button\" class=\"mv" + (i === m.at && i < S.div ? " key" : "") + (i < m.at ? " pre" : "") + (i >= S.div ? " you" : "") + (i + 1 === S.cur ? " on" : "") + "\" data-i=\"" + (i + 1) + "\">" + (num ? "<i>" + num + "</i>" : "") + s.replace(/</g, "&lt;") + "</button>"; });
      mvbox.innerHTML = h; if (rs) rs.hidden = S.div === 99;
    }
    function draw() {
      var fen = S.f[S.cur], pc = parseFen(fen), lm = S.cur > 0 ? S.u[S.cur - 1] : "";
      for (var n in sqs) { var d = sqs[n], c = pc[n], im = d.querySelector("img");
        d.classList.toggle("hl", !!lm && (n === lm.slice(0, 2) || n === lm.slice(2, 4))); d.classList.toggle("sel", n === sel); d.classList.toggle("lg", legal.indexOf(n) >= 0); d.classList.toggle("capt", legal.indexOf(n) >= 0 && !!c);
        if (c) { var src = "/img/pieces/" + (c === c.toUpperCase() ? "w" : "b") + c.toLowerCase() + ".png"; if (!im) { im = document.createElement("img"); im.alt = ""; im.draggable = false; d.appendChild(im); } if (im.getAttribute("src") !== src) im.setAttribute("src", src); } else if (im) im.remove(); }
      pills(); analyse();
    }
    function go(i) { S.cur = Math.max(0, Math.min(S.f.length - 1, i)); sel = null; legal = []; draw(); }
    function clickSq(n) {
      loadChess().then(function (C) {
        var fen = S.f[S.cur], c = new C(fen), pc = parseFen(fen)[n];
        if (sel && legal.indexOf(n) >= 0) {
          var mv = c.move({ from: sel, to: n, promotion: "q" }); if (!mv) return; var uci = mv.from + mv.to + (mv.promotion || "");
          if (S.cur < S.div && S.u[S.cur] === uci && S.cur < m.u.length) { S.cur++; } else { S.f = S.f.slice(0, S.cur + 1); S.u = S.u.slice(0, S.cur); S.s = S.s.slice(0, S.cur); S.f.push(c.fen()); S.u.push(uci); S.s.push(mv.san); if (S.cur < S.div) S.div = S.cur; S.cur++; }
          sel = null; legal = []; draw(); return; }
        if (pc && (pc === pc.toUpperCase()) === (c.turn() === "w")) { sel = n; legal = c.moves({ square: n, verbose: true }).map(function (x) { return x.to; }); } else { sel = null; legal = []; }
        draw();
      });
    }
    function analyse() {
      if (!on) return; var my = ++tok, fen = S.f[S.cur]; out.hidden = false; out.innerHTML = "<small>Thinking&hellip;</small>";
      engine(function (E) { if (my !== tok) return; var white = fen.split(" ")[1] === "w", cp = 0, mate = null, best = "";
        E.lis = function (l) { if (my !== tok) return; if (l.indexOf("info") === 0 && l.indexOf(" score ") > 0) { var s = l.match(/score (cp|mate) (-?\d+)/), pv = l.match(/ pv (\S+)/); if (s) { if (s[1] === "mate") { mate = +s[2]; } else { cp = +s[2]; mate = null; } } if (pv) best = pv[1]; }
          if (l.indexOf("bestmove") === 0) { var wv = white ? cp : -cp, wm = mate === null ? null : (white ? mate : -mate), pct = wm !== null ? (wm > 0 ? 100 : 0) : Math.max(3, Math.min(97, 50 + 50 * (2 / (1 + Math.exp(-wv / 180)) - 1)));
            fillEl.style.height = pct + "%"; barn.textContent = wm !== null ? "M" + Math.abs(wm) : (wv >= 0 ? "+" : "") + (wv / 100).toFixed(1); barn.className = pct >= 50 ? "lo" : "hi";
            out.innerHTML = say(wv, wm) + (best ? "<br><small>Best move here: " + nice(fen, best) + " &middot; " + (white ? "White" : "Black") + " to move</small>" : "<br><small>Game over</small>"); } };
        E.w.postMessage("stop"); E.w.postMessage("position fen " + fen); E.w.postMessage("go depth 16"); });
    }
    var api = { box: box, go: go, cur: function () { return S.cur; }, len: function () { return S.f.length; } }; BOXES.push(api);
    box.addEventListener("click", function (ev) {
      var b = ev.target.closest("button"); if (!b) return; ACTIVE = api; var a = b.getAttribute("data-a"), i = b.getAttribute("data-i");
      if (i) go(+i); else if (a === "start") go(0); else if (a === "end") go(S.f.length - 1); else if (a === "prev") go(S.cur - 1); else if (a === "next") go(S.cur + 1);
      else if (a === "reset") { S.f = m.f.slice(); S.u = m.u.slice(); S.s = m.s.slice(); S.div = 99; go(m.at); }
      else if (a === "eng") { on = !on; b.classList.toggle("on", on); box.classList.toggle("eng-on", on); bar.hidden = !on; if (!on) { tok++; out.hidden = true; } else analyse(); }
    });
    box.addEventListener("mouseenter", function () { ACTIVE = api; });
    draw();
  });
  document.addEventListener("keydown", function (e) {
    if (!BOXES.length || e.target.closest("input,textarea,select") || e.altKey || e.ctrlKey || e.metaKey) return;
    var k = e.key; if (k !== "ArrowLeft" && k !== "ArrowRight" && k !== "Home" && k !== "End") return;
    var a = ACTIVE || BOXES.slice().sort(function (x, y) { var c = function (b) { var r = b.box.getBoundingClientRect(); return Math.abs(r.top + r.height / 2 - innerHeight / 2); }; return c(x) - c(y); })[0];
    e.preventDefault(); if (k === "ArrowLeft") a.go(a.cur() - 1); else if (k === "ArrowRight") a.go(a.cur() + 1); else if (k === "Home") a.go(0); else a.go(a.len() - 1);
  });


  var q = document.getElementById("pq"); if (!q) return;
  var cards = [].slice.call(document.querySelectorAll("#pall .pc")), start = document.getElementById("pstart"), cnt = document.getElementById("pcount"), more = document.getElementById("pmore"), none = document.getElementById("pnone");
  var F = { tag: "", lv: "", ph: "", st: "" }, shown = 20, STEP = 20;
  run = function (keep) {
    if (keep !== true) shown = STEP;
    var w = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean), any = w.length || F.tag || F.lv || F.ph || F.st, hit = 0;
    start.style.display = any ? "none" : "";
    cards.forEach(function (c) {
      var m = MARK[c.getAttribute("data-slug")] || "", ok = w.every(function (x) { return c.dataset.q.indexOf(x) >= 0; });
      if (F.lv && c.dataset.lv !== F.lv && c.dataset.lv !== "all") ok = false;
      if (F.ph && c.dataset.ph !== F.ph && c.dataset.ph !== "all") ok = false;
      if (F.tag && ("|" + c.dataset.tags + "|").indexOf("|" + F.tag + "|") < 0) ok = false;
      if (F.st === "saved" && m.indexOf("s") < 0) ok = false;
      if (F.st === "learned" && m.indexOf("l") < 0) ok = false;
      if (F.st === "todo" && m.indexOf("l") >= 0) ok = false;
      if (ok) { hit++; c.style.display = hit <= shown ? "" : "none"; } else c.style.display = "none";
    });
    cnt.textContent = any ? hit + " principle" + (hit === 1 ? "" : "s") + " found" : "All principles (" + cards.length + ")";
    more.hidden = hit <= shown; more.textContent = "Show more (" + (hit - shown) + " left)"; none.hidden = hit > 0;
  };
  q.addEventListener("input", function () { run(); });
  more.addEventListener("click", function () { shown += STEP; run(true); });
  [].forEach.call(document.querySelectorAll(".ptopic"), function (b) { b.addEventListener("click", function () { F.tag = b.getAttribute("data-tag"); [].forEach.call(document.querySelectorAll(".ptopic"), function (x) { x.classList.toggle("on", x === b); }); run(); }); });
  [].forEach.call(document.querySelectorAll(".pseg"), function (g) { g.addEventListener("click", function (ev) { var b = ev.target.closest("button"); if (!b) return; F[g.getAttribute("data-seg")] = b.getAttribute("data-v"); [].forEach.call(g.children, function (x) { x.classList.toggle("on", x === b); }); run(); }); });
  run();
})();
