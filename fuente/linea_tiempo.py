# Arma la línea de tiempo del video a partir de las frases grabadas:
#   · narracion_48k.wav (voz colocada con pausas), musica_bucle.wav (cierra en bucle sin corte), mezcla.wav
#   · tiempos.json (eventos de animación para Blender), subs.json + RECOEVO_subtitulos.srt, tarjetas.json
# Uso (Python de tts-env): python linea_tiempo.py ../audio/guion_frases.json ../audio/voz_frases ../audio/musica_cruda.wav ../audio
import os
import sys
import json
import math
import subprocess
import numpy as np
import soundfile as sf
import torch
import torchaudio

FPS = 30
SR = 48000


def leer(ruta):
    w, s = sf.read(ruta, dtype='float32', always_2d=True)
    w = torch.from_numpy(w.T.copy())
    if s != SR:
        w = torchaudio.functional.resample(w, s, SR)
    return w.numpy()


def rms_db(x):
    return 20 * math.log10(max(1e-9, float(np.sqrt(np.mean(x ** 2)))))


def main():
    guion_p, voz_dir, musica_p, salida = sys.argv[1:5]
    bloques = json.load(open(guion_p, encoding='utf-8'))
    B = {b['id']: b for b in bloques}
    voz = {b['id']: leer(os.path.join(voz_dir, b['id'] + '.wav'))[0] for b in bloques}
    # mismo nivel para todas las frases (la mezcla final se normaliza en sonoridad)
    for k, w in voz.items():
        voz[k] = w * 10 ** ((-21.0 - rms_db(w[np.abs(w) > 0.01 * np.abs(w).max()])) / 20)
    dur = {k: len(w) / SR for k, w in voz.items()}

    # pausas después de cada frase: dejan ver la acción que la frase anuncia
    PAUSA = {'p1a': 0.45, 'p1b': 0.9, 'p2a': 0.45, 'p2b': 1.0, 'c1': 0.45, 'c2': 1.1,
             's1': 0.5, 's2': 1.3, 's3': 1.3, 's4': 1.3, 's5': 2.2,
             'd1a': 3.6, 'd1b': 1.1, 'd1c': 1.1, 'd2': 1.9,
             'm1': 0.45, 'm2': 0.45, 'm3': 0.45, 'm4': 0.0}
    t = 1.0
    pos = {}
    for b in bloques:
        if b['id'] == 'd1b':
            # la frase del piñón espera a que las piezas terminen de separarse (≈4 s desde que empieza la explosión)
            f_s5 = pos['s5'][1]
            explota = f_s5 + 0.3 + 0.9 + 0.6 + 0.4 + 2.8 + 0.1
            t = max(t, explota + 3.8)
        pos[b['id']] = (round(t, 3), round(t + dur[b['id']], 3))
        t += dur[b['id']] + PAUSA.get(b['id'], 0.5)
    ini = {k: v[0] for k, v in pos.items()}
    fin = {k: v[1] for k, v in pos.items()}

    # ---- eventos de animación (segundos)
    T = {}
    T['tapa_abre'] = ini['s2'] + 0.05
    T['cascaras'] = ini['s2'] + 0.85
    T['tapa_cierra'] = ini['s3'] + 0.0
    T['rayosx_on'] = ini['s3'] + 0.55
    T['pisadas_der'] = [round(ini['s3'] + 1.15 + 0.9 * k, 3) for k in range(4)]
    T['pisada_izq'] = ini['s4'] + 0.25
    T['rayosx_off'] = fin['s4'] + 0.7
    T['puerta_abre'] = ini['s5'] + 0.05
    T['balde_sale'] = ini['s5'] + 1.1
    T['balde_entra'] = fin['s5'] + 0.3
    T['puerta_cierra'] = T['balde_entra'] + 0.9
    T['flota'] = T['puerta_cierra'] + 0.6
    T['disuelve'] = [T['flota'] + 0.4, T['flota'] + 3.2]
    T['explota'] = T['disuelve'][1] + 0.1
    T['grupos'] = [T['explota'] + 2.0, ini['d1b'], ini['d1c'], ini['d2']]
    T['etiquetas_fin'] = fin['d2'] + 1.3
    T['arma'] = T['etiquetas_fin'] + 0.5
    T['aterriza'] = [T['arma'] + 5.0, T['arma'] + 7.6]
    T['regresa'] = [T['arma'] + 5.6, T['arma'] + 9.0]
    T['cierre_logo'] = [ini['m3'] - 0.3, fin['m4'] + 0.9]
    total = max(fin['m4'] + 2.4, T['regresa'][1] + 1.7)
    nfot = int(math.ceil(total * FPS))
    T['dur'] = nfot / FPS
    T['voz'] = pos
    # ini['d1b'] debe dejar tiempo a la explosión: si no, se corre todo (no debería pasar con las pausas de arriba)
    assert ini['d1b'] >= T['explota'] + 3.7, (ini['d1b'], T['explota'])
    for k, v in T.items():
        if isinstance(v, float):
            T[k] = round(v, 3)
    json.dump(T, open(os.path.join(salida, 'tiempos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---- tarjetas de cifras (en pantalla, además de los subtítulos)
    tarjetas = [
        {'ini': ini['p1a'] + 0.2, 'fin': fin['p1a'] + 0.3, 'grande': '33.000 t', 'texto': 'de basura al día van a rellenos en Colombia',
         'pie': 'Solo 1 de cada 5 se aprovecha · Superservicios, 2024'},
        {'ini': ini['p1b'] + 0.1, 'fin': fin['p1b'] + 0.6, 'grande': '≈6.000 t/día', 'texto': 'llegan a Doña Juana: más de la mitad es orgánico',
         'pie': 'Licencia hasta ≈2029 · UAESP'},
        {'ini': fin['p1b'] - 1.6, 'fin': fin['p1b'] + 0.8, 'grande': '7 de 10', 'texto': 'vecinos de Usme dicen que los perros rompen las bolsas',
         'pie': 'Entrevistas del equipo, 2026', 'segunda': True},
        {'ini': ini['p2a'] + 0.4, 'fin': fin['p2a'] + 0.2, 'grande': '+94 %', 'texto': 'de los fertilizantes del país es importado',
         'pie': 'Investigación del equipo'},
        {'ini': ini['p2a'] + 4.0, 'fin': fin['p2b'] + 0.4, 'grande': '+187 %', 'texto': 'subió la urea entre 2021 y 2022',
         'pie': 'El campo paga por el abono que la ciudad entierra', 'segunda': True},
        {'ini': ini['c1'] + 0.1, 'fin': fin['c1'] + 0.7, 'grande': 'Decreto 0772', 'texto': 'de 2026: separar en casa es obligatorio',
         'pie': 'Ruta de orgánicos al menos 1 vez por semana · Minvivienda'},
        {'ini': ini['c2'] + 0.2, 'fin': fin['c2'] + 0.7, 'grande': '6 de 10', 'texto': 'vecinos separarían si tuvieran con qué',
         'pie': '4 de 10 ya reutilizan cáscaras · entrevistas del equipo'},
        {'ini': ini['m1'] + 0.1, 'fin': fin['m2'] + 0.5, 'tipo': 'comparacion'},
    ]
    json.dump(tarjetas, open(os.path.join(salida, 'tarjetas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---- subtítulos (texto en pantalla con cifras)
    subs = [{'ini': ini[b['id']], 'fin': fin[b['id']], 'texto': b['sub']} for b in bloques]
    json.dump(subs, open(os.path.join(salida, 'subs.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    def tc(s):
        ms = int(round(s * 1000))
        return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'
    with open(os.path.join(salida, 'RECOEVO_subtitulos.srt'), 'w', encoding='utf-8') as fh:
        for i, s in enumerate(subs, 1):
            fh.write(f"{i}\n{tc(s['ini'])} --> {tc(s['fin'])}\n{s['texto']}\n\n")

    # ---- audio: voz + música en bucle exacto (el video tiene nfot + 1 fotogramas; el último repite el primero)
    largo = int(round((nfot + 1) / FPS * SR))
    narr = np.zeros(largo, np.float32)
    for k, (a, _) in pos.items():
        i = int(round(a * SR))
        narr[i:i + len(voz[k])] += voz[k][:max(0, largo - i)]
    sf.write(os.path.join(salida, 'narracion_48k.wav'), narr, SR, subtype='PCM_24')
    mus = leer(musica_p)                       # estéreo
    X = int(3.0 * SR)                          # cruce del bucle
    if mus.shape[1] < largo + X:
        reps = int(math.ceil((largo + X) / mus.shape[1]))
        mus = np.concatenate([mus] * reps, 1)
    cuerpo = mus[:, :largo].copy()
    rampa = np.linspace(0, 1, X, dtype=np.float32) ** 0.5
    cuerpo[:, :X] = mus[:, largo:largo + X] * (1 - rampa) + mus[:, :X] * rampa     # el final empalma con el inicio
    cuerpo *= 10 ** ((-25.0 - rms_db(cuerpo)) / 20)
    # baja la música mientras habla la voz (suave, 0,25 s de ataque y 0,6 s de salida)
    hay_voz = np.zeros(largo, np.float32)
    for a, b in pos.values():
        hay_voz[int(a * SR):int(b * SR)] = 1
    k = int(0.4 * SR)
    env = np.convolve(hay_voz, np.ones(k, np.float32) / k, mode='same')
    ganancia = 1 - 0.45 * np.clip(env * 1.6, 0, 1)
    cuerpo *= ganancia[None, :]
    sf.write(os.path.join(salida, 'musica_bucle.wav'), cuerpo.T, SR, subtype='PCM_24')
    mezcla = cuerpo + narr[None, :] * 1.0
    sf.write(os.path.join(salida, 'mezcla_sin_norm.wav'), mezcla.T, SR, subtype='FLOAT')
    # sonoridad final −16 LUFS, pico −1,5 dBTP (ffmpeg del sistema, 2 pasadas)
    med = subprocess.run(['ffmpeg', '-hide_banner', '-i', os.path.join(salida, 'mezcla_sin_norm.wav'), '-af',
                          'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(med[med.rfind('{'):med.rfind('}') + 1])
    filtro = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
              f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(salida, 'mezcla_sin_norm.wav'), '-af', filtro,
                    '-c:a', 'pcm_s24le', os.path.join(salida, 'mezcla.wav')], check=True)
    print(json.dumps({'duracion_video_s': round((nfot + 1) / FPS, 3), 'nfot': nfot, 'voz_ini': ini['p1a'], 'voz_fin': fin['m4'],
                      'explota': T['explota'], 'arma': T['arma']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
