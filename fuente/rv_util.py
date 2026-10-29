# Utilidades para construir la escena de RECOEVO en Blender 5.2 (bpy).
# Mallas paramétricas, materiales PBR y fotogramas clave densos (interpolación lineal).
import math
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler, Quaternion

FPS = 30


# ---------------------------------------------------------------- color
def srgb_a_lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexcol(h, a=1.0):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return (srgb_a_lineal(r), srgb_a_lineal(g), srgb_a_lineal(b), a)


# ---------------------------------------------------------------- colecciones
def coleccion(nombre, padre=None):
    c = bpy.data.collections.get(nombre)
    if c is None:
        c = bpy.data.collections.new(nombre)
        (padre or bpy.context.scene.collection).children.link(c)
    return c


# ---------------------------------------------------------------- materiales
def nuevo_material(nombre):
    m = bpy.data.materials.new(nombre)
    if m.node_tree is None:
        m.use_nodes = True
    return m


def _nodo(nt, tipo, x=0, y=0):
    n = nt.nodes.new(tipo)
    n.location = (x, y)
    return n


def material(nombre, color, rugosidad=0.5, metal=0.0, bump=0.0, escala_bump=400.0,
             coat=0.0, transmision=0.0, alpha=1.0, sss=0.0, aniso=0.0, emision=None,
             fantasma=False, ior=1.45, thin=False, ruido_color=0.0, escala_color=30.0, color2=None):
    """Principled BSDF con extras opcionales.
    fantasma=True añade un nodo Valor 'fantasma' (0 opaco .. 1 transparente) para la vista de rayos X."""
    m = nuevo_material(nombre)
    nt = m.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputMaterial', 900, 0)
    p = _nodo(nt, 'ShaderNodeBsdfPrincipled', 300, 0)
    p.inputs['Base Color'].default_value = color
    p.inputs['Roughness'].default_value = rugosidad
    p.inputs['Metallic'].default_value = metal
    p.inputs['IOR'].default_value = ior
    if coat:
        p.inputs['Coat Weight'].default_value = coat
        p.inputs['Coat Roughness'].default_value = 0.08
    if transmision:
        p.inputs['Transmission Weight'].default_value = transmision
    if thin:
        p.inputs['Thin Wall'].default_value = True
    if sss:
        p.inputs['Subsurface Weight'].default_value = sss
        p.inputs['Subsurface Radius'].default_value = (0.6, 0.5, 0.4)
        p.inputs['Subsurface Scale'].default_value = 0.004
    if aniso:
        p.inputs['Anisotropic'].default_value = aniso
    if emision is not None:
        p.inputs['Emission Color'].default_value = emision[0]
        p.inputs['Emission Strength'].default_value = emision[1]
    if alpha < 1.0:
        p.inputs['Alpha'].default_value = alpha
    if ruido_color > 0:
        # variación de color con ruido (madera, aserrín, cáscaras, granito)
        tc = _nodo(nt, 'ShaderNodeTexCoord', -900, 300)
        nz = _nodo(nt, 'ShaderNodeTexNoise', -700, 300)
        nz.inputs['Scale'].default_value = escala_color
        nz.inputs['Detail'].default_value = 6.0
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
        mix = _nodo(nt, 'ShaderNodeMix', -300, 300)
        mix.data_type = 'RGBA'
        mix.inputs['Factor'].default_value = 0.5
        nt.links.new(nz.outputs['Fac'], mix.inputs['Factor'])
        mix.inputs['A'].default_value = color
        mix.inputs['B'].default_value = color2 if color2 else tuple(c * (1 - ruido_color) for c in color[:3]) + (1,)
        nt.links.new(mix.outputs['Result'], p.inputs['Base Color'])
    if bump > 0:
        tc = _nodo(nt, 'ShaderNodeTexCoord', -900, -300)
        nz = _nodo(nt, 'ShaderNodeTexNoise', -700, -300)
        nz.inputs['Scale'].default_value = escala_bump
        nz.inputs['Detail'].default_value = 4.0
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
        bn = _nodo(nt, 'ShaderNodeBump', -300, -300)
        bn.inputs['Strength'].default_value = bump
        bn.inputs['Distance'].default_value = 0.0005
        nt.links.new(nz.outputs['Fac'], bn.inputs['Height'])
        nt.links.new(bn.outputs['Normal'], p.inputs['Normal'])
    salida = p.outputs['BSDF']
    if fantasma:
        # rayos X: mezcla con transparente + un borde tenue (fresnel) para leer la forma
        v = _nodo(nt, 'ShaderNodeValue', 300, 350)
        v.name = v.label = 'fantasma'
        v.outputs[0].default_value = 0.0
        tr = _nodo(nt, 'ShaderNodeBsdfTransparent', 400, 220)
        lw = _nodo(nt, 'ShaderNodeLayerWeight', 300, 500)
        lw.inputs['Blend'].default_value = 0.35
        mul = _nodo(nt, 'ShaderNodeMath', 520, 420)
        mul.operation = 'MULTIPLY'
        nt.links.new(lw.outputs['Facing'], mul.inputs[0])
        mul.inputs[1].default_value = 0.35
        inv = _nodo(nt, 'ShaderNodeMath', 620, 380)
        inv.operation = 'SUBTRACT'
        nt.links.new(v.outputs[0], inv.inputs[0])
        nt.links.new(mul.outputs[0], inv.inputs[1])
        clamp = _nodo(nt, 'ShaderNodeClamp', 700, 380)
        nt.links.new(inv.outputs[0], clamp.inputs['Value'])
        mx = _nodo(nt, 'ShaderNodeMixShader', 760, 0)
        nt.links.new(clamp.outputs[0], mx.inputs['Fac'])
        nt.links.new(salida, mx.inputs[1])
        nt.links.new(tr.outputs[0], mx.inputs[2])
        salida = mx.outputs[0]
    nt.links.new(salida, out.inputs['Surface'])
    return m


