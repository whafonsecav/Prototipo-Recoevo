/* RECOEVO · prototipo interactivo para tablet.
   El mismo equipo del video (exportado de Blender). Tocar una pieza abre su ficha; «Separar» despieza el equipo;
   «Cómo funciona» muestra el uso paso a paso; si nadie toca la pantalla, entra en modo vitrina. */
(function () {
  "use strict";
  const T = THREE;
  const $ = s => document.querySelector(s);
  const lienzo = $("#lienzo");
  const suave = x => { x = Math.min(1, Math.max(0, x)); return x * x * x * (x * (x * 6 - 15) + 10); };
  const B2G = v => new T.Vector3(v[0], v[2], -v[1]);      // ejes de Blender → glTF

  // ---------------------------------------------------------------- render y escena
  const render = new T.WebGLRenderer({ canvas: lienzo, antialias: true, alpha: true, powerPreference: "high-performance" });
  render.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  render.outputEncoding = T.sRGBEncoding;
  render.toneMapping = T.ACESFilmicToneMapping;
  render.toneMappingExposure = 1.05;
  render.shadowMap.enabled = true;
  render.shadowMap.type = T.PCFSoftShadowMap;
  const escena = new T.Scene();
  const camara = new T.PerspectiveCamera(32, 1, 0.02, 30);

  function entorno() {                     // estudio suave hecho a mano (como un RoomEnvironment)
    const e = new T.Scene();
    const caja = new T.Mesh(new T.BoxGeometry(10, 6, 10), new T.MeshBasicMaterial({ color: 0xf3efe4, side: T.BackSide }));
    caja.position.y = 3; e.add(caja);
    const panel = (w, h, x, y, z, ry, i) => {
      const m = new T.Mesh(new T.PlaneGeometry(w, h), new T.MeshBasicMaterial({ color: new T.Color(i, i, i * 0.97) }));
      m.position.set(x, y, z); m.rotation.y = ry; m.lookAt(0, 1, 0); e.add(m);
    };
    panel(3.5, 2.2, -3, 3.5, 3, 0, 6);
    panel(3, 2, 3.5, 2.5, 1.5, 0, 3);
    panel(4, 1.5, 0, 5.5, -2, 0, 4);
    panel(2, 4, 0, 2, -4.8, 0, 2);
    const pm = new T.PMREMGenerator(render);
    return pm.fromScene(e, 0.04).texture;
  }
  escena.environment = entorno();
  const sol = new T.DirectionalLight(0xfff3e2, 1.1);
  sol.position.set(-1.6, 3.2, 2.2);
  sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048);
  Object.assign(sol.shadow.camera, { left: -1.2, right: 1.2, top: 1.6, bottom: -0.6, near: 0.5, far: 8 });
  sol.shadow.bias = -0.0004;
  sol.shadow.radius = 6;
  escena.add(sol, new T.HemisphereLight(0xffffff, 0xd9d2bf, 0.35));
  const piso = new T.Mesh(new T.PlaneGeometry(8, 8), new T.ShadowMaterial({ opacity: 0.16 }));
  piso.rotation.x = -Math.PI / 2;
  piso.receiveShadow = true;
  escena.add(piso);

  // ---------------------------------------------------------------- estado
  let modelo = null, N = {};
  const pieza = {};                 // id → definición
  const mallasDe = {};              // id → [mallas]
  const mallaAPieza = new Map();
  const ray = new T.Raycaster();
  let separado = 0, separadoMeta = 0;
  let seleccion = null, enRecorrido = false, ultimoToque = performance.now();
  const orbita = new Orbita(camara, lienzo, new T.Vector3(0, 0.27, 0));
  orbita.radio = 2.0;
  const VISTA_INICIO = { theta: 0.55, phi: 1.2, radio: 2.0, objetivo: new T.Vector3(0, 0.27, 0) };
  const tabla = () => (innerWidth >= innerHeight ? SEPARAR.horizontal : SEPARAR.vertical);
  const SUBE = () => (innerWidth >= innerHeight ? 0.18 : 0.26);
  const ORDEN = ["G_tapa", "G_gabinete", "G_puerta", "G_balde", "G_base", "G_patas", "G_pedal_der", "G_pedal_izq", "G_deposito",
    "G_camara", "G_seguro", "G_peine", "G_eje", "G_perilla", "G_reten_izq", "G_reten_der", "G_pinon", "G_cremallera"];
  const ANG_REPOSO = -12 * Math.PI / 180, ANG_PISADO = 2.4 * Math.PI / 180;

  function tamano() {
    const w = innerWidth, h = innerHeight;
    render.setSize(w, h, false);
    camara.aspect = w / h;
    camara.fov = w >= h ? 30 : 42;
    camara.updateProjectionMatrix();
  }
  addEventListener("resize", tamano);
  tamano();

  // ---------------------------------------------------------------- carga
  cargarGLB("assets/modelo/recoevo.glb", p => { $("#barra i").style.width = (p * 100).toFixed(0) + "%"; })
    .then(({ escena: m, porNombre }) => {
      modelo = m; N = porNombre;
      escena.add(modelo);
      for (const p of PARTES) pieza[p.id] = p;
      // cada malla con su propio material (para resaltar sin afectar a otras piezas)
      modelo.traverse(o => {
        if (!o.isMesh) return;
        o.material = o.material.clone();
        o.material.userData.base = { emis: o.material.emissive.clone(), op: o.material.opacity, tr: o.material.transparent };
        let a = o, id = null;
        while (a && !id) { id = PARTES.find(p => p.nodos.includes(a.name))?.id; a = a.parent; }
        if (id) { mallaAPieza.set(o, id); (mallasDe[id] = mallasDe[id] || []).push(o); }
      });
      reposo();
      crearPuntos();
      $("#carga").classList.add("fuera");
      setTimeout(() => $("#pista").classList.add("visible"), 600);
    })
    .catch(err => { $("#carga p").textContent = "No se pudo cargar el modelo: " + err.message; });

  function reposo() {
    for (const k of ["piv_pedal_der", "piv_pedal_izq"]) if (N[k]) N[k].rotation.x = ANG_REPOSO;
  }

  // ---------------------------------------------------------------- separar / armar
  function aplicarSeparado(e) {
    const t = tabla(), n = ORDEN.length;
    for (const [nombre, v] of Object.entries(t)) {
      const o = N[nombre];
      if (!o) continue;
      const i = ORDEN.indexOf(nombre);
      const k = i < 0 ? suave((e - 0.3) / 0.7) : suave((e - i / n * 0.45) / 0.55);
      o.position.copy(B2G(v).multiplyScalar(k));
      if (v.length > 3) o.rotation.y = v[3] * k;
    }
    if (N.RECOEVO) N.RECOEVO.position.y = SUBE() * suave(e) + 0.02 * suave(e);
  }
  function alternarSeparar() {
    separadoMeta = separadoMeta > 0.5 ? 0 : 1;
    $("#b-separar span").textContent = separadoMeta ? "Armar" : "Separar piezas";
    $("#b-separar").classList.toggle("activo", !!separadoMeta);
    if (!seleccion) orbita.ir({ ...VISTA_INICIO, radio: separadoMeta ? (innerWidth >= innerHeight ? 3.5 : 4.3) : 2.0,
      objetivo: new T.Vector3(0, separadoMeta ? 0.74 : 0.27, 0) }, 1.4);
  }

  // ---------------------------------------------------------------- puntos táctiles sobre las piezas
  const puntos = [];
  function crearPuntos() {
    const capa = $("#puntos");
    for (const p of PARTES) {
      const b = document.createElement("button");
      b.className = "punto";
      b.setAttribute("aria-label", p.titulo);
      b.innerHTML = "<i></i>";
      b.addEventListener("click", ev => { ev.stopPropagation(); abrir(p.id); });
      capa.appendChild(b);
      puntos.push({ b, p });
    }
  }
  const GRANDES = ["tapa", "gabinete", "puerta", "pedal_der", "pedal_izq"];
  const v3 = new T.Vector3();
  function moverPuntos() {
    const w = innerWidth, h = innerHeight;
    for (const { b, p } of puntos) {
      const a = N[p.ancla];
      if (!a) { b.style.display = "none"; continue; }
      a.getWorldPosition(v3).project(camara);
      const vis = (separado > 0.85 || (separado < 0.05 && GRANDES.includes(p.id))) && !enRecorrido && v3.z < 1;
      b.style.transform = `translate(${(v3.x * 0.5 + 0.5) * w}px, ${(-v3.y * 0.5 + 0.5) * h}px)`;
      b.classList.toggle("visible", vis);
    }
  }

  // ---------------------------------------------------------------- elegir pieza
  orbita.alTocar = (x, y) => {
    if (enRecorrido) { pararRecorrido(); return; }
    if (!modelo) return;
    ray.setFromCamera(new T.Vector2(x / innerWidth * 2 - 1, -(y / innerHeight) * 2 + 1), camara);
    const hits = ray.intersectObjects([...mallaAPieza.keys()], false);
    if (hits.length) abrir(mallaAPieza.get(hits[0].object));
  };
  orbita.alInteractuar = () => { ultimoToque = performance.now(); salirVitrina(); $("#pista").classList.remove("visible"); };

  function resaltar(id) {
    modelo.traverse(o => {
      if (!o.isMesh) return;
      const m = o.material, b = m.userData.base;
      const esta = mallaAPieza.get(o) === id;
      m.emissive.copy(b.emis);
      if (id && esta) m.emissive.set(0x1d6b3f).multiplyScalar(0.35);
      m.transparent = b.tr || (id && !esta);
      m.opacity = id && !esta ? Math.min(b.op, 0.22) : b.op;
      m.depthWrite = !(m.transparent);
    });
  }

  function abrir(id) {
    const p = pieza[id];
    if (!p) return;
    seleccion = id;
    $("#pista").classList.remove("visible");
    ultimoToque = performance.now();
    salirVitrina();
    resaltar(id);
    const a = N[p.ancla];
    if (a) {
      const pos = a.getWorldPosition(new T.Vector3());
      orbita.ir({ theta: orbita.theta, phi: Math.min(1.35, Math.max(0.9, orbita.phi)), radio: separado > 0.5 ? 1.7 : 1.4, objetivo: pos }, 0.9);
    }
    const i = PARTES.indexOf(p);
    $("#modal-icono").src = `assets/img/iconos/icono_${p.icono}.svg`;
    $("#modal-n").textContent = `${i + 1} / ${PARTES.length}`;
    $("#modal-titulo").textContent = p.titulo;
    $("#modal-corto").textContent = p.corto;
    $("#modal-texto").textContent = p.texto;
    $("#modal-datos").innerHTML = p.datos.map(d => `<li>${d}</li>`).join("");
    document.body.classList.add("con-modal");
  }
  function cerrar() {
    seleccion = null;
    resaltar(null);
    document.body.classList.remove("con-modal");
    orbita.ir({ theta: orbita.theta, phi: 1.2, radio: separado > 0.5 ? (innerWidth >= innerHeight ? 3.5 : 4.3) : 2.0,
      objetivo: new T.Vector3(0, separado > 0.5 ? 0.74 : 0.27, 0) }, 0.9);
  }
  function vecina(d) {
    const i = PARTES.findIndex(p => p.id === seleccion);
    abrir(PARTES[(i + d + PARTES.length) % PARTES.length].id);
  }
  $("#modal-cerrar").addEventListener("click", cerrar);
  $("#velo").addEventListener("click", cerrar);
  $("#modal-sig").addEventListener("click", () => vecina(1));
  $("#modal-ant").addEventListener("click", () => vecina(-1));
  addEventListener("keydown", e => {
    if (e.key === "Escape") cerrar();
    if (seleccion && e.key === "ArrowRight") vecina(1);
    if (seleccion && e.key === "ArrowLeft") vecina(-1);
  });

  // ---------------------------------------------------------------- cómo funciona (recorrido animado)
  let rec = null;
  function fantasma(on) {
    for (const id of ["gabinete", "puerta", "tapa", "base", "balde", "camara"]) for (const o of mallasDe[id] || []) {
      const b = o.material.userData.base;
      o.material.transparent = on || b.tr;
      o.material.opacity = on ? (id === "camara" ? 0.35 : 0.16) : b.op;
      o.material.depthWrite = !on;
    }
  }
  function empezarRecorrido() {
    if (seleccion) cerrar();
    separadoMeta = 0;
    $("#b-separar span").textContent = "Separar piezas";
    $("#b-separar").classList.remove("activo");
    enRecorrido = true;
    rec = { t: 0, cues: new Set() };
    document.body.classList.add("con-recorrido");
    orbita.ir({ theta: 0.75, phi: 1.12, radio: 1.75, objetivo: new T.Vector3(0, 0.27, 0) }, 1.0);
  }
  function pararRecorrido() {
    enRecorrido = false;
    rec = null;
    fantasma(false);
    for (const k of ["piv_tapa", "rot_pinon", "rot_dosif", "rot_eje", "rot_trinquete", "rot_perilla"]) if (N[k]) N[k].rotation.x = 0;
    if (N.piv_puerta) N.piv_puerta.rotation.y = 0;
    if (N.corr_balde) N.corr_balde.position.z = 0;
    if (N.corr_cremallera) N.corr_cremallera.position.y = 0;
    if (N.corr_seguro) N.corr_seguro.position.y = 0;
    reposo();
    document.body.classList.remove("con-recorrido");
  }
  const pisada = (t, t0) => {                 // ángulo del pedal en una pisada (bajar 0,3 s, sostener, subir)
    const k = t < t0 ? 0 : t < t0 + 0.3 ? suave((t - t0) / 0.3) : t < t0 + 0.42 ? 1 : 1 - suave((t - t0 - 0.42) / 0.33);
    return ANG_REPOSO + (ANG_PISADO - ANG_REPOSO) * k;
  };
  const dzCrem = th => 0.12 * (Math.sin(-th) - Math.sin(-ANG_REPOSO));
  function pasoRecorrido(dt) {
    rec.t += dt;
    const t = rec.t;
    const paso = t < 4.5 ? 0 : t < 10 ? 1 : t < 14 ? 2 : t < 20 ? 3 : 4;
    if (paso >= 4) { pararRecorrido(); orbita.ir(VISTA_INICIO, 1.2); return; }
    $("#recorrido-texto").textContent = PASOS[paso].texto;
    document.querySelectorAll("#recorrido-pasos i").forEach((e, i) => e.classList.toggle("on", i <= paso));
    // 1 · tapa
    const tapa = suave((t - 0.4) / 0.9) * (1 - suave((t - 4.0) / 0.7));
    if (N.piv_tapa) N.piv_tapa.rotation.x = -80 * Math.PI / 180 * tapa;
    if (N.corr_seguro) N.corr_seguro.position.y = -0.010 * tapa;
    // 2 · pedal derecho con rayos X
    fantasma(t > 5.0 && t < 14.0);
    const pd = [5.6, 6.5, 7.4, 8.3];
    let th = ANG_REPOSO;
    for (const p0 of pd) if (t >= p0 && t < p0 + 0.9) th = pisada(t, p0);
    if (N.piv_pedal_der) N.piv_pedal_der.rotation.x = th;
    const dz = dzCrem(th);
    if (N.corr_cremallera) N.corr_cremallera.position.y = dz;
    if (N.rot_pinon) N.rot_pinon.rotation.x = -dz / 0.012;
    let giro = 0;
    for (const p0 of pd) if (t >= p0) giro += t < p0 + 0.3 ? -dzCrem(pisada(t, p0)) / 0.012 : 0.030 / 0.012;
    for (const k of ["rot_eje", "rot_trinquete", "rot_perilla"]) if (N[k]) N[k].rotation.x = giro;
    // 3 · pedal izquierdo y dosificador
    if (N.piv_pedal_izq) N.piv_pedal_izq.rotation.x = t >= 11 && t < 12 ? pisada(t, 11) : ANG_REPOSO;
    if (N.rot_dosif) N.rot_dosif.rotation.x = Math.PI / 2 * suave((t - 11) / 0.32);
    // 4 · puerta y balde
    const pu = suave((t - 14.4) / 1.0) * (1 - suave((t - 18.6) / 0.9));
    if (N.piv_puerta) N.piv_puerta.rotation.y = -100 * Math.PI / 180 * pu;
    if (N.corr_balde) N.corr_balde.position.z = 0.15 * suave((t - 15.3) / 0.9) * (1 - suave((t - 17.8) / 0.8));
    // cámara
    const cue = (t0, vista) => { if (t >= t0 && !rec.cues.has(t0)) { rec.cues.add(t0); orbita.ir(vista, 1.0); } };
    cue(4.6, { theta: 0.85, phi: 1.32, radio: 1.65, objetivo: new T.Vector3(0.02, 0.22, 0) });
    cue(10.2, { theta: -0.65, phi: 1.32, radio: 1.65, objetivo: new T.Vector3(-0.04, 0.22, 0) });
    cue(14.1, { theta: 0.3, phi: 1.28, radio: 1.55, objetivo: new T.Vector3(0, 0.2, 0.05) });
  }

  // ---------------------------------------------------------------- vitrina (nadie toca la pantalla)
  let vitrina = false, tVitrina = 0;
  function salirVitrina() {
    if (!vitrina) return;
    vitrina = false;
    document.body.classList.remove("vitrina");
  }

  // ---------------------------------------------------------------- botones
  $("#b-separar").addEventListener("click", () => { ultimoToque = performance.now(); salirVitrina(); if (enRecorrido) pararRecorrido(); alternarSeparar(); });
  $("#b-funciona").addEventListener("click", () => { ultimoToque = performance.now(); salirVitrina(); enRecorrido ? pararRecorrido() : empezarRecorrido(); });
  $("#b-centrar").addEventListener("click", () => { ultimoToque = performance.now(); salirVitrina(); if (seleccion) cerrar(); orbita.ir({ ...VISTA_INICIO,
    radio: separadoMeta ? (innerWidth >= innerHeight ? 3.5 : 4.3) : 2.0, objetivo: new T.Vector3(0, separadoMeta ? 0.74 : 0.27, 0) }, 1.0); });
  document.querySelectorAll(".dock .boton").forEach(b => b.addEventListener("click", () => $("#pista").classList.remove("visible")));

  // ---------------------------------------------------------------- bucle
  let antes = performance.now();
  function cuadro(ahora) {
    const dt = Math.min(0.1, (ahora - antes) / 1000);
    antes = ahora;
    if (modelo) {
      separado += (separadoMeta - separado) * Math.min(1, dt * 2.2);
      if (Math.abs(separadoMeta - separado) < 0.001) separado = separadoMeta;
      aplicarSeparado(separado);
      if (enRecorrido && rec) pasoRecorrido(dt);
      // vitrina: tras 35 s sin tocar, gira sola y se arma / separa cada 9 s
      if (!vitrina && !seleccion && !enRecorrido && ahora - ultimoToque > 35000) {
        vitrina = true; tVitrina = 0; document.body.classList.add("vitrina");
      }
      if (vitrina) {
        tVitrina += dt;
        if (tVitrina > 9) { tVitrina = 0; alternarSeparar(); }
      }
      moverPuntos();
    }
    orbita.actualizar(dt, vitrina);
    render.render(escena, camara);
    requestAnimationFrame(cuadro);
  }
  requestAnimationFrame(cuadro);
  window.__rv = { orbita, camara, get separado() { return separado; } };   // para depurar desde la consola

  // ---------------------------------------------------------------- sin conexión (para el evento)
  const local = ["localhost", "127.0.0.1"].includes(location.hostname);
  if ("serviceWorker" in navigator && location.protocol !== "file:" && !local) navigator.serviceWorker.register("sw.js").catch(() => {});
})();
