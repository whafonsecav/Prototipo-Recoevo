/* RECOEVO · página del presupuesto realista.
   Dibuja las tablas del presupuesto ejecutivo (presupuesto/datos.js, generado desde el Excel) con la misma agrupación con
   la que se guardó el libro. Todo el detalle se abre con + / − en la misma tabla; la «i» solo explica qué es cada cosa. */
(function () {
  "use strict";
  const P = window.PRESUPUESTO;
  const $ = (s, r = document) => r.querySelector(s);
  const MILLON = 1e6;
  const estado = { pesos: false, abiertos: new Map(), inicial: new Map() };
  const filas = new Map();        // id → { f, tabla, padre, el }
  const tipoNivel = new Map();    // id de fila que se abre → 0 (total de tabla) o 1+ (rubro con detalle)
  const toggles = new Map();      // id → botones + / −
  const dependientes = [];        // { el, padres }: se esconde si algún padre está cerrado
  const numeros = [];             // cifras que cambian con «Pesos completos»

  if (!P) { $("#tablas").textContent = "No se pudo cargar el presupuesto."; return; }

  // ---------------------------------------------------------------- números (formato colombiano: 1.234.567,8)
  function miles(n, dec = 0) {
    const [e, d] = Math.abs(n).toFixed(dec).split(".");
    return e.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (d ? "," + d : "");
  }

  function fmt(v, k, opc = {}) {
    if (v === null || v === undefined || v === "") return "—";
    if (typeof v === "string") return v;
    const menos = v < 0 ? "−" : "";
    if (k === "$" || k === "$s") {
      const a = Math.abs(v);
      if (a > 0 && a < 0.5) return "menos de $1";
      const t = !estado.pesos && !opc.completo && a >= MILLON
        ? "$" + miles(a / MILLON, a >= 100 * MILLON ? 0 : 1) + " M"
        : "$" + miles(a);
      return k === "$s" ? (v < 0 ? "▼ " : "▲ ") + t : menos + t;
    }
    if (k && k[0] === "%") return menos + miles(Math.abs(v) * 100, opc.dec ?? +k.slice(1)) + " %";
    if (k === "mes") return "mes " + miles(v);
    if (k === "n1") return menos + miles(v, 1);
    return menos + miles(v);
  }

  function num(e, v, k, opc) {
    e.textContent = fmt(v, k, opc);
    if (typeof v === "number") {
      if (k === "$s") e.classList.add(v < 0 ? "neg" : "pos");
      else if (v < 0) e.classList.add("menos");
      if (k === "$" || k === "$s") numeros.push({ e, v, k, opc });
    }
    return e;
  }

  function repintar() { for (const n of numeros) n.e.textContent = fmt(n.v, n.k, n.opc); }

  function el(tag, attrs = {}, ...hijos) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v === undefined || v === null || v === false) continue;
      if (k === "class") e.className = v;
      else e.setAttribute(k, v === true ? "" : v);
    }
    for (const h of hijos.flat()) if (h !== null && h !== undefined && h !== false) e.append(h.nodeType ? h : String(h));
    return e;
  }

  const sufijo = u => ({ "años": " años", "% al año": " al año" })[u] || "";
  const conUnidad = u => u && !sufijo(u) && !["%", "pesos", "mes", "productos"].includes(u);
  const unidadCorta = u => u.replace(/^pesos\s*/, "");
  const tieneInfo = f => !!(f.que || f.espec || f.porque);

  // si todo el valor cae en un solo año (como las compras del año 0), no hay promedio por año
  function soloUnAnio(f) {
    if (!f.anios) return null;
    const con = f.anios.map((v, i) => [v, i]).filter(([v]) => v && Math.abs(v) >= 0.5);
    return con.length === 1 ? con[0][1] : null;
  }

  // ---------------------------------------------------------------- agrupar y desagrupar
  function registrar(f, tabla, padre, elemento) { filas.set(f.id, { f, tabla, padre, el: elemento }); }

  function abrible(id, abierto, nivel) {
    estado.abiertos.set(id, !!abierto);
    estado.inicial.set(id, !!abierto);
    tipoNivel.set(id, nivel);
  }

  function botonToggle(id, nombre) {
    const b = el("button", { type: "button", class: "tg", "data-tg": id, "data-nombre": nombre }, el("span", { "aria-hidden": "true" }));
    if (!toggles.has(id)) toggles.set(id, []);
    toggles.get(id).push(b);
    return b;
  }

  function botonInfo(f, nombre) {
    return tieneInfo(f) ? el("button", { type: "button", class: "info", "data-info": f.id, "aria-label": "Qué es: " + nombre }, "i") : null;
  }

  function aplicar() {
    for (const d of dependientes) d.el.hidden = !d.padres.every(id => estado.abiertos.get(id));
    for (const [id, bs] of toggles) {
      const ab = !!estado.abiertos.get(id);
      for (const b of bs) {
        b.setAttribute("aria-expanded", ab);
        b.firstChild.textContent = ab ? "−" : "+";
        b.setAttribute("aria-label", (ab ? "Agrupar " : "Desagrupar ") + b.dataset.nombre);
      }
    }
    marcarNivel();
  }

  function preset(n) {
    const m = new Map();
    for (const [id, nv] of tipoNivel) m.set(id, n === "excel" ? estado.inicial.get(id) : n === "1" ? false : n === "2" ? nv === 0 : true);
    return m;
  }

  function marcarNivel() {
    let marcado = false;
    for (const b of document.querySelectorAll("[data-nivel]")) {
      const igual = !marcado && [...preset(b.dataset.nivel)].every(([k, v]) => !!estado.abiertos.get(k) === !!v);
      b.setAttribute("aria-pressed", igual);
      if (igual) marcado = true;
    }
  }

  function nivel(n) { estado.abiertos = preset(n); aplicar(); }
  function alternar(id) { estado.abiertos.set(id, !estado.abiertos.get(id)); aplicar(); }

  // abre lo necesario para que se vea una fila, la muestra y la marca un momento
  function ir(id) {
    const r = filas.get(id);
    if (!r) return;
    for (let p = r.padre; p; p = filas.get(p).padre) estado.abiertos.set(p, true);
    if (tipoNivel.has(id)) estado.abiertos.set(id, true);
    aplicar();
    r.el.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
    r.el.classList.remove("resaltar");
    void r.el.offsetWidth;
    r.el.classList.add("resaltar");
  }

  // ---------------------------------------------------------------- tablas que suman (1 a 11)
  const COLS = [["c-can", "Cantidad (10 años)"], ["c-uni", "Unidad"], ["c-pre", "Precio de cada unidad"],
                ["c-tot", "Total 10 años"], ["c-pro", "Promedio por año"], ["c-pp", "Por producto"]];

  function cabAnios() { return P.anios.map((a, i) => el("th", { scope: "col", class: "c-an", title: a }, "Año " + i)); }

  function tablaSuma(t) {
    const f = t.fila;
    const info = { num: f.num, titulo: f.titulo };
    const cuerpo = el("tbody");
    const fila = (x, nv, padres) => {
      const kids = x.hijos && x.hijos.length;
      const nombre = nv === 0 ? x.titulo : x.nombre;
      if (kids) abrible(x.id, x.abierto, nv);
      const det = x.cant && x.precio && conUnidad(x.unidad)
        ? el("span", { class: "det" }, `${fmt(...x.cant)} ${x.unidad} × ${fmt(...x.precio, { completo: true })}`) : null;
      const tr = el("tr", { class: `n${Math.min(nv, 3)} ${x.color || ""}`, "data-tg": kids ? x.id : null },
        el("th", { scope: "row", class: "c-con" }, el("div", { class: "con" },
          kids ? botonToggle(x.id, nombre) : el("span", { class: "tg-hueco", "aria-hidden": "true" }),
          nv === 0 ? el("span", { class: "num", "aria-label": "Tabla " + x.num }, x.num) : null,
          el("span", { class: "nom" }, nombre, botonInfo(x, nombre), det))));
      const solo = soloUnAnio(x);
      const reparto = x.unidad === "productos";     // «735.450 productos × costo por producto» repite la columna Por producto
      for (const [c] of COLS) {
        const td = el("td", { class: c });
        if (reparto && (c === "c-can" || c === "c-uni" || c === "c-pre")) { tr.append(td); continue; }
        if (c === "c-uni") td.textContent = x.cant ? x.unidad || "" : "";
        else if (c === "c-pro" && solo !== null && x.total) td.append(el("span", { class: "solo" }, "solo en el año " + solo));
        else {
          const p = { "c-can": x.cant, "c-pre": x.precio, "c-tot": x.total, "c-pro": x.prom, "c-pp": x.pp }[c];
          if (p) num(td, ...p);
          else if (c === "c-pp") td.textContent = "—";
        }
        tr.append(td);
      }
      P.anios.forEach((_, i) => {
        const td = el("td", { class: "c-an" });
        if (x.anios && x.anios[i] !== null) num(td, x.anios[i], x.tanios);
        tr.append(td);
      });
      registrar(x, info, padres[padres.length - 1], tr);
      if (padres.length) dependientes.push({ el: tr, padres: [...padres] });
      cuerpo.append(tr);
      (x.hijos || []).forEach(h => fila(h, nv + 1, [...padres, x.id]));
    };
    fila(f, 0, []);
    const cab = el("tr", {}, el("th", { scope: "col", class: "c-con" }, "Concepto"),
      COLS.map(([c, txt]) => el("th", { scope: "col", class: c }, txt)), cabAnios());
    const tabla = el("table", { class: "t-suma" }, el("caption", { class: "sr" }, `Tabla ${f.num}: ${f.titulo}`), el("thead", {}, cab), cuerpo);
    return el("section", { class: "tabla", id: "tabla-" + f.num },
      el("div", { class: "desliza", role: "region", "aria-label": `Tabla ${f.num}` }, tabla),
      t.nota ? el("p", { class: "nota-tabla" }, t.nota.replace(/^Nota de la tabla \d+:\s*/, "")) : null);
  }

  // ---------------------------------------------------------------- tablas de cálculo paso a paso (12 a 14)
  function veredicto(t) { return /^NO\b/.test(t || "") ? "no" : /^S[ÍI]\b/.test(t || "") ? "si" : ""; }

  function valorCalc(x, clase) {
    const p = el("p", { class: clase });
    p.append(num(el("b"), x.valor ? x.valor[0] : null, x.valor ? x.valor[1] : null));
    if (conUnidad(x.unidad)) p.append(el("small", {}, " " + unidadCorta(x.unidad)));
    return p;
  }

  function tablaCalculo(t) {
    const f = t.fila;
    const info = { num: f.num, titulo: f.titulo };
    if (f.hijos.length) abrible(f.id, f.abierto, 0);
    const cab = el("div", { class: `calc-cab ${f.color || ""}`, "data-tg": f.hijos.length ? f.id : null },
      el("div", { class: "calc-titulo" },
        f.hijos.length ? botonToggle(f.id, f.titulo) : null,
        el("span", { class: "num", "aria-label": "Tabla " + f.num }, f.num),
        el("h4", {}, f.titulo, botonInfo(f, f.titulo))),
      el("div", { class: "calc-res" },
        el("p", { class: "calc-nombre" }, f.nombre.replace(/^RESULTADO:\s*/, "")),
        valorCalc(f, "calc-valor"),
        f.palabras ? el("p", { class: "calc-palabras " + veredicto(f.palabras) }, f.palabras) : null));
    registrar(f, info, null, cab);
    const pasos = el("ol", { class: "pasos" });
    for (const h of f.hijos) {
      const li = el("li", { class: `paso ${h.color || ""}` },
        el("span", { class: "nom" }, h.nombre, botonInfo(h, h.nombre)),
        valorCalc(h, "paso-valor"),
        h.palabras ? el("span", { class: "paso-palabras " + veredicto(h.palabras) }, h.palabras) : null);
      registrar(h, info, f.id, li);
      pasos.append(li);
    }
    dependientes.push({ el: pasos, padres: [f.id] });
    return el("section", { class: "tabla calc", id: "tabla-" + f.num, "aria-label": `Tabla ${f.num}: ${f.titulo}` }, cab, pasos);
  }

  // ---------------------------------------------------------------- tabla 0 (productos) y 0b (datos del plan)
  function tablaProductos(p) {
    const info = { num: "0", titulo: p.titulo };
    const raiz = { id: p.id, nombre: p.nombre, que: p.que, porque: p.porque };
    abrible(p.id, p.abierto, 0);
    const principal = el("tr", { class: `n0 ${p.color || ""}`, "data-tg": p.id },
      el("th", { scope: "row", class: "c-con" }, el("div", { class: "con" }, botonToggle(p.id, p.nombre),
        el("span", { class: "num", "aria-label": "Tabla 0" }, "0"), el("span", { class: "nom" }, p.nombre, botonInfo(raiz, p.nombre)))),
      el("td", { class: "c-cap" }, "—"), num(el("td", { class: "c-ven" }), ...p.total));
    registrar(raiz, info, null, principal);
    const cuerpo = el("tbody", {}, principal);
    for (const x of p.filas) {
      const tr = el("tr", { class: "n1" },
        el("th", { scope: "row", class: "c-con" }, el("div", { class: "con" }, el("span", { class: "tg-hueco", "aria-hidden": "true" }),
          el("span", { class: "nom" }, x.nombre, botonInfo(x, x.nombre)))),
        num(el("td", { class: "c-cap" }), ...x.cap), num(el("td", { class: "c-ven" }), ...x.vend));
      registrar(x, info, p.id, tr);
      dependientes.push({ el: tr, padres: [p.id] });
      cuerpo.append(tr);
    }
    const tabla = el("table", { class: "t-prod" }, el("caption", { class: "sr" }, "Tabla 0: " + p.titulo),
      el("thead", {}, el("tr", {}, el("th", { scope: "col", class: "c-con" }, "Año"),
        el("th", { scope: "col", class: "c-cap", title: p.cols[0] }, "Capacidad", el("span", { class: "sub-th" }, "al mes")),
        el("th", { scope: "col", class: "c-ven", title: p.cols[1] }, "Vendidos", el("span", { class: "sub-th" }, "en el año")))), cuerpo);
    return el("section", { class: "tabla", id: "tabla-0" }, el("div", { class: "desliza" }, tabla));
  }

  function valorDato(x) {
    if (x.valor) return fmt(...x.valor, { completo: true }) + sufijo(x.unidad);
    if (x.anios) return `${fmt(x.anios[0], x.tanios)} → ${fmt(x.anios[x.anios.length - 1], x.tanios)} en el año 10`;
    return "—";
  }

  function tablaDatos(d) {
    const info = { num: "0b", titulo: d.titulo };
    const cuerpo = el("tbody");
    for (const x of d.filas) {
      const tr = el("tr", { class: "n1" },
        el("th", { scope: "row", class: "c-con" }, el("div", { class: "con" }, el("span", { class: "nom" }, x.nombre, botonInfo(x, x.nombre)))),
        el("td", { class: "c-val" }, valorDato(x)));
      registrar(x, info, null, tr);
      cuerpo.append(tr);
    }
    const tabla = el("table", { class: "t-datos" }, el("caption", { class: "sr" }, "Tabla 0b: " + d.titulo),
      el("thead", {}, el("tr", {}, el("th", { scope: "col", class: "c-con" }, "Dato"), el("th", { scope: "col", class: "c-val" }, "Valor"))), cuerpo);
    return el("section", { class: "tabla", id: "tabla-0b" },
      el("div", { class: "tabla-cab" }, el("span", { class: "num" }, "0b"), el("h4", {}, d.titulo)),
      el("div", { class: "desliza" }, tabla));
  }

  // ---------------------------------------------------------------- «i»: qué es (sin cálculos: las cifras están en la tabla)
  const dlg = $("#ficha"), cuerpoFicha = $("#ficha-cuerpo");

  function abrirInfo(id) {
    const r = filas.get(id);
    if (!r) return;
    const { f, tabla, padre } = r;
    const corto = t => t.replace(/\s*\([^)]*\)\s*$/, "");
    const pf = padre ? filas.get(padre).f : null;
    const ruta = tabla.num === "0b" ? "Datos del plan" : `Tabla ${tabla.num} · ${corto(tabla.titulo)}`;
    $("#ficha-ruta").textContent = pf && filas.get(padre).padre ? `${ruta} › ${corto(pf.nombre)}` : ruta;
    cuerpoFicha.textContent = "";
    cuerpoFicha.append(el("h2", { id: "ficha-titulo" }, (!padre && f.titulo) || f.nombre));
    if (f.que) cuerpoFicha.append(el("h3", {}, "¿Qué es?"), el("p", {}, f.que));
    if (f.espec) cuerpoFicha.append(el("h3", {}, "Especificación"), el("p", {}, f.espec));
    if (f.porque) cuerpoFicha.append(el("h3", {}, "¿De dónde sale?"), el("p", {}, f.porque));
    if (!dlg.open) {
      dlg.showModal();
      document.documentElement.classList.add("con-ficha");
      history.pushState({ ficha: id }, "", "#" + id);
    }
    $("#ficha-cerrar").focus({ preventScroll: true });
  }

  function cerrar(desdeHistoria) {
    if (dlg.open) dlg.close();
    document.documentElement.classList.remove("con-ficha");
    if (!desdeHistoria && history.state && history.state.ficha) history.back();
  }

  // ---------------------------------------------------------------- arriba: tarjetas y resumen ejecutivo
  function tarjetas() {
    const c = P.costo, boton = $("#costo");
    boton.dataset.ir = c.fila;
    boton.append(el("span", { class: "cu-etq" }, "Costo de un producto"), el("span", { class: "cu-valor" }, fmt(...c.valor, { completo: true })),
      el("span", { class: "cu-nota" }, c.nota), el("span", { class: "cu-mas" }, "Ver en la tabla 9 →"));
    const ol = $("#preguntas");
    for (const p of P.preguntas) {
      const [v, k] = p.valor;
      const valor = el("span", { class: "p-valor" });
      if ((k === "$" || k === "$s") && Math.abs(v) >= MILLON) valor.append("$" + miles(v / MILLON), el("small", {}, " millones"));
      else valor.append(k[0] === "%" ? fmt(v, k, { dec: 0 }) : fmt(v, k === "$s" ? "$" : k, { completo: true }));
      if (p.unidad) valor.append(el("small", {}, " " + p.unidad));
      ol.append(el("li", {}, el("button", { type: "button", class: "pregunta" + (p.alerta ? " alerta" : ""), "data-ir": p.fila },
        el("span", { class: "p-num", "aria-hidden": "true" }, p.n), el("span", { class: "p-titulo" }, p.titulo), valor,
        el("span", { class: "p-nota" }, p.nota), p.alerta ? el("span", { class: "p-alerta" }, "✘ No llega a la meta de los socios") : null)));
    }
  }

  function textoConclusion() {
    const [cab, ...resto] = P.conclusion.texto.split(":");
    return el("p", {}, el("b", { class: veredicto(cab) }, cab + ":"), resto.join(":"));
  }

  function resumen() {
    $("#conclusion").append(textoConclusion());
    $("#supone").textContent = P.supone.replace(/^Qué supone:\s*/, "");
    $("#conclusion-final").append(el("h2", {}, "Conclusión final"), textoConclusion());
    const [fecha, hora] = P.fuente.guardado.split(" ");
    const [a, m, d] = fecha.split("-").map(Number);
    const mes = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"][m - 1];
    $("#fuente").textContent = `Fuente: ${P.fuente.archivo}, hoja ${P.fuente.hoja}, guardado el ${d} de ${mes} de ${a} a las ${hora}; ` +
      "el detalle de máquinas, moldes y gastos de arranque sale del plan detallado del mismo escenario. Todo se reparte entre los " +
      miles(P.nprod) + " productos de los 10 años. El Excel trae también los escenarios pesimista y optimista.";
  }

  // ---------------------------------------------------------------- armar la página
  tarjetas();
  resumen();
  const cont = $("#tablas");
  cont.textContent = "";
  cont.append(el("section", { class: "parte", id: "parte-0" },
    el("header", { class: "parte-cab" }, el("p", { class: "parte-letra" }, "Para empezar"), el("h3", {}, "Los datos de partida")),
    tablaProductos(P.productos), tablaDatos(P.datos)));
  for (const p of P.partes) {
    cont.append(el("section", { class: "parte", id: "parte-" + p.letra.slice(-1).toLowerCase() },
      el("header", { class: "parte-cab" }, el("p", { class: "parte-letra" }, p.letra), el("h3", {}, p.titulo), el("p", {}, p.texto)),
      p.tablas.map(t => t.tipo === "suma" ? tablaSuma(t) : tablaCalculo(t))));
  }
  aplicar();

  // ---------------------------------------------------------------- eventos
  document.addEventListener("click", e => {
    const info = e.target.closest("[data-info]");
    if (info) { abrirInfo(info.dataset.info); return; }
    const nv = e.target.closest("[data-nivel]");
    if (nv) { nivel(nv.dataset.nivel); return; }
    const a = e.target.closest("[data-ir]");
    if (a) { ir(a.dataset.ir); return; }
    const tg = e.target.closest("[data-tg]");
    if (tg && !(window.getSelection && String(window.getSelection()).length > 2)) alternar(tg.dataset.tg);
  });
  $("#ficha-cerrar").addEventListener("click", () => cerrar(false));
  dlg.addEventListener("click", e => { if (e.target === dlg) cerrar(false); });
  dlg.addEventListener("cancel", e => { e.preventDefault(); cerrar(false); });
  window.addEventListener("popstate", () => { if (dlg.open) cerrar(true); });
  $("#sw-pesos").addEventListener("change", e => { estado.pesos = e.target.checked; repintar(); });
  $("#sw-anios").addEventListener("change", e => document.documentElement.classList.toggle("ver-anios", e.target.checked));

  // enlace directo a una fila: …/presupuesto/#r108 la muestra en su tabla
  const h = location.hash.slice(1);
  if (filas.has(h)) { history.replaceState(null, "", location.pathname + location.search); requestAnimationFrame(() => ir(h)); }
})();
