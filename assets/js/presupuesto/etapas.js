/* RECOEVO · presupuesto: el plan por etapas y lo que pedimos (Ronda 2, 25-nov-2026).
   Las cifras de cada etapa salen de presupuesto/datos.js (presupuesto ejecutivo sin crédito, hoja Realista), sumando filas
   de las tablas 1, 2 y 3; no se cambia ninguna cifra. Las etapas, sus tiempos, sus metas y el pedido vienen de
   08_RECOEVO_RONDA_2_FINAL_2026-11-25/04_Cifras_revisadas/4_Plan_sin_credito_etapas_y_ley.md (pedido confirmado
   por el equipo el 23-nov-2026). Si las tres etapas no suman la inversión inicial, la sección no se muestra. */
(function () {
  "use strict";
  const P = window.PRESUPUESTO;
  const caja = document.getElementById("etapas");
  if (!P || !caja) return;

  // ---------------------------------------------------------------- lo que no está en el Excel (decisiones del equipo)
  const PEDIDO = 55e6;          // lo que se pide hoy
  const PARTE = 0.10;           // a cambio del 10 % de RECOEVO
  const VPN = 2766e6;           // valor presente neto del plan sin crédito (plan detallado realista, hoja «11 Resultados»)
  const MESES = [3, 4, 6];      // duración de cada etapa (la 2 y la 3 son aproximadas)

  // ---------------------------------------------------------------- filas del presupuesto por id
  const fila = {};
  const recorrer = f => { fila[f.id] = f; (f.hijos || []).forEach(recorrer); };
  P.partes.forEach(p => p.tablas.forEach(t => recorrer(t.fila)));
  const val = id => (fila[id] ? (fila[id].valor || fila[id].total)[0] : NaN);
  const sum = ids => ids.reduce((s, id) => s + val(id), 0);
  const anio1 = P.productos && P.productos.filas[0] ? P.productos.filas[0].vend[0] : null;

  // ---------------------------------------------------------------- formato colombiano
  const miles = (n, dec = 0) => {
    const [e, d] = Math.abs(n).toFixed(dec).split(".");
    return (n < 0 ? "−" : "") + e.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (d ? "," + d : "");
  };
  const mill = (n, dec = 1) => "$" + miles(n / 1e6, dec) + " millones";
  const M = (n, dec = 1) => "$" + miles(n / 1e6, dec) + " M";

  function el(tag, attrs = {}, ...hijos) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v === undefined || v === null || v === false) continue;
      if (k === "class") e.className = v; else e.setAttribute(k, v === true ? "" : v);
    }
    for (const h of hijos.flat()) if (h !== null && h !== undefined && h !== false) e.append(h.nodeType ? h : String(h));
    return e;
  }
  const html = s => { const t = document.createElement("template"); t.innerHTML = s; return t.content; };
  function cuenta(renglones, resultado) {
    const ol = el("ol", { class: "cuenta" });
    for (const [tipo, signo, texto, valor] of renglones)
      ol.append(el("li", { class: "linea " + tipo }, el("span", { class: "signo", "aria-hidden": "true" }, signo || ""),
        el("span", { class: "que" }, html(texto)), el("span", { class: "cuanto" }, valor)));
    if (resultado) ol.append(el("li", { class: "linea total " + resultado[0] }, el("span", { class: "signo", "aria-hidden": "true" }, "="),
      el("span", { class: "que" }, html(resultado[1])), el("span", { class: "cuanto" }, resultado[2])));
    return ol;
  }

  // ---------------------------------------------------------------- las tres etapas, armadas con filas del presupuesto
  const legales = ["r40-5", "r40-6", "r40-7", "r40-8"];             // marca, modelo de utilidad, diseño y búsqueda de patentes
  const validar = ["r41-1", "r41-2", "r41-4", "r41-5", ...legales];
  const e1 = sum(validar);
  const e2 = val("r35") + val("r41-3");
  const restoArranque = val("r39") - e1 - val("r41-3");
  const e3 = val("r34") + val("r36") + restoArranque + val("r58");
  const inv = val("r55");
  if (![e1, e2, e3, inv].every(Number.isFinite) || Math.abs(e1 + e2 + e3 - inv) > 1) {
    console.warn("etapas: las etapas no suman la inversión inicial; no se muestra la sección");
    caja.remove();
    return;
  }

  const ETAPAS = [
    {
      n: 1, nombre: "Validar", total: e1, meses: "3 meses",
      titulo: "Validar: 10 familias de Tihuaque prueban 5 prototipos",
      dice: "<b>Sin fábrica.</b> Talleres de Bogotá hacen las piezas (impresión 3D, corte láser y metalmecánica) y el equipo arma los 5 prototipos. Rotan entre 10 familias en dos turnos de 6 semanas.",
      meta: "8 de cada 10 familias lo usan todos los días.", metaTxt: "Para pasar a la siguiente: ",
      partes: [
        ["r41-1", "Ajuste del diseño para fabricar en inyección (planos y simulación de los moldes)"],
        ["r41-2", "5 prototipos funcionales impresos en 3D"],
        ["r41-4", "Pruebas: 20.000 pisadas del pedal y del seguro, corte, olor y caída de la caja"],
        ["r41-5", "Muestras y validación de proveedores (resina, fleje, carbón activado)"],
        [legales, "Registro de la marca, el modelo de utilidad y el diseño, con abogado y búsqueda de patentes"],
      ],
      ir: "r41", irTexto: "Ver en la tabla 2 →",
    },
    {
      n: 2, nombre: "Preserie", total: e2, meses: "≈ 4 meses",
      titulo: "Preserie: los moldes y los primeros 300 productos",
      dice: "Los <b>moldes son propios</b> (tardan de 10 a 12 semanas en hacerse) y un <b>taller de inyección contratado</b> (maquila) fabrica los 300 productos de la preserie. Todavía no hay fábrica propia.",
      meta: "preventas y cartas de intención de empresas, conjuntos y alcaldías.", metaTxt: "Para pasar a la siguiente: ",
      partes: [
        ["r35", "Moldes y troqueles (10 moldes, troqueles y planchas de la caja)"],
        ["r41-3", "Preserie de 300 productos con los moldes definitivos"],
      ],
      ir: "r35", irTexto: "Ver en la tabla 1 →",
    },
    {
      n: 3, nombre: "Fábrica", total: e3, meses: "≈ 6 meses",
      titulo: "Fábrica: montaje de la planta propia",
      dice: "Las máquinas tardan unos 4 meses en llegar. Cuando la planta está lista, <b>arranca el año 1 de ventas</b>" + (anio1 ? ": " + miles(anio1) + " productos ese año." : "."),
      meta: "vender desde el mes 1.", metaTxt: "La meta: ",
      partes: [
        ["r34", "Máquinas: inyectoras, prensa, horno de temple, láser y línea de ensamble"],
        ["r36", "Bodega, energía, seguridad y oficina"],
        [null, "El resto de los gastos de arranque: trámites, puesta en marcha, lanzamiento, sueldos de montaje e imprevistos", restoArranque],
        ["r58", "Dinero de respaldo (IVA de las máquinas, depósito, capital de trabajo y colchón): <i>vuelve después</i>"],
      ],
      ir: "r55", irTexto: "Ver en la tabla 4 →",
    },
  ];

  // ---------------------------------------------------------------- barra de los $5.520 M con las tres partes
  const barra = el("div", { class: "et-barra", role: "img",
    "aria-label": `Inversión de ${mill(inv, 0)} en tres etapas: ` + ETAPAS.map(e => `${e.nombre} ${mill(e.total)}`).join(", ") });
  ETAPAS.forEach(e => barra.append(el("span", { class: "et-seg s" + e.n, style: `flex-grow:${(e.total / inv).toFixed(4)}` },
    el("b", {}, e.n))));
  const leyenda = el("ol", { class: "et-leyenda" }, ETAPAS.map(e => el("li", { class: "s" + e.n },
    el("i", { "aria-hidden": "true" }), el("span", {}, el("b", {}, `${e.n}. ${e.nombre}`), " · " + e.meses), el("strong", {}, M(e.total)))),
    el("li", { class: "tot" }, el("i", { "aria-hidden": "true" }), el("span", {}, el("b", {}, "Total"), " · sin crédito"), el("strong", {}, M(inv, 0))));

  // ---------------------------------------------------------------- línea de tiempo
  const tiempo = el("ol", { class: "et-tiempo", "aria-label": "Cuánto dura cada etapa" },
    ETAPAS.map(e => el("li", { class: "s" + e.n }, el("b", {}, e.meses), el("span", {}, `Etapa ${e.n}: ${e.nombre.toLowerCase()}`))),
    el("li", { class: "venta" }, el("b", {}, "Año 1"), el("span", {}, anio1 ? `Ventas: ${miles(anio1)} productos` : "Empiezan las ventas")));

  // ---------------------------------------------------------------- tarjeta del pedido
  const valorEmpresa = PEDIDO / PARTE;
  const pedido = el("article", { class: "resp calc ancho et-pedido" },
    el("p", { class: "resp-tipo" }, "Lo que pedimos hoy"),
    el("h3", {}, "¿Cuánto pedimos y a cambio de qué?"),
    el("p", { class: "resp-valor" }, "$" + miles(PEDIDO / 1e6) + " millones", el("small", {}, " por el " + miles(PARTE * 100) + " % de RECOEVO")),
    el("p", { class: "resp-dice" }, html(`Es <b>solo la etapa 1</b>: validar el producto con 10 familias. Es <b>parte de los ${mill(inv, 0)}</b>, no algo aparte. El resto se pide después, etapa por etapa, con datos en la mano.`)),
    el("p", { class: "resp-sub" }, "Cómo se llega a esa cifra"),
    cuenta([
      ["sale", "", "Lo que cuesta la etapa 1 (validar)", mill(e1)],
    ], ["calc", "Lo que pedimos, redondeado", mill(PEDIDO, 0)]),
    el("p", { class: "resp-sub" }, "Cuánto vale RECOEVO con ese pedido"),
    cuenta([
      ["calc", "", "Lo que pedimos", mill(PEDIDO, 0)],
      ["calc", "÷", "Parte de RECOEVO para quien invierte", miles(PARTE * 100) + " %"],
    ], ["calc", "Valor de RECOEVO con ese dinero adentro", mill(valorEmpresa, 0)]),
    el("details", { class: "resp-mas" }, el("summary", {}, "¿Por qué el 10 %?"),
      html(`<p>Todo el plan, llevado a pesos de hoy, vale <b>${mill(VPN, 0)}</b> (es el <b>VPN</b>, se dice «ve-pe-ene»: valor presente neto, lo que valen hoy todas las ganancias futuras después de descontar lo que cuesta el dinero). Nuestro pedido valora a RECOEVO en <b>${mill(valorEmpresa, 0)}</b>, cerca del ${miles(valorEmpresa / VPN * 100)} % de eso. La diferencia es el riesgo: la empresa todavía no vende. Quien invierta hoy tiene la primera opción para invertir en las etapas siguientes.</p>`)));

  // ---------------------------------------------------------------- tarjetas de las etapas
  const grid = el("div", { class: "resp-grid et-grid" });
  for (const e of ETAPAS) {
    const renglones = e.partes.map(([ids, texto, fijo], i) => {
      const v = fijo !== undefined ? fijo : Array.isArray(ids) ? sum(ids) : val(ids);
      return ["sale", i ? "+" : "", texto, mill(v)];
    });
    grid.append(el("article", { class: "resp sale et-etapa s" + e.n },
      el("p", { class: "resp-tipo" }, `Etapa ${e.n} · ${e.meses}`),
      el("h3", {}, e.titulo),
      el("p", { class: "resp-valor" }, "$" + miles(e.total / 1e6, 1), el("small", {}, " millones")),
      el("p", { class: "resp-dice" }, html(e.dice)),
      el("p", { class: "resp-sub" }, "En qué se usa"),
      cuenta(renglones, ["sale", `Etapa ${e.n}`, mill(e.total)]),
      el("p", { class: "et-meta" }, el("b", {}, e.metaTxt), e.meta),
      el("button", { type: "button", class: "resp-ir", "data-ir": e.ir }, e.irTexto)));
  }

  caja.append(
    el("h2", { class: "sub", id: "t-etapas" }, "El plan por etapas y lo que pedimos"),
    el("p", { class: "resp-dice et-intro" }, html(`Para empezar se necesitan <b>${mill(inv, 0)}</b>, <b>sin crédito</b>: los ponen socios e inversionistas, sin intereses ni cuotas. No se piden de una vez: van en <b>3 etapas</b>, y solo se pasa a la siguiente si la anterior funciona.`)),
    barra, leyenda, tiempo,
    el("p", { class: "fuente et-fuente" }, `De la primera inversión a la primera venta pasan unos ${MESES.reduce((a, b) => a + b, 0)} meses. Las cifras de cada etapa suman filas de las tablas 1, 2 y 3; juntas dan la inversión inicial de la tabla 4.`),
    pedido, grid);
})();
