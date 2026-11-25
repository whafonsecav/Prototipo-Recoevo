# -*- coding: utf-8 -*-
"""Guion de la presentación del 25-nov-2026 (ronda 2, «Negociando con Tiburones»: 5 min de pitch + 5 de preguntas).

Las palabras son EXACTAMENTE las notas del presentador de cada pantalla de la presentación de esa ronda
(repositorio whafonsecav/Recoevo2, index.html, <aside class="notas"> de cada <section class="diapo">; commit ab4afe3).
Aquí solo se agregan las marcas del teleprompter: **clave**  [[cifra]]  {gesto}. Cada {Clic} es un clic de la
presentación (el siguiente paso de la misma pantalla o la pantalla siguiente).

Si cambian las notas de la presentación, se cambian aquí y se revisa con:
    python generar_pitch.py <carpeta_web> --verificar <Recoevo2/index.html>
que compara palabra por palabra este guion (sin marcas) con las notas.
"""
import html as _html, re as _re

GUION_FINAL = [
  dict(t="Saludo", ancla="Buenas tardes: quiénes somos.", poster="Pantalla 1 · Portada",
       pregunta="¿Cómo abre la presentación?",
       pistas=["buenas tardes", "somos RECOEVO"],
       p=["Buenas tardes. Somos **RECOEVO**."]),
  dict(t="La comida que enterramos", ancla="33.300 t de basura al día, 60 % comida, Doña Juana y el Decreto 0772.", poster="Pantalla 2 · La comida que enterramos",
       pregunta="¿Qué cifras muestran el problema y qué dice la ley?",
       pistas=["33.300 t de basura al día", "60 % es comida", "Doña Juana: 6.800 t al día", "licencia hasta 2029", "Decreto 0772: separar orgánicos", "en la cocina no hay forma fácil"],
       p=["Cada día, Colombia entierra [[33.300 toneladas]] de basura.",
          "{Clic} Y el [[60 %]] es **comida**.",
          "{Clic} Solo a **Doña Juana** llegan [[6.800 toneladas]] al día, y su licencia vence en [[2029]].",
          "{Clic} Desde julio, el **Decreto 0772** obliga a separar los orgánicos. Pero en la cocina **no hay una forma fácil**."]),
  dict(t="El campo paga caro el abono", ancla="Urea +187 %, 94 % importado, 40 % de tierra degradada.", poster="Pantalla 3 · El campo paga caro el abono",
       pregunta="¿Qué pasa en el campo con el abono?",
       pistas=["urea subió 187 %", "guerra en Irán: volvió a subir", "94 % importado", "40 % de tierra degradada", "la ciudad entierra lo que el campo necesita"],
       p=["Y a pocos kilómetros, el **campo** paga caro el abono: el bulto de **urea** subió [[187 %]].",
          "{Clic} Y con la guerra en Irán **volvió a subir**.",
          "{Clic} Más del [[94 %]] del fertilizante es importado, y el [[40 %]] de la tierra está degradada.",
          "{Clic} **La ciudad entierra la comida que el campo necesita.**"]),
  dict(t="Trabajo de campo en Tihuaque", ancla="Lo que vimos y oímos en el barrio de Samuel.", poster="Pantalla 4 · Trabajo de campo en Tihuaque",
       pregunta="¿Qué encontraron en el trabajo de campo?",
       pistas=["Tihuaque, Usme: barrio de Samuel", "entrevistas, observación, 220 frases", "todos: el shut de la esquina", "75 % ratas o plagas", "63 % mezcla todo", "88 % costumbre y afán", "satisfacción < 2 de 5", "«todo es un revoltijo»", "nadie rechazó la idea"],
       p=["Lo vimos de cerca en **Tihuaque**, en Usme, el barrio de nuestro compañero **Samuel**: entrevistas, observación y [[220]] frases analizadas.",
          "{Clic} Todos señalaron el **shut** de la esquina; el [[75 %]] habló de ratas o plagas y el [[63 %]] mezcla todo.",
          "{Clic} ¿Por qué no separan? El [[88 %]] habla de **costumbre y afán**, y la satisfacción con la basura no llega a [[2 sobre 5]].",
          "{Clic} Una vecina lo dijo así: «**todo es un revoltijo**».",
          "{Clic} Pero **nadie rechazó la idea**. Lo que falta es una forma fácil."]),
  dict(t="RECOEVO: cómo funciona", ancla="Echa, pisa, corta, sin olor y entrega; el prototipo digital.", poster="Pantalla 5 · La solución en 3D",
       pregunta="¿Qué es RECOEVO y cómo funciona, paso a paso?",
       pistas=["triturador con el pie", "sin electricidad y sin olor", "1 echas: tapa abierta, pedal bloqueado", "2 pisas: cremallera y piñón", "13 cuchillas, tiras de 5 mm, < 1 min al día", "3 filtro de carbón, 6 meses", "4 bolsa cerrada cada 5 días", "18 piezas, 0 cables", "prototipo digital a escala real"],
       p=["Por eso creamos **RECOEVO**: un triturador de cocina que funciona **con el pie**. Sin electricidad y sin olor.",
          "{Clic} **Uno**: echas las cáscaras. Con la tapa abierta, el pedal se bloquea.",
          "{Clic} **Dos**: pisas. Una cremallera y un piñón hacen girar el eje.",
          "{Clic} [[Trece cuchillas]] de acero cortan en tiras de [[cinco milímetros]]: menos de un minuto al día.",
          "{Clic} **Tres**: un filtro de carbón atrapa el olor durante [[seis meses]].",
          "{Clic} Y **cuatro**: la bolsa sale cerrada cada [[5 días]] a la ruta de orgánicos.",
          "{Clic} Dieciocho piezas, cero cables. Es el **prototipo digital a escala real**: el primer dinero que pedimos fabrica los cinco primeros."]),
  dict(t="Sin luz y a precio de caneca", ancla="Cero energía y $199.900 frente a más de un millón.", poster="Pantalla 6 · Por qué RECOEVO",
       pregunta="¿Qué lo hace diferente?",
       pistas=["no gasta energía", "tarifa o racionamiento: sigue funcionando", "199.900: precio de caneca con pedal", "eléctrico: más de un millón"],
       p=["Y **no gasta energía**: si sube la tarifa o hay racionamiento, sigue funcionando.",
          "{Clic} Cuesta [[199.900 pesos]]: lo de una buena caneca con pedal. Un procesador eléctrico cuesta más de [[un millón]]."]),
  dict(t="Lo que esperamos lograr y los ODS", ancla="735.450 hogares, 769.728 t fuera del relleno y los ODS 12, 11 y 13.", poster="Pantalla 7 · Lo que esperamos lograr",
       pregunta="¿Cuál es el impacto en 10 años?",
       pistas=["735.450 hogares = 1 de cada 4", "0,87 kg por hogar al día (dato oficial)", "769.728 t fuera del relleno", "año 10: 544 t al día = 1 de cada 5 kilos", "ODS 12, 11 y 13"],
       p=["En diez años, [[735.450 hogares]] con RECOEVO: **uno de cada cuatro** hogares de Bogotá.",
          "{Clic} Con el dato oficial de Bogotá, [[0,87 kilos]] por hogar al día, son [[769.728 toneladas]] fuera del relleno.",
          "{Clic} En el año diez, [[544 toneladas]] cada día: **uno de cada cinco kilos** de comida de los hogares de Bogotá.",
          "{Clic} Y aporta a los **Objetivos de Desarrollo Sostenible** [[12, 11 y 13]]."]),
  dict(t="Modelo de negocio", ancla="Vender el producto por cuatro canales; comodato para estratos 1 y 2.", poster="Pantalla 8 · Modelo de negocio",
       pregunta="¿Cómo gana dinero y qué pasa con los estratos 1 y 2?",
       pistas=["vender el producto: 199.900", "lotes a empresas, conjuntos y alcaldías", "4 canales", "estratos 1 y 2: comodato, gratis"],
       p=["¿Cómo ganamos dinero? **Vendiendo el producto**: [[199.900]] a los hogares, y por lotes a empresas, conjuntos y alcaldías.",
          "{Clic} Por **cuatro canales**: marketplaces, lotes, tienda propia y grandes superficies.",
          "{Clic} ¿Y los estratos uno y dos? No les vendemos: la alcaldía o el conjunto compra el lote y se lo presta en **comodato**, gratis."]),
  dict(t="Las cifras", ancla="Inversión sin crédito, costo y ganancia por producto, equilibrio, recuperación y utilidad.", poster="Pantalla 9 · Las cifras, sin crédito",
       pregunta="¿Cuánto se invierte, cuánto cuesta y cuánto deja cada producto?",
       pistas=["5.520 M sin crédito", "105.584 M ÷ 735.450 = 143.564", "entran 208.139, quedan 41.974", "equilibrio 2.334/mes, mes 16", "recuperación mes 51", "utilidad 30.870 M; por cada 100 vuelven 559"],
       p=["Para arrancar necesitamos [[5.520 millones]] de pesos, y **sin crédito**: cero intereses.",
          "{Clic} ¿Y cuánto cuesta cada producto? En diez años la empresa gasta [[105.584 millones]] y vende [[735.450 productos]]: [[143.564 pesos]] cada uno, con todo incluido.",
          "{Clic} De cada producto entran [[208.139 pesos]]. Menos costos variables, fijos e impuesto, quedan [[41.974]] de **ganancia**.",
          "{Clic} El **equilibrio** son [[2.334 productos]] al mes: lo pasamos en el mes [[16]]. Y en el mes [[51]] **recuperamos la inversión**.",
          "{Clic} En diez años, la **utilidad neta** es de [[30.870 millones]]: por cada [[100]] pesos invertidos vuelven [[559]]."]),
  dict(t="El plan por etapas y lo que pedimos", ancla="Tres etapas; hoy solo la primera: $55 M por el 10 %.", poster="Pantalla 10 · El plan por etapas y el pedido",
       pregunta="¿Cómo se usa el dinero y qué le piden hoy al jurado?",
       pistas=["5.520 M, pero no de una vez", "3 meses sin fábrica: talleres de Bogotá", "10 familias de Tihuaque, 5 prototipos", "luego moldes y fábrica; año 1 de ventas", "hoy: 55 M por el 10 %", "el resto después, con datos"],
       p=["El plan completo cuesta [[5.520 millones]], pero **no lo pedimos de una vez**. Primero, [[tres meses]] sin fábrica: talleres de Bogotá hacen las piezas y [[diez familias]] de Tihuaque prueban [[cinco prototipos]]. Si funciona, vienen los moldes y la fábrica, y ahí arranca el año uno de ventas.",
          "{Clic} Por eso hoy les pedimos solo la primera parte: [[55 millones]], por el [[10 %]] de RECOEVO. El resto se pide después, **con datos en la mano**."]),
  dict(t="Cierre", ancla="La invitación a construirlo juntos.", poster="Pantalla 11 · Cierre",
       pregunta="¿Cómo cierra?",
       pistas=["construirlo con ustedes", "mil gracias"],
       p=["**Nos encantaría construirlo con ustedes.** Mil gracias."]),
]

