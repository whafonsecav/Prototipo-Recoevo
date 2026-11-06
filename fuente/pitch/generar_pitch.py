# -*- coding: utf-8 -*-
"""Genera la página del pitch de RECOEVO (E-Fest 2026-2) para la web oficial: pitch/index.html.

Uso:  python generar_pitch.py <carpeta_web>            -> escribe <carpeta_web>/pitch/index.html
      python generar_pitch.py <carpeta_web> --medir    -> solo imprime la duración de cada bloque
      python generar_pitch.py <carpeta_web> --suelto <archivo.html>  -> versión que abre sin la web (para Drive)

El guion vive en GUION (abajo). Marcas: **clave**  [[cifra]]  {gesto}  ~frase que se puede quitar~
Todas las cifras salen del póster y del presupuesto ejecutivo realista (3-nov-2026); las de Usme, de las
fuentes citadas en FUENTES_USME.
"""
import base64, html, math, pathlib, re, sys

RITMO = 2.8          # palabras habladas por segundo: ritmo de conversación (unas 168 por minuto)
PAUSA_INICIO = 2     # segundos de silencio antes de empezar
RESPIRO = 0.5        # segundos entre bloques (un solo presentador: sin relevos)

# ------------------------------------------------------------------ EL GUION (un presentador)
GUION = [
  dict(t="El problema de la basura", ancla="Bolsas rotas, la comida que se entierra y Doña Juana.", poster="Póster 01 · cifras rosadas «En la ciudad»",
       pregunta="¿Con qué pregunta abre y qué cifras muestran el tamaño del problema?",
       pistas=["bolsa rota en la calle", "líquido y ese olor", "no es plástico: es comida", "2024: 33.300 t al día", "60 % es comida", "Doña Juana: 6.800 t al día", "licencia hasta 2029"],
       p=["{Pausa. Mire al jurado antes de hablar.} ¿Quién de ustedes no ha visto una **bolsa de basura rota** en la calle? Desgarrada, con un líquido oscuro regado por el andén… y ese olor que uno prefiere no respirar. Lo que se riega ahí casi nunca es plástico: **es comida**.",
          "{Señale las cifras rosadas.} En 2024, Colombia enterró [[33.300 toneladas]] de basura al día, y cerca del [[60 %]] era comida. Solo a **Doña Juana** llegan [[6.800 toneladas]] diarias, y su licencia se vence en [[2029]]."]),
  dict(t="Lo que vimos en Villa Rosita", ancla="El barrio de nuestro compañero y lo que encontramos en el trabajo de campo.", poster="Póster 01 · fotos del campo y cifras del trabajo de campo",
       pregunta="¿Dónde nació la idea? ¿Qué encontraron en el trabajo de campo con los vecinos?",
       pistas=["no es una cifra", "nuestro compañero Samuel: Villa Rosita, Usme; lo vive a diario", "trabajo de campo en su barrio", "100 %: el shut de la esquina", "lo encontramos desbordado", "perrito buscando comida en un icopor", "75 %: perros, ratas o plagas", "63 %: mezcla todo en la misma bolsa", "«todo es un revoltijo»", "falta conciencia; nadie rechazó la idea; falta una forma fácil"],
       p=["Para nosotros esto no es una cifra. {Señale a su compañero.} Nuestro compañero **Samuel** vive en **Villa Rosita, en Usme**. Él lo vive todos los días, y esta idea nació en su cuadra.",
          "Por eso hicimos un trabajo de campo en su barrio. En las conversaciones con los vecinos, el [[100 %]] señaló el mismo **shut** de la esquina, y cuando fuimos lo encontramos desbordado~, a pesar del aviso de multa~. Vimos un **perrito** buscando comida en un icopor tirado, y el [[75 %]] nos habló de **perros, ratas o plagas**. Más de la mitad, el [[63 %]], **mezcla todo** en la misma bolsa; alguien nos lo dijo sin rodeos: «Las cáscaras de la papa, el cartón, las cáscaras de huevo… **todo es un revoltijo**».",
          "Falta conciencia, sí. Pero nadie rechazó la idea: **lo que falta es una forma fácil**."]),
  dict(t="El problema de los campesinos", ancla="La ironía: el abono que necesitan y lo caro que les sale.", poster="Póster 01 · «En el campo»",
       pregunta="¿Cuál es la ironía? ¿Qué podría hacer el campo con esos restos y qué hacemos nosotros?",
       pistas=["a pocos kilómetros, en la Sabana", "campesinos podrían usarlos como abono", "los mezclamos: terminan en el relleno", "el abono les sale caro", "urea = abono químico más usado", "enero 2021 → enero 2022: de 80.000 a 230.000", "subió 187 %"],
       p=["Y aquí viene lo **irónico**: a pocos kilómetros de ese shut, en la Sabana, hay **campesinos** que podrían usar esos restos como **abono**. ~Incluso la mitad de los vecinos con los que hablamos nos mencionó el abono.~ Pero los mezclamos con todo, y terminan **enterrados en el relleno**.",
          "{Señale «En el campo».} Y a ellos el abono les sale caro: entre enero de 2021 y enero de 2022, el bulto de **urea**, el abono químico más usado, pasó de [[80.000 a 230.000 pesos]]: subió [[187 %]]. ~Y más del [[94 %]] del fertilizante del país es importado.~"]),
  dict(t="La ley: Decreto 0772", ancla="Ya es obligatorio separar, pero en la cocina no hay cómo.", poster="Póster 01 · recuadro azul del decreto",
       pregunta="¿Qué obliga el Decreto 0772 de 2026 y qué falta?",
       pistas=["conector: un dato importante", "desde julio ya existe una ley", "Decreto 0772 de 2026", "todos los hogares deben separar los orgánicos", "en la cocina no hay una forma fácil y limpia", "de ahí nació RECOEVO"],
       p=["{Señale el recuadro azul.} Y aquí hay un dato importante: en el tema de los residuos orgánicos, desde julio ya existe una ley. El **Decreto 0772 de 2026** obliga a todos los hogares a **separar los orgánicos**. O sea, separar ya no es opcional; el problema es que en la cocina no hay una forma fácil y limpia de hacerlo. **Y de ahí nació RECOEVO.**"]),

  dict(t="La solución: RECOEVO", ancla="El código QR, el prototipo en 3D y cómo se usa.", poster="Póster 02 y 03 · el código QR, el prototipo y «Así funciona»",
       pregunta="¿Qué le pide al jurado antes de explicar? ¿Qué es RECOEVO y cómo se usa?",
       pistas=["escanear el QR", "todo el proyecto", "primer enlace: prototipo 3D", "moverlo y desarmarlo pieza por pieza", "prototipo inicial", "triturador que funciona con el pie", "sin electricidad y sin olor", "pisar 20 segundos al día", "13 cuchillas", "bolsa compostable"],
       p=["{Señale el código QR.} Antes de contarles cómo funciona, les pedimos el favor de **escanear este código QR**: ahí está todo el proyecto, y en el primer enlace pueden mover el **prototipo en 3D** y desarmarlo pieza por pieza. Es un prototipo inicial.",
          "{Señale el prototipo.} RECOEVO es un **triturador de cocina que funciona con el pie**, sin electricidad y sin olor. Uno echa las cáscaras, pisa unos [[20 segundos]] al día, y [[trece cuchillas]] las cortan y las dejan en una **bolsa compostable**."]),
  dict(t="Por qué RECOEVO y no otro", ancla="Frente a canecas y eléctricos, y cómo responde a cada dolor.", poster="Póster 03 · precios frente al mercado y Value Proposition Canvas",
       pregunta="¿Qué lo hace diferente de lo que ya existe? ¿Cómo responde a lo que contaron los vecinos?",
       pistas=["caneca con pedal: solo guarda", "eléctrico: más de un millón y gasta luz", "RECOEVO: 199.900 con IVA", "lo de una buena caneca, pero tritura y no huele", "si huele: filtro de carbón", "si los perros la rompen: queda cerrada en el balde", "si parece difícil: veinte segundos al día"],
       p=["{Señale la barra de precios.} ¿Y qué lo hace diferente? Una caneca con pedal solo guarda la basura, y un procesador eléctrico cuesta más de [[un millón]] de pesos y gasta luz. RECOEVO cuesta [[199.900]] con IVA: lo que vale una buena caneca, pero **tritura y no huele**.",
          "{Señale el Value Proposition Canvas.} Y lo diseñamos con lo que nos contaron los vecinos: si la bolsa huele, el **filtro de carbón** lo resuelve; si los perros la rompen, aquí queda **cerrada dentro del balde**; y si separar parece difícil, son **veinte segundos al día**."]),
  dict(t="El impacto que esperamos", ancla="Usme, Bogotá, hogares, toneladas y porcentajes.", poster="Póster 03 · recuadro verde de 406.983 t · bloque 05 (mercado)",
       pregunta="¿Por qué empezar en Usme? ¿Cuántos hogares de cuántos y cuánta comida sale de Doña Juana?",
       pistas=["Usme: validamos, vía a Doña Juana, 85 % campo", "luego Bogotá: 2,9 millones de hogares", "10 años: 735.450 hogares, uno por hogar", "= 1 de cada 4 hogares de Bogotá", "medio kilo por hogar al día: menos de la mitad de lo que dice la UAESP", "los hogares llegan poco a poco: 16.200 el año 1 → 735.450 el año 10", "10 años: 407.000 t = 2 meses de Doña Juana = 1,6 %", "año 10, con todos: 288 t al día = 4 %"],
       p=["Vamos a empezar por **Usme**: allá validamos el problema, Doña Juana queda en la vía a Usme, y el [[85 %]] de Usme es campo~, con unos [[17.000 campesinos]]~. Ahí los dos problemas viven juntos.",
          "Después seguimos con **Bogotá**, que tiene unos [[2,9 millones de hogares]], y luego con otras ciudades. La meta es que en diez años [[735.450 hogares]] tengan su RECOEVO: es como **uno de cada cuatro hogares de Bogotá**.",
          "{Señale el recuadro verde.} Para calcular el impacto usamos **medio kilo** de restos de comida por hogar al día. Es menos de la mitad de lo que muestran los datos de la UAESP, la entidad de la Alcaldía que maneja el aseo de Bogotá, así que el impacto real podría ser mayor. Y como los hogares van llegando poco a poco, de [[16.200]] el primer año a [[735.450]] en el año diez, en total son unas [[407.000 toneladas]] en diez años que no llegan al relleno: **lo que recibe Doña Juana en dos meses**, el [[1,6 %]] de todo lo que le llegaría en esos diez años. ~Y en el año diez, ya con todos los hogares, serán unas [[288 toneladas]] menos cada día: el [[4 %]] de lo que entra hoy a Doña Juana.~"]),
  dict(t="Hoy y con RECOEVO", ancla="El camino de una cáscara antes y después.", poster="Póster 04 · Customer Journey Map",
       pregunta="¿Qué camino hace hoy una cáscara y cuál hace con RECOEVO?",
       pistas=["hoy: bolsa rota en la esquina → Doña Juana", "con RECOEVO: bolsa cerrada desde la cocina → ruta de orgánicos"],
       p=["{Señale el bloque 04.} Piénsenlo así: hoy una cáscara termina en una bolsa rota en la esquina, y después en Doña Juana. Con RECOEVO, sale de la cocina en una **bolsa cerrada**, directo a la **ruta de orgánicos**."]),
  dict(t="Cómo gana dinero", ancla="Los cuatro canales de venta, sus porcentajes y por qué.", poster="Póster 05 · fuentes de ingreso, canales de venta (dona) y clientes",
       pregunta="¿Cómo gana dinero? ¿Por qué canales vende, en qué porcentaje y por qué?",
       pistas=["vende el producto, por cuatro caminos", "35 % marketplaces: cobran ~14 %, llegan a todo el país", "35 % lotes: empresas, conjuntos y alcaldías; 15 % más barato (142.000 + IVA), cientos a la vez; el decreto los obliga", "15 % tienda en línea: sin intermediario, solo pasarela (~3,5 %), pero ~27.000 de publicidad por venta", "15 % grandes superficies: se quedan con ~40 % y pagan a 60 días", "envío por internet: lo paga el cliente (Bogotá 14.900)", "cadenas y lotes: el flete ya está en los costos"],
       p=["{Señale la dona de canales.} ¿Y cómo gana dinero? **Vendiendo el producto**, por cuatro caminos. El [[35 %]] de las ventas, por **marketplaces** como Mercado Libre: cobran alrededor del [[14 %]] y llegan a todo el país. Otro [[35 %]], **por lotes** a empresas, conjuntos y alcaldías: les damos un precio un [[15 %]] más bajo, [[142.000]] pesos más IVA, pero compran cientos de una vez, y el decreto también los obliga a separar.",
          "Un [[15 %]] en nuestra **tienda en línea**: ahí no hay un almacén ni un marketplace en medio, así que no pagamos comisión, solo la pasarela de pago, cerca del [[3,5 %]]; eso sí, pagamos publicidad en redes para conseguir cada venta, unos [[27.000]] pesos. Y solo un [[15 %]] en **grandes superficies**, porque se quedan con cerca del [[40 %]] del precio~ y pagan a 60 días~.",
          "¿Y el envío? En las ventas por internet lo paga el cliente aparte: en Bogotá son [[14.900]] pesos. Y a las cadenas y los lotes se los llevamos nosotros en estibas; ese flete ya está dentro de los costos."]),
  dict(t="Los ODS", ancla="Por qué lo pensamos con tres Objetivos de Desarrollo Sostenible.", poster="Póster 05 · Objetivos de Desarrollo Sostenible (12, 11 y 13)",
       pregunta="¿Para qué más sirve RECOEVO? ¿Con qué ODS se pensó y por qué?",
       pistas=["no es solo un negocio: un propósito", "ODS 12 Producción y consumo responsables: menos comida desperdiciada", "ODS 11 Ciudades y comunidades sostenibles: menos bolsas rotas, ratas y carga para Doña Juana", "ODS 13 Acción por el clima: la comida enterrada suelta metano (80 veces el CO₂ en 20 años)"],
       p=["Pero esto no es solo un negocio: lo pensamos con un propósito, alineado con tres **Objetivos de Desarrollo Sostenible** de la ONU.",
          "{Señale el ODS 12.} El ODS [[12]], **Producción y consumo responsables**, pide reducir a la mitad la comida que se desperdicia y la basura que generamos: RECOEVO saca los restos de comida de la bolsa de basura. El ODS [[11]], **Ciudades y comunidades sostenibles**, busca ciudades que manejen mejor sus residuos: menos bolsas rotas en las esquinas, menos ratas y menos carga para Doña Juana. Y el ODS [[13]], **Acción por el clima**: la comida enterrada se pudre sin aire y suelta **metano**, un gas que calienta el planeta unas [[80]] veces más que el CO₂ en sus primeros veinte años. Si la comida no llega al relleno, ese metano no se produce."]),

  dict(t="Los números: lo que cuesta", ancla="Inversión, precio, costo por producto, costos fijos y variables.", poster="Póster 06 · franja amarilla y recuadros (también en el QR: página del presupuesto)",
       pregunta="¿Cuánto hay que invertir? ¿A cuánto se vende y por qué? ¿Cuánto cuesta cada producto y cuáles son los costos fijos y variables?",
       pistas=["también en el QR: página del presupuesto", "escenario realista, 10 años", "inversión: 5.954 millones (fábrica, arranque, respaldo)", "precio: 199.900 con IVA el año 1, lo de una buena caneca", "promedio de 10 años: 275.630 con IVA", "costo por producto: 144.319", "variables: unos 104.000 por producto", "fijos: 2.872 millones al año"],
       p=["{Señale el bloque 06.} Ahora, los **números** del plan a diez años, en el escenario realista; también están en el QR, en la página del presupuesto.",
          "Para empezar necesitamos una **inversión inicial** de [[5.954 millones]] de pesos: la fábrica, el arranque y un respaldo de caja que se recupera. El **precio** es de [[199.900]] con IVA el primer año, lo que una familia paga por una buena caneca; con la inflación, en promedio de los diez años queda en [[275.630]], también con IVA.",
          "Cada producto nos **cuesta** en promedio [[144.319]] pesos, con todo incluido: unos [[104.000]] son **costos variables**, como los materiales y las comisiones; y los **costos fijos**, como la nómina y el arriendo, suman unos [[2.872 millones]] al año."]),
  dict(t="Los números: lo que deja", ancla="Margen, punto de equilibrio, utilidad, retorno y rentabilidad.", poster="Póster 06 · recuadros de equilibrio, margen, recuperación, utilidad y TIR",
       pregunta="¿Cuál es el margen de contribución, el punto de equilibrio y cuándo se alcanza? ¿Cuánto se gana, cuál es el retorno, cuándo se recupera y cuál es la rentabilidad?",
       pistas=["margen de contribución: 49 %", "equilibrio = fijos ÷ margen = 2.380 al mes", "lo superamos en el mes 17", "utilidad neta 10 años: 30.508 millones", "retorno 512 %", "se recupera en el mes 50", "por cada 100 gastados, casi 29 (28,7 %)", "de cada 100 vendidos, casi 20 (19,9 %)"],
       p=["De lo que nos llega por producto, el [[49 %]] queda libre para pagar esos costos fijos: es el **margen de contribución**. Dividiendo los costos fijos entre ese margen, el **punto de equilibrio** da [[2.380]] productos al mes, y lo superamos en el mes [[17]].",
          "En diez años, la **utilidad neta**, ya pagados costos e impuestos, es de [[30.508 millones]]: un **retorno de la inversión** del [[512 %]], y la inversión se recupera en el mes [[50]].",
          "Y la **rentabilidad**: por cada 100 pesos que gastamos ganamos casi 29, el [[28,7 %]]; y de cada 100 que vendemos nos quedan casi 20, el [[19,9 %]]. ~Y la TIR, lo que rinde al año el dinero invertido, es del [[33,9 %]].~"]),
  dict(t="El cierre", ancla="Lo que nos ilusiona y la invitación a una mentoría.", poster="Pie del póster",
       pregunta="¿Qué sienten por esta idea y qué le piden al jurado?",
       pistas=["nos ilusiona de verdad", "nació en la cuadra de Samuel", "esa bolsa la hemos visto todos", "mercadeo e ingeniería de sistemas", "posiblemente nos falte la mirada de quien ha creado empresa", "quede o no seleccionada: después del evento, una conversación, una posible mentoría", "afinar los números con su experiencia", "esa bolsa no tiene por qué seguir ahí", "eslogan: Menos relleno, más vida"],
       p=["Esta idea **nos ilusiona** de verdad. Nació en la cuadra de Samuel, pero esa bolsa rota la hemos visto todos. ~Y nos emociona pensar que una cáscara puede volver a ser tierra viva.~",
          "Somos estudiantes de **mercadeo y de ingeniería de sistemas**, y entendemos que posiblemente nos falte la mirada de quien ya ha creado empresa. Por eso, quede o no seleccionada esta idea, después de este evento nos gustaría llevar este proyecto a **una conversación con ustedes, una posible mentoría**, para afinar estos números con su experiencia.",
          "Porque creemos que esa bolsa de la esquina no tiene por qué seguir ahí. Nuestro eslogan lo dice: **Menos relleno, más vida.** Muchas gracias."]),
]

