// csv.js
// Celdas de CSV que Excel abre sin ejecutar nada.
//
// Excel (y LibreOffice) toman como FORMULA una celda que empieza con
// = + - @, tabulador o retorno de carro, aunque vaya entre comillas. Un texto
// que llega de SAP, de un Excel de proveedor o de una captura manual como
// =HYPERLINK("http://...","Ver") se ejecuta al abrir el CSV. La regla (OWASP
// "CSV Injection"): a ESOS textos se les antepone un apostrofo.
//
//     csvNeutral("=HYPERLINK(...)")  -> "'=HYPERLINK(...)"
//     csvNeutral("-cmd")             -> "'-cmd"
//     csvNeutral(-5)                 -> -5        (numero: no se toca)
//     csvNeutral("-1234.50")         -> "-1234.50" (numero en texto: no se toca)
//     csvNeutral("2026-09-10")       -> "2026-09-10"
//     csvNeutral(null)               -> null      (cada tablero decide como sale)
//
//     csvCelda(v) -> la celda ya neutralizada, entre comillas y con las comillas
//                    internas dobladas; null/undefined salen como "".
//
// Todo export a CSV pasa cada valor por aqui. El export a XLSX no lo necesita:
// SheetJS escribe los textos como texto, nunca como formula.
//
// Lo carga cada tablero que exporta CSV, junto a seguro.js:
//     <script src="/shared/js/csv.js"></script>

(function () {
  const DISPARA = /^[=+\-@\t\r]/;
  // Un numero escrito como texto ("-5", "-1,234.50", "1e-3", "12.5%") no
  // puede ser una formula: se deja igual para que Excel lo lea como numero.
  const NUMERO = /^[+-]?((\d{1,3}(,\d{3})+|\d+)(\.\d+)?|\.\d+)([eE][+-]?\d+)?%?$/;

  function csvNeutral(v) {
    if (v === null || v === undefined || typeof v === "number" ||
        typeof v === "boolean" || typeof v === "bigint") return v;
    const s = String(v);
    if (!DISPARA.test(s)) return v;
    if (NUMERO.test(s)) return v;
    return "'" + s;
  }

  function csvCelda(v) {
    return '"' + String(csvNeutral(v) ?? "").replace(/"/g, '""') + '"';
  }

  window.csvNeutral = csvNeutral;
  window.csvCelda = csvCelda;
})();
