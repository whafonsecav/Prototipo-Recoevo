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
  dict(t="Portada", ancla="Saludo y qué es RECOEVO: una alternativa para aprovechar los residuos orgánicos.", poster="Pantalla 1 · Portada",
       pregunta="¿Cómo abre la presentación?",
       pistas=["buenas tardes a todos", "somos RECOEVO", "una alternativa para aprovechar los residuos orgánicos", "es decir, restos de comida de los hogares", "artefacto analógico, sin electricidad"],
       p=["Buenas tardes a todos. Somos **RECOEVO**, y venimos a presentarles una alternativa para aprovechar los **residuos orgánicos**, es decir, los restos de comida que se originan en los hogares. Esto, a través de un **artefacto analógico**, sin usar electricidad."]),

  dict(t="La comida que enterramos", ancla="Cuánta basura se entierra, cuánta es comida, Doña Juana y el Decreto 0772.", poster="Pantalla 2 · La comida que enterramos",
       pregunta="¿Qué cifras muestran el tamaño del problema y qué dice la ley?",
       pistas=["no sé si ustedes sabían", "33.300 t al día (Superservicios, 2024)", "60 % es comida (Secretaría del Hábitat)", "Doña Juana: 6.800 t al día (UAESP, 2026)", "licencia hasta 2029 (El Tiempo)", "Decreto 0772: separar orgánicos", "sin embargo: no hay forma fácil en la cocina"],
       p=["{Clic} No sé si ustedes sabían que cada día, en Colombia, se entierran [[33.300 toneladas]] de basura, según Superservicios, con datos de 2024.",
          "{Clic} Y que, según la Secretaría del Hábitat de Bogotá, cerca del [[60 %]] de esa basura **es comida**: cáscaras y sobras de nuestras cocinas.",
          "{Clic} Solo a **Doña Juana**, el relleno de Bogotá, llegan [[6.800 toneladas]] al día, según la UAESP este año, y su licencia vence en [[2029]], en tres años, según El Tiempo.",
          "{Clic} Por eso, desde julio, el **Decreto 0772** de este año obliga a separar los residuos orgánicos. Sin embargo, en la cocina **no existe una forma fácil y limpia** de hacerlo."]),

  dict(t="El campo paga caro el abono", ancla="El otro lado de la historia: la urea, lo que importamos y la ironía.", poster="Pantalla 3 · El campo paga caro el abono",
       pregunta="¿Qué pasa en el campo con el abono y cuál es la ironía?",
       pistas=["el otro lado de la historia", "urea: el abono químico más usado", "subió 187 % de 2021 a 2022 (DANE)", "este año volvió a subir: guerra en Irán (El Colombiano)", "94 % importado (El Colombiano)", "40 % de la tierra degradada (Asocompost, 2019)", "la ironía: la ciudad entierra lo que el campo necesita"],
       p=["{Clic} Miremos el otro lado de la historia: a pocos kilómetros, **el campo paga caro el abono**. El bulto de **urea**, el abono químico más usado, subió [[187 %]] de 2021 a 2022, según el DANE.",
          "{Clic} Y este año **volvió a subir** por la guerra en Irán, según El Colombiano.",
          "{Clic} Además, según ese diario, más del [[94 %]] del fertilizante es **importado**, y según Asocompost, en 2019, el [[40 %]] de la tierra agrícola estaba degradada.",
          "{Clic} Y aquí está la ironía: **la ciudad entierra la comida que el campo necesita** como abono."]),

  dict(t="Trabajo de campo en Tihuaque", ancla="Lo que vimos y lo que nos dijeron los vecinos en el barrio de Samuel.", poster="Pantalla 4 · Trabajo de campo en Tihuaque",
       pregunta="¿Qué encontraron en el trabajo de campo y qué les dio confianza?",
       pistas=["para verlo de cerca", "septiembre: Tihuaque, Usme, barrio de Samuel; 8 vecinos", "todos: el shut, el punto de basura de la esquina", "75 % ratas o plagas", "63 % mezcla todo", "88 % costumbre y afán", "«todo es un revoltijo»", "nadie rechazó la idea", "la gente sí quiere: falta una forma fácil"],
       p=["{Clic} Para verlo de cerca, en septiembre hicimos un trabajo de campo en **Tihuaque**, en Usme, el barrio de nuestro compañero **Samuel**, y entrevistamos a **ocho vecinos**.",
          "{Clic} Encontramos que **todos** señalaron el **shut**, es decir, el punto de basura de la esquina, como el gran problema. El [[75 %]] habló de ratas o plagas, y el [[63 %]] mezcla todo en la misma bolsa.",
          "{Clic} ¿Y por qué no separan? El [[88 %]] dice que es por **la costumbre y el afán**.",
          "{Clic} Una vecina lo resumió así: «**todo es un revoltijo**».",
          "{Clic} Pero lo más importante: **nadie rechazó la idea**. Más de la mitad la apoya, y el resto, con condiciones. Es decir, la gente sí quiere separar; falta **una forma fácil**."]),

  dict(t="RECOEVO: cómo funciona", ancla="Qué es y sus cuatro pasos: echar, pisar y cortar, sin olor, entregar.", poster="Pantalla 5 · La solución en 3D",
       pregunta="¿Qué es RECOEVO y cómo funciona, paso a paso?",
       pistas=["esa forma fácil es RECOEVO", "triturador que funciona con el pie", "primero: se echan las cáscaras; tapa abierta = pedal bloqueado", "segundo: se pisa; cremallera y piñón, sin motor", "13 cuchillas; 20 pisadas = menos de 40 segundos", "tercero: sin olor; filtro de carbón, medio año", "cuarto: bolsa cerrada cada 5 días", "prototipo digital a escala real"],
       p=["{Clic} Y esa forma fácil es **RECOEVO**: un triturador de cocina que funciona **con el pie**, sin electricidad y sin olor.",
          "{Clic} Funciona en cuatro pasos. **Primero, se echan las cáscaras;** con la tapa abierta, el pedal se bloquea.",
          "{Clic} **Segundo, se pisa.** Una cremallera y un piñón hacen girar el eje, sin motor.",
          "{Clic} El eje mueve [[13 cuchillas]] de acero que cortan los restos en tiras. Bastan unas [[20 pisadas]] al día, es decir, menos de [[40 segundos]].",
          "{Clic} **Tercero, sin olor:** un filtro de carbón en la tapa atrapa los olores durante medio año.",
          "{Clic} **Y cuarto, se entrega:** cada cinco días sale una **bolsa compostable cerrada**, lista para la ruta de orgánicos.",
          "{Clic} Lo que ven es el **prototipo digital a escala real**; el primer dinero que pedimos es para fabricar los físicos."]),

  dict(t="Sin luz y a precio de caneca", ancla="Cero energía y el precio frente a una caneca y a los eléctricos.", poster="Pantalla 6 · Por qué RECOEVO",
       pregunta="¿Qué lo hace diferente de lo que ya existe?",
       pistas=["¿por qué RECOEVO y no otra opción?", "no gasta energía: tarifa o racionamiento", "199.900: cerca de una buena caneca", "la caneca solo guarda", "eléctrico: más de un millón (Homecenter y tiendas en línea, octubre)"],
       p=["{Clic} ¿Y por qué RECOEVO y no otra opción? Primero, porque **no gasta energía**: si sube la tarifa o hay racionamiento, sigue funcionando.",
          "{Clic} Y segundo, por su precio: [[199.900 pesos]], cerca de una buena caneca con pedal, que solo guarda la basura; uno eléctrico cuesta más de [[un millón]], según precios de octubre en Homecenter y tiendas en línea."]),

  dict(t="Lo que esperamos lograr y los ODS", ancla="Hogares, toneladas fuera del relleno y los tres ODS.", poster="Pantalla 7 · Lo que esperamos lograr",
       pregunta="¿Cuál es el impacto en diez años y con qué ODS se alinea?",
       pistas=["¿qué esperamos lograr?", "Usme → el resto de Bogotá", "735.450 hogares = 1 de cada 4 de los ≈ 2,9 M que tiene hoy Bogotá (DANE, Encuesta Multipropósito 2025)", "UAESP y DANE: 0,87 kg por hogar al día", "llegan poco a poco: 769.728 t en 10 años", "año 10: 544 t al día = 1 de cada 5 kilos", "más que un negocio: ODS 12 abono, 11 menos ratas, 13 metano"],
       p=["{Clic} ¿Y qué esperamos lograr? Empezamos en Usme y seguimos con el resto de Bogotá: en diez años llegamos a [[735.450 hogares]], es decir, **uno de cada cuatro** de los que tiene hoy Bogotá, según el DANE en 2025.",
          "{Clic} Con **datos oficiales** de la UAESP y del DANE, cada hogar bota [[0,87 kilos]] de comida al día. Como los hogares llegan poco a poco, en diez años son [[769.728 toneladas]] que no llegan al relleno.",
          "{Clic} Y en el año diez serían [[544 toneladas]] cada día, es decir, **uno de cada cinco kilos** de la comida que botan los hogares de Bogotá.",
          "{Clic} Por eso es más que un negocio: aporta a tres **Objetivos de Desarrollo Sostenible** de la ONU. Al [[12]], consumo responsable, porque la comida **vuelve a la tierra** como abono en vez de enterrarse. Al [[11]], ciudades sostenibles: **menos bolsas rotas y menos ratas** en las esquinas. Y al [[13]], el clima: la comida enterrada suelta **metano**, ochenta veces más dañino que el CO₂, según El Tiempo; sin ella en el relleno, estimamos evitar unas [[385.000 toneladas]] de gases en diez años."]),

  dict(t="Modelo de negocio", ancla="A quién se vende, por qué canales y el comodato para estratos 1 y 2.", poster="Pantalla 8 · Modelo de negocio",
       pregunta="¿Cómo gana dinero, por qué canales y qué pasa con los estratos 1 y 2?",
       pistas=["pasemos al negocio", "ganamos vendiendo el producto", "hogares: en cuotas", "lotes de 100 o más: 15 % menos", "el decreto también obliga a las empresas", "4 canales: marketplaces, lotes, tienda en línea, grandes superficies", "estratos 1 y 2: comodato = préstamo gratuito"],
       p=["{Clic} Pasemos al negocio: ganamos **vendiendo el producto**. A los hogares, que pueden pagar en cuotas; y a empresas, conjuntos y alcaldías, por lotes de cien o más, un [[15 %]] más barato.",
          "{Clic} Vendemos por **cuatro canales**: marketplaces, lotes, tienda en línea y grandes superficies.",
          "{Clic} ¿Y los estratos uno y dos? No les vendemos: la alcaldía o el conjunto compra el lote y se lo presta en **comodato**, es decir, gratis."]),

  dict(t="Las cifras", ancla="Inversión, costo y ganancia por producto, equilibrio, recuperación y utilidad.", poster="Pantalla 9 · Las cifras, sin crédito",
       pregunta="¿Cuánto se invierte, cuánto cuesta y cuánto deja cada producto, y cuándo se recupera?",
       pistas=["los números de nuestro plan financiero a diez años", "5.530 M, sin crédito: sin intereses", "105.593 M = todo: variables + fijos", "÷ 735.450 = 143.576", "entran 208.139: sin IVA, con inflación", "quedan 41.966 por producto", "equilibrio 2.334 al mes: mes 16 = 1 año y 4 meses", "recuperación: mes 51 = 4 años y 3 meses", "utilidad neta = lo que queda tras costos e impuestos: 30.864 M", "por cada 100 vuelven 558"],
       p=["{Clic} Ahora, los números de **nuestro plan financiero** a diez años. Para arrancar necesitamos [[5.530 millones]] de pesos, de socios e inversionistas, **sin crédito**, es decir, sin intereses.",
          "{Clic} ¿Cuánto cuesta cada producto? En diez años la empresa gasta en total [[105.593 millones]]: **costos variables**, como los materiales, que suben con cada producto, y **costos fijos**, como la planta y las máquinas, que se pagan aunque no se venda. Dividido entre los [[735.450 productos]] vendidos, cada uno cuesta [[143.576 pesos]].",
          "{Clic} ¿Y cuánto deja? En promedio entran [[208.139 pesos]], sin IVA y con la inflación de diez años; restando costos e impuestos, quedan [[41.966]] de **ganancia**.",
          "{Clic} El **punto de equilibrio**, es decir, lo que hay que vender para no perder, son [[2.334 productos]] al mes; lo alcanzamos en el mes [[16]], es decir, al año y cuatro meses de vender. Y **recuperamos la inversión** en el mes [[51]]: a los cuatro años y tres meses.",
          "{Clic} En diez años, la **utilidad neta**, es decir, lo que le queda a la empresa después de pagar todos los costos y los impuestos, es de [[30.864 millones]]: por cada [[100]] pesos invertidos, vuelven [[558]]."]),

  dict(t="El plan por etapas y lo que pedimos", ancla="Las tres etapas con sus metas y el pedido de hoy: $63 M por el 10 %.", poster="Pantalla 10 · El plan por etapas y el pedido",
       pregunta="¿Cómo se usa el dinero por etapas y qué le piden hoy al jurado?",
       pistas=["inversión grande: va en tres etapas", "validar: 4 meses, sin fábrica, talleres de Bogotá", "diseño listo para fabricar, pruebas, marca y 10 prototipos", "10 prototipos, uno por familia: 3 meses de prueba (un hábito tarda 66 días: estudio de Londres, 2010)", "nosotros recogemos las bolsas, las pesamos y las llevamos a compostar", "meta: 8 de cada 10 familias lo usan a diario", "luego preserie y fábrica; ventas al año y dos meses", "hoy: 63 M por el 10 %", "vale hoy ≈ 552 M; con los 63 M ≈ 615 M; 63 = 10 %", "parte del total, no adicional", "primera opción en las siguientes etapas"],
       p=["{Clic} Sabemos que es una inversión grande, por eso va en tres etapas. La primera es **validar**, en cuatro meses y sin fábrica: dejamos el diseño listo para fabricar, lo probamos, protegemos la marca y armamos **diez prototipos, uno por familia**, para que **diez familias** de Tihuaque lo usen **tres meses**, el tiempo que tarda un hábito según un estudio de Londres de 2010. Nosotros mismos recogemos las bolsas cada semana, las pesamos y las llevamos a compostar. Si ocho de cada diez familias lo usan a diario, siguen la **preserie** y la **fábrica**, y al año y dos meses arrancan las ventas.",
          "{Clic} Por eso hoy les pedimos solo esa primera etapa: [[63 millones]] por el [[10 %]] de RECOEVO. Hoy RECOEVO vale unos [[552 millones]]; con sus 63 adentro, unos [[615]]: por eso, el **10 %**. Es parte del total, y si cumplimos la meta, ustedes tienen la **primera opción** en las siguientes etapas."]),

  dict(t="Cierre", ancla="La historia en una frase y el siguiente paso, con ustedes.", poster="Pantalla 11 · Cierre",
       pregunta="¿Cómo cierra y qué invita a hacer?",
       pistas=["para cerrar", "hoy: la comida termina enterrada", "con RECOEVO vuelve a ser vida", "siguiente paso: 10 familias de Tihuaque", "con ustedes", "menos relleno, más vida", "muchas gracias"],
       p=["{Clic} Para cerrar: con RECOEVO, la comida de nuestras cocinas deja de ir al relleno y **vuelve a ser vida**. Nuestro siguiente paso son las diez familias de Tihuaque, y nos encantaría darlo **con ustedes**. **Menos relleno, más vida.** Muchas gracias."]),
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
