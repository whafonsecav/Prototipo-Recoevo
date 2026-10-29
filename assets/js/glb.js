/* Lector mínimo de .glb (glTF 2.0 binario) para three.js r149 clásico.
   Soporta lo que exporta Blender para este modelo: nodos con TRS, mallas trianguladas (POSITION, NORMAL, TEXCOORD_0,
   índices) y materiales PBR de factores (color, metal, rugosidad, transparencia). Sin texturas ni animaciones. */
(function () {
  "use strict";
  const T = THREE;
  const TIPOS = { 5120: Int8Array, 5121: Uint8Array, 5122: Int16Array, 5123: Uint16Array, 5125: Uint32Array, 5126: Float32Array };
  const COMP = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 };

  function leerGLB(buf) {
    const dv = new DataView(buf);
    if (dv.getUint32(0, true) !== 0x46546c67) throw new Error("No es un archivo .glb");
    let off = 12, json = null, bin = null;
    while (off < buf.byteLength) {
      const largo = dv.getUint32(off, true), tipo = dv.getUint32(off + 4, true);
      const datos = buf.slice(off + 8, off + 8 + largo);
      if (tipo === 0x4e4f534a) json = JSON.parse(new TextDecoder().decode(datos));
      else if (tipo === 0x004e4942) bin = datos;
      off += 8 + largo;
    }
    return { json, bin };
  }

  function accesor(g, i) {
    const a = g.json.accessors[i], bv = g.json.bufferViews[a.bufferView];
    const n = COMP[a.type], Tipo = TIPOS[a.componentType];
    const inicio = (bv.byteOffset || 0) + (a.byteOffset || 0);
    const paso = bv.byteStride || 0;
    if (paso && paso !== n * Tipo.BYTES_PER_ELEMENT) {        // intercalado: copiar
      const out = new Tipo(a.count * n), dv = new DataView(g.bin);
      for (let k = 0; k < a.count; k++) for (let c = 0; c < n; c++) {
        const o = inicio + k * paso + c * Tipo.BYTES_PER_ELEMENT;
        out[k * n + c] = Tipo === Float32Array ? dv.getFloat32(o, true) : Tipo === Uint16Array ? dv.getUint16(o, true) : dv.getUint32(o, true);
      }
      return { arr: out, n };
    }
    return { arr: new Tipo(g.bin, inicio, a.count * n), n };
  }

  function material(g, i) {
    if (i === undefined) return new T.MeshStandardMaterial({ color: 0xcccccc, roughness: 0.6 });
    const m = g.json.materials[i], p = m.pbrMetallicRoughness || {};
    const c = p.baseColorFactor || [1, 1, 1, 1];
    const mat = new T.MeshStandardMaterial({
      color: new T.Color().fromArray(c), metalness: p.metallicFactor ?? 1, roughness: p.roughnessFactor ?? 1,
      side: m.doubleSided ? T.DoubleSide : T.FrontSide, name: m.name || ""
    });
    const ext = m.extensions || {};
    const trans = ext.KHR_materials_transmission ? ext.KHR_materials_transmission.transmissionFactor || 0 : 0;
    if (m.alphaMode === "BLEND" || c[3] < 1 || trans > 0) {
      mat.transparent = true;
      mat.opacity = Math.min(c[3], 1 - trans * 0.6);
      mat.depthWrite = false;
    }
    if (m.emissiveFactor) mat.emissive.fromArray(m.emissiveFactor);
    return mat;
  }

  function malla(g, i, mats) {
    const grupo = new T.Group();
    for (const pr of g.json.meshes[i].primitives) {
      const geo = new T.BufferGeometry();
      const at = pr.attributes;
      const pos = accesor(g, at.POSITION);
      geo.setAttribute("position", new T.BufferAttribute(pos.arr, 3));
      if (at.NORMAL !== undefined) geo.setAttribute("normal", new T.BufferAttribute(accesor(g, at.NORMAL).arr, 3));
      else geo.computeVertexNormals();
      if (at.TEXCOORD_0 !== undefined) geo.setAttribute("uv", new T.BufferAttribute(accesor(g, at.TEXCOORD_0).arr, 2));
      if (pr.indices !== undefined) geo.setIndex(new T.BufferAttribute(accesor(g, pr.indices).arr, 1));
      geo.computeBoundingSphere();
      if (!mats[pr.material]) mats[pr.material] = material(g, pr.material);
      const me = new T.Mesh(geo, mats[pr.material]);
      me.castShadow = true;
      me.receiveShadow = true;
      grupo.add(me);
    }
    return grupo.children.length === 1 ? grupo.children[0] : grupo;
  }

  function nodo(g, i, mats, porNombre) {
    const n = g.json.nodes[i];
    const ob = n.mesh !== undefined ? malla(g, n.mesh, mats) : new T.Group();
    ob.name = n.name || "";
    if (n.matrix) { const M = new T.Matrix4().fromArray(n.matrix); M.decompose(ob.position, ob.quaternion, ob.scale); }
    else {
      if (n.translation) ob.position.fromArray(n.translation);
      if (n.rotation) ob.quaternion.fromArray(n.rotation);
      if (n.scale) ob.scale.fromArray(n.scale);
    }
    if (ob.name) porNombre[ob.name] = ob;
    for (const h of n.children || []) ob.add(nodo(g, h, mats, porNombre));
    return ob;
  }

  window.cargarGLB = async function (url, alAvanzar) {
    const r = await fetch(url);
    if (!r.ok) throw new Error("No se pudo leer el modelo (" + r.status + ")");
    let buf;
    const total = +r.headers.get("content-length") || 0;
    if (r.body && total && alAvanzar) {
      const lector = r.body.getReader(), partes = [];
      let leido = 0;
      for (;;) {
        const { done, value } = await lector.read();
        if (done) break;
        partes.push(value);
        leido += value.length;
        alAvanzar(leido / total);
      }
      const u = new Uint8Array(leido);
      let o = 0;
      for (const p of partes) { u.set(p, o); o += p.length; }
      buf = u.buffer;
    } else buf = await r.arrayBuffer();
    const g = leerGLB(buf);
    const mats = {}, porNombre = {};
    const escena = new T.Group();
    const s = g.json.scenes[g.json.scene || 0];
    for (const i of s.nodes) escena.add(nodo(g, i, mats, porNombre));
    return { escena, porNombre };
  };
})();
