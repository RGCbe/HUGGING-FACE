// Tea Break Uploader: a Cloudflare Worker that sends Manoj's own finished videos to his own TikTok inbox.
//
// TikTok Login Kit (user.info.basic) connects the account. The Content Posting API Upload flow (video.upload)
// sends a video as a draft to the creator's TikTok inbox; he adds the caption and posts it in the TikTok app.
//
// Bindings (deploy.py sets them): TB, a KV namespace; BASE_URL and LEGAL_URL, plain text.
// Secrets (the owner adds them in the Cloudflare dashboard, never in code): TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET.
// Optional TIKTOK_VERIFY = "FILENAME=CONTENT", the file TikTok's URL-prefix check asks for.
//
// KV keys: "owner" (the first TikTok account that connects; no other account can use the app), "token",
// "q:NAME" (a queued video: title, caption, size, chunk, count), "v:NAME:K" (the video's K-th upload chunk,
// written by tiktok_queue.py so that every TikTok chunk is one KV value), "sent:NAME" (when it went to the inbox).

const API = "https://open.tiktokapis.com";
const SCOPES = "user.info.basic,video.upload";

export default {
  async fetch(request, env, ctx) {
    // keys pasted into the dashboard can carry a stray space or line break: TikTok would reject them
    env = { ...env, TIKTOK_CLIENT_KEY: (env.TIKTOK_CLIENT_KEY || "").trim(), TIKTOK_CLIENT_SECRET: (env.TIKTOK_CLIENT_SECRET || "").trim() };
    try {
      return await route(request, env, ctx);
    } catch (e) {
      console.log("error", e && e.stack || e);
      return html(page(env, `<div class="card err">Something went wrong: ${esc(String(e && e.message || e))}</div>`), 500);
    }
  },
};