FRASE_CADENA = ("Una <b>bolsa</b> rota en el <b>barrio</b>; la <b>ironía</b> y la <b>ley</b>; un <b>pedal</b> a buen <b>precio</b>; "
                "<b>Usme</b> cambia su <b>recorrido</b>; el <b>negocio</b> y los <b>ODS</b>; la <b>inversión</b> y la <b>utilidad</b>; y pedimos <b>mentoría</b>.")

PARTES = [("El problema", 1, 4), ("La solución", 5, 8), ("El negocio", 9, 12), ("El cierre", 13, 13)]

# ------------------------------------------------------------------ medición (cifras contadas como se pronuncian)
MARCA = re.compile(r"(~)|\{([^}]*)\}|\*\*([^*]+)\*\*|\[\[([^\]]+)\]\]")

def partes(s):
    out, opt, last = [], False, 0
    for m in MARCA.finditer(s):
        if m.start() > last: out.append(("txt", s[last:m.start()], opt))
        if m.group(1): opt = not opt
        elif m.group(2) is not None: out.append(("dir", m.group(2), opt))
        elif m.group(3) is not None: out.append(("kw", m.group(3), opt))
        else: out.append(("num", m.group(4), opt))
        last = m.end()
    if last < len(s): out.append(("txt", s[last:], opt))
    return out

def pal_entero(n):
    if n < 30: return 1
    if n < 100: return 1 if n % 10 == 0 else 3
    if n < 1000: return 1 + (pal_entero(n % 100) if n % 100 else 0)
    if n < 10**6:
        k, r = divmod(n, 1000)
        return (0 if k == 1 else pal_entero(k)) + 1 + (pal_entero(r) if r else 0)
    m, r = divmod(n, 10**6)
    return pal_entero(m) + 1 + (pal_entero(r) if r else 0)

def pal_cifra(tok):
    ent, _, dec = tok.partition(",")
    ent = ent.replace(".", "")
    n = (1 if re.match(r"0\d", ent) else 0) + pal_entero(int(ent or 0))
    return n + (1 + len(dec) if dec else 0)

def pal_texto(s):
    n = 0
    for w in re.findall(r"\d[\d.,]*\d|\d|%|[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", s):
        n += 2 if w == "%" else pal_cifra(w) if w[0].isdigit() else 1
    return n

def medir():
    t, filas = PAUSA_INICIO, []
    for i, b in enumerate(GUION):
        tot = opc = 0
        for p in b["p"]:
            for tipo, s, o in partes(p):
                if tipo == "dir": continue
                k = pal_texto(s); tot += k; opc += k if o else 0
        ini = t; dur = tot / RITMO; t = ini + dur + (RESPIRO if i < len(GUION) - 1 else 0)
        filas.append(dict(ini=ini, fin=ini + dur, pal=tot, opc=opc))
    total = filas[-1]["fin"]
    sin_opc = total - sum(f["opc"] for f in filas) / RITMO
    return filas, total, sin_opc

def mmss(s):
    s = int(round(s)); return f"{s // 60}:{s % 60:02d}"

# ------------------------------------------------------------------ HTML del texto
def e(s): return html.escape(s, quote=True)

def html_parrafo(p):
    out, abierto = [], False
    for tipo, s, o in partes(p):
        if o and not abierto: out.append('<span class="opc">'); abierto = True
        if not o and abierto: out.append('</span>'); abierto = False
        if tipo == "kw": out.append(f'<strong>{e(s)}</strong>')
        elif tipo == "num": out.append(f'<b class="num">{e(s)}</b>')
        elif tipo == "dir": out.append(f'<span class="gesto">{e(s)}</span>')
        else: out.append(e(s))
    if abierto: out.append('</span>')
    return "".join(out)

# ------------------------------------------------------------------ preguntas del jurado
# Banco de preguntas del jurado: (palabras clave, pregunta, respuesta corta, en sencillo, cómo se calculó / de dónde sale)
# Cifras: presupuesto ejecutivo y plan detallado realista (3-nov-2026), póster E-Fest y sus fuentes, estudio de campo (19-sep-2026).
GRUPOS = {
  "Competencia": ["Competencia", "Copiar o importar", "Diferenciación", "Patente"],
  "Datos del problema": ["Basura en Colombia", "Desperdicio de comida", "Doña Juana", "Fertilizantes y urea", "Metano", "Orgánicos", "Ratas y plagas", "Tierra degradada"],
  "Fábrica": ["Capacidad", "Empleos", "Fábrica propia", "Máquinas y moldes", "Materia prima", "Planta"],
  "Finanzas": ["Costo por producto", "Costos fijos y variables", "Dólar", "EBITDA", "Financiación", "Impuestos", "Inflación", "Inversión inicial", "Margen de contribución", "Precio", "Punto de equilibrio", "Recuperación (payback)", "Rentabilidad", "Riesgos", "ROI", "TIR", "Utilidad", "VPN y WACC"],
  "Impacto y ODS": ["CO₂", "Compost", "ODS", "Plástico reciclado", "Toneladas"],
  "Ley": ["Código de colores", "Decreto 0772", "Permisos", "Ruta de orgánicos"],
  "Mercado y clientes": ["Bogotá", "Clientes", "Demanda", "Empresas y conjuntos", "Hogares", "LTV y CAC", "Mercado (TAM, SAM, SOM)", "Usme"],
  "Producto": ["Atascos", "Bolsas", "Cómo funciona", "Cuchillas", "Filtro y olor", "Garantía", "Material seco", "Prototipo", "Seguridad", "Tamaño y peso"],
  "Proyecto y equipo": ["Equipo", "Metodologías", "Origen de la idea", "Siguiente paso"],
  "Trabajo de campo": ["Barreras", "Confiabilidad", "Disposición", "Hallazgos", "Metodología del campo"],
  "Ventas y canales": ["Canales", "Comisiones", "Cuotas", "Envíos", "Grandes superficies", "Lotes", "Marketing", "Marketplaces", "Tienda en línea"],
}
PROFE = "Las 9 de la profesora"

