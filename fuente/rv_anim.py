# Animación de RECOEVO: uso en la cocina, rayos X, flotar, vista explosionada, rearmado y regreso al primer fotograma.
# Todo sale de un diccionario de tiempos (segundos) que se recalcula con los tiempos reales de la voz.
import math
import random
import bpy
from mathutils import Vector, Quaternion
from rv_util import (FPS, Pista, claves, suave, suave_sal, suave_ent, mezclar, mirar)
import rv_producto as RP

RAIZ = (0.05, -0.20, 0.0)    # sitio del equipo: frente al mesón, junto a la tabla de picar (donde se usa)
ELEVA = 0.14                 # cuánto flota

TIEMPOS = {
    'dur': 85.0,
    'tapa_abre': 19.0, 'cascaras': 19.9, 'tapa_cierra': 22.0,
    'rayosx_on': 22.6, 'pisadas_der': [23.4, 24.3, 25.2, 26.1],
    'pisada_izq': 28.0, 'rayosx_off': 30.6,
    'puerta_abre': 32.6, 'balde_sale': 33.7, 'balde_entra': 38.6, 'puerta_cierra': 39.6,
    'flota': 41.2, 'disuelve': [42.0, 45.0],
    'explota': 45.4,
    'grupos': [46.4, 50.4, 57.2, 64.3, 67.5],
    'etiquetas_fin': 71.6,
    'arma': 72.2,
    'aterriza': [77.6, 80.2],
    'regresa': [78.4, 81.8],
    'cierre_logo': [75.6, 82.6],
}

# desplazamientos de la vista explosionada (coordenadas del equipo), por formato
EXPLOTA = {
    'h': {
        'tapa': ((0, 0.02, 0.56), (0, 0, 0)), 'gabinete': ((0, 0.04, 0.42), (0, 0, 0)),
        'puerta': ((-0.44, -0.30, -0.02), (0, 0, -0.45)), 'balde': ((0, -0.34, -0.12), (0, 0, 0)),
        'base': ((0, 0.02, -0.20), (0, 0, 0)), 'patas': ((0, 0.02, -0.28), (0, 0, 0)),
        'pedal_der': ((0.32, -0.16, -0.14), (0, 0, 0)), 'pedal_izq': ((-0.30, -0.16, -0.16), (0, 0, 0)),
        'deposito': ((-0.42, 0.02, 0.02), (0, 0, 0.3)), 'camara': ((0, 0.0, 0.04), (0, 0, 0)),
        'seguro': ((0.30, -0.05, 0.14), (0, 0, 0)), 'peine': ((0, -0.22, -0.07), (0, 0, 0)),
        'eje': ((0, -0.13, -0.02), (0, 0, 0)), 'perilla': ((-0.24, -0.13, -0.02), (0, 0, 0)),
        'reten_izq': ((-0.075, -0.13, -0.02), (0, 0, 0)), 'reten_der': ((0.075, -0.13, -0.02), (0, 0, 0)),
        'pinon': ((0.17, -0.13, -0.02), (0, 0, 0)), 'cremallera': ((0.34, -0.10, -0.06), (0, 0, 0)),
    },
    'v': {
        'tapa': ((0, 0.02, 0.64), (0, 0, 0)), 'gabinete': ((0, 0.04, 0.47), (0, 0, 0)),
        'puerta': ((-0.25, -0.30, -0.07), (0, 0, -0.45)), 'balde': ((0, -0.34, -0.17), (0, 0, 0)),
        'base': ((0, 0.02, -0.27), (0, 0, 0)), 'patas': ((0, 0.02, -0.37), (0, 0, 0)),
        'pedal_der': ((0.19, -0.16, -0.21), (0, 0, 0)), 'pedal_izq': ((-0.19, -0.16, -0.23), (0, 0, 0)),
        'deposito': ((-0.27, 0.02, 0.05), (0, 0, 0.3)), 'camara': ((0, 0.0, 0.06), (0, 0, 0)),
        'seguro': ((0.20, -0.05, 0.18), (0, 0, 0)), 'peine': ((0, -0.22, -0.07), (0, 0, 0)),
        'eje': ((0, -0.13, 0.0), (0, 0, 0)), 'perilla': ((-0.17, -0.13, 0.0), (0, 0, 0)),
        'reten_izq': ((-0.06, -0.13, 0.0), (0, 0, 0)), 'reten_der': ((0.06, -0.13, 0.0), (0, 0, 0)),
        'pinon': ((0.12, -0.13, 0.0), (0, 0, 0)), 'cremallera': ((0.23, -0.10, -0.09), (0, 0, 0)),
    },
}
SUBE_EXTRA = {'h': 0.18, 'v': 0.26}   # el equipo sube un poco más mientras está despiezado (nada atraviesa el piso)
ORDEN = ['tapa', 'gabinete', 'puerta', 'balde', 'base', 'patas', 'pedal_der', 'pedal_izq', 'deposito', 'camara',
         'seguro', 'peine', 'eje', 'perilla', 'reten_izq', 'reten_der', 'pinon', 'cremallera']