async function route(request, env, ctx) {
  const url = new URL(request.url);
  const base = (env.BASE_URL || url.origin).replace(/\/$/, "");
  const ck = "; Path=/; HttpOnly; Secure; SameSite=Lax";
  const p = url.pathname;
  if (request.method === "GET" && p === "/") {
    return html(await home(env, await sessionOpenId(request, env), url.searchParams.get("msg") || ""));
  }
  if (p === "/login") {
    const state = randomToken();
    const auth = "https://www.tiktok.com/v2/auth/authorize/?" + new URLSearchParams({
      client_key: env.TIKTOK_CLIENT_KEY, response_type: "code", scope: SCOPES, redirect_uri: base + "/callback", state });
    return redirect(auth, [["Set-Cookie", `st=${state}; Max-Age=900${ck}`]]);
  }
  if (p === "/callback") {
    const q = url.searchParams;
    if (q.get("error")) return redirect("/?" + new URLSearchParams({ msg: `TikTok was not connected: ${q.get("error_description") || q.get("error")}` }));
    const st = cookies(request).st || "-";
    if (!q.get("code") || !safeEqual(q.get("state") || "", st)) {
      return redirect("/?" + new URLSearchParams({ msg: "That sign-in link expired. Please connect again." }));
    }
    const t = await tiktokForm(env, { code: q.get("code"), grant_type: "authorization_code", redirect_uri: base + "/callback" });
    if (!t.access_token) return redirect("/?" + new URLSearchParams({ msg: `TikTok sign-in failed: ${t.error_description || t.error || "unknown error"}` }));
    const info = await tiktok("GET", "/v2/user/info/?fields=open_id,avatar_url,display_name", t.access_token);
    const user = (info.data && info.data.user) || {};
    const openId = t.open_id || user.open_id;
    const owner = await env.TB.get("owner", "json");
    if (owner && owner.open_id !== openId) {
      return redirect("/?" + new URLSearchParams({ msg: "This app is private: it only works with its owner's TikTok account." }));
    }
    if (!owner) await env.TB.put("owner", JSON.stringify({ open_id: openId, display_name: user.display_name, since: now() }));
    await saveTokens(env, t, user);
    return redirect("/", [["Set-Cookie", `s=${await makeSession(env, openId)}; Max-Age=${7 * 86400}${ck}`],
                          ["Set-Cookie", `st=; Max-Age=0${ck}`]]);
  }
  if (p === "/logout") return redirect("/", [["Set-Cookie", `s=; Max-Age=0${ck}`]]);
  if (request.method === "POST" && p === "/send") {
    const origin = request.headers.get("Origin");
    if (origin && origin.replace(/\/$/, "") !== base) return text("Not allowed", 403);
    if (!(await ownerSession(request, env))) return text("Please connect with TikTok first.", 403);
    const name = new URLSearchParams(await request.text()).get("name") || "";
    const meta = await env.TB.get("q:" + name, "json");
    if (!meta) return text("That video is not in the queue.", 404);
    if (await env.TB.get("sent:" + name)) return text("This video is already in your TikTok inbox.", 409);
    const last = await env.TB.get("job:" + name, "json");
    if (last && (last.state === "processing" || (last.state === "uploading" && now() - last.at < 600))) {
      return text("TikTok is still working on this video. Reload the page in a minute.", 409);
    }
    const { readable, writable } = new TransformStream();
    const w = writable.getWriter();
    const say = (line) => w.write(new TextEncoder().encode(line + "\n"));
    ctx.waitUntil(send(env, name, meta, say).catch((e) => say("FAILED " + (e && e.message || e))).finally(() => w.close()));
    return new Response(readable, { headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" } });
  }
  if (env.TIKTOK_VERIFY && p.startsWith("/tiktok") && p.endsWith(".txt")) {
    const [file, ...rest] = env.TIKTOK_VERIFY.split("=");
    if (p === "/" + file) return text(rest.join("="));
  }
  if (p === "/healthz") return text("ok");
  return html(page(env, '<div class="card">Page not found. <a href="/">Go home</a></div>'), 404);
}

// ---------- the upload ----------
async function send(env, name, meta, say) {
  const token = await accessToken(env);
  const init = await tiktok("POST", "/v2/post/publish/inbox/video/init/", token, {
    source_info: { source: "FILE_UPLOAD", video_size: meta.size, chunk_size: meta.chunk, total_chunk_count: meta.count } });
  if (!init.error || init.error.code !== "ok") throw new Error("TikTok refused the upload: " + JSON.stringify(init.error || init));
  const { publish_id, upload_url } = init.data;
  // remembered, so the page can show how it ended even if it was closed while TikTok was still working
  const job = (state, extra = {}) => env.TB.put("job:" + name, JSON.stringify({ publish_id, state, at: now(), ...extra }));
  await job("uploading");
  await say(`Sending to TikTok (0 of ${meta.count})`);
  for (let k = 0; k < meta.count; k++) {
    const part = await env.TB.get(`v:${name}:${k}`, "arrayBuffer");
    if (!part) throw new Error(`part ${k + 1} of the video is missing`);
    const start = k * meta.chunk, end = start + part.byteLength - 1;
    let r;
    for (let attempt = 0; attempt < 3; attempt++) {
      r = await fetch(upload_url, { method: "PUT", body: part, headers: {
        "Content-Type": "video/mp4", "Content-Range": `bytes ${start}-${end}/${meta.size}` } });
      if (r.ok || r.status < 500) break;
      await sleep(3000);
    }
    if (!r.ok) {
      await job("failed", { reason: `TikTok refused part ${k + 1}: HTTP ${r.status}` });
      throw new Error(`TikTok refused part ${k + 1}: HTTP ${r.status}`);
    }
    await say(`Sending to TikTok (${k + 1} of ${meta.count})`);
  }
  await job("processing");
  for (let i = 0; i < 40; i++) {
    const st = await checkJob(env, name);
    if (st.state === "failed") throw new Error(st.reason);
    if (st.state === "inbox") {
      await say("DONE In your TikTok inbox: open TikTok, tap the notification, paste the caption and post.");
      return;
    }
    await say("TikTok is processing the video");
    await sleep(4000);
  }
  await say("DONE Still processing at TikTok: check your TikTok inbox in a few minutes, or reload this page.");
}

// Ask TikTok how the last upload of NAME is doing, and record it when it has reached the inbox.
async function checkJob(env, name) {
  const job = await env.TB.get("job:" + name, "json");
  if (!job) return { state: "none" };
  if (job.state === "inbox" || job.state === "failed" || job.state === "uploading") return job;
  const s = await tiktok("POST", "/v2/post/publish/status/fetch/", await accessToken(env), { publish_id: job.publish_id });
  const st = s.data && s.data.status;
  if (st === "FAILED") {
    const failed = { ...job, state: "failed", reason: "TikTok could not process it: " + (s.data.fail_reason || "unknown"), at: now() };
    await env.TB.put("job:" + name, JSON.stringify(failed));
    return failed;
  }
  if (st === "SEND_TO_USER_INBOX" || st === "PUBLISH_COMPLETE") {
    const meta = (await env.TB.get("q:" + name, "json")) || {};
    await env.TB.put("sent:" + name, JSON.stringify({ publish_id: job.publish_id, status: st, at: now() }));
    for (let k = 0; k < (meta.count || 0); k++) await env.TB.delete(`v:${name}:${k}`);  // free the space; the record stays
    const done = { ...job, state: "inbox", status: st, at: now() };
    await env.TB.put("job:" + name, JSON.stringify(done));
    return done;
  }
  return { ...job, state: "processing", status: st || (s.error && s.error.code) };
}

// ---------- TikTok ----------
async function tiktok(method, path, token, body) {
  const headers = { Authorization: `Bearer ${token}` };
  if (body) headers["Content-Type"] = "application/json; charset=UTF-8";
  const r = await fetch(API + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  return r.json().catch(() => ({ error: { code: "http_" + r.status } }));
}

async function tiktokForm(env, fields) {
  const r = await fetch(API + "/v2/oauth/token/", { method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ client_key: env.TIKTOK_CLIENT_KEY, client_secret: env.TIKTOK_CLIENT_SECRET, ...fields }) });
  return r.json().catch(() => ({ error: "http_" + r.status }));
}

async function saveTokens(env, t, user) {
  const old = (await env.TB.get("token", "json")) || {};
  const rec = { open_id: t.open_id || old.open_id, access_token: t.access_token, refresh_token: t.refresh_token,
    expires_at: now() + Number(t.expires_in || 7200), refresh_expires_at: now() + Number(t.refresh_expires_in || 15552000),
    scope: t.scope, display_name: (user && user.display_name) || old.display_name,
    avatar_url: (user && user.avatar_url) || old.avatar_url, updated: now() };
  await env.TB.put("token", JSON.stringify(rec));
  return rec;
}

async function accessToken(env) {
  const rec = await env.TB.get("token", "json");
  if (!rec) throw new Error("TikTok is not connected yet");
  if (rec.expires_at - 120 > now()) return rec.access_token;
  const t = await tiktokForm(env, { grant_type: "refresh_token", refresh_token: rec.refresh_token });
  if (!t.access_token) throw new Error("TikTok refused to refresh the connection: " + (t.error_description || t.error));
  return (await saveTokens(env, t)).access_token;  // TikTok rotates the refresh token: keep the new one
}

// ---------- sessions ----------
async function hmac(env, value) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(env.TIKTOK_CLIENT_SECRET),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(value));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function makeSession(env, openId) {
  const exp = String(now() + 7 * 86400);
  return `${encodeURIComponent(openId)}|${exp}|${await hmac(env, openId + "|" + exp)}`;
}

