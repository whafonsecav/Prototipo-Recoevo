# Renderiza un pase (cocina o estudio) de la escena con Cycles.
# Uso: blender -b ../blend/recoevo_h.blend --python render.py -- --pase cocina --ini 0 --fin 1349 --salida ../frames/h/cocina
#      [--muestras 160] [--umbral 0.015] [--fotos 0,600,1200] [--escala 100]
# Autodetecta la GPU (OptiX > CUDA > CPU) y usa todos los hilos de la CPU para lo que la GPU no hace.
import sys
import os
import time
import argparse
import platform
import bpy


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--pase', default='cocina', choices=['cocina', 'estudio'])
    p.add_argument('--ini', type=int, default=None)
    p.add_argument('--fin', type=int, default=None)
    p.add_argument('--fotos', default=None, help='lista de fotogramas sueltos separados por coma')
    p.add_argument('--salida', required=True)
    p.add_argument('--muestras', type=int, default=160)
    p.add_argument('--umbral', type=float, default=0.015)
    p.add_argument('--escala', type=int, default=100)
    p.add_argument('--paso', type=int, default=1)
    p.add_argument('--rapido', action='store_true', help='menos rebotes + GI rápida (calidad casi igual con el denoiser)')
    return p.parse_args(a)


def configurar_dispositivo():
    prefs = bpy.context.preferences.addons['cycles'].preferences
    elegido = None
    for tipo in ('OPTIX', 'CUDA', 'HIP', 'ONEAPI', 'METAL'):
        try:
            prefs.compute_device_type = tipo
            prefs.refresh_devices()
        except Exception:
            continue
        gpus = [d for d in prefs.devices if d.type == tipo]
        if gpus:
            for d in prefs.devices:
                d.use = (d.type == tipo)
            elegido = (tipo, [d.name for d in gpus])
            break
    sc = bpy.context.scene
    if elegido:
        sc.cycles.device = 'GPU'
    else:
        sc.cycles.device = 'CPU'
        prefs.compute_device_type = 'NONE'
    hilos = os.cpu_count() or 1
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = hilos
    try:
        import psutil  # noqa: F401
        ram = f'{psutil.virtual_memory().available / 2**30:.1f} GB libres'
    except Exception:
        ram = 'RAM no medida (psutil no está en el Python de Blender)'
    print(f'[hardware] CPU: {platform.processor() or "?"} · {hilos} hilos lógicos (usados: {hilos}) · {ram}', flush=True)
    print(f'[hardware] Render en: {elegido[0] + " " + ", ".join(elegido[1]) if elegido else "CPU (sin GPU compatible)"}', flush=True)


def configurar(A):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    configurar_dispositivo()
    cy = sc.cycles
    cy.samples = A.muestras
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = A.umbral
    cy.adaptive_min_samples = 24
    cy.use_denoising = True
    try:
        cy.denoiser = 'OPENIMAGEDENOISE'
        cy.denoising_use_gpu = True
        cy.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        cy.denoising_prefilter = 'ACCURATE'
        cy.denoising_quality = 'HIGH'
    except Exception as e:
        print('[aviso] denoiser:', e)
    cy.use_animated_seed = False
    cy.seed = 7
    cy.max_bounces = 10
    cy.diffuse_bounces = 4
    cy.glossy_bounces = 4
    cy.transmission_bounces = 8
    cy.transparent_max_bounces = 24
    cy.sample_clamp_indirect = 6.0
    if getattr(A, 'rapido', False):
        cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 6, 3, 3, 4
        cy.transparent_max_bounces = 16
        try:
            cy.use_fast_gi = True
            cy.fast_gi_method = 'ADD'
            sc.world.light_settings.distance = 2.0
        except Exception as e:
            print('[aviso] fast GI:', e)
    cy.blur_glossy = 0.6
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    sc.render.use_persistent_data = True
    sc.render.film_transparent = False
    sc.render.resolution_percentage = A.escala
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.view_settings.exposure = -1.0 if A.pase == 'cocina' else -0.9
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.image_settings.color_depth = '8'
    sc.render.image_settings.compression = 15
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    # pase: qué colección y qué mundo
    coc, est = bpy.data.collections['Cocina'], bpy.data.collections['Estudio']
    coc.hide_render = A.pase != 'cocina'
    est.hide_render = A.pase != 'estudio'
    sc.world = bpy.data.worlds['Cielo Bogota' if A.pase == 'cocina' else 'Estudio']


def main():
    A = args()
    configurar(A)
    sc = bpy.context.scene
    A.salida = os.path.abspath(A.salida)
    os.makedirs(A.salida, exist_ok=True)
    t0 = time.time()
    if A.fotos:
        for f in [int(x) for x in A.fotos.split(',')]:
            sc.frame_set(f)
            sc.render.filepath = os.path.join(A.salida, f'f{f:05d}.png')
            bpy.ops.render.render(write_still=True)
            print(f'[render] {A.pase} f{f} en {time.time() - t0:.1f} s', flush=True)
    else:
        sc.frame_start = A.ini if A.ini is not None else sc.frame_start
        sc.frame_end = A.fin if A.fin is not None else sc.frame_end
        sc.frame_step = A.paso
        sc.render.filepath = os.path.join(A.salida, 'f#####')
        bpy.ops.render.render(animation=True)
    print(f'[render] terminado en {time.time() - t0:.1f} s', flush=True)


if __name__ == '__main__':
    main()
