// Members area: passwordless login (magic link) with Supabase. The key below is a publishable key (public by design); access is limited per user by row level security.
const SB_URL = "https://ytxrrmvszifvtdyilezn.supabase.co", SB_KEY = "sb_publishable_nARSIxN5aKJghUK745Frdw_QbXhdf29";
const $ = (s) => document.querySelector(s); const esc = (t) => String(t == null ? "" : t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const ev = (n) => { try { if (window.goatcounter && goatcounter.count) goatcounter.count({ path: n, title: n, event: true }); } catch (e) {} };
const sb = window.__sb = window.supabase.createClient(SB_URL, SB_KEY, { auth: { persistSession: true, detectSessionInUrl: true, flowType: "pkce" } });
const SOCIALS = [["youtube", "YouTube", "https://www.youtube.com/@ThroiyChess?sub_confirmation=1"], ["instagram", "Instagram", "https://www.instagram.com/throiychess"], ["tiktok", "TikTok", "https://www.tiktok.com/@throiychess"], ["facebook", "Facebook", "https://www.facebook.com/throiychess"]];
const AV = { king: "♚︎", queen: "♛︎", rook: "♜︎", bishop: "♝︎", knight: "♞︎", pawn: "♟︎", star: "★", bolt: "✦" };
const LEVELS = [["Pawn", 0], ["Knight", 100], ["Bishop", 250], ["Rook", 500], ["Queen", 1000], ["King", 2000]];
let profile = null, A = [];

async function render(session) {
  if (location.hash === "#logout") { await sb.auth.signOut(); try { localStorage.removeItem("tc_av"); } catch (e) {} history.replaceState(null, "", "/members/"); session = null; }
  $("#m-login").hidden = !!session; $("#m-app").hidden = !session; if (!session) { document.documentElement.removeAttribute("data-in"); return; } document.documentElement.setAttribute("data-in", "1");
  $("#m-email").textContent = session.user.email; show();
  const { data: p } = await sb.from("profiles").select("*").eq("id", session.user.id).maybeSingle(); profile = p || { socials: {} }; window.__plan = profile.plan || "free";
  $("#m-name").value = profile.display_name || ""; $("#m-cc").value = profile.chesscom_username || ""; $("#m-li").value = profile.lichess_username || "";
  const { data: c } = await sb.rpc("daily_checkin"); const r = Array.isArray(c) ? c[0] : c; if (r) { Object.assign(profile, { points: r.points, streak: r.streak, best_streak: r.best_streak, last_checkin: r.last_checkin }); profile._gained = r.gained || 0; }
  const u = $("#az-user"); if (u && !u.value) { if (profile.chesscom_username) { u.value = profile.chesscom_username; $("#az-site").value = "chesscom"; } else if (profile.lichess_username) { u.value = profile.lichess_username; $("#az-site").value = "lichess"; } }
  drawHello(); drawSocials(); await drawAnalyses(); drawEarn();
}
window.addEventListener("az-saved", () => { drawAnalyses().then(drawEarn); });
function drawHello() {
  $("#m-hello").textContent = profile.display_name ? "Welcome back, " + profile.display_name : "Welcome back";
  $("#m-ava").textContent = AV[profile.avatar] || AV.pawn; try { localStorage.setItem("tc_av", AV[profile.avatar] || AV.pawn); } catch (e) {}
}
const VIEWS = ["overview", "analyze", "reports", "training", "puzzles", "earn", "plan", "profile"];
function show() { const v = VIEWS.includes(location.hash.slice(1)) ? location.hash.slice(1) : "overview";
  document.querySelectorAll(".mview").forEach((s) => { s.hidden = s.dataset.view !== v; });
  document.querySelectorAll(".mnav a").forEach((a) => { if (a.dataset.v === v) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); }); }
window.addEventListener("hashchange", () => { if (location.hash === "#logout") render(null); else show(); });