async function sessionOpenId(request, env) {
  const s = cookies(request).s;
  if (!s || !env.TIKTOK_CLIENT_SECRET) return null;
  const [id, exp, sig] = s.split("|");
  const openId = decodeURIComponent(id || "");
  if (!sig || Number(exp) < now()) return null;
  return safeEqual(sig, await hmac(env, openId + "|" + exp)) ? openId : null;
}

async function ownerSession(request, env) {
  const id = await sessionOpenId(request, env);
  const owner = await env.TB.get("owner", "json");
  return id && owner && owner.open_id === id ? id : null;
}

// ---------- pages ----------
const CSS = `body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#fffaf0;color:#222}
main{max-width:760px;margin:0 auto;padding:24px 16px 48px}h1{font-size:1.6em;margin:.2em 0}
.btn{display:inline-block;background:#111;color:#fff;border:0;border-radius:8px;padding:12px 18px;font-size:1em;text-decoration:none;cursor:pointer}
.btn:disabled{opacity:.5}.btn.light{background:#eee;color:#111}
.card{background:#fff;border:1px solid #eadfcf;border-radius:12px;padding:16px;margin:14px 0}
.who{display:flex;align-items:center;gap:12px}.who img{width:48px;height:48px;border-radius:50%}
textarea{width:100%;box-sizing:border-box;min-height:70px;font:inherit;padding:8px;border-radius:8px;border:1px solid #ccc}
.muted{color:#666;font-size:.92em}.st{font-weight:600}footer{margin-top:32px}footer a{color:#b3541e;margin-right:14px}.err{background:#fdecea;border-color:#f5c2c0}`;