BANCO = [
  # ------------------------------------------------------------------ las 9 de la profesora (mismo orden de la página del presupuesto)
  (["Inversión inicial", PROFE], "1. ¿Cuánto dinero hay que poner para empezar? (inversión inicial)", "$5.954 millones",
   "Es todo el dinero que se necesita antes de vender el primer producto: montar la fábrica, arrancar y tener un respaldo de caja.",
   ["Máquinas, moldes, planta y oficina: $3.147 M (97 máquinas $1.672 M; 13 moldes y troqueles $1.013 M; bodega, computadores y muebles $462 M).",
    "Gastos de arranque: $484 M (trámites, marca y patente, desarrollo del producto, puesta en marcha, lanzamiento, sueldos de montaje y 10 % de imprevistos).",
    "Dinero de respaldo, que se recupera: $2.323 M (capital de trabajo $1.171 M; IVA de las máquinas $598 M; colchón de caja $500 M; depósito del arriendo $54 M).",
    "3.147 + 484 + 2.323 = $5.954 M."]),
  (["Precio", PROFE], "2. ¿A cuánto se vende y cómo llegaron a ese precio?", "$199.900 con IVA el año 1 · $275.630 con IVA en promedio de 10 años",
   "Cuesta lo que vale una buena caneca, pero tritura y no huele. Como el precio sube cada año con la inflación, en promedio de los 10 años el cliente paga $275.630, también con IVA.",
   ["Techo, el mercado: menos de $200.000. Caneca con pedal de 20 L $119.900 (solo guarda); eléctricos FoodCycler $1.265.000 y Lomi $1.737.000.",
    "Piso, el costo: cada producto cuesta $144.319 con todo incluido; el precio tiene que cubrirlo y dejar ganancia.",
    "Precio con IVA por año: año 1 $199.900 · año 2 $211.244 · año 3 $223.232 · año 4 $235.901 · año 5 $249.288 · año 6 $263.435 · año 7 $278.385 · año 8 $294.184 · año 9 $310.879 · año 10 $328.521.",
    "Promedio de 10 años: lo que pagan los clientes, cada venta pesa igual. Como en los últimos años se vende más, queda en $275.630."]),
  (["Costo por producto", PROFE], "3. ¿Cuánto cuesta hacer un producto?", "$144.319 con todo incluido",
   "Es lo que cuesta, en promedio de 10 años, fabricar, vender, administrar y financiar cada RECOEVO.",
   ["Gasto completo de 10 años $106.139 M ÷ 735.450 productos vendidos = $144.319.",
    "Fabricar $74.205 = materiales $58.081 + energía $4.637 + planta $11.487.",
    "Administrar y vender $63.868 = nómina de todos $29.310 + legales $1.149 + oficina e impuestos $3.269 + publicidad, comisiones, distribución y garantía $30.141.",
    "Más máquinas que se van gastando $4.825, arranque $658 e intereses $762."]),
  (["Costos fijos y variables", PROFE], "4. ¿Cuáles son los costos fijos y los variables?", "Variable $104.611 por producto · fijos $2.872 M al año",
   "Los variables aparecen con cada producto que se hace; los fijos se pagan aunque no se venda nada.",
   ["Variables: materiales, operarios, energía, comisiones, anuncios, distribución, garantía e ICA = $104.611 por producto (promedio de 10 años).",
    "Fijos: nómina de planta, comercial y administrativa, arriendo y servicios, legales, oficina, marketing fijo, intereses y máquinas = $2.872 M al año (promedio de los años 1 a 10)."]),
  (["Utilidad", PROFE], "5. ¿Cuál es la utilidad neta?", "$30.508 millones en 10 años",
   "Es lo que les queda a los socios después de pagar todo, incluido el impuesto de renta: unos $41.500 por producto vendido.",
   ["Ventas $153.075 M − gasto completo $106.139 M = $46.936 M antes de impuestos.",
    "Impuesto de renta 35 %: $16.428 M. Queda $30.508 M.",
    "Año 0 (montaje) −$486 M · año 1 −$864 M · año 2 +$136 M · año 3 +$1.454 M · año 5 +$2.836 M · año 10 +$6.489 M."]),
  (["Punto de equilibrio", "Margen de contribución", PROFE], "6. ¿Cuál es el punto de equilibrio y cuándo se alcanza?", "2.380 productos al mes · se supera en el mes 17",
   "Es lo mínimo que hay que vender al mes para no perder dinero.",
   ["Lo que recibe la empresa por producto $205.185 − costo variable $104.611 = margen de contribución $100.574 (49 %).",
    "Costos fijos $2.872 M al año ÷ $100.574 = 28.554 al año ÷ 12 = 2.380 al mes.",
    "Ventas: 800 al mes al arrancar, 2.000 al cerrar el año 1 y 9.500 al mes en el año 10. El mes 17 se venden 2.500: por primera vez más que 2.380."]),
  (["ROI", "Recuperación (payback)", PROFE], "7. ¿Cuál es el retorno de la inversión y cuándo se recupera?", "512 % · se recupera en el mes 50",
   "El ROI (retorno de la inversión) compara lo que se gana con lo que se puso al principio. 512 % no son millones: es un porcentaje. Quiere decir que en 10 años, por cada $100 invertidos se ganan $512, más de cinco veces lo invertido. La inversión se recupera a los 4 años y 2 meses.",
   ["ROI: utilidad neta $30.508 M ÷ inversión $5.954 M = 5,12.",
    "Mes de recuperación: se suma mes a mes el dinero libre que deja el negocio (lo que entra menos todo lo que sale, también máquinas, inventario y facturas por cobrar). Tras el mes 1 va en −$4.547 M; deja de ser negativo en el mes 50."]),
  (["Rentabilidad", PROFE], "8. ¿Cuál es la rentabilidad sobre los costos?", "28,7 %",
   "Por cada $100 que se gastan, se ganan casi $29 de utilidad neta.",
   ["Utilidad neta $30.508 M ÷ gasto completo $106.139 M = 28,7 %.", "Antes de impuestos sería 44,2 %."]),
  (["Rentabilidad", "Utilidad", PROFE], "9. ¿Cuál es la rentabilidad sobre las ventas (el porcentaje de utilidad)?", "19,9 %",
   "De cada $100 que se venden, quedan casi $20 de utilidad neta.",
   ["Utilidad neta $30.508 M ÷ ventas $153.075 M = 19,9 %.", "Antes de impuestos sería 30,7 %."]),

  # ------------------------------------------------------------------ finanzas
  (["ROI", "Rentabilidad"], "¿Cómo puede el ROI ser de 512 % si la rentabilidad es solo de 28,7 % y 19,9 %?", "Porque dividen la misma utilidad entre cosas distintas",
   "La utilidad es la misma, $30.508 M en 10 años. El ROI la divide entre la inversión inicial, que se pone una sola vez ($5.954 M). Las rentabilidades la dividen entre todo lo que se gasta o se vende en 10 años, que es mucho más grande. Es como una tienda: se monta una vez, pero vende miles de veces; cada venta deja poco, pero la suma de muchas ventas devuelve varias veces lo que costó montarla.",
   ["ROI = utilidad ÷ inversión inicial = 30.508 ÷ 5.954 = 512 %.",
    "Rentabilidad sobre costos = utilidad ÷ gasto completo de 10 años = 30.508 ÷ 106.139 = 28,7 %. Ese gasto no lo ponen los socios: lo pagan las mismas ventas, mes a mes.",
    "Rentabilidad sobre ventas = utilidad ÷ ventas de 10 años = 30.508 ÷ 153.075 = 19,9 %.",
    "La cuenta que las une: cada peso invertido genera $25,7 en ventas en 10 años (153.075 ÷ 5.954), y de cada peso vendido quedan 19,9 centavos. 25,7 × 19,9 % = 5,12, o sea 512 %.",
    "Y en tiempo: la TIR de 33,9 % al año es la misma idea pero año por año, teniendo en cuenta que la ganancia llega más tarde que la inversión."]),
  (["ROI", "Recuperación (payback)", "Utilidad"], "¿Cómo va el retorno de la inversión año por año?", "Negativo los dos primeros años, positivo desde el año 3 y 512 % en el año 10",
   "El retorno se va acumulando: los primeros años se pierde porque la fábrica arranca con pocas ventas, y después cada año deja más. Ojo: que la utilidad acumulada ya sea positiva en el año 3 no es lo mismo que recuperar la inversión; recuperarla es que el dinero que entra ya devolvió los $5.954 M que se pusieron, y eso pasa en el mes 50, a los 4 años y 2 meses.",
   ["Retorno acumulado (utilidad neta acumulada ÷ inversión de $5.954 M): año 1 −23 % · año 2 −20 % · año 3 +4 % · año 4 +38 % · año 5 +86 % · año 6 +149 % · año 7 +223 % · año 8 +308 % · año 9 +403 % · año 10 +512 %.",
    "Retorno de cada año (utilidad del año ÷ inversión): año 1 −15 % · año 2 +2 % · año 3 +24 % · año 4 +34 % · año 5 +48 % · año 6 +63 % · año 7 +74 % · año 8 +85 % · año 9 +96 % · año 10 +109 %.",
    "Utilidad neta por año: año 0 −$486 M (montaje) · año 1 −$864 M · año 2 +$136 M · año 3 +$1.454 M · año 4 +$2.022 M · año 5 +$2.836 M · año 6 +$3.778 M · año 7 +$4.385 M · año 8 +$5.050 M · año 9 +$5.710 M · año 10 +$6.489 M (presupuesto, tabla 11).",
    "¿Por qué el mes 50 y no el año 3? La recuperación cuenta el dinero de verdad: las máquinas se pagan completas al inicio, y parte del dinero se queda en inventario y en facturas que las cadenas pagan a 60 días."]),
  (["Utilidad", "Rentabilidad"], "¿La rentabilidad es lo mismo que la utilidad? ¿Qué es el porcentaje de utilidad?", "La utilidad son pesos; el porcentaje de utilidad es 19,9 %",
   "La utilidad es cuánto dinero queda: $30.508 M en 10 años. El porcentaje de utilidad es esa misma utilidad vista como parte de lo que se vende: de cada $100 que se venden quedan $19,9. Es lo mismo que la rentabilidad sobre ventas. La rentabilidad sobre costos (28,7 %) mide lo mismo, pero frente a lo que se gasta.",
   ["Utilidad neta: ventas $153.075 M − gasto $106.139 M − impuesto $16.428 M = $30.508 M.",
    "Porcentaje de utilidad (margen neto, o rentabilidad sobre ventas) = 30.508 ÷ 153.075 = 19,9 %.",
    "Rentabilidad sobre costos = 30.508 ÷ 106.139 = 28,7 %: por cada $100 que se gastan, se ganan $28,7.",
    "Antes de impuestos serían 30,7 % sobre ventas y 44,2 % sobre costos.",
    "No confundir con el margen de contribución (49 %): ese es lo que deja cada producto antes de pagar los costos fijos y los impuestos."]),
  (["TIR", "Rentabilidad"], "¿Qué es la TIR y por qué da 33,9 %?", "33,9 % al año",
   "La TIR es la rentabilidad anual del proyecto. Es como si todo el dinero invertido estuviera en una cuenta que paga 33,9 % de interés cada año durante los 10 años.",
   ["Se ponen en una línea de tiempo todo el dinero que sale (la inversión y las compras) y todo el que entra mes a mes durante los 10 años.",
    "La TIR es la tasa de interés con la que, al traer todo ese dinero a pesos de hoy, lo que entra y lo que sale quedan exactamente iguales (VPN = 0).",
    "Como 33,9 % es más que el 22,4 % que cuesta conseguir el dinero (WACC), el proyecto gana más de lo que cuesta financiarlo. No se cuenta ningún valor de venta de la empresa al final."]),
  (["VPN y WACC", "Rentabilidad"], "¿Qué es el VPN y cuánto da?", "+$3.397 millones",
   "El VPN es lo que el proyecto deja de más, en pesos de hoy, después de pagarle a quien puso el dinero lo que espera ganar. Si es positivo, el proyecto vale la pena.",
   ["Cada peso que entra en el futuro se «trae a hoy» dividiéndolo por (1 + 22,4 %) por cada año que falta.",
    "Se suman todos esos pesos de hoy y se resta la inversión: da +$3.397 M en 10 años, sin contar un valor de venta de la empresa al final."]),
  (["VPN y WACC"], "¿Qué es el 22,4 % (WACC) y de dónde sale?", "22,4 % al año: lo que cuesta conseguir el dinero",
   "Es la mezcla de lo que piden los socios por arriesgar su dinero y lo que cobra el banco por el préstamo.",
   ["Socios: ponen el 82 % del dinero y piden 24,5 % al año.",
    "Banco: presta el 18 % al 19,5 %; como los intereses bajan el impuesto de renta (35 %), en realidad cuesta 12,7 %.",
    "0,82 × 24,5 % + 0,18 × 12,7 % ≈ 22,4 %."]),
  (["Financiación", "Inversión inicial"], "¿De dónde sale el dinero? ¿Socios o deuda?", "Socios $4.880 M + crédito $1.074 M",
   "El 82 % lo ponen los socios y el 18 % es un préstamo del banco para la maquinaria.",
   ["Crédito de $1.074 M al 19,5 % efectivo anual, a 5 años, con cuotas mensuales iguales (Bancóldex o leasing).",
    "Sus intereses en los 10 años suman $561 M y ya están dentro del gasto.", "4.880 + 1.074 = $5.954 M."]),
  (["Financiación", "ROI"], "¿Qué retorno tendría un socio?", "Por cada $100 que pone, el negocio deja $625 de utilidad en 10 años",
   "Además de recuperar su aporte, la utilidad acumulada equivale a más de seis veces lo que puso.",
   ["Utilidad neta de 10 años $30.508 M ÷ aporte de los socios $4.880 M = 6,25.",
    "Si la empresa se valorara en el año 10 a 5 veces su EBITDA, la rentabilidad anual del socio sería 32,7 %, frente a 24,5 % que exige."]),
  (["EBITDA"], "¿Qué es el EBITDA y cuándo es positivo?", "Positivo desde el mes 9",
   "EBITDA (se dice «ebitda») es lo que deja la operación antes de pagar intereses, impuestos y el desgaste de las máquinas. Muestra si vender ya cubre lo que cuesta operar.",
   ["Ventas del mes − costos de operar el mes, sin contar intereses, impuestos ni depreciación.",
    "En el plan se vuelve positivo en el mes 9; la utilidad neta, en el mes 18."]),
  (["Utilidad"], "¿Cuándo empiezan a ganar dinero?", "Desde el año 2",
   "El primer año se pierde porque la fábrica arranca con poca venta y paga sus costos fijos completos.",
   ["Año 1: −$864 M; año 2: +$136 M; año 3: +$1.454 M (presupuesto, tabla 11).", "Mes a mes, la utilidad neta se vuelve positiva en el mes 18."]),
  (["Margen de contribución"], "¿Qué es el margen de contribución?", "49 %: $100.574 por producto",
   "De cada $100 que le llegan a la empresa por producto, $49 quedan libres para pagar los costos fijos.",
   ["Precio que recibe la empresa (promedio, sin IVA, ya pagadas tiendas y cadenas) $205.185 − costo variable $104.611 = $100.574.",
    "100.574 ÷ 205.185 = 49 %."]),
  (["Precio", "Impuestos"], "¿El precio incluye IVA? ¿Cuánto le queda a la empresa?", "Sí: $199.900 incluye IVA; sin IVA son $167.983",
   "El IVA (19 %) no es dinero de la empresa: se le entrega al Estado.",
   ["199.900 ÷ 1,19 = 167.983.",
    "Después de lo que cobran tiendas y cadenas y del descuento por lote, la empresa recibe en promedio $205.185 por producto en los 10 años (el precio sube con la inflación)."]),
  (["Precio", "Cuotas", "Usme"], "¿Es accesible para los hogares de Usme?", "Sí: cuesta lo de una buena caneca y se puede pagar en 12 cuotas de $16.658",
   "Además, empresas, conjuntos y alcaldías pueden comprar por lotes para sus comunidades.",
   ["199.900 ÷ 12 = 16.658.",
    "Precio por lote: $142.000 + IVA hoy; en promedio de 10 años la empresa recibe $195.360 por producto en lotes, más que el costo total de $144.319."]),
  (["Impuestos"], "¿Qué impuestos pagan?", "Renta 35 %: $16.428 M en 10 años",
   "También el IVA (19 %), que paga el cliente y se le entrega al Estado, el impuesto de industria y comercio (ICA) y el 4 × 1.000.",
   ["Renta: 35 % de (ventas − gasto completo) = 35 % × $46.936 M. Las pérdidas de los primeros años se descuentan de las ganancias siguientes.",
    "ICA ≈ $1.680 por producto y 4 × 1.000 ≈ $616 por producto, ya dentro de los gastos."]),
  (["Inflación"], "¿Cómo manejan la inflación?", "5,7 % al año, el promedio del DANE de 2016 a 2025",
   "Todo sube con la inflación: el precio, las compras y los sueldos.",
   ["Compras, arriendo y contratistas: +5,7 % al año.",
    "Sueldos ligados al salario mínimo: +8,4 % (inflación + 2,7 puntos). Profesionales: +6,7 %.",
    "No se usa la meta de 3 % del Banco de la República porque desde 2021 la inflación nunca bajó de 5 %."]),
  (["Dólar", "Materia prima"], "¿Cómo les afecta el dólar?", "Poco: cerca del 30 % de los materiales es importado",
   "La resina de plástico, que es lo que más pesa en el costo, es nacional.",
   ["Se importan el fleje inoxidable de las cuchillas y algunos retenes; la maquinaria se paga en dólares, pero ya está en la inversión.",
    "Se cubre comprando por contenedor y con coberturas cambiarias con el banco."]),
  (["Riesgos"], "¿Cuál es el mayor riesgo y cómo lo manejan?", "Que se venda menos de lo planeado",
   "Todavía no hay ventas reales, así que la demanda es lo primero que hay que probar.",
   ["Preserie con preventas y cartas de intención antes de producir en serie.",
    "La fábrica crece por escalones: se agregan turnos antes que máquinas, y la segunda etapa solo se compra si las ventas pasan el 85 % de la capacidad.",
    "La capacidad libre se puede vender como maquila; y el Decreto 0772 empuja el canal de lotes.",
    "El segundo riesgo es técnico (cuchillas y seguro): los ensayos están presupuestados."]),
  (["Riesgos", "VPN y WACC"], "¿Qué tan seguro es que el negocio dé ganancia?", "87 % de probabilidad de VPN positivo",
   "Se simuló el negocio miles de veces moviendo al azar ventas, precios y costos: en 87 de cada 100 casos crea valor.",
   ["Simulación Monte Carlo del plan detallado: en cada corrida las variables cambian dentro de rangos realistas y se calcula el VPN."]),

  # ------------------------------------------------------------------ datos del problema
  (["Basura en Colombia"], "¿Cuánta basura entierra Colombia?", "33.300 toneladas al día",
   "Y solo 1 de cada 5 toneladas se aprovecha; el resto va a rellenos y botaderos.",
   ["Superservicios, Informe Nacional de Disposición Final 2024: 12,15 millones de toneladas al año ÷ 365 ≈ 33.300 al día; el 80 % va a disposición final.",
    "Hay 249 sitios: 160 rellenos sanitarios y 72 botaderos a cielo abierto."]),
  (["Orgánicos", "Basura en Colombia"], "¿Cuánto de esa basura es comida?", "Cerca del 60 %",
   "Más de la mitad de lo que botamos son restos de comida.",
   ["Secretaría del Hábitat de Bogotá: entre 60 y 61,5 % de orgánicos.",
    "UAESP: los hogares de Bogotá sacan unas 3.440 toneladas de orgánicos al día."]),
  (["Doña Juana"], "¿Cuánto recibe Doña Juana y cuánto le queda?", "6.800 toneladas al día · licencia hasta 2029",
   "Es el relleno de Bogotá; se entra por la vía al Llano, antes de llegar a Usme.",
   ["UAESP: 608.100 toneladas en el primer trimestre de 2026 ≈ 6.769 al día; en 2025 recibió 2,42 millones de toneladas (+5 %).",
    "La CAR prorrogó su licencia hasta el primer semestre de 2029 (El Tiempo, octubre de 2026)."]),
  (["Ratas y plagas"], "¿Hay datos de ratas y plagas?", "135 puntos críticos de ratas en Bogotá",
   "La basura a la intemperie es refugio y comida para las ratas.",
   ["Semana, 17 de marzo de 2026, con datos del Distrito: 135 puntos de alta infestación en 10 localidades.",
    "UAESP: 968 toneladas de basura arrojadas a las calles de Bogotá cada día."]),
  (["Desperdicio de comida"], "¿Cuánta comida se pierde en Colombia?", "9,76 millones de toneladas al año",
   "Es el 34 % de la comida disponible: un tercio se pierde o se desperdicia.",
   ["DNP, estudio de 2016 (es la última medición oficial)."]),
  (["Fertilizantes y urea"], "¿Por qué el abono les sale caro a los campesinos?", "Más del 94 % del fertilizante se importa, y la urea subió 187 %",
   "La urea es el abono químico más usado. Entre enero de 2021 y enero de 2022, el bulto de 50 kg pasó de $80.000 a $230.000.",
   ["(230.000 − 80.000) ÷ 80.000 = 187 %. Fuente: DANE-SIPSA vía U.S. Trade.gov.",
    "El Colombiano, abril de 2026: más del 94 % se importa, y en 2026 la urea volvió a subir ($120.000–130.000 el bulto en Medellín)."]),
  (["Tierra degradada", "Compost"], "¿Para qué le sirve el compost a la tierra?", "El 40 % de la tierra agrícola está degradada",
   "El compost devuelve materia orgánica al suelo. Hoy se aplica menos de lo necesario.",
   ["2,8 millones de hectáreas degradadas; se aplican menos de 300 kg de enmiendas orgánicas por hectárea, cuando lo mínimo recomendado es 1 tonelada (Agronegocios; CONtexto Ganadero con Asocompost).",
    "Colombia produce unas 900.000 toneladas de abono orgánico al año."]),
  (["Metano", "CO₂"], "¿Por qué la comida enterrada calienta el planeta?", "Suelta metano, unas 80 veces más potente que el CO₂ en 20 años",
   "En el relleno la comida se pudre sin aire, y así produce metano.",
   ["El Tiempo, octubre de 2026, con datos citados por Greenpeace sobre Doña Juana."]),

  # ------------------------------------------------------------------ ley
  (["Decreto 0772"], "¿Qué dice el Decreto 0772 de 2026?", "Obliga a todos los hogares a separar los residuos en la fuente",
   "Y crea una ruta que recoge los orgánicos por separado, al menos una vez por semana.",
   ["Ministerio de Vivienda, expedido el 16 de julio de 2026 (Diario Oficial 53.556).",
    "Artículo 2.3.2.2.2.8.82: es obligación de los usuarios separar los residuos en la fuente.",
    "Los municipios deben ir montando el tratamiento de orgánicos y fijar metas para enterrar menos en su plan de residuos (PGIRS)."]),
  (["Código de colores"], "¿Cuál es el código de colores de las bolsas?", "Blanca, negra y verde",
   "Blanca: lo que se aprovecha (plástico, cartón, vidrio). Negra: lo que no se aprovecha. Verde: los orgánicos, que es lo que deja listo RECOEVO.",
   ["Resolución 2184 de 2019 de los ministerios de Ambiente y de Vivienda, vigente desde 2021."]),
  (["Ruta de orgánicos", "Decreto 0772"], "¿Y si en mi barrio todavía no pasa la ruta de orgánicos?", "La bolsa cerrada también sirve para compostar",
   "El decreto obliga a crear la ruta poco a poco; mientras llega, la bolsa se puede llevar a compostaje.",
   ["Decreto 0772 de 2026: ruta selectiva de orgánicos al menos una vez por semana, implementada de forma progresiva por los municipios."]),
  (["Permisos"], "¿Qué permisos necesitan?", "Los de cualquier fábrica; no hay reglamento técnico para un triturador mecánico",
   "Como no tiene motor, no le aplica el reglamento eléctrico (RETIE).",
   ["Sociedad S.A.S., RUT, facturación electrónica, uso de suelo industrial, concepto de Bomberos, sistema de seguridad y salud en el trabajo, plan de envases (REP), garantía legal (Ley 1480 de 2011) y registros ante la SIC.",
    "Se confirmará con la SIC que no hay reglamento técnico obligatorio."]),

  # ------------------------------------------------------------------ mercado y clientes
  (["Mercado (TAM, SAM, SOM)", "Hogares"], "¿Qué tan grande es el mercado?", "18,9 M hogares · 13,6 M urbanos · 735.450 en 10 años",
   "TAM: todos los hogares del país. SAM: los urbanos, que la ley obliga a separar. SOM: los que el plan espera alcanzar.",
   ["DANE, Encuesta de Calidad de Vida 2025 y proyección de hogares 2025.", "735.450 ÷ 13,6 millones = 5,4 %."]),
  (["Hogares", "Bogotá"], "¿Cuántos hogares quieren alcanzar?", "735.450 en 10 años: como 1 de cada 4 hogares de Bogotá",
   "Uno por hogar. Se empieza en Usme, luego Bogotá y después las ciudades principales.",
   ["Bogotá tiene unos 2,9 millones de hogares (DANE, Encuesta Multipropósito 2025): 735.450 ÷ 2,9 millones ≈ 25 %.",
    "Productos al año: año 1 16.200 · año 3 50.250 · año 5 77.500 · año 10 110.750."]),
  (["Usme"], "¿Por qué empezar en Usme?", "Porque ahí se juntan los dos problemas",
   "Allá validamos el problema, Doña Juana queda en la vía a Usme, y el 85 % de Usme es campo.",
   ["Usme: 18.477 de sus 21.507 hectáreas son rurales (85,9 %, Universidad Santo Tomás).",
    "Unos 17.000 campesinos: la localidad con más campesinos de Bogotá (Alcaldía).", "Unos 415.000 habitantes (Observatorio de Salud de Bogotá, 2024)."]),
  (["Clientes", "Empresas y conjuntos"], "¿Quiénes son los clientes?", "Hogares urbanos, y empresas, conjuntos y alcaldías",
   "Los hogares compran por internet o en almacenes; las empresas, conjuntos y alcaldías compran por lotes para sus comunidades.",
   ["Mezcla de los 10 años: lotes 35 %, marketplaces 35 %, tienda propia 15 % y cadenas 15 % de los productos."]),
  (["Empresas y conjuntos", "Lotes"], "¿Por qué comprarían los conjuntos, empresas y alcaldías?", "Porque el decreto también los obliga a separar",
   "Comprando por lotes, entregan un RECOEVO a cada hogar y cumplen la norma con su comunidad.",
   ["Precio por lote: $142.000 + IVA por producto, con un taller de separación de $8.000 + IVA.",
    "En 10 años: 259.491 productos por lotes (35 %)."]),
  (["LTV y CAC", "Clientes", "Marketing"], "¿Cuánto cuesta conseguir un cliente y cuánto deja?", "Conseguirlo cuesta ≈$56.572 y deja ≈$115.073",
   "LTV es lo que deja un cliente; CAC es lo que cuesta conseguirlo con publicidad. La relación es de 2 a 1.",
   ["LTV ≈ $115.073 de margen por una venta directa; CAC ≈ $56.572; LTV ÷ CAC ≈ 2,0.",
    "Por eso la mayor parte de la venta va por marketplaces, cadenas y lotes, donde no hay que pagar publicidad por cada venta."]),
  (["Demanda", "Riesgos"], "¿Qué evidencia de demanda tienen?", "Una obligación legal nueva y el trabajo de campo",
   "No damos la demanda por hecha: la preserie sirve para preventas y cartas de intención.",
   ["Decreto 0772 de 2026: todos los hogares deben separar los orgánicos.",
    "Trabajo de campo: el 100 % señala el shut como el problema, el 63 % mezcla todo, el 75 % habla de plagas y nadie rechazó la idea."]),

  # ------------------------------------------------------------------ trabajo de campo
  (["Metodología del campo", "Confiabilidad"], "¿Cómo hicieron el trabajo de campo?", "Entrevistas a vecinos y observación en Villa Rosita, Usme",
   "Fue un estudio cualitativo para validar el problema, no una encuesta de todo el barrio.",
   ["Sábado 19 de septiembre de 2026, sector Tihuaque.", "8 personas entrevistadas (66 minutos de audio) y 22 fotos y 4 videos.",
    "220 frases analizadas con el Framework Method y doble codificación; con 4 entrevistas ya aparecía el 97 % de los temas."]),
  (["Hallazgos"], "¿Qué encontraron en el trabajo de campo?", "100 % señala el shut · 75 % habla de plagas · 63 % mezcla todo",
   "La cadena falla en tres puntos: en la cocina (se mezcla), en la calle (se rompe la bolsa) y en la recolección.",
   ["Porcentajes sobre las personas entrevistadas: 63 % se queja de la recolección; 88 % está insatisfecho con el barrio (1,76 sobre 5); 50 % relaciona los residuos con el abono.",
    "Observación: shut desbordado pese al aviso de multa, perros comiendo de lo expuesto, bolsas en los andenes por las vías destapadas."]),
  (["Disposición"], "¿Los vecinos usarían algo así?", "Nadie rechazó la idea",
   "El 57 % la apoya de una vez y el 43 % pone condiciones.",
   ["Condiciones más pedidas: pedagogía (63 %), líderes o Junta (38 %), que pase la recolección (25 %), un incentivo (25 %), ver que funciona (25 %) y que sea práctico (25 %).",
    "El 38 % ya reutiliza las sobras: el hábito existe."]),
  (["Barreras"], "¿Qué impide hoy separar en casa?", "El hábito (88 %) y «¿y si los demás no?» (63 %)",
   "La gente no separa porque no tiene la costumbre y porque siente que los demás tampoco lo harán.",
   ["Además, el 50 % siente que el Estado está ausente."]),
  (["Confiabilidad"], "¿Qué tan confiable es el trabajo de campo?", "Sirve para validar el problema, no para medir todo el barrio",
   "Es una muestra pequeña e intencional; por eso se usa para entender, no para proyectar cifras.",
   ["Transcripciones verificadas con Whisper (92 % de coincidencia) y doble codificación con 96,9 % de acuerdo (kappa 0,70).",
    "Se siguió la lista de chequeo COREQ para estudios cualitativos."]),

  # ------------------------------------------------------------------ competencia
  (["Competencia"], "¿Quién es la competencia?", "Las canecas con pedal y los procesadores eléctricos",
   "Las canecas solo guardan la basura; los eléctricos cuestan más de un millón y gastan luz.",
   ["Precios a octubre de 2026: caneca inoxidable con pedal de 20 L $119.900 (Homecenter); FoodCycler $1.265.000 (Best Buy); Lomi 3 $1.737.000 (lomi.com, dólar a $3.163,76)."]),
  (["Diferenciación", "Competencia"], "¿Qué los hace diferentes?", "Tritura sin electricidad, no huele y cuesta lo de una buena caneca",
   "Es de 6 a 9 veces más barato que un procesador eléctrico y no tiene motor que se dañe.",
   ["1.265.000 ÷ 199.900 = 6,3 veces; 1.737.000 ÷ 199.900 = 8,7 veces.",
    "Sin motor: no gasta luz, no hay piezas eléctricas que se quemen y no necesita enchufe cerca."]),
  (["Competencia", "Diferenciación"], "¿Ya existe un producto así?", "No encontramos uno a pedal a la venta",
   "Solo hay prototipos y proyectos caseros.",
   ["Atomlab (India) y Low-Tech Lab (Francia) tienen trituradores a pedal caseros; el Green Cycler (EE. UU.) es de manivela y demuestra que el corte manual funciona."]),
  (["Patente", "Copiar o importar"], "¿Qué impide que los copien?", "Registro ante la SIC y la ventaja de costo",
   "El diseño se protege con registros, y fabricar en casa da un costo difícil de igualar.",
   ["Modelo de utilidad y diseño industrial ante la SIC, y registro de la marca (≈$6,8 M, en los gastos de arranque).",
    "Producir cuesta $101.373 con resina comprada por tonelada y cuchillas hechas en casa; un importador pagaría flete, arancel y el margen del fabricante."]),
  (["Copiar o importar", "Fábrica propia"], "¿Por qué no importarlo de China?", "No hay un producto a pedal que importar",
   "Hacerlo afuera exigiría los mismos moldes y además flete, arancel y el margen del maquilador.",
   ["Con fábrica propia se controla la calidad (sobre todo el temple de las cuchillas) y los tiempos de entrega, y se genera empleo en Colombia."]),

  # ------------------------------------------------------------------ producto
  (["Cómo funciona"], "¿Cómo funciona RECOEVO?", "Se echan las cáscaras, se pisa unos 20 segundos al día y 13 cuchillas las cortan",
   "Funciona con el pie, sin electricidad, y deja los restos en una bolsa compostable cerrada.",
   ["Boca de 12 × 10 cm; unas 11 pisadas al día, de ≈13,2 julios cada una; tiras de ≈5 mm.",
    "Caen a un balde de 10 L con bolsa compostable; una bolsa cerrada por semana para la ruta de orgánicos."]),
  (["Prototipo", "Cómo funciona"], "¿Está comprobado que funciona?", "Los cálculos cuadran; falta la prueba física con la preserie",
   "La fuerza del pie alcanza de sobra para cortar restos de cocina.",
   ["La cuchilla empuja ≈170 N con fuerza media (una zanahoria cruda pide de 100 a 200 N).",
    "Las piezas trabajan por debajo de su límite: el piñón a ≈158 de 250 MPa y el eje a ≈57 de 215 MPa.",
    "El desarrollo y los ensayos del producto están presupuestados: $75 M."]),
  (["Prototipo"], "¿Tienen prototipo?", "Sí: un prototipo inicial en 3D, en el código QR",
   "En la página del QR se puede mover y desarmar pieza por pieza.",
   ["El siguiente paso es la preserie física, para pruebas y preventas."]),
  (["Cuchillas"], "¿Cuánto duran las cuchillas?", "Varios años con residuo de cocina",
   "Son de acero inoxidable templado, hechas en la fábrica.",
   ["13 cuchillas de acero inoxidable tipo 420, templadas a 48–52 HRC.",
    "Un juego cuesta ≈$7.364 fabricado en casa; la vida exacta se confirma con un ensayo de desgaste en la preserie."]),
  (["Filtro y olor"], "¿Cómo controlan el olor?", "Filtro de carbón activado, juntas y una válvula",
   "El olor queda encerrado y el aire sale limpio.",
   ["Juntas de caucho (EPDM) en la tapa y la puerta, filtro de 60 g de carbón activado que dura 6 meses y válvula de una vía.",
    "El líquido de los restos lo absorbe un material seco opcional."]),
  (["Bolsas", "Material seco"], "¿Qué bolsas usa y qué es el material seco?", "Cualquier bolsa compostable; el material seco es opcional",
   "El material seco absorbe el líquido: papel, cartón picado, hojas secas o aserrín. Si la bolsa se saca cada 2 o 3 días, no hace falta.",
   ["Un hogar produce ≈3,4 kg de orgánicos por semana, que triturados ocupan ≈5,6 L; el balde tiene 7,5 L útiles: una bolsa por semana alcanza.",
    "El pedal izquierdo echa el material seco (≈3 porciones de 40 mL al día)."]),
  (["Seguridad"], "¿Es seguro si hay niños en casa?", "Sí: con la tapa abierta el pedal se bloquea",
   "No tiene motor: si se suelta el pie, todo se detiene.",
   ["Un pasador bloquea la cremallera con la tapa abierta; la boca y la tolva no dejan meter la mano hasta las cuchillas; la puerta tiene cierre de doble acción.",
    "Se valida con 20.000 ciclos del seguro antes de salir al mercado."]),
  (["Atascos", "Seguridad"], "¿Qué pasa si entra un hueso o una cuchara?", "El pedal se detiene y una perilla de reversa lo destraba",
   "Como no hay volante ni motor, no hay energía guardada que dañe las cuchillas.",
   ["El manual excluye huesos, semillas duras y fibras largas."]),
  (["Tamaño y peso", "Plástico reciclado"], "¿Cuánto mide, cuánto pesa y de qué está hecho?", "32 × 34 × 52 cm, ≈5 kg, con 70 % de plástico reciclado",
   "Ocupa lo de una caneca y va al lado del mesón de la cocina.",
   ["Gabinete y base en polipropileno 70 % reciclado; cuchillas y eje en acero inoxidable.",
    "Caja de envío: 55 × 34 × 32 cm y 5,6 kg."]),
  (["Garantía"], "¿Tiene garantía?", "Sí: la garantía legal, con una reserva del 3 % de las ventas",
   "Si algo falla, la empresa lo repara.",
   ["Ley 1480 de 2011 (Estatuto del Consumidor).", "En el presupuesto: «Distribución a clientes y garantía»."]),

  # ------------------------------------------------------------------ fábrica
  (["Fábrica propia"], "¿Qué fabrican y qué compran?", "Fabrican casi todo desde la materia prima",
   "Se compra resina, acero y carbón por kilo o tonelada, y en la planta se hacen las piezas.",
   ["Se inyectan las 12 piezas plásticas, se estampan y templan las cuchillas, se hacen los resortes, se cortan en láser el piñón y la cremallera, y se ensambla y prueba el 100 %.",
    "Se compran hechos solo tornillos, retenes, juntas, la válvula y la caja impresa."]),
  (["Fábrica propia", "Costo por producto"], "¿Por qué fabricar y no mandar a hacer?", "Con este volumen sale más barato",
   "Mandar a hacer las piezas costaría mucho más por cada producto.",
   ["Piezas plásticas: ≈$25.368 por producto con inyección propia, frente a $38.311 en maquila.",
    "Cuchillas: ≈$7.364 hechas en casa, frente a $20.660 en maquila local."]),
  (["Capacidad"], "¿Cuánto puede producir la fábrica?", "Hasta ≈11.453 productos al mes",
   "Arranca con un turno y crece a tres a medida que suben las ventas.",
   ["Con 3 turnos de inyección y 2 de ensamble: ≈559 por día hábil y 137.438 al año.",
    "El año 1 trabaja 1 turno (≈3.818 al mes). El cuello de botella se calcula máquina por máquina."]),
  (["Máquinas y moldes"], "¿Qué máquinas compran?", "97 máquinas y equipos por $1.672 M, más 13 moldes por $1.013 M",
   "Son nuevas, servo y de China; los moldes se hacen a la medida.",
   ["3 inyectoras (650, 400 y 250 toneladas) con robots, prensa de 80 toneladas, horno de temple, enrolladora de resortes, láser y torno.",
    "Los moldes aguantan ≈1 millón de piezas."]),
  (["Planta"], "¿Dónde queda la planta?", "Una bodega de 1.150 m² en la Sabana de Bogotá",
   "En Soacha o Funza, cerca de Bogotá y de las vías nacionales.",
   ["Arriendo de ≈$21.000 por m² al mes y un transformador de 225 kVA para las inyectoras."]),
  (["Empleos"], "¿Cuántos empleos generan?", "34 empleos directos en el mejor momento",
   "Es un equipo pequeño que crece con las ventas.",
   ["Año 1: 7 personas fijas y 4–5 operarios; los operarios se contratan por escalones según el volumen.",
    "Redes y página web por prestación de servicios."]),
  (["Materia prima"], "¿Cómo compran la materia prima?", "Por kilo y por tonelada",
   "Comprar al por mayor baja el costo de cada producto.",
   ["En el año 3: ≈170 toneladas de resina al año y ≈40 de fleje inoxidable (un contenedor cada 2–3 meses).",
    "La primera ronda de producción: 4.400 productos, $193 M en materia prima."]),

  # ------------------------------------------------------------------ ventas y canales
  (["Canales"], "¿Por dónde venden y en qué proporción?", "Marketplaces 35 % · lotes 35 % · tienda propia 15 % · cadenas 15 %",
   "Se combinan canales que llegan a todo el país con los que venden por volumen.",
   ["Marketplaces: cobran alrededor del 14 % y llegan a todo el país.",
    "Lotes: un precio 15 % más bajo ($142.000 + IVA frente a $167.983 sin IVA al público), pero cientos de productos de una vez.",
    "Tienda propia: no hay intermediario; solo se paga la pasarela de pago (≈3,5 %), pero cada venta cuesta ≈$26.877 de publicidad.",
    "Cadenas: se quedan con cerca del 40 % y pagan a 60 días o más; por eso solo el 15 %."]),
  (["Marketplaces", "Comisiones"], "¿Cuánto cobran los marketplaces?", "Alrededor del 14 %",
   "Solo se paga la comisión cuando se vende.",
   ["Mercado Libre: 9 a 20 % según la categoría; Éxito.com: 8 a 20 % + IVA; Falabella.com ≈15 %. El plan usa 14 %."]),
  (["Grandes superficies", "Comisiones"], "¿Por qué solo el 15 % en almacenes de cadena?", "Porque se quedan con cerca del 40 % del precio",
   "Venden en muchas ciudades, pero cobran caro y pagan tarde.",
   ["Margen de la cadena de 30 a 35 % más cobros de 8 a 12 % (codificación, promociones, devoluciones).",
    "Pagan a 45–90 días."]),
  (["Tienda en línea", "Comisiones"], "¿Cuánto deja una venta en la tienda en línea propia?", "≈$161.000 antes de publicidad · ≈$134.000 después",
   "En la tienda propia no hay un almacén ni un marketplace en medio: la empresa recibe el precio completo sin IVA y solo paga la pasarela de pago (la empresa que procesa la tarjeta, PSE o Nequi). Pero tiene que pagar anuncios para conseguir cada venta.",
   ["Precio sin IVA: $167.983.",
    "Pasarela de pago: ≈3,5 % del pago = 199.900 × 3,5 % ≈ $6.997 → quedan ≈$160.986.",
    "Publicidad en Meta y Google: ≈$26.877 por venta en línea → quedan ≈$134.109.",
    "Para comparar: en un marketplace quedan ≈$144.465 (después del 14 % de comisión) y en una cadena ≈$100.790. El envío lo paga el cliente aparte."]),
  (["Lotes", "Precio"], "¿Cuánto cuesta por lote, qué descuento tiene y cómo llegaron a él?", "$142.000 + IVA por producto: 15 % menos que al público",
   "Es un descuento por volumen para pedidos de 100 productos o más, entregados. Con IVA son $168.980, frente a $199.900 al público. Se fijó para que la empresa nunca venda por debajo de lo que le cuesta cada producto.",
   ["El descuento: precio al público sin IVA 199.900 ÷ 1,19 = $167.983; lote $142.000; 142.000 ÷ 167.983 = 0,845, o sea 15,5 % menos.",
    "Cómo se llegó: es un supuesto del plan (hoja «Supuestos»: «precio por lotes a empresas, sin IVA, entregado», para 100 productos o más) con una regla: nunca por debajo del costo total. Como sube con la inflación, en promedio de los 10 años la empresa recibe $195.360 por producto en lotes, más que el costo total promedio de $144.319.",
    "Para comparar: en un marketplace, después del 14 % de comisión, a la empresa le quedan ≈$144.465 por producto; en una cadena, que se queda el 40 %, ≈$100.790. El lote deja $142.000 sin comisión ni publicidad por venta.",
    "En el presupuesto: tabla 10, «Lotes a empresas, conjuntos y alcaldías», 259.491 productos (35 %) por $50.694 M en 10 años. El taller de separación ($8.000 + IVA por producto) va en «Envíos y talleres», y el flete de la entrega en «Distribución a clientes y garantía» (tabla 7)."]),
  (["Envíos"], "¿Los costos de envío están incluidos? ¿Quién los paga?", "En internet lo paga el cliente; a cadenas y lotes, la empresa",
   "En las ventas por internet el envío se cobra aparte, al costo más 10 %. A cadenas y lotes se lleva en estibas y el flete ya está en los costos.",
   ["Por zona: Bogotá $14.900 (le cuesta a la empresa $13.000), Sabana $17.900, ciudades principales $26.900, intermedias $31.900 y municipios lejanos $41.900; promedio $20.270 (costo $18.000).",
    "La caja pesa 5,6 kg, pero la transportadora la cobra como 15 kg por su tamaño.",
    "Cadenas y lotes: «Distribución a clientes y garantía», $8.271 por producto (presupuesto, tabla 7)."]),
  (["Marketing", "Tienda en línea", "Canales"], "¿En qué canales hay que pagar publicidad y cuánto está en el presupuesto?", "Solo por las ventas de la tienda propia: ≈$26.877 por venta, $2.952 M en 10 años",
   "En marketplaces, cadenas y lotes no se paga un anuncio por cada venta: ahí se paga una comisión o el margen del almacén. Aparte hay un marketing fijo que sirve a toda la marca.",
   ["Anuncios en Meta y Google: 109.839 ventas de la tienda propia × ≈$26.877 = $2.952 M (presupuesto, tabla 7).",
    "Marketplaces: comisión de ≈14 % por venta. Cadenas: su margen de 30–35 % más cobros de 8–12 %, que incluyen promociones. Lotes: 2 % para el vendedor de empresas.",
    "Marketing fijo para toda la marca (redes, web, demostraciones en almacenes, ferias e islas): $2.841 M en 10 años, ≈$23,7 M al mes.",
    "Todo junto, publicidad y comercialización suman $22.167 M en 10 años, $30.141 por producto: comisiones $10.291 M + distribución y garantía $6.083 M + anuncios $2.952 M + marketing fijo $2.841 M."]),
  (["Marketing"], "¿Cuánto invierten en marketing?", "≈$2.841 M de marketing fijo y ≈$2.952 M en anuncios en 10 años",
   "Redes, página web, demostraciones en almacenes, ferias e islas en centros comerciales, más anuncios por cada venta en línea.",
   ["Marketing fijo ≈$23,7 M al mes en promedio; anuncios ≈$26.877 por venta en línea (presupuesto, tabla 7)."]),
  (["Cuotas", "Precio"], "¿Se puede pagar a cuotas?", "Sí: 12 cuotas de $16.658",
   "Se paga con los medios de pago de siempre en Colombia: tarjeta, PSE, Nequi, Daviplata, Bancolombia, efectivo o Addi.",
   ["199.900 ÷ 12 = 16.658."]),

  # ------------------------------------------------------------------ impacto y ODS
  (["Toneladas", "Doña Juana"], "¿Cuánta basura le quitan a Doña Juana?", "≈407.000 toneladas en 10 años: lo que recibe en dos meses",
   "Los hogares llegan poco a poco, así que el impacto crece cada año.",
   ["Toneladas por año: año 1 ≈1.100 · año 2 ≈4.600 · año 3 ≈10.600 · año 4 ≈19.000 · año 5 ≈29.300 · año 6 ≈41.100 · año 7 ≈54.000 · año 8 ≈67.700 · año 9 ≈82.200 · año 10 ≈97.600.",
    "407.000 ÷ 6.800 t al día ≈ 60 días; es el 1,6 % de lo que le llegaría en 10 años.",
    "En el año 10, con todos los hogares: 735.450 × 0,46 kg × 85 % ≈ 288 t al día, el 4 % de lo que entra hoy cada día."]),
  (["Toneladas"], "¿De dónde sale el medio kilo de comida por hogar al día?", "Es un supuesto del plan, menos de la mitad del dato de la UAESP",
   "Usamos 0,46 kg por hogar al día, y que el 85 % de los hogares lo usa a diario. El impacto real podría ser mayor.",
   ["No se pesó en el trabajo de campo, que fue de entrevistas.",
    "UAESP: los hogares de Bogotá sacan ≈3.440 t de orgánicos al día; entre 2,9 millones de hogares da ≈1,2 kg por hogar."]),
  (["CO₂", "Metano", "Toneladas"], "¿Cuánto CO₂ evitan?", "≈203.491 toneladas de CO₂ equivalente en 10 años",
   "Es el efecto de no enterrar esa comida, que en el relleno produciría metano.",
   ["Cálculo del plan a partir de las 406.983 toneladas, con un factor conservador que falta validar."]),
  (["ODS"], "¿Qué Objetivos de Desarrollo Sostenible ataca y por qué?", "El 12, el 11 y el 13",
   "ODS 12, Producción y consumo responsables: menos comida desperdiciada. ODS 11, Ciudades y comunidades sostenibles: menos bolsas rotas, ratas y carga para Doña Juana. ODS 13, Acción por el clima: menos metano.",
   ["Metas de la Agenda 2030 de la ONU: 12.3 (reducir a la mitad el desperdicio de alimentos), 12.5 (reducir la basura) y 11.6 (mejor manejo de los residuos de las ciudades).",
    "Metano: unas 80 veces más potente que el CO₂ en 20 años."]),
  (["Compost"], "¿RECOEVO produce abono?", "No: deja los restos listos para la ruta de orgánicos o para compostar",
   "Convertir esas bolsas en abono para el campo es la fase 2, y está por fuera de las cifras.",
   ["Si se compostaran, las 406.983 toneladas darían ≈142.444 toneladas de compost (plan detallado)."]),
  (["Plástico reciclado"], "¿Qué tan sostenible es el producto en sí?", "70 % de plástico reciclado en las piezas grandes y cero electricidad",
   "No gasta luz en toda su vida y usa plástico reciclado en el gabinete y la base.",
   ["Gabinete y base en polipropileno 70 % reciclado; la empresa cumple el plan de envases (REP)."]),

  # ------------------------------------------------------------------ proyecto y equipo
  (["Origen de la idea", "Usme"], "¿Cómo nació la idea?", "En la cuadra de Samuel, en Villa Rosita (Usme)",
   "Nuestro compañero Samuel vive con este problema todos los días; de ahí salió la idea y ahí la validamos.",
   ["Luego unimos los dos problemas: la comida que se entierra en la ciudad y el abono caro del campo, más el Decreto 0772 que obliga a separar."]),
  (["Equipo"], "¿Quiénes son y quién sabe manejar una fábrica?", "Cinco estudiantes del Politécnico Grancolombiano",
   "Somos de mercadeo y de ingeniería de sistemas; por eso buscamos mentoría en administración.",
   ["Ricardo Beltrán, William Fonseca, Samuel Medina, Faber Ortiz y Camila Riaño. Docente: Ingrid Zoraida Sandoval Pérez.",
    "En el plan, la parte técnica la cubre un jefe de producción con experiencia en plásticos desde el montaje y un ingeniero de procesos desde el año 2."]),
  (["Metodologías"], "¿Qué metodologías usaron?", "Design Thinking, Lean Startup y cuatro herramientas más",
   "Empatizar en Usme, definir el problema, idear y prototipar.",
   ["Investigación de campo, Customer Journey Map, Value Proposition Canvas y Business Model Canvas (marco metodológico del póster)."]),
  (["Siguiente paso"], "¿Qué sigue ahora?", "Una preserie para preventas y cartas de intención",
   "Probar la demanda y el producto antes de crecer.",
   ["Preserie física con ensayos (cuchillas, seguro), preventas a hogares y cartas de intención de grandes superficies (Lean Startup)."]),
]

