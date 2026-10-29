# Narración con la voz clonada de William («william_3reels» de ClonacionVoz) y el mismo motor de la app (OmniVoice).
# Por qué fuera de la app: el Control inteligente de aplicaciones de Windows bloquea hoy el python.exe 3.11 sin firma de
# ClonacionVoz\.python (registro CodeIntegrity 3077/3033 del 29-oct). Aquí se usa el Python 3.12 firmado de tts-env, con el
# paquete omnivoice copiado a una carpeta temporal y los mismos pesos (ClonacionVoz\modelos\hf). La carpeta de la app no se toca.
# Método (igual que la app v2): continuar el recorte «inicio» de William (termina bajando), 3 tomas por bloque,
# Whisper verifica la lectura y se descartan las tomas cuyo final sube; se elige la de menor error y final más natural.
# Uso: python voz_omnivoice.py guion.json carpeta_salida [--tomas 3] [--velocidad 1.05]
import os
import sys
import json
import time
import shutil
import argparse
import tempfile
import unicodedata
import re

RAIZ_APP = r'C:\Users\willi\ClonacionVoz'
os.environ.setdefault('HF_HOME', os.path.join(RAIZ_APP, 'modelos', 'hf'))
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')

import numpy as np            # noqa: E402
import soundfile as sf        # noqa: E402
import torch                  # noqa: E402


def preparar_omnivoice():
    origen = os.path.join(RAIZ_APP, 'motores', 'omnivoice', '.venv', 'Lib', 'site-packages', 'omnivoice')
    destino = os.path.join(tempfile.gettempdir(), 'recoevo_omnivoice_pkg')
    if not os.path.isdir(os.path.join(destino, 'omnivoice')):
        shutil.copytree(origen, os.path.join(destino, 'omnivoice'))
    sys.path.insert(0, destino)


def normal(t):
    t = unicodedata.normalize('NFKD', t.lower())
    t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9ñ ]+', ' ', t).split()


def wer(ref, hip):
    r, h = normal(ref), normal(hip)
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev = cur
    return d[len(h)] / max(1, len(r))


NUMEROS = set('cero un uno una dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciseis diecisiete '
               'dieciocho diecinueve veinte veintiuno veintidos veintinueve treinta cuarenta cincuenta sesenta setenta ochenta noventa '
               'cien ciento doscientos novecientos mil millon millones por ciento y'.split())


def wer_texto(ref, hip):
    """Error de palabras sin contar las cifras (Whisper las escribe con números y el guion de la voz con letras)."""
    r = ' '.join(w for w in normal(ref) if w not in NUMEROS and not w.isdigit())
    h = ' '.join(w for w in normal(hip) if w not in NUMEROS and not any(c.isdigit() for c in w))
    return wer(r, h)


def final_sube(wav, sr):
    """Semitonos entre el tono medio de la frase y el de sus últimos 0,45 s con voz (positivo = sube)."""
    try:
        import librosa
        f0, voz, _ = librosa.pyin(wav.astype(np.float32), fmin=70, fmax=400, sr=sr, frame_length=1024)
        f0 = f0[voz] if voz is not None else f0
    except Exception:          # sin librosa/numba: detector de tono de torchaudio
        import torchaudio
        f0 = torchaudio.functional.detect_pitch_frequency(torch.from_numpy(wav.astype(np.float32)), sr,
                                                          freq_low=70, freq_high=400).numpy()
        f0 = f0[(f0 > 70) & (f0 < 400)]
    f0 = f0[~np.isnan(f0)]
    if len(f0) < 20:
        return 0.0
    n = max(8, int(0.45 * sr / 256))
    return float(12 * np.log2(np.median(f0[-n:]) / np.median(f0)))


