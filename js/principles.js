(function () {
  var q = document.getElementById("pq"), lv = document.getElementById("plv"), ph = document.getElementById("pph"), tg = document.getElementById("ptag"), cnt = document.getElementById("pcount"), st = document.getElementById("pstart");
  if (!q) return;
  var cards = [].slice.call(document.querySelectorAll("#pall .pc"));
  function run() {
    var w = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean), any = w.length || lv.value || ph.value || tg.value, n = 0;
    st.style.display = any ? "none" : "";
    cards.forEach(function (c) {
      var ok = w.every(function (x) { return c.dataset.q.indexOf(x) >= 0; });
      if (lv.value && c.dataset.lv !== lv.value && c.dataset.lv !== "all") ok = false;
      if (ph.value && c.dataset.ph !== ph.value && c.dataset.ph !== "all") ok = false;
      if (tg.value && ("|" + c.dataset.tags + "|").indexOf("|" + tg.value + "|") < 0) ok = false;
      c.style.display = ok ? "" : "none"; if (ok) n++;
    });
    [].forEach.call(document.querySelectorAll("#pall .pgrid"), function (g) {
      var vis = [].some.call(g.children, function (c) { return c.style.display !== "none"; });
      g.style.display = vis ? "" : "none"; g.previousElementSibling.style.display = vis ? "" : "none";
    });
    cnt.textContent = any ? n + " principle" + (n === 1 ? "" : "s") + " found" : "";
  }
  [q, lv, ph, tg].forEach(function (el) { el.addEventListener("input", run); el.addEventListener("change", run); });
})();
