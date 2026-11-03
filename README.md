# RECOEVO · Web oficial

Triturador de restos de comida para la cocina, **a pedal y sin electricidad**, con filtro de carbón activado. *Menos relleno, más vida.*
Precio al público: **$199.900 IVA incluido**.

**Menú principal (el QR del póster lleva aquí):** https://whafonsecav.github.io/Prototipo-Recoevo/

## Secciones

| # | Sección | Dirección |
|---|---|---|
| 1 | Ver el prototipo en 3D | https://whafonsecav.github.io/Prototipo-Recoevo/prototipo/ |
| 2 | Video pitch del equipo | https://whafonsecav.github.io/Prototipo-Recoevo/video-pitch/ |
| 3 | Video del prototipo explicado | https://whafonsecav.github.io/Prototipo-Recoevo/video-prototipo/ |
| 4 | Estudio de campo: resultados de las encuestas | https://whafonsecav.github.io/Prototipo-Recoevo/estudio-campo/ |
| 5 | Videos del evento | https://whafonsecav.github.io/Prototipo-Recoevo/videos/ |

Cada página tiene un botón fijo **«← Menú»** para volver.

## Prototipo en 3D: cómo se usa
- **Un dedo** (o clic izquierdo): girar.
- **Dos dedos**: pellizcar para acercar o alejar justo donde están los dedos, y arrastrar para mover la vista
  arriba, abajo y a los lados. Con mouse: la rueda acerca hacia el puntero y el clic derecho (o Shift) arrastra la vista.
- **Tocar una pieza** (o un punto verde): se abre su ficha. La cámara va al centro de esa pieza y se acerca según su
  tamaño (las piezas chicas, como el filtro, quedan grandes); la ficha trae además una imagen de la pieza sola.
  Con la ficha abierta se puede seguir girando, acercando y moviendo la vista.
- **Separar piezas**: el producto se despieza; **Armar** lo vuelve a juntar.
- **Pieza por pieza**: recorre las 18 fichas con «Anterior» y «Siguiente».
- **Cómo funciona**: recorrido animado en 4 pasos (tapa, pedal derecho, pedal izquierdo opcional, balde).
- **⟲**: vuelve a la vista inicial. Si nadie toca la pantalla durante 35 s, gira solo (modo vitrina).

Las fichas salen de la lista de materiales y de la hoja «5 Producto» del plan de fábrica: 32 × 34 × 52 cm, ≈ 5 kg,
balde de 10 L para cualquier bolsa compostable del supermercado (RECOEVO no vende bolsas), filtro de 60 g de carbón activado
(dura ≈ 6 meses) y compartimento de 2 L para material seco **opcional** (papel, hojas secas, aserrín o nada).

## Qué hay aquí

| Carpeta / archivo | Qué es |
|---|---|
| `index.html` | Menú principal |
| `prototipo/` | Visor 3D (three.js r149 incluido, sin servidores externos) |
| `video-pitch/`, `video-prototipo/`, `videos/` | Páginas de los videos |
| `estudio-campo/` | Presentación del estudio de campo (Villa Rosita, Usme) |
| `assets/css/` | `marca.css` (menú y páginas) y `prototipo.css` (visor) |
| `assets/js/prototipo/` | Visor: `partes.js` (fichas de cada pieza), `glb.js`, `controles.js`, `app.js` |
| `assets/modelo/recoevo.glb` | El producto en 3D, exportado de Blender |
| `assets/img/`, `assets/fonts/`, `assets/vendor/` | Logo, íconos, miniaturas del menú, tipografías Lexend y Nunito, three.js |
| `video/` | Videos comprimidos (H.264, inicio rápido) y sus portadas en `video/portadas/` |
| `fuente/` | Scripts de Blender que generan el modelo 3D y el video del evento |
| `sw.js`, `manifest.webmanifest` | Funcionamiento sin conexión y «app» en la pantalla de inicio |
| `404.html`, `.nojekyll` | Página de error amable y publicación directa en GitHub Pages |

El video del prototipo explicado se publica como `video/RECOEVO_prototipo_explicado.mp4`; mientras no esté, su página muestra «¡Muy pronto!».
Ningún archivo pasa de 95 MB (límite de GitHub).

## Privacidad del estudio de campo
- Los participantes aparecen solo con un código (E01–E08); sus perfiles se dejaron generales.
- No se publican los audios de las entrevistas ni la foto de las autorizaciones firmadas.
- Las caras de terceros en los videos de la calle están difuminadas.

## Créditos y licencias
- Producto, textos y videos: equipo RECOEVO (Politécnico Grancolombiano, Proceso Administrativo, 2026).
- three.js (MIT), Lexend y Nunito (SIL OFL): licencias en `assets/vendor` y `assets/fonts`. Mapa satelital: Esri World Imagery.
- RECOEVO todavía no se fabrica: las medidas y los materiales vienen del plan de fábrica.