def recortar(wav, sr, umbral_db=-42):
    """Quita silencios del principio y del final (deja 40 ms)."""
    env = np.abs(wav)
    lim = 10 ** (umbral_db / 20) * max(1e-6, env.max())
    idx = np.where(env > lim)[0]
    if not len(idx):
        return wav
    a, b = max(0, idx[0] - int(0.04 * sr)), min(len(wav), idx[-1] + int(0.04 * sr))
    return wav[a:b]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('guion')
    p.add_argument('salida')
    p.add_argument('--tomas', type=int, default=3)
    p.add_argument('--velocidad', type=float, default=1.05)
    p.add_argument('--voz', default='william_3reels')
    p.add_argument('--solo', default='', help='ids separados por coma: regenera solo esos bloques')
    A = p.parse_args()
    os.makedirs(A.salida, exist_ok=True)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch.set_num_threads(os.cpu_count() or 1)
    gpu = torch.cuda.get_device_name(0) if dev == 'cuda' else 'sin GPU'
    print(f'[hardware] {os.cpu_count()} hilos · {gpu} → OmniVoice en {dev}', flush=True)

    preparar_omnivoice()
    from omnivoice import OmniVoice
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import asr

    voz = os.path.join(RAIZ_APP, 'voces', A.voz)
    with open(os.path.join(voz, 'perfil.json'), encoding='utf-8') as fh:
        perfil = json.load(fh)
    ref = os.path.join(voz, perfil['inicio']['archivo'])
    ref_texto = perfil['inicio']['texto']
    print('[voz]', perfil['nombre'], '· referencia', os.path.basename(ref), f"({perfil['inicio']['duracion']} s)", flush=True)

    t0 = time.time()
    try:
        modelo = OmniVoice.from_pretrained('k2-fsa/OmniVoice', dtype=torch.float16)
    except TypeError:
        modelo = OmniVoice.from_pretrained('k2-fsa/OmniVoice', torch_dtype=torch.float16)
    modelo = modelo.to(dev).eval()
    prompt = modelo.create_voice_clone_prompt(ref_audio=ref, ref_text=ref_texto)
    sr = int(modelo.sampling_rate)
    asr.cargar(dev)
    print(f'[voz] modelos cargados en {time.time() - t0:.0f} s', flush=True)

    with open(A.guion, encoding='utf-8') as fh:
        bloques = json.load(fh)          # [{"id": "p1a", "voz": "texto para la voz", "sub": "texto en pantalla"}, ...]
    ruta_inf = os.path.join(A.salida, 'informe_voz.json')
    previo = {}
    if A.solo and os.path.exists(ruta_inf):
        previo = {x['id']: x for x in json.load(open(ruta_inf, encoding='utf-8'))['bloques']}
    solo = set(x for x in A.solo.split(',') if x)
    informe = []
    for b in bloques:
        if solo and b['id'] not in solo:
            if b['id'] in previo:
                informe.append(previo[b['id']])
            continue
        mejores = []
        for k in range(A.tomas):
            semilla = 1000 + 37 * k + sum(map(ord, b['id']))
            torch.manual_seed(semilla)
            np.random.seed(semilla % 2**31)
            with torch.no_grad():
                wav = modelo.generate(text=b['voz'], language='es', voice_clone_prompt=prompt,
                                      speed=None if abs(A.velocidad - 1) < 1e-3 else A.velocidad,
                                      num_step=32, guidance_scale=2.0, denoise=True)[0]
            wav = np.asarray(wav, dtype=np.float32)
            wav = recortar(wav, sr)
            hip = asr.transcribir(wav, sr)
            e = wer_texto(b['voz'], hip)
            sube = final_sube(wav, sr)
            pide = 'recoevo' in normal(b['voz']) or 'reco evo' in ' '.join(normal(b['voz']))
            oye = ' '.join(normal(hip)).replace('reco evo', 'recoevo').replace('reco-evo', 'recoevo').replace('recoebo', 'recoevo')
            marca = 1.0 if (pide and 'recoevo' not in oye) else 0.0
            puntaje = e * 10 + marca * 3 + max(0.0, sube - 0.5) * 0.6
            mejores.append((puntaje, k, wav, e, sube, hip))
            print(f"  {b['id']} toma {k}: error {e:.2f} · marca {'ok' if not marca else 'NO'} · final {sube:+.1f} st · "
                  f"{len(wav) / sr:.1f} s · «{hip}»", flush=True)
        mejores.sort(key=lambda x: x[0])
        puntaje, k, wav, e, sube, hip = mejores[0]
        ruta = os.path.join(A.salida, f"{b['id']}.wav")
        sf.write(ruta, wav, sr)
        informe.append({'id': b['id'], 'toma': k, 'error': round(e, 3), 'final_st': round(sube, 2), 'duracion': round(len(wav) / sr, 3),
                        'transcripcion': hip.strip(), 'archivo': ruta})
        print(f"[voz] {b['id']}: toma {k} elegida (error {e:.2f}, final {sube:+.1f} st)", flush=True)
    with open(os.path.join(A.salida, 'informe_voz.json'), 'w', encoding='utf-8') as fh:
        json.dump({'voz': A.voz, 'motor': 'OmniVoice (k2-fsa) en tts-env', 'velocidad': A.velocidad, 'sr': sr, 'bloques': informe}, fh,
                  ensure_ascii=False, indent=1)
    print(f'[voz] listo en {time.time() - t0:.0f} s', flush=True)


if __name__ == '__main__':
    main()
