"""Lee la hoja «Realista» del presupuesto ejecutivo y escribe presupuesto/datos.js para la página web.

Uso:  python fuente/presupuesto/extraer_presupuesto.py <RECOEVO_Presupuesto_Ejecutivo.xlsx> [presupuesto/datos.js]

- Usa los valores que Excel dejó calculados (el libro debe estar guardado desde Excel).
- Respeta la agrupación con la que se guardó el libro: lo que está plegado en Excel sale plegado en la web.
- Limpia los textos para la web: quita las referencias de celdas (G34, F5…), escribe «dinero» en vez de «plata»
  y pone los miles con punto en los textos que arma Excel con fórmulas.
"""
import json, os, re, sys
from datetime import datetime
import openpyxl
from openpyxl.utils import get_column_letter

SRC = sys.argv[1]
DST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "..", "presupuesto", "datos.js")
HOJA = "Realista"
ANIOS = list(range(11, 22))            # columnas K..U = años 0..10

wf = openpyxl.load_workbook(SRC)                  # fórmulas y agrupación
wv = openpyxl.load_workbook(SRC, data_only=True)  # valores calculados por Excel
F, V = wf[HOJA], wv[HOJA]
NPROD = None                                      # productos vendidos en 10 años (se lee de la tabla 0)


# ---------------------------------------------------------------- textos
def caso(original, nuevo):
    if original.isupper():
        return nuevo.upper()
    if original[:1].isupper():
        return nuevo[:1].upper() + nuevo[1:]
    return nuevo


DINERO = [(r"\bla plata que deja el negocio, sumada\b", "el dinero que deja el negocio, sumado"),
          (r"\bde la plata\b", "del dinero"), (r"\btoda la plata\b", "todo el dinero"),
          (r"\bla plata prestada\b", "el dinero prestado"), (r"\besa plata\b", "ese dinero"),
          (r"\bla plata\b", "el dinero"), (r"\bplata\b", "dinero")]
REF = r"−?\$?[A-Z]{1,2}\$?\d{1,3}"


def sin_celdas(t):
    """Quita las referencias de celdas de Excel, que en la web no dicen nada."""
    t = re.sub(r"Por producto: " + REF + r" ÷ " + REF + r"\.",
               lambda m: f"Por producto: este total ÷ los {miles(NPROD)} productos vendidos en los 10 años.", t)
    t = re.sub(r"^\((?:" + REF + r"|[\s+])+\)\s*÷", "Suma de las filas de costo variable ÷", t)
    t = re.sub(r"\bG ÷ E\b", "total ÷ cantidad", t)
    t = re.sub(r"\s*\(columnas? [A-Z]( a [A-Z])?\)", "", t)
    t = re.sub(r"\(([^():]+): fila \d+(?:, fila \d+)*\)", r"(\1)", t)   # «(tablas 6 y 7: fila 81, fila 87…)»
    # «(tabla 10: G118 ÷ E118)» → «(tabla 10)»;  «(b ÷ a: E155 ÷ E154)» → «(b ÷ a)»
    t = re.sub(r"\(([^():]+): [^()]*\b[A-Z]{1,2}\d{1,3}\b[^()]*\)", r"(\1)", t)
    # paréntesis que solo tienen celdas, signos y números: se quitan
    t = re.sub(r"\s*\((?:" + REF + r"|[\s+÷×=−\-,.\d]|\ba\b)+\)", "", t)
    t = re.sub(r"\b[A-Z]{1,2}\d{1,3} a [A-Z]{1,2}\d{1,3}\b", "", t)
    t = re.sub(r"\s+([.,;:])", r"\1", t)
    return re.sub(r"\s{2,}", " ", t).strip()


def miles_texto(t):
    """Los textos que arma Excel con FIXED() salen con coma de miles (2,380): en Colombia va punto (2.380)."""
    while re.search(r"(\d),(\d{3})(?!\d)", t):
        t = re.sub(r"(\d),(\d{3})(?!\d)", r"\1.\2", t)
    return t