ETIQUETAS = [
    # id, título, detalle, anclas, grupo (una por frase de «Por dentro»: 0 carcasa, 1 cremallera, 2 cuchillas, 3 tapa y seguro)
    ('gabinete', 'Gabinete de PP inyectado', '70 % plástico reciclado', ['A_gabinete'], 0),
    ('puerta', 'Puerta frontal', 'Cierre de doble acción para niños', ['A_puerta'], 0),
    ('balde', 'Balde de 10 L', 'Bolsa compostable: 1 por semana', ['A_balde'], 0),
    ('base', 'Base y bastidor de pedales', 'PP 70 % reciclado', ['A_base'], 0),
    ('patas', 'Patas antideslizantes', 'TPE', ['A_patas'], 0),
    ('pedal_der', 'Pedal derecho', 'Palanca 2:1 · tritura', ['A_pedal_der'], 1),
    ('cremallera', 'Cremallera de acero', '30 mm por pisada', ['A_cremallera'], 1),
    ('pinon', 'Piñón con trinquete', 'Gira el eje solo hacia adelante', ['A_pinon'], 1),
    ('eje', 'Eje inox con 13 cuchillas', 'Ø56 mm, acero templado', ['A_eje'], 2),
    ('peine', 'Peine fijo inox', '12 dedos: tiras de ≈5 mm', ['A_peine'], 2),
    ('camara', 'Cámara y tolva de corte', 'Boca de 12 × 10 cm', ['A_camara'], 2),
    ('retenes', 'Retenes y bujes', 'NBR y POM: sin fugas', ['A_reten_izq', 'A_reten_der'], 2),
    ('perilla', 'Perilla de reversa', 'Destraba el eje a mano', ['A_perilla'], 2),
    ('tapa', 'Tapa con junta EPDM', 'Sella el olor y aloja el filtro', ['A_tapa'], 3),
    ('filtro', 'Filtro de carbón activado', '60 g + válvula de una vía', ['A_filtro'], 3),
    ('seguro', 'Seguro de tapa', 'Tapa abierta: pedal bloqueado', ['A_seguro'], 3),
    ('pedal_izq', 'Pedal izquierdo', 'Suelta 40 mL de aserrín', ['A_pedal_izq'], 3),
    ('deposito', 'Depósito de aserrín 2 L', 'Con dosificador rotativo', ['A_deposito'], 3),
]


def f_(t):
    return int(round(t * FPS))


def claves_fn(obj, ruta, fn, t0, t1, nfot, indice=-1):
    """Claves en cada fotograma de [t0, t1] más un reposo a cada lado."""
    fs = sorted(set([0, nfot] + list(range(max(0, f_(t0) - 1), min(nfot, f_(t1) + 1) + 1))))
    for f in fs:
        v = fn(f / FPS)
        if indice >= 0:
            getattr(obj, ruta)[indice] = v
        else:
            setattr(obj, ruta, v)
        obj.keyframe_insert(ruta, index=indice, frame=f)


