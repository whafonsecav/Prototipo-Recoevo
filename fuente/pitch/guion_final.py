# -*- coding: utf-8 -*-
"""Guion del teleprompter para la presentación del 25-nov-2026 (ronda 2, «Negociando con Tiburones»: pitch + preguntas).

Regla de William (24-nov-2026): las láminas guían el guion. Cada párrafo de cada pantalla es UN clic de la
presentación (repositorio whafonsecav/Recoevo2, index.html: un <p data-p="N"> en las notas de cada pantalla) y
habla SOLO de lo que aparece en la lámina en ese momento; nunca se adelanta un tema de una lámina posterior.
Estilo pedido: sencillo pero profesional, cercano sin ser formal, neutro, con conectores entre párrafos y temas,
y explicando cada cifra para que no queden dudas. Duración: 5 minutos, máximo 7.

Marcas del teleprompter: **clave**  [[cifra]]  {gesto}. {Clic} = un clic de la presentación (el siguiente paso
de la misma lámina o la lámina siguiente).

Si cambian los pasos de la presentación, se revisa con:
    python generar_pitch.py <carpeta_web> --verificar <Recoevo2/index.html>
que comprueba que cada pantalla tenga tantos párrafos como pasos tiene la lámina.
"""
import re as _re

GUION_FINAL = [
  dict(t="Portada", ancla="Quiénes somos y qué hace RECOEVO, en una frase.", poster="Pantalla 1 · Portada",
       pregunta="¿Cómo abre la presentación?",
       pistas=["buenas tardes", "somos RECOEVO", "restos de comida, sin electricidad", "empecemos por el problema"],
       p=["Buenas tardes. Somos **RECOEVO**, y venimos a mostrarles cómo aprovechar los restos de comida de la cocina **sin usar electricidad**. Empecemos por el problema."]),

  dict(t="La comida que enterramos", ancla="Cuánta basura se entierra, cuánta es comida, Doña Juana y el Decreto 0772.", poster="Pantalla 2 · La comida que enterramos",
       pregunta="¿Qué cifras muestran el tamaño del problema y qué dice la ley?",
       pistas=["33.300 t al día", "60 % es comida", "Doña Juana: 6.800 t al día", "licencia hasta 2029: en tres años", "Decreto 0772: separar orgánicos", "falta una forma fácil en la cocina"],
       p=["{Clic} Cada día, Colombia entierra [[33.300 toneladas]] de basura.",
          "{Clic} Y el [[60 %]] **es comida**: cáscaras y sobras que salen de nuestras cocinas.",
          "{Clic} Solo en Bogotá, a **Doña Juana** llegan [[6.800 toneladas]] al día, y su licencia vence en [[2029]], o sea, en tres años.",
          "{Clic} Por eso, desde julio, el **Decreto 0772** obliga a separar los orgánicos. Pero en la cocina **no hay una forma fácil y limpia** de hacerlo."]),

  dict(t="El campo paga caro el abono", ancla="La urea, lo que importamos y la ironía: la ciudad entierra lo que el campo necesita.", poster="Pantalla 3 · El campo paga caro el abono",
       pregunta="¿Qué pasa en el campo con el abono y cuál es la ironía?",
       pistas=["urea: el abono químico más usado", "subió 187 % de 2021 a 2022", "este año volvió a subir: guerra en Irán", "94 % importado", "40 % de la tierra degradada", "la ciudad entierra lo que el campo necesita"],
       p=["{Clic} Y a pocos kilómetros, **el campo paga caro el abono**: el bulto de **urea**, el abono químico más usado, subió [[187 %]] entre 2021 y 2022.",
          "{Clic} Y este año **volvió a subir**, por la guerra en Irán.",
          "{Clic} Además, más del [[94 %]] del fertilizante del país es **importado**, y el [[40 %]] de la tierra agrícola está degradada.",
          "{Clic} Esa es la ironía: **la ciudad entierra la comida que el campo necesita** como abono."]),

  dict(t="Trabajo de campo en Tihuaque", ancla="Lo que vimos y lo que nos dijeron los vecinos en el barrio de Samuel.", poster="Pantalla 4 · Trabajo de campo en Tihuaque",
       pregunta="¿Qué encontraron en el trabajo de campo y qué les dio confianza?",
       pistas=["Tihuaque, Usme: barrio de Samuel", "entrevistas y recorrido; las fotos son de ese día", "todos: el shut de la esquina", "75 % ratas o plagas", "63 % mezcla todo", "88 % costumbre y afán", "«todo es un revoltijo»", "nadie rechazó la idea", "falta una forma fácil"],
       p=["{Clic} Lo vimos de cerca en **Tihuaque**, en Usme, el barrio de nuestro compañero **Samuel**: entrevistamos a los vecinos, y estas fotos son de ese día.",
          "{Clic} **Todos** señalaron el **shut**, el punto de basura de la esquina, como el foco del problema. El [[75 %]] habló de ratas o plagas, y el [[63 %]] mezcla todo en la misma bolsa.",
          "{Clic} ¿Y por qué no separan? El [[88 %]] dice que es **la costumbre y el afán**.",
          "{Clic} Una vecina lo resumió así: «**todo es un revoltijo**».",
          "{Clic} Pero **nadie rechazó la idea**: más de la mitad la apoya, y el resto la apoya con condiciones. Lo que falta es **una forma fácil**."]),

  dict(t="RECOEVO: cómo funciona", ancla="Qué es y sus cuatro pasos: echa, pisa y corta, sin olor, entrega.", poster="Pantalla 5 · La solución en 3D",
       pregunta="¿Qué es RECOEVO y cómo funciona, paso a paso?",
       pistas=["triturador que funciona con el pie", "sin electricidad y sin olor", "1 echa: tapa abierta = pedal bloqueado", "2 pisa: cremallera y piñón, sin motor", "13 cuchillas, 20 pisadas, menos de 40 segundos", "3 sin olor: filtro de carbón, medio año", "4 entrega: bolsa cerrada cada 5 días", "18 piezas, cero cables", "prototipo digital a escala real"],
       p=["{Clic} Y esa forma fácil es **RECOEVO**: un triturador de cocina que funciona **con el pie**, sin electricidad y sin olor.",
          "{Clic} **Uno: se echan las cáscaras.** Mientras la tapa está abierta, el pedal se bloquea, por seguridad.",
          "{Clic} **Dos: se pisa.** El pedal mueve una cremallera y un piñón que hacen girar el eje, sin motor.",
          "{Clic} Ese eje mueve [[13 cuchillas]] de acero que cortan los restos en tiras pequeñas. Bastan unas [[20 pisadas]] al día: menos de [[40 segundos]].",
          "{Clic} **Tres: sin olor.** Un filtro de carbón en la tapa atrapa el olor durante seis meses, o sea, medio año.",
          "{Clic} **Y cuatro: se entrega.** Cada cinco días sale una **bolsa compostable cerrada**, lista para la ruta de orgánicos.",
          "{Clic} Son [[18 piezas]] y cero cables. Es el **prototipo digital a escala real**: el primer dinero que pedimos fabrica los primeros prototipos físicos."]),

  dict(t="Sin luz y a precio de caneca", ancla="Cero energía y el precio frente a una caneca y a los eléctricos.", poster="Pantalla 6 · Por qué RECOEVO",
       pregunta="¿Qué lo hace diferente de lo que ya existe?",
       pistas=["no gasta energía: tarifa o racionamiento", "199.900: lo de una buena caneca", "la caneca solo guarda", "eléctrico: más de un millón"],
       p=["{Clic} ¿Y por qué RECOEVO? Primero, porque **no gasta energía**: si sube la tarifa o hay racionamiento, sigue funcionando.",
          "{Clic} Y segundo, por el precio: [[199.900 pesos]], cerca de lo que vale una buena caneca con pedal, que solo guarda la basura. Un procesador eléctrico cuesta más de [[un millón]]."]),

  dict(t="Lo que esperamos lograr y los ODS", ancla="Hogares, toneladas fuera del relleno y los tres ODS.", poster="Pantalla 7 · Lo que esperamos lograr",
       pregunta="¿Cuál es el impacto en diez años y con qué ODS se alinea?",
       pistas=["Usme → Bogotá → el país", "735.450 hogares = 1 de cada 4 de Bogotá", "dato oficial: 0,87 kg por hogar al día", "769.728 t en 10 años", "año 10: 544 t al día = 1 de cada 5 kilos", "ODS 12, 11 y 13: metano"],
       p=["{Clic} ¿Qué esperamos lograr? Empezamos en Usme, luego Bogotá y el país. En diez años, [[735.450 hogares]] con RECOEVO: **uno de cada cuatro hogares de Bogotá**.",
          "{Clic} Con el **dato oficial de Bogotá**, [[0,87 kilos]] de comida por hogar al día, son [[769.728 toneladas]] que en esos diez años no llegan al relleno.",
          "{Clic} Y en el año diez serán [[544 toneladas]] cada día: **uno de cada cinco kilos** de la comida que hoy botan los hogares de Bogotá.",
          "{Clic} Por eso esto es más que un negocio. Aporta a tres **Objetivos de Desarrollo Sostenible**: el [[12]], consumo responsable; el [[11]], ciudades sostenibles; y el [[13]], acción por el clima, porque la comida enterrada suelta **metano**."]),

  dict(t="Modelo de negocio", ancla="A quién se vende, por qué canales y el comodato para estratos 1 y 2.", poster="Pantalla 8 · Modelo de negocio",
       pregunta="¿Cómo gana dinero, por qué canales y qué pasa con los estratos 1 y 2?",
       pistas=["ganamos vendiendo el producto", "hogares: 199.900, en cuotas", "lotes de 100 o más: 15 % menos", "el decreto también obliga a las empresas", "4 canales: marketplaces, lotes, tienda en línea, grandes superficies", "estratos 1 y 2: comodato, gratis"],
       p=["{Clic} ¿Cómo ganamos dinero? **Vendiendo el producto**: a los hogares, a [[199.900]] con IVA y en cuotas; y a empresas, conjuntos y alcaldías, por lotes de cien o más, un [[15 %]] más barato, porque el decreto también los obliga.",
          "{Clic} Vendemos por **cuatro canales**: marketplaces como Mercado Libre, lotes, nuestra tienda en línea y grandes superficies como Homecenter.",
          "{Clic} ¿Y los estratos uno y dos? A ellos no les vendemos: la alcaldía o el conjunto compra el lote y se lo presta al hogar en **comodato**, gratis. Así cumplen el decreto sin pagar nada."]),

  dict(t="Las cifras", ancla="Inversión, costo y ganancia por producto, equilibrio, recuperación y utilidad.", poster="Pantalla 9 · Las cifras, sin crédito",
       pregunta="¿Cuánto se invierte, cuánto cuesta y cuánto deja cada producto, y cuándo se recupera?",
       pistas=["5.520 M, sin crédito", "105.584 M ÷ 735.450 = 143.564", "entran 208.139: promedio de 10 años, sin IVA", "quedan 41.974 por producto", "equilibrio 2.334 al mes: mes 16 = 1 año y 4 meses", "recuperación: mes 51 = 4 años y 3 meses", "utilidad 30.870 M: por cada 100 vuelven 559"],
       p=["{Clic} Vamos a los números del plan a diez años. Para arrancar necesitamos [[5.520 millones]] de pesos, que ponen socios e inversionistas, **sin crédito**: cero intereses.",
          "{Clic} ¿Cuánto cuesta cada producto? En diez años se gastan [[105.584 millones]] y se venden [[735.450 productos]]: [[143.564 pesos]] cada uno, todo incluido.",
          "{Clic} ¿Y cuánto deja? Entran en promedio [[208.139 pesos]] por producto, ya sin IVA y con la inflación de los diez años. Menos costos e impuestos, quedan [[41.974 pesos]] de **ganancia**.",
          "{Clic} El **punto de equilibrio** es de [[2.334 productos]] al mes, y lo pasamos en el mes [[16]], o sea, al año y cuatro meses de empezar a vender. Y **recuperamos toda la inversión** en el mes [[51]]: a los cuatro años y tres meses.",
          "{Clic} En diez años, la **utilidad neta**, la ganancia limpia, es de [[30.870 millones]]: por cada [[100]] pesos invertidos vuelven [[559]]."]),

  dict(t="El plan por etapas y lo que pedimos", ancla="Las tres etapas con sus metas y el pedido de hoy: $55 M por el 10 %.", poster="Pantalla 10 · El plan por etapas y el pedido",
       pregunta="¿Cómo se usa el dinero por etapas y qué le piden hoy al jurado?",
       pistas=["no pedimos todo de una vez: 3 etapas", "validar: 3 meses, sin fábrica", "5 prototipos se turnan entre 10 familias: 5 y 5, seis semanas cada grupo", "meta: 8 de cada 10 lo usan a diario", "preserie y fábrica: al año y un mes, ventas", "hoy: 55 M por el 10 %", "parte de los 5.520", "primera opción en las etapas 2 y 3"],
       p=["{Clic} Y como es mucho dinero, no lo pedimos de una vez: son tres etapas. Primero, **validar**: tres meses, sin fábrica. Talleres de Bogotá hacen las piezas y armamos **cinco prototipos**, que se turnan entre **diez familias** de Tihuaque: cinco familias los usan seis semanas y luego pasan a las otras cinco. Si ocho de cada diez familias lo usan a diario, siguen la **preserie** y la **fábrica**, y al año y un mes de empezar, arrancan las ventas.",
          "{Clic} Por eso hoy les pedimos solo la primera etapa: [[55 millones]] por el [[10 %]] de RECOEVO. Son parte del total, no algo aparte, y si cumplimos, ustedes tienen la **primera opción** en las siguientes etapas."]),

  dict(t="Cierre", ancla="La idea en una frase y el siguiente paso, con ustedes.", poster="Pantalla 11 · Cierre",
       pregunta="¿Cómo cierra y qué invita a hacer?",
       pistas=["hoy: la comida termina enterrada", "con RECOEVO vuelve a ser vida", "siguiente paso: 10 familias de Tihuaque", "con ustedes", "menos relleno, más vida", "mil gracias"],
       p=["{Clic} Hoy, la comida de nuestras cocinas termina enterrada mientras el campo paga caro el abono. Con RECOEVO, esa comida **vuelve a ser vida**. Nuestro siguiente paso son las diez familias de Tihuaque, y nos encantaría darlo **con ustedes**. **Menos relleno, más vida.** Mil gracias."]),
]