def material_emisor(nombre, color, fuerza):
    m = nuevo_material(nombre)
    nt = m.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputMaterial', 300, 0)
    e = _nodo(nt, 'ShaderNodeEmission', 0, 0)
    e.inputs['Color'].default_value = color
    e.inputs['Strength'].default_value = fuerza
    nt.links.new(e.outputs[0], out.inputs['Surface'])
    return m


def vidrio_delgado(nombre, reflejo=0.12):
    """Vidrio de ventana sin refracción (transparente + reflejo por fresnel): limpio de ruido."""
    m = nuevo_material(nombre)
    nt = m.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputMaterial', 600, 0)
    tr = _nodo(nt, 'ShaderNodeBsdfTransparent', 0, 100)
    gl = _nodo(nt, 'ShaderNodeBsdfGlossy', 0, -100)
    gl.inputs['Roughness'].default_value = 0.02
    fr = _nodo(nt, 'ShaderNodeFresnel', 0, 300)
    fr.inputs['IOR'].default_value = 1.5
    mul = _nodo(nt, 'ShaderNodeMath', 200, 300)
    mul.operation = 'MULTIPLY'
    nt.links.new(fr.outputs[0], mul.inputs[0])
    mul.inputs[1].default_value = reflejo / 0.04
    mx = _nodo(nt, 'ShaderNodeMixShader', 400, 0)
    nt.links.new(mul.outputs[0], mx.inputs['Fac'])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])
    return m


def material_atributo(nombre, rugosidad=0.6, bump=0.0, attr='Col'):
    """Color por cara/vértice desde un atributo (montones de tiras, aserrín)."""
    m = nuevo_material(nombre)
    nt = m.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputMaterial', 600, 0)
    p = _nodo(nt, 'ShaderNodeBsdfPrincipled', 300, 0)
    p.inputs['Roughness'].default_value = rugosidad
    at = _nodo(nt, 'ShaderNodeAttribute', 0, 0)
    at.attribute_name = attr
    nt.links.new(at.outputs['Color'], p.inputs['Base Color'])
    if bump:
        nz = _nodo(nt, 'ShaderNodeTexNoise', -300, -300)
        nz.inputs['Scale'].default_value = 600
        bn = _nodo(nt, 'ShaderNodeBump', 0, -300)
        bn.inputs['Strength'].default_value = bump
        bn.inputs['Distance'].default_value = 0.0004
        nt.links.new(nz.outputs['Fac'], bn.inputs['Height'])
        nt.links.new(bn.outputs['Normal'], p.inputs['Normal'])
    nt.links.new(p.outputs['BSDF'], out.inputs['Surface'])
    return m


# ---------------------------------------------------------------- mallas
def objeto(nombre, bm, mat=None, col=None, suave=True, angulo=32, padre=None):
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nombre, me)
    (col or bpy.context.scene.collection).objects.link(ob)
    if mat is not None:
        if isinstance(mat, (list, tuple)):
            for mm in mat:
                me.materials.append(mm)
        else:
            me.materials.append(mat)
    if suave:
        me.shade_smooth()
        try:
            me.set_sharp_from_angle(angle=math.radians(angulo))
        except Exception:
            pass
    if padre is not None:
        ob.parent = padre
    return ob


