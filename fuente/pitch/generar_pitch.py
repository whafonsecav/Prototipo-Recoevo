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

RITMO = 2.6          # palabras habladas por segundo: ritmo tranquilo de presentación
PAUSA_INICIO = 2     # segundos de silencio antes de empezar
RESPIRO = 0.5        # segundos entre bloques (un solo presentador: sin relevos)

# ------------------------------------------------------------------ EL GUION (un presentador)
GUION = [
  dict(t="El gancho", ancla="Bolsa", poster="Póster 01 · cifras rosadas «En la ciudad»",
       pregunta="¿Con qué pregunta abre y qué cifras muestran el tamaño del problema?",
       pistas=["bolsa rota en la calle", "líquido y olor", "es comida", "2024: 33.300 t al día", "1 de cada 5", "60 % comida", "Doña Juana 6.800 t", "licencia hasta 2029"],
       p=["{Pausa. Mire al jurado antes de hablar.} ¿Quién de ustedes no ha visto una **bolsa de basura rota** en la calle? Desgarrada, con un líquido oscuro en el andén… y ese olor.",
          "Lo que se riega casi nunca es plástico. **Es comida.**",
          "{Señale las cifras rosadas.} En 2024, Colombia enterró [[33.300 toneladas]] de basura al día y solo aprovechó [[1 de cada 5]]; cerca del [[60 %]] es comida. Y hoy a **Doña Juana** llegan [[6.800]] toneladas diarias, con licencia solo hasta [[2029]]."]),
  dict(t="Nos toca de cerca", ancla="Barrio", poster="Póster 01 · fotos del campo y «8 de 8»",
       pregunta="¿Dónde nació la idea? ¿Qué vieron y qué les contaron los vecinos?",
       pistas=["no nos es ajeno", "compañero de Villa Rosita, Usme", "septiembre: 8 vecinos", "los 8: el shut", "perrito e icopor", "6 de 8: perros, ratas, plagas", "5 de 8 mezclan", "«todo es un revoltijo»", "falta conciencia y una forma fácil"],
       p=["Este problema no nos es ajeno. {Señale a su compañero.} Nuestro compañero vive en **Villa Rosita, en Usme**, y esta idea nació en su cuadra.",
          "En septiembre escuchamos a [[8]] vecinos. **Los 8 señalaron el shut**: desbordado~, pese al aviso de multa~. Vimos un **perrito** comiendo de un icopor tirado. [[6 de 8]] hablaron de **perros, ratas o plagas**, y [[5 de 8]] **mezclan todo**: «Las cáscaras de la papa, el cartón, las cáscaras de huevo… **todo es un revoltijo**».",
          "Falta conciencia, sí, pero nadie rechazó la idea: **falta una forma fácil**."]),
  dict(t="La ironía", ancla="Ironía", poster="Póster 01 · «En el campo»",
       pregunta="¿Cuál es la ironía? ¿Qué podría hacer el campo con esos restos y qué hacemos nosotros?",
       pistas=["a pocos kilómetros", "campesinos de la Sabana", "esos restos sirven de abono", "los mezclamos con todo", "terminan enterrados en el relleno", "94 % del fertilizante importado", "urea (abono químico): de 80.000 a 230.000 entre enero de 2021 y enero de 2022, +187 %", "la ciudad entierra la comida que el campo necesita"],
       p=["Y lo más **irónico** es esto: a pocos kilómetros de ese shut, los **campesinos de la Sabana** podrían usar esos restos como **abono**. Pero los mezclamos con todo y terminan **enterrados en el relleno**.",
          "{Señale «En el campo».} Y el campo la necesita: más del [[94 %]] del fertilizante del país es **importado**. Entre enero de 2021 y enero de 2022, el bulto de **urea** (el abono químico más usado en los cultivos) pasó de [[80.000 a 230.000 pesos]] (subió [[187 %]]). ~**La ciudad entierra la comida que el campo necesita.**~"]),
  dict(t="La ley ya lo exige", ancla="Ley", poster="Póster 01 · recuadro azul del decreto",
       pregunta="¿Qué obliga el Decreto 0772 de 2026 y qué falta?",
       pistas=["desde julio", "Decreto 0772 de 2026", "separar los orgánicos", "ruta cada semana", "falta una forma limpia en la cocina", "nació RECOEVO"],
       p=["{Señale el recuadro azul.} Y desde julio, el **Decreto 0772 de 2026** obliga a cada hogar a **separar los orgánicos**~ y crea una ruta que los recoge cada semana~. **La ley ya existe; falta una forma limpia de cumplirla en la cocina.** De ahí **nació RECOEVO**."]),
  dict(t="Qué es y cómo funciona", ancla="Pedal", poster="Póster 02 y 03 · prototipo y «Así funciona»",
       pregunta="¿Qué es RECOEVO y cómo se usa, paso a paso?",
       pistas=["triturador de cocina a pedal", "sin luz y sin olor", "echa", "pisa 20 segundos al día", "13 cuchillas", "bolsa compostable", "filtro de carbón", "bolsa cerrada cada semana"],
       p=["{Señale el prototipo.} RECOEVO es un **triturador de cocina a pedal**, sin electricidad y sin olor. Usted **echa** las cáscaras y **pisa** [[20 segundos]] al día: [[13 cuchillas]] las cortan y caen a una **bolsa compostable**. Un **filtro de carbón** atrapa el olor, y [[cada semana]] sale una **bolsa cerrada** para la ruta."]),
  dict(t="Por qué RECOEVO", ancla="Precio", poster="Póster 03 · precios frente al mercado y Value Proposition Canvas",
       pregunta="¿Por qué RECOEVO y no otra marca? ¿Qué dolor resuelve cada parte?",
       pistas=["caneca 119.900: solo guarda", "eléctrico: más de un millón", "RECOEVO 199.900", "huele → filtro", "perros → bolsa cerrada", "difícil → 20 segundos"],
       p=["{Señale la barra de precios.} ~¿Y frente a las demás marcas?~ Una caneca con pedal cuesta [[119.900]] y solo guarda; un procesador eléctrico, más de [[un millón]]. RECOEVO cuesta [[199.900]]: **lo de una buena caneca, pero tritura y no huele.**",
          "{Señale el Value Proposition Canvas.} Y cada dolor que oímos tiene respuesta. ¿Huele? **Filtro.** ¿Perros? **Bolsa cerrada.** ¿Difícil? **Veinte segundos.**"]),
  dict(t="Lo que esperamos lograr", ancla="Usme", poster="Póster 03 · recuadro verde de 406.983 t",
       pregunta="¿Por qué empezar en Usme? ¿Cuántos hogares de cuántos y cuántas toneladas salen del relleno?",
       pistas=["validamos allá", "Doña Juana en el camino", "85 % campo, 17.000 campesinos", "135.000 hogares", "meta 7.300 (5,4 %)", "168 kilos por hogar al año", "1.200 t menos al año", "10 años: 407.000 t = 2 meses de Doña Juana"],
       p=["Empezamos por **Usme**: allá **validamos**, **Doña Juana queda en el camino**, y el [[85 %]] de Usme es **campo**, con [[17.000 campesinos]]. ~Los dos problemas viven juntos.~",
          "Usme tiene unos [[135.000 hogares]]; la meta: [[7.300]], el [[5,4 %]]. Cada hogar bota [[168 kilos]] de comida al año: [[1.200 toneladas]] menos para Doña Juana. {Señale el recuadro verde.} Y en 10 años, en el país, unas [[407.000 toneladas]]: **lo que recibe Doña Juana en dos meses**."]),
  dict(t="Hoy y con RECOEVO", ancla="Recorrido", poster="Póster 04 · Customer Journey Map",
       pregunta="¿Qué recorrido hace hoy una cáscara y cuál hace con RECOEVO?",
       pistas=["hoy: bolsa mezclada → perros → Doña Juana", "con RECOEVO: tapa → pedal → bolsa cerrada → ruta de orgánicos"],
       p=["{Señale el bloque 04.} Hoy la cáscara va a una bolsa mezclada, la rompen los perros y acaba en **Doña Juana**. Con RECOEVO: **tapa, pedal, bolsa cerrada y ruta de orgánicos**."]),
  dict(t="Cómo gana dinero", ancla="Negocio", poster="Póster 05 · fuentes de ingreso, canales, clientes y ODS",
       pregunta="¿Cómo gana dinero, a quién le vende, por dónde, y qué ODS ataca?",
       pistas=["solo vende el producto", "hogares: internet y almacenes", "lotes a empresas, conjuntos y alcaldías", "ODS 12, 11 y 13", "comida enterrada es metano"],
       p=["{Señale el bloque 05.} Ganamos **vendiendo el producto**, sin recargas: a **hogares**, en internet y en almacenes; y **por lotes** a empresas, conjuntos y alcaldías. Y atacamos tres **ODS**: [[12]], consumo responsable; [[11]], ciudades sostenibles; y [[13]], clima, porque **comida enterrada es metano**."]),
  dict(t="Los números", ancla="Números", poster="Póster 06 · franja amarilla y seis recuadros",
       pregunta="¿Cuánto se invierte, cuál es el equilibrio y cuándo se logra, cuándo se recupera y cuánto se gana?",
       pistas=["inversión 5.954 millones", "de 100 pesos, 49 pagan fijos", "fijos ÷ margen = 2.380 al mes", "mes 17", "recuperamos en el mes 50", "utilidad neta 30.508 millones", "retorno 512 %", "20 de cada 100 vendidos", "29 por cada 100 gastados"],
       p=["{Señale el bloque 06.} Los **números**, escenario realista a 10 años. **Inversión inicial:** [[5.954 millones]], en fábrica, arranque y respaldo de caja.",
          "De cada [[100]] pesos que recibimos, [[49]] pagan los costos fijos: es el **margen de contribución**. Costos fijos entre ese margen da el **punto de equilibrio**: [[2.380]] productos al mes, que superamos en el mes [[17]].",
          "**Recuperamos la inversión** en el mes [[50]]. **Utilidad neta**: [[30.508 millones]], un **retorno** de [[512 %]]. De cada 100 pesos vendidos quedan [[20]] de utilidad, y por cada 100 gastados ganamos [[29]]."]),
  dict(t="El cierre", ancla="Mentoría", poster="Pie del póster",
       pregunta="¿Qué sienten por esta idea y qué le piden al jurado?",
       pistas=["nos ilusiona", "nació en la cuadra de un compañero", "esa bolsa la hemos visto todos", "mercadeo e ingeniería de sistemas", "nos falta la mirada de quien ha creado empresa", "una conversación, una mentoría", "Menos relleno, más vida"],
       p=["Esta idea **nos ilusiona**: nació en la cuadra de un compañero, pero esa bolsa rota la hemos visto todos.",
          "Somos de **mercadeo e ingeniería de sistemas**, y nos falta la mirada de quien ya ha **creado empresa**. Por eso, quede o no seleccionada, les pedimos **una conversación, una mentoría**, para mejorarla con su experiencia.",
          "Porque esa bolsa de la esquina **no tiene por qué seguir ahí**. **Menos relleno, más vida.** Gracias."]),
]