# Frase equivocada del libro guardado el 3-nov-2026 (fila «Venta de productos»): el promedio de 10 años ($205.185) da MÁS
# que $199.900 por la inflación. Ya está corregida en el generador del Excel; esto la arregla mientras se rearma el libro.
CORRECCIONES = {"Es menor que $199.900 porque se descuenta el IVA (19 %), la parte de la cadena y el descuento por lote.":
                "Es el promedio de los 10 años, sin IVA (19 %) y ya descontada la parte de la cadena y el descuento por lote. "
                "Da más que $199.900 porque ese es el precio de hoy: sube con la inflación cada año y la mayoría de las ventas "
                "llega en los últimos años."}


def texto(r, c):
    v = V.cell(r, c).value
    if not isinstance(v, str) or v.strip() in ("", "—"):
        return None
    for viejo, nuevo in CORRECCIONES.items():
        v = v.replace(viejo, nuevo)
    f = F.cell(r, c).value
    if isinstance(f, str) and f.startswith("="):
        v = miles_texto(v)
    for pat, rep in DINERO:
        v = re.sub(pat, lambda m: caso(m.group(0), rep), v, flags=re.I)
    return sin_celdas(v)


SIGLAS = {"ROI", "IVA", "ICA", "REP", "TIR", "POM", "DIAN"}


def oracion(t):
    """«6. COSTO DE PRODUCCIÓN (fabricar…)» → «Costo de producción (fabricar…)» (los títulos de Excel van en mayúsculas)."""
    t = " ".join(w if re.sub(r"\W", "", w) in SIGLAS else w.lower() for w in t.split(" "))
    i = next(i for i, ch in enumerate(t) if ch.isalpha())
    return t[:i] + t[i].upper() + t[i + 1:]


def miles(n):
    return f"{n:,.0f}".replace(",", ".")


# ---------------------------------------------------------------- números
def tipo(fmt, v):
    if "%" in fmt:
        dec = len(fmt.split(".")[1].split("%")[0]) if "." in fmt else 0
        return f"%{dec}"
    if '"mes "' in fmt:
        return "mes"
    if "$" in fmt:
        return "$s" if "▲" in fmt else "$"
    if "0.0" in fmt:
        return "n1"
    return "n0" if float(v).is_integer() or "#,##0" in fmt else "n1"


def num(r, c):
    """Devuelve [valor, tipo] o None si la celda no es un número."""
    x = V.cell(r, c)
    if isinstance(x.value, bool) or not isinstance(x.value, (int, float)):
        return None
    v = round(x.value, 4)
    return [int(v) if float(v).is_integer() else v, tipo(x.number_format, v)]


def nivel(r):
    return F.row_dimensions[r].outlineLevel or 0


def oculto(r):
    return bool(F.row_dimensions[r].hidden)


def color(r):
    c = V.cell(r, 2)
    rgb = c.fill.fgColor.rgb if c.fill and c.fill.fill_type else None
    return {"FFFFE699": "amarillo", "FFDDEBF7": "azul", "FFF2F2F2": "gris", "FFEEF3FA": "nota"}.get(rgb)


def vacia(r):
    return all(V.cell(r, c).value in (None, "") for c in range(2, 22))


def hasta_vacia(r):
    fin = r
    while fin <= V.max_row and not vacia(fin) and V.cell(fin, 2).value != "Concepto":
        fin += 1
    return fin


def anidar(filas):
    """Convierte la lista plana (con nivel 1 y 2) en árbol y marca qué filas están abiertas en Excel."""
    raiz = []
    for f in filas:
        if f["nivel"] == 2 and raiz:
            raiz[-1].setdefault("hijos", []).append(f)
        else:
            raiz.append(f)
    for f in raiz:
        if f.get("hijos"):
            f["abierto"] = not f["hijos"][0].pop("_oculto")
            for h in f["hijos"][1:]:
                h.pop("_oculto")
        for h in f.get("hijos", []):
            h.pop("_oculto", None)
    return raiz


def fila_suma(r):
    d = dict(id=f"r{r}", nivel=nivel(r), nombre=texto(r, 2), que=texto(r, 3), unidad=texto(r, 4), como=texto(r, 10),
             color=color(r), _oculto=oculto(r))
    for k, c in (("cant", 5), ("precio", 6), ("total", 7), ("prom", 8), ("pp", 9)):
        x = num(r, c)
        if x:
            d[k] = x
    anios = [num(r, c) for c in ANIOS]
    if any(anios):
        d["anios"] = [a[0] if a else None for a in anios]
        d["tanios"] = next(a[1] for a in anios if a)
    return {k: v for k, v in d.items() if v not in (None, "")}


