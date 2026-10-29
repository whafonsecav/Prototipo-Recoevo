#!/usr/bin/env bash
# Render final de los dos formatos (se puede reanudar: Blender salta los fotogramas que ya existen).
# Tramos: cocina 0–2030 y 2820–3304; estudio 1940–2930 (los cruces de la transición tienen los dos pases).
cd "$(dirname "$0")"
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
OPC="--muestras 40 --umbral 0.04 --rapido"
for a in h v; do
  for tramo in "cocina 0 2030" "estudio 1940 2930" "cocina 2820 3280"; do
    set -- $tramo
    echo "[$(date +%H:%M:%S)] $a $1 $2-$3"
    "$B" -b ../blend/recoevo_$a.blend --python render.py -- --pase $1 --ini $2 --fin $3 --salida ../frames/$a/$1 $OPC 2>&1 \
      | grep -E "hardware|terminado|Error|Traceback"
  done
done
echo "[$(date +%H:%M:%S)] render terminado"