PARTES_FINAL = [("El saludo y el problema", 1, 4), ("La solución", 5, 7), ("El negocio", 8, 10), ("El cierre", 11, 11)]


def verificar(ruta_index):
    """Comprueba que el guion siga las láminas: mismas pantallas, en el mismo orden, y un párrafo por cada clic."""
    h = open(ruta_index, encoding="utf-8").read()
    secs = _re.findall(r'<section class="diapo[^"]*"[^>]*data-titulo="([^"]+)"[^>]*>(.*?)</section>', h, _re.S)
    errores = []
    if len(secs) != len(GUION_FINAL):
        errores.append(f"pantallas: la presentación tiene {len(secs)} y el guion {len(GUION_FINAL)}")
    for i, ((tit, cuerpo), b) in enumerate(zip(secs, GUION_FINAL), 1):
        aside = _re.search(r'<aside class="notas">(.*?)</aside>', cuerpo, _re.S)
        pasos = len(_re.findall(r'<p data-p="\d+">', aside.group(1) if aside else ""))
        if tit != b["t"] and not (i == 1 and b["t"] == "Portada"):
            errores.append(f"pantalla {i}: la lámina se llama «{tit}» y el guion «{b['t']}»")
        if pasos != len(b["p"]):
            errores.append(f"pantalla {i} ({tit}): la lámina tiene {pasos} clics y el guion {len(b['p'])} párrafos")
        clics = sum(1 for p in b["p"] if p.startswith("{Clic}"))
        esperados = len(b["p"]) - (1 if i == 1 else 0)
        if clics != esperados:
            errores.append(f"pantalla {i} ({tit}): {clics} marcas {{Clic}} y deberían ser {esperados}")
    return errores