FRASE_CADENA = ("Una <b>bolsa</b> rota en el <b>barrio</b>; la <b>ironía</b> y la <b>ley</b>; un <b>pedal</b> a buen <b>precio</b>; "
                "<b>Usme</b> cambia su <b>recorrido</b>; el <b>negocio</b> da <b>números</b>; y pedimos <b>mentoría</b>.")

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
PROFE = [
  ("¿Cuál es la inversión inicial?", "$5.954 millones",
   "Todo el dinero para empezar antes de vender el primer producto. Lo ponen los socios ($4.880 M) y un crédito del banco ($1.074 M).",
   ["Máquinas, moldes, planta y oficina: <b>$3.147 M</b> (97 máquinas $1.672 M; 13 moldes y troqueles $1.013 M; bodega, computadores y muebles $462 M).",
    "Gastos de arranque: <b>$484 M</b> (trámites, marca y patente, desarrollo del producto, puesta en marcha, lanzamiento, sueldos de montaje y 10 % de imprevistos).",
    "Dinero de respaldo, que se recupera: <b>$2.323 M</b> (capital de trabajo $1.171 M; IVA de las máquinas $598 M; colchón de caja $500 M; depósito del arriendo $54 M).",
    "3.147 + 484 + 2.323 = <b>$5.954 M</b>. Crédito al 19,5 % efectivo anual, a 5 años."]),
  ("¿Cuál es el precio de venta y cómo llegaron a él?", "$199.900 con IVA",
   "Al público. Por lotes a empresas, conjuntos y alcaldías: $142.000 + IVA. Se fijó entre un techo (lo que la gente paga por una buena caneca) y un piso (lo que cuesta hacer, vender y financiar cada producto).",
   ["<b>Techo, el mercado:</b> menos de $200.000. Caneca con pedal $119.900 (solo guarda); eléctricos FoodCycler $1.265.000 y Lomi $1.737.000.",
    "<b>Piso, el costo:</b> cada producto cuesta <b>$144.319</b> con todo incluido (promedio de 10 años).",
    "<b>Lo que llega a la empresa:</b> $167.983 sin IVA hoy; descontando lo que cobran tiendas y cadenas, y con el precio subiendo con la inflación cada año, recibe en promedio <b>$205.185</b> por producto. Deja $60.866 antes de impuestos."]),
  ("¿Cuál es el punto de equilibrio?", "2.380 productos al mes",
   "28.554 al año. Es lo mínimo que hay que vender para no perder dinero: costos fijos ÷ margen de contribución.",
   ["Lo que recibe la empresa por producto: <b>$205.185</b>.",
    "Costo variable (materiales, operarios, energía, comisiones, anuncios, distribución, garantía e ICA): <b>$104.611</b>.",
    "Margen de contribución: 205.185 − 104.611 = <b>$100.574</b> (49 %).",
    "Costos fijos al año, promedio de 10 años: <b>$2.872 M</b>.",
    "2.872 M ÷ 100.574 = 28.554 al año ÷ 12 = <b>2.380 al mes</b>."]),
  ("¿Cuándo alcanzan el punto de equilibrio?", "Mes 17",
   "Ese mes se venden 2.500 productos, por primera vez más que los 2.380 necesarios.",
   ["Las ventas empiezan en 800 al mes, cierran el año 1 en 2.000 al mes y llegan a 9.500 al mes en el año 10.",
    "El primer mes que pasa de 2.380 es el 17.",
    "En años: el año 1 pierde $864 M; desde el año 2 hay utilidad ($136 M)."]),
  ("¿Cuándo se recupera la inversión?", "Mes 50",
   "4 años y 2 meses.",
   ["Se suma mes a mes el dinero libre que deja el negocio: lo que entra menos todo lo que sale (también compras de máquinas, inventario y facturas por cobrar).",
    "Al terminar el mes 1 la suma va en −$4.547 M por el montaje; el primer mes en que deja de ser negativa es el <b>50</b>."]),
  ("¿Cuál es el retorno de la inversión (ROI)?", "512 %",
   "En 10 años, por cada $100 invertidos se ganan $512: 5,1 veces lo invertido.",
   ["Utilidad neta de 10 años $30.508 M ÷ inversión inicial $5.954 M = <b>5,12</b>."]),
  ("¿Cuál es la rentabilidad?", "19,9 % sobre ventas · 28,7 % sobre costos",
   "De cada $100 que se venden quedan $20 de utilidad neta; por cada $100 que se gastan se ganan $29. Ya pagado el impuesto de renta.",
   ["Ventas 10 años $153.075 M − gasto completo $106.139 M = utilidad antes de impuestos <b>$46.936 M</b>.",
    "Impuesto de renta 35 %: $16.428 M → utilidad neta <b>$30.508 M</b>.",
    "Sobre ventas: 30.508 ÷ 153.075 = <b>19,9 %</b>. Sobre costos: 30.508 ÷ 106.139 = <b>28,7 %</b>.",
    "Antes de impuestos: 30,7 % sobre ventas y 44,2 % sobre costos."]),
  ("¿Cuál es el porcentaje de utilidad?", "19,9 %",
   "La utilidad neta es el 19,9 % de las ventas. El margen de contribución (lo que deja cada producto para pagar los costos fijos) es 49 %.",
   ["Utilidad neta ÷ ventas = 30.508 ÷ 153.075 = <b>19,9 %</b>.",
    "Margen de contribución ÷ precio recibido = 100.574 ÷ 205.185 = <b>49 %</b>."]),
  ("¿Cuánto es la utilidad del negocio?", "$30.508 millones",
   "Utilidad neta en 10 años: unos $41.500 por producto. El año 1 pierde, desde el año 2 gana y el año 10 deja $6.489 M.",
   ["Ventas − gasto completo − impuesto de renta.",
    "Año 0 (montaje) −$486 M · año 1 −$864 M · año 2 +$136 M · año 3 +$1.454 M · año 5 +$2.836 M · año 10 +$6.489 M."]),
  ("¿Cuánto cuesta hacer un producto?", "$144.319",
   "Con todo incluido, promedio de 10 años: materiales $58.081; producción completa $74.205; administración, nómina y ventas $63.868.",
   ["Producción $74.205 = materiales $58.081 + energía $4.637 + planta $11.487.",
    "Administración $63.868 = nómina de todos $29.310 + legales $1.149 + oficina e impuestos $3.269 + publicidad, comisiones, distribución y garantía $30.141.",
    "Más máquinas que se gastan $4.825, arranque $658 e intereses $762. Total <b>$144.319</b> (gasto de 10 años $106.139 M ÷ 735.450 productos)."]),
  ("¿Qué es la TIR de 33,9 %?", "33,9 % al año",
   "Lo que rinde al año el dinero invertido en el proyecto, como el interés de un CDT, pero de este negocio.",
   ["Es la tasa con la que el valor de hoy de todo lo que entra y sale en 10 años da cero (plan financiero detallado, escenario realista)."]),
]