PARTES_FINAL = [("El saludo y el problema", 1, 4), ("La solución", 5, 7), ("El negocio", 8, 10), ("El cierre", 11, 11)]


def _plano(s):
    """El texto tal como se dice: sin gestos ni marcas."""
    s = _re.sub(r"\{[^}]*\}\s*", "", s)
    s = s.replace("**", "").replace("[[", "").replace("]]", "").replace("~", "")
    return " ".join(s.split())


def verificar(ruta_index):
    """Compara el guion (sin marcas) con las notas de cada pantalla del index.html de la presentación."""
    h = open(ruta_index, encoding="utf-8").read()
    secs = _re.findall(r'<section class="diapo[^"]*"[^>]*data-titulo="([^"]+)"[^>]*>(.*?)</section>', h, _re.S)
    errores = []
    if len(secs) != len(GUION_FINAL):
        errores.append(f"pantallas: la presentación tiene {len(secs)} y el guion {len(GUION_FINAL)}")
    for i, ((tit, cuerpo), b) in enumerate(zip(secs, GUION_FINAL), 1):
        aside = _re.search(r'<aside class="notas">(.*?)</aside>', cuerpo, _re.S)
        notas = [" ".join(_html.unescape(_re.sub(r"<[^>]+>", "", x)).split())
                 for x in _re.findall(r'<p data-p="\d+">(.*?)</p>', aside.group(1) if aside else "", _re.S)]
        mias = [_plano(p) for p in b["p"]]
        if notas != mias:
            errores.append(f"pantalla {i} ({tit}):\n  notas: {notas}\n  guion: {mias}")
    return errores
