# Escribe el guion final (texto exacto grabado + tiempos reales) a partir de guion_v2.json y tiempos.json.
import sys
import json

guion = json.load(open(sys.argv[1], encoding='utf-8'))
T = json.load(open(sys.argv[2], encoding='utf-8'))
salida = sys.argv[3]
SECCIONES = {
    'problema1': 'PROBLEMÁTICA 1 · LA BASURA DE LA CIUDAD  (cocina colombiana, el equipo frente al mesón)',
    'problema2': 'PROBLEMÁTICA 2 · EL CAMPO SIN ABONO  (la ventana con la sábila)',
    'consecuencia': 'LA CONSECUENCIA · HAY QUE SEPARAR EN CASA',
    'solucion': 'LA SOLUCIÓN · RECOEVO, CÓMO SE USA  (tapa, cáscaras, pedal derecho con rayos X, pedal izquierdo, balde)',
    'dentro': 'POR DENTRO · VISTA EXPLOSIONADA  (la cocina se desvanece, el equipo flota y se despieza con etiquetas)',
    'mercado': 'POR QUÉ ES LA MEJOR OPCIÓN + LLAMADO A LA ACCIÓN  (se arma y vuelve exactamente al primer fotograma)',
}


def mmss(s):
    return f'{int(s // 60)}:{s % 60:04.1f}'


dur = T['dur'] + 1 / 30
lineas = ['RECOEVO · VIDEO DE PRODUCTO PARA EL EVENTO DE INVERSIONISTAS',
          'Guion de narración — VERSIÓN GRABADA (29-oct-2026)',
          'Voz: clon «william_3reels» de ClonacionVoz, motor OmniVoice (el mismo de la app), velocidad 1,10×.',
          f'Duración del video: {mmss(dur)} ({dur:.1f} s), en bucle: el último fotograma es igual al primero.',
          'La voz arranca en 0:01 y termina 2,4 s antes del final; la música cierra el bucle sin corte.',
          '', 'Columna VOZ: lo que dice la narración. Columna PANTALLA: el subtítulo (con cifras).', '']
actual = None
for b in guion:
    if b['sec'] != actual:
        actual = b['sec']
        lineas += ['═' * 100, SECCIONES[actual], '═' * 100]
    a, f = T['voz'][b['id']]
    voz = b['voz'].replace('Reco Evo', 'Recoevo').replace(' iva ', ' IVA ')
    lineas += [f'[{mmss(a)} – {mmss(f)}]', f'  VOZ:      {voz}', f'  PANTALLA: {b["sub"]}', '']
lineas += ['─' * 100,
           'Tarjetas de cifras en pantalla: 33.000 t/día y 1 de cada 5 (Superservicios 2024) · Doña Juana ≈6.000 t/día,',
           'más de la mitad orgánico, licencia hasta ≈2029 (UAESP) · 7 de cada 10 vecinos de Usme: perros rompen las bolsas',
           '(entrevistas del equipo) · más del 94 % de fertilizantes importado · urea +187 % entre 2021 y 2022 ·',
           'Decreto 0772 de 2026 (Minvivienda) · 6 de cada 10 separarían si tuvieran con qué · 4 de cada 10 ya reutilizan cáscaras.',
           'Comparación: triturador eléctrico importado $1,3–1,7 M (+ luz y filtros) · compostera de patio $410–660 mil ·',
           'caneca con pedal 44 L $204 mil · RECOEVO v3 $199.900 con IVA (investigación A7 del plan de fábrica, oct-2026).',
           'Cierre: logo + «Súmate a esta iniciativa» + QR a https://whafonsecav.github.io/Prototipo-Recoevo/',
           '',
           'Nota honesta: las cifras de Usme salen de 10 entrevistas cualitativas del equipo (no es una encuesta estadística).',
           'Para la voz, «Recoevo» se escribió «Reco Evo» en dos frases (el modelo decía «Recuevo»); suena «Re-co-e-vo».']
open(salida, 'w', encoding='utf-8').write('\n'.join(lineas) + '\n')
print('ok', salida)