# ---------------------------------------------------------------- pedales, cremallera, eje
def pista_pedal(pisadas, bajar=0.30, sostener=0.12, subir=0.33):
    p = Pista(RP.ANG_REPOSO)
    for t in pisadas:
        p.a(t, t + bajar, RP.ANG_PISADO, suave)
        p.a(t + bajar + sostener, t + bajar + sostener + subir, RP.ANG_REPOSO, suave)
    return p


def dz_crem(theta):
    return RP.BRAZO_CREM * (math.sin(-theta) - math.sin(-RP.ANG_REPOSO))


def animar(P, T, aspecto, nfot):
    random.seed(21)
    raiz = P['raiz']
    raiz.location = RAIZ
    dur = T['dur']

    # ---- tapa y seguro
    claves(P['piv_tapa'], 'rotation_euler', Pista(0.0).a(T['tapa_abre'], T['tapa_abre'] + 0.9, math.radians(-80))
           .a(T['tapa_cierra'], T['tapa_cierra'] + 0.75, 0.0), nfot, indice=0)
    claves(P['corr_seguro'], 'location', Pista(0.0).a(T['tapa_abre'] + 0.25, T['tapa_abre'] + 0.55, -0.010)
           .a(T['tapa_cierra'] + 0.45, T['tapa_cierra'] + 0.7, 0.0), nfot, indice=2)

    # ---- pedal derecho → cremallera → piñón → eje (el trinquete solo arrastra al bajar)
    pd = pista_pedal(T['pisadas_der'])
    claves(P['piv_pedal_der'], 'rotation_euler', pd, nfot, indice=0)
    t0, t1 = T['pisadas_der'][0] - 0.1, T['pisadas_der'][-1] + 1.0
    claves_fn(P['corr_cremallera'], 'location', lambda t: dz_crem(pd.valor(t)), t0, t1, nfot, indice=2)
    claves_fn(P['rot_pinon'], 'rotation_euler', lambda t: -dz_crem(pd.valor(t)) / RP.R_PASO, t0, t1, nfot, indice=0)

    def giro_eje(t):
        g = 0.0
        for tp in T['pisadas_der']:
            if t >= tp:
                g += -dz_crem(pd.valor(min(t, tp + 0.30))) / RP.R_PASO if t < tp + 0.30 else RP.GIRO_PISADA
        return g
    for nombre in ('rot_eje', 'rot_trinquete', 'rot_perilla'):
        claves_fn(P[nombre], 'rotation_euler', giro_eje, t0, t1, nfot, indice=0)

    # ---- pedal izquierdo → dosificador rotativo (90°: una celda de 40 mL)
    pi_ = pista_pedal([T['pisada_izq']], bajar=0.32, sostener=0.25, subir=0.38)
    claves(P['piv_pedal_izq'], 'rotation_euler', pi_, nfot, indice=0)
    claves(P['rot_dosif'], 'rotation_euler', Pista(0.0).a(T['pisada_izq'], T['pisada_izq'] + 0.32, math.pi / 2), nfot, indice=0)

    # ---- puerta y balde
    claves(P['piv_puerta'], 'rotation_euler', Pista(0.0).a(T['puerta_abre'], T['puerta_abre'] + 1.0, math.radians(-100))
           .a(T['puerta_cierra'], T['puerta_cierra'] + 0.9, 0.0), nfot, indice=2)
    claves(P['corr_balde'], 'location', Pista(0.0).a(T['balde_sale'], T['balde_sale'] + 1.0, -0.15)
           .a(T['balde_entra'], T['balde_entra'] + 0.9, 0.0), nfot, indice=1)

    # ---- rayos X (los materiales con nodo 'fantasma')
    nivel = {'PP verde': 0.90, 'Logo blanco en relieve': 0.90, 'PP verde monte': 0.90, 'PP blanco': 0.90, 'PP reciclado grafito': 0.55, 'PP-GF30 gris': 0.62,
             'PP balde blanco': 0.6, 'Bolsa compostable': 0.55}
    for m in bpy.data.materials:
        n = m.node_tree.nodes.get('fantasma') if m.node_tree else None
        if n is None or m.name not in nivel:
            continue
        pista = Pista(0.0).a(T['rayosx_on'], T['rayosx_on'] + 0.6, nivel[m.name]).a(T['rayosx_off'], T['rayosx_off'] + 0.6, 0.0)
        for f in pista.fotogramas_activos(nfot):
            n.outputs[0].default_value = pista.valor(f / FPS)
            n.outputs[0].keyframe_insert('default_value', frame=f)

    cascaras_y_tiras(P, T, nfot)
    flotar_y_explotar(P, T, aspecto, nfot)


