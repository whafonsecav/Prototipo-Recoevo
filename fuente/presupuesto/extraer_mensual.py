"""Lee la hoja «Proyección» del plan detallado REALISTA y escribe presupuesto/mensual.js para la página web.

Uso:  python fuente/presupuesto/extraer_mensual.py <RECOEVO_Plan_Detallado_Realista.xlsx> [presupuesto/mensual.js]

Solo copia cifras que el Excel ya calculó (el libro debe estar guardado desde Excel), mes a mes:
- productos vendidos (la rampa de ventas que sirve para saber CUÁNDO se llega al punto de equilibrio);
- precio sin IVA de la tienda propia y los marketplaces (× 1,19 = precio al público con IVA, que sube con la inflación);
- flujo libre acumulado (el mes en que se recupera la inversión);
- y de la hoja «9 Ventas y marketing», parte 3: la tarifa de envío por zona de las ventas por internet.
No cambia ningún número del presupuesto: la página solo los muestra y los explica.
"""
import json, os, sys
from datetime import datetime
import openpyxl

SRC = sys.argv[1]
DST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "..", "presupuesto", "mensual.js")
FILAS = {                                   # rótulo de la columna B → clave en la web
    "Año operativo": "anio",
    "Productos vendidos": "vendidos",
    "Precio sin IVA · directo y marketplaces": "precio_sin_iva",
    "Flujo libre acumulado (recuperación de la inversión)": "flujo_acumulado",
}
MESES = 120

ws = openpyxl.load_workbook(SRC, data_only=True, read_only=True)["Proyección"]
filas = list(ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True))
cab = next(r for r in filas if r[1] == "Mes #")
col0 = cab.index(0)                          # columna del mes 0 (las siguientes son los meses 1…120)
datos = {}
for r in filas:
    rotulo = (r[1] or "").strip() if isinstance(r[1], str) else ""
    if rotulo in FILAS and FILAS[rotulo] not in datos:
        datos[FILAS[rotulo]] = [r[col0 + m] for m in range(MESES + 1)]
faltan = set(FILAS.values()) - set(datos)
if faltan:
    sys.exit("No encontré en la hoja Proyección: " + ", ".join(sorted(faltan)))
for k, v in datos.items():
    if any(not isinstance(x, (int, float)) for x in v[1:]):
        sys.exit(f"La fila «{k}» tiene celdas sin valor calculado: guarda el libro desde Excel y vuelve a correr.")

# ---------------------------------------------------------------- envíos de las ventas por internet (hoja «9 Ventas y marketing», parte 3)
hv = list(openpyxl.load_workbook(SRC, data_only=True, read_only=True)["9 Ventas y marketing"].iter_rows(values_only=True))
celdas = lambda r: [v for v in r if v not in (None, "")]
def dato(rotulo):
    for r in hv:
        c = celdas(r)
        if c and isinstance(c[0], str) and c[0].startswith(rotulo) and len(c) > 1 and isinstance(c[1], (int, float)):
            return c[1]
    sys.exit(f"No encontré «{rotulo}» en la hoja 9 Ventas y marketing.")
i = next(k for k, r in enumerate(hv) if celdas(r)[:1] == ["Zona"])
zonas, promedio = [], None
for r in hv[i + 2:]:
    c = celdas(r)
    if not c:
        break
    if str(c[0]).startswith("PROMEDIO"):
        promedio = {"costo": c[2], "cobra": c[3]}
        break
    zonas.append({"zona": c[0], "pedidos": c[1], "costo": c[2], "cobra": c[3], "como": c[5] if len(c) > 5 else ""})
if not zonas or not promedio:
    sys.exit("No encontré la tabla de zonas de envío en la hoja 9 Ventas y marketing.")
envio = {"zonas": zonas, "promedio": promedio,
         "caja_cm": [dato("Caja: largo"), dato("Caja: ancho"), dato("Caja: alto")],
         "peso_real": dato("Peso del producto en su caja"), "peso_cobrado": dato("Peso que se cobra")}

salida = {
    "fuente": {"archivo": os.path.basename(SRC), "hoja": "Proyección",
               "guardado": datetime.fromtimestamp(os.path.getmtime(SRC)).strftime("%Y-%m-%d %H:%M")},
    "iva": 0.19,
    **datos,
    "envio": envio,
}
os.makedirs(os.path.dirname(os.path.abspath(DST)), exist_ok=True)
with open(DST, "w", encoding="utf-8", newline="\n") as f:
    f.write("/* Generado por fuente/presupuesto/extraer_mensual.py desde la hoja «Proyección» del plan realista. No editar a mano. */\n")
    f.write("window.PRESUPUESTO_MENSUAL = " + json.dumps(salida, ensure_ascii=False, separators=(",", ":")) + ";\n")
v = datos["vendidos"]
print(f"mensual.js listo: {MESES} meses, {sum(v[1:]):,.0f} productos; mes 1 = {v[1]:,.0f}, mes 120 = {v[MESES]:,.0f}")
