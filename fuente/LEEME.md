# Fuente del video y del modelo 3D

Scripts para regenerar el video del evento y el modelo `.glb` de esta página (Blender 5.2 + Python 3.12).
El paso a paso completo está en `LEEME.txt` de la carpeta de entregables en Drive
(`04. Recoevo/02_RECOEVO_VIDEO_EVENTO_INVERSIONISTAS`).

| Script | Qué hace |
|---|---|
| `rv_producto.py` | Modelo del prototipo v3 (piezas y medidas de la lista de materiales v3) |
| `rv_cocina.py`, `rv_estudio.py` | Cocina colombiana y estudio limpio |
| `rv_anim.py` | Uso, rayos X, explosionada, cámaras y etiquetas |
| `construir_escena.py` | Arma la escena por formato (16:9 / 9:16) y exporta el `.glb` |
| `render.py`, `render_todo.sh` | Render con Cycles (autodetecta GPU y CPU) |
| `voz_omnivoice.py`, `asr.py` | Voz clonada de William (OmniVoice) y verificación con Whisper |
| `musica.py` | Música suave con MusicGen |
| `linea_tiempo.py` | Tiempos, subtítulos, tarjetas y mezcla en bucle |
| `componer.py` | Compone y codifica los MP4 (primer y último fotograma idénticos) |

No incluye fotogramas, archivos `.blend` ni audios de trabajo (pesan varios GB).
