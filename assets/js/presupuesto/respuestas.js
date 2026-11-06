/* RECOEVO · presupuesto: las respuestas, fáciles y con colores.
   Arriba de las tablas responde las preguntas del presupuesto con su cuenta paso a paso, sin cambiar ninguna cifra:
   todo sale de presupuesto/datos.js (presupuesto ejecutivo, hoja Realista) y presupuesto/mensual.js (hoja Proyección
   del plan realista). Colores: rojo tierra = sale dinero, azul = entra dinero, morado = cálculos y resultados. */
(function () {
  "use strict";
  const P = window.PRESUPUESTO, M = window.PRESUPUESTO_MENSUAL;
  const caja = document.getElementById("respuestas");
  if (!P || !caja) return;

  // ---------------------------------------------------------------- filas del presupuesto por id
  const fila = {};
  const recorrer = f => { fila[f.id] = f; (f.hijos || []).forEach(recorrer); };
  P.partes.forEach(p => p.tablas.forEach(t => recorrer(t.fila)));
  P.datos.filas.forEach(f => { fila[f.id] = f; });
  const val = id => { const f = fila[id]; return f ? (f.valor || f.total)[0] : NaN; };
  const pp = id => (fila[id] && fila[id].pp ? fila[id].pp[0] : NaN);
  const anios = id => (fila[id] && fila[id].anios) || [];
  const vendidos = [0, ...P.productos.filas.map(f => f.vend[0])];          // año 0 … 10
  const suma = (a, i, j) => a.slice(i, j + 1).reduce((s, x) => s + (x || 0), 0);

  // ---------------------------------------------------------------- números (formato colombiano)
  const miles = (n, dec = 0) => {
    const [e, d] = Math.abs(n).toFixed(dec).split(".");
    return (n < 0 ? "−" : "") + e.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (d ? "," + d : "");
  };
  const pesos = n => "$" + miles(n);
  const mill = n => "$" + miles(n / 1e6) + " millones";
  const pct = (n, d = 1) => miles(n * 100, d) + " %";

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

  // una cuenta: renglones [tipo, signo, texto, valor] y el resultado
  function cuenta(renglones, resultado) {
    const ol = el("ol", { class: "cuenta" });
    for (const [tipo, signo, texto, valor] of renglones)
      ol.append(el("li", { class: "linea " + tipo }, el("span", { class: "signo", "aria-hidden": "true" }, signo || ""),
        el("span", { class: "que" }, html(texto)), el("span", { class: "cuanto" }, valor)));
    if (resultado) ol.append(el("li", { class: "linea total " + resultado[0] }, el("span", { class: "signo", "aria-hidden": "true" }, "="),
      el("span", { class: "que" }, html(resultado[1])), el("span", { class: "cuanto" }, resultado[2])));
    return ol;
  }

  const TIPO = { sale: "Sale dinero", entra: "Entra dinero", calc: "Cálculo" };
  function tarjeta({ tipo, pregunta, valor, unidad, dice, cuentaEl, mas, ir, irTexto, ancho, extra }) {
    const art = el("article", { class: `resp ${tipo}${ancho ? " ancho" : ""}` },
      el("p", { class: "resp-tipo" }, TIPO[tipo]),
      el("h3", {}, pregunta),
      el("p", { class: "resp-valor" }, valor, unidad ? el("small", {}, " " + unidad) : null),
      el("p", { class: "resp-dice" }, html(dice)));
    if (cuentaEl) art.append(el("p", { class: "resp-sub" }, "Cómo se llega a esa cifra"), cuentaEl);
    if (extra) art.append(extra);
    if (mas) art.append(el("details", { class: "resp-mas" }, el("summary", {}, "Explicación más detallada"), html(mas)));
    if (ir) art.append(el("button", { type: "button", class: "resp-ir", "data-ir": ir }, irTexto || "Ver en la tabla →"));
    return art;
  }

  // ---------------------------------------------------------------- cifras del presupuesto (sin cambiar nada)
  const N = P.nprod;
  const inv = val("r55"), maq = val("r56"), arr = val("r57"), resp = val("r58");
  const socios = (fila.r55.como.match(/socios \(\$([\d.]+)\)/) || [])[1];
  const credito = (fila.r55.como.match(/crédito del banco \(\$([\d.]+)/) || [])[1];
  const gasto = val("r108"), ventas = val("r117"), impuesto = -val("r133"), utilidad = val("r130");
  const costo10 = pp("r108");
  const gAnio = anios("r108"), vAnio = anios("r118");
  const costo1 = gAnio[1] / vendidos[1];
  const costo2a10 = suma(gAnio, 2, 10) / suma(vendidos, 2, 10);
  const recibe1 = vAnio[1] / vendidos[1];
  const recibe2a10 = suma(vAnio, 2, 10) / suma(vendidos, 2, 10);
  const inflacion = val("r22");

  // precio al público con IVA: promedio de lo que pagan los clientes (cada mes pesa según lo que se vende)
  let precioAnio = null, precio2a10 = null, precioMes1 = val("r19");
  if (M) {
    const iva = 1 + M.iva;
    precioAnio = Array(11).fill(0).map(() => [0, 0]);
    for (let m = 1; m < M.vendidos.length; m++) {
      const a = M.anio[m], u = M.vendidos[m];
      precioAnio[a][0] += M.precio_sin_iva[m] * iva * u;
      precioAnio[a][1] += u;
    }
    const tot = precioAnio.slice(2).reduce((s, [p, u]) => [s[0] + p, s[1] + u], [0, 0]);
    precio2a10 = tot[0] / tot[1];
    precioAnio = precioAnio.map(([p, u]) => (u ? p / u : null));
    precioMes1 = M.precio_sin_iva[1] * iva;
  }

  // ---------------------------------------------------------------- las tarjetas
  const grid = el("div", { class: "resp-grid" });

  grid.append(tarjeta({
    tipo: "sale", pregunta: "1. ¿Cuánto dinero hay que poner para empezar?",
    valor: "$" + miles(inv / 1e6), unidad: "millones",
    dice: "Es la <b>inversión inicial</b>: se pone en el año 0, antes de vender el primer producto.",
    cuentaEl: cuenta([
      ["sale", "", "Máquinas, moldes, planta y oficina", mill(maq)],
      ["sale", "+", "Gastos de arranque (trámites, desarrollo, puesta en marcha, lanzamiento)", mill(arr)],
      ["sale", "+", "Dinero de respaldo (IVA de las máquinas, depósito, capital de trabajo, colchón): <i>vuelve después</i>", mill(resp)],
    ], ["sale", "Inversión inicial", mill(inv)]),
    mas: socios && credito ? `<p><b>¿Quién lo pone?</b> Los socios, $${miles(+socios.replace(/\./g, "") / 1e6)} millones, y un crédito del banco de $${miles(+credito.replace(/\./g, "") / 1e6)} millones (19,5 % efectivo anual a 5 años). Los intereses del crédito están en los gastos (tabla 8).</p>` : null,
    ir: "r55", irTexto: "Ver en la tabla 4 →",
  }));

  grid.append(tarjeta({
    tipo: "entra", pregunta: "2. ¿A cuánto se vende?",
    valor: pesos(precioMes1), unidad: "con IVA",
    dice: `Es el <b>precio al público</b> de todo el año 1. Sube con la inflación (${pct(inflacion)} al año) al empezar cada año del plan, en julio.`,
    cuentaEl: cuenta([
      ["entra", "", "Precio al público al empezar (con IVA)", pesos(precioMes1)],
      ["sale", "−", "IVA (se dice «iva»: impuesto al valor agregado, 19 %): no es dinero de la empresa, va para el Estado", pesos(precioMes1 - precioMes1 / 1.19)],
    ], ["entra", "Precio sin IVA en la tienda propia", pesos(precioMes1 / 1.19)]),
    extra: precio2a10 ? el("ul", { class: "resp-anios" },
      el("li", {}, el("span", {}, "Año 1, en promedio (con IVA)"), el("b", {}, pesos(precioAnio[1]))),
      el("li", {}, el("span", {}, "Años 2 a 10, en promedio (con IVA)"), el("b", {}, pesos(precio2a10))),
      el("li", {}, el("span", {}, "Lo que le llega a la empresa por producto, años 2 a 10 (sin IVA, ya descontada la parte de las tiendas)"), el("b", {}, pesos(recibe2a10)))) : null,
    mas: `<p>Se vende por cuatro caminos: la tienda en línea propia; los <b>marketplaces</b>, que son páginas web como Mercado Libre y Falabella.com y cobran ≈ 14 % de comisión por cada venta; las <b>grandes superficies</b>, que son tiendas físicas como Homecenter, Éxito y Alkosto, compran el producto, lo revenden, se quedan con ≈ 40 % del precio y pagan a 60 días; y los <b>lotes a empresas</b>, que se venden más baratos; por eso a la empresa le llega, en promedio de los 10 años, <b>${pesos(pp("r118"))}</b> por producto sin IVA (en el año 1, ${pesos(recibe1)}). Ese promedio es mayor que el precio de hoy porque los precios suben con la inflación durante los 10 años.</p>`,
    ir: "r118", irTexto: "Ver en la tabla 10 →",
  }));

  grid.append(tarjeta({
    tipo: "sale", pregunta: "3. ¿Cuánto cuesta hacer un producto?",
    valor: pesos(costo10), unidad: "promedio de los 10 años",
    dice: "Todo incluido: máquinas, arranque, fabricación, nómina, ventas e intereses, <b>repartido entre los " + miles(N) + " productos</b> de los 10 años.",
    cuentaEl: cuenta([
      ["sale", "", "Fabricar: materiales, energía y planta", pesos(pp("r111"))],
      ["sale", "+", "Administrar y vender: nómina de todos, legales, oficina, publicidad y comisiones", pesos(pp("r112"))],
      ["sale", "+", "Máquinas y moldes (repartidos en los años que duran)", pesos(pp("r109"))],
      ["sale", "+", "Gastos de arranque", pesos(pp("r110"))],
      ["sale", "+", "Intereses del crédito", pesos(pp("r113"))],
    ], ["sale", "Costo de un producto (gasto completo ÷ productos vendidos)", pesos(costo10)]),
    extra: el("ul", { class: "resp-anios" },
      el("li", {}, el("span", {}, "Año 1: se venden pocos (" + miles(vendidos[1]) + ") y los costos fijos se reparten entre menos"), el("b", {}, pesos(costo1))),
      el("li", {}, el("span", {}, "Años 2 a 10, en promedio, con inflación y aumento de sueldos"), el("b", {}, pesos(costo2a10))),
      el("li", {}, el("span", {}, "Promedio de los 10 años (incluye el año 0, antes de vender)"), el("b", {}, pesos(costo10)))),
    mas: `<p>Cada año los materiales suben con la inflación y los sueldos ligados al salario mínimo suben un poco más (tabla 0b). Pero a medida que se venden más productos, los costos fijos (nómina de planta, arriendo, máquinas) se reparten entre más unidades: por eso el costo baja después del año 1. El gasto completo de los 10 años es <b>${mill(gasto)}</b> ÷ ${miles(N)} productos = <b>${pesos(costo10)}</b>.</p>`,
    ir: "r108", irTexto: "Ver en la tabla 9 →",
  }));

  grid.append(tarjeta({
    tipo: "sale", pregunta: "4. ¿Cuáles son los costos fijos y los variables?",
    valor: pesos(val("r144")), unidad: "variable por producto",
    dice: `<b>Variable</b>: lo que cuesta cada producto de más. <b>Fijo</b>: lo que se paga al año aunque no se venda nada: <b>${mill(val("r146"))}</b> al año, en promedio.`,
    cuentaEl: cuenta([
      ["sale", "", "Costo variable: " + fila.r144.palabras.replace(/\.$/, "").toLowerCase(), pesos(val("r144")) + " c/u"],
      ["sale", "", "Costos fijos al año: " + fila.r146.palabras.replace(/\.$/, "").toLowerCase(), mill(val("r146"))],
    ]),
    ir: "r146", irTexto: "Ver en la tabla 13 →",
  }));

  grid.append(tarjeta({
    tipo: "calc", pregunta: "5. ¿Cuál es la utilidad neta? (cuánto entra y cuánto queda en los 10 años)",
    valor: "$" + miles(utilidad / 1e6), unidad: `millones · el ${pct(utilidad / ventas)} de las ventas`,
    dice: "<b>La utilidad neta es la ganancia limpia</b>: lo que les queda a los socios después de pagar absolutamente todo (materiales, sueldos, arriendo, máquinas, publicidad e intereses) y también el impuesto de renta.",
    cuentaEl: cuenta([
      ["entra", "", "Ventas (sin IVA)", mill(ventas)],
      ["sale", "−", "Gasto completo (todo lo de la pregunta 3)", mill(gasto)],
      ["sale", "−", "Impuesto de renta (35 % de lo que queda)", mill(impuesto)],
    ], ["calc", "Utilidad (ganancia) neta", mill(utilidad)]),
    extra: el("ul", { class: "resp-anios" },
      el("li", {}, el("span", {}, html(`Sobre las ventas: de los <b>${mill(ventas)}</b> que pagan los clientes en 10 años, <b>${mill(utilidad)}</b> quedan para los socios`)), el("b", {}, pct(utilidad / ventas))),
      el("li", {}, el("span", {}, html(`Sobre los costos: el negocio gasta <b>${mill(gasto)}</b> en 10 años y, además de pagar todo eso, deja <b>${mill(utilidad)}</b> de ganancia`)), el("b", {}, pct(utilidad / gasto))),
      el("li", {}, el("span", {}, "Por cada producto vendido"), el("b", {}, pesos(pp("r130"))))),
    mas: `<p>Llevado a un producto: entra <b>${pesos(pp("r117"))}</b>, cuesta <b>${pesos(costo10)}</b> y el impuesto se lleva <b>${pesos(-pp("r133"))}</b>; quedan <b>${pesos(pp("r130"))}</b> de ganancia por cada producto vendido. Se llama «neta» porque ya se le quitó todo, incluso el impuesto; si no se le quita el impuesto se llama utilidad antes de impuestos.</p>`,
    ir: "r130", irTexto: "Ver en la tabla 11 →",
  }));

  // punto de equilibrio: cuántos, cómo y cuándo
  const pe = val("r148"), mesPE = val("r150");
  let rampa = "", grafPE = null;
  if (M) {
    const v = M.vendidos, d1 = v[2] - v[1];
    let k = 2; while (k < 60 && v[k + 1] - v[k] === d1) k++;
    const d2 = v[k + 1] - v[k];
    rampa = `Las ventas empiezan en <b>${miles(v[1])}</b> productos en el mes 1 y suben <b>${miles(d1)}</b> cada mes hasta <b>${miles(v[k])}</b> (mes ${k}); después suben <b>${miles(d2)}</b> cada mes. En el mes ${mesPE - 1} se venden ${miles(v[mesPE - 1])} (todavía no alcanza) y en el <b>mes ${mesPE}</b>, <b>${miles(v[mesPE])}</b>: por primera vez más que los ${miles(pe)}.`;
    grafPE = barrasPE(v, pe, mesPE);
  }
  grid.append(tarjeta({
    tipo: "calc", ancho: true, pregunta: "6. ¿Cuál es el punto de equilibrio y cuándo se alcanza?",
    valor: miles(pe), unidad: `productos al mes · se alcanza en el mes ${mesPE}`,
    dice: "Es lo que hay que vender para no perder: lo que entra paga justo todos los costos. Se alcanza en el <b>mes " + mesPE + "</b> de ventas.",
    cuentaEl: cuenta([
      ["entra", "", "Precio que recibe la empresa por producto (promedio, sin IVA)", pesos(val("r143"))],
      ["sale", "−", "Costo variable por producto", pesos(val("r144"))],
      ["calc", "=", "Margen de contribución: lo que deja cada producto para pagar los fijos", pesos(val("r145"))],
      ["sale", "", "Costos fijos al año", mill(val("r146"))],
      ["calc", "÷", "Margen de contribución", pesos(val("r145"))],
      ["calc", "=", "Productos al año para no perder", miles(val("r147"))],
      ["calc", "÷", "12 meses", "12"],
    ], ["calc", "Punto de equilibrio al mes", miles(pe) + " productos"]),
    extra: grafPE ? el("div", { class: "resp-graf" }, el("p", { class: "resp-sub" }, "¿Cómo se proyectó cuándo se alcanza?"), el("p", { class: "resp-dice" }, html(rampa)), grafPE) : null,
    ir: "r150", irTexto: "Ver en la tabla 13 →",
  }));

  // retorno de la inversión y mes de recuperación
  const mesRec = val("r156");
  grid.append(tarjeta({
    tipo: "calc", ancho: true, pregunta: "7. ¿Cuál es el retorno de la inversión?",
    valor: pct(val("r153"), 0), unidad: `en 10 años · la inversión se recupera en el mes ${mesRec}`,
    dice: `Los socios y el banco ponen <b>${mill(inv)}</b> para empezar y en 10 años el negocio deja <b>${mill(utilidad)}</b> de utilidad neta: <b>${miles(utilidad / inv, 1)} veces</b> lo invertido. La inversión vuelve completa en el <b>mes ${mesRec}</b> (${fila.r156.palabras.replace(/^Mes \d+ = /, "").replace(/\.$/, "")}); de ahí en adelante, lo que deja el negocio es ganancia.`,
    cuentaEl: cuenta([
      ["calc", "", "Utilidad neta de los 10 años", mill(utilidad)],
      ["sale", "÷", "Inversión inicial", mill(inv)],
    ], ["calc", "Retorno de la inversión (ROI, se dice «erre-o-i»)", pct(val("r153"), 0)]),
    extra: M ? el("div", { class: "resp-graf" }, el("p", { class: "resp-sub" }, "¿Cómo se calcula el mes en que se recupera?"),
      el("p", { class: "resp-dice" }, "Se suma mes a mes el dinero libre que deja el negocio (lo que entra menos todo lo que sale, también las máquinas nuevas y el dinero que queda en inventario). Empieza en negativo por la inversión; el mes en que la suma llega a cero, la inversión está recuperada."),
      lineaRecuperacion(M.flujo_acumulado, mesRec)) : null,
    ir: "r153", irTexto: "Ver en la tabla 14 →",
  }));

  grid.append(tarjeta({
    tipo: "calc", pregunta: "8. ¿Cuál es la rentabilidad sobre los costos?",
    valor: pct(utilidad / gasto), unidad: "",
    dice: `En 10 años el negocio gasta <b>${mill(gasto)}</b> (fabricar, administrar, vender, máquinas e intereses) y, además de pagar todo eso y el impuesto, deja <b>${mill(utilidad)}</b> de utilidad neta: una ganancia de más de la cuarta parte de todo lo gastado. El precio cubre los costos con holgura.`,
    cuentaEl: cuenta([
      ["calc", "", "Utilidad neta de los 10 años", mill(utilidad)],
      ["sale", "÷", "Gasto completo de los 10 años", mill(gasto)],
    ], ["calc", "Rentabilidad sobre los costos", pct(utilidad / gasto)]),
    ir: "r108", irTexto: "Ver el gasto completo →",
  }));

  grid.append(tarjeta({
    tipo: "calc", pregunta: "9. ¿Cuál es la rentabilidad sobre las ventas (el porcentaje de utilidad final)?",
    valor: pct(utilidad / ventas), unidad: "",
    dice: `De los <b>${mill(ventas)}</b> que pagan los clientes en 10 años, <b>${mill(utilidad)}</b> quedan como ganancia limpia para los socios, ya pagado todo e incluido el impuesto. Alcanza para pagar el crédito del banco, devolverles a los socios lo que pusieron y reinvertir en el negocio.`,
    cuentaEl: cuenta([
      ["calc", "", "Utilidad neta de los 10 años", mill(utilidad)],
      ["entra", "÷", "Ventas de los 10 años", mill(ventas)],
    ], ["calc", "Rentabilidad sobre las ventas = porcentaje de utilidad final", pct(utilidad / ventas)]),
    mas: `<p>El <b>porcentaje de utilidad final</b>, o <b>margen neto</b>, es esta misma cifra: en RECOEVO, el ${pct(utilidad / ventas)} de todo lo que pagan los clientes en 10 años (${mill(utilidad)} de ${mill(ventas)}) termina siendo de los socios; el resto se va en fabricar, administrar, vender, intereses e impuesto de renta. La pregunta 8 compara la misma ganancia con lo que se gasta y no con lo que se vende; por eso da otro porcentaje.</p>`,
    ir: "r130", irTexto: "Ver en la tabla 11 →",
  }));

  // ---------------------------------------------------------------- envíos: quién los paga (los inversionistas lo preguntan)
  const E = M && M.envio;
  if (E && fila.r123 && fila.r124 && fila.r125) {
    const zonas = el("div", { class: "desliza anios-caja" }, el("table", { class: "t-anios t-envio" },
      el("caption", { class: "sr" }, "Tarifa de envío por zona de las ventas por internet"),
      el("thead", {}, el("tr", {}, el("th", { scope: "col" }, "A dónde va el pedido"), el("th", { scope: "col" }, "Parte de los pedidos"),
        el("th", { scope: "col", class: "entra" }, "Cobra al cliente"), el("th", { scope: "col", class: "sale" }, "Le cuesta a la empresa"))),
      el("tbody", {}, E.zonas.map(z => el("tr", {}, el("th", { scope: "row" }, z.zona), el("td", {}, miles(z.pedidos * 100) + " %"),
        el("td", { class: "entra" }, pesos(z.cobra)), el("td", { class: "sale" }, pesos(z.costo)))),
        el("tr", { class: "prom" }, el("th", { scope: "row" }, "Promedio por pedido"), el("td", {}, "100 %"),
          el("td", { class: "entra" }, pesos(E.promedio.cobra)), el("td", { class: "sale" }, pesos(E.promedio.costo))))));
    grid.append(tarjeta({
      tipo: "entra", ancho: true, pregunta: "10. ¿Y el envío? ¿Quién lo paga?",
      valor: pesos(E.promedio.cobra), unidad: "envío promedio por pedido, que el cliente paga aparte del precio",
      dice: "En las ventas <b>por internet</b> (tienda propia y marketplaces) el <b>cliente paga el envío aparte</b>, a lo que cobra la transportadora más el 10 %. A las <b>cadenas y a los lotes de empresas</b> no se les cobra envío: la empresa los lleva en estibas y ese flete ya está en los gastos.",
      cuentaEl: cuenta([
        ["entra", "", "Lo que pagan los clientes por envíos y las empresas por talleres (10 años)", mill(val("r124"))],
        ["sale", "−", "Lo que cobran la transportadora y los talleristas", mill(-val("r125"))],
      ], ["calc", "Queda para pagar el empaque y el manejo de los pedidos", mill(val("r123"))]),
      extra: el("div", { class: "resp-graf" },
        el("p", { class: "resp-sub" }, "Tarifa por zona (ventas por internet)"), zonas,
        el("p", { class: "resp-dice" }, html(`<b>Cadenas y lotes:</b> el flete lo paga la empresa y está en la tabla 7, fila «Distribución a clientes y garantía»: <b>${pesos(pp("r101"))}</b> por producto, contando también la reserva del 3 % de las ventas para garantías.`)),
        el("button", { type: "button", class: "resp-ir", "data-ir": "r101" }, "Ver en la tabla 7 →")),
      mas: `<p>La caja mide ${E.caja_cm.join(" × ")} cm y pesa ${miles(E.peso_real, 1)} kg con el producto, pero la transportadora la cobra como si pesara ${miles(E.peso_cobrado, 0)} kg por su tamaño (las cajas grandes y livianas se cobran por volumen). Por eso un envío cuesta en promedio ${pesos(E.promedio.costo)} y se cobran ${pesos(E.promedio.cobra)}: la diferencia paga el empaque y el manejo. Los talleres de uso los pagan aparte las empresas que compran por lotes.</p>`,
      ir: "r123", irTexto: "Ver en la tabla 10 →",
    }));
  }

  // ---------------------------------------------------------------- año por año: precio y costo
  const filasAnio = [];
  for (let a = 1; a <= 10; a++)
    filasAnio.push(el("tr", {}, el("th", { scope: "row" }, "Año " + a),
      el("td", {}, miles(vendidos[a])),
      el("td", { class: "entra" }, precioAnio ? pesos(precioAnio[a]) : "—"),
      el("td", { class: "entra" }, pesos(vAnio[a] / vendidos[a])),
      el("td", { class: "sale" }, pesos(gAnio[a] / vendidos[a]))));
  const prom = (txt, p, r, c, clase) => el("tr", { class: clase }, el("th", { scope: "row" }, txt), el("td", {}, ""),
    el("td", { class: "entra" }, p), el("td", { class: "entra" }, r), el("td", { class: "sale" }, c));
  const tablaAnios = el("div", { class: "desliza anios-caja" }, el("table", { class: "t-anios" },
    el("caption", { class: "sr" }, "Precio y costo de un producto, año por año"),
    el("thead", {}, el("tr", {}, el("th", { scope: "col" }, "Año"), el("th", { scope: "col" }, "Vendidos"),
      el("th", { scope: "col", class: "entra" }, "Precio con IVA"), el("th", { scope: "col", class: "entra" }, "Le llega a la empresa (sin IVA)"),
      el("th", { scope: "col", class: "sale" }, "Cuesta hacerlo"))),
    el("tbody", {}, filasAnio,
      prom("Promedio años 2 a 10", precio2a10 ? pesos(precio2a10) : "—", pesos(recibe2a10), pesos(costo2a10), "prom"),
      prom("Promedio de los 10 años", "", pesos(pp("r118")), pesos(costo10), "prom total"))));

  caja.append(
    el("div", { class: "colores", role: "note", "aria-label": "Qué quiere decir cada color" },
      el("span", { class: "c sale" }, el("i", {}), "Sale dinero: inversión y gastos"),
      el("span", { class: "c entra" }, el("i", {}), "Entra dinero: ventas"),
      el("span", { class: "c calc" }, el("i", {}), "Cálculos y resultados")),
    el("details", { class: "siglas" }, el("summary", {}, "Siglas y palabras que aparecen: qué son y cómo se dicen"),
      el("dl", {}, [
        ["IVA («iva»)", "Impuesto al valor agregado: el 19 % que se le suma al precio y va para el Estado, no para la empresa."],
        ["ROI («erre-o-i»)", "Retorno de la inversión: cuánta utilidad neta deja el negocio comparada con lo que se puso para empezar."],
        ["ICA («ica»)", "Impuesto de industria y comercio: impuesto del municipio sobre lo que se vende."],
        ["REP («rep»)", "Responsabilidad extendida del productor: la empresa responde por el reciclaje de sus empaques."],
        ["DANE («dane»)", "Departamento Administrativo Nacional de Estadística: de ahí sale la inflación que usa el plan."],
        ["Marketplace («márket-pleis»)", "Página web donde muchas marcas venden, como Mercado Libre y Falabella.com. Cobra ≈ 14 % de comisión por cada venta."],
        ["Gran superficie o cadena", "Tienda física grande, como Homecenter, Éxito y Alkosto, que compra el producto y lo revende. Se queda con ≈ 40 % del precio y paga a 60 días."],
        ["Utilidad neta", "La ganancia limpia: lo que queda después de pagar todo, incluido el impuesto de renta."],
        ["M", "Millones de pesos."],
      ].flatMap(([t, d]) => [el("dt", {}, t), el("dd", {}, d)]))),
    el("p", { class: "resp-intro" }, html("Todo es para los <b>10 años</b> del plan y también <b>llevado a un producto</b>. Toca «Ver en la tabla» para ir al detalle.")),
    grid,
    el("section", { class: "bloque anios", "aria-labelledby": "t-anios" },
      el("h2", { class: "sub", id: "t-anios" }, "Año por año: precio y costo de un producto"),
      el("p", { class: "resp-dice" }, html("El precio sube con la inflación al empezar cada año del plan (en julio). El costo de un producto es alto el año 1 porque se venden pocos y los costos fijos se reparten entre menos; luego baja, aunque los materiales y los sueldos suben cada año.")),
      tablaAnios,
      el("p", { class: "fuente" }, "Costo = gasto completo del año ÷ productos vendidos ese año (tabla 9). Le llega a la empresa = venta de productos del año ÷ productos vendidos (tabla 10). Precio al público = promedio de lo que pagan los clientes cada mes (hoja Proyección del plan realista). El año 0 se gastan " + mill(gAnio[0]) + " antes de vender; van en el promedio de los 10 años.")));

  // ---------------------------------------------------------------- gráficas sencillas (SVG)
  function barrasPE(v, pe, mesPE) {
    const n = Math.max(24, mesPE + 6), W = 640, H = 220, izq = 46, abajo = 26, arriba = 12;
    const max = Math.max(pe, ...v.slice(1, n + 1)) * 1.08, bw = (W - izq - 8) / n;
    const y = x => H - abajo - (x / max) * (H - abajo - arriba);
    let s = `<svg viewBox="0 0 ${W} ${H}" class="graf" role="img" aria-label="Productos vendidos cada mes frente al punto de equilibrio de ${miles(pe)} al mes">`;
    for (let m = 1; m <= n; m++) {
      const x = izq + (m - 1) * bw + 2, yy = y(v[m]), ok = v[m] >= pe;
      s += `<rect x="${x}" y="${yy}" width="${bw - 4}" height="${H - abajo - yy}" rx="3" class="${ok ? "b-ok" : "b-no"}"><title>Mes ${m}: ${miles(v[m])} productos</title></rect>`;
      if (m === 1 || m % 6 === 0 || m === mesPE) s += `<text x="${x + (bw - 4) / 2}" y="${H - 8}" class="${m === mesPE ? "t-fuerte" : ""}" text-anchor="middle">${m}</text>`;
    }
    s += `<line x1="${izq}" x2="${W - 4}" y1="${y(pe)}" y2="${y(pe)}" class="l-pe"/><text x="${izq - 6}" y="${y(pe) + 4}" text-anchor="end" class="t-pe">${miles(pe)}</text>`;
    s += `<text x="${izq + (mesPE - 1) * bw + bw / 2}" y="${y(v[mesPE]) - 6}" text-anchor="middle" class="t-fuerte">mes ${mesPE}</text>`;
    s += `<text x="${izq}" y="${H - 8}" text-anchor="end" class="t-eje">mes</text></svg>`;
    const fig = el("figure", { class: "fig" }, html(s), el("figcaption", {}, "Barras: productos vendidos cada mes (claras: todavía no alcanza; oscuras: ya pasó). Línea: punto de equilibrio."));
    return fig;
  }

  function lineaRecuperacion(f, mesRec) {
    const n = Math.min(f.length - 1, Math.max(60, mesRec + 10)), W = 640, H = 220, izq = 54, abajo = 26, arriba = 14;
    const vals = f.slice(0, n + 1), min = Math.min(...vals), max = Math.max(0, ...vals);
    const x = m => izq + (m / n) * (W - izq - 8), y = v => arriba + (max - v) / (max - min) * (H - abajo - arriba);
    const pts = vals.map((v, m) => `${x(m).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
    let s = `<svg viewBox="0 0 ${W} ${H}" class="graf" role="img" aria-label="Dinero libre acumulado mes a mes: llega a cero en el mes ${mesRec}">`;
    s += `<line x1="${izq}" x2="${W - 4}" y1="${y(0)}" y2="${y(0)}" class="l-cero"/><text x="${izq - 6}" y="${y(0) + 4}" text-anchor="end" class="t-eje">$0</text>`;
    s += `<text x="${izq - 6}" y="${y(min) + 4}" text-anchor="end" class="t-eje">${"−$" + miles(-min / 1e6)} M</text>`;
    s += `<polyline points="${pts}" class="l-flujo"/>`;
    s += `<circle cx="${x(mesRec)}" cy="${y(f[mesRec])}" r="6" class="p-rec"/><text x="${x(mesRec)}" y="${y(f[mesRec]) - 12}" text-anchor="middle" class="t-fuerte">mes ${mesRec}</text>`;
    for (let m = 12; m <= n; m += 12) s += `<text x="${x(m)}" y="${H - 8}" text-anchor="middle" class="t-eje">${m}</text>`;
    s += `<text x="${izq}" y="${H - 8}" text-anchor="end" class="t-eje">mes</text></svg>`;
    return el("figure", { class: "fig" }, html(s), el("figcaption", {}, "Dinero libre acumulado: empieza en negativo por la inversión y en el mes " + mesRec + " vuelve a cero."));
  }
})();
