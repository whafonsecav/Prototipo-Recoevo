# Espacio limpio donde el equipo flota y se despieza: ciclorama gris cálido muy claro con luz suave de estudio.
import math
import bpy
import bmesh
from mathutils import Vector
from rv_util import hexcol, material, objeto, _nodo


def construir(col, centro):
    cx, cy = centro[0], centro[1]
    bm = bmesh.new()
    # perfil: piso desde el frente, curva de 1,8 m de radio, pared al fondo
    perfil = []
    for i in range(10):
        perfil.append((cy - 7.0 + i * 0.75, 0.0))
    R = 1.8
    y0 = cy + 1.2
    for i in range(1, 17):
        a = math.radians(90 * i / 16)
        perfil.append((y0 + R * math.sin(a), R * (1 - math.cos(a))))
    perfil.append((y0 + R, 7.0))
    filas = []
    for (y, z) in perfil:
        filas.append([bm.verts.new((cx + x, y, z)) for x in (-7.0, 7.0)])
    for i in range(len(filas) - 1):
        bm.faces.new((filas[i][0], filas[i][1], filas[i + 1][1], filas[i + 1][0]))
    m = material('Ciclorama', hexcol('#E3E7E1'), 0.85)
    ob = objeto('Ciclorama', bm, m, col, angulo=89)
    # luces suaves
    def area(nombre, loc, objetivo, tam, energia, color=(1, 1, 1)):
        li = bpy.data.lights.new(nombre, 'AREA')
        li.shape = 'DISK'
        li.size = tam
        li.energy = energia
        li.color = color
        o = bpy.data.objects.new(nombre, li)
        col.objects.link(o)
        o.location = loc
        o.rotation_euler = (Vector(objetivo) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        o.visible_camera = False
        return o
    obj = (cx, cy, 0.45)
    area('Clave', (cx - 1.5, cy - 1.7, 2.1), obj, 1.8, 300, (1.0, 0.97, 0.93))
    area('Relleno', (cx + 1.9, cy - 1.2, 1.0), obj, 2.0, 55, (0.95, 0.98, 1.0))
    area('Contraluz', (cx + 0.6, cy + 1.6, 1.9), obj, 1.6, 200)
    area('Cenital', (cx, cy - 0.2, 2.6), obj, 2.5, 70)
    return ob


def mundo_estudio():
    w = bpy.data.worlds.new('Estudio')
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = _nodo(nt, 'ShaderNodeOutputWorld', 300, 0)
    bg = _nodo(nt, 'ShaderNodeBackground', 100, 0)
    bg.inputs['Color'].default_value = hexcol('#E9EDE7')
    bg.inputs['Strength'].default_value = 0.12
    nt.links.new(bg.outputs[0], out.inputs['Surface'])
    return w