def fila_calc(r):
    d = dict(id=f"r{r}", nivel=nivel(r), nombre=texto(r, 2), que=texto(r, 3), unidad=texto(r, 4), valor=num(r, 5),
             palabras=texto(r, 6), como=texto(r, 10), color=color(r), _oculto=oculto(r))
    return {k: v for k, v in d.items() if v not in (None, "")}


# ---------------------------------------------------------------- recorrido de la hoja
out = dict(titulo=texto(1, 2), supone=texto(2, 2), leer=None, productos=None, datos=None, partes=[], conclusion=None)
parte = None
r = 1
while r <= V.max_row:
    b = V.cell(r, 2).value
    b = b if isinstance(b, str) else ""
    if b.startswith("0. PRODUCTOS"):
        fin = hasta_vacia(r + 1)
        p = r + 1
        NPROD = V.cell(p, 6).value
        filas = [dict(id=f"r{x}", nombre=texto(x, 2), que=texto(x, 3), unidad=texto(x, 4), cap=num(x, 5), vend=num(x, 6),
                      porque=texto(x, 7)) for x in range(p + 1, fin)]
        out["productos"] = dict(id=f"r{p}", titulo=oracion(b.split(". ", 1)[1]), nombre=oracion(texto(p, 2)), que=texto(p, 3),
                                total=num(p, 6), porque=texto(p, 7), abierto=not oculto(p + 1), color=color(p),
                                cols=[texto(r, 5), texto(r, 6)], filas=[{k: v for k, v in f.items() if v} for f in filas])
        out["leer"] = texto(3, 2)      # se limpia después de conocer NPROD
        r = fin
    elif b.startswith("0b. "):
        fin = hasta_vacia(r + 1)
        filas = []
        for x in range(r + 1, fin):
            d = dict(id=f"r{x}", nombre=texto(x, 2), que=texto(x, 3), unidad=texto(x, 4), valor=num(x, 5), porque=texto(x, 6))
            anios = [num(x, c) for c in ANIOS]
            if any(anios):
                d["anios"] = [a[0] if a else None for a in anios]
                d["tanios"] = next(a[1] for a in anios if a)
            filas.append({k: v for k, v in d.items() if v})
        out["datos"] = dict(titulo=oracion(b.split(". ", 1)[1]), filas=filas)
        r = fin
    elif b.startswith("PARTE "):
        cab, _, resto = texto(r, 2).partition(":")
        letra, _, cab = cab.partition(" · ")
        parte = dict(letra=letra.title(), titulo=oracion(cab), texto=resto.strip()[:1].upper() + resto.strip()[1:], tablas=[])
        out["partes"].append(parte)
    elif b == "Concepto":
        m = r + 1
        if str(V.cell(m, 2).value or "").startswith("("):
            m += 1
        fin = hasta_vacia(m + 1)
        num_t, tit = V.cell(m, 2).value.split(". ", 1)
        principal = fila_suma(m)
        principal.pop("_oculto")
        hijos = anidar([fila_suma(x) for x in range(m + 1, fin)])
        principal.update(num=num_t, titulo=oracion(texto(m, 2).split(". ", 1)[1]), hijos=hijos,
                         abierto=bool(hijos) and not oculto(m + 1))
        parte["tablas"].append(dict(tipo="suma", fila=principal))
        r = fin
        continue
    elif b.startswith("Nota de la tabla"):
        parte["tablas"][-1]["nota"] = texto(r, 2)
    elif re.match(r"^\d+\. ", b) and V.cell(r, 3).value == "¿Qué es?":
        m = r + 1
        fin = hasta_vacia(m + 1)
        principal = fila_calc(m)
        principal.pop("_oculto")
        hijos = [fila_calc(x) for x in range(m + 1, fin)]
        abierto = bool(hijos) and not hijos[0]["_oculto"]
        for h in hijos:
            h.pop("_oculto")
        num_t, tit = b.split(". ", 1)
        principal.update(num=num_t, titulo=oracion(tit), hijos=hijos, abierto=abierto)
        parte["tablas"].append(dict(tipo="calculo", fila=principal))
        r = fin
        continue
    elif b.startswith("CONCLUSIÓN"):
        out["conclusion"] = dict(titulo=oracion(b), texto=texto(r + 1, 2))
        r += 1
    r += 1