FUENTES = [
  "Póster RECOEVO E-Fest 2026-2 y sus 10 fuentes (Superservicios 2024; Secretaría del Hábitat; UAESP; El Tiempo, 16-oct-2026; Semana; El Colombiano; DANE-SIPSA; Agronegocios; Homecenter, Best Buy, lomi.com; estudio de campo en Villa Rosita, 19-sep-2026).",
  "RECOEVO, presupuesto ejecutivo y plan financiero a 10 años, escenario realista (3-nov-2026): tablas 4, 9, 10, 11, 13 y 14.",
  'Decreto 0772 de 2026, Ministerio de Vivienda: <a href="https://normas.cra.gov.co/gestor/docs/decreto_0772_2026.htm">normas.cra.gov.co</a>.',
  'Usme, 414.995 habitantes: Observatorio de Salud de Bogotá, «Usme +Bienestar 2024» (<a href="https://saludata.saludcapital.gov.co/osb/wp-content/uploads/2024/12/Usme_MasBienestar_2024_v1_2.pdf">saludata</a>).',
  'Usme, 3,07 personas por hogar: DANE, Encuesta Multipropósito 2021 (<a href="https://www.dane.gov.co/files/investigaciones/multi/Presentacion_EM_2021.pdf">dane.gov.co</a>).',
  'Usme, 85,9 % rural (18.477 de 21.507 ha): Universidad Santo Tomás (<a href="https://repository.usta.edu.co/items/18786bd5-dfd9-489f-a768-c6a314d7cc83">repositorio</a>). Unos 17.000 campesinos: Alcaldía de Bogotá (<a href="https://bogota.gov.co/mi-ciudad/desarrollo-economico/el-distrito-celebra-el-dia-del-campesino">bogota.gov.co</a>).',
  'Bogotá, unos 2,9 millones de hogares: DANE, Encuesta Multipropósito 2025 (<a href="https://www.portafolio.co/economia/bogota-tiene-cada-vez-mas-hogares-unipersonales-el-promedio-de-personas-por-hogar-cayo-a-2-7-en-505292">Portafolio</a>). Orgánicos de los hogares de Bogotá, unas 3.440 t al día: UAESP (2022).',
  'Comisiones por canal (marketplaces, cadenas, pasarelas de pago): informe RECOEVO B7, márgenes y canales 2026. Envíos por zona: plan detallado realista, hoja «9 Ventas y marketing», sección 3. Metano: unas 80 veces el CO₂ en 20 años (El Tiempo, 16-oct-2026, con datos citados por Greenpeace). ODS: metas 12.3, 12.5 y 11.6 de la Agenda 2030 de la ONU.',
  'Acceso a Doña Juana por la vía al Llano, antes de Usme: Blu Radio (<a href="https://www.bluradio.com/medio-ambiente/dona-juana-entienda-que-paso-y-como-funciona-el-relleno-sanitario-de-bogota">bluradio.com</a>).',
  "Método para memorizar: práctica de recuperación (Roediger y Karpicke, 2006); efecto de producción, decir en voz alta (MacLeod y otros, 2010); práctica espaciada (Cepeda y otros, 2006); pistas que desaparecen (Glisky, Schacter y Tulving, 1986); método de los lugares (Dresler y otros, 2017).",
]

