/* Controles táctiles de órbita, con inercia suave:
   - un dedo (o clic izquierdo): girar;
   - dos dedos: pellizcar para acercar o alejar HACIA donde están los dedos, y arrastrar para desplazar la vista;
   - rueda del mouse: acercar hacia el puntero; clic derecho, Shift + arrastrar o rueda presionada: desplazar.
   Distingue un toque (para elegir una pieza) de un arrastre. */
(function () {
  "use strict";
  const T = THREE;

  window.Orbita = class {
    constructor(camara, elemento, objetivo) {
      this.cam = camara;
      this.el = elemento;
      this.objetivo = objetivo.clone();
      this.radio = 2.2; this.theta = 0.55; this.phi = 1.18;           // ángulos en radianes
      this.min = 0.22; this.max = 5.2;
      this.limite = new T.Box3(new T.Vector3(-0.9, -0.3, -0.9), new T.Vector3(0.9, 1.7, 0.9));   // el objetivo no se aleja del producto
      this.vt = 0; this.vp = 0;
      this.punteros = new Map();
      this.pellizco = 0;
      this.centro = null;                                             // punto medio de los dos dedos
      this.desplazando = false;
      this.alTocar = null;
      this.alInteractuar = null;
      this.destino = null;                                            // animación suave a una vista
      this._ray = new T.Raycaster();
      const el = this.el;
      el.addEventListener("pointerdown", e => this._abajo(e));
      el.addEventListener("pointermove", e => this._mover(e));
      el.addEventListener("pointerup", e => this._arriba(e));
      el.addEventListener("pointercancel", e => this._arriba(e));
      el.addEventListener("contextmenu", e => e.preventDefault());
      el.addEventListener("wheel", e => {
        e.preventDefault();
        this._interaccion();
        this._acercar(1 + e.deltaY * 0.0012, e.clientX, e.clientY);
      }, { passive: false });
    }
    _lim(r) { return Math.min(this.max, Math.max(this.min, r)); }
    _interaccion() { this.destino = null; if (this.alInteractuar) this.alInteractuar(); }

    // punto del espacio que está debajo del dedo o del puntero, sobre el plano que pasa por el objetivo
    _puntoBajo(x, y) {
      const r = this.el.getBoundingClientRect();
      this._ray.setFromCamera(new T.Vector2((x - r.left) / r.width * 2 - 1, -((y - r.top) / r.height) * 2 + 1), this.cam);
      const normal = this.cam.getWorldDirection(new T.Vector3());
      const plano = new T.Plane().setFromNormalAndCoplanarPoint(normal, this.objetivo);
      return this._ray.ray.intersectPlane(plano, new T.Vector3());
    }
    // acercar o alejar dejando quieto lo que está bajo el dedo (como en un mapa)
    _acercar(factor, x, y) {
      const nuevo = this._lim(this.radio * factor), k = nuevo / this.radio;
      if (x !== undefined) {
        const p = this._puntoBajo(x, y);
        if (p) this.objetivo.add(p.sub(this.objetivo).multiplyScalar(1 - k));
        this.objetivo.clamp(this.limite.min, this.limite.max);
      }
      this.radio = nuevo;
    }
    // desplazar la vista: el producto sigue al dedo
    _desplazar(dx, dy) {
      const alto = this.el.clientHeight || 1;
      const escala = 2 * this.radio * Math.tan(T.MathUtils.degToRad(this.cam.fov) / 2) / alto;
      const der = new T.Vector3().setFromMatrixColumn(this.cam.matrixWorld, 0);
      const arriba = new T.Vector3().setFromMatrixColumn(this.cam.matrixWorld, 1);
      this.objetivo.addScaledVector(der, -dx * escala).addScaledVector(arriba, dy * escala);
      this.objetivo.clamp(this.limite.min, this.limite.max);
    }
    _medio() { const p = [...this.punteros.values()]; return { x: (p[0].x + p[1].x) / 2, y: (p[0].y + p[1].y) / 2 }; }
    _distancia() { const p = [...this.punteros.values()]; return Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y); }

    _abajo(e) {
      try { this.el.setPointerCapture(e.pointerId); } catch (err) { /* algunos navegadores no lo permiten: sigue funcionando */ }
      this.punteros.set(e.pointerId, { x: e.clientX, y: e.clientY, x0: e.clientX, y0: e.clientY, t0: performance.now() });
      this.desplazando = e.pointerType === "mouse" && (e.button === 2 || e.button === 1 || e.shiftKey);
      if (this.punteros.size === 2) { this.pellizco = this._distancia(); this.centro = this._medio(); }
      this.vt = this.vp = 0;
      this._interaccion();
    }
    _mover(e) {
      const p = this.punteros.get(e.pointerId);
      if (!p) return;
      const dx = e.clientX - p.x, dy = e.clientY - p.y;
      p.x = e.clientX; p.y = e.clientY;
      if (this.punteros.size === 1 && this.desplazando) {
        this._desplazar(dx, dy);
      } else if (this.punteros.size === 1) {
        const k = 4.2 / Math.max(500, this.el.clientHeight);
        this.vt = -dx * k; this.vp = -dy * k;
        this.theta += this.vt; this.phi = Math.min(1.52, Math.max(0.35, this.phi + this.vp));
      } else if (this.punteros.size === 2) {
        const d = this._distancia(), m = this._medio();
        if (this.centro) this._desplazar(m.x - this.centro.x, m.y - this.centro.y);
        if (this.pellizco > 0) this._acercar(this.pellizco / d, m.x, m.y);
        this.pellizco = d; this.centro = m;
      }
    }
    _arriba(e) {
      const p = this.punteros.get(e.pointerId);
      this.punteros.delete(e.pointerId);
      if (this.punteros.size < 2) { this.pellizco = 0; this.centro = null; }
      if (this.punteros.size === 0) this.desplazando = false;
      if (p && this.alTocar && Math.hypot(e.clientX - p.x0, e.clientY - p.y0) < 9 && performance.now() - p.t0 < 450) {
        this.vt = this.vp = 0;
        this.alTocar(e.clientX, e.clientY);
      }
    }
    ir(vista, seg = 1.2) {          // vista = {theta, phi, radio, objetivo}
      this.destino = { de: { theta: this.theta, phi: this.phi, radio: this.radio, obj: this.objetivo.clone() }, a: vista, t: 0, dur: seg };
    }
    actualizar(dt, autoGiro) {
      if (this.destino) {
        const d = this.destino;
        d.t += dt;
        let k = Math.min(1, d.t / d.dur);
        k = k * k * (3 - 2 * k);
        // girar por el camino corto
        let dth = d.a.theta - d.de.theta;
        dth = Math.atan2(Math.sin(dth), Math.cos(dth));
        this.theta = d.de.theta + dth * k;
        this.phi = d.de.phi + (d.a.phi - d.de.phi) * k;
        this.radio = d.de.radio + (d.a.radio - d.de.radio) * k;
        if (d.a.objetivo) this.objetivo.copy(d.de.obj).lerp(d.a.objetivo, k);
        if (k >= 1) this.destino = null;
      } else if (this.punteros.size === 0) {
        this.theta += this.vt; this.phi = Math.min(1.52, Math.max(0.35, this.phi + this.vp));
        this.vt *= 0.92; this.vp *= 0.92;
        if (autoGiro) this.theta += dt * 0.12;
      }
      const s = Math.sin(this.phi);
      this.cam.position.set(
        this.objetivo.x + this.radio * s * Math.sin(this.theta),
        this.objetivo.y + this.radio * Math.cos(this.phi),
        this.objetivo.z + this.radio * s * Math.cos(this.theta));
      this.cam.lookAt(this.objetivo);
      this.cam.updateMatrixWorld();
    }
  };
})();