# etiquetas de los años (de la tabla 0) y textos que dependían del total de productos
out["anios"] = ["Año 0 · montaje, antes de vender"] + [f["nombre"].replace(" (", " · ").rstrip(")") for f in out["productos"]["filas"]]
out["nprod"] = NPROD


# ---------------------------------------------------------------- las 8 preguntas (tarjetas de arriba)
def buscar(pref):
    def rec(f):
        if (f.get("nombre") or "").startswith(pref):
            return f
        for h in f.get("hijos", []):
            x = rec(h)
            if x:
                return x
    for p in out["partes"]:
        for t in p["tablas"]:
            x = rec(t["fila"])
            if x:
                return x
    for f in out["datos"]["filas"]:
        if f["nombre"].startswith(pref):
            return f
    raise SystemExit(f"No encontré la fila «{pref}» en la hoja {HOJA}")


inv, mat, prod, adm = buscar("4. "), buscar("Materiales"), buscar("6. "), buscar("7. ")
gasto, uti, precio = buscar("9. "), buscar("11. "), buscar("Precio al público")
meta, pe, pe_mes = buscar("RESULTADO: utilidad sobre"), buscar("RESULTADO: punto de equilibrio"), buscar("¿En qué mes se logra")
roi, rec_mes = buscar("RESULTADO: retorno"), buscar("¿En qué mes se recupera")
pp = lambda f: f"${miles(f['pp'][0])} por producto"
out["costo"] = dict(fila=gasto["id"], valor=gasto["pp"], nota="Todo incluido: máquinas, arranque, producción, nómina, ventas e intereses, "
                    f"repartido entre los {miles(NPROD)} productos de los 10 años.")
out["preguntas"] = [
    dict(n=1, titulo="Inversión inicial", fila=inv["id"], valor=inv["total"], nota="Lo que hay que poner para empezar (año 0)."),
    dict(n=2, titulo="Costo de materiales", fila=mat["id"], valor=mat["total"], nota=f"10 años · {pp(mat)}"),
    dict(n=3, titulo="Costo de producción", fila=prod["id"], valor=prod["total"], nota=f"10 años · {pp(prod)}"),
    dict(n=4, titulo="Gastos administrativos", fila=adm["id"], valor=adm["total"], nota=f"10 años, con toda la nómina · {pp(adm)}"),
    dict(n=5, titulo="Utilidad neta", fila=uti["id"], valor=uti["total"],
         nota=f"10 años · {round(meta['valor'][0] * 100, 1):.1f} % sobre el costo (meta 35 %)".replace(".", ",", 1),
         alerta=meta["valor"][0] < 0.35),
    dict(n=6, titulo="Precio de venta", fila=precio["id"], valor=precio["valor"], nota="Al público, con IVA. Sube con la inflación."),
    dict(n=7, titulo="Punto de equilibrio", fila=pe["id"], valor=pe["valor"], unidad="al mes",
         nota=f"Productos al mes para no perder · se logra en el mes {pe_mes['valor'][0]}"),
    dict(n=8, titulo="Retorno de la inversión", fila=roi["id"], valor=roi["valor"],
         nota=f"En 10 años · la inversión se recupera en el mes {rec_mes['valor'][0]}"),
]
out["fuente"] = dict(archivo=os.path.basename(SRC), hoja=HOJA,
                     guardado=(wf.properties.modified or datetime.fromtimestamp(os.path.getmtime(SRC))).strftime("%Y-%m-%d %H:%M"))

js = ("// Generado por fuente/presupuesto/extraer_presupuesto.py desde " + os.path.basename(SRC) + " (hoja " + HOJA + ").\n"
      "// No editar a mano: si cambia el Excel, se vuelve a correr el script.\n"
      "window.PRESUPUESTO = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
os.makedirs(os.path.dirname(os.path.abspath(DST)), exist_ok=True)
open(DST, "w", encoding="utf-8").write(js)
print("ok", DST, f"{len(js) / 1024:.0f} KB", "| productos:", NPROD, "| tablas:", sum(len(p["tablas"]) for p in out["partes"]))
