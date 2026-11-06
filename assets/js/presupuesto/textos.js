/* RECOEVO · presupuesto: ajustes de redacción pedidos por William (6-nov-2026), aplicados ANTES de dibujar la página.
   No cambia ninguna cifra: reescribe frases del tipo «por cada $100…» para decir qué significa la cifra en el negocio,
   con las cifras reales, y aclara los canales de venta. Las cifras se leen de presupuesto/datos.js y mensual.js. */
(function () {
  "use strict";
  const P = window.PRESUPUESTO, M = window.PRESUPUESTO_MENSUAL;
  if (!P) return;
  const fila = {};
  const recorrer = f => { fila[f.id] = f; (f.hijos || []).forEach(recorrer); };
  P.partes.forEach(p => p.tablas.forEach(t => recorrer(t.fila)));
  P.datos.filas.forEach(f => { fila[f.id] = f; });
  const miles = (n, dec = 0) => {
    const [e, d] = Math.abs(n).toFixed(dec).split(".");
    return e.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (d ? "," + d : "");
  };
  const mill = n => "$" + miles(n / 1e6) + " millones";
  const v = id => (fila[id] && (fila[id].valor || fila[id].total) || [NaN])[0];
  const inv = v("r55"), util = v("r130"), veces = miles(util / inv, 1);

  // retorno de la inversión (tabla 14 y conclusión): las cifras reales en vez de «por cada $100 invertidos…»
  if (fila.r153) {
    fila.r153.nombre = fila.r153.nombre.replace("(ROI)", "(ROI, se dice «erre-o-i»)");
    fila.r153.palabras = `Se ponen ${mill(inv)} para empezar y en 10 años el negocio deja ${mill(util)} de utilidad neta: ${veces} veces lo invertido.`;
  }
  if (P.conclusion && P.conclusion.texto)
    P.conclusion.texto = P.conclusion.texto.replace(/\s*\(por cada \$100 invertidos se ganan \$[\d.]+\)/, ` (${veces} veces la inversión inicial)`);

  // inflación (datos del plan): con el precio real en vez de «lo que hoy vale $100…»
  if (fila.r22 && fila.r22.porque && M) {
    const precio = m => Math.round(M.precio_sin_iva[m] * (1 + M.iva));
    const m5 = M.anio.findIndex(a => a === 5);
    if (m5 > 0)
      fila.r22.porque = fila.r22.porque.replace(/lo que hoy vale \$100 en el año 5 vale \$125/,
        `el precio al público pasa de $${miles(precio(1))} en el año 1 a $${miles(precio(m5))} en el año 5`);
  }

  // canales de venta: qué es un marketplace y qué es una gran superficie (no son lo mismo)
  if (fila.r120) fila.r120.nombre = "Marketplaces: páginas web como Mercado Libre y Falabella.com (cobran ≈ 14 % de comisión)";
  if (fila.r121) fila.r121.nombre = "Grandes superficies: tiendas físicas que compran y revenden (Homecenter, Éxito, Alkosto; se quedan con ≈ 40 % y pagan a 60 días)";
})();