function page(env, body) {
  const legal = env.LEGAL_URL || "";
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tea Break Uploader</title><style>${CSS}</style></head><body><main><h1>☕ Tea Break Uploader</h1>${body}
<footer class="muted"><a href="${legal}/">About</a><a href="${legal}/terms.html">Terms of Service</a><a href="${legal}/privacy.html">Privacy Policy</a></footer>
</main></body></html>`;
}

async function home(env, openId, msg) {
  if (!env.TIKTOK_CLIENT_KEY || !env.TIKTOK_CLIENT_SECRET) {
    return page(env, '<div class="card err">Setup needed: add the secrets TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET in this Worker\'s settings.</div>');
  }
  const note = msg ? `<div class="card err">${esc(msg)}</div>` : "";
  const owner = await env.TB.get("owner", "json");
  if (!openId || !owner || owner.open_id !== openId) {
    return page(env, note + `<p>Send your finished Tea Break videos to your TikTok account as drafts, then post them from the TikTok app.</p>
<div class="card"><p><a class="btn" href="/login">Connect with TikTok</a></p>
<p class="muted">You sign in on TikTok's own page. The app only asks to see your basic profile (name and picture) and to send
videos to your TikTok inbox as drafts. Nothing is posted until you post it yourself in TikTok.</p></div>`);
  }
  const tok = (await env.TB.get("token", "json")) || {};
  const who = `<div class="card who">${tok.avatar_url ? `<img src="${esc(tok.avatar_url)}" alt="">` : ""}
<div><div>Connected to TikTok as <b>${esc(tok.display_name || "your account")}</b></div>
<div class="muted"><a href="/logout">Sign out of this page</a></div></div></div>`;
  const list = await env.TB.list({ prefix: "q:" });
  const rows = [];
  for (const k of list.keys) {
    const name = k.name.slice(2);
    const it = (await env.TB.get(k.name, "json")) || {};
    let sent = await env.TB.get("sent:" + name, "json");
    let note = "", canSend = !sent;
    if (!sent) {
      const job = await checkJob(env, name).catch((e) => ({ state: "failed", reason: String(e.message || e) }));
      if (job.state === "inbox") { sent = { at: job.at }; canSend = false; }
      else if (job.state === "processing") { note = "⏳ TikTok is still processing this video. Reload this page in a minute."; canSend = false; }
      else if (job.state === "uploading" && now() - job.at < 600) { note = "⏳ Sending to TikTok…"; canSend = false; }
      else if (job.state === "uploading") note = "The last try was interrupted. You can send it again.";
      else if (job.state === "failed") note = "❌ The last try failed: " + job.reason + ". You can send it again.";
    }
    const n = esc(name);
    rows.push(`<div class="card"><div><b>${esc(it.title || name)}</b> <span class="muted">(${Math.round((it.size || 0) / 1048576)} MB)</span></div>
<p class="muted">Caption to paste in TikTok:</p><textarea readonly id="c-${n}">${esc(it.caption || "")}</textarea>
<p><button class="btn light" onclick="copyCap('${n}', this)">Copy caption</button>
${canSend ? `<button class="btn" id="b-${n}" onclick="go('${n}')">Send to TikTok</button>` : ""}</p>
<div class="st" id="s-${n}">${esc(note)}</div>${sent ? `<div class="st">✅ Sent to your TikTok inbox on ${new Date(sent.at * 1000).toDateString()}. Open TikTok, tap the notification, paste the caption and post.</div>` : ""}</div>`);
  }
  const vids = rows.join("") || '<div class="card muted">No videos are waiting. New videos appear here when they are ready.</div>';
  const script = `<script>
function copyCap(n,b){navigator.clipboard.writeText(document.getElementById('c-'+n).value);b.textContent='Copied'}
async function go(n){const b=document.getElementById('b-'+n),s=document.getElementById('s-'+n);b.disabled=true;s.textContent='Starting';
 const r=await fetch('/send',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'name='+encodeURIComponent(n)});
 if(!r.ok){s.textContent=await r.text();b.disabled=false;return}
 const rd=r.body.getReader(),dec=new TextDecoder();let buf='';
 for(;;){const {value,done}=await rd.read();if(done)break;buf+=dec.decode(value,{stream:true});
  const lines=buf.split('\\n');buf=lines.pop();for(const l of lines){if(!l)continue;
   if(l.startsWith('DONE ')){s.textContent='✅ '+l.slice(5);b.remove()}else if(l.startsWith('FAILED ')){s.textContent='❌ '+l.slice(7);b.disabled=false}else s.textContent=l}}}
</script>`;
  return page(env, note + who + "<h2>Videos ready for TikTok</h2>" + vids +
    '<p class="muted">After you send a video, TikTok puts it in your inbox. Open TikTok, tap the notification, paste the caption, choose who can see it, and post.</p>' + script);
}

// ---------- helpers ----------
const now = () => Math.floor(Date.now() / 1000);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const html = (body, status = 200) => new Response(body, { status, headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" } });
const text = (body, status = 200) => new Response(body, { status, headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" } });
const redirect = (to, headers = []) => { const h = new Headers({ Location: to }); for (const [k, v] of headers) h.append(k, v); return new Response(null, { status: 302, headers: h }); };
function cookies(request) {
  const out = {};
  for (const part of (request.headers.get("Cookie") || "").split(";")) {
    const i = part.indexOf("=");
    if (i > 0) out[part.slice(0, i).trim()] = part.slice(i + 1).trim();
  }
  return out;
}
function randomToken() { const b = new Uint8Array(24); crypto.getRandomValues(b); return [...b].map((x) => x.toString(16).padStart(2, "0")).join(""); }
function safeEqual(a, b) { if (a.length !== b.length) return false; let d = 0; for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i); return d === 0; }
