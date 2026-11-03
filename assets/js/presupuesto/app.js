/* RECOEVO · página del presupuesto realista.
   Dibuja las tablas del presupuesto ejecutivo (presupuesto/datos.js, generado desde el Excel) con la misma agrupación con
   la que se guardó el libro, deja agrupar y desagrupar como en Excel y abre una ficha que explica cada fila. */
(function () {
  "use strict";
  const P = window.PRESUPUESTO;
  const $ = (s, r = document) => r.querySelector(s);
  const MILLON = 1e6;
  const estado = { pesos: false, abiertos: new Map(), inicial: new Map() };
  const filas = new Map();        // id → { f, tipo, tabla, padre }
  const tipoNivel = new Map();    // id de fila que se abre → 0 (total de tabla) o 1 (rubro con detalle)
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
      else if (k === "text") e.textContent = v;
      else e.setAttribute(k, v === true ? "" : v);
    }
    for (const h of hijos.flat()) if (h !== null && h !== undefined && h !== false) e.append(h.nodeType ? h : String(h));
    return e;
  }

  const sufijo = u => ({ "años": " años", "% al año": " al año" })[u] || "";
  const conUnidad = u => u && !sufijo(u) && !["%", "pesos", "mes", "productos"].includes(u);
  const unidadCorta = u => u.replace(/^pesos\s*/, "");
  const enMillones = v => (v < 0 ? "−" : "") + "$" + miles(Math.abs(v) / MILLON, Math.abs(v) >= 100 * MILLON ? 0 : 1) + " millones";

  // ---------------------------------------------------------------- agrupar y desagrupar
  function registrar(f, tipo, tabla, padre) { filas.set(f.id, { f, tipo, tabla, padre }); tabla.orden.push(f.id); }

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

  function aplicar() {
    for (const d of dependientes) d.el.hidden = !d.padres.every(id => estado.abiertos.get(id));
    for (const [id, bs] of toggles) {
      const ab = !!estado.abiertos.get(id);
      for (const b of bs) {
        b.setAttribute("aria-expanded", ab);
        b.firstChild.textContent = ab ? "−" : "+";
        b.setAttribute("aria-label", (ab ? "Cerrar" : "Abrir") + " el detalle de " + b.dataset.nombre);
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
      const p = preset(b.dataset.nivel);
      const igual = !marcado && [...p].every(([k, v]) => !!estado.abiertos.get(k) === !!v);
      b.setAttribute("aria-pressed", igual);
      if (igual) marcado = true;
    }
  }

  function nivel(n) { estado.abiertos = preset(n); aplicar(); }
  function alternar(id) { estado.abiertos.set(id, !estado.abiertos.get(id)); aplicar(); }

  // ---------------------------------------------------------------- tablas que suman (1 a 11)
  const COLS = [["c-can", "Cantidad (10 años)"], ["c-uni", "Unidad"], ["c-pre", "Precio de cada unidad"],
                ["c-tot", "Total 10 años"], ["c-pro", "Promedio por año"], ["c-pp", "Por producto"]];

  function cabAnios() { return P.anios.map((a, i) => el("th", { scope: "col", class: "c-an", title: a }, "Año " + i)); }

  function tablaSuma(t) {
    const f = t.fila;
    const info = { num: f.num, titulo: f.titulo, orden: [] };
    const cuerpo = el("tbody");
    const fila = (x, nv, padres) => {
      registrar(x, "suma", info, padres[padres.length - 1]);
      const kids = x.hijos && x.hijos.length;
      const nombre = nv === 0 ? x.titulo : x.nombre;
      if (kids) abrible(x.id, x.abierto, nv);
      const tr = el("tr", { class: `n${nv} ${x.color || ""}`, "data-ficha": x.id },
        el("th", { scope: "row", class: "c-con" }, el("div", { class: "con" },
          kids ? botonToggle(x.id, nombre) : el("span", { class: "tg-hueco", "aria-hidden": "true" }),
          nv === 0 ? el("span", { class: "num", "aria-label": "Tabla " + x.num }, x.num) : null,
          el("button", { type: "button", class: "nom", "data-ficha": x.id }, nombre))));
      const vals = { "c-can": x.cant, "c-pre": x.precio, "c-pro": x.prom, "c-pp": x.pp };
      for (const [c] of COLS) {
        const td = el("td", { class: c });
        if (c === "c-uni") td.textContent = x.unidad || "";
        else if (c === "c-tot") {
          td.append(x.total ? num(el("span", { class: "v-tot" }), ...x.total) : "");
          td.append(num(el("span", { class: "v-pp" }), x.pp ? x.pp[0] : null, x.pp ? x.pp[1] : null));
        } else if (vals[c]) num(td, ...vals[c]);
        else if (c === "c-pp") td.textContent = "—";
        tr.append(td);
      }
      P.anios.forEach((_, i) => {
        const td = el("td", { class: "c-an" });
        if (x.anios && x.anios[i] !== null) num(td, x.anios[i], x.tanios);
        tr.append(td);
      });
      if (padres.length) dependientes.push({ el: tr, padres: [...padres] });
      cuerpo.append(tr);
      (x.hijos || []).forEach(h => fila(h, nv + 1, [...padres, x.id]));
    };
    fila(f, 0, []);
    const cab = el("tr", {}, el("th", { scope: "col", class: "c-con" }, "Concepto"),
      COLS.map(([c, txt]) => el("th", { scope: "col", class: c }, txt, c === "c-tot" ? el("span", { class: "v-pp" }, "por producto") : null)),
      cabAnios());
    const tabla = el("table", { class: "t-suma" }, el("caption", { class: "sr" }, `Tabla ${f.num}: ${f.titulo}`), el("thead", {}, cab), cuerpo);
    return el("section", { class: "tabla", id: "tabla-" + f.num },
      el("div", { class: "desliza", tabindex: "0", role: "region", "aria-label": `Tabla ${f.num}` }, tabla),
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
    const info = { num: f.num, titulo: f.titulo, orden: [] };
    registrar(f, "calc", info, null);
    if (f.hijos.length) abrible(f.id, f.abierto, 0);
    const cab = el("div", { class: `calc-cab ${f.color || ""}`, "data-ficha": f.id },
      el("div", { class: "calc-titulo" },
        f.hijos.length ? botonToggle(f.id, f.titulo) : null,
        el("span", { class: "num", "aria-label": "Tabla " + f.num }, f.num),
        el("h4", {}, el("button", { type: "button", class: "nom", "data-ficha": f.id }, f.titulo))),
      el("div", { class: "calc-res" },
        el("p", { class: "calc-nombre" }, f.nombre.replace(/^RESULTADO:\s*/, "")),
        valorCalc(f, "calc-valor"),
        f.palabras ? el("p", { class: "calc-palabras " + veredicto(f.palabras) }, f.palabras) : null));
    const pasos = el("ol", { class: "pasos" });
    for (const h of f.hijos) {
      registrar(h, "calc", info, f.id);
      pasos.append(el("li", { class: `paso ${h.color || ""}`, "data-ficha": h.id },
        el("button", { type: "button", class: "nom", "data-ficha": h.id }, h.nombre),
        valorCalc(h, "paso-valor"),
        h.palabras ? el("span", { class: "paso-palabras " + veredicto(h.palabras) }, h.palabras) : null));
    }
    dependientes.push({ el: pasos, padres: [f.id] });
    return el("section", { class: "tabla calc", id: "tabla-" + f.num, "aria-label": `Tabla ${f.num}: ${f.titulo}` }, cab, pasos);
  }

  // ---------------------------------------------------------------- tabla 0 (productos) y 0b (datos del plan)
  function tablaProductos(p) {
    const info = { num: "0", titulo: p.titulo, orden: [] };
    const raiz = { id: p.id, nombre: p.nombre, que: p.que, porque: p.porque, vend: p.total, hijos: p.filas, titulo: p.titulo };
    registrar(raiz, "prod", info, null);
    abrible(p.id, p.abierto, 0);
    const cuerpo = el("tbody", {}, el("tr", { class: `n0 ${p.color || ""}`, "data-ficha": p.id },
      el("th", { scope: "row", class: "c-con" }, el("div", { class: "con" }, botonToggle(p.id, p.nombre),
        el("span", { class: "num", "aria-label": "Tabla 0" }, "0"), el("button", { type: "button", class: "nom", "data-ficha": p.id }, p.nombre))),
      el("td", { class: "c-cap" }, "—"), num(el("td", { class: "c-ven" }), ...p.total)));
    for (const x of p.filas) {
      registrar(x, "prod", info, p.id);
      const tr = el("tr", { class: "n1", "data-ficha": x.id },
        el("th", { scope: "row", class: "c-con" }, el("div", { class: "con" }, el("span", { class: "tg-hueco", "aria-hidden": "true" }),
          el("button", { type: "button", class: "nom", "data-ficha": x.id }, x.nombre))),
        num(el("td", { class: "c-cap" }), ...x.cap), num(el("td", { class: "c-ven" }), ...x.vend));
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
    if (x.valor) return fmt(...x.valor) + sufijo(x.unidad);
    if (x.anios) return `${fmt(x.anios[0], x.tanios)} → ${fmt(x.anios[x.anios.length - 1], x.tanios)} en el año 10`;
    return "—";
  }

  function tablaDatos(d) {
    const info = { num: "0b", titulo: d.titulo, orden: [] };
    const cuerpo = el("tbody");
    for (const x of d.filas) {
      registrar(x, "dato", info, null);
      cuerpo.append(el("tr", { class: "n1", "data-ficha": x.id },
        el("th", { scope: "row", class: "c-con" }, el("div", { class: "con" },
          el("button", { type: "button", class: "nom", "data-ficha": x.id }, x.nombre))),
        el("td", { class: "c-val" }, valorDato(x))));
    }
    const tabla = el("table", { class: "t-datos" }, el("caption", { class: "sr" }, "Tabla 0b: " + d.titulo),
      el("thead", {}, el("tr", {}, el("th", { scope: "col", class: "c-con" }, "Dato"), el("th", { scope: "col", class: "c-val" }, "Valor"))), cuerpo);
    return el("section", { class: "tabla", id: "tabla-0b" },
      el("div", { class: "tabla-cab" }, el("span", { class: "num" }, "0b"), el("h4", {}, d.titulo)),
      el("div", { class: "desliza" }, tabla));
  }

  // ---------------------------------------------------------------- ficha (explicación de una fila)
  const dlg = $("#ficha"), cuerpoFicha = $("#ficha-cuerpo");
  let actual = null;

  function cifra(etq, valor, opc = {}) {
    return el("div", { class: "cifra" + (opc.grande ? " grande" : "") }, el("span", {}, etq), el("b", {}, valor), opc.nota ? el("small", {}, opc.nota) : null);
  }

  function barras(vals, k) {
    const max = Math.max(...vals.map(v => Math.abs(v || 0))) || 1;
    return el("ol", { class: "barras" }, vals.map((v, i) => {
      const barra = el("span", { class: "b-barra" + (v < 0 ? " neg" : "") });
      barra.style.setProperty("--w", (Math.abs(v || 0) / max * 100).toFixed(1) + "%");
      return el("li", {}, el("span", { class: "b-anio", title: P.anios[i] }, "Año " + i),
        el("span", { class: "b-pista" }, barra), el("span", { class: "b-valor" }, fmt(v, k)));
    }));
  }

  function listaHijos(hs, total, k) {
    return el("ul", { class: "hijos" }, hs.map(h => {
      const p = h.total || h.valor || h.vend;
      const pct = total && p && total > 0 && p[0] >= 0 ? Math.round(p[0] / total * 100) : null;
      return el("li", {}, el("button", { type: "button", "data-ficha": h.id },
        el("span", { class: "h-nom" }, h.titulo && h.num ? h.titulo : h.nombre),
        el("span", { class: "h-val" }, p ? fmt(p[0], p[1]) : ""),
        pct !== null ? el("span", { class: "h-pct" }, pct < 1 ? "menos del 1 % del total" : `el ${pct} % del total`) : null));
    }));
  }

  function pintarFicha({ f, tipo, tabla, padre }) {
    const pf = padre ? filas.get(padre).f : null;
    const corto = t => t.replace(/\s*\([^)]*\)\s*$/, "");
    const ruta = tabla.num === "0b" ? "Datos del plan" : `Tabla ${tabla.num} · ${corto(tabla.titulo)}`;
    $("#ficha-ruta").textContent = pf && pf.nombre && filas.get(padre).padre ? `${ruta} › ${corto(pf.nombre)}` : ruta;
    const c = cuerpoFicha;
    c.textContent = "";
    const titulo = tipo === "dato" || tipo === "prod" && padre ? f.nombre : (f.titulo || f.nombre);
    c.append(el("h2", { id: "ficha-titulo" }, titulo));
    if (tipo === "calc" && !padre) c.append(el("p", { class: "ficha-sub" }, f.nombre.replace(/^RESULTADO:\s*/, "Resultado: ")));

    const cifras = el("div", { class: "ficha-cifras" });
    if (tipo === "suma") {
      if (f.total) cifras.append(cifra("Total de los 10 años", fmt(...f.total, { completo: true }),
        { grande: true, nota: Math.abs(f.total[0]) >= MILLON ? "≈ " + enMillones(f.total[0]) : null }));
      if (f.pp) cifras.append(cifra("Por producto", fmt(...f.pp, { completo: true })));
      if (f.prom) cifras.append(cifra("Promedio por año", fmt(...f.prom)));
    } else if (tipo === "calc" || tipo === "dato") {
      cifras.append(cifra(tipo === "calc" && !padre ? "Resultado" : "Valor", f.valor ? fmt(...f.valor, { completo: true }) + sufijo(f.unidad) : valorDato(f),
        { grande: true, nota: conUnidad(f.unidad) ? unidadCorta(f.unidad) : null }));
    } else if (tipo === "prod") {
      cifras.append(cifra(padre ? "Productos vendidos en el año" : "Productos vendidos en los 10 años", fmt(...f.vend), { grande: true }));
      if (f.cap) cifras.append(cifra("Capacidad de la fábrica al mes", fmt(...f.cap)));
    }
    c.append(cifras);
    if (f.palabras) c.append(el("p", { class: "palabras-caja " + veredicto(f.palabras) }, f.palabras));

    if (tipo === "suma" && pf && pf.total && f.total && pf.total[0] > 0 && f.total[0] >= 0) {
      const pct = f.total[0] / pf.total[0] * 100;
      const barra = el("span", { class: "relleno" });
      barra.style.setProperty("--w", Math.max(pct, 0.5).toFixed(1) + "%");
      c.append(el("div", { class: "parte-de" },
        el("p", {}, `Es ${pct < 1 ? "menos del 1 %" : "el " + miles(pct, pct < 10 ? 1 : 0) + " %"} de «${pf.titulo || pf.nombre}».`),
        el("span", { class: "pista" }, barra)));
    }

    if (f.que) c.append(el("h3", {}, "¿Qué es?"), el("p", {}, f.que));
    if (f.como) c.append(el("h3", {}, "¿Cómo se calcula?"), el("p", {}, f.como));
    if (f.porque) c.append(el("h3", {}, "¿De dónde sale?"), el("p", {}, f.porque));

    if (tipo === "suma" && f.cant && f.unidad && f.unidad !== "productos") {
      c.append(el("h3", {}, "Cantidad y precio"), el("dl", { class: "ficha-dl" },
        el("dt", {}, "Cantidad en los 10 años"), el("dd", {}, fmt(...f.cant) + " " + f.unidad),
        f.precio ? [el("dt", {}, "Precio de cada unidad (promedio)"), el("dd", {}, fmt(...f.precio, { completo: true }))] : null));
    }
    if (f.hijos && f.hijos.length) {
      const total = tipo === "suma" && f.total ? f.total[0] : tipo === "prod" ? f.vend[0] : null;
      c.append(el("h3", {}, tipo === "calc" ? "Paso a paso" : tipo === "prod" ? "Año por año" : "Qué suma esta fila"),
        listaHijos(f.hijos, total));
    }
    if (f.anios && f.anios.some(v => v)) c.append(el("h3", {}, "Año por año"), barras(f.anios, f.tanios));

    const i = tabla.orden.indexOf(f.id);
    const ant = $("#ficha-ant"), sig = $("#ficha-sig");
    ant.disabled = i <= 0; sig.disabled = i >= tabla.orden.length - 1;
    ant.dataset.ir = tabla.orden[i - 1] || ""; sig.dataset.ir = tabla.orden[i + 1] || "";
  }

  function abrir(id, modo) {
    const r = filas.get(id);
    if (!r) return;
    actual = id;
    pintarFicha(r);
    if (!dlg.open) { dlg.showModal(); document.documentElement.classList.add("con-ficha"); }
    if (modo === "push") history.pushState({ ficha: id }, "", "#" + id);
    else if (modo === "replace") history.replaceState({ ficha: id }, "", "#" + id);
    cuerpoFicha.scrollTop = 0;
    $("#ficha-cerrar").focus({ preventScroll: true });
  }

  function cerrar(desdeHistoria) {
    if (dlg.open) dlg.close();
    document.documentElement.classList.remove("con-ficha");
    if (!desdeHistoria && history.state && history.state.ficha) history.back();
    actual = null;
  }

  // ---------------------------------------------------------------- arriba: costo de un producto y las 8 preguntas
  function tarjetas() {
    const c = P.costo, boton = $("#costo");
    boton.dataset.ficha = c.fila;
    boton.append(el("span", { class: "cu-etq" }, "Costo de un producto"), el("span", { class: "cu-valor" }, fmt(...c.valor, { completo: true })),
      el("span", { class: "cu-nota" }, c.nota), el("span", { class: "cu-mas" }, "Ver cómo se calcula →"));
    const ol = $("#preguntas");
    for (const p of P.preguntas) {
      const [v, k] = p.valor;
      const valor = el("span", { class: "p-valor" });
      if ((k === "$" || k === "$s") && Math.abs(v) >= MILLON) valor.append("$" + miles(v / MILLON), el("small", {}, " millones"));
      else valor.append(k[0] === "%" ? fmt(v, k, { dec: 0 }) : fmt(v, k === "$s" ? "$" : k, { completo: true }));
      if (p.unidad) valor.append(el("small", {}, " " + p.unidad));
      ol.append(el("li", {}, el("button", { type: "button", class: "pregunta" + (p.alerta ? " alerta" : ""), "data-ficha": p.fila },
        el("span", { class: "p-num", "aria-hidden": "true" }, p.n), el("span", { class: "p-titulo" }, p.titulo), valor,
        el("span", { class: "p-nota" }, p.nota), p.alerta ? el("span", { class: "p-alerta" }, "✘ No llega a la meta de los socios") : null)));
    }
    $("#supone").textContent = P.supone.replace(/^Qué supone:\s*/, "");
  }

  function conclusion() {
    const cc = P.conclusion;
    const [cab, ...resto] = cc.texto.split(":");
    $("#conclusion").append(el("h2", {}, cc.titulo),
      el("p", {}, el("b", { class: veredicto(cab) }, cab + ":"), resto.join(":")));
    const [fecha, hora] = P.fuente.guardado.split(" ");
    const [a, m, d] = fecha.split("-").map(Number);
    const mes = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"][m - 1];
    $("#fuente").textContent = `Fuente: ${P.fuente.archivo}, hoja ${P.fuente.hoja}, guardado el ${d} de ${mes} de ${a} a las ${hora}. ` +
      "Las cifras salen directo del Excel y se reparten entre los " + miles(P.nprod) + " productos de los 10 años. " +
      "El Excel trae también los escenarios pesimista y optimista, con la misma estructura.";
  }

  // ---------------------------------------------------------------- armar la página
  tarjetas();
  const cont = $("#tablas");
  cont.textContent = "";
  cont.append(el("section", { class: "parte", id: "parte-0" },
    el("header", { class: "parte-cab" }, el("p", { class: "parte-letra" }, "Para empezar"), el("h3", {}, "Los datos de partida"),
      el("p", {}, "Cuántos productos se venden en los 10 años y los datos con los que se hacen todas las cuentas.")),
    tablaProductos(P.productos), tablaDatos(P.datos)));
  for (const p of P.partes) {
    cont.append(el("section", { class: "parte", id: "parte-" + p.letra.slice(-1).toLowerCase() },
      el("header", { class: "parte-cab" }, el("p", { class: "parte-letra" }, p.letra), el("h3", {}, p.titulo), el("p", {}, p.texto)),
      p.tablas.map(t => t.tipo === "suma" ? tablaSuma(t) : tablaCalculo(t))));
  }
  conclusion();
  aplicar();

  // ---------------------------------------------------------------- eventos
  document.addEventListener("click", e => {
    const tg = e.target.closest(".tg");
    if (tg) { alternar(tg.dataset.tg); return; }
    const nv = e.target.closest("[data-nivel]");
    if (nv) { nivel(nv.dataset.nivel); return; }
    const ir = e.target.closest("[data-ir]");
    if (ir && ir.dataset.ir) { abrir(ir.dataset.ir, "replace"); return; }
    const a = e.target.closest("[data-ficha]");
    if (a && !(window.getSelection && String(window.getSelection()).length > 2)) abrir(a.dataset.ficha, dlg.open ? "replace" : "push");
  });
  $("#ficha-cerrar").addEventListener("click", () => cerrar(false));
  dlg.addEventListener("click", e => { if (e.target === dlg) cerrar(false); });
  dlg.addEventListener("cancel", e => { e.preventDefault(); cerrar(false); });
  window.addEventListener("popstate", e => {
    if (e.state && e.state.ficha) abrir(e.state.ficha, "none");
    else if (dlg.open) cerrar(true);
  });
  $("#sw-pesos").addEventListener("change", e => { estado.pesos = e.target.checked; repintar(); });
  $("#sw-anios").addEventListener("change", e => document.documentElement.classList.toggle("ver-anios", e.target.checked));

  // enlace directo a una fila: …/presupuesto/#r108
  const h = location.hash.slice(1);
  if (filas.has(h)) { history.replaceState(null, "", location.pathname + location.search); abrir(h, "push"); }
})();
