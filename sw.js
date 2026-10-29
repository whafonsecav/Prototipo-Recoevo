/* Guarda todo en la tablet para que el prototipo funcione sin internet en el evento. */
const VERSION = "recoevo-cache-5";
const ARCHIVOS = [
  "./", "index.html", "manifest.webmanifest", "assets/css/app.css",
  "assets/vendor/three.min.js", "assets/js/partes.js", "assets/js/glb.js", "assets/js/controles.js", "assets/js/app.js",
  "assets/fonts/Lexend.woff2", "assets/fonts/Nunito.woff2", "assets/modelo/recoevo.glb",
  "assets/img/logo.svg", "assets/img/isotipo.svg", "assets/img/icono-192.png", "assets/img/icono-512.png",
  ...["olor", "filtro", "reciclado", "seguro", "balde", "pedal", "aserrin", "flecha", "ciclo", "cuchillas", "tiras", "check"]
    .map(i => `assets/img/iconos/icono_${i}.svg`)
];
self.addEventListener("install", e => e.waitUntil(caches.open(VERSION).then(c => c.addAll(ARCHIVOS)).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k))))
  .then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || e.request.url.includes("/video/")) return;   // los videos van directo por la red
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(resp => {
    const copia = resp.clone();
    caches.open(VERSION).then(c => c.put(e.request, copia));
    return resp;
  }).catch(() => caches.match("index.html"))));
});
