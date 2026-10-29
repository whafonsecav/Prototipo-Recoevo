# RECOEVO · Prototipo interactivo v3

Triturador de residuos orgánicos para la cocina, **a pedal y sin electricidad**. Esta página muestra el prototipo v3
(el del plan de fábrica del 29-oct-2026) en 3D para explorarlo en una tablet durante el evento de inversionistas.

**Abrir:** https://whafonsecav.github.io/Prototipo-Recoevo/

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
3. Desde ese momento funciona **sin conexión**: el modelo y todo lo necesario quedan guardados en la tablet.

## Qué hay aquí
| Carpeta / archivo | Qué es |
|---|---|
| `index.html`, `assets/` | La app (three.js r149 incluido, sin servidores externos) |
| `assets/modelo/recoevo_v3.glb` | El mismo modelo 3D del video, exportado de Blender |
| `assets/js/partes.js` | Texto de cada pieza (fuente: lista de materiales v3 del plan de fábrica) |
| `sw.js`, `manifest.webmanifest` | Funcionamiento sin conexión y «app» en la pantalla de inicio |
| `video/` | Videos del evento (16:9 y 9:16), subtítulos `.srt` y guion |
| `fuente/` | Scripts para regenerar el modelo y los videos (Blender 5.2 + Python) |

## Créditos y licencias
- Modelo, textos y video: equipo RECOEVO (Politécnico Grancolombiano, Proceso Administrativo, 2026).
- three.js (MIT), Lexend y Nunito (SIL OFL) — licencias en `assets/vendor` y `assets/fonts`.
- El prototipo v3 aún no está fabricado ni ensayado; las cifras del producto vienen del plan de fábrica v3.
