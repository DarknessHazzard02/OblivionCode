# Librerías de terceros servidas por el portal

Todas se sirven desde `/shared/vendor/`: el navegador no carga código de
internet. Versiones fijas; el SHA-256 permite verificar que no cambiaron.

| Archivo | Paquete y versión | Licencia | Origen |
|---|---|---|---|
| `chartjs/chart.umd.min.js` | chart.js 4.5.1 | MIT | cdn.jsdelivr.net/npm/chart.js@4.5.1 |
| `chartjs/chartjs-plugin-datalabels.min.js` | chartjs-plugin-datalabels 2.2.0 | MIT | cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0 |
| `chartjs/chartjs-chart-sankey.min.js` | chartjs-chart-sankey 0.12.1 | MIT | cdn.jsdelivr.net/npm/chartjs-chart-sankey@0.12.1 |
| `xlsx/xlsx.full.min.js` | SheetJS CE 0.20.3 (corrige CVE-2023-30533 y CVE-2024-22363 de 0.18.5) | Apache-2.0 | cdn.sheetjs.com/xlsx-0.20.3 |
| `leaflet/*` | leaflet 1.9.4 | BSD-2-Clause | cdn.jsdelivr.net/npm/leaflet@1.9.4 |
| `tabler/*` | @tabler/icons-webfont 3.48.0 (en `tabler-icons.min.css` se quitaron 3 reglas de iconos que ningún tablero usa (dos logos de marcas comerciales y un signo zodiacal), para que el archivo no contenga nombres de productos de terceros; por eso su SHA-256 no es el del paquete original) | MIT | cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.48.0 |
| `fonts/inter-*` | @fontsource/inter 5.3.0 | SIL OFL 1.1 | cdn.jsdelivr.net/npm/@fontsource/inter@5.3.0 |
| `fonts/barlow-condensed-*` | @fontsource/barlow-condensed 5.3.0 | SIL OFL 1.1 | cdn.jsdelivr.net/npm/@fontsource/barlow-condensed@5.3.0 |
| `mapas/countries-50m.json` | world-atlas 2.0.2 (fronteras de Natural Earth 1:50m) | ISC; datos de dominio público | cdn.jsdelivr.net/npm/world-atlas@2.0.2 |
| `mapas/states-10m.json` | us-atlas 3.0.1 (estados de EE. UU., US Census) | ISC; datos de dominio público | cdn.jsdelivr.net/npm/us-atlas@3.0.1 |
| `mapas/topojson-client.min.js` | topojson-client 3.1.0 | ISC | cdn.jsdelivr.net/npm/topojson-client@3.1.0 |
| `banderas/mx.svg`, `banderas/us.svg` (+ `banderas/LICENSE`) | flag-icons 7.5.0 (banderas 4x3 de México y EE. UU. del menú del portal; antes se pedían a flagcdn.com, que recibía la IP de cada usuario) | MIT | cdn.jsdelivr.net/npm/flag-icons@7.5.0 |
| `fonts.css` | escrito para el portal (@font-face de las fuentes de arriba) | — | — |

Descargadas el 2026-09-23 (las banderas, el 2026-09-29).

## SHA-256

