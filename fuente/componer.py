# Compone el video final: une los pases de Blender (cocina / estudio), dibuja etiquetas, subtítulos y cierre con el logo,
# y codifica con ffmpeg del sistema (H.264, yuv420p, rango TV, BT.709). El último fotograma es copia exacta del primero.
# Uso (Python de tts-env):
#   python componer.py --aspecto h --frames ../frames/h --anclas ../blend/anclas_h.json --subs ../audio/subs.json
#                      --audio ../audio/mezcla.wav --salida ../salida/RECOEVO_16x9.mp4
#   python componer.py ... --foto 1650 --png prueba.png      (un solo fotograma, para revisar)
# Paraleliza por procesos (todos los núcleos menos uno) y registra el hardware usado.
import os
import sys
import json
import math
import time
import argparse
import subprocess
import multiprocessing as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MARCA = r'G:\Mi unidad\Universidad\02-Semestres\03. Tercer semestre (2027-01)\01. Proceso Administrativo\04. Recoevo\03_RECOEVO_MARCA_Y_WEB'
F_TIT = os.path.join(MARCA, '_Fuentes_editables', 'fonts', 'Lexend[wght].ttf')
F_TXT = os.path.join(MARCA, '_Fuentes_editables', 'fonts', 'Nunito[wght].ttf')
LOGO = os.path.join(MARCA, 'Logo', 'PNG_transparente', 'RECOEVO_logo_horizontal_color.png')
MONTE = (21, 71, 52)
EVO = (14, 154, 72)
TINTA = (28, 39, 33)
CREMA = (251, 245, 232)

G = {}   # estado global de cada proceso


def fuente(ruta, tam, peso):
    try:
        f = ImageFont.truetype(ruta, tam)
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
        return f
    except Exception:
        return ImageFont.truetype('segoeui.ttf', tam)


def suave(x):
    x = max(0.0, min(1.0, x))
    return x * x * x * (x * (x * 6 - 15) + 10)


def caja_redonda(w, h, r, color, sombra=True, borde=None):
    pad = 24 if sombra else 0
    im = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    if sombra:
        s = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(s).rounded_rectangle((pad, pad + 6, pad + w, pad + h + 6), r, fill=(0, 0, 0, 60))
        im = Image.alpha_composite(im, s.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=color, outline=borde, width=1 if borde else 0)
    return im, pad


def tarjeta_etiqueta(titulo, detalle, escala):
    ft = fuente(F_TIT, int(29 * escala), 640)
    fd = fuente(F_TXT, int(22 * escala), 650)
    px, py = int(18 * escala), int(12 * escala)
    wt = ft.getbbox(titulo)[2]
    wd = fd.getbbox(detalle)[2] if detalle else 0
    ht = int(36 * escala)
    hd = int(28 * escala) if detalle else 0
    w, h = max(wt, wd) + 2 * px, ht + hd + 2 * py
    im, pad = caja_redonda(w, h, int(14 * escala), (255, 255, 255, 236), True, (21, 71, 52, 40))
    d = ImageDraw.Draw(im)
    d.text((pad + px, pad + py - int(2 * escala)), titulo, font=ft, fill=MONTE + (255,))
    if detalle:
        d.text((pad + px, pad + py + ht - int(4 * escala)), detalle, font=fd, fill=(60, 74, 66, 255))
    return im, pad, w, h


def envolver(texto, f, ancho):
    pal, lineas, act = texto.split(), [], ''
    for p in pal:
        prueba = (act + ' ' + p).strip()
        if f.getbbox(prueba)[2] <= ancho or not act:
            act = prueba
        else:
            lineas.append(act)
            act = p
    if act:
        lineas.append(act)
    return lineas


