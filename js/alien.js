(function () {
  "use strict";
  var D = null, Chess = null;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var FILES = "abcdefgh";

  function boardHTML(fen, flip, last, sel, hint) {
    var rows = fen.split(" ")[0].split("/"), grid = [];
    rows.forEach(function (r) { var row = []; r.split("").forEach(function (c) { if (/\d/.test(c)) for (var i = 0; i < +c; i++) row.push(""); else row.push(c); }); grid.push(row); });
    var h = '<div class="al-bd' + (flip ? " flip" : "") + '">';
    for (var r = 0; r < 8; r++) for (var f = 0; f < 8; f++) {
      var rr = flip ? 7 - r : r, ff = flip ? 7 - f : f, sq = FILES[ff] + (8 - rr), c = grid[rr][ff];
      var cls = "al-sq " + ((rr + ff) % 2 ? "d" : "l") + (last && (last.from === sq || last.to === sq) ? " lm" : "") + (sel === sq ? " sel" : "") + (hint && hint.indexOf(sq) >= 0 ? " hint" : "");
      var co = (f === 0 ? '<span class="co rk">' + (8 - rr) + "</span>" : "") + (r === 7 ? '<span class="co fl">' + FILES[ff] + "</span>" : "");
      h += '<div class="' + cls + '" data-sq="' + sq + '">' + co + (c ? '<img alt="" draggable="false" src="/img/pieces/' + (c === c.toUpperCase() ? "w" : "b") + c.toLowerCase() + '.png">' : "") + "</div>";
    }
    return h + "</div>";
  }

  /* ---------- tabs ---------- */
  function tabs() {
    var ts = $$(".al-tab"), ps = $$(".al-panel");
    function show(id) {
      if (!ps.some(function (p) { return p.id === id; })) id = "short";
      ts.forEach(function (t) { var on = t.getAttribute("data-t") === id; t.setAttribute("aria-selected", on); t.classList.toggle("on", on); });
      ps.forEach(function (p) { p.hidden = p.id !== id; });
    }
    ts.forEach(function (t) { t.addEventListener("click", function (e) { e.preventDefault(); var id = t.getAttribute("data-t"); show(id); try { history.replaceState(null, "", "#" + id); } catch (x) {} }); });
    $$("[data-go]").forEach(function (b) { b.addEventListener("click", function (e) { e.preventDefault(); show(b.getAttribute("data-go")); window.scrollTo({ top: $(".al-tabs").offsetTop - 70, behavior: "smooth" }); }); });
    show((location.hash || "#short").slice(1));
    var sa = $$(".al-seg button");
    sa.forEach(function (b) { b.addEventListener("click", function () { var m = b.getAttribute("data-m"); sa.forEach(function (x) { x.classList.toggle("on", x === b); }); $$("[data-lv]").forEach(function (el) { el.hidden = el.getAttribute("data-lv") !== m; }); }); });
  }

  /* ---------- learn: same player as the trap pages ---------- */
  function learn() {
    var L = D.lines, cur = 0, ln = L[0], B = $("#board"), sqs = [], P = "/img/pieces/";
    for (var r = 7; r >= 0; r--) for (var f = 0; f < 8; f++) {
      var d = document.createElement("div"); d.className = "sq " + ((r + f) % 2 ? "l" : "d"); d.dataset.n = FILES[f] + (r + 1);
      if (f === 0) { var c = document.createElement("span"); c.className = "co rk"; c.textContent = r + 1; d.appendChild(c); }
      if (r === 0) { var c2 = document.createElement("span"); c2.className = "co fl"; c2.textContent = FILES[f]; d.appendChild(c2); }
      B.appendChild(d); sqs.push(d);
    }
    function parse(fen) { var m = {}; fen.split("/").forEach(function (row, i) { var f = 0; row.split("").forEach(function (ch) { if (/\d/.test(ch)) f += +ch; else { m[FILES[f] + (8 - i)] = ch; f++; } }); }); return m; }
    function note(i) { var k = i; while (k >= 0 && !ln.notes[k]) k--; return ln.notes[k] || { label: "", tag: "", text: "", marks: [] }; }
    function movesHTML() { var h = ""; ln.plies.forEach(function (p, i) { if (!i) return; if (i % 2) h += "<span>" + ((i + 1) / 2 | 0) + ".</span>"; h += '<button type="button" data-p="' + i + '">' + p.san + "</button>"; }); $("#moves").innerHTML = h; }
    function show(i) {
      cur = Math.max(0, Math.min(ln.plies.length - 1, i)); var p = ln.plies[cur], m = parse(p.fen), n = note(cur), mk = (ln.notes[cur] && ln.notes[cur].marks) || [];
      sqs.forEach(function (d) {
        var s = d.dataset.n; d.classList.toggle("hl", s === p.fr || s === p.to); d.classList.toggle("mk", mk.indexOf(s) >= 0 || mk.indexOf("!" + s) >= 0); d.classList.toggle("red", mk.indexOf("!" + s) >= 0);
        var old = d.querySelector("img"); if (old) old.remove(); var c = m[s];
        if (c) { var im = document.createElement("img"); im.alt = ""; im.src = P + (c === c.toUpperCase() ? "w" : "b") + c.toLowerCase() + ".png"; d.appendChild(im); }
      });
      $("#nl").textContent = n.label; var t = $("#nt"); t.textContent = n.tag; t.hidden = !n.tag; $("#nx").textContent = n.text;
      $$("#moves button").forEach(function (b) { b.classList.toggle("on", +b.dataset.p === cur); });
    }
    function pick(k) { ln = L[k]; $$("#al-chips button").forEach(function (b, x) { b.classList.toggle("on", x === k); }); movesHTML(); show(0); }
    $("#al-chips").innerHTML = L.map(function (l) { return '<button type="button">' + l.title + "</button>"; }).join("");
    $$("#al-chips button").forEach(function (b, k) { b.onclick = function () { pick(k); }; });
    $("#first").onclick = function () { show(0); }; $("#prev").onclick = function () { show(cur - 1); };
    $("#next").onclick = function () { show(cur + 1); }; $("#last").onclick = function () { show(ln.plies.length - 1); };
    $("#moves").onclick = function (e) { var b = e.target.closest("button"); if (b) show(+b.dataset.p); };
    document.addEventListener("keydown", function (e) {
      if (e.altKey || e.ctrlKey || e.metaKey || /INPUT|TEXTAREA|SELECT/.test(e.target.tagName || "")) return;
      var p = $("#learn"), q = $("#practice"), nb = $("#al-pq-next");
      if (p && !p.hidden) { if (e.key === "ArrowRight") { e.preventDefault(); show(cur + 1); } else if (e.key === "ArrowLeft") { e.preventDefault(); show(cur - 1); } }
      if (q && !q.hidden && nb && !nb.hidden && (e.key === "ArrowRight" || e.key === "Enter")) { e.preventDefault(); nb.click(); }
    });
    pick(0);
  }

  /* ---------- replies ---------- */
  function replies() {
    $$(".al-rep").forEach(function (box) {
      var rows = D.replies[box.getAttribute("data-r")]; var h = "";
      rows.forEach(function (r) {
        var cp = r.cp, k = cp >= 150 ? "win" : cp >= 50 ? "good" : cp > -50 ? "eq" : "bad";
        var w = Math.max(4, Math.min(100, (cp + 100) / 6));
        h += '<li class="k-' + k + '"><b>' + r.san + '</b><span class="bar"><i style="width:' + w + '%"></i></span><span class="lab">' + r.label + "</span><em>" + (r.best ? "You: " + r.best : "") + "</em></li>";
      });
      box.innerHTML = h;
    });
  }

  /* ---------- practice ---------- */
  function practice() {
    var root = $("#al-prac"), pool = D.practice.slice(), cur = null, hearts = 3, score = 0, asked = 0, sel = null, done = false, chess = null;
    var order = pool.map(function (_, k) { return k; });
    for (var k = order.length - 1; k > 0; k--) { var j = Math.floor(Math.random() * (k + 1)); var t = order[k]; order[k] = order[j]; order[j] = t; }
    var idx = 0;
    var bd = $("#al-pq-board"), msg = $("#al-pq-msg"), hr = $("#al-hearts"), sc = $("#al-score"), nx = $("#al-pq-next"), ttl = $("#al-pq-title"), ln = $("#al-pq-line");
    function hearts_() { hr.textContent = "♥ ".repeat(hearts).trim() + (hearts < 3 ? " " + "♡ ".repeat(3 - hearts).trim() : ""); }
    function load() {
      if (hearts <= 0 || idx >= order.length) return end();
      cur = pool[order[idx]]; done = false; sel = null; chess = new Chess(cur.fen);
      ttl.textContent = cur.title; ln.textContent = cur.line; msg.className = "al-msg"; msg.textContent = "Your move."; nx.hidden = true;
      sc.textContent = "Position " + (idx + 1) + " of " + order.length + " \u00b7 solved " + score; hearts_(); draw();
    }
    function draw() { bd.innerHTML = boardHTML(chess.fen(), false, cur.last, sel); }
    function end() {
      bd.innerHTML = ""; ln.textContent = ""; ttl.textContent = hearts <= 0 ? "Out of hearts" : "All done!";
      msg.className = "al-msg"; msg.innerHTML = "You solved <b>" + score + "</b> of " + asked + ". " + (score >= asked - 1 ? "Strong. Time to try it in a real game." : "Go back to Learn and try again, it gets easier.");
      nx.hidden = false; nx.textContent = "Play again"; nx.onclick = function () { location.hash = "practice"; location.reload(); };
    }
    bd.addEventListener("click", function (ev) {
      if (done || !chess) return; var s = ev.target.closest("[data-sq]"); if (!s) return; var sq = s.getAttribute("data-sq");
      var p = chess.get(sq);
      if (!sel) { if (p && p.color === "w") { sel = sq; draw(); } return; }
      if (sq === sel) { sel = null; draw(); return; }
      if (p && p.color === "w") { sel = sq; draw(); return; }
      var mvs = chess.moves({ verbose: true }).filter(function (m) { return m.from === sel && m.to === sq; });
      if (!mvs.length) { sel = null; draw(); return; }
      var m = mvs.filter(function (x) { return x.promotion === "q"; })[0] || mvs[0];
      answer(m.san);
    });
    function answer(san) {
      done = true; asked++;
      var best = cur.moves[0].cp, mine = null; cur.moves.forEach(function (x) { if (x.san === san) mine = x; });
      var ok = mine && mine.cp >= best - 60;
      var mv = null; try { mv = chess.move(san); } catch (e) {} sel = null; bd.innerHTML = boardHTML(chess.fen(), false, mv ? { from: mv.from, to: mv.to } : null, null);
      if (ok) { score++; msg.className = "al-msg ok"; msg.innerHTML = "<b>Yes, " + san + "!</b> " + cur.why; }
      else { hearts--; msg.className = "al-msg bad"; msg.innerHTML = "<b>" + san + " is not it.</b> The best move was <b>" + cur.moves[0].san + "</b>. " + cur.why; }
      sc.textContent = "Position " + (idx + 1) + " of " + order.length + " \u00b7 solved " + score; hearts_(); idx++;
      nx.hidden = false; nx.textContent = hearts <= 0 || idx >= order.length ? "See result" : "Next position"; nx.onclick = load;
    }
    load();
  }

  function init() {
    tabs(); learn(); replies();
    import("/js/chess.js").then(function (m) { Chess = m.Chess; practice(); });
  }
  fetch("/js/alien-data.json").then(function (r) { return r.json(); }).then(function (d) { D = d; init(); });
})();
