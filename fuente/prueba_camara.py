# Renderiza fotos de prueba con cámaras candidatas (sin tocar la animación guardada).
# Uso: blender -b escena.blend --python prueba_camara.py -- --json candidatos.json --salida carpeta [--pase cocina]
import sys
import os
import json
import argparse
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as RD  # noqa: E402


def main():
    a = sys.argv[sys.argv.index('--') + 1:]
    p = argparse.ArgumentParser()
    p.add_argument('--json', required=True)
    p.add_argument('--salida', required=True)
    p.add_argument('--pase', default='cocina')
    p.add_argument('--muestras', type=int, default=64)
    p.add_argument('--escala', type=int, default=50)
    A = p.parse_args(a)
    RD.configurar(argparse.Namespace(pase=A.pase, muestras=A.muestras, umbral=0.03, escala=A.escala))
    sc = bpy.context.scene
    cam = sc.camera
    cam.animation_data_clear()
    cam.data.animation_data_clear()
    salida = os.path.abspath(A.salida)
    os.makedirs(salida, exist_ok=True)
    with open(A.json, encoding='utf-8') as fh:
        cands = json.load(fh)
    for c in cands:
        sc.frame_set(c.get('f', 0))
        if 'aspecto' in c:
            sc.render.resolution_x, sc.render.resolution_y = (1920, 1080) if c['aspecto'] == 'h' else (1080, 1920)
        cam.rotation_mode = 'QUATERNION'
        cam.location = c['loc']
        cam.rotation_quaternion = (Vector(c['tgt']) - Vector(c['loc'])).to_track_quat('-Z', 'Y')
        cam.data.lens = c['lens']
        cam.data.dof.aperture_fstop = c.get('f_stop', 2.8)
        cam.data.dof.focus_distance = (Vector(c['tgt']) - Vector(c['loc'])).length
        sc.render.filepath = os.path.join(salida, c['nombre'] + '.png')
        bpy.ops.render.render(write_still=True)
        print('[prueba]', c['nombre'], flush=True)


main()
