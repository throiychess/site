// Members area: passwordless login (magic link) with Supabase. The key below is a publishable key (public by design); access is limited per user by row level security.
const SB_URL = "https://ytxrrmvszifvtdyilezn.supabase.co", SB_KEY = "sb_publishable_nARSIxN5aKJghUK745Frdw_QbXhdf29";
const $ = (s) => document.querySelector(s); const esc = (t) => String(t == null ? "" : t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const ev = (n) => { try { if (window.goatcounter && goatcounter.count) goatcounter.count({ path: n, title: n, event: true }); } catch (e) {} };
const sb = window.supabase.createClient(SB_URL, SB_KEY, { auth: { persistSession: true, detectSessionInUrl: true, flowType: "pkce" } });
const SOCIALS = [["youtube", "YouTube", "https://www.youtube.com/@ThroiyChess?sub_confirmation=1"], ["instagram", "Instagram", "https://www.instagram.com/throiychess"], ["tiktok", "TikTok", "https://www.tiktok.com/@throiychess"], ["facebook", "Facebook", "https://www.facebook.com/throiychess"]];
let profile = null;

async function render(session) {
  $("#m-login").hidden = !!session; $("#m-app").hidden = !session; if (!session) return;
  $("#m-email").textContent = session.user.email;
  const { data: p } = await sb.from("profiles").select("*").eq("id", session.user.id).maybeSingle(); profile = p || { socials: {} };
  $("#m-name").value = profile.display_name || ""; $("#m-cc").value = profile.chesscom_username || ""; $("#m-li").value = profile.lichess_username || "";
  drawSocials(); await drawAnalyses();
}
function drawSocials() {
  const so = profile.socials || {}; const n = SOCIALS.filter(([k]) => so[k]).length;
  $("#m-soc").innerHTML = SOCIALS.map(([k, name, url]) => `<div class="m-soc"><span><b>${name}</b></span>${so[k] ? `<span class="small">Following &#10003;</span>` : `<a class="btn" target="_blank" rel="noopener" href="${url}" data-k="${k}">Follow</a><button class="btn solid" type="button" data-claim="${k}">I follow</button>`}</div>`).join("");
  $("#m-socmsg").textContent = n === 4 ? "You follow Throiy Chess everywhere. Thank you! You get a free in-depth analysis when the improvement program starts." : `${n} of 4. Follow all four and you get a free in-depth analysis when the improvement program starts.`;
}
async function drawAnalyses() {
  const { data, error } = await sb.from("analyses").select("id,created_at,site,username,games,accuracy,avg_loss,band,top_leak").order("created_at", { ascending: false }).limit(30);
  const box = $("#m-list"); if (error) { box.innerHTML = `<p class="small">Could not load your analyses.</p>`; return; }
  if (!data.length) { box.innerHTML = `<p>No saved reports yet. <a href="/analyze/">Analyze your games</a> while you are logged in and your report is saved here.</p>`; return; }
  let trend = ""; if (data.length >= 2) { const d = (data[0].avg_loss - data[data.length - 1].avg_loss); trend = `<p class="az-what"><b>Pawns lost per move:</b> ${Number(data[data.length - 1].avg_loss).toFixed(2)} &rarr; ${Number(data[0].avg_loss).toFixed(2)} (${d <= 0 ? "" : "+"}${d.toFixed(2)} since your first saved report). Lower is better.</p>`; }
  box.innerHTML = trend + `<div class="az-gm">` + data.map((a) => `<div class="m-row"><span class="small">${new Date(a.created_at).toLocaleDateString()}</span><span><b>${esc(a.username)}</b> <span class="small">${a.site === "chesscom" ? "Chess.com" : "Lichess"} &middot; ${a.games} game${a.games > 1 ? "s" : ""}</span></span><span class="small">${Number(a.accuracy).toFixed(0)}% accuracy &middot; ${Number(a.avg_loss).toFixed(2)} pawns/move${a.band ? " &middot; looks like " + esc(a.band) : ""}</span><button class="btn" type="button" data-del="${a.id}">Delete</button></div>`).join("") + `</div>`;
}
$("#m-form").addEventListener("submit", async (e) => {
  e.preventDefault(); const email = $("#m-mail").value.trim(), msg = $("#m-msg"); if (!email) return; msg.textContent = "Sending…"; ev("members-login-request");
  const { error } = await sb.auth.signInWithOtp({ email, options: { emailRedirectTo: location.origin + "/members/", shouldCreateUser: true } });
  msg.textContent = error ? (error.status === 429 ? "Too many tries. Please wait a few minutes." : "That did not work. Check the address and try again.") : "Check your inbox: we sent you a login link. Open it on this device.";
});
$("#m-prof").addEventListener("submit", async (e) => { e.preventDefault(); const s = (await sb.auth.getSession()).data.session; if (!s) return;
  const { error } = await sb.from("profiles").update({ display_name: $("#m-name").value.trim() || null, chesscom_username: $("#m-cc").value.trim() || null, lichess_username: $("#m-li").value.trim() || null }).eq("id", s.user.id);
  $("#m-pmsg").textContent = error ? "Could not save." : "Saved."; });
document.addEventListener("click", async (e) => {
  const c = e.target.closest("[data-claim]"), d = e.target.closest("[data-del]"), o = e.target.closest("#m-out"); const s = (await sb.auth.getSession()).data.session;
  if (c && s) { const so = { ...(profile.socials || {}), [c.dataset.claim]: new Date().toISOString() }; const { error } = await sb.from("profiles").update({ socials: so }).eq("id", s.user.id); if (!error) { profile.socials = so; drawSocials(); ev("members-follow-" + c.dataset.claim); } }
  if (d && s) { await sb.from("analyses").delete().eq("id", d.dataset.del); drawAnalyses(); }
  if (o) { await sb.auth.signOut(); render(null); }
});
sb.auth.onAuthStateChange((evt, session) => { if (evt === "SIGNED_IN" || evt === "INITIAL_SESSION" || evt === "SIGNED_OUT") setTimeout(() => render(session), 0); });
