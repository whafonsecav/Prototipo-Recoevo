# Música suave para el video (MusicGen stereo large, local). Genera ~100 s en tramos encadenados.
# Uso (Python de tts-env): python musica.py salida.wav [segundos]
# Autodetecta GPU (CUDA) o CPU y lo registra.
import os
import sys
import time
import numpy as np
import soundfile as sf
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

salida = sys.argv[1]
total = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
torch.set_num_threads(os.cpu_count() or 1)
try:
    import psutil
    ram = f'{psutil.virtual_memory().available / 2**30:.1f} GB libres'
except Exception:
    ram = 'RAM no medida'
gpu = torch.cuda.get_device_name(0) + f' ({torch.cuda.get_device_properties(0).total_memory / 2**30:.1f} GB)' if dev == 'cuda' else 'sin GPU'
print(f'[hardware] {os.cpu_count()} hilos (torch usa {torch.get_num_threads()}) · {ram} · {gpu} → generación en {dev}', flush=True)

nombre = 'facebook/musicgen-stereo-large'
proc = AutoProcessor.from_pretrained(nombre)
modelo = MusicgenForConditionalGeneration.from_pretrained(nombre, torch_dtype=torch.float16 if dev == 'cuda' else torch.float32).to(dev)
SR = modelo.config.audio_encoder.sampling_rate
FR = 50
BASE = ('soft warm acoustic background music for an elegant product video, gentle felt piano and soft marimba, '
        'light plucked guitar, airy pads, slow steady tempo 90 bpm, optimistic and calm, sustainable home, '
        'no drums, no vocals, clean high quality mix')
TRAMOS = [(BASE + ', intro, sparse', 30), (BASE, 26), (BASE + ', slightly brighter', 26), (BASE + ', same theme, calm', 26)]


def generar(prompt, seg, previo=None, ctx=8, semilla=0):
    torch.manual_seed(semilla)
    if previo is None:
        inp = proc(text=[prompt], padding=True, return_tensors='pt').to(dev)
    else:
        cola = previo[:, -ctx * SR:]
        inp = proc(audio=[cola], text=[prompt], sampling_rate=SR, padding=True, return_tensors='pt')
        inp = {k: (v.to(dev).half() if (v.dtype == torch.float32 and dev == 'cuda') else v.to(dev)) for k, v in inp.items()}
    with torch.no_grad():
        a = modelo.generate(**inp, do_sample=True, guidance_scale=3.0, max_new_tokens=int(seg * FR))
    a = a[0].float().cpu().numpy()
    return a[:, ctx * SR:] if previo is not None else a


t0 = time.time()
out = None
k = 0
while out is None or out.shape[1] / SR < total:
    p, s = TRAMOS[min(k, len(TRAMOS) - 1)]
    a = generar(p, s, out, semilla=31 + k)
    out = a if out is None else np.concatenate([out, a], 1)
    print(f'  tramo {k}: {out.shape[1] / SR:.1f} s ({time.time() - t0:.0f} s)', flush=True)
    k += 1
sf.write(salida, out.T, SR)
print('[musica] listo', salida, f'{out.shape[1] / SR:.1f} s en {time.time() - t0:.0f} s', flush=True)
