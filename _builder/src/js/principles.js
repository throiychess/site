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