OTRAS = [
  ("¿Por qué Usme y no otra localidad?",
   "Allá validamos el problema con los vecinos; Doña Juana queda en el camino a Usme (se entra por la vía al Llano); y el 85 % de Usme es campo, con unos 17.000 campesinos, la localidad con más campesinos de Bogotá. La basura de la ciudad y el abono del campo están en el mismo lugar."),
  ("¿De dónde salen los 7.300 hogares y las 1.200 toneladas?",
   "415.000 habitantes (Observatorio de Salud de Bogotá, 2024) ÷ 3,07 personas por hogar (DANE, Encuesta Multipropósito 2021) ≈ 135.000 hogares. Con la misma meta realista del plan (5,4 % = 735.450 ÷ 13,6 millones de hogares urbanos): ≈ 7.300 hogares. 7.300 × 0,46 kg al día × 365 ≈ 1.225 toneladas al año. El año 1 el plan vende 16.200 productos en Bogotá y alrededores, empezando por Usme."),
  ("¿De dónde salen las 406.983 toneladas?",
   "735.450 hogares en 10 años; cada uno saca 0,46 kg de restos al día; se suman los días en que cada producto está en uso. 406.983 t ÷ 6.800 t diarias de Doña Juana ≈ 60 días: dos meses."),
  ("¿RECOEVO produce abono?",
   "No. Tritura y guarda sin olor los restos en una bolsa compostable lista para la ruta de orgánicos o para compostar. Convertir las bolsas en abono para el campo es la fase 2, fuera de estas cifras."),
  ("¿Hay que comprarles bolsas, aserrín o recargas?",
   "No. Sirve cualquier bolsa compostable; el material seco (papel, hojas secas o aserrín) es opcional. No se venden recargas ni suscripciones."),
  ("¿Es seguro con niños?",
   "Sí: con la tapa abierta el pedal se bloquea, y una perilla de reversa destraba el eje si algo se atasca."),
  ("¿Quién es la competencia?",
   "Las canecas con pedal, que solo guardan, y los procesadores eléctricos como FoodCycler y Lomi, de más de un millón y que gastan luz. No encontramos a la venta otro triturador de cocina a pedal; solo prototipos caseros."),
  ("¿Qué sigue ahora?",
   "Una preserie para preventas y cartas de intención de grandes superficies: probar la demanda antes de crecer (Lean Startup)."),
  ("¿Qué tan confiable es el trabajo de campo?",
   "Es un estudio cualitativo para validar el problema: 8 entrevistas, 220 frases analizadas con doble codificación y 96,9 % de acuerdo. Las cifras hablan de esas 8 personas, no de todo el barrio."),
]

