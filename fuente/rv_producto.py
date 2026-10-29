# RECOEVO v3 (prototipo del plan de fábrica del 29-oct-2026): triturador doméstico a pedal, 32 × 34 × 52 cm, ≈5 kg.
# Geometría alineada con la lista de materiales v3 (01_RECOEVO_PLAN_DE_FABRICA_2026-10-29/Herramientas_modelo/build/data.py)
# y la hoja de ingeniería (palanca 2:1: 24 cm al pie y 12 cm a la cremallera; pie 60 mm → cremallera 30 mm → ≈143° de eje).
# Origen = centro del piso bajo el equipo; frente hacia -Y; eje de cuchillas paralelo a X. Medidas en metros.
import math
import random
import bpy
import bmesh
from mathutils import Vector, Matrix
from rv_util import (hexcol, material, material_atributo, objeto, bisel, bm_caja, caja, pts_rect_redondeado,
                     bm_prisma, bm_tina, bm_cilindro, cilindro, bm_toro, bm_perfil_eje_x, booleana, aplicar_mod,
                     borrar, vacio, colgar)

W, D = 0.32, 0.34
Y_FR = -D / 2
Z_PLINTO = (0.013, 0.100)       # base y bastidor de pedales (PP 70 % reciclado): zócalo visible
Z_PISO = 0.112                  # plataforma del balde
Z_TOP = 0.470                   # cubierta superior del gabinete
Z_TAPA = 0.512
PUERTA_Z = (0.113, 0.302)       # hueco de la puerta frontal
BALDE_Z = (0.115, 0.297)        # balde de 10 L
EJE_Y, EJE_Z = -0.060, 0.365
EJE_X = (-0.103, 0.147)         # barra hexagonal inox 12 mm de 0,25 m
X_PIN = 0.143                   # plano del piñón (placa de 8 mm) y de la cremallera (4 mm)
R_PASO = 0.012                  # piñón M2 Z12
CARRERA_CREM = 0.030            # 30 mm por pisada
GIRO_PISADA = CARRERA_CREM / R_PASO        # ≈2,5 rad ≈ 143°
PIV_PEDAL = (0.040, 0.040)      # (y, z) del eje de los pedales (acero Ø8)
BRAZO_PIE, BRAZO_CREM = 0.24, 0.12
ANG_REPOSO = math.radians(-12.0)          # pedal levantado al frente
ANG_PISADO = math.radians(2.4)            # 0,24·(sin12°+sin2,4°) ≈ 60 mm de recorrido del pie
PASO_CUCHILLA = 0.0025 + 0.0056           # 13 cuchillas de 2,5 mm + 12 separadores POM de 5,6 mm


def materiales():
    M = {}
    M['verde'] = material('PP verde', hexcol('#0E9A48'), 0.46, bump=0.08, escala_bump=900, fantasma=True)          # Verde Evo
    M['monte'] = material('PP verde monte', hexcol('#154734'), 0.42, bump=0.08, escala_bump=900, fantasma=True)   # Verde Monte
    M['amarillo'] = material('PP amarillo', hexcol('#F2B227'), 0.42)                                               # Amarillo Cosecha
    M['crema'] = material('PP crema', hexcol('#FBF5E8'), 0.4)
    M['logo'] = material('Logo blanco en relieve', hexcol('#F7F7F3'), 0.30, coat=0.2, fantasma=True)   # logo horizontal blanco de la marca, en relieve
    M['blanco'] = material('PP blanco', hexcol('#F2F1EC'), 0.36, bump=0.06, escala_bump=900, fantasma=True)
    M['piezas'] = material('PP-GF piezas blancas', hexcol('#F4F3EE'), 0.35)
    M['base'] = material('PP reciclado grafito', hexcol('#1F2723'), 0.55, bump=0.12, escala_bump=700, fantasma=True)
    M['camara'] = material('PP-GF30 gris', hexcol('#6A716C'), 0.48, bump=0.1, escala_bump=800, fantasma=True)
    M['pedal_v'] = material('PP-GF30 verde', hexcol('#154734'), 0.5, bump=0.1, escala_bump=800, fantasma=True)
    M['pedal_b'] = material('PP-GF30 amarillo', hexcol('#F2B227'), 0.5, bump=0.1, escala_bump=800, fantasma=True)
    M['inox'] = material('Inox 304', hexcol('#CDD0D2'), 0.17, metal=1.0, aniso=0.35)
    M['cuchilla'] = material('Acero 3Cr13 templado', hexcol('#B9BDC0'), 0.22, metal=1.0, aniso=0.2)
    M['acero'] = material('Acero', hexcol('#8C9194'), 0.30, metal=1.0)
    M['zinc'] = material('Acero zincado', hexcol('#B7BEC6'), 0.26, metal=1.0, bump=0.15, escala_bump=1500)
    M['pom'] = material('POM blanco', hexcol('#F2F0E7'), 0.28)
    M['pagf'] = material('PA-GF negro', hexcol('#202322'), 0.45)
    M['caucho'] = material('NBR EPDM TPE', hexcol('#161616'), 0.78, bump=0.25, escala_bump=500)
    M['balde'] = material('PP balde blanco', hexcol('#F2F1EC'), 0.40, fantasma=True)
    M['bolsa'] = material('Bolsa compostable', hexcol('#A4D65E'), 0.55, transmision=0.3, thin=True, bump=0.3,
                          escala_bump=60, fantasma=True)
    M['cordon'] = material('Cordon bolsa', hexcol('#5E9935'), 0.6)
    M['aserrin'] = material('Aserrin', hexcol('#C79D69'), 0.85, bump=0.6, escala_bump=300, ruido_color=0.35,
                            escala_color=180)
    M['tanque'] = material('PP natural translucido', hexcol('#EEEAE0'), 0.45, alpha=0.40)
    M['carbon'] = material('Malla con carbon activado', hexcol('#1C1E1E'), 0.92, bump=0.9, escala_bump=350)
    M['silicona'] = material('Silicona gris', hexcol('#5A605C'), 0.55)
    M['tiras'] = material_atributo('Tiras organicas', 0.6, bump=0.4)
    M['banano'] = material('Cascara banano', hexcol('#E2C13A'), 0.5, ruido_color=0.45, escala_color=25,
                           color2=hexcol('#8A6A22'))
    M['naranja_c'] = material('Cascara naranja', hexcol('#F08A1C'), 0.45, bump=0.5, escala_bump=250)
    M['huevo'] = material('Cascara huevo', hexcol('#E9D9C0'), 0.5)
    M['papa'] = material('Cascara papa', hexcol('#9C7449'), 0.7, ruido_color=0.4, escala_color=40)
    M['aguacate'] = material('Cascara aguacate', hexcol('#2F3B1E'), 0.55, bump=0.6, escala_bump=200)
    return M