# ---------------------------------------------------------------- cáscaras, tiras y aserrín
def altura_monton(x, y):
    yb = -0.022
    u, v = x / 0.112, (y - yb) / 0.106
    z0 = RP.BALDE_Z[0] + 0.06
    return z0 + 0.035 * max(0.0, 1 - 0.55 * (u * u + v * v)) + 0.002


def cascaras_y_tiras(P, T, nfot):
    random.seed(4)
    boca = Vector((0, -0.065, 0))
    pis = T['pisadas_der']
    g = 3.0   # gravedad "de cine" (cámara lenta suave)
    for i, ob in enumerate(P['cascaras']):
        ts = T['cascaras'] + i * 0.24
        z_ini = 1.30
        reposo = Vector((random.uniform(-0.035, 0.035), boca.y + random.uniform(-0.022, 0.022), 0.405 + 0.008 * (i % 4)))
        caida = math.sqrt(2 * (z_ini - reposo.z) / g)
        ini = Vector((reposo.x * 0.4, reposo.y, z_ini))
        r0 = Vector((random.uniform(-3, 3), random.uniform(-3, 3), random.uniform(-3, 3)))
        r1 = Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-3, 3)))
        tc = pis[i % len(pis)] + 0.05   # se consume en esta pisada

        def pos(t, ts=ts, ini=ini, reposo=reposo, caida=caida, tc=tc):
            if t < ts:
                return tuple(ini)
            if t < ts + caida:
                k = ((t - ts) / caida) ** 2
                return tuple(ini.lerp(reposo, k))
            if t < tc:
                return tuple(reposo)
            k = suave((t - tc) / 0.35)
            return tuple(reposo.lerp(Vector((reposo.x, RP.EJE_Y, RP.EJE_Z + 0.01)), k))

        def esc(t, ts=ts, tc=tc):
            if t < ts:
                return (0.0, 0.0, 0.0)
            if t < tc:
                return (1.0, 1.0, 1.0)
            k = 1 - suave((t - tc) / 0.35)
            return (k, k, k)

        def rot(t, ts=ts, caida=caida, r0=r0, r1=r1):
            k = min(1.0, max(0.0, (t - ts) / caida))
            return tuple(r0.lerp(r1, suave_sal(k)))
        a, b = ts - 0.1, tc + 0.5
        claves_fn(ob, 'location', pos, a, b, nfot)
        claves_fn(ob, 'scale', esc, a, b, nfot)
        claves_fn(ob, 'rotation_euler', rot, a, b, nfot)

    # tiras de ≈5 mm que caen al balde en cada pisada
    ocultar = T['puerta_cierra'] + 1.2
    for k, ob in enumerate(P['tiras']):
        tp = pis[k % len(pis)] + 0.10 + random.uniform(0, 0.25)
        x0 = random.uniform(-0.045, 0.045)
        y0 = -0.065 + random.uniform(-0.02, 0.02)
        p0 = Vector((x0, y0, 0.300))
        p1 = Vector((x0 * 1.2 + random.uniform(-0.01, 0.01), y0 + random.uniform(-0.03, 0.03), 0))
        p1.z = altura_monton(p1.x, p1.y)
        caida = math.sqrt(2 * (p0.z - p1.z) / 6.0)
        r0 = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(0, 6)))
        r1 = Vector((0, 0, r0.z + random.uniform(-2, 2)))
        claves_fn(ob, 'location', lambda t, tp=tp, p0=p0, p1=p1, c=caida: tuple(p0.lerp(p1, min(1, max(0, (t - tp) / c)) ** 2)),
                  tp - 0.05, tp + caida + 0.05, nfot)
        claves_fn(ob, 'rotation_euler', lambda t, tp=tp, c=caida, r0=r0, r1=r1: tuple(r0.lerp(r1, min(1, max(0, (t - tp) / c)))),
                  tp - 0.05, tp + caida + 0.05, nfot)
        claves(ob, 'scale', Pista((0.0, 0.0, 0.0)).a(tp - 0.034, tp, (1.0, 1.0, 1.0)).a(ocultar, ocultar + 0.034, (0.0, 0.0, 0.0)), nfot)

    # granos de aserrín (una dosis de 40 mL) desde el tobogán del dosificador
    tz = T['pisada_izq'] + 0.25
    for k, ob in enumerate(P['granos']):
        tp = tz + k / len(P['granos']) * 0.55
        p0 = Vector((-0.098 + random.uniform(-0.014, 0.014), 0.084 + random.uniform(-0.012, 0.012), 0.292))
        p1 = Vector((p0.x * 0.9 + random.uniform(-0.02, 0.02), 0.06 + random.uniform(-0.03, 0.02), 0))
        p1.z = altura_monton(p1.x, p1.y) + random.uniform(0, 0.004)
        caida = math.sqrt(2 * (p0.z - p1.z) / 6.0)
        claves_fn(ob, 'location', lambda t, tp=tp, p0=p0, p1=p1, c=caida: tuple(p0.lerp(p1, min(1, max(0, (t - tp) / c)) ** 2)),
                  tp - 0.05, tp + caida + 0.05, nfot)
        ob.rotation_euler = (random.uniform(0, 3), random.uniform(0, 3), random.uniform(0, 3))
        claves(ob, 'scale', Pista((0.0, 0.0, 0.0)).a(tp - 0.034, tp, (1.0, 1.0, 1.0)).a(ocultar, ocultar + 0.034, (0.0, 0.0, 0.0)), nfot)