def bisel(ob, ancho, segmentos=3, angulo=35, duro=True):
    md = ob.modifiers.new('Bisel', 'BEVEL')
    md.width = ancho
    md.segments = segmentos
    md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(angulo)
    md.harden_normals = duro
    md.use_clamp_overlap = True
    return md


def bm_caja(sx, sy, sz, c=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx + c[0], v.co.y * sy + c[1], v.co.z * sz + c[2]))
    return bm


def caja(nombre, sx, sy, sz, c, mat, col=None, b=0.002, seg=3, padre=None):
    ob = objeto(nombre, bm_caja(sx, sy, sz, c), mat, col)
    if b > 0:
        bisel(ob, b, seg)
    if padre is not None:
        ob.parent = padre
    return ob


def pts_rect_redondeado(sx, sy, r, seg=10, cx=0.0, cy=0.0):
    r = min(r, sx / 2 - 1e-5, sy / 2 - 1e-5)
    pts = []
    esquinas = [(sx / 2 - r, sy / 2 - r, 0), (-sx / 2 + r, sy / 2 - r, 90),
                (-sx / 2 + r, -sy / 2 + r, 180), (sx / 2 - r, -sy / 2 + r, 270)]
    for (x, y, a0) in esquinas:
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((cx + x + r * math.cos(a), cy + y + r * math.sin(a)))
    return pts


def bm_prisma(pts, z0, z1, tapa_inf=True, tapa_sup=True):
    """Extruye un polígono 2D (XY) entre z0 y z1."""
    bm = bmesh.new()
    a = [bm.verts.new((x, y, z0)) for x, y in pts]
    b = [bm.verts.new((x, y, z1)) for x, y in pts]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    if tapa_inf:
        bm.faces.new(list(reversed(a)))
    if tapa_sup:
        bm.faces.new(b)
    bm.normal_update()
    return bm


def bm_tina(pts_inf, pts_sup, z0, z1, fondo=True):
    """Superficie abierta arriba entre dos contornos (mismo número de puntos)."""
    bm = bmesh.new()
    a = [bm.verts.new((x, y, z0)) for x, y in pts_inf]
    b = [bm.verts.new((x, y, z1)) for x, y in pts_sup]
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    if fondo:
        bm.faces.new(list(reversed(a)))
    bm.normal_update()
    return bm


def bm_cilindro(r, h, seg=48, r2=None, eje='Z', c=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2), depth=h)
    rot = {'Z': Matrix.Identity(4), 'X': Matrix.Rotation(math.radians(90), 4, 'Y'),
           'Y': Matrix.Rotation(math.radians(90), 4, 'X')}[eje]
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ rot, verts=bm.verts)
    return bm


def cilindro(nombre, r, h, c, mat, eje='Z', seg=48, col=None, b=0.0, r2=None, padre=None):
    ob = objeto(nombre, bm_cilindro(r, h, seg, r2, eje, c), mat, col, angulo=40)
    if b > 0:
        bisel(ob, b, 2, 50)
    if padre is not None:
        ob.parent = padre
    return ob


def bm_toro(R, r, segM=48, segm=16, eje='Z', c=(0, 0, 0)):
    bm = bmesh.new()
    anillos = []
    for i in range(segM):
        a = 2 * math.pi * i / segM
        fila = []
        for j in range(segm):
            b = 2 * math.pi * j / segm
            x = (R + r * math.cos(b)) * math.cos(a)
            y = (R + r * math.cos(b)) * math.sin(a)
            z = r * math.sin(b)
            fila.append(bm.verts.new((x, y, z)))
        anillos.append(fila)
    for i in range(segM):
        for j in range(segm):
            i2, j2 = (i + 1) % segM, (j + 1) % segm
            bm.faces.new((anillos[i][j], anillos[i2][j], anillos[i2][j2], anillos[i][j2]))
    rot = {'Z': Matrix.Identity(4), 'X': Matrix.Rotation(math.radians(90), 4, 'Y'),
           'Y': Matrix.Rotation(math.radians(90), 4, 'X')}[eje]
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ rot, verts=bm.verts)
    bm.normal_update()
    return bm


