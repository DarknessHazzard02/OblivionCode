// seguro.js
// Todo texto que venga de DATOS (SAP, Oracle, una hoja de Google, meta.json,
// la URL) se pinta como texto, nunca como HTML. Si un tablero arma HTML con
// plantillas (`...${x}...`), cada dato va dentro de esc():
//
//     el.innerHTML = `<td>${esc(r.proveedor)}</td>`;
//
// Mejor aun, cuando no hace falta HTML: el.textContent = r.proveedor.
//
// Para pasar un dato a un manejador en linea (onclick="f('...')") no basta
// esc(): el dato vive dentro de JavaScript. Ahi va escArg(), que lo convierte
// en un literal de JS y luego lo escapa para el atributo:
//
//     `<button onclick="abrir(${escArg(r.id)})">`
//
// Lo carga cada tablero ANTES de su propio <script>:
//     <script src="/shared/js/seguro.js"></script>

(function () {
  const MAPA = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;", "`": "&#96;" };

  function esc(v) {
    if (v === null || v === undefined) return "";
    return String(v).replace(/[&<>"'`]/g, c => MAPA[c]);
  }

  function escArg(v) {
    return esc(JSON.stringify(v === undefined ? null : v));
  }

  window.esc = esc;
  window.escArg = escArg;
})();
