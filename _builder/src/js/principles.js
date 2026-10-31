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

  /* interactive example boards */
  var GL = { K: "♚", Q: "♛", R: "♜", B: "♝", N: "♞", P: "♟" }, SQ = "abcdefgh";
  function boardSvg(fen, mv) {
    var rows = fen.split(" ")[0].split("/"), s = "<svg viewBox=\"0 0 80 80\" role=\"img\" aria-label=\"Chess position\" style=\"max-width:100%;height:auto;border-radius:6px\">", r, f, ch, hl = {};
    if (mv) { hl[mv.slice(0, 2)] = 1; hl[mv.slice(2, 4)] = 1; }
    for (r = 0; r < 8; r++) for (f = 0; f < 8; f++) s += "<rect x=\"" + f * 10 + "\" y=\"" + r * 10 + "\" width=\"10\" height=\"10\" fill=\"" + ((r + f) % 2 ? "#b58863" : "#f0d9b5") + "\"/>" + (hl[SQ[f] + (8 - r)] ? "<rect x=\"" + f * 10 + "\" y=\"" + r * 10 + "\" width=\"10\" height=\"10\" fill=\"#e3c073\" opacity=\".6\"/>" : "");
    rows.forEach(function (row, r) { var f = 0; row.split("").forEach(function (ch) { if (/\d/.test(ch)) { f += +ch; return; } var up = ch === ch.toUpperCase();
      s += "<text x=\"" + (f * 10 + 5) + "\" y=\"" + (r * 10 + 8) + "\" text-anchor=\"middle\" font-size=\"9\" fill=\"" + (up ? "#f4f4f4" : "#111") + "\" stroke=\"" + (up ? "#111" : "#f4f4f4") + "\" stroke-width=\"0.5\" paint-order=\"stroke\" style=\"font-family:'Segoe UI Symbol','DejaVu Sans',serif\">" + GL[ch.toUpperCase()] + "</text>"; f++; }); });
    return s + "</svg>";
  }
  var ENG = null, ENGQ = 0;
  function engine(cb) {
    if (ENG) return cb(ENG);
    var w = new Worker("/js/stockfish/stockfish-17.1-lite-single-03e3232.js"), ready = false;
    ENG = { w: w, lis: null, ok: false }; w.onmessage = function (e) { var l = String(e.data); if (l === "readyok" && !ENG.ok) { ENG.ok = true; cb(ENG); } else if (ENG.lis) ENG.lis(l); };
    w.postMessage("uci"); w.postMessage("setoption name Hash value 16"); w.postMessage("isready");
  }
  function say(cp, mate, white) {
    var v = white ? cp : -cp; if (mate !== null) { var m = white ? mate : -mate; return (m > 0 ? "White" : "Black") + " has a forced mate"; }
    var a = Math.abs(v); var w = a < 25 ? "The position is about equal" : (a < 60 ? "slightly" : a < 130 ? "clearly" : a < 250 ? "much" : "completely");
    if (a < 25) return w; return (v > 0 ? "White" : "Black") + (a < 250 ? " is " + w + " better" : " is winning");
  }
  function pieceAt(fen, sq) { var rows = fen.split(" ")[0].split("/"), f = SQ.indexOf(sq[0]), r = 8 - +sq[1], x = 0, out = ""; rows[r].split("").forEach(function (ch) { if (/\d/.test(ch)) x += +ch; else { if (x === f) out = ch; x++; } }); return out; }
  function nice(fen, uci) { var p = pieceAt(fen, uci.slice(0, 2)), t = pieceAt(fen, uci.slice(2, 4)), P = p.toUpperCase(); return (P === "P" ? "" : P) + uci.slice(0, 2) + (t ? "x" : "-") + uci.slice(2, 4) + (uci[4] ? "=" + uci[4].toUpperCase() : ""); }
  [].forEach.call(document.querySelectorAll(".xb"), function (box) {
    var m = JSON.parse(box.getAttribute("data-m")), cur = m.at, bd = box.querySelector(".xbd"), pills = [].slice.call(box.querySelectorAll(".xbm .mv")), out = box.querySelector(".xbv"), eb = box.querySelector(".eng"), on = false, tok = 0;
    function analyse() {
      if (!on) return; var my = ++tok, fen = m.f[cur]; out.hidden = false; out.innerHTML = "<small>Thinking&hellip;</small>";
      engine(function (E) { if (my !== tok) return; var white = fen.split(" ")[1] === "w", cp = 0, mate = null, best = "";
        E.lis = function (l) { if (my !== tok) return; if (l.indexOf("info") === 0 && l.indexOf(" score ") > 0) { var s = l.match(/score (cp|mate) (-?\d+)/), pv = l.match(/ pv (\S+)/); if (s) { if (s[1] === "mate") { mate = +s[2]; cp = 0; } else { cp = +s[2]; mate = null; } } if (pv) best = pv[1]; }
          if (l.indexOf("bestmove") === 0) { var wv = white ? cp : -cp, pct = mate !== null ? ((white ? mate : -mate) > 0 ? 100 : 0) : Math.max(4, Math.min(96, 50 + 50 * (2 / (1 + Math.exp(-wv / 180)) - 1)));
            out.innerHTML = "<div class=\"bar\"><i style=\"width:" + pct + "%\"></i></div>" + say(wv, mate === null ? null : (white ? mate : -mate), true) + (best ? "<br><small>Best move here: " + nice(fen, best) + " &middot; " + (white ? "White" : "Black") + " to move</small>" : "<br><small>Game over</small>"); } };
        E.w.postMessage("stop"); E.w.postMessage("position fen " + fen); E.w.postMessage("go depth 16"); });
    }
    function show() {
      bd.innerHTML = boardSvg(m.f[cur], cur > 0 ? m.u[cur - 1] : "");
      pills.forEach(function (b) { b.classList.toggle("on", +b.getAttribute("data-i") === cur); }); analyse();
    }
    box.addEventListener("click", function (ev) {
      var b = ev.target.closest("button"); if (!b) return; var a = b.getAttribute("data-a"), i = b.getAttribute("data-i");
      if (i) cur = +i; else if (a === "start") cur = 0; else if (a === "end") cur = m.f.length - 1; else if (a === "prev") cur = Math.max(0, cur - 1); else if (a === "next") cur = Math.min(m.f.length - 1, cur + 1);
      else if (a === "eng") { on = !on; b.classList.toggle("on", on); if (!on) { tok++; out.hidden = true; } }
      show();
    });
    pills.forEach(function (b) { if (+b.getAttribute("data-i") === cur + 0 && false) b.classList.add("on"); });
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
