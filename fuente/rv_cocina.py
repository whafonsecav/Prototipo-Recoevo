# Cocina integral colombiana de clase media (estrato 3–4): mesón de granito negro, muebles en madecor tipo cedro,
# enchape blanco, piso de cerámica beige de 45 cm, ventana corrediza de aluminio con sábila, estufa de 4 puestos,
# chocolatera con molinillo, nevera blanca, limpión de cuadros. Luz de la mañana por la ventana.
import math
import random
import bpy
import bmesh
from mathutils import Vector, Matrix
from rv_util import (hexcol, material, vidrio_delgado, material_emisor, objeto, bisel, bm_caja, caja, cilindro,
                     bm_cilindro, bm_prisma, bm_tina, pts_rect_redondeado, bm_toro, booleana, borrar, _nodo, nuevo_material)

Y_MURO = 0.60            # cara interior del muro del fondo
X_IZQ, X_DER = -2.60, 2.30
Y_FRENTE = -2.60
Z_TECHO = 2.40
X_MESON = (-2.55, 0.30)  # mesón: del muro izquierdo hasta el final (junto al RECOEVO)
Z_MESON = 0.90
VENTANA = (-0.95, -0.05, 1.05, 2.00)   # x0, x1, z0, z1 (muro del fondo, sobre la poceta)
VENTANA_DER = (-1.45, -0.35, 1.00, 2.05)  # y0, y1, z0, z1 (muro derecho)


# ---------------------------------------------------------------- materiales procedimentales
def mat_baldosa(nombre, c1, c2, mortero, ancho, alto, rug, plano='XY', desfase=0.0, rug_mortero=0.8, bump=0.6):
    m = nuevo_material(nombre)
    nt = m.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputMaterial', 900, 0)
    p = _nodo(nt, 'ShaderNodeBsdfPrincipled', 600, 0)
    tc = _nodo(nt, 'ShaderNodeTexCoord', -900, 0)
    sep = _nodo(nt, 'ShaderNodeSeparateXYZ', -700, 0)
    comb = _nodo(nt, 'ShaderNodeCombineXYZ', -500, 0)
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    a, b = {'XY': ('X', 'Y'), 'XZ': ('X', 'Z'), 'YZ': ('Y', 'Z')}[plano]
    nt.links.new(sep.outputs[a], comb.inputs['X'])
    nt.links.new(sep.outputs[b], comb.inputs['Y'])
    br = _nodo(nt, 'ShaderNodeTexBrick', -300, 0)
    br.offset = desfase
    br.offset_frequency = 2
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = mortero
    br.inputs['Mortar Smooth'].default_value = 0.3
    br.inputs['Brick Width'].default_value = ancho
    br.inputs['Row Height'].default_value = alto
    br.inputs['Bias'].default_value = 0.0
    br.inputs['Color1'].default_value = c1
    br.inputs['Color2'].default_value = c2
    br.inputs['Mortar'].default_value = hexcol('#BDB6A8')
    nt.links.new(comb.outputs[0], br.inputs['Vector'])
    # variación suave dentro de cada baldosa
    nz = _nodo(nt, 'ShaderNodeTexNoise', -300, -300)
    nz.inputs['Scale'].default_value = 3.0
    nt.links.new(comb.outputs[0], nz.inputs['Vector'])
    mx = _nodo(nt, 'ShaderNodeMix', 0, 100)
    mx.data_type = 'RGBA'
    mx.blend_type = 'MULTIPLY'
    mx.inputs['Factor'].default_value = 0.08
    nt.links.new(br.outputs['Color'], mx.inputs['A'])
    nt.links.new(nz.outputs['Color'], mx.inputs['B'])
    nt.links.new(mx.outputs['Result'], p.inputs['Base Color'])
    mr = _nodo(nt, 'ShaderNodeMapRange', 200, -200)
    mr.inputs['To Min'].default_value = rug_mortero
    mr.inputs['To Max'].default_value = rug
    nt.links.new(br.outputs['Fac'], mr.inputs['Value'])
    mr.inputs['From Min'].default_value = 1.0
    mr.inputs['From Max'].default_value = 0.0
    nt.links.new(mr.outputs['Result'], p.inputs['Roughness'])
    bn = _nodo(nt, 'ShaderNodeBump', 300, -400)
    bn.inputs['Strength'].default_value = bump
    bn.inputs['Distance'].default_value = 0.002
    inv = _nodo(nt, 'ShaderNodeMath', 100, -400)
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    nt.links.new(br.outputs['Fac'], inv.inputs[1])
    nt.links.new(inv.outputs[0], bn.inputs['Height'])
    nt.links.new(bn.outputs['Normal'], p.inputs['Normal'])
    p.inputs['Coat Weight'].default_value = 0.0
    nt.links.new(p.outputs['BSDF'], out.inputs['Surface'])
    return m