# ------------------------------------------------------------------ filtros de preguntas
import unicodedata
UAESP = "UAESP (la entidad de la Alcaldía de Bogotá que maneja el aseo y Doña Juana)"
def orden(t):
    return "".join(ch for ch in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(ch) != "Mn")
def con_uaesp(textos):
    """La primera vez que aparece «UAESP» en una tarjeta, dice qué es."""
    hecho, out = False, []
    for t in textos:
        if not hecho and "UAESP" in t:
            t = t.replace("UAESP", UAESP, 1); hecho = True
        out.append(t)
    return out
_todas = {k for ks in GRUPOS.values() for k in ks}
for ks, q, *_ in BANCO:
    for k in ks:
        assert k == PROFE or k in _todas, f"palabra clave sin grupo: {k} ({q})"
for k in _todas:
    assert any(k in ks for ks, *_ in BANCO), f"palabra clave sin preguntas: {k}"

# ------------------------------------------------------------------ página
CSS = r"""
:root{--hl:rgba(164,214,94,.5);--gesto:#7a5a35;--num:#0a6e35;--papel2:#f3efe3}
.volver{z-index:1000}
.pitch{max-width:860px;margin:0 auto;padding:6px 16px 10px;padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right))}
.kicker{font-family:"Lexend",system-ui,sans-serif;font-weight:700;font-size:13px;letter-spacing:1.6px;text-transform:uppercase;color:var(--evo);margin:0 0 6px}
.pitch h1{font-size:clamp(28px,7vw,44px);letter-spacing:-.4px}
.bajada{margin:10px 0 0;color:var(--suave);font-size:17px;max-width:40em}
.datos{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 0;padding:0;list-style:none}
.datos li{padding:6px 12px;border-radius:999px;background:var(--papel);border:1px solid var(--linea);font-weight:700;font-size:14.5px}
.datos li.dest{background:var(--monte);color:#fff;border-color:var(--monte)}
.modos{position:sticky;top:0;z-index:20;background:var(--crema);margin:18px -16px 0;padding:10px 16px 10px 128px;border-bottom:1px solid var(--linea);display:flex;gap:8px;padding-top:calc(10px + env(safe-area-inset-top))}
@media (max-width:700px){.modos{position:fixed;top:auto;bottom:0;left:0;right:0;margin:0;padding:6px max(6px,env(safe-area-inset-right)) calc(6px + env(safe-area-inset-bottom)) max(6px,env(safe-area-inset-left));border-top:1px solid var(--linea);border-bottom:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px;box-shadow:0 -6px 18px rgba(21,71,52,.08)}.modos a,.modos button{padding:9px 2px;font-size:12.5px;text-align:center;border-radius:12px;min-width:0;overflow:hidden;text-overflow:ellipsis}body{padding-bottom:76px}}
.modos a,.modos button{flex:none;font:inherit;font-family:"Lexend",system-ui,sans-serif;font-weight:600;font-size:15px;text-decoration:none;color:var(--monte);background:var(--papel);border:1px solid var(--linea);border-radius:999px;padding:9px 15px;cursor:pointer;white-space:nowrap}
.modos .tele{background:var(--monte);color:#fff;border-color:var(--monte)}
section{scroll-margin-top:80px}
@media (max-width:700px){section{scroll-margin-top:70px}}
h2.sec{font-size:clamp(24px,5.6vw,32px);margin:34px 0 4px}
.sec-sub{color:var(--suave);margin:0 0 14px;max-width:42em}
.orden{background:var(--papel);border:1px solid var(--linea);border-radius:18px;padding:14px 16px;margin:6px 0 4px}
.orden p{margin:0;font-size:16.5px}
.orden .lbl{font-family:"Lexend";font-weight:700;font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:var(--evo);display:block;margin-bottom:4px}
.orden .titulo{font-size:13px;margin-bottom:8px}
.orden .parte{display:grid;gap:4px;padding:8px 0;border-top:1px solid var(--linea)}
.orden .parte .lbl{color:var(--tierra);margin:0}
.orden ol{margin:0;padding-left:1.6em;display:grid;gap:4px}
.orden li{font-size:16px;line-height:1.4}
.orden li a{text-decoration:none;color:var(--monte)}
.orden li b{font-weight:800}
.orden li span{color:var(--suave)}
.leyenda{display:flex;flex-wrap:wrap;gap:4px 16px;font-size:14px;color:var(--suave);margin:10px 0 0}
.bloque{border-top:1px solid var(--linea);padding:20px 0 6px}
.b-cab{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;margin-bottom:8px}
.b-n{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:50%;background:var(--monte);color:#fff;font-family:"Lexend";font-weight:700;font-size:16px;flex:none}
.b-cab h3{font-size:21px}
.b-t{font-family:"Lexend";font-weight:600;font-size:13px;color:var(--monte);background:var(--papel2);border-radius:999px;padding:3px 10px;font-variant-numeric:tabular-nums}
.b-p{flex-basis:100%;font-size:14px;color:var(--suave);margin-left:44px}
.b-texto p{margin:0 0 12px;font-size:19px;line-height:1.7;max-width:40em}
.b-texto strong{font-weight:800;background:linear-gradient(transparent 60%,var(--hl) 60%)}
.num{font-family:"Lexend",system-ui,sans-serif;font-weight:700;color:var(--num);white-space:nowrap}
.gesto{display:inline-block;font-style:italic;font-size:14.5px;color:var(--gesto);background:var(--papel2);border-radius:8px;padding:0 8px;margin-right:4px}
.opc{color:var(--suave)}
.opc::after{content:" ✂";color:var(--tierra);font-weight:700}
.total{margin:8px 0 0;padding:12px 16px;border-radius:16px;background:rgba(164,214,94,.22);border:1px solid rgba(14,154,72,.25);font-size:15.5px}
/* práctica */
.metodo{margin:0;padding:0;list-style:none;display:grid;gap:10px;counter-reset:m}
.metodo li{display:grid;grid-template-columns:34px 1fr;gap:10px;align-items:start;font-size:16.5px}
.metodo li::before{counter-increment:m;content:counter(m);display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:var(--sol);color:var(--monte);font-family:"Lexend";font-weight:700;font-size:15px}
.metodo b{color:var(--monte)}
.por-que{font-size:14.5px;color:var(--suave);margin:10px 0 0}
.tarjeta-p{margin-top:18px;background:var(--papel);border:1px solid var(--linea);border-radius:22px;box-shadow:var(--sombra);padding:18px}
.tp-top{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;justify-content:space-between}
.tp-paso{font-family:"Lexend";font-weight:700;font-size:13px;letter-spacing:1.2px;text-transform:uppercase;color:var(--evo)}
.tp-modo{display:inline-flex;border:1px solid var(--linea);border-radius:999px;overflow:hidden}
.tp-modo button{font:inherit;font-size:14px;font-weight:700;border:0;background:var(--papel);color:var(--monte);padding:7px 12px;cursor:pointer}
.tp-modo button[aria-pressed="true"]{background:var(--monte);color:#fff}
.barra-prog{height:6px;border-radius:99px;background:var(--papel2);margin:12px 0 14px;overflow:hidden}
.barra-prog i{display:block;height:100%;background:var(--evo);width:0;transition:width .3s}
.tp-preg{font-family:"Lexend";font-weight:700;color:var(--monte);font-size:clamp(20px,4.6vw,25px);line-height:1.3;margin:0}
.tp-inst{color:var(--suave);font-size:15px;margin:6px 0 0}
.tp-pistas{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0 0;padding:0;list-style:none}
.tp-pistas li{background:rgba(164,214,94,.3);border-radius:10px;padding:4px 10px;font-weight:700;font-size:15px}
.tp-guion{margin-top:14px;border-top:1px dashed var(--linea);padding-top:12px}
.tp-guion p{font-size:17.5px;line-height:1.65;margin:0 0 10px}
.tp-acc{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.btn{font:inherit;font-family:"Lexend",system-ui,sans-serif;font-weight:600;font-size:15px;border-radius:999px;padding:10px 16px;cursor:pointer;border:1px solid var(--monte);background:var(--monte);color:#fff}
.btn.sec{background:var(--papel);color:var(--monte);border-color:var(--linea)}
.btn.ok{background:var(--evo);border-color:var(--evo)}
.btn.rep{background:var(--sol);color:var(--monte);border-color:var(--sol)}
.tp-nav{display:flex;justify-content:space-between;gap:8px;margin-top:14px;border-top:1px solid var(--linea);padding-top:12px}
.marcas{display:flex;flex-wrap:wrap;gap:5px;margin-top:12px}
.marcas button{font:inherit;font-family:"Lexend";font-weight:700;font-size:13px;width:32px;height:32px;border-radius:50%;border:1px solid var(--linea);background:var(--papel);color:var(--monte);cursor:pointer}
.marcas button.ok{background:var(--evo);color:#fff;border-color:var(--evo)}
.marcas button.rep{background:var(--sol);border-color:var(--sol)}
.marcas button.act{outline:3px solid var(--monte);outline-offset:1px}
/* preguntas */
.profe{display:grid;gap:10px}
.q{background:var(--papel);border:1px solid var(--linea);border-radius:18px;padding:14px 16px}
.q-p{font-weight:800;color:var(--monte);font-size:16.5px;margin:0}
.q-r{font-family:"Lexend";font-weight:700;font-size:clamp(22px,5.4vw,28px);color:var(--num);line-height:1.2;margin:4px 0 2px}
.q-d{margin:0;font-size:16px}
.q details{margin-top:8px}
.q summary{cursor:pointer;font-weight:700;color:var(--evo);font-size:15px}
.q ul{margin:8px 0 0;padding-left:1.15em;display:grid;gap:4px;font-size:15px}
.otras details{border-top:1px solid var(--linea);padding:12px 0}
.otras summary{cursor:pointer;font-weight:800;color:var(--monte)}
.otras p{margin:8px 0 0;font-size:16px}
.fuentes{font-size:14px;color:var(--suave)}
.fuentes ol{padding-left:1.2em;display:grid;gap:5px}
.fuentes summary{cursor:pointer;font-weight:700;color:var(--monte);font-size:16px}
/* teleprompter */
.tele-capa{position:fixed;inset:0;z-index:2000;background:#0b1410;color:#f4f1e8;display:flex;flex-direction:column}
.tele-capa[hidden]{display:none}
.tele-texto{flex:1 1 auto;min-height:0;overflow-y:auto;padding:0 max(20px,env(safe-area-inset-right)) 0 max(20px,env(safe-area-inset-left));scrollbar-width:none}
.tele-texto::-webkit-scrollbar{display:none}
.tele-texto .in{max-width:900px;margin:0 auto;padding:38vh 0 60vh}
.tele-texto h4{font-family:"Lexend";font-size:.5em;letter-spacing:2px;text-transform:uppercase;color:var(--brote);margin:1.4em 0 .4em}
.tele-texto p{margin:0 0 .7em;line-height:1.45}
.tele-texto strong{color:#fff;font-weight:800}
.tele-texto .num{color:var(--sol)}
.tele-texto .gesto{background:transparent;color:#8fd1a8;font-size:.55em;padding:0}
.tele-texto .opc{color:#b9c2b8}
.tele-guia{position:absolute;left:0;right:0;top:38vh;height:2px;background:rgba(242,178,39,.55);pointer-events:none}
.tele-guia::before{content:"";position:absolute;left:6px;top:-7px;border:8px solid transparent;border-left:12px solid var(--sol)}
.tele-saltos{position:absolute;right:max(10px,env(safe-area-inset-right));top:calc(38vh - 70px);display:grid;gap:10px;z-index:2}
.tele-saltos button{display:grid;place-items:center;gap:2px;width:64px;height:64px;border-radius:18px;border:1px solid rgba(255,255,255,.3);background:rgba(20,35,27,.85);color:#fff;cursor:pointer;font:inherit;font-family:"Lexend";font-size:11px;font-weight:600;padding:6px 0;touch-action:manipulation}
.tele-saltos button:active{background:var(--sol);color:var(--monte)}
.tele-saltos svg{width:26px;height:26px;fill:none;stroke:currentColor;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}
.tele-texto .in{padding-right:64px}
.tele-ctl{flex:none;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:8px;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:#14231b;border-top:1px solid rgba(255,255,255,.12)}
.tele-ctl button{font:inherit;font-family:"Lexend";font-weight:600;font-size:15px;border-radius:999px;border:1px solid rgba(255,255,255,.25);background:transparent;color:#fff;padding:9px 14px;cursor:pointer;min-width:44px}
.tele-ctl .play{background:var(--sol);color:var(--monte);border-color:var(--sol);min-width:110px}
.tele-ctl output{font-family:"Lexend";font-weight:700;font-size:20px;min-width:56px;text-align:center;font-variant-numeric:tabular-nums}
.tele-ctl small{color:#b9c2b8;font-size:13px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.buscador{display:flex;gap:8px;align-items:stretch;margin:4px 0 10px}
.buscador input{flex:1;min-width:0;font:inherit;font-size:17px;padding:14px 16px;border-radius:16px;border:2px solid var(--monte);background:var(--papel);color:var(--tinta)}
.buscador input:focus{outline:3px solid var(--sol);outline-offset:2px}
#q-voz{flex:none;display:inline-flex;align-items:center;gap:6px;font:inherit;font-family:"Lexend",system-ui,sans-serif;font-weight:600;font-size:15px;border:0;border-radius:16px;background:var(--monte);color:#fff;padding:0 14px;cursor:pointer}
#q-voz svg{width:20px;height:20px;fill:currentColor}
#q-voz.oyendo{background:var(--sol);color:var(--monte)}
.atajos{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px}
.atajos button{font:inherit;font-size:14px;font-weight:700;border:1px solid var(--linea);background:var(--papel);color:var(--monte);border-radius:999px;padding:6px 12px;cursor:pointer}
.q-estado{color:var(--suave);font-size:15px;margin:0 0 10px;min-height:1.2em}
.q-lista{display:grid;gap:10px}
.grupo-t{font-size:20px;margin:14px 0 2px}
.q-lista.buscando .grupo-t{display:none}
.q.top{outline:3px solid var(--sol);outline-offset:0}
.q.top::before{content:"Respuesta más probable";display:inline-block;font-family:"Lexend";font-weight:700;font-size:12px;letter-spacing:.8px;text-transform:uppercase;background:var(--sol);color:var(--monte);border-radius:999px;padding:3px 10px;margin-bottom:6px}
.q[hidden],.grupo-t[hidden]{display:none!important}
.filtros{display:grid;gap:12px;background:var(--papel);border:1px solid var(--linea);border-radius:20px;padding:14px}
.f-top{display:flex;flex-wrap:wrap;gap:8px}
.f-grupo{display:grid;gap:6px;border-top:1px solid var(--linea);padding-top:10px}
.f-g{font-family:"Lexend";font-weight:700;font-size:12px;letter-spacing:1.3px;text-transform:uppercase;color:var(--evo)}
.f-chips{display:flex;flex-wrap:wrap;gap:6px}
.filtros button,.q-tags button{font:inherit;font-size:14px;font-weight:700;border:1px solid var(--linea);background:var(--crema);color:var(--monte);border-radius:999px;padding:6px 11px;cursor:pointer;line-height:1.2}
.filtros button span{display:inline-block;min-width:1.5em;text-align:center;font-size:12px;background:var(--papel);border-radius:999px;padding:1px 6px;margin-left:3px;color:var(--suave)}
.filtros button.activo{background:var(--monte);color:#fff;border-color:var(--monte)}
.filtros button.activo span{background:var(--sol);color:var(--monte)}
.f-top button{font-size:15px;padding:8px 14px}
.q-estado{font-family:"Lexend";font-weight:700;color:var(--monte);font-size:16px;margin:14px 0 8px;scroll-margin-top:76px}
.q-s{margin:6px 0 0;font-size:16px}
.q-s b,.q-c b{color:var(--monte)}
.q-c{margin-top:8px;font-size:15px}
.q-c ul{margin:4px 0 0;padding-left:1.15em;display:grid;gap:4px}
.q-tags{display:flex;flex-wrap:wrap;gap:5px;margin:10px 0 0}
.q-tags button{font-size:12.5px;padding:3px 9px;background:var(--papel)}
.tele-texto{cursor:grab;touch-action:none;user-select:none;-webkit-user-select:none}
.tele-texto.arrastrando{cursor:grabbing}
.tele-texto .in{position:relative}
.tele-marca{position:absolute;left:-10px;right:-10px;top:0;height:0;border-radius:10px;background:rgba(242,178,39,.28);box-shadow:inset 4px 0 0 var(--sol);opacity:0;pointer-events:none;transition:opacity .25s}
.tele-marca.ver{opacity:1}
.tele-ayuda{flex-basis:100%;text-align:center;color:#b9c2b8;font-size:12.5px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
@media print{.modos,.volver,#practicar .tarjeta-p,.tele-capa{display:none!important}.b-texto p{font-size:13pt}}
"""