# ---------------------------------------------------------------- flotar, explotar y rearmar
def flotar_y_explotar(P, T, aspecto, nfot):
    raiz = P['raiz']
    t_fl, (t_at0, t_at1) = T['flota'], T['aterriza']

    def z_raiz(t):
        if t < t_fl:
            return 0.0
        sube = ELEVA * suave((t - t_fl) / 2.6)
        baja = suave((t - t_at0) / (t_at1 - t_at0)) if t > t_at0 else 0.0
        # vaivén suave mientras flota (vale 0 al empezar y al terminar)
        ventana = suave((t - t_fl - 1.5) / 2.0) * (1 - suave((t - (t_at0 - 2.0)) / 2.0))
        vaiven = 0.008 * math.sin(2 * math.pi * (t - t_fl) / 5.0) * ventana
        extra = SUBE_EXTRA[aspecto] * suave((t - T['explota']) / 2.4) * (1 - suave((t - T['arma'] - 0.8) / 2.4))
        return (sube + vaiven + extra) * (1 - baja)
    claves_fn(raiz, 'location', z_raiz, t_fl - 0.1, t_at1 + 0.1, nfot, indice=2)

    desp = EXPLOTA[aspecto]
    n = len(ORDEN)
    for i, nombre in enumerate(ORDEN):
        g = P['G_' + nombre]
        d, r = desp[nombre]
        s_ida = 0.12 * i
        s_vuelta = 0.12 * (n - 1 - i)
        te, ta = T['explota'] + s_ida, T['arma'] + s_vuelta
        claves(g, 'location', Pista((0.0, 0.0, 0.0)).a(te, te + 2.2, d).a(ta, ta + 2.0, (0.0, 0.0, 0.0)), nfot)
        if any(r):
            claves(g, 'rotation_euler', Pista((0.0, 0.0, 0.0)).a(te, te + 2.2, r).a(ta, ta + 2.0, (0.0, 0.0, 0.0)), nfot)
    # piezas internas que se separan un poco más
    te, ta = T['explota'] + 0.6, T['arma'] + 1.2
    for nombre, d in (('G_tapa_filtro', (0, 0, 0.085)), ('G_filtro', (0, 0, 0.045))):
        claves(P[nombre], 'location', Pista((0.0, 0.0, 0.0)).a(te, te + 2.0, d).a(ta, ta + 1.8, (0.0, 0.0, 0.0)), nfot)
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (1, -1), (-1, -1))):
        claves(P[f'G_pata{i}'], 'location', Pista((0.0, 0.0, 0.0)).a(te, te + 2.0, (sx * 0.035, sy * 0.035, 0))
               .a(ta, ta + 1.8, (0.0, 0.0, 0.0)), nfot)