function followCount() { const so = (profile && profile.socials) || {}; return SOCIALS.filter(([k]) => so[k]).length; }
function totalPoints() { return (profile.points || 0) + A.length * 20 + followCount() * 10; }
function badgeList() {
  const n = A.length, f = followCount(), st = Math.max(profile.streak || 0, profile.best_streak || 0), chron = A.slice().reverse();
  const improved = chron.length >= 2 && Number(chron[chron.length - 1].avg_loss) < Number(chron[0].avg_loss);
  return [["First report", "Save your first report", n >= 1, "chart"], ["Regular", "Save 5 reports", n >= 5, "chart"], ["Dedicated", "Save 10 reports", n >= 10, "chart"], ["Improver", "Lower your pawns lost per move between two reports", improved, "bolt"],
    ["Supporter", "Follow Throiy Chess on all four", f === 4, "star"], ["3-day streak", "Visit 3 days in a row", st >= 3, "flame"], ["Week streak", "Visit 7 days in a row", st >= 7, "flame"], ["Month streak", "Visit 30 days in a row", st >= 30, "flame"]];
}
function drawEarn() {
  const pts = totalPoints(); let li = 0; LEVELS.forEach(([, t], i) => { if (pts >= t) li = i; }); const cur = LEVELS[li], nx = LEVELS[li + 1];
  const pct = nx ? Math.round(((pts - cur[1]) / (nx[1] - cur[1])) * 100) : 100;
  $("#m-level").innerHTML = `<div class="mlv"><span class="mava big">${AV[profile.avatar] || AV.pawn}</span><div><b>${cur[0]}</b><span class="small"> level</span><div class="mbar"><i style="width:${pct}%"></i></div><span class="small">${pts} points${nx ? ` &middot; ${nx[1] - pts} to ${nx[0]}` : " &middot; top level"}</span></div></div>`;
  const st = profile.streak || 0; $("#m-streak").innerHTML = `<div class="mlv"><span class="mflame">&#128293;</span><div><b>${st} day${st === 1 ? "" : "s"}</b><span class="small"> streak</span><br><span class="small">${profile._gained ? "+" + profile._gained + " points today. " : ""}Best: ${Math.max(profile.best_streak || 0, st)}. Come back tomorrow to keep it.</span></div></div>`;
  $("#m-av").innerHTML = Object.entries(AV).map(([k, g]) => `<button type="button" class="mavb${profile.avatar === k ? " on" : ""}" data-av="${k}" aria-label="Avatar ${k}" aria-pressed="${profile.avatar === k}">${g}</button>`).join("");
  $("#m-badges").innerHTML = badgeList().map(([t, d, ok]) => `<div class="mbdg${ok ? " on" : ""}"><b>${ok ? "&#9733; " : "&#9734; "}${esc(t)}</b><span class="small">${esc(d)}</span></div>`).join("");
  $("#m-ava").textContent = AV[profile.avatar] || AV.pawn; drawOverview(A);
}
function drawSocials() {
  const so = profile.socials || {}; const n = followCount();
  $("#m-soc").innerHTML = SOCIALS.map(([k, name, url]) => `<div class="m-soc"><span><b>${name}</b> <span class="small">+10 points</span></span>${so[k] ? `<span class="small">Following &#10003;</span>` : `<a class="btn" target="_blank" rel="noopener" href="${url}" data-k="${k}">Follow</a><button class="btn solid" type="button" data-claim="${k}">I follow</button>`}</div>`).join("");
  $("#m-socmsg").textContent = n === 4 ? "You follow Throiy Chess everywhere. Thank you! You get a free in-depth analysis when the improvement program starts." : `${n} of 4. Follow all four and you get a free in-depth analysis when the improvement program starts.`;
}
function chart(data, key, title, lowerBetter, dec, suffix) {
  const d = data.slice().reverse(), vals = d.map((x) => Number(x[key])), n = vals.length, W = 600, H = 190, pl = 58, pr = 18, pt = 16, pb = 34;
  let lo = Math.min(...vals), hi = Math.max(...vals); if (hi - lo < 1e-9) { const pad = Math.abs(hi) * 0.1 + 0.02; lo -= pad; hi += pad; } else { const pad = (hi - lo) * 0.2; lo -= pad; hi += pad; }
  const X = (i) => (n === 1 ? (pl + W - pr) / 2 : pl + (i * (W - pl - pr)) / (n - 1)), Y = (v) => pt + ((hi - v) / (hi - lo)) * (H - pt - pb);
  const pts = vals.map((v, i) => `${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(" "), last = vals[n - 1], diff = last - vals[0], good = n > 1 && (lowerBetter ? diff < 0 : diff > 0);
  const fmt = (v) => v.toFixed(dec) + (suffix || ""), dt = (x) => new Date(x.created_at).toLocaleDateString(undefined, { day: "numeric", month: "short" });
  const dots = vals.map((v, i) => `<circle cx="${X(i).toFixed(1)}" cy="${Y(v).toFixed(1)}" r="${i === n - 1 ? 5 : 3.5}" class="${i === n - 1 ? "last" : ""}"><title>${esc(dt(d[i]))}: ${fmt(v)}</title></circle>`).join("");
  return `<div class="mchart"><div class="mch"><b>${title}</b><span class="${n > 1 ? (good ? "up" : "down") : ""}">${fmt(last)}${n > 1 ? ` (${diff > 0 ? "+" : ""}${diff.toFixed(dec)}${suffix || ""} since first)` : ""}</span></div>
<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(title)} over ${n} report${n > 1 ? "s" : ""}"><line x1="${pl}" y1="${pt}" x2="${W - pr}" y2="${pt}"/><line x1="${pl}" y1="${H - pb}" x2="${W - pr}" y2="${H - pb}"/>
<text x="${pl - 6}" y="${pt + 4}" text-anchor="end">${fmt(hi)}</text><text x="${pl - 6}" y="${H - pb + 4}" text-anchor="end">${fmt(lo)}</text>
<text x="${pl}" y="${H - 8}">${esc(dt(d[0]))}</text>${n > 1 ? `<text x="${W - pr}" y="${H - 8}" text-anchor="end">${esc(dt(d[n - 1]))}</text>` : ""}
${n > 1 ? `<polyline points="${pts}"/>` : ""}${dots}</svg></div>`;
}
function drawOverview(data) {
  const n = data.length, last = data[0], first = data[n - 1];
  const stat = (b, s) => `<div class="mstat"><b>${b}</b><span>${s}</span></div>`;
  $("#m-stats").innerHTML = (n ? stat(n, "saved report" + (n > 1 ? "s" : "")) + stat(Number(last.accuracy).toFixed(0) + "%", "accuracy, latest") + stat(Number(last.avg_loss).toFixed(2), "pawns lost per move" + (n > 1 ? " (" + (last.avg_loss - first.avg_loss <= 0 ? "" : "+") + (last.avg_loss - first.avg_loss).toFixed(2) + " since first)" : "")) + (last.band ? stat(esc(last.band), "your play looks like") : "") : stat("0", "saved reports yet")) + stat("&#128293; " + (profile.streak || 0), "day streak") + stat(totalPoints(), "points");
  $("#m-next").innerHTML = n ? `<p><b>Next step:</b> run a fresh report with your newest games and see if your pawns lost per move went down.</p><a class="btn solid" href="#analyze">Analyze new games</a>` : `<p><b>Next step:</b> analyze your last 5 games. It takes a minute and your report is saved here.</p><a class="btn solid" href="#analyze">Analyze my games</a>`;
}
async function drawAnalyses() {
  const { data, error } = await sb.from("analyses").select("id,created_at,site,username,games,accuracy,avg_loss,band,top_leak").order("created_at", { ascending: false }).limit(30);
  if (!error) { A = data; drawOverview(data); }
  const box = $("#m-list"), ch = $("#m-charts"); if (error) { box.innerHTML = `<p class="small">Could not load your analyses.</p>`; return; }
  if (!data.length) { ch.innerHTML = ""; box.innerHTML = `<p>No saved reports yet. <a href="#analyze">Analyze your games</a> while you are logged in and your report is saved here.</p>`; return; }
  ch.innerHTML = `<div class="mcharts">${chart(data, "avg_loss", "Pawns lost per move", true, 2, "")}${chart(data, "accuracy", "Accuracy", false, 0, "%")}</div>` + (data.length < 2 ? `<p class="small">One report so far. Run another one after a few more games and your progress shows as a line.</p>` : "");
  box.innerHTML = `<div class="az-gm">` + data.map((a) => `<div class="m-row"><span class="small">${new Date(a.created_at).toLocaleDateString()}</span><span><b>${esc(a.username)}</b> <span class="small">${a.site === "chesscom" ? "Chess.com" : "Lichess"} &middot; ${a.games} game${a.games > 1 ? "s" : ""}</span></span><span class="small">${Number(a.accuracy).toFixed(0)}% accuracy &middot; ${Number(a.avg_loss).toFixed(2)} pawns/move${a.band ? " &middot; looks like " + esc(a.band) : ""}</span><button class="btn" type="button" data-del="${a.id}">Delete</button></div>`).join("") + `</div>`;
}
let hcId = null, hcTok = null;
function hcInit() { if (!window.TS_KEY || hcId !== null) return; if (!window.turnstile) return setTimeout(hcInit, 300); hcId = window.turnstile.render("#m-hc", { sitekey: window.TS_KEY, size: "flexible", callback: (t) => { hcTok = t; }, "expired-callback": () => { hcTok = null; } }); }
hcInit();
$("#m-form").addEventListener("submit", async (e) => {
  e.preventDefault(); const email = $("#m-mail").value.trim(), msg = $("#m-msg"); if (!email) return; if (window.TS_KEY && !hcTok) { msg.textContent = "Please wait a second while we check that you are human, then try again."; return; } msg.textContent = "Sending…"; ev("members-login-request");
  const { error } = await sb.auth.signInWithOtp({ email, options: { emailRedirectTo: location.origin + "/members/", shouldCreateUser: true, ...(hcTok ? { captchaToken: hcTok } : {}) } });
  if (window.turnstile && hcId !== null) { window.turnstile.reset(hcId); hcTok = null; }
  msg.textContent = error ? (error.status === 429 ? "Too many tries. Please wait a few minutes." : "That did not work. Check the address and try again.") : "Check your inbox: we sent you a login link. Open it on this device.";
});
const gbtn = $("#m-google"); if (gbtn) gbtn.addEventListener("click", () => { ev("members-login-google"); sb.auth.signInWithOAuth({ provider: "google", options: { redirectTo: location.origin + "/members/" } }); });
let gTries = 0;
async function gInit() {
  const box = $("#m-gid"); if (!box || !window.G_ID) return;
  if (!(window.google && google.accounts && google.accounts.id)) { if (++gTries < 25) return setTimeout(gInit, 300); if (gbtn) gbtn.hidden = false; return; }
  const raw = Array.from(crypto.getRandomValues(new Uint8Array(16)), (x) => x.toString(16).padStart(2, "0")).join("");
  const hashed = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(raw))), (x) => x.toString(16).padStart(2, "0")).join("");
  google.accounts.id.initialize({ client_id: window.G_ID, nonce: hashed, ux_mode: "popup", callback: async (r) => { ev("members-login-google"); const { error } = await sb.auth.signInWithIdToken({ provider: "google", token: r.credential, nonce: raw }); if (error) { $("#m-msg").textContent = "Google login did not work. Try the e-mail link instead."; } } });
  google.accounts.id.renderButton(box, { type: "standard", theme: "outline", size: "large", text: "continue_with", shape: "pill", width: 360 });
}
gInit();
$("#m-prof").addEventListener("submit", async (e) => { e.preventDefault(); const s = (await sb.auth.getSession()).data.session; if (!s) return;
  const { error } = await sb.from("profiles").update({ display_name: $("#m-name").value.trim() || null, chesscom_username: $("#m-cc").value.trim() || null, lichess_username: $("#m-li").value.trim() || null }).eq("id", s.user.id);
  if (!error) { profile.display_name = $("#m-name").value.trim() || null; drawHello(); }
  $("#m-pmsg").textContent = error ? "Could not save." : "Saved."; });
document.addEventListener("click", async (e) => {
  const c = e.target.closest("[data-claim]"), d = e.target.closest("[data-del]"), o = e.target.closest("#m-out"), av = e.target.closest("[data-av]"); const s = (await sb.auth.getSession()).data.session;
  if (c && s) { const so = { ...(profile.socials || {}), [c.dataset.claim]: new Date().toISOString() }; const { error } = await sb.from("profiles").update({ socials: so }).eq("id", s.user.id); if (!error) { profile.socials = so; drawSocials(); drawEarn(); ev("members-follow-" + c.dataset.claim); } }
  if (av && s) { const { error } = await sb.from("profiles").update({ avatar: av.dataset.av }).eq("id", s.user.id); if (!error) { profile.avatar = av.dataset.av; drawEarn(); ev("members-avatar"); } }
  if (d && s) { await sb.from("analyses").delete().eq("id", d.dataset.del); drawAnalyses().then(drawEarn); }
  if (o) { await sb.auth.signOut(); try { localStorage.removeItem("tc_av"); } catch (e) {} document.documentElement.removeAttribute("data-in"); render(null); }
  if (e.target.closest("#m-del") && s) { if (!confirm("Delete your account and all saved reports? This cannot be undone.")) return; $("#m-delmsg").textContent = "Deleting…";
    const { error } = await sb.functions.invoke("delete-account"); if (error) { $("#m-delmsg").textContent = "Could not delete. Please contact us."; return; } await sb.auth.signOut(); ev("members-account-deleted"); render(null); $("#m-msg").textContent = "Your account has been deleted."; }
});
sb.auth.onAuthStateChange((evt, session) => { if (evt === "SIGNED_IN" || evt === "INITIAL_SESSION" || evt === "SIGNED_OUT") setTimeout(() => render(session), 0); });
