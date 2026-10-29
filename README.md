# RECOEVO · Prototipo interactivo

Triturador de residuos orgánicos para la cocina, **a pedal y sin electricidad**. *Menos relleno, más vida.*
Esta página muestra el equipo en 3D para explorarlo en una tablet durante el evento de inversionistas.

**Abrir:** https://whafonsecav.github.io/Prototipo-Recoevo/

**Videos del evento** (1 min 49 s, en bucle, con subtítulos):
[horizontal 16:9](https://whafonsecav.github.io/Prototipo-Recoevo/video/RECOEVO_video_evento_16x9.mp4) ·
[vertical 9:16](https://whafonsecav.github.io/Prototipo-Recoevo/video/RECOEVO_video_evento_9x16.mp4)

## Cómo se usa
- **Deslizar** con un dedo: girar el equipo. **Pellizcar**: acercar o alejar.
- **Tocar una pieza** (o un punto verde): se abre su ficha con qué hace y de qué está hecha.
- **Separar piezas**: el equipo se despieza (vista explosionada) con un punto en cada pieza.
- **Cómo funciona**: recorrido animado en 4 pasos (tapa, pedal derecho, pedal izquierdo, balde).
- **Centrar** (⟲): vuelve a la vista inicial.
- Si nadie toca la pantalla durante 35 s, entra en **modo vitrina**: gira solo y se arma y separa cada 9 s.

## Para el evento (sin internet)
1. Abrir la dirección en Chrome o Safari de la tablet con internet una vez.
2. Menú → **Agregar a la pantalla de inicio** (queda como app de pantalla completa).
3. Desde ese momento funciona **sin conexión**: todo lo necesario queda guardado en la tablet.

## Qué hay aquí
| Carpeta / archivo | Qué es |
|---|---|
| `index.html`, `assets/` | La app (three.js r149 incluido, sin servidores externos) |
| `assets/modelo/recoevo.glb` | El equipo en 3D, el mismo del video, exportado de Blender |
| `assets/js/partes.js` | Texto de cada pieza (fuente: lista de materiales del plan de fábrica) |
| `sw.js`, `manifest.webmanifest` | Funcionamiento sin conexión y «app» en la pantalla de inicio |
| `video/` | Videos del evento (16:9 y 9:16), subtítulos `.srt` y guion |
| `fuente/` | Scripts para regenerar el equipo en 3D y los videos (Blender 5.2 + Python) |

## Créditos y licencias
- Equipo, textos y video: equipo RECOEVO (Politécnico Grancolombiano, Proceso Administrativo, 2026).
- three.js (MIT), Lexend y Nunito (SIL OFL) — licencias en `assets/vendor` y `assets/fonts`.
- RECOEVO todavía no está fabricado ni ensayado; las medidas y los materiales vienen del plan de fábrica.
