"""Voz del guion de la final: un MP3 con una voz neural en español latino y los tiempos de cada frase.

El teleprompter usa esos tiempos para que el texto avance al ritmo de la voz.
Se genera frase por frase (edge-tts) y se arma con pausas fijas: entre frases, entre clics y entre pantallas.
La velocidad de la voz se ajusta sola para que el total dure lo mismo que el guion medido (≈ 7:00).

Uso:  python fuente/pitch/voz_guion.py <carpeta web> [--voz es-CO-SalomeNeural] [--meta SEGUNDOS]
Escribe: <web>/pitch/audio/RECOEVO_guion_final.mp3  y  fuente/pitch/voz_tiempos.json (lo lee generar_pitch.py).
Requiere: pip install edge-tts, y ffmpeg en el PATH. El texto que se envía es el guion público de la web.
"""
import asyncio, hashlib, json, os, pathlib, re, subprocess, sys, tempfile, time

import numpy as np
import edge_tts

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import generar_pitch as g  # noqa: E402  (el guion, sus marcas y su medición)

SR = 24000
VOZ = "es-CO-SalomeNeural"
NOMBRE = "RECOEVO_guion_final.mp3"
INICIO, FRASE, CLIC, PANTALLA, FINAL = 0.6, 0.45, 1.0, 1.6, 0.8   # segundos de silencio

# Cómo debe decirse en voz alta lo que la voz leería mal (revisado con una transcripción automática del audio)
DICCION = [
    (r"\bRECOEVO\b", "Reco Evo"),          # si no, suena «recuevo»
    (r"\b0772\b", "cero setecientos setenta y dos"),
    (r"\bIVA\b", "iva"),
    (r"CO₂", "ce o dos"),
]
FIN_FRASE = re.compile(r"[.!?…][»\"”)\]]*$")

# Las cifras se le dan a la voz en letras, para que no se coma ninguna parte («199.900» = «ciento noventa y nueve mil novecientos»)
UN = ("cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciséis diecisiete "
      "dieciocho diecinueve veinte veintiuno veintidós veintitrés veinticuatro veinticinco veintiséis veintisiete "
      "veintiocho veintinueve").split()