JS = r"""
(function(){
  "use strict";
  var B=[].slice.call(document.querySelectorAll(".bloque"));
  var DATOS=B.map(function(b){return {n:Number(b.dataset.n),t:b.querySelector("h3").textContent,preg:b.dataset.pregunta,pistas:JSON.parse(b.dataset.pistas),ancla:b.dataset.ancla,html:b.querySelector(".b-texto").innerHTML};});
  var TOTAL=Number(document.body.dataset.total||280);
  function mmss(s){s=Math.max(0,Math.round(s));return Math.floor(s/60)+":"+String(s%60).padStart(2,"0");}
  function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}

  /* ---------- filtros de preguntas ---------- */
  var $=function(id){return document.getElementById(id);};
  var lista=$("q-lista"), estado=$("q-estado"), filtros=$("filtros");
  if(lista&&filtros){
    var tarj=[].slice.call(lista.querySelectorAll(".q"));
    var filtrar=function(k,desplazar){
      var n=0;
      tarj.forEach(function(t){var ver=k==="*"||t.getAttribute("data-k").indexOf("|"+k+"|")>=0;t.hidden=!ver;if(ver)n++;});
      [].forEach.call(filtros.querySelectorAll("button"),function(b){b.classList.toggle("activo",b.getAttribute("data-k")===k);});
      estado.textContent=(k==="*"?"Todas las preguntas":"Tema: "+k)+" · "+n+(n===1?" pregunta":" preguntas");
      if(desplazar){estado.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"});}
    };
    filtros.addEventListener("click",function(e){var b=e.target.closest("button");if(b)filtrar(b.getAttribute("data-k"),true);});
    lista.addEventListener("click",function(e){var b=e.target.closest(".q-tags button");if(b)filtrar(b.getAttribute("data-k"),true);});
    filtrar(filtros.querySelector("button.activo").getAttribute("data-k"),false);
    window.filtrarPreguntas=function(k){filtrar(k,false);return tarj.filter(function(t){return !t.hidden;}).map(function(t){return t.querySelector(".q-p").textContent;});};
  }

  /* ---------- teleprompter ---------- */
  var capa=$("tele"), caja=$("tele-texto"), reloj=$("tele-reloj"), bPlay=$("tele-play"), vel=$("tele-vel");
  var corre=false, mult=1, tam=34, ult=0, seg=0, raf=0, resto=0;
  caja.querySelector(".in").innerHTML=DATOS.map(function(d){return "<h4>"+d.n+" · "+esc(d.t)+"</h4>"+d.html;}).join("");
  [].forEach.call(caja.querySelectorAll(".opc"),function(o){o.remove();});
  var interior=caja.querySelector(".in");
  (function envolver(){
    var tw=document.createTreeWalker(interior,NodeFilter.SHOW_TEXT),nodos=[];
    while(tw.nextNode())nodos.push(tw.currentNode);
    nodos.forEach(function(t){
      if(!t.nodeValue.trim())return;
      var f=document.createDocumentFragment();
      t.nodeValue.split(/(\s+)/).forEach(function(pz){if(!pz)return;
        if(/^\s+$/.test(pz))f.appendChild(document.createTextNode(pz));
        else{var w=document.createElement("span");w.className="w";w.textContent=pz;f.appendChild(w);}});
      t.parentNode.replaceChild(f,t);
    });
  })();
  var marca=document.createElement("div");marca.className="tele-marca";interior.appendChild(marca);
  var arrastre=null,tMarca=0;
  function marcar(w){if(!w)return;marca.style.top=(w.offsetTop-4)+"px";marca.style.height=(w.offsetHeight+8)+"px";marca.classList.add("ver");tMarca=Date.now();
    setTimeout(function(){if(!arrastre&&Date.now()-tMarca>=2900)marca.classList.remove("ver");},3000);}
  function palabraEn(x,y){var el=document.elementFromPoint(x,y);if(!el||!el.closest)return null;var w=el.closest(".w");if(w)return w;
    var bloque=el.closest("p,h4")||el,mejor=null,dist=1e9;
    [].forEach.call(bloque.querySelectorAll?bloque.querySelectorAll(".w"):[],function(c){var r=c.getBoundingClientRect(),d=Math.abs((r.top+r.bottom)/2-y)*4+Math.abs((r.left+r.right)/2-x);if(d<dist){dist=d;mejor=c;}});
    return mejor;}
  function palabraEnGuia(){var r=caja.getBoundingClientRect(),y=window.innerHeight*0.38+6;
    for(var x=r.left+r.width*0.2;x<r.left+r.width*0.8;x+=12){var w=palabraEn(x,y);if(w)return w;}return null;}
  caja.addEventListener("pointerdown",function(e){if(e.button>0||e.target.closest("button"))return;
    arrastre={y:e.clientY,s:caja.scrollTop};try{caja.setPointerCapture(e.pointerId);}catch(_){}
    caja.classList.add("arrastrando");marcar(palabraEn(e.clientX,e.clientY));});
  caja.addEventListener("pointermove",function(e){if(!arrastre)return;caja.scrollTop=Math.max(0,arrastre.s-(e.clientY-arrastre.y));resto=0;});
  function soltar(){if(!arrastre)return;arrastre=null;caja.classList.remove("arrastrando");tMarca=Date.now();
    setTimeout(function(){if(!arrastre&&Date.now()-tMarca>=2900)marca.classList.remove("ver");},3000);}
  caja.addEventListener("pointerup",soltar);caja.addEventListener("pointercancel",soltar);
  function pxSeg(){return (caja.scrollHeight-caja.clientHeight)/TOTAL*mult;}
  function paso(ts){
    if(!corre) return;
    var dt=ult?(ts-ult)/1000:0; ult=ts; seg+=dt;
    if(!arrastre){resto+=pxSeg()*dt; var entero=Math.floor(resto); if(entero>0){caja.scrollTop+=entero;resto-=entero;}}
    reloj.textContent=mmss(seg);
    if(caja.scrollTop+caja.clientHeight>=caja.scrollHeight-2){parar();bPlay.textContent="Terminó";}
    else raf=requestAnimationFrame(paso);
  }
  function arrancar(){corre=true;ult=0;bPlay.textContent="Pausa";raf=requestAnimationFrame(paso);}
  function parar(){corre=false;cancelAnimationFrame(raf);bPlay.textContent="Seguir";}
  function aplicarTam(){var r=caja.scrollTop/Math.max(1,caja.scrollHeight);caja.style.fontSize=tam+"px";caja.scrollTop=r*caja.scrollHeight;}
  function abrir(){capa.hidden=false;document.body.style.overflow="hidden";caja.scrollTop=0;seg=0;reloj.textContent="0:00";bPlay.textContent="Iniciar";tam=window.innerWidth<600?28:38;aplicarTam();try{capa.requestFullscreen&&capa.requestFullscreen().catch(function(){});}catch(e){}}
  function cerrar(){parar();capa.hidden=true;document.body.style.overflow="";try{document.fullscreenElement&&document.exitFullscreen();}catch(e){}}
  [].forEach.call(document.querySelectorAll("[data-tele]"),function(b){b.addEventListener("click",function(e){e.preventDefault();abrir();});});
  bPlay.onclick=function(){corre?parar():arrancar();};
  $("tele-mas").onclick=function(){mult=Math.min(2,Math.round((mult+0.1)*10)/10);vel.textContent=mult.toFixed(1)+"×";};
  $("tele-menos").onclick=function(){mult=Math.max(0.5,Math.round((mult-0.1)*10)/10);vel.textContent=mult.toFixed(1)+"×";};
  $("tele-amas").onclick=function(){tam=Math.min(64,tam+4);aplicarTam();};
  $("tele-amenos").onclick=function(){tam=Math.max(20,tam-4);aplicarTam();};
  $("tele-reini").onclick=function(){parar();caja.scrollTop=0;seg=0;reloj.textContent="0:00";bPlay.textContent="Iniciar";};
  function mover(n){var lh=tam*1.45,desde=caja.scrollTop,hasta=Math.max(0,desde+n*lh),t0=0;resto=0;
    var suave=!matchMedia("(prefers-reduced-motion: reduce)").matches;
    if(!suave){caja.scrollTop=hasta;marcar(palabraEnGuia());return;}
    function f(t){if(!t0)t0=t;var k=Math.min(1,(t-t0)/320);k=1-Math.pow(1-k,3);caja.scrollTop=desde+(hasta-desde)*k;
      if(k<1)requestAnimationFrame(f);else marcar(palabraEnGuia());}
    requestAnimationFrame(f);}
  $("tele-atras").onclick=function(){mover(-2);};
  $("tele-adelante").onclick=function(){mover(2);};
  $("tele-cerrar").onclick=cerrar;
  document.addEventListener("keydown",function(e){
    if(capa.hidden) return;
    if(e.key==="Escape") cerrar();
    else if(e.key===" "){e.preventDefault();corre?parar():arrancar();}
    else if(e.key==="ArrowUp") $("tele-menos").click();
    else if(e.key==="ArrowDown") $("tele-mas").click();
    else if(e.key==="ArrowLeft"||e.key==="PageUp"){e.preventDefault();mover(-2);}
    else if(e.key==="ArrowRight"||e.key==="PageDown"){e.preventDefault();mover(2);}
  });
})();
"""

