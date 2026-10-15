// Service worker of the QR File sender page (web/qrsend.html).
//
// The page needs no network at all once it is loaded, thus the worker keeps
// the four files of the application in a cache and the page also works
// offline. Every path is relative to this file: the four files can be in
// any folder of any web server, and the worker controls that folder only.
//
// APP_VERSION must be the version of the VERSION file (the test gate checks
// it). Each release thus changes this file, the browser installs the new
// worker, and the new worker fills a new cache.
const APP_VERSION = "26.10.6";
const CACHE_PREFIX = "qrfile-web-";
const CACHE_NAME = CACHE_PREFIX + "v" + APP_VERSION;

const FILES = ["qrsend.html", "qrcodegen.js", "manifest.json"];
const PAGE = "qrsend.html";

const url = (path) => new URL(path, self.registration.scope).href;

// A server that is frozen or behind a dead link can accept a connection and
// never answer. fetch() has no timeout of its own: without one, a
// network-first worker waits forever and the page never opens. After one
// timeout, the worker stops asking the network for a while.
const NAV_TIMEOUT_MS = 1500;
const NET_TIMEOUT_MS = 3000;
const DEAD_FOR_MS = 30000;
let deadUntil = 0;

function fetchOrTimeout(request, ms) {
  const control = new AbortController();
  const timer = setTimeout(() => control.abort(), ms);
  return fetch(request, { signal: control.signal }).then(
    (res) => { clearTimeout(timer); deadUntil = 0; return res; },
    (err) => { clearTimeout(timer); deadUntil = Date.now() + DEAD_FOR_MS; throw err; }
  );
}

async function fillCache() {
  const cache = await caches.open(CACHE_NAME);
  for (const f of FILES) {
    const res = await fetchOrTimeout(new Request(url(f), { cache: "no-store" }), NET_TIMEOUT_MS);
    if (!res.ok) throw new Error("precache: " + f + " failed with " + res.status);
    await cache.put(url(f), res);
  }
  return (await cache.keys()).length;
}

// No catch: when the install fails (offline, server error), the browser
// keeps the running worker and its complete cache, and tries again later.
self.addEventListener("install", (event) => {
  event.waitUntil(fillCache().then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    if ((await cache.keys()).length >= FILES.length) {
      const names = await caches.keys();
      await Promise.all(names
        .filter((n) => n.startsWith(CACHE_PREFIX) && n !== CACHE_NAME)
        .map((n) => caches.delete(n)));
    }
    await self.clients.claim();
  })());
});

// Network first, cache second: while the server answers, the page is always
// the newest copy (a local or LAN server answers far inside the timeout).
// ignoreSearch: "qrsend.html?app=1" (the installed start URL) and
// "qrsend.html" are the same file.
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  let u;
  try { u = new URL(req.url); } catch (e) { return; }
  if (u.origin !== self.location.origin) return;

  const navigating = req.mode === "navigate";
  event.respondWith((async () => {
    const cached = async () => {
      const hit = await caches.match(req, { ignoreSearch: true });
      if (hit || !navigating) return hit;
      return caches.match(url(PAGE));
    };
    if (Date.now() < deadUntil) {
      const hit = await cached();
      if (hit) return hit;
    }
    try {
      const fresh = await fetchOrTimeout(req, navigating ? NAV_TIMEOUT_MS : NET_TIMEOUT_MS);
      if (fresh.ok && fresh.type === "basic" && !u.search && FILES.some((f) => url(f) === u.href)) {
        const copy = fresh.clone();
        caches.open(CACHE_NAME).then((c) => c.put(req, copy)).catch(() => {});
      }
      return fresh;
    } catch (err) {
      const hit = await cached();
      if (hit) return hit;
      return navigating
        ? new Response("<!doctype html><meta charset=utf-8><title>QR File</title>" +
            "<p>QR File is offline and not in the cache yet. Open it once with the server reachable.</p>",
            { headers: { "Content-Type": "text/html; charset=utf-8" } })
        : Response.error();
    }
  })());
});

// The page asks which worker runs and how many files it holds.
self.addEventListener("message", (event) => {
  if (!event.data || event.data.type !== "status") return;
  const port = event.ports && event.ports[0];
  const p = (async () => {
    const cache = await caches.open(CACHE_NAME);
    const files = (await cache.keys()).length;
    if (port) port.postMessage({ type: "status", version: APP_VERSION, files: files, total: FILES.length });
  })();
  if (event.waitUntil) event.waitUntil(p);
});