def mat_madera(nombre, c1, c2, escala=6.0, rug=0.45, eje='Z'):
    m = nuevo_material(nombre)
    nt = m.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputMaterial', 900, 0)
    p = _nodo(nt, 'ShaderNodeBsdfPrincipled', 600, 0)
    tc = _nodo(nt, 'ShaderNodeTexCoord', -900, 0)
    mp = _nodo(nt, 'ShaderNodeMapping', -700, 0)
    mp.inputs['Scale'].default_value = {'Z': (1, 1, 0.08), 'X': (0.08, 1, 1), 'Y': (1, 0.08, 1)}[eje]
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    wv = _nodo(nt, 'ShaderNodeTexWave', -400, 0)
    wv.wave_type = 'RINGS'
    wv.inputs['Scale'].default_value = escala
    wv.inputs['Distortion'].default_value = 6.0
    wv.inputs['Detail'].default_value = 3.0
    wv.inputs['Detail Scale'].default_value = 1.5
    nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
    nz = _nodo(nt, 'ShaderNodeTexNoise', -400, -250)
    nz.inputs['Scale'].default_value = 40.0
    nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    cr = _nodo(nt, 'ShaderNodeValToRGB', -100, 0)
    cr.color_ramp.elements[0].color = c1
    cr.color_ramp.elements[1].color = c2
    mx = _nodo(nt, 'ShaderNodeMath', -200, -100)
    mx.operation = 'MULTIPLY_ADD'
    nt.links.new(wv.outputs['Fac'], mx.inputs[0])
    mx.inputs[1].default_value = 0.8
    nt.links.new(nz.outputs['Fac'], mx.inputs[2])
    cl = _nodo(nt, 'ShaderNodeClamp', -150, 0)
    nt.links.new(mx.outputs[0], cl.inputs['Value'])
    nt.links.new(cl.outputs[0], cr.inputs['Fac'])
    nt.links.new(cr.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rug
    p.inputs['Coat Weight'].default_value = 0.25
    p.inputs['Coat Roughness'].default_value = 0.25
    nt.links.new(p.outputs['BSDF'], out.inputs['Surface'])
    return m


def mat_granito(nombre):
    m = nuevo_material(nombre)
    nt = m.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputMaterial', 900, 0)
    p = _nodo(nt, 'ShaderNodeBsdfPrincipled', 600, 0)
    tc = _nodo(nt, 'ShaderNodeTexCoord', -900, 0)
    vo = _nodo(nt, 'ShaderNodeTexVoronoi', -600, 0)
    vo.inputs['Scale'].default_value = 260.0
    nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
    nz = _nodo(nt, 'ShaderNodeTexNoise', -600, -250)
    nz.inputs['Scale'].default_value = 90.0
    nz.inputs['Detail'].default_value = 8.0
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = _nodo(nt, 'ShaderNodeValToRGB', -300, 0)
    cr.color_ramp.elements[0].position = 0.0
    cr.color_ramp.elements[0].color = hexcol('#070707')
    cr.color_ramp.elements[1].position = 0.62
    cr.color_ramp.elements[1].color = hexcol('#141414')
    e = cr.color_ramp.elements.new(0.75)
    e.color = hexcol('#5A5A58')
    e = cr.color_ramp.elements.new(0.86)
    e.color = hexcol('#C9C4BA')
    mx = _nodo(nt, 'ShaderNodeMath', -400, 0)
    mx.operation = 'MULTIPLY'
    nt.links.new(vo.outputs['Color'], mx.inputs[0])
    nt.links.new(nz.outputs['Fac'], mx.inputs[1])
    pw = _nodo(nt, 'ShaderNodeMath', -350, 100)
    pw.operation = 'MULTIPLY'
    pw.inputs[1].default_value = 1.7
    nt.links.new(mx.outputs[0], pw.inputs[0])
    nt.links.new(pw.outputs[0], cr.inputs['Fac'])
    nt.links.new(cr.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = 0.10
    p.inputs['Coat Weight'].default_value = 0.4
    p.inputs['Coat Roughness'].default_value = 0.05
    nt.links.new(p.outputs['BSDF'], out.inputs['Surface'])
    return m


def mat_cuadros(nombre, c1, c2, escala=40):
    m = nuevo_material(nombre)
    nt = m.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputMaterial', 600, 0)
    p = _nodo(nt, 'ShaderNodeBsdfPrincipled', 300, 0)
    tc = _nodo(nt, 'ShaderNodeTexCoord', -400, 0)
    ch = _nodo(nt, 'ShaderNodeTexChecker', -100, 0)
    ch.inputs['Scale'].default_value = escala
    ch.inputs['Color1'].default_value = c1
    ch.inputs['Color2'].default_value = c2
    nt.links.new(tc.outputs['Object'], ch.inputs['Vector'])
    nt.links.new(ch.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = 0.85
    p.inputs['Sheen Weight'].default_value = 0.5
    nt.links.new(p.outputs['BSDF'], out.inputs['Surface'])
    return m


def mat_exterior(nombre):
    """Lo que se ve por la ventana: cielo claro de la mañana y árboles, sobreexpuesto como en una foto real."""
    m = nuevo_material(nombre)
    nt = m.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputMaterial', 900, 0)
    em = _nodo(nt, 'ShaderNodeEmission', 650, 0)
    tc = _nodo(nt, 'ShaderNodeTexCoord', -900, 0)
    sep = _nodo(nt, 'ShaderNodeSeparateXYZ', -700, 100)
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    nz = _nodo(nt, 'ShaderNodeTexNoise', -600, -150)
    nz.inputs['Scale'].default_value = 1.6
    nz.inputs['Detail'].default_value = 10.0
    nz.inputs['Roughness'].default_value = 0.65
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    # máscara de copa de árboles: ruido + altura
    alt = _nodo(nt, 'ShaderNodeMapRange', -400, 100)
    alt.inputs['From Min'].default_value = 0.6
    alt.inputs['From Max'].default_value = 2.6
    nt.links.new(sep.outputs['Z'], alt.inputs['Value'])
    resta = _nodo(nt, 'ShaderNodeMath', -250, 0)
    resta.operation = 'SUBTRACT'
    nt.links.new(nz.outputs['Fac'], resta.inputs[0])
    nt.links.new(alt.outputs['Result'], resta.inputs[1])
    msk = _nodo(nt, 'ShaderNodeMapRange', -100, 0)
    msk.inputs['From Min'].default_value = 0.02
    msk.inputs['From Max'].default_value = 0.10
    nt.links.new(resta.outputs[0], msk.inputs['Value'])
    hoja = _nodo(nt, 'ShaderNodeMix', 200, -100)
    hoja.data_type = 'RGBA'
    nt.links.new(nz.outputs['Fac'], hoja.inputs['Factor'])
    hoja.inputs['A'].default_value = hexcol('#4C6B3A')
    hoja.inputs['B'].default_value = hexcol('#8FA96A')
    cielo = _nodo(nt, 'ShaderNodeMix', 200, 150)
    cielo.data_type = 'RGBA'
    nt.links.new(alt.outputs['Result'], cielo.inputs['Factor'])
    cielo.inputs['A'].default_value = hexcol('#E7EEF2')
    cielo.inputs['B'].default_value = hexcol('#B9D2E6')
    mz = _nodo(nt, 'ShaderNodeMix', 420, 0)
    mz.data_type = 'RGBA'
    nt.links.new(msk.outputs['Result'], mz.inputs['Factor'])
    nt.links.new(cielo.outputs['Result'], mz.inputs['A'])
    nt.links.new(hoja.outputs['Result'], mz.inputs['B'])
    nt.links.new(mz.outputs['Result'], em.inputs['Color'])
    em.inputs['Strength'].default_value = 7.0
    nt.links.new(em.outputs[0], out.inputs['Surface'])
    return m


# ---------------------------------------------------------------- construcción
def construir(col, M):
    random.seed(3)
    C = {}
    piso = mat_baldosa('Piso ceramica beige', hexcol('#D9CDB6'), hexcol('#CFC2A8'), 0.004, 0.45, 0.45, 0.22, 'XY',
                       rug_mortero=0.9, bump=0.5)
    enchape = mat_baldosa('Enchape blanco', hexcol('#F1F0EB'), hexcol('#ECEBE5'), 0.0035, 0.25, 0.20, 0.08, 'XZ', 0.5,
                          bump=0.8)
    pintura = material('Pintura crema', hexcol('#E6DAC0'), 0.88, bump=0.05, escala_bump=200)
    techo = material('Techo blanco', hexcol('#F2F0EA'), 0.9)
    cedro = mat_madera('Madecor cedro', hexcol('#7A4A2C'), hexcol('#683E24'), 3.0, 0.42)
    cedro_h = mat_madera('Madecor cedro horizontal', hexcol('#7A4A2C'), hexcol('#683E24'), 3.0, 0.42, eje='X')
    granito = mat_granito('Granito negro')
    alu = material('Aluminio', hexcol('#C4C7CA'), 0.32, metal=1.0)
    inox = material('Inox cocina', hexcol('#C9CCCF'), 0.24, metal=1.0, aniso=0.5)
    vidrio = vidrio_delgado('Vidrio ventana')
    negro_v = material('Vidrio negro estufa', hexcol('#0B0B0C'), 0.04, coat=0.6)
    hierro = material('Parrilla hierro', hexcol('#1A1A1A'), 0.55, metal=0.6)
    nevera = material('Nevera blanca', hexcol('#F2F2EF'), 0.25, coat=0.3)
    zocalo = material('Zocalo', hexcol('#2A2622'), 0.6)
    teja = material('Matera barro', hexcol('#A9562F'), 0.75, bump=0.3, escala_bump=200)
    sabila = material('Sabila', hexcol('#6E8F4E'), 0.45, sss=0.2, ruido_color=0.3, escala_color=20)
    tierra = material('Tierra', hexcol('#3B2A1D'), 0.95, bump=1.0, escala_bump=300)
    tabla = mat_madera('Tabla de picar', hexcol('#C8A170'), hexcol('#A27A4C'), 9.0, 0.5, eje='X')
    plat = material('Ceramica blanca', hexcol('#F4F2EC'), 0.12, coat=0.5)
    limpion = mat_cuadros('Limpion cuadros', hexcol('#B8312F'), hexcol('#F2EDE4'), 45)
    banano = material('Banano', hexcol('#E6C42F'), 0.45, ruido_color=0.2, escala_color=30)
    naranja = material('Naranja', hexcol('#EE8A1E'), 0.4, bump=0.5, escala_bump=300)
    aguacate = material('Aguacate', hexcol('#2E3A1C'), 0.5, bump=0.7, escala_bump=150)
    termo = material('Termo rojo', hexcol('#B32A2A'), 0.3, coat=0.4)
    vidrio_f = material('Vidrio frasco', hexcol('#F4F6F4'), 0.05, transmision=1.0, thin=True)
    granos = [material('Lentejas', hexcol('#8E6A3A'), 0.7, bump=0.8, escala_bump=400),
              material('Frijol rojo', hexcol('#6E2A22'), 0.5, bump=0.8, escala_bump=300),
              material('Arroz', hexcol('#F1ECE0'), 0.6, bump=0.8, escala_bump=600)]
    tapa_roja = material('Tapa roja', hexcol('#C23B2F'), 0.4)

    # ---- cuarto
    caja('Piso', X_DER - X_IZQ, Y_MURO - Y_FRENTE, 0.02, ((X_IZQ + X_DER) / 2, (Y_MURO + Y_FRENTE) / 2, -0.01), piso, col, b=0)
    caja('Techo', X_DER - X_IZQ, Y_MURO - Y_FRENTE, 0.02, ((X_IZQ + X_DER) / 2, (Y_MURO + Y_FRENTE) / 2, Z_TECHO + 0.01), techo, col, b=0)
    caja('Muro izquierdo', 0.15, Y_MURO - Y_FRENTE + 0.3, Z_TECHO, (X_IZQ - 0.075, (Y_MURO + Y_FRENTE) / 2, Z_TECHO / 2), pintura, col, b=0)
    # muro derecho con ventana (por aquí entra el sol de la mañana)
    wy0, wy1, wz0, wz1 = VENTANA_DER
    xm = X_DER + 0.075
    caja('Muro derecho a', 0.15, wy0 - Y_FRENTE + 0.15, Z_TECHO, (xm, (Y_FRENTE - 0.15 + wy0) / 2, Z_TECHO / 2), pintura, col, b=0)
    caja('Muro derecho b', 0.15, Y_MURO + 0.15 - wy1, Z_TECHO, (xm, (wy1 + Y_MURO + 0.15) / 2, Z_TECHO / 2), pintura, col, b=0)
    caja('Muro derecho bajo', 0.15, wy1 - wy0, wz0, (xm, (wy0 + wy1) / 2, wz0 / 2), pintura, col, b=0)
    caja('Muro derecho alto', 0.15, wy1 - wy0, Z_TECHO - wz1, (xm, (wy0 + wy1) / 2, (wz1 + Z_TECHO) / 2), pintura, col, b=0)
    alu_v = material('Aluminio ventana', hexcol('#C4C7CA'), 0.32, metal=1.0)
    caja('Alfeizar der', 0.19, wy1 - wy0 + 0.06, 0.025, (xm - 0.02, (wy0 + wy1) / 2, wz0 + 0.0125), granito, col, b=0.003)
    xv = X_DER + 0.10
    for y in (wy0 + 0.02, wy1 - 0.02):
        caja('Marco ventana der v', 0.05, 0.04, wz1 - wz0, (xv, y, (wz0 + wz1) / 2), alu_v, col, b=0.002)
    for z in (wz0 + 0.045, wz1 - 0.02):
        caja('Marco ventana der h', 0.05, wy1 - wy0, 0.04, (xv, (wy0 + wy1) / 2, z), alu_v, col, b=0.002)
    caja('Parteluz der', 0.04, 0.03, wz1 - wz0, (xv, (wy0 + wy1) / 2, (wz0 + wz1) / 2), alu_v, col, b=0.002)
    vd = caja('Vidrio der', 0.004, wy1 - wy0 - 0.06, wz1 - wz0 - 0.08, (xv, (wy0 + wy1) / 2, (wz0 + wz1) / 2), vidrio_delgado('Vidrio der'),
              col, b=0)
    vd.visible_shadow = False
    ext2 = caja('Exterior der', 0.05, 12.0, 7.0, (X_DER + 3.5, -0.8, 1.6), mat_exterior('Exterior der'), col, b=0)
    ext2.visible_shadow = False
    caja('Muro frente', X_DER - X_IZQ + 0.3, 0.15, Z_TECHO, ((X_IZQ + X_DER) / 2, Y_FRENTE - 0.075, Z_TECHO / 2), pintura, col, b=0)
    vx0, vx1, vz0, vz1 = VENTANA
    e = 0.15
    yc = Y_MURO + e / 2
    # muro del fondo con hueco de ventana
    caja('Muro fondo izq', vx0 - X_IZQ, e, Z_TECHO, ((X_IZQ + vx0) / 2, yc, Z_TECHO / 2), pintura, col, b=0)
    caja('Muro fondo der', X_DER - vx1, e, Z_TECHO, ((vx1 + X_DER) / 2, yc, Z_TECHO / 2), pintura, col, b=0)
    caja('Muro bajo ventana', vx1 - vx0, e, vz0, ((vx0 + vx1) / 2, yc, vz0 / 2), pintura, col, b=0)
    caja('Muro sobre ventana', vx1 - vx0, e, Z_TECHO - vz1, ((vx0 + vx1) / 2, yc, (vz1 + Z_TECHO) / 2), pintura, col, b=0)
    # enchape sobre el mesón (y alrededor de la ventana) + franja detrás del RECOEVO hasta 1,45 m
    z_e1 = 1.50
    caja('Enchape izq', vx0 - X_MESON[0], 0.008, z_e1 - Z_MESON, ((X_MESON[0] + vx0) / 2, Y_MURO - 0.004, (Z_MESON + z_e1) / 2), enchape, col, b=0)
    caja('Enchape der', 0.98 - vx1, 0.008, z_e1 - Z_MESON, ((vx1 + 0.98) / 2, Y_MURO - 0.004, (Z_MESON + z_e1) / 2), enchape, col, b=0)
    caja('Enchape bajo ventana', vx1 - vx0, 0.008, vz0 - Z_MESON, ((vx0 + vx1) / 2, Y_MURO - 0.004, (Z_MESON + vz0) / 2), enchape, col, b=0)
    caja('Enchape tras equipo', 0.98 - X_MESON[1], 0.008, Z_MESON, ((X_MESON[1] + 0.98) / 2, Y_MURO - 0.004, Z_MESON / 2), enchape, col, b=0)
    # guardaescoba
    caja('Guardaescoba', X_DER - 0.98, 0.012, 0.08, ((0.98 + X_DER) / 2, Y_MURO - 0.006, 0.04), piso, col, b=0.002)
    caja('Guardaescoba der', 0.012, Y_MURO - Y_FRENTE, 0.08, (X_DER - 0.006, (Y_MURO + Y_FRENTE) / 2, 0.04), piso, col, b=0.002)

    # ---- ventana corrediza de aluminio
    caja('Alfeizar', vx1 - vx0 + 0.06, e + 0.04, 0.025, ((vx0 + vx1) / 2, Y_MURO + e / 2 - 0.02, vz0 + 0.0125), granito, col, b=0.003)
    yv = Y_MURO + 0.10
    for x in (vx0 + 0.02, vx1 - 0.02):
        caja('Marco ventana v', 0.04, 0.05, vz1 - vz0, (x, yv, (vz0 + vz1) / 2), alu, col, b=0.002)
    for z in (vz0 + 0.045, vz1 - 0.02):
        caja('Marco ventana h', vx1 - vx0, 0.05, 0.04, ((vx0 + vx1) / 2, yv, z), alu, col, b=0.002)
    ancho_h = (vx1 - vx0 - 0.04) / 2 + 0.03
    for k, (x0, yy) in enumerate(((vx0 + 0.02, yv - 0.012), (vx0 + 0.02 + ancho_h * 0.55, yv + 0.012))):
        xc = x0 + ancho_h / 2
        for dx in (-ancho_h / 2 + 0.015, ancho_h / 2 - 0.015):
            caja('Hoja v', 0.03, 0.018, vz1 - vz0 - 0.08, (xc + dx, yy, (vz0 + vz1) / 2 + 0.01), alu, col, b=0.0015)
        for z in (vz0 + 0.075, vz1 - 0.035):
            caja('Hoja h', ancho_h, 0.018, 0.03, (xc, yy, z), alu, col, b=0.0015)
        caja('Vidrio', ancho_h - 0.03, 0.004, vz1 - vz0 - 0.14, (xc, yy, (vz0 + vz1) / 2 + 0.02), vidrio, col, b=0).visible_shadow = False
    # exterior
    ext = caja('Exterior', 14.0, 0.05, 7.0, (-0.5, Y_MURO + 3.5, 1.6), mat_exterior('Exterior manana'), col, b=0)
    ext.visible_shadow = False
    # sábila en matera de barro sobre el alféizar
    mx = (vx0 + vx1) / 2 + 0.22
    my = Y_MURO + 0.035
    objeto('Matera', bm_cilindro(0.065, 0.11, 40, r2=0.085, c=(mx, my, vz0 + 0.025 + 0.055)), teja, col)
    cilindro('Tierra matera', 0.078, 0.004, (mx, my, vz0 + 0.025 + 0.104), tierra, col=col)
    for k in range(11):
        a = 2 * math.pi * k / 11 + random.uniform(-0.2, 0.2)
        inc = random.uniform(0.25, 0.65)
        L = random.uniform(0.18, 0.30)
        bm = bm_cilindro(0.016, L, 6, r2=0.001, c=(0, 0, L / 2))
        for v in bm.verts:
            v.co.y *= 0.35
        ob = objeto('Hoja sabila', bm, sabila, col, angulo=70)
        ob.location = (mx + 0.02 * math.cos(a), my + 0.02 * math.sin(a), vz0 + 0.025 + 0.10)
        ob.rotation_euler = (inc * math.cos(a + math.pi / 2), inc * math.sin(a + math.pi / 2) * -1, a)
        ob.rotation_euler = (0, inc, a)

    # ---- muebles bajos (cocina integral) y mesón de granito
    x0, x1 = X_MESON
    caja('Zocalo muebles', x1 - x0, 0.02, 0.10, ((x0 + x1) / 2, Y_MURO - 0.54, 0.05), zocalo, col, b=0)
    caja('Cuerpo muebles', x1 - x0, 0.56, Z_MESON - 0.13, ((x0 + x1) / 2, Y_MURO - 0.28, (0.10 + Z_MESON - 0.03) / 2 + 0.0),
         cedro, col, b=0.001)
    caja('Costado mueble', 0.018, 0.58, Z_MESON - 0.03, (x1 - 0.009, Y_MURO - 0.29, (Z_MESON - 0.03) / 2), cedro, col, b=0.002)
    n = 5
    w = (x1 - x0) / n
    for k in range(n):
        cx = x0 + w * (k + 0.5)
        caja('Puerta mueble', w - 0.006, 0.018, 0.62, (cx, Y_MURO - 0.569, 0.43), cedro, col, b=0.0025)
        caja('Cajon mueble', w - 0.006, 0.018, 0.13, (cx, Y_MURO - 0.569, 0.81), cedro_h, col, b=0.0025)
        caja('Manija', 0.16, 0.012, 0.010, (cx, Y_MURO - 0.586, 0.83), alu, col, b=0.003)
        caja('Manija', 0.010, 0.012, 0.12, (cx + (w / 2 - 0.05) * (1 if k % 2 else -1), Y_MURO - 0.586, 0.62), alu, col, b=0.003)
    mes = objeto('Meson granito', bm_caja(x1 - x0 + 0.02, 0.62, 0.03, ((x0 + x1) / 2 + 0.01, Y_MURO - 0.31, Z_MESON - 0.015)),
                 granito, col)
    bisel(mes, 0.004, 3)
    # poceta de acero bajo la ventana
    px = (vx0 + vx1) / 2 - 0.05
    py = Y_MURO - 0.30
    c = objeto('_c', bm_caja(0.50, 0.38, 0.1, (px, py, Z_MESON)), None, col, suave=False)
    booleana(mes, c)
    borrar(c)
    pot = objeto('Poceta', bm_tina(pts_rect_redondeado(0.44, 0.32, 0.05, 8, px, py), pts_rect_redondeado(0.48, 0.36, 0.06, 8, px, py),
                                   Z_MESON - 0.18, Z_MESON - 0.002), inox, col)
    so = pot.modifiers.new('G', 'SOLIDIFY')
    so.thickness = 0.0015
    objeto('Ceja poceta', bm_prisma(pts_rect_redondeado(0.52, 0.40, 0.06, 8, px, py), Z_MESON - 0.003, Z_MESON + 0.0015), inox, col)
    c = objeto('_c', bm_prisma(pts_rect_redondeado(0.48, 0.36, 0.06, 8, px, py), Z_MESON - 0.01, Z_MESON + 0.01), None, col, suave=False)
    booleana(bpy.data.objects['Ceja poceta'], c)
    borrar(c)
    cilindro('Sifon', 0.03, 0.004, (px, py, Z_MESON - 0.178), inox, col=col)
    # grifería
    cilindro('Grifo base', 0.022, 0.05, (px, Y_MURO - 0.06, Z_MESON + 0.025), inox, col=col, b=0.003)
    curva = bpy.data.curves.new('GrifoC', 'CURVE')
    curva.dimensions = '3D'
    sp = curva.splines.new('BEZIER')
    sp.bezier_points.add(2)
    pts = [(px, Y_MURO - 0.06, Z_MESON + 0.05), (px, Y_MURO - 0.08, Z_MESON + 0.32), (px, Y_MURO - 0.27, Z_MESON + 0.22)]
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    curva.bevel_depth = 0.011
    curva.bevel_resolution = 4
    g = bpy.data.objects.new('Grifo', curva)
    col.objects.link(g)
    g.data.materials.append(inox)
    caja('Palanca grifo', 0.012, 0.08, 0.012, (px + 0.04, Y_MURO - 0.08, Z_MESON + 0.07), inox, col, b=0.004)

    # ---- estufa de 4 puestos empotrada + campana
    ex, ey = -1.47, Y_MURO - 0.30
    caja('Estufa vidrio', 0.58, 0.50, 0.008, (ex, ey, Z_MESON + 0.004), negro_v, col, b=0.002)
    for i, (dx, dy) in enumerate(((-0.14, -0.11), (0.14, -0.11), (-0.14, 0.11), (0.14, 0.11))):
        cilindro('Quemador', 0.040 if i % 2 else 0.032, 0.014, (ex + dx, ey + dy, Z_MESON + 0.015), hierro, col=col, b=0.002)
        cilindro('Tapa quemador', 0.026, 0.006, (ex + dx, ey + dy, Z_MESON + 0.024), hierro, col=col, b=0.001)
    for dy in (-0.11, 0.11):
        for dx in (-0.25, -0.03, 0.03, 0.25):
            caja('Parrilla', 0.012, 0.24, 0.012, (ex + dx, ey + dy, Z_MESON + 0.036), hierro, col, b=0.002)
        caja('Parrilla', 0.56, 0.012, 0.012, (ex, ey + dy - 0.11, Z_MESON + 0.036), hierro, col, b=0.002)
        caja('Parrilla', 0.56, 0.012, 0.012, (ex, ey + dy + 0.11, Z_MESON + 0.036), hierro, col, b=0.002)
    for k in range(4):
        cilindro('Perilla estufa', 0.016, 0.02, (ex - 0.21 + k * 0.14, Y_MURO - 0.585, 0.83), negro_v, eje='Y', col=col, b=0.003)
    caja('Campana', 0.60, 0.48, 0.14, (ex, Y_MURO - 0.24, 1.62), inox, col, b=0.01)
    caja('Ducto campana', 0.26, 0.24, 0.62, (ex, Y_MURO - 0.12, 2.0), inox, col, b=0.004)
    # olla y chocolatera con molinillo
    ol = objeto('Olla', bm_tina(pts_rect_redondeado(0.22, 0.22, 0.109, 10, ex + 0.14, ey + 0.11),
                                pts_rect_redondeado(0.22, 0.22, 0.109, 10, ex + 0.14, ey + 0.11), Z_MESON + 0.042, Z_MESON + 0.17), alu, col)
    s = ol.modifiers.new('G', 'SOLIDIFY')
    s.thickness = 0.002
    cilindro('Tapa olla', 0.113, 0.006, (ex + 0.14, ey + 0.11, Z_MESON + 0.173), alu, col=col, b=0.002)
    cilindro('Pomo olla', 0.015, 0.015, (ex + 0.14, ey + 0.11, Z_MESON + 0.183), negro_v, col=col, b=0.004)
    ch = objeto('Chocolatera', bm_cilindro(0.06, 0.16, 40, r2=0.045, c=(ex - 0.14, ey - 0.11, Z_MESON + 0.042 + 0.08)), alu, col)
    caja('Mango chocolatera', 0.16, 0.022, 0.012, (ex - 0.14 - 0.12, ey - 0.11, Z_MESON + 0.16), negro_v, col, b=0.005)
    cilindro('Molinillo', 0.0075, 0.34, (ex - 0.13, ey - 0.11, Z_MESON + 0.26), tabla, col=col)
    cilindro('Molinillo cabeza', 0.022, 0.05, (ex - 0.13, ey - 0.11, Z_MESON + 0.10), tabla, col=col, b=0.004)

    # ---- muebles altos
    for (a0, a1) in ((X_MESON[0], ex - 0.32), (ex + 0.32, vx0 - 0.05)):
        if a1 - a0 < 0.15:
            continue
        caja('Mueble alto', a1 - a0, 0.33, 0.70, ((a0 + a1) / 2, Y_MURO - 0.165, 1.85), cedro, col, b=0.002)
        nn = max(1, round((a1 - a0) / 0.40))
        ww = (a1 - a0) / nn
        for k in range(nn):
            cx = a0 + ww * (k + 0.5)
            caja('Puerta alta', ww - 0.006, 0.018, 0.69, (cx, Y_MURO - 0.339, 1.85), cedro, col, b=0.0025)
            caja('Manija alta', 0.010, 0.012, 0.12, (cx + (ww / 2 - 0.05) * (1 if k % 2 else -1), Y_MURO - 0.355, 1.58), alu, col, b=0.003)
    caja('Mueble alto techo', ex + 0.32 - (ex - 0.32), 0.33, 0.45, (ex, Y_MURO - 0.165, 2.10), cedro, col, b=0.002)

    # ---- calendario de la tienda del barrio en la pared, a la derecha del equipo
    cxl = 1.45
    caja('Calendario hoja', 0.30, 0.004, 0.44, (cxl, Y_MURO - 0.004, 1.42), plat, col, b=0)
    caja('Calendario foto', 0.28, 0.003, 0.18, (cxl, Y_MURO - 0.007, 1.53), material('Foto paisaje', hexcol('#6F9A5B'), 0.6,
         ruido_color=0.5, escala_color=12, color2=hexcol('#9CC3D9')), col, b=0)
    for k in range(5):
        caja('Calendario fila', 0.26, 0.002, 0.003, (cxl, Y_MURO - 0.007, 1.40 - k * 0.035), zocalo, col, b=0)
    caja('Calendario titulo', 0.16, 0.002, 0.018, (cxl, Y_MURO - 0.007, 1.425), tapa_roja, col, b=0)
    cilindro('Puntilla', 0.004, 0.01, (cxl, Y_MURO - 0.01, 1.64), alu, eje='Y', col=col)

    # limpión de cuadros colgado del tirador del cajón al lado del equipo
    lx = -1.30                     # limpión en el cajón junto a la estufa
    bm = bmesh.new()
    nx, nz = 10, 16
    vv = {}
    for i in range(nx + 1):
        for j in range(nz + 1):
            u, v = i / nx, j / nz
            vv[i, j] = bm.verts.new((lx - 0.12 + 0.24 * u, Y_MURO - 0.600 - 0.012 * math.sin(v * math.pi) - 0.006 * math.sin(u * 7),
                                     0.83 - 0.34 * v))
    for i in range(nx):
        for j in range(nz):
            bm.faces.new((vv[i, j], vv[i + 1, j], vv[i + 1, j + 1], vv[i, j + 1]))
    lm = objeto('Limpion', bm, limpion, col)
    so = lm.modifiers.new('G', 'SOLIDIFY')
    so.thickness = 0.002
    sb = lm.modifiers.new('S', 'SUBSURF')
    sb.levels = sb.render_levels = 1

    # ---- tabla de picar con frutas cerca del equipo, frutero y termo
    tx, ty = -0.05, Y_MURO - 0.30
    caja('Tabla', 0.38, 0.24, 0.018, (tx, ty, Z_MESON + 0.009), tabla, col, b=0.004)
    cuchillo = caja('Cuchillo hoja', 0.17, 0.028, 0.002, (tx + 0.05, ty - 0.07, Z_MESON + 0.019), inox, col, b=0.0008)
    caja('Cuchillo mango', 0.11, 0.022, 0.016, (tx - 0.09, ty - 0.07, Z_MESON + 0.026), zocalo, col, b=0.006)
    for k in range(3):   # bananos
        curva = bpy.data.curves.new('BananoC', 'CURVE')
        curva.dimensions = '3D'
        sp = curva.splines.new('BEZIER')
        sp.bezier_points.add(2)
        bx, by = 0.55 + k * 0.03 - 1.2, Y_MURO - 0.22 - k * 0.035
        for bp, p in zip(sp.bezier_points, ((bx - 0.09, by, Z_MESON + 0.07), (bx, by - 0.035, Z_MESON + 0.03 + k * 0.012),
                                           (bx + 0.09, by, Z_MESON + 0.07))):
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = 'AUTO'
        curva.bevel_depth = 0.016
        curva.bevel_resolution = 2
        b = bpy.data.objects.new('Banano', curva)
        col.objects.link(b)
        b.data.materials.append(banano)
    objeto('Frutero', bm_tina([(math.cos(a) * 0.08 - 0.65, math.sin(a) * 0.08 + Y_MURO - 0.25) for a in
                               [2 * math.pi * i / 40 for i in range(40)]],
                              [(math.cos(a) * 0.14 - 0.65, math.sin(a) * 0.14 + Y_MURO - 0.25) for a in
                               [2 * math.pi * i / 40 for i in range(40)]], Z_MESON, Z_MESON + 0.07), plat, col)
    for k, (dx, dy, r, mm) in enumerate(((-0.03, 0.02, 0.040, naranja), (0.04, -0.02, 0.038, naranja),
                                         (0.0, 0.05, 0.045, aguacate), (0.02, 0.0, 0.037, naranja))):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=r)
        if mm is aguacate:
            for v in bm.verts:
                v.co.z *= 1.25
        ob = objeto('Fruta', bm, mm, col)
        ob.location = (-0.65 + dx, Y_MURO - 0.25 + dy, Z_MESON + 0.05 + r * 0.7 + (0.02 if k == 3 else 0))
    termo_o = cilindro('Termo', 0.045, 0.26, (-1.06, Y_MURO - 0.14, Z_MESON + 0.13), termo, col=col, b=0.008)
    cilindro('Tapa termo', 0.040, 0.05, (-1.06, Y_MURO - 0.14, Z_MESON + 0.285), plat, col=col, b=0.006)

    # ---- repisa de madera con frascos (lentejas, frijol, arroz) sobre el equipo
    caja('Repisa', 0.60, 0.20, 0.025, (0.62, Y_MURO - 0.10, 1.42), tabla, col, b=0.003)
    for x in (0.38, 0.86):
        caja('Escuadra', 0.02, 0.16, 0.12, (x, Y_MURO - 0.08, 1.36), alu, col, b=0.002)
    for k in range(3):
        fx = 0.44 + k * 0.17
        objeto('Frasco', bm_cilindro(0.048, 0.17, 40, c=(fx, Y_MURO - 0.10, 1.433 + 0.085)), vidrio_f, col)
        cilindro('Contenido frasco', 0.045, 0.12, (fx, Y_MURO - 0.10, 1.433 + 0.062), granos[k], col=col)
        cilindro('Tapa frasco', 0.05, 0.022, (fx, Y_MURO - 0.10, 1.433 + 0.181), tapa_roja, col=col, b=0.004)

    # ---- lámpara de techo (plafón) y reloj
    pl = cilindro('Plafon', 0.18, 0.04, (-0.5, -0.9, Z_TECHO - 0.02), material_emisor('Plafon LED', hexcol('#FFF4E2'), 1.2), col=col)
    cilindro('Reloj', 0.14, 0.03, (0.62, Y_MURO - 0.015, 2.00), plat, eje='Y', col=col, b=0.008)
    cilindro('Aro reloj', 0.15, 0.025, (0.62, Y_MURO - 0.012, 2.00), alu, eje='Y', col=col, b=0.006)
    for k in range(12):
        a = 2 * math.pi * k / 12
        caja('Marca reloj', 0.004, 0.004, 0.018, (0.62 + 0.12 * math.sin(a), Y_MURO - 0.032, 2.00 + 0.12 * math.cos(a)),
             zocalo, col, b=0)
    caja('Manecilla', 0.006, 0.004, 0.09, (0.62 + 0.02, Y_MURO - 0.035, 2.00 + 0.04), zocalo, col, b=0)
    C['exterior'] = ext
    return C


def luces(col):
    """Sol de la mañana por la ventana + luz de cielo en el vano + relleno suave del resto de la casa."""
    L = {}
    sol = bpy.data.lights.new('Sol manana', 'SUN')
    sol.energy = 6.0
    sol.angle = math.radians(0.8)
    sol.color = (1.0, 0.93, 0.84)
    so = bpy.data.objects.new('Sol manana', sol)
    col.objects.link(so)
    d = Vector((-0.85, 0.27, -0.47)).normalized()     # entra por la ventana del muro derecho, rasante
    so.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    L['sol'] = so
    vx0, vx1, vz0, vz1 = VENTANA
    cielo = bpy.data.lights.new('Cielo ventana', 'AREA')
    cielo.shape = 'RECTANGLE'
    cielo.size, cielo.size_y = vx1 - vx0, vz1 - vz0
    cielo.energy = 70
    cielo.color = (0.86, 0.92, 1.0)
    co = bpy.data.objects.new('Cielo ventana', cielo)
    col.objects.link(co)
    co.location = ((vx0 + vx1) / 2, Y_MURO + 0.02, (vz0 + vz1) / 2)
    co.rotation_euler = (math.radians(-90), 0, 0)   # mira hacia -Y (adentro)
    co.visible_camera = False
    co.visible_glossy = False
    relleno = bpy.data.lights.new('Relleno casa', 'AREA')
    relleno.shape = 'RECTANGLE'
    relleno.size, relleno.size_y = 2.2, 1.6
    relleno.energy = 25
    relleno.color = (1.0, 0.96, 0.90)
    ro = bpy.data.objects.new('Relleno casa', relleno)
    col.objects.link(ro)
    ro.location = (1.30, -1.80, 1.90)
    ro.rotation_euler = (Vector((0.55, 0.40, 0.3)) - ro.location).to_track_quat('-Z', 'Y').to_euler()
    ro.visible_camera = False
    ro.visible_glossy = False
    L['relleno'] = ro
    wy0, wy1, wz0, wz1 = VENTANA_DER
    c2 = bpy.data.lights.new('Cielo ventana der', 'AREA')
    c2.shape = 'RECTANGLE'
    c2.size, c2.size_y = wy1 - wy0, wz1 - wz0
    c2.energy = 50
    c2.color = (0.88, 0.93, 1.0)
    o2 = bpy.data.objects.new('Cielo ventana der', c2)
    col.objects.link(o2)
    o2.location = (X_DER + 0.03, (wy0 + wy1) / 2, (wz0 + wz1) / 2)
    o2.rotation_euler = (0, math.radians(90), 0)     # mira hacia -X (adentro)
    o2.visible_camera = False
    o2.visible_glossy = False
    return L


def mundo_cocina():
    w = bpy.data.worlds.new('Cielo Bogota')
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputWorld', 400, 0)
    bg = _nodo(nt, 'ShaderNodeBackground', 200, 0)
    sky = _nodo(nt, 'ShaderNodeTexSky', 0, 0)
    for t in ('MULTIPLE_SCATTERING', 'SINGLE_SCATTERING', 'NISHITA', 'HOSEK_WILKIE'):
        try:
            sky.sky_type = t
            break
        except Exception:
            continue
    for k, v in (('sun_disc', False), ('sun_elevation', math.radians(30)), ('sun_rotation', math.radians(135)),
                 ('altitude', 2600.0), ('air_density', 1.0), ('ozone_density', 1.0)):
        try:
            setattr(sky, k, v)
        except Exception:
            pass
    nt.links.new(sky.outputs[0], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 0.35
    nt.links.new(bg.outputs[0], out.inputs['Surface'])
    return w