def pagina(modo_suelto=False, web=None):
    filas, total, sin_opc = medir()
    bloques = []
    for i, (b, f) in enumerate(zip(GUION, filas), 1):
        pistas_json = e(__import__("json").dumps(b["pistas"], ensure_ascii=False))
        texto = "".join(f"<p>{html_parrafo(p)}</p>" for p in b["p"])
        bloques.append(
            f'<article class="bloque" id="b{i}" data-n="{i}" data-ancla="{e(b["ancla"])}" data-pregunta="{e(b["pregunta"])}" data-pistas="{pistas_json}">'
            f'<div class="b-cab"><span class="b-n">{i}</span><h3>{e(b["t"])}</h3><span class="b-t">{mmss(f["ini"])} – {mmss(f["fin"])}</span>'
            f'<span class="b-p">{e(b["poster"])}</span></div><div class="b-texto">{texto}</div></article>')
    partes_html = []
    for nombre, ini, fin in PARTES:
        items = "".join(f'<li value="{k}"><a href="#b{k}"><b>{e(GUION[k-1]["t"])}</b></a> <span>{e(GUION[k-1]["ancla"])}</span></li>' for k in range(ini, fin + 1))
        partes_html.append(f'<div class="parte"><span class="lbl">{e(nombre)}</span><ol>{items}</ol></div>')
    indice = '<div class="orden"><span class="lbl titulo">El orden de los temas</span>' + "".join(partes_html) + '</div>'
    import json as _json
    tarjetas = []
    for ks, q, r, sencillo, calc in BANCO:
        sencillo, *calc = con_uaesp([sencillo] + list(calc))
        r = con_uaesp([r])[0]
        li = "".join(f"<li>{e(x)}</li>" for x in calc)
        etiquetas = "".join(f'<button type="button" data-k="{e(k)}">{e(k)}</button>' for k in ks if k != PROFE)
        tarjetas.append(f'<article class="q" data-k="|{e("|".join(ks))}|"><p class="q-p">{e(q)}</p><p class="q-r">{e(r)}</p>'
                        f'<p class="q-s"><b>En sencillo:</b> {e(sencillo)}</p>'
                        f'<div class="q-c"><b>Cómo se calculó o de dónde sale:</b><ul>{li}</ul></div>'
                        f'<p class="q-tags">{etiquetas}</p></article>')
    def cuantas(k): return sum(1 for ks, *_ in BANCO if k in ks)
    filtros = [f'<div class="f-top"><button type="button" class="activo" data-k="{e(PROFE)}">{e(PROFE)} <span>{cuantas(PROFE)}</span></button>'
               f'<button type="button" data-k="*">Todas <span>{len(BANCO)}</span></button></div>']
    for g in sorted(GRUPOS, key=orden):
        chips = "".join(f'<button type="button" data-k="{e(k)}">{e(k)} <span>{cuantas(k)}</span></button>' for k in sorted(GRUPOS[g], key=orden))
        filtros.append(f'<div class="f-grupo"><span class="f-g">{e(g)}</span><div class="f-chips">{chips}</div></div>')
    js_final = JS
    fuentes = "".join(f"<li>{f}</li>" for f in FUENTES)

    if modo_suelto:
        css_marca = (pathlib.Path(web) / "assets/css/marca.css").read_text(encoding="utf-8")
        css_marca = re.sub(r"@font-face\s*\{[^}]*\}", "", css_marca)
        logo = "data:image/svg+xml;base64," + base64.b64encode((pathlib.Path(web) / "assets/img/logo.svg").read_bytes()).decode()
        cabeza_css = f"<style>{css_marca}</style>"
        volver = ""
        icono = ""
    else:
        logo = "../assets/img/logo.svg"
        cabeza_css = ('<link rel="preload" href="../assets/fonts/Lexend.woff2" as="font" type="font/woff2" crossorigin>\n'
                      '<link rel="stylesheet" href="../assets/css/marca.css">')
        volver = ('<a class="volver" href="../" aria-label="Volver al menú principal"><svg viewBox="0 0 24 24" aria-hidden="true">'
                  '<path d="M15 5l-7 7 7 7"/></svg>Menú</a>')
        icono = '<link rel="icon" href="../assets/img/icono-192.png">'

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>RECOEVO · Pitch del póster</title>
<meta name="description" content="Guion del pitch de RECOEVO para el E-Fest 2026-2, con teleprompter y preguntas del jurado por temas.">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#154734">
{icono}
{cabeza_css}
<style>{CSS}</style>
</head>
<body data-total="{round(sin_opc)}">
{volver}
<header class="barra"><img src="{logo}" alt="recoevo" width="832" height="273"></header>
<main class="pitch">
  <p class="kicker">E-Fest 2026-2 · Pitch del póster</p>
  <h1>El pitch de RECOEVO</h1>
  <p class="bajada">El guion completo para una persona, conversado y en el orden del póster. También: un teleprompter y las preguntas del jurado, ordenadas por temas.</p>
  <ul class="datos"><li class="dest">≈ {mmss(sin_opc)} a ritmo de conversación</li><li>{mmss(total)} con las frases ✂</li><li>{len(GUION)} bloques</li><li>1 presentador</li></ul>

  <nav class="modos" aria-label="Secciones">
    <a href="#guion">Guion</a>
    <button type="button" class="tele" data-tele>Teleprompter</button>
    <a href="#preguntas">Preguntas</a>
  </nav>

  <section id="guion">
    <h2 class="sec">El guion</h2>
    {indice}
    <p class="leyenda"><span><b class="num">33.300</b> cifra impresa en el póster</span><span><strong style="background:linear-gradient(transparent 60%,var(--hl) 60%)">palabra clave</strong></span><span><span class="gesto">qué señalar</span></span><span><span class="opc">se puede quitar si va largo</span></span></p>
    {"".join(bloques)}
    <p class="total">Duración estimada a ritmo de conversación (unas 2,8 palabras por segundo): <b>{mmss(sin_opc)}</b> sin las frases marcadas con ✂ y <b>{mmss(total)}</b> con todas. El equipo decidió pasar de 5 minutos para que quepa todo; si el jurado corta en 5:00, lo primero que se quita son las frases ✂. El teleprompter muestra la versión sin ✂.</p>
  </section>

  <section id="preguntas">
    <h2 class="sec">Preguntas del jurado</h2>
    <p class="sec-sub">Toque un tema y aparecen todas sus preguntas, cada una con la respuesta, la explicación en sencillo y cómo se calculó. El número es cuántas preguntas tiene ese tema.</p>
    <div class="filtros" id="filtros">{"".join(filtros)}</div>
    <p class="q-estado" id="q-estado" aria-live="polite"></p>
    <div class="q-lista" id="q-lista">{"".join(tarjetas)}</div>
  </section>

  <section id="fuentes">
    <details class="fuentes"><summary>De dónde sale cada cifra</summary><ol>{fuentes}</ol>
    <p>Cifras del pitch que no están en el póster: los hogares de Bogotá y el «uno de cada cuatro», el medio kilo por hogar, el 1,6 % de Doña Juana, el promedio de $275.630, el desglose de la inversión, el costo por producto, los costos fijos y variables, el mes 17 y las rentabilidades. Todas se explican en las preguntas de arriba.</p></details>
  </section>