# ---------------------------------------------------------------- cámara
def R(x, y, z):
    return (RAIZ[0] + x, RAIZ[1] + y, z)


def claves_camara(T, aspecto):
    """(t, ubicación, objetivo, lente h, lente v, f/, reposo, subir objetivo en vertical)."""
    H = (R(0.57, -1.95, 0.72), R(-0.27, 0.20, 0.47), 33, 31, 2.8)
    pd, pi_ = T['pisadas_der'], T['pisada_izq']
    E, A = T['explota'], T['arma']
    V = T.get('voz', {})
    t_p2 = V.get('p2a', (16.0, 0))[0]
    t_c = V.get('c1', (27.0, 0))[0]
    t_s1 = V.get('s1', (33.0, 0))[0]
    K = [
        (0.0, *H, True, 0.19),
        (t_p2 - 1.0, R(0.40, -1.75, 0.76), R(-0.30, 0.20, 0.52), 34, 31, 2.8, False, 0.17),     # acercamiento lento
        (t_p2 + 5.5, R(-0.25, -1.85, 0.98), R(-0.55, 0.80, 1.32), 36, 33, 2.8, False, 0.08),    # la ventana con la sábila: el campo
        (t_c + 0.5, R(0.34, -1.75, 0.84), R(-0.08, 0.22, 0.46), 34, 31, 2.8, False, 0.17),      # de vuelta al equipo en la cocina
        (t_s1 + 0.5, R(0.55, -1.20, 0.80), R(-0.02, 0.05, 0.38), 36, 33, 3.0, False, 0.08),     # «Por eso creamos Recoevo»
        (T['tapa_abre'] - 1.2, R(0.55, -1.00, 0.86), R(0.0, -0.02, 0.40), 38, 34, 3.2, False, 0.06),
        (T['cascaras'] + 0.5, R(0.30, -0.70, 1.15), R(0.0, -0.06, 0.44), 36, 32, 3.5, True, 0.0),
        (T['tapa_cierra'] + 0.6, R(0.34, -0.78, 1.02), R(0.0, -0.04, 0.38), 36, 32, 3.5, False, 0.0),
        (pd[0] + 0.3, R(0.80, -1.15, 0.62), R(0.02, -0.02, 0.27), 36, 31, 4.0, False, 0.03),
        (pd[-1] + 0.6, R(0.62, -1.22, 0.58), R(0.0, -0.02, 0.27), 36, 31, 4.0, False, 0.03),
        (pi_ + 0.2, R(-0.55, -1.12, 0.60), R(-0.04, -0.02, 0.28), 36, 31, 4.0, False, 0.03),
        (T['rayosx_off'] + 0.6, R(-0.15, -0.95, 0.52), R(0.0, -0.06, 0.24), 36, 30, 4.0, False, 0.03),
        (T['balde_sale'] + 0.8, R(0.22, -0.90, 0.50), R(0.0, -0.14, 0.21), 36, 30, 3.5, False, 0.03),
        (T['balde_entra'] - 0.5, R(0.36, -0.88, 0.52), R(0.0, -0.12, 0.21), 36, 30, 3.5, False, 0.03),
        (T['flota'], R(0.55, -1.30, 0.74), R(0.0, 0.0, 0.34), 36, 32, 4.0, False, 0.05),
        (T['disuelve'][1], R(0.62, -1.55, 0.88), R(0.0, 0.0, 0.45), 38, 32, 5.6, False, 0.0),
        (E + 3.0, R(0.85, -2.05, 1.10), R(0.0, -0.05, 0.76), 27, 46, 11, False, 0.06),
        ((E + A) / 2, R(0.0, -2.30, 1.00), R(0.0, -0.05, 0.76), 27, 46, 11, False, 0.06),
        (A - 0.4, R(-0.82, -2.00, 1.10), R(0.0, -0.05, 0.76), 27, 46, 11, False, 0.06),
        (A + 3.4, R(-0.10, -1.75, 0.90), R(0.0, 0.0, 0.44), 36, 32, 8, False, 0.05),
        (T['aterriza'][0], R(0.62, -1.80, 0.78), R(-0.18, 0.12, 0.50), 34, 31, 4.0, False, 0.18),
        (T['regresa'][1] + 0.4, R(0.72, -2.12, 0.74), R(-0.30, 0.22, 0.58), 32, 30, 2.8, False, 0.19),   # cierre: acercamiento lento
        (T['dur'] - 0.8, *H, True, 0.19),
        (T['dur'], *H, True, 0.19),
    ]
    return K


