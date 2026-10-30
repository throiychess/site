// Feedback: floating button + short in-context questions. Stored in our own database (table "feedback", insert only).
(function () {
  var SB = "https://ytxrrmvszifvtdyilezn.supabase.co", KEY = "sb_publishable_nARSIxN5aKJghUK745Frdw_QbXhdf29";
  function token() { try { var k = Object.keys(localStorage).filter(function (x) { return /^sb-.*-auth-token$/.test(x); })[0]; var s = k && JSON.parse(localStorage.getItem(k)); return s && s.access_token; } catch (e) { return null; } }
  function send(row) {
    row.page = location.pathname.slice(0, 120);
    function go(auth) { var h = { "Content-Type": "application/json", apikey: KEY, Prefer: "return=minimal" }; if (auth) h.Authorization = "Bearer " + auth; return fetch(SB + "/rest/v1/feedback", { method: "POST", headers: h, body: JSON.stringify(row) }); }
    var t = token(); return (t ? go(t).then(function (r) { return r.ok ? r : go(null); }) : go(null)).then(function (r) { try { if (window.goatcounter && goatcounter.count) goatcounter.count({ path: "feedback-" + row.context, title: "feedback", event: true }); } catch (e) {} return r.ok; }).catch(function () { return false; });
  }
  var css = document.createElement("style");
  css.textContent = ".fbb{position:fixed;right:14px;bottom:14px;z-index:40;background:#17150f;color:#e3c073;border:1px solid #4a3d1c;border-radius:99px;padding:9px 15px;font:700 12.5px/1 inherit;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,.45)}.fbb:hover{background:#221d10}" +
    ".fbo{position:fixed;inset:0;z-index:60;background:rgba(0,0,0,.6);display:grid;place-items:center;padding:16px}.fbm{background:#17150f;border:1px solid #4a3d1c;border-radius:18px;padding:22px;max-width:440px;width:100%;color:#efe8d8;font-family:inherit}" +
    ".fbm h3{margin:0 0 4px;font-size:20px}.fbm p{margin:0 0 12px;color:#a59a83;font-size:14.5px}.fbr{display:flex;gap:8px;margin:0 0 12px;flex-wrap:wrap}.fbr button,.fbk button{flex:1;min-width:90px;background:#1d1a13;border:1px solid #2c271d;color:#efe8d8;border-radius:12px;padding:11px 8px;font:inherit;font-size:15px;cursor:pointer}" +
    ".fbr button.on,.fbk button.on{border-color:#e3c073;color:#e3c073}.fbk{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 12px}.fbk button{min-width:0;flex:0 0 auto;padding:7px 12px;font-size:13.5px}" +
    ".fbm textarea{width:100%;box-sizing:border-box;min-height:90px;background:#0e0d0b;border:1px solid #2c271d;border-radius:12px;color:#efe8d8;font:inherit;font-size:15px;padding:10px;resize:vertical}.fbm .row{display:flex;gap:10px;justify-content:flex-end;margin-top:12px}" +
    ".fbm .go{background:#e3c073;color:#14110b;border:0;border-radius:10px;padding:10px 18px;font:inherit;font-weight:800;cursor:pointer}.fbm .no{background:none;border:1px solid #2c271d;color:#a59a83;border-radius:10px;padding:10px 14px;font:inherit;cursor:pointer}" +
    ".fbi{background:#17150f;border:1px solid #2c271d;border-radius:14px;padding:16px;margin:22px 0}.fbi b{display:block;margin-bottom:8px}.fbi .fbr{margin:0}.fbi textarea{margin-top:10px}.fbi .small{color:#a59a83;font-size:14px}";
  document.head.appendChild(css);
  var RT = [["🙁", "Not good", 1], ["😐", "OK", 2], ["🙂", "Good", 3]];
  var KINDS = [["idea", "Idea"], ["bug", "Problem"], ["question", "Question"], ["praise", "Praise"]];
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function open(ctx, meta) {
    var o = document.createElement("div"); o.className = "fbo"; var rating = null, kind = null;
    o.innerHTML = '<div class="fbm" role="dialog" aria-modal="true" aria-label="Feedback"><h3>Tell us what you think</h3><p>Short is fine. We read everything and it decides what we build next.</p>' +
      '<div class="fbr">' + RT.map(function (r) { return '<button type="button" data-r="' + r[2] + '" aria-label="' + r[1] + '">' + r[0] + " " + r[1] + "</button>"; }).join("") + '</div>' +
      '<div class="fbk">' + KINDS.map(function (k) { return '<button type="button" data-k="' + k[0] + '">' + k[1] + "</button>"; }).join("") + '</div>' +
      '<textarea maxlength="1500" placeholder="What would make Throiy Chess better for you?" aria-label="Your feedback"></textarea><div class="row"><button class="no" type="button">Close</button><button class="go" type="button">Send</button></div><p class="msg" role="status" style="margin:10px 0 0"></p></div>';
    document.body.appendChild(o); var ta = o.querySelector("textarea"), msg = o.querySelector(".msg"); ta.focus();
    function close() { o.remove(); document.removeEventListener("keydown", esck); } function esck(e) { if (e.key === "Escape") close(); } document.addEventListener("keydown", esck);
    o.addEventListener("click", function (e) { var t = e.target;
      if (t === o || t.classList.contains("no")) return close();
      var r = t.closest("[data-r]"), k = t.closest("[data-k]");
      if (r) { rating = +r.dataset.r; o.querySelectorAll("[data-r]").forEach(function (x) { x.classList.toggle("on", x === r); }); }
      if (k) { kind = k.dataset.k; o.querySelectorAll("[data-k]").forEach(function (x) { x.classList.toggle("on", x === k); }); }
      if (t.classList.contains("go")) { var m = ta.value.trim(); if (!rating && !m) { msg.textContent = "Pick a face or write a few words."; return; } msg.textContent = "Sending…";
        send({ context: ctx || "general", rating: rating, kind: kind, message: m || null, meta: meta || null }).then(function (ok) { if (ok) { o.querySelector(".fbm").innerHTML = "<h3>Thank you!</h3><p>That helps a lot.</p>"; setTimeout(close, 1400); } else msg.textContent = "Could not send. Please try again later."; }); }
    });
  }
  // Inline question under a result. Asks at most once per few days per context unless force.
  function inline(el, ctx, q, meta, force) {
    if (!el) return; try { var last = +localStorage.getItem("tc_fb_" + ctx) || 0; if (!force && Date.now() - last < 3 * 864e5) return; } catch (e) {}
    el.innerHTML = '<div class="fbi"><b>' + esc(q) + '</b><div class="fbr">' + RT.map(function (r) { return '<button type="button" data-r="' + r[2] + '">' + r[0] + " " + r[1] + "</button>"; }).join("") + '</div><div class="fbx"></div></div>';
    el.addEventListener("click", function (e) { var r = e.target.closest("[data-r]"); if (!r || !el.contains(r)) return; var rating = +r.dataset.r;
      try { localStorage.setItem("tc_fb_" + ctx, Date.now()); } catch (x) {}
      send({ context: ctx, rating: rating, meta: meta || null });
      el.querySelector(".fbr").remove(); var box = el.querySelector(".fbx");
      box.innerHTML = '<p class="small" style="margin:0 0 6px">Thanks! ' + (rating === 3 ? "What did you like most?" : "What would make it better?") + ' (optional)</p><textarea maxlength="1500" aria-label="Your feedback"></textarea><div class="row" style="display:flex;justify-content:flex-end;margin-top:8px"><button class="go" type="button" style="background:#e3c073;color:#14110b;border:0;border-radius:10px;padding:9px 16px;font:inherit;font-weight:800;cursor:pointer">Send</button></div>';
      box.querySelector(".go").addEventListener("click", function () { var m = box.querySelector("textarea").value.trim(); if (m) send({ context: ctx + "-comment", rating: rating, message: m, meta: meta || null }); box.innerHTML = '<p class="small" style="margin:0">Thank you. This helps us decide what to build next.</p>'; });
    }, { once: false });
  }
  window.tcFeedback = { open: open, inline: inline };
  var b = document.createElement("button"); b.type = "button"; b.className = "fbb"; b.textContent = "Feedback"; b.setAttribute("aria-label", "Send feedback"); b.addEventListener("click", function () { open("button"); }); document.body.appendChild(b);
})();