</main>
<footer class="pie"><p><b>Menos relleno, más vida.</b></p><p>Ricardo Beltrán · William Fonseca · Samuel Medina · Faber Ortiz · Camila Riaño</p><p>Docente: Ingrid Zoraida Sandoval Pérez · Proceso Administrativo · Politécnico Grancolombiano</p></footer>

<div class="tele-capa" id="tele" hidden role="dialog" aria-label="Teleprompter">
  <div class="tele-texto" id="tele-texto"><div class="in"></div></div>
  <div class="tele-guia" aria-hidden="true"></div>
  <div class="tele-saltos" role="group" aria-label="Moverse por el texto">
    <button type="button" id="tele-atras" aria-label="Volver dos líneas"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 15l6-6 6 6"/></svg><span>2 líneas</span></button>
    <button type="button" id="tele-adelante" aria-label="Avanzar dos líneas"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg><span>2 líneas</span></button>
  </div>
  <div class="tele-ctl">
    <button type="button" class="play" id="tele-play">Iniciar</button>
    <output id="tele-reloj">0:00</output>
    <button type="button" id="tele-menos" aria-label="Más lento">−</button><small>velocidad <span id="tele-vel">1.0×</span></small><button type="button" id="tele-mas" aria-label="Más rápido">+</button>
    <button type="button" id="tele-amenos" aria-label="Letra más pequeña">A−</button><button type="button" id="tele-amas" aria-label="Letra más grande">A+</button>
    <button type="button" id="tele-reini">Reiniciar</button>
    <button type="button" id="tele-cerrar">Cerrar</button>
    <small class="tele-ayuda">Toque y arrastre el texto con el dedo para moverlo; la línea tocada queda marcada.</small>
  </div>
</div>
<script>{js_final}</script>
</body>
</html>
"""

if __name__ == "__main__":
    web = pathlib.Path(sys.argv[1])
    filas, total, sin_opc = medir()
    if "--medir" in sys.argv:
        for i, (b, f) in enumerate(zip(GUION, filas), 1):
            print(f"{i:2d} {b['t']:<26} {mmss(f['ini'])}-{mmss(f['fin'])}  {f['pal']:4d} palabras  (quitables {f['opc']})")
        print(f"TOTAL {mmss(total)} | sin quitables {mmss(sin_opc)} | a 2,4 pal/s {mmss(total * RITMO / 2.4)}")
        sys.exit()
    if "--suelto" in sys.argv:
        destino = pathlib.Path(sys.argv[sys.argv.index("--suelto") + 1])
        destino.write_text(pagina(True, web), encoding="utf-8"); print("suelto:", destino)
    else:
        (web / "pitch").mkdir(exist_ok=True)
        (web / "pitch/index.html").write_text(pagina(False, web), encoding="utf-8"); print("web:", web / "pitch/index.html")
    print(f"duración {mmss(total)} (sin quitables {mmss(sin_opc)})")
