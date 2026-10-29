/* Controles táctiles de órbita: un dedo gira, dos dedos acercan (pellizco), rueda del mouse acerca.
   Con inercia suave. Distingue un toque (para elegir una pieza) de un arrastre. */
(function () {
  "use strict";
  const T = THREE;

  window.Orbita = class {
    constructor(camara, elemento, objetivo) {
      this.cam = camara;
      this.el = elemento;
      this.objetivo = objetivo.clone();
      this.radio = 2.2; this.theta = 0.55; this.phi = 1.18;           // ángulos en radianes
      this.min = 0.9; this.max = 4.2;
      this.vt = 0; this.vp = 0;
      this.punteros = new Map();
      this.pellizco = 0;
      this.alTocar = null;
      this.alInteractuar = null;
      this.destino = null;                                            // animación suave a una vista
      const el = this.el;
      el.addEventListener("pointerdown", e => this._abajo(e));
      el.addEventListener("pointermove", e => this._mover(e));
      el.addEventListener("pointerup", e => this._arriba(e));
      el.addEventListener("pointercancel", e => this._arriba(e));
      el.addEventListener("wheel", e => { e.preventDefault(); this._interaccion(); this.radio = this._lim(this.radio * (1 + e.deltaY * 0.0012)); }, { passive: false });
    }
    _lim(r) { return Math.min(this.max, Math.max(this.min, r)); }
    _interaccion() { this.destino = null; if (this.alInteractuar) this.alInteractuar(); }
    _abajo(e) {
      this.el.setPointerCapture(e.pointerId);
      this.punteros.set(e.pointerId, { x: e.clientX, y: e.clientY, x0: e.clientX, y0: e.clientY, t0: performance.now() });
      if (this.punteros.size === 2) this.pellizco = this._distancia();
      this._interaccion();
    }
    _distancia() { const p = [...this.punteros.values()]; return Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y); }
    _mover(e) {
      const p = this.punteros.get(e.pointerId);
      if (!p) return;
      const dx = e.clientX - p.x, dy = e.clientY - p.y;
      p.x = e.clientX; p.y = e.clientY;
      if (this.punteros.size === 1) {
        const k = 4.2 / Math.max(500, this.el.clientHeight);
        this.vt = -dx * k; this.vp = -dy * k;
        this.theta += this.vt; this.phi = Math.min(1.52, Math.max(0.35, this.phi + this.vp));
      } else if (this.punteros.size === 2) {
        const d = this._distancia();
        if (this.pellizco > 0) this.radio = this._lim(this.radio * this.pellizco / d);
        this.pellizco = d;
      }
    }
    _arriba(e) {
      const p = this.punteros.get(e.pointerId);
      this.punteros.delete(e.pointerId);
      if (this.punteros.size < 2) this.pellizco = 0;
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
    }
  };
})();
