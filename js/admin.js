(function () {
  var SB_URL = "https://ytxrrmvszifvtdyilezn.supabase.co", SB_KEY = "sb_publishable_nARSIxN5aKJghUK745Frdw_QbXhdf29";
  var $ = function (s) { return document.querySelector(s); };
  var esc = function (t) { return String(t == null ? "" : t).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var sb = window.supabase.createClient(SB_URL, SB_KEY, { auth: { persistSession: true, detectSessionInUrl: false } });
  var root = $("#adm"), D = {}, tab = "users", q = "";
  function fmt(d) { if (!d) return "-"; var x = new Date(d); return x.toLocaleDateString("en-GB", { day: "2-digit", month: "short" }) + " " + x.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }); }
  function msg(h) { root.innerHTML = "<div class=\"acard\">" + h + "</div>"; }
  function kpi(l, v, s) { return "<div class=\"kpi\"><small>" + l + "</small><b>" + v + "</b>" + (s ? "<span>" + s + "</span>" : "") + "</div>"; }
  function chart(rows) {
    var days = [], m = 1, i, map = {}; rows.forEach(function (r) { map[r.d] = r.n; m = Math.max(m, r.n); });
    for (i = 29; i >= 0; i--) { var d = new Date(Date.now() - i * 864e5).toISOString().slice(0, 10); days.push([d, map[d] || 0]); }
    return "<svg viewBox=\"0 0 300 70\" class=\"ch\" role=\"img\" aria-label=\"Signups, last 30 days\">" + days.map(function (x, k) { var h = x[1] / m * 56; return "<rect x=\"" + (k * 10 + 1) + "\" y=\"" + (62 - h) + "\" width=\"8\" height=\"" + Math.max(h, 1) + "\" rx=\"2\" fill=\"" + (x[1] ? "#e3c073" : "#2c271d") + "\"><title>" + x[0] + ": " + x[1] + "</title></rect>"; }).join("") + "</svg>";
  }
  function csv(rows) { if (!rows.length) return ""; var k = Object.keys(rows[0]); return k.join(",") + "\n" + rows.map(function (r) { return k.map(function (c) { return "\"" + String(r[c] == null ? "" : typeof r[c] === "object" ? JSON.stringify(r[c]) : r[c]).replace(/"/g, "\"\"") + "\""; }).join(","); }).join("\n"); }
  function table(cols, rows) {
    return "<div class=\"tw\"><table><thead><tr>" + cols.map(function (c) { return "<th>" + c[0] + "</th>"; }).join("") + "</tr></thead><tbody>" + (rows.length ? rows.map(function (r) { return "<tr>" + cols.map(function (c) { return "<td>" + c[1](r) + "</td>"; }).join("") + "</tr>"; }).join("") : "<tr><td colspan=\"" + cols.length + "\">Nothing yet.</td></tr>") + "</tbody></table></div>";
  }
  function match(r) { return !q || JSON.stringify(r).toLowerCase().indexOf(q) >= 0; }
  function body() {
    var rows = (D[tab] || []).filter(match);
    if (tab === "users") return table([["Joined", function (r) { return fmt(r.created_at); }], ["Email", function (r) { return esc(r.email); }], ["Name", function (r) { return esc(r.display_name || ""); }], ["Chess.com / Lichess", function (r) { return esc((r.chesscom || "-") + " / " + (r.lichess || "-")); }], ["Analyses", function (r) { return r.analyses; }], ["Points", function (r) { return r.points == null ? "-" : r.points; }], ["Last login", function (r) { return fmt(r.last_sign_in_at); }], ["Plan", function (r) { return "<button type=\"button\" class=\"pl " + (r.plan === "premium" ? "on" : "") + "\" data-id=\"" + esc(r.id) + "\" data-p=\"" + (r.plan === "premium" ? "free" : "premium") + "\" title=\"Click to switch plan\">" + esc(r.plan || "free") + "</button>"; }]], rows);
    if (tab === "feedback") return table([["When", function (r) { return fmt(r.created_at); }], ["Type", function (r) { return esc(r.kind || r.context || ""); }], ["Rating", function (r) { return r.rating == null ? "-" : r.rating; }], ["Page", function (r) { return esc(r.page || ""); }], ["Message", function (r) { return esc(r.message || ""); }]], rows);
    return table([["When", function (r) { return fmt(r.created_at); }], ["User", function (r) { return esc(r.email || ""); }], ["Player", function (r) { return esc((r.site || "") + " " + (r.username || "")); }], ["Games", function (r) { return r.games; }], ["Accuracy", function (r) { return r.accuracy == null ? "-" : r.accuracy; }], ["Blunders", function (r) { return r.blunders; }], ["Band", function (r) { return esc(r.band || ""); }], ["Top leak", function (r) { return esc(r.top_leak || ""); }]], rows);
  }
  function draw() {
    var o = D.o, pl = o.plans || {};
    root.innerHTML = "<div class=\"kpis\">" + kpi("Members", o.users, "+" + o.new7 + " this week") + kpi("Active (7 days)", o.active7) + kpi("Premium", pl.premium || 0, (pl.free || 0) + " free") + kpi("Reports run", o.analyses, "+" + o.analyses7 + " this week") + kpi("Feedback", o.feedback, "+" + o.feedback7 + " this week" + (o.avg_rating ? " &middot; avg " + o.avg_rating : "")) + "</div>" +
      "<div class=\"two\"><div class=\"acard\"><h3>New members, last 30 days</h3>" + chart(o.signups || []) + "</div><div class=\"acard\"><h3>Top leaks found</h3>" + ((o.leaks || []).length ? (o.leaks || []).map(function (l) { return "<div class=\"lk\"><span>" + esc(l.leak) + "</span><b>" + l.n + "</b></div>"; }).join("") : "<p class=\"mut\">No reports yet.</p>") + "</div></div>" +
      "<div class=\"acard\"><div class=\"bar\"><div class=\"tabs\">" + [["users", "Members"], ["feedback", "Feedback"], ["analyses", "Reports"]].map(function (t) { return "<button type=\"button\" data-t=\"" + t[0] + "\" class=\"" + (tab === t[0] ? "on" : "") + "\">" + t[1] + " (" + (D[t[0]] || []).length + ")</button>"; }).join("") + "</div><input id=\"aq\" type=\"search\" placeholder=\"Search\" value=\"" + esc(q) + "\"><button type=\"button\" id=\"acsv\" class=\"gb\">Export CSV</button><a class=\"gb\" href=\"https://throiychess.goatcounter.com\" target=\"_blank\" rel=\"noopener\">Site analytics &rarr;</a></div><div id=\"abody\">" + body() + "</div></div>";
  }
  root.addEventListener("click", function (e) {
    var t = e.target.closest("[data-t]"), p = e.target.closest(".pl");
    if (t) { tab = t.getAttribute("data-t"); draw(); }
    else if (p) { if (!confirm("Set plan to " + p.getAttribute("data-p") + "?")) return; sb.rpc("admin_set_plan", { uid: p.getAttribute("data-id"), new_plan: p.getAttribute("data-p") }).then(function (r) { if (r.error) alert(r.error.message); else load(); }); }
    else if (e.target.id === "acsv") { var b = new Blob([csv((D[tab] || []).filter(match))], { type: "text/csv" }), a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = "throiychess-" + tab + ".csv"; a.click(); }
  });
  root.addEventListener("input", function (e) { if (e.target.id === "aq") { q = e.target.value.trim().toLowerCase(); $("#abody").innerHTML = body(); } });
  function load() {
    Promise.all([sb.rpc("admin_overview"), sb.rpc("admin_users", { lim: 500 }), sb.rpc("admin_feedback", { lim: 500 }), sb.rpc("admin_analyses", { lim: 300 })]).then(function (r) {
      if (r[0].error) { msg("<h3>No access</h3><p>This account is not an admin.</p>"); return; }
      D = { o: r[0].data, users: r[1].data || [], feedback: r[2].data || [], analyses: r[3].data || [] }; draw();
    });
  }
  sb.auth.getSession().then(function (s) {
    if (!s.data.session) { msg("<h3>Admin</h3><p>Log in first on the <a href=\"/members/\">members page</a>, then come back here.</p>"); return; }
    load();
  });
})();
