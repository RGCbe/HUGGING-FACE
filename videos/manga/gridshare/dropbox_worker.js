// A private drop box for rented GPU machines: they download their inputs from it and upload what they make.
// Every request must carry the secret key as the first part of the path: /KEY/files/NAME. Anything else is a 404.
//   PUT  /KEY/files/NAME   store the request body (up to 25 MiB), kept for 7 days
//   GET  /KEY/files/NAME   read it back
//   GET  /KEY/list?prefix= list the stored names
// Bindings: DROP (KV namespace), DROP_KEY (secret).
export default {
  async fetch(req, env) {
    const parts = new URL(req.url).pathname.split("/").filter(Boolean);
    if (!env.DROP_KEY || parts[0] !== env.DROP_KEY) return new Response("not found", { status: 404 });
    const url = new URL(req.url);
    if (parts[1] === "list" && req.method === "GET") {
      const names = [];
      let cursor;
      do {
        const r = await env.DROP.list({ prefix: url.searchParams.get("prefix") || "", cursor });
        names.push(...r.keys.map((k) => k.name));
        cursor = r.list_complete ? undefined : r.cursor;
      } while (cursor);
      return Response.json(names);
    }
    const name = decodeURIComponent(parts.slice(2).join("/"));
    if (parts[1] !== "files" || !name) return new Response("bad request", { status: 400 });
    if (req.method === "PUT") {
      const body = await req.arrayBuffer();
      if (body.byteLength > 25 * 1024 * 1024) return new Response("too big", { status: 413 });
      await env.DROP.put(name, body, { expirationTtl: 7 * 86400 });
      return new Response("ok");
    }
    if (req.method === "GET") {
      const v = await env.DROP.get(name, "arrayBuffer");
      return v ? new Response(v) : new Response("none", { status: 404 });
    }
    return new Response("method not allowed", { status: 405 });
  },
};