```
8f1195d55a2fd315a07d812328470ca9ba2abb78c8d317ff19619d5125e00cea  banderas/LICENSE
9dbc8ad8b35e52ce7cb686d5cd93bd95e4c0dd8505c184186a740148ffd34901  banderas/mx.svg
e7be4240cf57987926673708f09233be1ab6bdf35acc7b86bd32a263f197a2a7  banderas/us.svg
48444a82d4edcb5bec0f1965faacdde18d9c17db3063d042abada2f705c9f54a  chartjs/chart.umd.min.js
cb93753ccb1e8b875ccdfbbe482198226dfa24fcfb7643da0ff892a86e7b4f31  chartjs/chartjs-chart-sankey.min.js
20c08f3d9c6d2ef76df6d6a6f1127c0013339fe32add24222276c398c6308c38  chartjs/chartjs-plugin-datalabels.min.js
93d76786c3d85fef0c021ea4459b5919a5c7ccaa0abf0cc8a58daed08fcdf1ec  fonts.css
215a93c696f442034a46fbb382958f753fda60e30490683aeea6b235fcbb2b66  fonts/barlow-condensed-latin-600-normal.woff2
3787a5a419171630e6890cfa47c4da067474d005cd0ff8dc11ec090fdc3ee2b8  fonts/barlow-condensed-latin-700-normal.woff2
aef7edf54f79a5329fbca9c065b56dcec3852c680d58cf89a9ef2db6940ca4b3  fonts/barlow-condensed-latin-ext-600-normal.woff2
9d351bd9222bfab90f943850f8039aa73cdb40e0a6cfe4127308a48bef59d5f5  fonts/barlow-condensed-latin-ext-700-normal.woff2
be0276550393a72b94d673505567dceba801511d5e1ca5a87793190dc5d5a6ca  fonts/inter-latin-300-normal.woff2
8909904ab6c872eb994093482a88a28eca2cd95912d7b6fecd72103b0dc07edc  fonts/inter-latin-400-normal.woff2
f3779f1efccc4bdcdf9c0a02ab95bf6bd092ed09c48c08cedc725889edd1d19f  fonts/inter-latin-500-normal.woff2
f9a06e79cd3a2a20951c0f0e28f66dd0e6d3fda73911d640a2125c8fcb78f21a  fonts/inter-latin-600-normal.woff2
6f56409fd3d64bb85f7d070bce20749db2d66b6d63cec586cc22d1c761be2491  fonts/inter-latin-700-normal.woff2
a7d0a50f15d389cad679238466bdb5fc9787aa0715719064ce25abaff042820d  fonts/inter-latin-800-normal.woff2
b11def546ac052fad7993e39c53801b55af99b0fd51a9ac0e72884b5c3fcaa3f  fonts/inter-latin-ext-300-normal.woff2
6744a7f509ebc6ab220a6cd4ea77e898adf014f03d88dcda5d45d8a9feefb4e9  fonts/inter-latin-ext-400-normal.woff2
2c6fbc42d315528beb06c1096df45487bf4186c4b78b8111d12c9c951f8acca2  fonts/inter-latin-ext-500-normal.woff2
e4bdf67b0cd15ca9e184509275be95db942195d3cc2b17f6a0452f2adf75d0bf  fonts/inter-latin-ext-600-normal.woff2
143f9504f1377012aa3e39c90c4354ef429cb0494b9ac0e1437f1a81e5412236  fonts/inter-latin-ext-700-normal.woff2
eade55593308b9e4916dd7f47826929ce3e40cad85a2b338d56e5fd1e7bf8e5e  fonts/inter-latin-ext-800-normal.woff2
066daca850d8ffbef007af00b06eac0015728dee279c51f3cb6c716df7c42edf  leaflet/images/layers-2x.png
1dbbe9d028e292f36fcba8f8b3a28d5e8932754fc2215b9ac69e4cdecf5107c6  leaflet/images/layers.png
00179c4c1ee830d3a108412ae0d294f55776cfeb085c60129a39aa6fc4ae2528  leaflet/images/marker-icon-2x.png
574c3a5cca85f4114085b6841596d62f00d7c892c7b03f28cbfa301deb1dc437  leaflet/images/marker-icon.png
264f5c640339f042dd729062cfc04c17f8ea0f29882b538e3848ed8f10edb4da  leaflet/images/marker-shadow.png
a7837102824184820dfa198d1ebcd109ff6d0ff9a2672a074b9a1b4d147d04c6  leaflet/leaflet.css
db49d009c841f5ca34a888c96511ae936fd9f5533e90d8b2c4d57596f4e5641a  leaflet/leaflet.js
04342cdc1e3016bcd7db1630de95684d67b79fe3c8c460321e87aef469502394  mapas/countries-50m.json
d76b391ccfa8bff601d51e3e3da5d43a89fa46cd5caca72ce731b383be5596d0  mapas/states-10m.json
25cd02ae486cc5063e0215a4e4cfb15de83700c87ac48bac4d57dc6aaf3ebb89  mapas/topojson-client.min.js
dafbdda4cb0cdcb2cc0696a10314360dfee7fbc59d4195ec7a81c95d41e65f07  tabler/fonts/tabler-icons.woff2
61f8c6cfe878c8721fb363a7f0cf1dd4dd76a92b1bfbd8567777cf84c6c7bef6  tabler/tabler-icons.min.css
cc015130aa8521e7f088f88898eba949ccdcbfb38df0bd129b44b7273c3a6f41  xlsx/xlsx.full.min.js
```
