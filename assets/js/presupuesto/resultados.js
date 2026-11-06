/* RECOEVO · presupuesto, parte C: de las ventas a la utilidad neta, paso a paso (pedido de William, 6-nov-2026).
   Cascada con signos y porcentaje sobre las ventas, para los 10 años o para cada año; los indicadores con su cuenta
   (margen de contribución, rentabilidad sobre la venta = porcentaje de utilidad, rentabilidad sobre los costos,
   utilidad neta y ROI) y la tabla año por año con por qué cambia. Sin cambiar ninguna cifra: todo sale de
   presupuesto/datos.js. Cuadra al peso: ventas − variables − fijos − intereses − impuesto = utilidad neta (tabla 11). */
(function () {
  "use strict";
  const P = window.PRESUPUESTO;
  const parteC = document.getElementById("parte-c");
  if (!P || !parteC) return;

  const fila = {};
  const recorrer = f => { fila[f.id] = f; (f.hijos || []).forEach(recorrer); };
  P.partes.forEach(p => p.tablas.forEach(t => recorrer(t.fila)));
  const A = id => (fila[id] && fila[id].anios) || Array(11).fill(0);
  const total = a => a.reduce((s, x) => s + (x || 0), 0);
  const miles = (n, dec = 0) => {
    const [e, d] = Math.abs(n).toFixed(dec).split(".");
    return e.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (d ? "," + d : "");
  };
  const mill = n => (n < 0 ? "−" : "") + "$" + miles(Math.abs(n) / 1e6, Math.abs(n) < 1e9 ? 1 : 0) + " M";
  const pesos = n => (n < 0 ? "−" : "") + "$" + miles(Math.abs(n));
  const pct = (n, d = 1) => (n < 0 ? "−" : "") + miles(Math.abs(n) * 100, d) + " %";
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

  // ---------------------------------------------------------------- las cuentas de cada año (0 a 10) y del total
  // costos variables = las filas que el punto de equilibrio cuenta como variables (tabla 13, fila b)
  const VARIABLES = ["r71", "r80", "r86", "r95", "r99", "r100", "r101"];
  const anio = t => {
    const productos = A("r118")[t], envios = A("r123")[t], ventas = A("r117")[t];
    const variables = VARIABLES.reduce((s, id) => s + (A(id)[t] || 0), 0);
    const intereses = A("r113")[t], gasto = A("r108")[t], impuesto = -A("r133")[t];
    const fijos = gasto - variables - intereses;
    const margen = ventas - variables, operativa = margen - fijos, antes = operativa - intereses;
    return { productos, envios, ventas, variables, fijos, intereses, impuesto, gasto, margen, operativa, antes, neta: A("r130")[t] };
  };
  const anios = Array.from({ length: 11 }, (_, t) => anio(t));
  const T = Object.fromEntries(Object.keys(anios[0]).map(k => [k, total(anios.map(a => a[k]))]));
  const vendidos = [0, ...P.productos.filas.map(f => f.vend[0])];
  const N = P.nprod, inv = fila.r55.total[0];

  // ---------------------------------------------------------------- la cascada
  const cuerpo = el("ol", { class: "cuenta cascada-lista" });
  const quePasa = el("p", { class: "resp-dice cascada-dice" });
  const RENGLONES = [
    ["entra", "", "Ventas sin IVA", "ventas", "Lo que pagan los clientes por los productos, más lo que queda de los envíos y los talleres."],
    ["sale", "−", "Costos variables", "variables", "Crecen con cada producto: materiales, operarios, energía, comisiones, anuncios, distribución, garantía e ICA («ica», impuesto de industria y comercio)."],
    ["calc", "=", "Margen de contribución", "margen", "Lo que dejan los productos para pagar todo lo demás."],
    ["sale", "−", "Costos fijos", "fijos", "Se pagan aunque no se venda: nómina de planta, comercial y administrativa, arriendo, máquinas, oficina, legales, marketing fijo y el arranque del año 0."],
    ["calc", "=", "Utilidad operativa", "operativa", "Lo que deja el negocio con su operación, antes de pagar los intereses del banco y el impuesto."],
    ["sale", "−", "Intereses del crédito", "intereses", "Lo que cuesta el préstamo del banco (el crédito se paga en 5 años)."],
    ["calc", "=", "Utilidad antes de impuestos", "antes", ""],
    ["sale", "−", "Impuesto de renta", "impuesto", "35 % de la utilidad; las pérdidas de los primeros años se descuentan después."],
    ["calc", "=", "Utilidad neta", "neta", "La ganancia limpia que les queda a los socios."],
  ];
  function pintar(t) {
    const d = t === "total" ? T : anios[t];
    cuerpo.textContent = "";
    for (const [tipo, signo, nombre, k, explica] of RENGLONES) {
      const valor = d[k], p = d.ventas ? valor / d.ventas : null;
      const total = k === "neta";
      cuerpo.append(el("li", { class: `linea con-pct ${tipo}${signo === "=" ? " parcial" : ""}${total ? " total" : ""}` },
        el("span", { class: "signo", "aria-hidden": "true" }, signo),
        el("span", { class: "que" }, el("b", {}, nombre), explica ? el("small", {}, explica) : null),
        el("span", { class: "cuanto" }, mill(valor)),
        el("span", { class: "pct" }, p === null ? "—" : pct(p))));
    }
    const cuando = t === "total" ? "En los 10 años" : `En el año ${t}`;
    if (t === 0) quePasa.innerHTML = `En el año 0 todavía no se vende nada: se pagan ${mill(-d.neta)} de gastos de arranque y de puesta en marcha, que quedan como pérdida y se recuperan después.`;
    else if (d.neta < 0) quePasa.innerHTML = `${cuando} todavía se pierde: se venden ${miles(vendidos[t])} productos y el margen de contribución (${mill(d.margen)}) no alcanza para pagar los costos fijos (${mill(d.fijos)}).`;
    else quePasa.innerHTML = `${cuando} los clientes pagan ${mill(d.ventas)}. Después de pagar los costos variables, los fijos, los intereses y el impuesto, quedan <b>${mill(d.neta)}</b> de utilidad neta: el <b>${pct(d.neta / d.ventas)}</b> de lo vendido.`;
    selector.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.anio === String(t)));
  }
  const selector = el("div", { class: "anio-sel", role: "group", "aria-label": "Ver los 10 años o un año" },
    el("button", { type: "button", "data-anio": "total" }, "10 años"),
    Array.from({ length: 11 }, (_, t) => el("button", { type: "button", "data-anio": String(t) }, "Año " + t)));
  selector.addEventListener("click", e => {
    const b = e.target.closest("button[data-anio]");
    if (b) pintar(b.dataset.anio === "total" ? "total" : +b.dataset.anio);
  });

  // ---------------------------------------------------------------- los indicadores, cada uno con su cuenta
  const mcUno = fila.r145 ? fila.r145.valor[0] : (T.productos - T.variables) / N;
  const recibe = fila.r143 ? fila.r143.valor[0] : T.productos / N;
  const indicador = (tipo, titulo, valor, cuentaHtml, dice) => el("article", { class: `ind ${tipo}` },
    el("h4", {}, titulo), el("p", { class: "ind-valor" }, valor), el("p", { class: "ind-cuenta" }, html(cuentaHtml)), el("p", { class: "ind-dice" }, html(dice)));
  const indicadores = el("div", { class: "ind-grid" },
    indicador("calc", "Margen de contribución", pesos(mcUno) + " por producto · " + pct(mcUno / recibe),
      `${pesos(recibe)} que recibe la empresa − ${pesos(recibe - mcUno)} de costo variable = <b>${pesos(mcUno)}</b>; ${pesos(mcUno)} ÷ ${pesos(recibe)} = <b>${pct(mcUno / recibe)}</b>`,
      `Cada producto, después de pagar lo que cuesta hacerlo y venderlo, deja ${pesos(mcUno)} para pagar la planta, la nómina fija, las máquinas y los intereses. Con los ${miles(N)} productos de los 10 años son ${mill(mcUno * N)}. (En la cascada da ${pct(T.margen / T.ventas)} porque ahí también entra lo que queda de los envíos.)`),
    indicador("calc", "Rentabilidad sobre la venta = porcentaje de utilidad (margen neto)", pct(T.neta / T.ventas),
      `${mill(T.neta)} de utilidad neta ÷ ${mill(T.ventas)} de ventas = <b>${pct(T.neta / T.ventas)}</b>`,
      `De todo lo que pagan los clientes en 10 años, ${mill(T.neta)} terminan siendo de los socios; el resto se va en hacer, vender y administrar, en intereses y en el impuesto.`),
    indicador("calc", "Rentabilidad sobre los costos", pct(T.neta / T.gasto),
      `${mill(T.neta)} de utilidad neta ÷ ${mill(T.gasto)} de gasto completo = <b>${pct(T.neta / T.gasto)}</b>`,
      `El negocio gasta ${mill(T.gasto)} en 10 años y, además de pagar todo eso y el impuesto, deja ${mill(T.neta)}: el precio cubre los costos con holgura.`),
    indicador("calc", "Utilidad neta", mill(T.neta) + " · " + pct(T.neta / T.ventas) + " de las ventas",
      `${mill(T.ventas)} − ${mill(T.gasto)} de gasto completo − ${mill(T.impuesto)} de impuesto = <b>${mill(T.neta)}</b>`,
      `La ganancia limpia de los socios en los 10 años, ya pagado todo. Por producto: ${pesos(T.neta / N)}.`),
    indicador("calc", "ROI («erre-o-i»): retorno de la inversión", pct(T.neta / inv, 0),
      `${mill(T.neta)} de utilidad neta ÷ ${mill(inv)} de inversión inicial = <b>${pct(T.neta / inv, 0)}</b> (${miles(T.neta / inv, 1)} veces)`,
      `<b>En qué se diferencia de las rentabilidades:</b> estas comparan la ganancia con lo que se vende o se gasta durante los 10 años; el ROI la compara con el dinero que se puso al principio para montar la empresa (${mill(inv)}). Por eso es mucho más alto: con ${mill(inv)} se arma un negocio que en 10 años deja ${mill(T.neta)}.`));

  // ---------------------------------------------------------------- año por año
  const filas = anios.map((d, t) => el("tr", {}, el("th", { scope: "row" }, "Año " + t),
    el("td", { class: "entra" }, mill(d.ventas)), el("td", { class: "calc c-mc" }, mill(d.margen)), el("td", { class: d.neta < 0 ? "sale" : "calc" }, mill(d.neta)),
    el("td", {}, d.ventas ? pct(d.neta / d.ventas) : "—"), el("td", {}, d.gasto ? pct(d.neta / d.gasto) : "—")));
  const tabla = el("div", { class: "desliza anios-caja" }, el("table", { class: "t-anios t-result" },
    el("caption", { class: "sr" }, "Resultados año por año"),
    el("thead", {}, el("tr", {}, el("th", { scope: "col" }, "Año"), el("th", { scope: "col", class: "entra" }, "Ventas"),
      el("th", { scope: "col", class: "calc c-mc" }, "Margen de contribución"), el("th", { scope: "col", class: "calc" }, "Utilidad neta"),
      el("th", { scope: "col" }, "Sobre la venta"), el("th", { scope: "col" }, "Sobre los costos"))),
    el("tbody", {}, filas, el("tr", { class: "prom total" }, el("th", { scope: "row" }, "10 años"),
      el("td", { class: "entra" }, mill(T.ventas)), el("td", { class: "calc c-mc" }, mill(T.margen)), el("td", { class: "calc" }, mill(T.neta)),
      el("td", {}, pct(T.neta / T.ventas)), el("td", {}, pct(T.neta / T.gasto))))));
  const primero = anios.findIndex((d, t) => t > 0 && d.neta > 0);
  const sinInteres = anios.findIndex((d, t) => t > 0 && d.intereses === 0);
  const conImpuesto = anios.findIndex((d, t) => t > 0 && d.impuesto > 0);
  const porQue = el("div", { class: "resp-dice por-que" }, html(
    `<p><b>¿Por qué cambia de un año a otro?</b></p><ul>` +
    `<li>En el <b>año 0</b> no se vende: solo se gasta en el arranque (${mill(anios[0].neta)}).</li>` +
    `<li>En el <b>año 1</b> se venden ${miles(vendidos[1])} productos y el margen (${mill(anios[1].margen)}) todavía no alcanza para los costos fijos (${mill(anios[1].fijos)}): se pierden ${mill(-anios[1].neta)}.</li>` +
    `<li>Desde el <b>año ${primero}</b> hay ganancia y crece cada año: las ventas suben de ${miles(vendidos[1])} a ${miles(vendidos[10])} productos, mientras los costos fijos crecen mucho más despacio (de ${mill(anios[1].fijos)} a ${mill(anios[10].fijos)}).</li>` +
    `<li>Los <b>intereses</b> se acaban en el año ${sinInteres}, cuando se termina de pagar el crédito, y el <b>impuesto de renta</b> aparece en el año ${conImpuesto}, cuando ya se descontaron las pérdidas del principio.</li></ul>`));

  // ---------------------------------------------------------------- a la página: al comienzo de la parte C
  const bloque = el("section", { class: "cascada", id: "paso-a-paso", "aria-labelledby": "t-paso" },
    el("h3", { id: "t-paso" }, "De las ventas a la utilidad neta, paso a paso"),
    el("p", { class: "resp-dice" }, html("Cada fila resta lo que se paga, con su cifra en pesos y qué parte de las ventas es. Elige los <b>10 años</b> o un año.")),
    selector, cuerpo, quePasa,
    el("h3", { class: "ind-titulo" }, "Los indicadores, con su cuenta"), indicadores,
    el("h3", { class: "ind-titulo" }, "Año por año"), tabla, porQue,
    el("p", { class: "fuente" }, "Costos variables = materiales, energía e insumos, operarios, ICA, anuncios, comisiones y distribución con garantía (las filas que la tabla 13 cuenta como variables). Costos fijos = gasto completo de la tabla 9 menos variables y menos intereses. Todo cuadra al peso con la utilidad neta de la tabla 11."));
  const cab = parteC.querySelector(".parte-cab");
  cab ? cab.after(bloque) : parteC.prepend(bloque);
  pintar("total");

  // enlace desde la respuesta 5 (utilidad neta) hasta este paso a paso
  const r5 = [...document.querySelectorAll(".resp")].find(c => /^5\./.test(c.querySelector("h3").textContent));
  if (r5) r5.querySelector(".resp-ir").before(el("a", { class: "resp-ir enlace", href: "#paso-a-paso" }, "Ver el paso a paso y todos los indicadores →"));
})();
