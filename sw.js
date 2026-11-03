/* RECOEVO · funcionamiento sin conexión.
   Primero la red (siempre lo más nuevo); si no hay internet, lo guardado. Los videos van siempre directo por la red. */
const VERSION = "recoevo-web-1";
const BASICOS = [
  "./", "index.html", "manifest.webmanifest", "assets/css/marca.css", "assets/css/prototipo.css",
  "assets/fonts/Lexend.woff2", "assets/fonts/Nunito.woff2", "assets/img/logo.svg", "assets/img/logo-negativo.svg",
  "assets/img/isotipo.svg", "assets/img/icono-192.png",
  "prototipo/", "assets/vendor/three.min.js", "assets/modelo/recoevo.glb",
  ...["partes", "glb", "controles", "app"].map(n => `assets/js/prototipo/${n}.js`),
  ...["olor", "filtro", "reciclado", "seguro", "balde", "pedal", "material_seco", "flecha", "ciclo", "cuchillas", "tiras", "check"]
    .map(i => `assets/img/iconos/icono_${i}.svg`)
];
self.addEventListener("install", e => e.waitUntil(caches.open(VERSION).then(c => c.addAll(BASICOS)).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys()
  .then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k))))
  .then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  const r = e.request, url = new URL(r.url);
  if (r.method !== "GET" || url.origin !== location.origin || /\.(mp4|mp3)$/i.test(url.pathname) || r.headers.has("range")) return;
  e.respondWith(fetch(r).then(resp => {
    if (resp.ok && resp.type === "basic") { const copia = resp.clone(); caches.open(VERSION).then(c => c.put(r, copia)); }
    return resp;
  }).catch(() => caches.match(r).then(g => g || (r.mode === "navigate" ? caches.match("./") : Response.error()))));
});