def init(cfg):
    G.update(cfg)
    with open(cfg['anclas'], encoding='utf-8') as fh:
        A = json.load(fh)
    G['A'] = A
    G['T'] = A['tiempos']
    esc = 1.0 if cfg['aspecto'] == 'h' else 1.05
    G['tarjetas'] = {e['id']: tarjeta_etiqueta(e['titulo'], e['detalle'], esc) for e in A['etiquetas']}
    G['subs'] = []
    if cfg.get('subs') and os.path.exists(cfg['subs']):
        with open(cfg['subs'], encoding='utf-8') as fh:
            G['subs'] = json.load(fh)
    G['f_sub'] = fuente(F_TXT, 34 if cfg['aspecto'] == 'h' else 40, 700)
    # tarjeta de cierre: logo + llamado a la acción + QR al prototipo interactivo
    G['cierre'] = tarjeta_cierre(cfg['aspecto'])
    # tarjetas de cifras (problemáticas, consecuencia, comparación de mercado)
    G['cifras'] = []
    if cfg.get('tarjetas') and os.path.exists(cfg['tarjetas']):
        for c in json.load(open(cfg['tarjetas'], encoding='utf-8')):
            img = tarjeta_comparacion(cfg['aspecto']) if c.get('tipo') == 'comparacion' else tarjeta_cifra(c, cfg['aspecto'])
            G['cifras'].append((c, img))


QR = r'C:\Users\willi\recoevo-video-evento\audio\qr_prototipo.png'
URL_CORTA = 'whafonsecav.github.io/Prototipo-Recoevo'


def tarjeta_cifra(c, aspecto):
    h_ = aspecto == 'h'
    fg = fuente(F_TIT, 60 if h_ else 64, 760)
    ft = fuente(F_TXT, 26 if h_ else 30, 750)
    fp = fuente(F_TXT, 19 if h_ else 22, 650)
    ancho = 540 if h_ else 860
    lineas = envolver(c['texto'], ft, ancho - 48)
    pie = envolver(c.get('pie', ''), fp, ancho - 48) if c.get('pie') else []
    alto = 24 + 70 + len(lineas) * int(ft.size * 1.25) + (10 + len(pie) * int(fp.size * 1.3) if pie else 0) + 20
    im, pad = caja_redonda(ancho, alto, 24, (255, 255, 255, 228), True)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((pad, pad + 20, pad + 6, pad + 20 + 64), 3, fill=EVO + (255,))
    d.text((pad + 26, pad + 14), c['grande'], font=fg, fill=MONTE + (255,))
    y = pad + 24 + 66
    for linea in lineas:
        d.text((pad + 26, y), linea, font=ft, fill=TINTA + (255,))
        y += int(ft.size * 1.25)
    y += 8
    for linea in pie:
        d.text((pad + 26, y), linea, font=fp, fill=(86, 104, 94, 255))
        y += int(fp.size * 1.3)
    return im, pad, ancho, alto


def tarjeta_comparacion(aspecto):
    h_ = aspecto == 'h'
    ancho = 700 if h_ else 900
    ft = fuente(F_TIT, 30 if h_ else 34, 700)
    fn = fuente(F_TXT, 24 if h_ else 28, 750)
    fd = fuente(F_TXT, 18 if h_ else 21, 650)
    fpz = fuente(F_TIT, 27 if h_ else 31, 700)
    filas = [('Triturador eléctrico importado', '+ luz y filtros', '$1,3 – 1,7 M', False),
             ('Compostera de patio', 'necesita patio', '$410 – 660 mil', False),
             ('Caneca con pedal 44 L', 'solo guarda', '$204 mil', False),
             ('RECOEVO v3', 'tritura · sin luz · trae 5 bolsas', '$199.900', True)]
    alto_f = 66 if h_ else 76
    alto = 30 + 48 + len(filas) * alto_f + 44
    im, pad = caja_redonda(ancho, alto, 24, (255, 255, 255, 232), True)
    d = ImageDraw.Draw(im)
    d.text((pad + 26, pad + 22), 'Tratar los orgánicos en casa cuesta…', font=ft, fill=MONTE + (255,))
    y = pad + 30 + 48
    for nombre, nota, precio, nuestro in filas:
        if nuestro:
            d.rounded_rectangle((pad + 14, y - 6, pad + ancho - 14, y + alto_f - 10), 14, fill=EVO + (255,))
        col, col2 = ((255, 255, 255, 255), (230, 245, 235, 255)) if nuestro else (TINTA + (255,), (96, 112, 104, 255))
        d.text((pad + 28, y), nombre, font=fn, fill=col)
        d.text((pad + 28, y + int(fn.size * 1.15)), nota, font=fd, fill=col2)
        wp = fpz.getbbox(precio)[2]
        d.text((pad + ancho - 30 - wp, y + 4), precio, font=fpz, fill=col if nuestro else MONTE + (255,))
        y += alto_f
    d.text((pad + 26, y + 6), 'Precios de lista en Colombia, oct-2026 (fabricantes, Falabella, Homecenter)', font=fd,
           fill=(110, 124, 116, 255))
    return im, pad, ancho, alto


