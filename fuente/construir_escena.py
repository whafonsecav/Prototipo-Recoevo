# Construye la escena completa de RECOEVO para un formato (h = 1920×1080, v = 1080×1920) y la guarda en .blend.
# Uso: blender -b --factory-startup --python construir_escena.py -- --aspecto h [--tiempos tiempos.json]
#      [--salida ../blend/recoevo_h.blend] [--anclas ../blend/anclas_h.json] [--glb ../exportes/recoevo.glb]
import sys
import os
import json
import time
import argparse
import bpy

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import rv_util as U          # noqa: E402
import rv_producto as RP     # noqa: E402
import rv_cocina as RC       # noqa: E402
import rv_estudio as RE      # noqa: E402
import rv_anim as RA         # noqa: E402

MARCA = r"G:\Mi unidad\Universidad\02-Semestres\03. Tercer semestre (2027-01)\01. Proceso Administrativo\04. Recoevo\03_RECOEVO_MARCA_Y_WEB"
FUENTE_LOGO = os.path.join(MARCA, 'Logo', 'SVG', 'RECOEVO_logo_horizontal_mono_verde.svg')   # relieve del frente


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--aspecto', default='h', choices=['h', 'v'])
    p.add_argument('--tiempos', default=None)
    p.add_argument('--salida', default=None)
    p.add_argument('--anclas', default=None)
    p.add_argument('--glb', default=None)
    p.add_argument('--solo_producto', action='store_true')
    return p.parse_args(a)


def main():
    t_ini = time.time()
    A = args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
    sc = bpy.context.scene
    T = dict(RA.TIEMPOS)
    if A.tiempos and os.path.exists(A.tiempos):
        with open(A.tiempos, encoding='utf-8') as fh:
            T.update(json.load(fh))
    nfot = int(round(T['dur'] * U.FPS))
    sc.render.fps = U.FPS
    sc.frame_start, sc.frame_end = 0, nfot - 1      # el fotograma nfot es idéntico al 0 (se copia al codificar)
    if A.aspecto == 'h':
        sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    else:
        sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.resolution_percentage = 100

    c_prod = U.coleccion('Producto')
    c_coc = U.coleccion('Cocina')
    c_est = U.coleccion('Estudio')
    c_cam = U.coleccion('Camaras')

    M = RP.materiales()
    fuente = FUENTE_LOGO if os.path.exists(FUENTE_LOGO) else None
    P = RP.construir(c_prod, M, fuente)
    P['A_centro'] = U.vacio('A_centro', (0, 0, 0.27), c_prod, padre=P['raiz'])
    print(f'[escena] producto listo ({len(c_prod.all_objects)} objetos) en {time.time() - t_ini:.1f} s', flush=True)

    if A.glb:
        exportar_glb(P, A.glb)
        if A.solo_producto:
            return

    RC.construir(c_coc, M)
    RC.luces(c_coc)
    w_coc = RC.mundo_cocina()
    RE.construir(c_est, RA.RAIZ)
    w_est = RE.mundo_estudio()
    sc.world = w_coc
    w_est.use_fake_user = True
    w_coc.use_fake_user = True
    c_est.hide_render = True
    print(f'[escena] cocina y estudio listos en {time.time() - t_ini:.1f} s', flush=True)

    RA.animar(P, T, A.aspecto, nfot)
    cam = RA.camara('Camara_' + A.aspecto, A.aspecto, T, nfot, c_cam)
    sc.camera = cam
    print(f'[escena] animación lista en {time.time() - t_ini:.1f} s', flush=True)

    if A.anclas:
        exportar_anclas(sc, cam, P, nfot, A.anclas, T)
        print(f'[escena] anclas exportadas en {time.time() - t_ini:.1f} s', flush=True)
    if A.salida:
        os.makedirs(os.path.dirname(os.path.abspath(A.salida)), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A.salida), compress=True)
        print(f'[escena] guardada {A.salida} en {time.time() - t_ini:.1f} s', flush=True)


def exportar_anclas(sc, cam, P, nfot, ruta, T):
    from bpy_extras.object_utils import world_to_camera_view
    W, H = sc.render.resolution_x, sc.render.resolution_y
    nombres = sorted(k for k in P if k.startswith('A_'))
    datos = {'w': W, 'h': H, 'fps': U.FPS, 'nfot': nfot, 'tiempos': T, 'anclas': {n: [] for n in nombres},
             'etiquetas': [dict(id=e[0], titulo=e[1], detalle=e[2], anclas=e[3], grupo=e[4]) for e in RA.ETIQUETAS]}
    for f in range(nfot + 1):
        sc.frame_set(f)
        for n in nombres:
            co = P[n].matrix_world.translation
            v = world_to_camera_view(sc, cam, co)
            datos['anclas'][n].append((round(v.x * W, 1), round((1 - v.y) * H, 1), round(v.z, 3)))
    with open(ruta, 'w', encoding='utf-8') as fh:
        json.dump(datos, fh, ensure_ascii=False)


def exportar_glb(P, ruta):
    """Exporta solo el producto (con sus grupos) para el prototipo web."""
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    # glTF solo entiende el Principled conectado a la salida: se quita la mezcla de rayos X
    for m in bpy.data.materials:
        nt = m.node_tree
        if nt is None:
            continue
        pr = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if pr and out:
            nt.links.new(pr.outputs['BSDF'], out.inputs['Surface'])
    for ob in bpy.context.view_layer.objects:
        ob.select_set(False)
    keep = [o for o in [P['raiz']] + list(P['raiz'].children_recursive)
            if not o.name.startswith(('Tira ', 'Grano ', 'Cascara'))]
    for o in keep:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.abspath(ruta), use_selection=True, export_apply=True,
                              export_yup=True, export_extras=True, export_draco_mesh_compression_enable=False)
    print('[escena] glb exportado', ruta, flush=True)


if __name__ == '__main__':
    main()
