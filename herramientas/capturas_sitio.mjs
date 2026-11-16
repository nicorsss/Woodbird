// Capturas del sitio para la carpeta del Sprint 3: catálogo, carrito, checkout y páginas legales.
// Uso (con el sitio servido en BASE): node herramientas/capturas_sitio.mjs <BASE> <carpeta de salida>
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { lanzar } from "../sitio/pruebas/cdp.mjs";

const BASE = process.argv[2] || "http://127.0.0.1:8765/";
const SALIDA = process.argv[3] || "capturas";
mkdirSync(SALIDA, { recursive: true });

const b = await lanzar(9335);
await b.send("Page.enable");
await b.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
const espera = (ms) => new Promise((r) => setTimeout(r, ms));

async function abrir(ruta, ancho, alto, movil = false) {
  await b.send("Emulation.setDeviceMetricsOverride", { width: ancho, height: alto, deviceScaleFactor: 1, mobile: movil });
  await b.send("Page.navigate", { url: BASE + ruta });
  await espera(1500);
  await b.evaluar("document.fonts.ready.then(() => true)");
}

async function captura(nombre, js = "", { selector, desplazar = 0 } = {}) {
  if (js) await b.evaluar(`(async () => { ${js} })()`);
  if (selector) await b.evaluar(`(() => { const e = document.querySelector(${JSON.stringify(selector)}); scrollTo(0, e.getBoundingClientRect().top + scrollY - ${desplazar}); })()`);
  await espera(400);
  const cap = await b.send("Page.captureScreenshot", { format: "png" });
  writeFileSync(join(SALIDA, nombre + ".png"), Buffer.from(cap.data, "base64"));
  console.log("ok", nombre);
}

const AGREGAR = `for (const id of [1, 1, 3]) document.querySelector('[data-agregar="' + id + '"]').click();
  await new Promise((r) => setTimeout(r, 300));`;
const COMPLETAR = `const f = document.querySelector("#form-checkout");
  const set = (id, v) => { f.elements[id].value = v; };
  set("nombre", "Ana Pérez"); set("email", "ana@correo.com"); set("direccion", "Av. Sarmiento 123");
  set("localidad", "Resistencia"); set("cp", "3500");
  f.elements.terminos.checked = true; f.elements.consentimiento.checked = true;`;

// 1. Portada en escritorio: botón de arrepentimiento y contador del carrito
await abrir("index.html", 1366, 768);
await captura("01_portada_escritorio", AGREGAR);

// 2. Catálogo generado desde productos.json, con un filtro activo
await abrir("index.html", 1366, 900);
await captura("02_catalogo_filtro", `document.querySelector('#filtro-palo-santo').click();`, { selector: "#catalogo", desplazar: 80 });

// 3. Búsqueda sin tildes
await abrir("index.html", 1366, 900);
await captura("03_busqueda", `const q = document.querySelector("#buscar"); q.value = "chuna"; q.dispatchEvent(new Event("input", { bubbles: true }));`,
  { selector: "#catalogo", desplazar: 80 });

// 4. Carrito en el celular: Cardenal ×2 y Carpintero, con el contador en la barra
await abrir("index.html", 390, 844, true);
await captura("04_carrito_movil", AGREGAR, { selector: "#carrito", desplazar: 16 });

// 5. Checkout en escritorio con los datos completos, antes de confirmar
await abrir("index.html", 1366, 1000);
await captura("05_checkout_completo", AGREGAR + COMPLETAR, { selector: "#carrito", desplazar: 80 });

// 6. Confirmación del pedido simulado: formulario y carrito vacíos
await captura("06_confirmacion", `document.querySelector("#ir-al-pago").click();`, { selector: "#confirmacion", desplazar: 520 });

// 7. Compra bloqueada con el carrito vacío
await abrir("index.html", 1366, 1000);
await captura("07_carrito_vacio_bloquea", COMPLETAR + `document.querySelector("#ir-al-pago").click();`, { selector: "#error-pago", desplazar: 520 });

// 8. Pie con los enlaces legales
await abrir("index.html", 1366, 768);
await captura("08_pie_legal", `scrollTo(0, document.documentElement.scrollHeight);`);

// 9 y 10. Términos y condiciones: inicio y cláusula de arrepentimiento con su botón
await abrir("terminos-y-condiciones.html", 1366, 900);
await captura("09_terminos");
await captura("10_clausula_arrepentimiento", "", { selector: "#arrepentimiento", desplazar: 90 });

// 11. Falla de carga del catálogo (productos.json bloqueado)
await b.send("Network.enable");
await b.send("Network.setCacheDisabled", { cacheDisabled: true });
await b.send("Fetch.enable", { patterns: [{ urlPattern: "*productos.json*" }] });
b.on((m) => { if (m.method === "Fetch.requestPaused") b.send("Fetch.failRequest", { requestId: m.params.requestId, errorReason: "ConnectionFailed" }); });
await abrir("index.html", 390, 844, true);
await captura("11_error_de_carga", "", { selector: "#catalogo", desplazar: 16 });
await b.send("Fetch.disable");

b.cerrar();