# ---------------------------------------------------------------- perfiles 2D
def perfil_cuchilla(rr=0.020, rt=0.028, dientes=3, n=36):
    """Cuchilla de gancho Ø56: tres dientes en diente de sierra con la punta socavada."""
    pts = []
    S = 2 * math.pi / dientes
    for k in range(dientes):
        a0 = k * S
        for i in range(n):
            f = i / n * 0.85
            pts.append((rr + (rt - rr) * (f / 0.85) ** 1.3, a0 + f * S))
        pts.append((rt, a0 + 0.85 * S))
        pts.append((rt - 0.0028, a0 + 0.815 * S))
        pts.append((rr + 0.0012, a0 + 0.90 * S))
        pts.append((rr, a0 + 0.96 * S))
    return [(r * math.cos(a), r * math.sin(a)) for r, a in pts]


def perfil_engranaje(z=12, rp=R_PASO, m=0.002):
    ra, rf = rp + m, rp - 1.25 * m
    pts = []
    for k in range(z):
        a, p = 2 * math.pi * k / z, 2 * math.pi / z
        for f, r in ((0.02, rf), (0.20, rf), (0.36, ra), (0.54, ra), (0.70, rf), (0.98, rf)):
            pts.append((r * math.cos(a + f * p), r * math.sin(a + f * p)))
    return pts


def perfil_trinquete(z=16, r0=0.0085, r1=0.0118):
    pts = []
    for k in range(z):
        a, p = 2 * math.pi * k / z, 2 * math.pi / z
        pts.append((r0 * math.cos(a), r0 * math.sin(a)))
        pts.append((r1 * math.cos(a + 0.92 * p), r1 * math.sin(a + 0.92 * p)))
    return pts