FUENTES = [
  "Póster RECOEVO E-Fest 2026-2 y sus 10 fuentes (Superservicios 2024; Secretaría del Hábitat; UAESP; El Tiempo, 16-oct-2026; Semana; El Colombiano; DANE-SIPSA; Agronegocios; Homecenter, Best Buy, lomi.com; estudio de campo en Villa Rosita, 19-sep-2026).",
  "RECOEVO, presupuesto ejecutivo y plan financiero a 10 años, escenario realista (3-nov-2026): tablas 4, 9, 10, 11, 13 y 14.",
  'Decreto 0772 de 2026, Ministerio de Vivienda: <a href="https://normas.cra.gov.co/gestor/docs/decreto_0772_2026.htm">normas.cra.gov.co</a>.',
  'Usme, 414.995 habitantes: Observatorio de Salud de Bogotá, «Usme +Bienestar 2024» (<a href="https://saludata.saludcapital.gov.co/osb/wp-content/uploads/2024/12/Usme_MasBienestar_2024_v1_2.pdf">saludata</a>).',
  'Usme, 3,07 personas por hogar: DANE, Encuesta Multipropósito 2021 (<a href="https://www.dane.gov.co/files/investigaciones/multi/Presentacion_EM_2021.pdf">dane.gov.co</a>).',
  'Usme, 85,9 % rural (18.477 de 21.507 ha): Universidad Santo Tomás (<a href="https://repository.usta.edu.co/items/18786bd5-dfd9-489f-a768-c6a314d7cc83">repositorio</a>). Unos 17.000 campesinos: Alcaldía de Bogotá (<a href="https://bogota.gov.co/mi-ciudad/desarrollo-economico/el-distrito-celebra-el-dia-del-campesino">bogota.gov.co</a>).',
  'Acceso a Doña Juana por la vía al Llano, antes de Usme: Blu Radio (<a href="https://www.bluradio.com/medio-ambiente/dona-juana-entienda-que-paso-y-como-funciona-el-relleno-sanitario-de-bogota">bluradio.com</a>).',
  "Método para memorizar: práctica de recuperación (Roediger y Karpicke, 2006); efecto de producción, decir en voz alta (MacLeod y otros, 2010); práctica espaciada (Cepeda y otros, 2006); pistas que desaparecen (Glisky, Schacter y Tulving, 1986); método de los lugares (Dresler y otros, 2017).",
]

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
@media (max-width:700px){.modos{position:fixed;top:auto;bottom:0;left:0;right:0;margin:0;padding:6px max(6px,env(safe-area-inset-right)) calc(6px + env(safe-area-inset-bottom)) max(6px,env(safe-area-inset-left));border-top:1px solid var(--linea);border-bottom:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:4px;box-shadow:0 -6px 18px rgba(21,71,52,.08)}.modos a,.modos button{padding:9px 2px;font-size:12.5px;text-align:center;border-radius:12px;min-width:0;overflow:hidden;text-overflow:ellipsis}body{padding-bottom:76px}}
.modos a,.modos button{flex:none;font:inherit;font-family:"Lexend",system-ui,sans-serif;font-weight:600;font-size:15px;text-decoration:none;color:var(--monte);background:var(--papel);border:1px solid var(--linea);border-radius:999px;padding:9px 15px;cursor:pointer;white-space:nowrap}
.modos .tele{background:var(--monte);color:#fff;border-color:var(--monte)}
section{scroll-margin-top:80px}
@media (max-width:700px){section{scroll-margin-top:70px}}
h2.sec{font-size:clamp(24px,5.6vw,32px);margin:34px 0 4px}
.sec-sub{color:var(--suave);margin:0 0 14px;max-width:42em}
.orden{background:var(--papel);border:1px solid var(--linea);border-radius:18px;padding:14px 16px;margin:6px 0 4px}
.orden p{margin:0;font-size:16.5px}
.orden .lbl{font-family:"Lexend";font-weight:700;font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:var(--evo);display:block;margin-bottom:4px}
.orden b{color:var(--monte);background:linear-gradient(transparent 60%,var(--hl) 60%)}
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
.tele-ctl{flex:none;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:8px;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:#14231b;border-top:1px solid rgba(255,255,255,.12)}
.tele-ctl button{font:inherit;font-family:"Lexend";font-weight:600;font-size:15px;border-radius:999px;border:1px solid rgba(255,255,255,.25);background:transparent;color:#fff;padding:9px 14px;cursor:pointer;min-width:44px}
.tele-ctl .play{background:var(--sol);color:var(--monte);border-color:var(--sol);min-width:110px}
.tele-ctl output{font-family:"Lexend";font-weight:700;font-size:20px;min-width:56px;text-align:center;font-variant-numeric:tabular-nums}
.tele-ctl small{color:#b9c2b8;font-size:13px}
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

  /* ---------- práctica guiada ---------- */
  var CL="recoevo-pitch-practica";
  var est={i:0,modo:"bloque",marca:{}};
  try{var g=JSON.parse(localStorage.getItem(CL)||"null");if(g){est.i=Math.min(g.i||0,DATOS.length-1);est.modo=g.modo||"bloque";est.marca=g.marca||{};}}catch(e){}
  function guardar(){try{localStorage.setItem(CL,JSON.stringify(est));}catch(e){}}
  var nivel=0;
  var $=function(id){return document.getElementById(id);};
  function pintar(){
    var d=DATOS[est.i], cad=est.modo==="cadena";
    $("tp-paso").textContent="Bloque "+d.n+" de "+DATOS.length+" · "+d.t;
    $("tp-prog").style.width=((est.i+1)/DATOS.length*100)+"%";
    if(cad){
      $("tp-preg").textContent=d.n===1?"Diga el bloque 1 completo, en voz alta.":"Ahora diga seguido del bloque 1 al "+d.n+".";
      $("tp-inst").textContent="Sin mirar. Si se traba, abra las pistas: son las anclas de cada bloque, en orden.";
    } else {
      $("tp-preg").textContent=d.preg;
      $("tp-inst").textContent="Respóndala en voz alta, como si estuviera frente al jurado. Si se traba, abra las pistas; al final, compare con el guion.";
    }
    var pistas = cad ? DATOS.slice(0,est.i+1).map(function(x){return x.n+". "+x.ancla;}) : d.pistas;
    $("tp-pistas").innerHTML=pistas.map(function(p){return "<li>"+esc(p)+"</li>";}).join("");
    $("tp-pistas").hidden=nivel<1;
    var guion = cad ? DATOS.slice(0,est.i+1).map(function(x){return x.html;}).join("") : d.html;
    $("tp-guion").innerHTML=guion; $("tp-guion").hidden=nivel<2;
    $("b-pistas").hidden=nivel>=1; $("b-guion").hidden=nivel>=2;
    $("b-ant").disabled=est.i===0; $("b-sig").textContent=est.i===DATOS.length-1?"Volver al bloque 1":"Siguiente bloque →";
    [].forEach.call(document.querySelectorAll(".tp-modo button"),function(b){b.setAttribute("aria-pressed",String(b.dataset.modo===est.modo));});
    $("marcas").innerHTML=DATOS.map(function(x,k){var m=est.marca[k]||"";return '<button type="button" class="'+m+(k===est.i?" act":"")+'" data-k="'+k+'" aria-label="Bloque '+x.n+(m==="ok"?", lo dijo bien":m==="rep"?", para repasar":"")+'">'+x.n+'</button>';}).join("");
  }
  function ir(k){est.i=(k+DATOS.length)%DATOS.length;nivel=0;guardar();pintar();}
  if($("tp-preg")){
    $("b-pistas").onclick=function(){nivel=1;pintar();};
    $("b-guion").onclick=function(){nivel=2;pintar();};
    $("b-ok").onclick=function(){est.marca[est.i]="ok";ir(est.i+1);};
    $("b-rep").onclick=function(){est.marca[est.i]="rep";ir(est.i+1);};
    $("b-ant").onclick=function(){ir(est.i-1);};
    $("b-sig").onclick=function(){ir(est.i+1);};
    $("marcas").onclick=function(e){var b=e.target.closest("button");if(b)ir(Number(b.dataset.k));};
    [].forEach.call(document.querySelectorAll(".tp-modo button"),function(b){b.onclick=function(){est.modo=b.dataset.modo;nivel=0;guardar();pintar();};});
    $("b-limpiar").onclick=function(){est.marca={};guardar();pintar();};
    pintar();
  }

  /* ---------- teleprompter ---------- */
  var capa=$("tele"), caja=$("tele-texto"), reloj=$("tele-reloj"), bPlay=$("tele-play"), vel=$("tele-vel");
  var corre=false, mult=1, tam=34, ult=0, seg=0, raf=0, resto=0;
  caja.querySelector(".in").innerHTML=DATOS.map(function(d){return "<h4>"+d.n+" · "+esc(d.t)+"</h4>"+d.html;}).join("");
  function pxSeg(){return (caja.scrollHeight-caja.clientHeight)/TOTAL*mult;}
  function paso(ts){
    if(!corre) return;
    var dt=ult?(ts-ult)/1000:0; ult=ts; seg+=dt;
    resto+=pxSeg()*dt; var entero=Math.floor(resto); if(entero>0){caja.scrollTop+=entero;resto-=entero;}
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
  $("tele-cerrar").onclick=cerrar;
  document.addEventListener("keydown",function(e){
    if(capa.hidden) return;
    if(e.key==="Escape") cerrar();
    else if(e.key===" "){e.preventDefault();corre?parar():arrancar();}
    else if(e.key==="ArrowUp") $("tele-menos").click();
    else if(e.key==="ArrowDown") $("tele-mas").click();
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
    profe = []
    for p, r, d, calc in PROFE:
        li = "".join(f"<li>{c}</li>" for c in calc)
        profe.append(f'<div class="q"><p class="q-p">{e(p)}</p><p class="q-r">{e(r)}</p><p class="q-d">{e(d)}</p>'
                     f'<details><summary>¿Cómo se calculó?</summary><ul>{li}</ul></details></div>')
    otras = "".join(f'<details><summary>{e(p)}</summary><p>{e(r)}</p></details>' for p, r in OTRAS)
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
<title>RECOEVO · Pitch de 5 minutos</title>
<meta name="description" content="Guion del pitch de RECOEVO para el E-Fest 2026-2, con práctica guiada, teleprompter y respuestas para el jurado.">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#154734">
{icono}
{cabeza_css}
<style>{CSS}</style>
</head>
<body data-total="{round(total)}">
{volver}
<header class="barra"><img src="{logo}" alt="recoevo" width="832" height="273"></header>
<main class="pitch">
  <p class="kicker">E-Fest 2026-2 · Pitch del póster</p>
  <h1>El pitch de RECOEVO</h1>
  <p class="bajada">El guion completo para una persona, en el orden del póster. Abajo: cómo aprenderlo rápido, un teleprompter y las respuestas para el jurado.</p>
  <ul class="datos"><li class="dest">≈ {mmss(total)} hablando tranquilo</li><li>11 bloques</li><li>1 presentador</li></ul>

  <nav class="modos" aria-label="Secciones">
    <a href="#guion">Guion</a>
    <a href="#practicar">Practicar</a>
    <button type="button" class="tele" data-tele>Teleprompter</button>
    <a href="#preguntas">Preguntas</a>
  </nav>

  <section id="guion">
    <h2 class="sec">El guion</h2>
    <div class="orden"><span class="lbl">El orden en una frase</span><p>{FRASE_CADENA}</p></div>
    <p class="leyenda"><span><b class="num">33.300</b> cifra impresa en el póster</span><span><strong style="background:linear-gradient(transparent 60%,var(--hl) 60%)">palabra clave</strong></span><span><span class="gesto">qué señalar</span></span><span><span class="opc">se puede quitar si va largo</span></span></p>
    {"".join(bloques)}
    <p class="total">Duración estimada: <b>{mmss(total)}</b> a un ritmo tranquilo; <b>{mmss(sin_opc)}</b> si quita las frases marcadas con ✂. El límite es 5:00.</p>
  </section>

  <section id="practicar">
    <h2 class="sec">Cómo aprenderlo rápido</h2>
    <p class="sec-sub">Funciona con el tiempo que tenga, sea mucho o poco: repita el ciclo cuantas veces pueda. Varias vueltas cortas rinden más que una larga.</p>
    <ol class="metodo">
      <li><span><b>Escúchese una vez.</b> Lea el guion completo en voz alta con el <a href="#" data-tele>teleprompter</a>. Así sabe cómo suena y cuánto dura.</span></li>
      <li><span><b>Apréndase el orden.</b> La frase de arriba tiene las 11 anclas en orden: bolsa, barrio, ironía, ley, pedal, precio, Usme, recorrido, negocio, números, mentoría.</span></li>
      <li><span><b>Primera y última frase, palabra por palabra.</b> Lo demás, por ideas: si se olvida una palabra la cambia por otra, pero el arranque y el cierre tienen que salir solos.</span></li>
      <li><span><b>Practique con preguntas.</b> En la tarjeta de abajo, responda cada pregunta en voz alta. Solo si se traba, abra las pistas; al final, compare con el guion. Marque «Lo dije bien» o «Repasar».</span></li>
      <li><span><b>Encadene.</b> Cambie a «Encadenar»: diga del bloque 1 al 2, luego del 1 al 3… hasta el 11. Vuelva a los bloques amarillos.</span></li>
      <li><span><b>Ensayo final, de pie, frente al póster.</b> Las cifras están impresas: no hay que memorizarlas, solo saber dónde señalar. Cronometre con el teleprompter.</span></li>
    </ol>
    <p class="por-que">Por qué funciona: intentar recordar en voz alta enseña más que releer; decirlo en voz alta se recuerda mejor que leerlo en silencio; y el póster sirve de apuntador, porque cada bloque tiene su lugar.</p>

    <div class="tarjeta-p" aria-live="polite">
      <div class="tp-top"><span class="tp-paso" id="tp-paso">Bloque 1</span>
        <div class="tp-modo" role="group" aria-label="Forma de practicar"><button type="button" data-modo="bloque" aria-pressed="true">Bloque por bloque</button><button type="button" data-modo="cadena" aria-pressed="false">Encadenar</button></div></div>
      <div class="barra-prog"><i id="tp-prog"></i></div>
      <p class="tp-preg" id="tp-preg">Cargando la práctica…</p>
      <p class="tp-inst" id="tp-inst"></p>
      <ul class="tp-pistas" id="tp-pistas" hidden></ul>
      <div class="tp-guion" id="tp-guion" hidden></div>
      <div class="tp-acc">
        <button type="button" class="btn sec" id="b-pistas">Ver pistas</button>
        <button type="button" class="btn sec" id="b-guion">Ver el guion</button>
        <button type="button" class="btn ok" id="b-ok">Lo dije bien ✓</button>
        <button type="button" class="btn rep" id="b-rep">Repasar</button>
      </div>
      <div class="tp-nav"><button type="button" class="btn sec" id="b-ant">← Anterior</button><button type="button" class="btn" id="b-sig">Siguiente bloque →</button></div>
      <div class="marcas" id="marcas" aria-label="Bloques: verde, lo dijo bien; amarillo, para repasar"></div>
      <p class="por-que"><button type="button" class="btn sec" id="b-limpiar" style="padding:6px 12px;font-size:13px">Borrar marcas</button> Las marcas se guardan solo en este celular o computador.</p>
    </div>
  </section>

  <section id="preguntas">
    <h2 class="sec">Preguntas del jurado</h2>
    <p class="sec-sub">Las que pidió la profesora, con la respuesta corta para decir y, si la piden, cómo se calculó. Escenario realista a 10 años, pesos sin IVA salvo el precio al público.</p>
    <div class="profe">{"".join(profe)}</div>
    <h2 class="sec" style="font-size:22px">Otras que pueden salir</h2>
    <div class="otras">{otras}</div>
  </section>

  <section id="fuentes">
    <details class="fuentes"><summary>De dónde sale cada cifra</summary><ol>{fuentes}</ol>
    <p>Cifras del pitch que no están en el póster: las de Usme (135.000 hogares, meta de 7.300, 1.200 t al año, 85 % campo, 17.000 campesinos), los 168 kilos por hogar al año, el mes 17, la rentabilidad de 19,9 % y 28,7 % y «dos meses de Doña Juana». Todas se explican en las preguntas de arriba.</p></details>
  </section>
</main>
<footer class="pie"><p><b>Menos relleno, más vida.</b></p><p>Ricardo Beltrán · William Fonseca · Samuel Medina · Faber Ortiz · Camila Riaño</p><p>Docente: Ingrid Zoraida Sandoval Pérez · Proceso Administrativo · Politécnico Grancolombiano</p></footer>

<div class="tele-capa" id="tele" hidden role="dialog" aria-label="Teleprompter">
  <div class="tele-texto" id="tele-texto"><div class="in"></div></div>
  <div class="tele-guia" aria-hidden="true"></div>
  <div class="tele-ctl">
    <button type="button" class="play" id="tele-play">Iniciar</button>
    <output id="tele-reloj">0:00</output>
    <button type="button" id="tele-menos" aria-label="Más lento">−</button><small>velocidad <span id="tele-vel">1.0×</span></small><button type="button" id="tele-mas" aria-label="Más rápido">+</button>
    <button type="button" id="tele-amenos" aria-label="Letra más pequeña">A−</button><button type="button" id="tele-amas" aria-label="Letra más grande">A+</button>
    <button type="button" id="tele-reini">Reiniciar</button>
    <button type="button" id="tele-cerrar">Cerrar</button>
  </div>
</div>
<script>{JS}</script>
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
