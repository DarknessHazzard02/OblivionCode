// medir-celular.js — mide si un tablero cabe en un celular.
//
// Uso: abrir el tablero a 375 x 812 (panel Browser con preset "mobile", o
// DevTools > modo dispositivo), esperar a que carguen los datos, y pegar
// esto en la consola (o mandarlo con javascript_tool). Regresa un objeto;
// el tablero pasa solo si `pasa` es true.
//
// Se puede medir un tablero desde otra pagina del mismo portal metiendolo en
// un <iframe> de 375 x 812 y llamando medirCelular(iframe.contentWindow):
// el portal manda X-Frame-Options SAMEORIGIN, asi que se deja.

function medirCelular(win = window) {
  const d = win.document, W = d.documentElement.clientWidth, g = (e) => win.getComputedStyle(e);
  const vis = (el) => {
    const r = el.getBoundingClientRect(), s = g(el);
    return r.width > 0 && r.height > 0 && s.display !== "none" && s.visibility !== "hidden";
  };
  // Primer ancestro que recorta o hace scroll de lado.
  const contenedor = (el) => {
    for (let p = el.parentElement; p && p !== d.body; p = p.parentElement) {
      if (g(p).overflowX !== "visible") return p;
    }
    return null;
  };
  const nombre = (el) => el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") +
    (el.classList[0] ? "." + el.classList[0] : "");

  // 1. Lo que se sale de la pantalla sin estar dentro de algo con scroll.
  const desbordan = new Set();
  for (const el of d.body.querySelectorAll("*")) {
    if (!vis(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.right <= W + 2 || contenedor(el)) continue;
    if (g(el).position === "fixed" && r.left >= W - 1) continue; // cajon cerrado
    desbordan.add(nombre(el) + " " + Math.round(r.width) + "px");
  }

  // 2. Tablas mas anchas que su contenedor con overflow hidden: la parte que
  //    no cabe NO se puede ver de ninguna forma.
  const tablasCortadas = [...d.querySelectorAll("table")].filter(vis).filter((t) => {
    const c = contenedor(t);
    return c && g(c).overflowX === "hidden" &&
      t.getBoundingClientRect().width > c.getBoundingClientRect().width + 2;
  }).map(nombre);

  // 3. overflow-x: hidden en html/body TAPA el desborde: scrollWidth sale
  //    bien pero el contenido queda cortado. Se mide el body por separado.
  const tapado = ["hidden", "clip"].includes(g(d.body).overflowX) ||
    ["hidden", "clip"].includes(g(d.documentElement).overflowX);
  const anchoReal = Math.max(d.body.scrollWidth, d.documentElement.scrollWidth);

  // 4. Encabezado: no debe comerse media pantalla.
  const hdr = d.querySelector(".hdr, header");
  const altoEncabezado = hdr ? Math.round(hdr.getBoundingClientRect().height) : null;

  // 5. Algo fijo que tape mas de la mitad de la pantalla al abrir (sidebar).
  const tapaPantalla = [...d.querySelectorAll("aside, nav, .sidebar")].filter(vis)
    .filter((el) => {
      const r = el.getBoundingClientRect();
      return ["fixed", "sticky", "absolute"].includes(g(el).position) &&
        r.left < W / 2 && r.width > W / 2 && r.height > win.innerHeight / 2;
    }).map(nombre);

  // 6. Controles chicos para el dedo, y texto ilegible.
  const controles = [...d.querySelectorAll("button, a, select, input")].filter(vis);
  const controlesChicos = controles.filter((b) => b.getBoundingClientRect().height < 28).length;
  const textos = [...d.querySelectorAll("body *")].filter((e) => vis(e) &&
    [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()));
  const textoMenor10 = textos.filter((e) => parseFloat(g(e).fontSize) < 10).length;

  // 7. Una barra de filtros arriba del contenido que llega abierta. El panel
  //    lateral del tema (.filter-panel) no cuenta: ya arranca en su tira.
  const barra = d.querySelector(".filtros-bar, .filter-bar");
  const filtrosAbiertos = !!barra && vis(barra) && !barra.classList.contains("plegada") &&
    barra.getBoundingClientRect().height > 150;

  const pasa = desbordan.size === 0 && tablasCortadas.length === 0 &&
    anchoReal <= W + 2 && tapaPantalla.length === 0 && !tapado && !filtrosAbiertos;

  return {
    pagina: win.location.pathname, ancho: W, anchoReal, tapadoConOverflowHidden: tapado,
    desbordan: [...desbordan].slice(0, 10), totalDesbordan: desbordan.size,
    tablasCortadas, tapaPantalla, altoEncabezado, filtrosAbiertos,
    controles: controles.length, controlesChicos, textoMenor10, pasa,
  };
}

medirCelular();