def hermite(p0, p1, m0, m1, u):
    u2, u3 = u * u, u * u * u
    return (2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * m0 + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * m1


def valor_camara(K, t, aspecto):
    def vec(k):
        _, loc, tgt, lh, lv, f, _r, dzv = k
        tg = Vector(tgt) + (Vector((0, 0, dzv)) if aspecto == 'v' else Vector())
        return [Vector(loc), tg, float(lh if aspecto == 'h' else lv), float(f)]
    for i in range(len(K) - 1):
        if K[i][0] <= t <= K[i + 1][0]:
            break
    else:
        i = len(K) - 2
    t0, t1 = K[i][0], K[i + 1][0]
    u = 0.0 if t1 <= t0 else (t - t0) / (t1 - t0)
    out = []
    for c in range(4):
        p0, p1 = vec(K[i])[c], vec(K[i + 1])[c]

        def tangente(j):
            if K[j][6] or j == 0 or j == len(K) - 1:
                return p0 * 0
            a, b = vec(K[j - 1])[c], vec(K[j + 1])[c]
            return (b - a) / (K[j + 1][0] - K[j - 1][0]) * (t1 - t0)
        out.append(hermite(p0, p1, tangente(i), tangente(i + 1), u))
    return out


def camara(nombre, aspecto, T, nfot, col):
    cd = bpy.data.cameras.new(nombre)
    cd.sensor_fit = 'AUTO'
    cd.sensor_width = 36
    cd.dof.use_dof = True
    cam = bpy.data.objects.new(nombre, cd)
    col.objects.link(cam)
    cam.rotation_mode = 'QUATERNION'
    K = claves_camara(T, aspecto)
    q_prev = None
    for f in range(nfot + 1):
        loc, tgt, lente, fst = valor_camara(K, f / FPS, aspecto)
        q = mirar(loc, tgt)
        if q_prev is not None and q.dot(q_prev) < 0:
            q.negate()
        q_prev = q
        cam.location = loc
        cam.rotation_quaternion = q
        cd.lens = lente
        cd.dof.aperture_fstop = fst
        cd.dof.focus_distance = (Vector(tgt) - Vector(loc)).length
        cam.keyframe_insert('location', frame=f)
        cam.keyframe_insert('rotation_quaternion', frame=f)
        cd.keyframe_insert('lens', frame=f)
        cd.dof.keyframe_insert('aperture_fstop', frame=f)
        cd.dof.keyframe_insert('focus_distance', frame=f)
    return cam