DE = ["", "", "", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]
CE = ["", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos"]


def letras(n):
    if n < 30: return UN[n]
    if n < 100: return DE[n // 10] + (" y " + UN[n % 10] if n % 10 else "")
    if n < 1000: return ("cien" if n == 100 else CE[n // 100]) + (" " + letras(n % 100) if n % 100 else "")
    if n < 10 ** 6:
        k, r = divmod(n, 1000)
        return ("mil" if k == 1 else apocope(letras(k)) + " mil") + (" " + letras(r) if r else "")
    m, r = divmod(n, 10 ** 6)
    return ("un millón" if m == 1 else apocope(letras(m)) + " millones") + (" " + letras(r) if r else "")


def apocope(s):  # «cuarenta y uno mil» → «cuarenta y un mil»
    return re.sub(r"veintiuno$", "veintiún", re.sub(r"(?<![a-zé])uno$", "un", s))


def cifra_en_letras(m):
    ent, dec = m.group(1).replace(".", ""), m.group(2)
    dicho = ("cero " if re.match(r"0\d", ent) else "") + letras(int(ent))
    if dec: dicho += " coma " + letras(int(dec)) if not dec.startswith("0") else " coma " + " ".join(UN[int(d)] for d in dec)
    return dicho


def texto_hablado(p):
    """El párrafo tal como se lee en el teleprompter: sin gestos ni partes que se pueden quitar."""
    s = "".join(x for tipo, x, opc in g.partes(p) if tipo != "dir" and not opc)
    return re.sub(r"\s+", " ", s).strip()


def frases(s):
    """Parte un párrafo en frases con la misma regla que usa el teleprompter: una palabra que termina en . ! ? …"""
    out, act = [], []
    for tok in s.split(" "):
        act.append(tok)
        if FIN_FRASE.search(tok):
            out.append(" ".join(act)); act = []
    if act: out.append(" ".join(act))
    return [f for f in out if f.strip()]


def para_voz(f):
    for a, b in DICCION: f = re.sub(a, b, f)
    f = re.sub(r"(?<![\d.,])(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?![\d])", cifra_en_letras, f)
    f = re.sub(r"\s*%", " por ciento", f)
    return f


async def sintetizar(texto, voz, tasa, cache, sem):
    clave = hashlib.sha1(f"{voz}|{tasa}|{texto}".encode()).hexdigest()[:16]
    ruta = cache / f"{clave}.mp3"
    if not ruta.exists() or ruta.stat().st_size == 0:
        async with sem:
            for intento in range(4):
                try:
                    await edge_tts.Communicate(texto, voz, rate=tasa).save(str(ruta)); break
                except Exception as ex:  # la red falla a veces: se reintenta
                    if intento == 3: raise
                    print("  reintento:", texto[:40], ex); await asyncio.sleep(2 + intento * 2)
    return ruta


def decodificar(ruta):
    crudo = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ruta), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                           capture_output=True, check=True).stdout
    return np.frombuffer(crudo, np.int16).astype(np.float32) / 32768


def recortar(x, umbral_db=-42, margen=0.03):
    """Quita el silencio del principio y del final de cada frase (deja 30 ms)."""
    v = 10 ** (umbral_db / 20)
    voz = np.where(np.abs(x) > v)[0]
    if not len(voz): return x[:0]
    a = max(0, voz[0] - int(margen * SR)); b = min(len(x), voz[-1] + int(margen * SR))
    return x[a:b]


def estructura():
    """[(pantalla, párrafo, [frases])] en el orden del guion."""
    out = []
    for i, b in enumerate(g.GUION):
        for j, p in enumerate(b["p"]):
            out.append((i, j, frases(texto_hablado(p))))
    return out


async def generar_todo(est, voz, tasa, cache):
    hilos = os.cpu_count() or 4
    sem = asyncio.Semaphore(max(2, min(8, hilos)))   # el trabajo es de red: unas pocas a la vez
    tareas = [sintetizar(para_voz(f), voz, tasa, cache, sem) for _, _, fs in est for f in fs]
    return await asyncio.gather(*tareas)


def armar(est, rutas):
    pistas = [recortar(decodificar(r)) for r in rutas]
    k, t, piezas, parrafos = 0, INICIO, [np.zeros(int(INICIO * SR), np.float32)], []
    habla = 0.0
    for n, (i, j, fs) in enumerate(est):
        if n:
            hueco = PANTALLA if j == 0 else CLIC
            piezas.append(np.zeros(int(hueco * SR), np.float32)); t += hueco
        anclas = []
        for m, _ in enumerate(fs):
            if m:
                piezas.append(np.zeros(int(FRASE * SR), np.float32)); t += FRASE
            x = pistas[k]; k += 1
            anclas.append([round(t, 3), round(t + len(x) / SR, 3)])
            piezas.append(x); t += len(x) / SR; habla += len(x) / SR
        parrafos.append(anclas)
    piezas.append(np.zeros(int(FINAL * SR), np.float32)); t += FINAL
    return np.concatenate(piezas), parrafos, t, habla


def main():
    web = pathlib.Path(sys.argv[1])
    voz = sys.argv[sys.argv.index("--voz") + 1] if "--voz" in sys.argv else VOZ
    _, _, sin_opc = g.medir()
    meta = float(sys.argv[sys.argv.index("--meta") + 1]) if "--meta" in sys.argv else round(sin_opc)
    cache = pathlib.Path(tempfile.gettempdir()) / "recoevo_voz_cache"; cache.mkdir(exist_ok=True)
    est = estructura()
    nfr = sum(len(fs) for *_, fs in est)
    print(f"equipo: {os.cpu_count()} hilos lógicos; la síntesis es de red: hasta {max(2, min(8, os.cpu_count() or 4))} frases a la vez")
    print(f"guion: {len(g.GUION)} pantallas, {len(est)} párrafos (clics), {nfr} frases; meta {meta:.0f} s; voz {voz}")

    tasa, t0 = "+0%", time.time()
    rutas = asyncio.run(generar_todo(est, voz, tasa, cache))
    audio, parrafos, total, habla = armar(est, rutas)
    pausas = total - habla
    print(f"primera pasada ({tasa}): {g.mmss(total)}  (habla {habla:.0f} s + pausas {pausas:.0f} s)")
    pct = round((habla / max(30, meta - pausas) - 1) * 100)
    pct = max(-25, min(35, pct))
    if abs(pct) >= 2:
        tasa = f"{pct:+d}%"
        rutas = asyncio.run(generar_todo(est, voz, tasa, cache))
        audio, parrafos, total, habla = armar(est, rutas)
        print(f"ajustada ({tasa}): {g.mmss(total)}")
    print(f"síntesis y armado: {time.time() - t0:.0f} s")

    destino = web / "pitch" / "audio"; destino.mkdir(parents=True, exist_ok=True)
    mp3 = destino / NOMBRE
    pico = float(np.max(np.abs(audio))) or 1.0
    audio = audio * (10 ** (-1.5 / 20) / pico)      # volumen alto y parejo, sin tocar los tiempos
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "libmp3lame", "-b:a", "64k",
                    "-metadata", "title=RECOEVO · Guion de la final", "-metadata", "artist=RECOEVO",
                    "-metadata", "album=Ronda 2 · 25 de noviembre de 2026", str(mp3)],
                   input=pcm, check=True)
    datos = {"src": NOMBRE, "voz": voz, "tasa": tasa, "duracion": round(total, 2), "parrafos": parrafos}
    (AQUI / "voz_tiempos.json").write_text(json.dumps(datos, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"escrito: {mp3} ({mp3.stat().st_size / 1e6:.1f} MB, {g.mmss(total)})")
    print(f"escrito: {AQUI / 'voz_tiempos.json'}")


if __name__ == "__main__":
    main()