def bm_perfil_eje_x(pts_yz, x0, x1):
    """Polígono en el plano YZ extruido a lo largo de X (engranajes, cuchillas, cremallera)."""
    bm = bmesh.new()
    a = [bm.verts.new((x0, y, z)) for y, z in pts_yz]
    b = [bm.verts.new((x1, y, z)) for y, z in pts_yz]
    n = len(pts_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], b[i], b[j], a[j]))
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    bm.normal_update()
    # normales consistentes hacia afuera
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def unir_bm(bms):
    """Une varias bmesh en una sola."""
    me = bpy.data.meshes.new('_tmp')
    out = bmesh.new()
    for bm in bms:
        bm.to_mesh(me)
        out.from_mesh(me)
        bm.free()
    bpy.data.meshes.remove(me)
    return out


def booleana(ob, cortador, op='DIFFERENCE', aplicar=True):
    md = ob.modifiers.new('Bool', 'BOOLEAN')
    md.operation = op
    md.object = cortador
    md.solver = 'EXACT'
    if aplicar:
        aplicar_mod(ob, md.name)
    return md


def aplicar_mod(ob, nombre):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=nombre)


def borrar(ob):
    me = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    if me is not None and me.users == 0:
        bpy.data.meshes.remove(me)


def vacio(nombre, c=(0, 0, 0), col=None, padre=None, tam=0.02):
    e = bpy.data.objects.new(nombre, None)
    e.empty_display_size = tam
    e.location = c
    (col or bpy.context.scene.collection).objects.link(e)
    if padre is not None:
        e.parent = padre
    return e


def pivote(nombre, c, col=None, padre=None):
    """Vacío que hace de pivote; los hijos se cuelgan con su posición mundial conservada."""
    return vacio(nombre, c, col, padre)


def mundo(ob):
    """Matriz mundial calculada a mano (sin depender de que el depsgraph esté actualizado)."""
    m = ob.matrix_basis.copy()
    while ob.parent is not None:
        m = mundo(ob.parent) @ ob.matrix_parent_inverse @ m
        break
    return m


def colgar(hijo, padre):
    """Emparenta conservando la posición mundial (el hijo aún no tiene padre)."""
    hijo.parent = padre
    hijo.matrix_parent_inverse = mundo(padre).inverted()


# ---------------------------------------------------------------- animación
def suave(x):  # easeInOut (smootherstep)
    x = max(0.0, min(1.0, x))
    return x * x * x * (x * (x * 6 - 15) + 10)


def suave_sal(x):  # easeOut cúbico
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def suave_ent(x):  # easeIn cúbico
    x = max(0.0, min(1.0, x))
    return x ** 3


class Pista:
    """Valor animado (escalar o vector) como lista de tramos (t0, t1, v_destino, ease).
    Fuera de los tramos el valor se mantiene. Se muestrea a fotogramas enteros."""

    def __init__(self, v0):
        self.v0 = v0
        self.tramos = []

    def a(self, t0, t1, v, ease=suave):
        self.tramos.append((t0, t1, v, ease))
        return self

    def valor(self, t):
        v = self.v0
        for (t0, t1, vd, ease) in sorted(self.tramos, key=lambda s: s[0]):
            if t <= t0:
                break
            k = ease((t - t0) / max(1e-6, t1 - t0)) if t < t1 else 1.0
            v = mezclar(v, vd, k)
        return v

    def fotogramas_activos(self, nfot):
        """Fotogramas donde hay movimiento (más los bordes) para no llenar de claves los reposos."""
        fs = set([0, nfot])
        for (t0, t1, _, _) in self.tramos:
            f0, f1 = int(math.floor(t0 * FPS)) - 1, int(math.ceil(t1 * FPS)) + 1
            fs.update(range(max(0, f0), min(nfot, f1) + 1))
        return sorted(fs)


def mezclar(a, b, k):
    if isinstance(a, (int, float)):
        return a + (b - a) * k
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def claves(obj, ruta, pista, nfot, indice=-1, fotos=None):
    fotos = fotos if fotos is not None else pista.fotogramas_activos(nfot)
    for f in fotos:
        v = pista.valor(f / FPS)
        if indice >= 0:
            getattr(obj, ruta)[indice] = v
        else:
            setattr(obj, ruta, v)
        obj.keyframe_insert(ruta, index=indice, frame=f)


def claves_socket(socket, pista, nfot):
    for f in pista.fotogramas_activos(nfot):
        socket.default_value = pista.valor(f / FPS)
        socket.keyframe_insert('default_value', frame=f)


def mirar(loc, objetivo, roll=0.0):
    d = Vector(objetivo) - Vector(loc)
    q = d.to_track_quat('-Z', 'Y')
    if roll:
        q = q @ Quaternion((0, 0, 1), roll)
    return q