def mover_yz(pts, y0, z0, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    return [(y0 + x * c - y * s, z0 + x * s + y * c) for x, y in pts]


def bm_losa_xz(sx, sz, grosor, r, cx, cz, y0, seg=8):
    """Losa redondeada en el plano XZ (puerta, junta) desde y0 hacia +Y."""
    bm = bm_prisma(pts_rect_redondeado(sx, sz, r, seg), 0, grosor)
    for v in bm.verts:
        x, y, z = v.co
        v.co = Vector((x + cx, y0 + z, y + cz))
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.normal_update()
    return bm


def bm_aro(sx, sy, r, grosor_pared, z0, z1, cx=0.0, cy=0.0, seg=8):
    """Marco (rectángulo redondeado hueco) entre z0 y z1."""
    ext = pts_rect_redondeado(sx, sy, r, seg, cx, cy)
    inn = pts_rect_redondeado(sx - 2 * grosor_pared, sy - 2 * grosor_pared, max(0.001, r - grosor_pared), seg, cx, cy)
    bm = bmesh.new()
    n = len(ext)
    e0 = [bm.verts.new((x, y, z0)) for x, y in ext]
    e1 = [bm.verts.new((x, y, z1)) for x, y in ext]
    i0 = [bm.verts.new((x, y, z0)) for x, y in inn]
    i1 = [bm.verts.new((x, y, z1)) for x, y in inn]
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((e0[k], e0[j], e1[j], e1[k]))
        bm.faces.new((i0[j], i0[k], i1[k], i1[j]))
        bm.faces.new((e1[k], e1[j], i1[j], i1[k]))
        bm.faces.new((e0[j], e0[k], i0[k], i0[j]))
    bm.normal_update()
    return bm


# ---------------------------------------------------------------- construcción
def construir(col, M, fuente_logo):
    random.seed(7)
    P = {}
    raiz = vacio('RECOEVO', (0, 0, 0), col, tam=0.1)
    P['raiz'] = raiz

    def grupo(nombre, padre=None):
        g = vacio('G_' + nombre, (0, 0, 0), col, padre=padre or raiz, tam=0.03)
        P['G_' + nombre] = g
        return g

    def ancla(nombre, c, g):
        P['A_' + nombre] = vacio('A_' + nombre, c, col, padre=g, tam=0.01)

    def piv(nombre, c, g):
        P[nombre] = vacio(nombre, c, col, padre=g, tam=0.02)
        return P[nombre]

    def h(ob, padre):
        colgar(ob, padre)
        return ob

    def cortar(ob, bms):
        for bm in bms:
            c = objeto('_c', bm, None, col, suave=False)
            booleana(ob, c)
            borrar(c)

    # ---------------- patas antideslizantes (TPE, 4)
    g = grupo('patas')
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (1, -1), (-1, -1))):
        pg = grupo(f'pata{i}', g)
        h(cilindro(f'Pata TPE {i}', 0.018, 0.013, (sx * 0.128, sy * 0.138, 0.0065), M['caucho'], b=0.0025), pg)
    ancla('patas', (0.128, -0.138, 0.006), g)

    # ---------------- base y bastidor de pedales (PP 70 % reciclado, con nervios)
    g = grupo('base')
    pl = objeto('Base', bm_prisma(pts_rect_redondeado(W + 0.006, D + 0.006, 0.039, 12), *Z_PLINTO), M['base'], col)
    bisel(pl, 0.004, 3)
    aplicar_mod(pl, 'Bisel')
    cortar(pl, [bm_caja(0.030, 0.06, 0.070, (0.126, Y_FR, 0.061)), bm_caja(0.030, 0.06, 0.070, (-0.126, Y_FR, 0.061)),
                bm_prisma(pts_rect_redondeado(W - 0.010, D - 0.010, 0.03, 10), Z_PLINTO[0] + 0.004, Z_PLINTO[1] + 0.01)])
    h(pl, g)
    h(caja('Plataforma del balde', W - 0.012, D - 0.014, 0.004, (0, 0, Z_PISO - 0.002), M['base'], b=0.001), g)
    for x in (-0.11, -0.055, 0.0, 0.055, 0.11):          # nervios
        h(caja('Nervio', 0.003, D - 0.03, Z_PISO - Z_PLINTO[0] - 0.008, (x, 0.0, (Z_PISO + Z_PLINTO[0]) / 2 - 0.002),
               M['base'], b=0.0005), g)
    for x in (-0.150, 0.150):                               # soportes del eje de pedales
        h(caja('Soporte eje pedales', 0.008, 0.026, 0.040, (x, PIV_PEDAL[0], 0.036), M['base'], b=0.0015), g)
    h(cilindro('Eje de pedales Ø8', 0.004, 0.300, (0, PIV_PEDAL[0], PIV_PEDAL[1]), M['acero'], eje='X'), g)
    ancla('base', (-0.163, -0.10, 0.065), g)

    # ---------------- pedales (PP-GF30): palanca con pivote atrás, 24 cm al pie y 12 cm a la cremallera
    for lado, x0, x1, mp in (('der', 0.040, 0.136, M['pedal_v']), ('izq', -0.136, -0.062, M['pedal_b'])):
        g = grupo('pedal_' + lado)
        pv = piv('piv_pedal_' + lado, (0, PIV_PEDAL[0], PIV_PEDAL[1]), g)
        cx, w = (x0 + x1) / 2, x1 - x0
        y_pie = PIV_PEDAL[0] - BRAZO_PIE
        xb = 0.128 if lado == 'der' else -0.128          # brazo pasa por la ranura de la esquina
        zc = PIV_PEDAL[1] + 0.006
        h(caja(f'Pedal {lado}', w, 0.064, 0.012, (cx, y_pie, zc + 0.004), mp, b=0.0045), pv)
        for k in range(6):
            h(caja('Estria', w - 0.014, 0.004, 0.0022, (cx, y_pie - 0.024 + k * 0.0096, zc + 0.0108), mp, b=0.0009), pv)
        h(caja(f'Brazo pedal {lado}', 0.016, BRAZO_PIE - 0.02, 0.012, (xb, PIV_PEDAL[0] - (BRAZO_PIE - 0.02) / 2, zc),
               mp, b=0.002), pv)
        h(caja('Union brazo', abs(xb - cx) + 0.02, 0.020, 0.010, ((xb + cx) / 2, y_pie + 0.02, zc), mp, b=0.002), pv)
        h(cilindro('Buje pedal', 0.008, 0.022, (xb, PIV_PEDAL[0], PIV_PEDAL[1]), mp, eje='X', b=0.001), pv)
        if lado == 'der':
            h(caja('Oreja cremallera', 0.022, 0.016, 0.014, (X_PIN - 0.004, PIV_PEDAL[0] - BRAZO_CREM, zc), mp, b=0.002), pv)
        else:
            h(caja('Oreja dosificador', 0.022, 0.016, 0.014, (-0.146, 0.010, zc), mp, b=0.002), pv)
        ancla('pedal_' + lado, (cx, y_pie, zc + 0.012), pv)   # sigue al pedal (reposo levantado)

    # ---------------- gabinete (PP inyectado, 70 % reciclado, logo en relieve)
    g = grupo('gabinete')
    gb = objeto('Gabinete', bm_prisma(pts_rect_redondeado(W, D, 0.036, 12), Z_PLINTO[1], Z_TOP), M['verde'], col)
    bisel(gb, 0.007, 4, 60)
    aplicar_mod(gb, 'Bisel')
    cortar(gb, [
        bm_prisma(pts_rect_redondeado(W - 0.005, D - 0.005, 0.0335, 12), Z_PLINTO[1] - 0.01, Z_TOP - 0.004),  # hueco (pared 2,5 mm)
        bm_caja(0.276, 0.05, PUERTA_Z[1] - PUERTA_Z[0], (0, Y_FR, sum(PUERTA_Z) / 2)),                       # puerta
        bm_caja(0.120, 0.100, 0.06, (0, -0.065, Z_TOP)),                                                    # boca 12 × 10 cm
        bm_prisma(pts_rect_redondeado(0.070, 0.090, 0.012, 6, -0.097, 0.084), Z_TOP - 0.03, Z_TOP + 0.03),  # recarga de aserrín
        bm_cilindro(0.0245, 0.03, 48, eje='X', c=(-0.160, EJE_Y, EJE_Z)),                                   # perilla de reversa
    ])
    h(gb, g)
    logo = logo_relieve(fuente_logo, M['logo'], col, ancho=0.205, z=0.386)
    h(logo, g)
    P['logo'] = logo
    tap = objeto('Tapita de recarga', bm_prisma(pts_rect_redondeado(0.068, 0.088, 0.012, 6, -0.097, 0.084),
                                               Z_TOP - 0.004, Z_TOP - 0.0005), M['crema'], col)
    bisel(tap, 0.0015, 2)
    h(tap, g)
    for x in (-0.11, 0.11):   # bisagras de la tapa
        h(cilindro('Bisagra tapa', 0.0055, 0.04, (x, D / 2 - 0.003, Z_TOP + 0.002), M['monte'], eje='X', b=0.001), g)
    ancla('gabinete', (0.158, -0.02, 0.24), g)

    # ---------------- puerta frontal (PP virgen) con cierre de doble acción y junta
    g = grupo('puerta')
    bp = piv('piv_puerta', (-0.1375, Y_FR, 0.2), g)
    zc = sum(PUERTA_Z) / 2
    pu = objeto('Puerta frontal', bm_losa_xz(0.2725, PUERTA_Z[1] - PUERTA_Z[0] - 0.003, 0.011, 0.012, 0, zc, Y_FR - 0.0008),
                M['blanco'], col)
    bisel(pu, 0.0028, 3)
    h(pu, bp)
    h(caja('Tirador puerta', 0.016, 0.014, 0.110, (0.112, Y_FR - 0.006, zc - 0.005), M['monte'], b=0.0065), bp)
    h(caja('Cierre niños', 0.030, 0.008, 0.014, (0.112, Y_FR - 0.004, PUERTA_Z[1] - 0.020), M['amarillo'], b=0.0035), bp)
    h(caja('Botón cierre', 0.010, 0.005, 0.007, (0.104, Y_FR - 0.0085, PUERTA_Z[1] - 0.020), M['piezas'], b=0.0018), bp)
    jt = objeto('Junta EPDM puerta', bm_losa_xz(0.258, PUERTA_Z[1] - PUERTA_Z[0] - 0.018, 0.003, 0.008, 0, zc, Y_FR + 0.010),
                M['caucho'], col)
    cortar(jt, [bm_caja(0.248, 0.02, PUERTA_Z[1] - PUERTA_Z[0] - 0.028, (0, Y_FR + 0.011, zc))])
    h(jt, bp)
    ancla('puerta', (0.07, Y_FR - 0.012, 0.15), g)

    # ---------------- balde extraíble 10 L con asa, aro y bolsa compostable con cordón
    g = grupo('balde')
    cor = piv('corr_balde', (0, 0, 0), g)
    yb = -0.022
    z0, z1 = BALDE_Z
    tub = objeto('Balde 10 L', bm_tina(pts_rect_redondeado(0.236, 0.226, 0.03, 8, 0, yb),
                                        pts_rect_redondeado(0.256, 0.246, 0.035, 8, 0, yb), z0, z1), M['balde'], col)
    so = tub.modifiers.new('Grosor', 'SOLIDIFY')
    so.thickness, so.offset = 0.0025, 1.0
    h(tub, cor)
    aro = objeto('Aro de la bolsa', bm_aro(0.270, 0.260, 0.040, 0.008, z1 - 0.004, z1 + 0.004, 0, yb), M['monte'], col)
    bisel(aro, 0.0018, 2)
    h(aro, cor)
    h(caja('Asa balde', 0.12, 0.016, 0.014, (0, yb - 0.131, z1 - 0.028), M['monte'], b=0.0065), cor)
    bolsa = objeto('Bolsa compostable', bm_tina(pts_rect_redondeado(0.231, 0.221, 0.028, 8, 0, yb),
                                                 pts_rect_redondeado(0.251, 0.241, 0.033, 8, 0, yb), z0 + 0.003, z1 + 0.002),
                   M['bolsa'], col)
    tx = bpy.data.textures.new('ArrugasBolsa', 'CLOUDS')
    tx.noise_scale = 0.03
    sb = bolsa.modifiers.new('Sub', 'SUBSURF')
    sb.levels = sb.render_levels = 2
    dsp = bolsa.modifiers.new('Arrugas', 'DISPLACE')
    dsp.texture, dsp.strength = tx, 0.0025
    h(bolsa, cor)
    dob = objeto('Doblez de la bolsa', bm_tina(pts_rect_redondeado(0.276, 0.266, 0.042, 8, 0, yb),
                                              pts_rect_redondeado(0.272, 0.262, 0.041, 8, 0, yb), z1 - 0.040, z1 + 0.004, False),
                 M['bolsa'], col)
    s2 = dob.modifiers.new('Sub', 'SUBSURF')
    s2.levels = s2.render_levels = 2
    d2 = dob.modifiers.new('Arrugas', 'DISPLACE')
    d2.texture, d2.strength = tx, 0.004
    h(dob, cor)
    h(objeto('Cordón', bm_toro(0.133, 0.0016, 96, 8, c=(0, yb, z1 - 0.036)), M['cordon'], col), cor)
    P['cordon'] = None
    h(montoncito('Contenido del balde', (0, yb), 0.112, 0.106, z0 + 0.06, z0 + 0.095, 520, M['tiras'], col), cor)
    ancla('balde', (0.11, yb - 0.124, 0.22), g)

    # ---------------- cámara y tolva de corte (PP + 30 % fibra de vidrio) con bujes POM
    g = grupo('camara')
    du = objeto('Camara y tolva de corte', bm_aro(0.120, 0.104, 0.006, 0.004, 0.306, Z_TOP - 0.004, 0, -0.065, 4),
                M['camara'], col)
    cortar(du, [bm_cilindro(0.0072, 0.03, 32, eje='X', c=(x, EJE_Y, EJE_Z)) for x in (-0.058, 0.058)])
    bisel(du, 0.0012, 2)
    h(du, g)
    h(objeto('Labio tolva', bm_aro(0.132, 0.112, 0.008, 0.007, Z_TOP - 0.010, Z_TOP - 0.004, 0, -0.065, 4), M['camara'], col), g)
    for x in (-0.0585, 0.0585):
        h(cilindro('Buje POM', 0.011, 0.007, (x, EJE_Y, EJE_Z), M['pom'], eje='X', b=0.0008), g)
    ancla('camara', (0.060, -0.118, 0.43), g)

    # ---------------- eje hexagonal inox 12 mm con 13 cuchillas y 12 separadores POM
    g = grupo('eje')
    rot = piv('rot_eje', (0, EJE_Y, EJE_Z), g)
    hexa = [(0.00693 * math.cos(math.radians(30 + 60 * k)), 0.00693 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    ob = objeto('Eje hexagonal', bm_perfil_eje_x(mover_yz(hexa, EJE_Y, EJE_Z), *EJE_X), M['inox'], col)
    bisel(ob, 0.0006, 2)
    h(ob, rot)
    perfil = perfil_cuchilla()
    x00 = -6 * PASO_CUCHILLA
    for i in range(13):
        x = x00 + i * PASO_CUCHILLA
        bm = bm_perfil_eje_x(mover_yz(perfil, EJE_Y, EJE_Z, rot=i * math.radians(360 / 13 * 3)), x - 0.00125, x + 0.00125)
        ob = objeto(f'Cuchilla {i + 1:02d}', bm, M['cuchilla'], col, angulo=25)
        bisel(ob, 0.0004, 1, 30)
        h(ob, rot)
        if i < 12:
            h(cilindro(f'Separador POM {i + 1}', 0.018, 0.0056, (x + PASO_CUCHILLA / 2, EJE_Y, EJE_Z), M['pom'], eje='X',
                       seg=40, b=0.0005), rot)
    ancla('eje', (0.030, EJE_Y - 0.030, EJE_Z + 0.012), g)

    # perilla de reversa (pieza pequeña inyectada) en el extremo izquierdo del eje
    g = grupo('perilla')
    rper = piv('rot_perilla', (0, EJE_Y, EJE_Z), g)
    h(cilindro('Cubo perilla', 0.0095, 0.050, (-0.125, EJE_Y, EJE_Z), M['amarillo'], eje='X', b=0.001), rper)
    h(cilindro('Perilla de reversa', 0.0205, 0.013, (-0.1555, EJE_Y, EJE_Z), M['amarillo'], eje='X', seg=64, b=0.003), rper)
    for k in range(12):
        a = 2 * math.pi * k / 12
        h(caja('Estria perilla', 0.011, 0.004, 0.004, (-0.1555, EJE_Y + 0.0205 * math.cos(a), EJE_Z + 0.0205 * math.sin(a)),
               M['amarillo'], b=0.0012), rper)
    ancla('perilla', (-0.162, EJE_Y, EJE_Z + 0.016), g)

    # ---------------- peine fijo (inox 304 de 2 mm, 12 dedos de 5 mm en huecos de 5,6 mm)
    g = grupo('peine')
    h(caja('Peine base', 0.104, 0.002, 0.050, (0, -0.110, EJE_Z - 0.010), M['inox'], b=0.0005), g)
    for k in range(12):
        x = x00 + PASO_CUCHILLA / 2 + k * PASO_CUCHILLA
        y0, y1 = -0.110, EJE_Y - 0.0185
        h(caja('Dedo del peine', 0.005, y1 - y0, 0.002, (x, (y0 + y1) / 2, EJE_Z - 0.003), M['inox'], b=0.0005), g)
    ancla('peine', (0.050, -0.108, EJE_Z - 0.030), g)

    # ---------------- retenes de labio NBR 12 × 22 × 5 (2)
    for lado, x in (('izq', -0.0645), ('der', 0.0645)):
        g = grupo('reten_' + lado)
        ob = objeto('Reten NBR ' + lado, bm_toro(0.0085, 0.0026, 48, 14, eje='X', c=(x, EJE_Y, EJE_Z)), M['caucho'], col)
        h(ob, g)
        ancla('reten_' + lado, (x, EJE_Y, EJE_Z + 0.011), g)

    # ---------------- piñón M2 Z12 (placa A36 de 8 mm, zincado) y trinquete (rueda PA-GF + 2 uñas de acero)
    g = grupo('pinon')
    rp = piv('rot_pinon', (0, EJE_Y, EJE_Z), g)
    ob = objeto('Piñón M2 Z12', bm_perfil_eje_x(mover_yz(perfil_engranaje(), EJE_Y, EJE_Z), X_PIN - 0.004, X_PIN + 0.004),
                M['zinc'], col, angulo=25)
    bisel(ob, 0.0003, 1, 30)
    h(ob, rp)
    for k in range(2):
        a = math.pi * k
        h(caja('Uña trinquete', 0.0015, 0.009, 0.003, (X_PIN - 0.0055, EJE_Y + 0.0105 * math.cos(a + 0.5),
                                                       EJE_Z + 0.0105 * math.sin(a + 0.5)), M['acero'], b=0.0004), rp)
    rt = objeto('Rueda de trinquete', bm_perfil_eje_x(mover_yz(perfil_trinquete(), EJE_Y, EJE_Z), X_PIN - 0.014, X_PIN - 0.0065),
                M['pagf'], col, angulo=25)
    h(rt, piv('rot_trinquete', (0, EJE_Y, EJE_Z), g))   # va fija al eje: gira con él
    P['rueda_trinquete'] = rt
    ancla('pinon', (X_PIN + 0.004, EJE_Y + 0.004, EJE_Z + 0.016), g)

    # ---------------- cremallera (acero 4 mm, una sola pieza del pedal al piñón) + guías + resorte
    g = grupo('cremallera')
    cr = piv('corr_cremallera', (0, 0, 0), g)
    yp = EJE_Y - R_PASO
    paso = math.pi * 0.002
    zt, zb = EJE_Z + 0.045, PIV_PEDAL[1] + 0.006 + BRAZO_CREM * math.sin(-ANG_REPOSO) - 0.004
    perf = [(yp - 0.016, zb), (yp - 0.016, zt), (yp - 0.0025, zt)]
    z = zt - 0.004
    while z - paso > EJE_Z - 0.060:
        perf += [(yp - 0.0025, z), (yp + 0.002, z - 0.24 * paso), (yp + 0.002, z - 0.50 * paso), (yp - 0.0025, z - 0.74 * paso)]
        z -= paso
    perf += [(yp - 0.0025, z), (yp - 0.0065, z - 0.012), (yp - 0.0065, zb)]
    ob = objeto('Cremallera de acero', bm_perfil_eje_x(perf, X_PIN - 0.002, X_PIN + 0.002), M['acero'], col, angulo=25)
    h(ob, cr)
    h(cilindro('Pasador cremallera', 0.003, 0.016, (X_PIN - 0.002, yp - 0.010, zb + 0.004), M['acero'], eje='X'), cr)
    for zg in (0.17, EJE_Z - 0.065):
        h(caja('Guía cremallera', 0.010, 0.024, 0.018, (X_PIN + 0.007, yp - 0.010, zg), M['camara'], b=0.0015), g)
    hel = bpy.data.curves.new('ResorteRetorno', 'CURVE')
    hel.dimensions = '3D'
    sp = hel.splines.new('POLY')
    n = 220
    sp.points.add(n - 1)
    for i in range(n):
        a = i / n * 2 * math.pi * 16
        sp.points[i].co = (X_PIN + 0.0085 + 0.0045 * math.cos(a), yp - 0.012 + 0.0045 * math.sin(a), 0.19 + 0.08 * i / n, 1)
    hel.bevel_depth = 0.0007
    res = bpy.data.objects.new('Resorte de retorno', hel)
    col.objects.link(res)
    res.data.materials.append(M['acero'])
    h(res, g)
    ancla('cremallera', (X_PIN + 0.003, yp - 0.012, 0.24), g)

    # ---------------- depósito de aserrín 2 L (PP natural) + dosificador rotativo de 40 mL + varilla
    g = grupo('deposito')
    tq = objeto('Deposito de aserrin', bm_prisma(pts_rect_redondeado(0.110, 0.148, 0.012, 6, -0.098, 0.084), 0.336, Z_TOP - 0.005),
                M['tanque'], col)
    bisel(tq, 0.002, 2)
    h(tq, g)
    h(objeto('Aserrín del depósito', bm_prisma(pts_rect_redondeado(0.104, 0.142, 0.010, 6, -0.098, 0.084), 0.338, 0.425),
             M['aserrin'], col), g)
    h(caja('Caja del dosificador', 0.090, 0.050, 0.034, (-0.098, 0.084, 0.318), M['piezas'], b=0.003), g)
    rd = piv('rot_dosif', (-0.098, 0.084, 0.318), g)
    h(cilindro('Rotor dosificador', 0.0155, 0.092, (-0.098, 0.084, 0.318), M['pom'], eje='X', b=0.0008), rd)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        h(caja('Paleta', 0.090, 0.0025, 0.010, (-0.098, 0.084 + 0.0165 * math.cos(a), 0.318 + 0.0165 * math.sin(a)),
               M['pom'], b=0.0005), rd)
    h(caja('Manivela', 0.005, 0.028, 0.006, (-0.146, 0.072, 0.318), M['acero'], b=0.0008), rd)
    h(caja('Tobogán', 0.040, 0.034, 0.012, (-0.098, 0.084, 0.297), M['piezas'], b=0.002), g)
    h(cilindro('Varilla del dosificador', 0.0022, 0.255, (-0.148, 0.020, 0.188), M['acero']), g)
    ancla('deposito', (-0.150, 0.03, 0.42), g)

    # ---------------- seguro de tapa (pasador que bloquea la cremallera con la tapa abierta)
    g = grupo('seguro')
    sc = piv('corr_seguro', (0, 0, 0), g)
    h(cilindro('Pasador del seguro', 0.0032, 0.040, (X_PIN, yp - 0.008, EJE_Z + 0.073), M['piezas'], b=0.0006), sc)
    h(caja('Leva del seguro', 0.018, 0.012, 0.005, (X_PIN - 0.004, yp - 0.008, Z_TOP - 0.008), M['piezas'], b=0.0012), sc)
    ancla('seguro', (X_PIN, yp - 0.008, Z_TOP - 0.006), g)

    # ---------------- tapa con alojamiento del filtro, junta EPDM perimetral, filtro de 60 g y válvula Ø20
    g = grupo('tapa')
    bt = piv('piv_tapa', (0, D / 2 - 0.003, Z_TOP + 0.002), g)
    tp = objeto('Tapa', bm_prisma(pts_rect_redondeado(W + 0.002, D + 0.002, 0.037, 12), Z_TOP + 0.0012, Z_TAPA), M['monte'], col)
    bisel(tp, 0.010, 5, 60)
    h(tp, bt)
    h(caja('Labio de apertura', 0.10, 0.012, 0.007, (0, Y_FR - 0.003, Z_TOP + 0.009), M['monte'], b=0.0032), bt)
    jt = objeto('Junta EPDM tapa', bm_aro(W - 0.014, D - 0.014, 0.030, 0.006, Z_TOP - 0.0015, Z_TOP + 0.0015), M['caucho'], col)
    h(jt, bt)
    fg = vacio('G_filtro', (0, 0, 0), col, padre=bt, tam=0.01)
    P['G_filtro'] = fg
    h(caja('Filtro de carbón 60 g', 0.072, 0.058, 0.018, (0, 0.072, Z_TAPA - 0.012), M['carbon'], b=0.006), fg)
    tf = vacio('G_tapa_filtro', (0, 0, 0), col, padre=bt, tam=0.01)
    P['G_tapa_filtro'] = tf
    h(cilindro('Tapa del filtro', 0.042, 0.004, (0, 0.072, Z_TAPA + 0.001), M['crema'], seg=72, b=0.0015), tf)
    for k in range(7):
        h(caja('Ranura', 0.060 - abs(k - 3) * 0.010, 0.0028, 0.002, (0, 0.072 - 0.021 + k * 0.007, Z_TAPA + 0.0031),
               M['carbon'], b=0.0006), tf)
    h(cilindro('Válvula de una vía Ø20', 0.010, 0.004, (0.098, 0.115, Z_TAPA + 0.0008), M['silicona'], b=0.0012), bt)
    ancla('tapa', (0.11, -0.06, Z_TAPA + 0.002), g)
    ancla('filtro', (0.030, 0.072, Z_TAPA + 0.004), tf)

    # ---------------- cáscaras, tiras y granos (escena de uso)
    P['cascaras'] = cascaras(col, M)
    P['tiras'] = particulas('Tira', 34, col, M['tiras'], (0.0048, 0.022, 0.0012))
    P['granos'] = particulas('Grano', 70, col, M['aserrin'], (0.003, 0.003, 0.002))
    for ob in P['cascaras'] + P['tiras'] + P['granos']:
        ob.parent = raiz
    return P


def logo_relieve(svg, mat, col, ancho, z):
    """Logo de la marca (isotipo + logotipo, SVG monocromo) convertido en relieve de 1,2 mm sobre el frente.
    Si no hay SVG, usa el nombre en texto."""
    antes = set(bpy.data.objects)
    if svg and svg.lower().endswith('.svg'):
        import addon_utils
        addon_utils.enable('io_curve_svg', default_set=True)
        bpy.ops.import_curve.svg(filepath=svg)
        curvas = [o for o in bpy.data.objects if o not in antes and o.type == 'CURVE']
    else:
        cu = bpy.data.curves.new('LogoRECOEVO', 'FONT')
        cu.body = 'recoevo'
        if svg:
            cu.font = bpy.data.fonts.load(svg)
        ob = bpy.data.objects.new('Logo', cu)
        col.objects.link(ob)
        curvas = [ob]
    # mallas planas en XY, unidas y llevadas al tamaño
    mallas = []
    for c in curvas:
        c.data.extrude = 0.0
        c.data.dimensions = '2D'
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(c.evaluated_get(dg))
        me.transform(c.matrix_world)
        mallas.append(me)
        for cc in c.users_collection:
            cc.objects.unlink(c)
    bm = bmesh.new()
    for me in mallas:
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    s = ancho / (max(xs) - min(xs))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    for v in bm.verts:
        v.co = Vector(((v.co.x - cx) * s, (v.co.y - cy) * s, 0))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    caras = list(bm.faces)
    ext = bmesh.ops.extrude_face_region(bm, geom=caras)
    nuevos = [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, 0.0012), verts=nuevos)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # al plano frontal: XY → XZ, relieve hacia -Y
    for v in bm.verts:
        x, y, zz = v.co
        v.co = Vector((x, Y_FR - zz + 0.0002, z + y))
    ob = objeto('Logo en relieve', bm, mat, col, angulo=50)
    bisel(ob, 0.00035, 1, 50, duro=False)
    return ob


def montoncito(nombre, c, ax, ay, z0, z1, n, mat, col):
    """Montículo de tiras de cáscara (≈5 mm) y aserrín con color por cara."""
    random.seed(11)
    bm = bmesh.new()
    capa = bm.loops.layers.color.new('Col')
    paleta = [hexcol(x) for x in ('#D2B14A', '#E08A2A', '#7E9A3C', '#9C7449', '#C79D69', '#C79D69', '#5E7D2E',
                                  '#E8D9B8', '#B5562B', '#C79D69')]
    nx = ny = 22
    vs = {}
    for i in range(nx + 1):
        for j in range(ny + 1):
            u, v = i / nx * 2 - 1, j / ny * 2 - 1
            hh = z0 + (z1 - z0) * max(0.0, 1 - 0.55 * (u * u + v * v)) + random.uniform(-0.002, 0.002)
            vs[i, j] = bm.verts.new((c[0] + u * ax, c[1] + v * ay, hh))
    for i in range(nx):
        for j in range(ny):
            f = bm.faces.new((vs[i, j], vs[i + 1, j], vs[i + 1, j + 1], vs[i, j + 1]))
            cf = random.choice(paleta)
            for lo in f.loops:
                lo[capa] = cf
    for k in range(n):
        u, v = random.uniform(-1, 1) * 0.92, random.uniform(-1, 1) * 0.92
        hh = z0 + (z1 - z0) * max(0.0, 1 - 0.55 * (u * u + v * v)) + 0.001
        L, A = random.uniform(0.012, 0.030), random.uniform(0.004, 0.0058)
        curv = 0.004 * random.choice((-1, 1))
        m = Matrix.Translation((c[0] + u * ax, c[1] + v * ay, hh)) @ Matrix.Rotation(random.uniform(0, math.pi), 4, 'Z') @ \
            Matrix.Rotation(random.uniform(-0.5, 0.5), 4, 'X')
        cf = random.choice(paleta)
        base = [(sx * L / 2, sy * A / 2, sz * 0.0006) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        vv = [bm.verts.new(m @ Vector((x, y, z + curv * (2 * x / L) ** 2))) for x, y, z in base]
        for q in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
            f = bm.faces.new([vv[i] for i in q])
            for lo in f.loops:
                lo[capa] = cf
    return objeto(nombre, bm, mat, col, angulo=60)


def particulas(nombre, n, col, mat, tam):
    random.seed(sum(map(ord, nombre)))
    paleta = [hexcol(x) for x in ('#D2B14A', '#E08A2A', '#7E9A3C', '#9C7449', '#5E7D2E', '#B5562B')]
    obs = []
    for k in range(n):
        bm = bm_caja(tam[0] * random.uniform(0.8, 1.2), tam[1] * random.uniform(0.6, 1.3), tam[2])
        capa = bm.loops.layers.color.new('Col')
        cf = random.choice(paleta)
        for f in bm.faces:
            for lo in f.loops:
                lo[capa] = cf
        ob = objeto(f'{nombre} {k:03d}', bm, mat, col, suave=False)
        ob.scale = (0, 0, 0)
        obs.append(ob)
    return obs


def cascaras(col, M):
    """Ocho cáscaras: banano, naranja, huevo, papa y aguacate."""
    obs = []

    def cinta(nombre, L, A, curva, mat):
        bm = bmesh.new()
        n = 14
        filas = []
        R = L / max(curva, 1e-3)
        for i in range(n + 1):
            s = i / n - 0.5
            a = s * curva
            x, z = R * math.sin(a), R * (1 - math.cos(a))
            ancho = A * (0.55 + 0.45 * math.cos(s * math.pi))
            filas.append([bm.verts.new((x, -ancho / 2, z)), bm.verts.new((x, ancho / 2, z))])
        for i in range(n):
            bm.faces.new((filas[i][0], filas[i + 1][0], filas[i + 1][1], filas[i][1]))
        ob = objeto(nombre, bm, mat, col, angulo=80)
        so = ob.modifiers.new('Grosor', 'SOLIDIFY')
        so.thickness = 0.0025
        sb = ob.modifiers.new('Sub', 'SUBSURF')
        sb.levels = sb.render_levels = 1
        return ob

    def casquete(nombre, r, ang, mat, grosor):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < r * math.cos(ang)], context='VERTS')
        ob = objeto(nombre, bm, mat, col, angulo=80)
        so = ob.modifiers.new('Grosor', 'SOLIDIFY')
        so.thickness = grosor
        return ob

    obs.append(cinta('Cascara banano 1', 0.11, 0.035, 1.6, M['banano']))
    obs.append(cinta('Cascara banano 2', 0.10, 0.032, 1.2, M['banano']))
    obs.append(casquete('Cascara naranja 1', 0.035, 1.0, M['naranja_c'], 0.004))
    obs.append(casquete('Cascara naranja 2', 0.033, 0.8, M['naranja_c'], 0.004))
    obs.append(casquete('Cascara huevo', 0.022, 1.57, M['huevo'], 0.0007))
    obs.append(cinta('Cascara papa 1', 0.07, 0.022, 3.2, M['papa']))
    obs.append(cinta('Cascara papa 2', 0.06, 0.020, 2.6, M['papa']))
    obs.append(casquete('Cascara aguacate', 0.040, 1.45, M['aguacate'], 0.003))
    for ob in obs:
        ob.scale = (0, 0, 0)
    return obs