def tarjeta_cierre(aspecto):
    h_ = aspecto == 'h'
    lw = 420 if h_ else 560
    logo = Image.open(LOGO).convert('RGBA')
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    qs = 190 if h_ else 230
    qr = Image.open(QR).convert('RGBA').resize((qs, qs), Image.NEAREST)
    f1 = fuente(F_TIT, 38 if h_ else 44, 720)
    f2 = fuente(F_TXT, 24 if h_ else 28, 700)
    f3 = fuente(F_TXT, 19 if h_ else 22, 700)
    l1 = 'Súmate a esta iniciativa'
    l2 = '$199.900 · IVA incluido · sin cables · sin olores'
    l3 = 'Explora el prototipo'
    fe = fuente(F_TIT, 36 if h_ else 42, 720)             # eslogan de la marca: «Menos relleno, más vida.»
    e1, e2 = 'Menos relleno, ', 'más vida.'
    banda = int(fe.size * 1.9)
    texto_w = max(lw, f1.getbbox(l1)[2], f2.getbbox(l2)[2])
    ancho = texto_w + qs + 100
    alto_sup = max(logo.height + 22 + 54 + 40, qs + 50) + 24
    alto = alto_sup + banda
    im, pad = caja_redonda(ancho, alto, 30, (255, 255, 255, 236), True)
    d = ImageDraw.Draw(im)
    im.alpha_composite(logo, (pad + 30, pad + 20))
    y = pad + 20 + logo.height + 14
    d.text((pad + 30, y), l1, font=f1, fill=MONTE + (255,))
    d.text((pad + 30, y + int(f1.size * 1.3)), l2, font=f2, fill=(70, 86, 78, 255))
    xq = pad + ancho - qs - 30
    im.alpha_composite(qr, (xq, pad + 22))
    d.text((xq + (qs - f3.getbbox(l3)[2]) // 2, pad + 26 + qs), l3, font=f3, fill=MONTE + (255,))
    # banda Verde Monte con el eslogan («más vida.» en Verde Brote), debajo del logo completo
    d.rounded_rectangle((pad, pad + alto_sup, pad + ancho, pad + alto), 30, fill=MONTE + (255,))
    d.rectangle((pad, pad + alto_sup, pad + ancho, pad + alto_sup + 30), fill=MONTE + (255,))
    w1, w2 = fe.getbbox(e1)[2], fe.getbbox(e2)[2]
    xe = pad + (ancho - w1 - w2) // 2
    ye = pad + alto_sup + (banda - fe.size) // 2 - 4
    d.text((xe, ye), e1, font=fe, fill=(255, 255, 255, 255))
    d.text((xe + w1, ye), e2, font=fe, fill=(164, 214, 94, 255))
    return im, pad, ancho, alto


def cifras(lienzo, f):
    t = f / G['A']['fps']
    W = G['A']['w']
    h_ = G['aspecto'] == 'h'
    y0 = 64 if h_ else 112
    ocupado = []
    for c, (im, pad, w, hh) in G['cifras']:
        a = suave((t - c['ini']) / 0.45) * (1 - suave((t - c['fin']) / 0.45))
        if a <= 0.003:
            continue
        x = (70 if h_ else (W - w) // 2) - int(28 * (1 - suave((t - c['ini']) / 0.45)))
        y = y0 + sum(o + 18 for o in ocupado)
        ocupado.append(hh)
        capa = im.copy()
        capa.putalpha(capa.getchannel('A').point(lambda v: int(v * a)))
        lienzo.alpha_composite(capa, (x - pad, int(y) - pad))


def leer(pase, f):
    ruta = os.path.join(G['frames'], pase, f'f{f:05d}.png')
    if not os.path.exists(ruta):
        # vista previa con fotogramas sueltos: el más cercano disponible
        d = os.path.join(G['frames'], pase)
        cand = sorted(int(n[1:6]) for n in os.listdir(d) if n.startswith('f') and n.endswith('.png')) if os.path.isdir(d) else []
        if not cand:
            return None
        ff = min(cand, key=lambda c: abs(c - f))
        ruta = os.path.join(d, f'f{ff:05d}.png')
    im = Image.open(ruta).convert('RGB')
    if im.size != (G['A']['w'], G['A']['h']):
        im = im.resize((G['A']['w'], G['A']['h']), Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def mascara(t0, t1, t, centro, W, H, invertir=False):
    """Radial: el estudio entra desde los bordes hacia el equipo (y al volver, la cocina sale del equipo hacia afuera)."""
    p = suave((t - t0) / (t1 - t0))
    if invertir:
        p = 1 - p
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot(xx - centro[0], yy - centro[1]) / math.hypot(W, H) * 1.6
    umbral = 1.25 - 1.6 * p
    a = np.clip((r - umbral) / 0.32 + 0.5, 0, 1)
    a = a * a * (3 - 2 * a)
    return a[..., None], p


def base(f):
    T = G['T']
    t = f / G['A']['fps']
    d0, d1 = T['disuelve']
    r0, r1 = T['regresa']
    if t < d0 or t > r1:
        return leer('cocina', f)
    if d1 < t < r0:
        return leer('estudio', f)
    c = G['A']['anclas']['A_centro'][f]
    W, H = G['A']['w'], G['A']['h']
    k, e = leer('cocina', f), leer('estudio', f)
    if k is None or e is None:
        return k if e is None else e
    a, p = mascara(d0, d1, t, c, W, H) if t <= d1 else mascara(r0, r1, t, c, W, H, invertir=True)
    img = k * (1 - a) + e * a
    # un leve resplandor en el borde de la transición
    brillo = 4 * a * (1 - a)
    img = img + brillo * 22.0 * math.sin(math.pi * p)
    return np.clip(img, 0, 255)


def etiquetas(lienzo, f):
    T, A = G['T'], G['A']
    t = f / A['fps']
    grupos = T['grupos'] + [T['etiquetas_fin']]
    W, H = A['w'], A['h']
    horizontal = G['aspecto'] == 'h'
    centro_x = A['anclas']['A_centro'][f][0]
    d = ImageDraw.Draw(lienzo)
    visibles = []
    for e in A['etiquetas']:
        g = e['grupo']
        t_in, t_out = grupos[g], grupos[g + 1]
        orden = [x['id'] for x in A['etiquetas'] if x['grupo'] == g].index(e['id'])
        a_in = suave((t - t_in - 0.18 * orden) / 0.45)
        a_out = 1 - suave((t - t_out + 0.35) / 0.4)
        alfa = a_in * a_out
        if alfa <= 0.003:
            continue
        pts = [A['anclas'][n][f] for n in e['anclas']]
        if any(p[2] <= 0 for p in pts):
            continue
        visibles.append((e, alfa, pts))
    # disposición por lado, sin solaparse
    for lado in ('izq', 'der'):
        grupo = [v for v in visibles if (v[2][0][0] < centro_x) == (lado == 'izq')]
        grupo.sort(key=lambda v: v[2][0][1])
        y_min = 70 if horizontal else 110
        y_max = H - (150 if horizontal else 400)
        ys = []
        for e, alfa, pts in grupo:
            im, pad, w, h = G['tarjetas'][e['id']]
            y = min(max(pts[0][1] - h / 2, y_min), y_max - h)
            if ys and y < ys[-1] + 14:
                y = ys[-1] + 14
            ys.append(y + h)
        # si se pasó del borde inferior, subir todo
        if ys and ys[-1] > y_max:
            sube = ys[-1] - y_max
            ys = [y - sube for y in ys]
        for (e, alfa, pts), y_fin in zip(grupo, ys):
            im, pad, w, h = G['tarjetas'][e['id']]
            y = int(y_fin - h)
            if horizontal:
                x = int((min(centro_x - 330, min(p[0] for p in pts) - 90) - w) if lado == 'izq'
                        else max(centro_x + 330, max(p[0] for p in pts) + 90))
                x = max(50, min(W - 50 - w, x))
            else:
                x = 34 if lado == 'izq' else W - 34 - w
            capa = im.copy()
            if alfa < 1:
                capa.putalpha(capa.getchannel('A').point(lambda v: int(v * alfa)))
            lienzo.alpha_composite(capa, (x - pad, y - pad))
            ex = x + w if lado == 'izq' else x
            ey = y + h / 2
            for p in pts:
                col = MONTE + (int(220 * alfa),)
                d.line((ex, ey, p[0], p[1]), fill=col, width=3)
                r = 8
                d.ellipse((p[0] - r - 3, p[1] - r - 3, p[0] + r + 3, p[1] + r + 3), fill=(255, 255, 255, int(235 * alfa)))
                d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=EVO + (int(255 * alfa),))


def subtitulos(lienzo, f):
    t = f / G['A']['fps']
    W, H = G['A']['w'], G['A']['h']
    horizontal = G['aspecto'] == 'h'
    for s in G['subs']:
        if s['ini'] - 0.1 <= t <= s['fin'] + 0.1:
            alfa = min(suave((t - s['ini'] + 0.1) / 0.18), 1 - suave((t - s['fin']) / 0.18 + 0.45))
            if alfa <= 0.01:
                continue
            ft = G['f_sub']
            lineas = envolver(s['texto'], ft, 1560 if horizontal else 960)
            alto_l = int(ft.size * 1.32)
            ancho = max(ft.getbbox(l)[2] for l in lineas)
            px, py = 26, 12
            w, h = ancho + 2 * px, alto_l * len(lineas) + 2 * py - 6
            x = (W - w) // 2
            y = H - (40 if horizontal else 220) - h
            capa = Image.new('RGBA', lienzo.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(capa)
            d.rounded_rectangle((x, y, x + w, y + h), 14, fill=TINTA + (int(150 * alfa),))
            for i, l in enumerate(lineas):
                lw = ft.getbbox(l)[2]
                d.text(((W - lw) // 2, y + py + i * alto_l - 4), l, font=ft, fill=(255, 255, 255, int(255 * alfa)))
            lienzo.alpha_composite(capa)
            break


def cierre(lienzo, f):
    t = f / G['A']['fps']
    c0, c1 = G['T']['cierre_logo']
    alfa = suave((t - c0) / 0.7) * (1 - suave((t - c1) / 0.8))
    if alfa <= 0.003:
        return
    card, pad, w, h = G['cierre']
    W = G['A']['w']
    x, y = ((70, 64) if G['aspecto'] == 'h' else ((W - w) // 2, 112))
    capa = card.copy()
    capa.putalpha(capa.getchannel('A').point(lambda v: int(v * alfa)))
    lienzo.alpha_composite(capa, (x - pad, y - pad))


def componer(f):
    nfot = G['A']['nfot']
    ff = 0 if f >= nfot else f          # el último fotograma es el primero: bucle perfecto
    img = base(ff)
    lienzo = Image.fromarray(img.astype(np.uint8)).convert('RGBA')
    etiquetas(lienzo, ff)
    cifras(lienzo, ff)
    subtitulos(lienzo, ff)
    cierre(lienzo, ff)
    return np.asarray(lienzo.convert('RGB')).tobytes()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--aspecto', required=True)
    p.add_argument('--frames', required=True)
    p.add_argument('--anclas', required=True)
    p.add_argument('--subs', default=None)
    p.add_argument('--tarjetas', default=None)
    p.add_argument('--audio', default=None)
    p.add_argument('--salida', default=None)
    p.add_argument('--foto', type=int, default=None)
    p.add_argument('--png', default=None)
    p.add_argument('--paso', type=int, default=1, help='vista previa: un fotograma de cada N')
    p.add_argument('--qp', type=int, default=17, help='cuantizador constante: el primer y el último fotograma (iguales) se codifican idénticos')
    A = p.parse_args()
    cfg = dict(aspecto=A.aspecto, frames=os.path.abspath(A.frames), anclas=os.path.abspath(A.anclas),
               subs=os.path.abspath(A.subs) if A.subs else None,
               tarjetas=os.path.abspath(A.tarjetas) if A.tarjetas else None)
    if A.foto is not None:
        init(cfg)
        W, H = G['A']['w'], G['A']['h']
        Image.frombytes('RGB', (W, H), componer(A.foto)).save(A.png)
        print('[componer] foto', A.foto, '→', A.png)
        return
    init(cfg)
    W, H, nfot, fps = G['A']['w'], G['A']['h'], G['A']['nfot'], G['A']['fps']
    hilos = os.cpu_count() or 2
    try:
        import psutil
        ram = f'{psutil.virtual_memory().available / 2**30:.1f} GB libres'
    except Exception:
        ram = 'RAM no medida'
    trab = max(1, hilos - 1)
    print(f'[hardware] {hilos} hilos lógicos · {ram} · compongo con {trab} procesos + ffmpeg (x264 usa sus propios hilos)', flush=True)
    fotos = list(range(0, nfot + 1, A.paso))
    if fotos[-1] != nfot:
        fotos.append(nfot)
    fps_out = fps / A.paso
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', f'{fps_out}', '-i', '-']
    if A.audio:
        cmd += ['-i', A.audio]
    ultimo = len(fotos) - 1
    cmd += ['-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
            '-c:v', 'libx264', '-preset', 'slow', '-qp', str(A.qp), '-tune', 'film',
            '-x264-params', f'keyint={ultimo}:min-keyint={ultimo}:scenecut=0:colorprim=bt709:transfer=bt709:colormatrix=bt709:range=tv',
            '-force_key_frames', f'expr:eq(n,0)+eq(n,{ultimo})',
            '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709']
    if A.audio:
        cmd += ['-c:a', 'aac', '-b:a', '256k', '-ar', '48000']   # la mezcla dura exactamente lo mismo que el video
    cmd += ['-movflags', '+faststart', A.salida]
    t0 = time.time()
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with mp.Pool(trab, initializer=init, initargs=(cfg,)) as pool:
        for i, datos in enumerate(pool.imap(componer, fotos, chunksize=4)):
            ff.stdin.write(datos)
            if i % 150 == 0:
                print(f'  {i}/{len(fotos)} fotogramas ({time.time() - t0:.0f} s)', flush=True)
    ff.stdin.close()
    ff.wait()
    print(f'[componer] listo {A.salida} en {time.time() - t0:.0f} s', flush=True)


if __name__ == '__main__':
    mp.freeze_support()
    main()
