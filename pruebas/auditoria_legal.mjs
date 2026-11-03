// Auditoría legal del sitio en producción (Sprint 4, tarea 4.6).
// Recorre las tres páginas publicadas con Chrome sin interfaz y verifica los instrumentos
// jurídicos: aviso de IA, Política de Privacidad (Ley 25.326) y Términos y Condiciones con
// botón de arrepentimiento (Ley 24.240, Res. SCI 424/2020 y 274/2021). También registra cada
// pedido de red, las cookies y el almacenamiento local para contrastarlos con la política.
// Uso: node pruebas/auditoria_legal.mjs [<URL base>] [<carpeta de salida>]
//
// © 2026 Reiss Jorge Nicolás
// SPDX-License-Identifier: GPL-3.0-or-later (ver LICENSE)
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { lanzar } from "./cdp.mjs";

const BASE = process.argv[2] || "https://nicorsss.github.io/Woodbird/";
const SALIDA = process.argv[3] || "pruebas/auditoria";
mkdirSync(SALIDA, { recursive: true });

const b = await lanzar(9337);
const espera = (ms) => new Promise((r) => setTimeout(r, ms));
await b.send("Page.enable");
await b.send("Network.enable");
await b.send("Network.clearBrowserCookies");
await b.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });

// Registro de red: cada pedido con su método, destino y si lleva cuerpo
let pedidos = [];
const seguridad = {};
b.on((e) => {
  if (e.method === "Network.requestWillBeSent") {
    const r = e.params.request;
    pedidos.push({ metodo: r.method, url: r.url, conCuerpo: Boolean(r.hasPostData || r.postData) });
  }
  if (e.method === "Network.responseReceived" && e.params.type === "Document" && e.params.response.securityDetails) {
    const s = e.params.response.securityDetails;
    seguridad[e.params.response.url] = {
      protocolo: s.protocol, cifrado: s.cipher, certificado: s.subjectName, emisor: s.issuer,
      validoHasta: new Date(s.validTo * 1000).toISOString().slice(0, 10),
      estado: e.params.response.securityState,
    };
  }
});

const resultados = [];
function verificar(id, pagina, requisito, norma, cumple, evidencia) {
  resultados.push({ id, pagina, requisito, norma, cumple: Boolean(cumple), evidencia });
  console.log(`${cumple ? "CUMPLE  " : "NO CUMPLE"} ${id} ${pagina}: ${requisito}`);
}

async function abrir(ruta, ancho = 1366, alto = 768, movil = false) {
  await b.send("Emulation.setDeviceMetricsOverride", { width: ancho, height: alto, deviceScaleFactor: 1, mobile: movil });
  pedidos = [];
  await b.send("Page.navigate", { url: BASE + ruta });
  await espera(2500);
  await b.evaluar("document.fonts.ready.then(() => true)");
}

async function captura(nombre) {
  const cap = await b.send("Page.captureScreenshot", { format: "png" });
  writeFileSync(join(SALIDA, nombre + ".png"), Buffer.from(cap.data, "base64"));
}

// Estado que se repite en las tres páginas: encabezado y pie legales
const COMUNES = `(() => {
  const vh = innerHeight;
  const arr = document.querySelector("header a.arrepentimiento");
  const r = arr?.getBoundingClientRect();
  const pie = document.querySelector("footer");
  const enlace = (texto) => [...pie.querySelectorAll("a")].find((a) => a.textContent.includes(texto));
  const dato = (a) => a ? { texto: a.textContent.trim(), href: a.href } : null;
  return {
    arrepentimiento: arr ? { texto: arr.textContent.trim(), href: arr.href, arriba: Math.round(r.top), abajo: Math.round(r.bottom),
      visible: r.bottom <= vh && r.width > 0 && getComputedStyle(arr).visibility !== "hidden" } : null,
    ia: dato(enlace("Declaración ética")),
    privacidad: dato(enlace("Política de privacidad")),
    terminos: dato(enlace("Términos y condiciones")),
    consumidor: dato(enlace("Defensa de las y los Consumidores")),
    licencia: pie.textContent.includes("GNU GPL") && pie.textContent.includes("CC BY-NC-SA"),
    avisoIA: pie.textContent.includes("generadas con inteligencia artificial") || pie.textContent.includes("Imagen con IA"),
  };
})()`;

async function estadoHttp(url) {
  try {
    const r = await fetch(url, { method: "GET", redirect: "follow" });
    return r.status;
  } catch (e) {
    return String(e.message);
  }
}

const PAGINAS = [["index.html", "Inicio"], ["politica-privacidad.html", "Privacidad"], ["terminos-y-condiciones.html", "Términos"], ["declaracion-ia.html", "Declaración IA"]];
const estados = {};

for (const [ruta, nombre] of PAGINAS) {
  for (const [ancho, alto, movil, sufijo] of [[390, 844, true, "movil"], [1366, 768, false, "escritorio"]]) {
    await abrir(ruta, ancho, alto, movil);
    const c = await b.evaluar(COMUNES);
    estados[`${nombre} ${sufijo}`] = c;
    await captura(`${ruta.replace(".html", "")}-${sufijo}`);
    verificar("L01", `${nombre} (${ancho} px)`, "Botón de arrepentimiento en el encabezado, visible sin desplazarse",
      "Ley 24.240 art. 34; Res. SCI 424/2020", c.arrepentimiento?.visible && c.arrepentimiento.href.endsWith("terminos-y-condiciones.html#arrepentimiento"),
      c.arrepentimiento ? `«${c.arrepentimiento.texto}» entre ${c.arrepentimiento.arriba} y ${c.arrepentimiento.abajo} px de una pantalla de ${alto} px → ${c.arrepentimiento.href.replace(BASE, "")}` : "No se encontró el botón");
  }
  const c = estados[`${nombre} escritorio`];
  verificar("L02", nombre, "Enlace a la Declaración ética y de transparencia de IA en el pie", "Aviso legal de uso de IA (consigna 4.6)",
    c.ia, c.ia ? `«${c.ia.texto}» → ${c.ia.href.replace(BASE, "")}` : "Sin enlace");
  verificar("L03", nombre, "Enlace a la Política de privacidad en el pie", "Ley 25.326 art. 6", c.privacidad, c.privacidad?.href.replace(BASE, "") ?? "Sin enlace");
  verificar("L04", nombre, "Enlace a los Términos y condiciones en el pie", "Ley 24.240 art. 4", c.terminos, c.terminos?.href.replace(BASE, "") ?? "Sin enlace");
  verificar("L05", nombre, "Enlace «Defensa de las y los Consumidores. Para reclamos ingrese aquí»", "Res. SCI 274/2021",
    c.consumidor?.href.startsWith("https://www.argentina.gob.ar/"), c.consumidor ? `→ ${c.consumidor.href}` : "Sin enlace");
  verificar("L06", nombre, "Aviso de licencias (código GPL y documentación CC BY-NC-SA)", "Ley 11.723", c.licencia, c.licencia ? "Presente en el pie" : "Falta");
}

// Los destinos de los enlaces legales responden
const destinos = new Map();
for (const c of Object.values(estados)) {
  for (const k of ["ia", "privacidad", "terminos", "consumidor"]) if (c[k]) destinos.set(c[k].href.split("#")[0], k);
  if (c.arrepentimiento) destinos.set(c.arrepentimiento.href.split("#")[0], "arrepentimiento");
}
for (const [url, k] of destinos) {
  const s = await estadoHttp(url);
  verificar("L07", "Enlaces", `El destino del enlace de ${k} responde`, "Accesibilidad de la información (Ley 24.240 art. 4)", s === 200, `${url.replace(BASE, "")} → HTTP ${s}`);
}

// El ancla #arrepentimiento existe y explica el procedimiento
await abrir("terminos-y-condiciones.html#arrepentimiento");
const arr = await b.evaluar(`(() => { const s = document.getElementById("arrepentimiento"); return s ? { titulo: s.querySelector("h2,h3")?.textContent.trim(), texto: s.textContent.replace(/\\s+/g, " ").slice(0, 400), y: Math.round(s.getBoundingClientRect().top) } : null; })()`);
await captura("terminos-arrepentimiento");
verificar("L08", "Términos", "La sección de arrepentimiento existe y el enlace lleva directo a ella", "Ley 24.240 art. 34; Res. SCI 424/2020",
  arr && arr.y < 200 && /10|diez/i.test(arr.texto), arr ? `«${arr.titulo}», a ${arr.y} px del borde superior` : "No existe el ancla");

// Contenido mínimo de los textos legales publicados
const textoDe = async (ruta) => { await abrir(ruta); return b.evaluar(`document.body.innerText`); };
const priv = await textoDe("politica-privacidad.html");
const term = await textoDe("terminos-y-condiciones.html");
const contiene = (t, ...claves) => claves.filter((k) => !t.toLowerCase().includes(k.toLowerCase()));
for (const [id, pagina, requisito, norma, t, claves] of [
  ["L09", "Privacidad", "Identifica al responsable del tratamiento y su domicilio", "Ley 25.326 art. 6", priv, ["Responsable del tratamiento", "Reiss Jorge Nicolás", "Resistencia"]],
  ["L10", "Privacidad", "Informa los derechos de acceso, rectificación y supresión y cómo ejercerlos", "Ley 25.326 arts. 14 a 16", priv, ["acceso", "rectificación", "supresión"]],
  ["L11", "Privacidad", "Informa a la autoridad de control (AAIP)", "Ley 25.326 art. 29; Ley 27.275", priv, ["Agencia de Acceso a la Información Pública"]],
  ["L12", "Privacidad", "Declara el consentimiento, la finalidad y los terceros que reciben datos técnicos", "Ley 25.326 arts. 5, 6 y 11", priv, ["consentimiento", "finalidad", "Google Fonts"]],
  ["L13", "Términos", "Informa el derecho de arrepentimiento de 10 días corridos", "Ley 24.240 art. 34", term, ["arrepentimiento", "10 días"]],
  ["L14", "Términos", "Informa la garantía legal", "Ley 24.240 art. 11", term, ["garantía"]],
  ["L15", "Términos", "Declara el carácter simulado de la tienda y el uso de IA", "Ley 24.240 art. 4 (información veraz)", term, ["inteligencia artificial", "demostración"]],
]) {
  const faltan = contiene(t, ...claves);
  verificar(id, pagina, requisito, norma, faltan.length === 0, faltan.length ? `Faltan: ${faltan.join(", ")}` : `Menciona: ${claves.join(", ")}`);
}

// Catálogo: cada imagen de producto lleva el sello de IA y carga
await abrir("index.html", 1366, 900);
const cat = await b.evaluar(`(async () => {
  for (const img of document.querySelectorAll(".tarjeta img")) { img.loading = "eager"; }
  await Promise.all([...document.querySelectorAll(".tarjeta img")].map((i) => i.decode().catch(() => null)));
  const figuras = [...document.querySelectorAll(".tarjeta figure")];
  return {
    figuras: figuras.length,
    conSello: figuras.filter((f) => f.querySelector("figcaption")?.textContent.trim() === "Imagen con IA").length,
    cargadas: figuras.filter((f) => f.querySelector("img")?.naturalWidth > 0).length,
    conAlt: figuras.filter((f) => (f.querySelector("img")?.alt || "").includes("generado con IA")).length,
  };
})()`);
await b.evaluar(`document.getElementById("catalogo").scrollIntoView()`);
await espera(500);
await captura("catalogo-sello-ia");
verificar("L16", "Inicio", "Cada imagen de producto lleva el sello «Imagen con IA» y un texto alternativo que lo declara", "Declaración ética de IA; transparencia",
  cat.figuras > 0 && cat.conSello === cat.figuras && cat.conAlt === cat.figuras, `${cat.conSello} de ${cat.figuras} con sello; ${cat.conAlt} con alt; ${cat.cargadas} cargadas`);

// Checkout: avisos, aceptación obligatoria y ausencia de transmisión de datos
await abrir("index.html", 1366, 1000);
const chk = await b.evaluar(`(async () => {
  for (const id of [1, 3]) document.querySelector('[data-agregar="' + id + '"]').click();
  await new Promise((r) => setTimeout(r, 300));
  const f = document.querySelector("#form-checkout");
  const sec = document.querySelector("#checkout");
  return {
    action: f.getAttribute("action"), metodo: f.getAttribute("method"), submit: f.querySelectorAll('[type="submit"]').length,
    terminosObligatorio: f.elements.terminos.required, consentimientoObligatorio: f.elements.consentimiento.required,
    avisoDemo: /no se realizan ventas/i.test(sec.innerText),
    aviso10: /10 días/.test(sec.innerText),
  };
})()`);
verificar("L17", "Checkout", "Aviso visible de tienda de demostración: no hay ventas ni cobros", "Ley 24.240 art. 4", chk.avisoDemo, chk.avisoDemo ? "Presente sobre el formulario" : "Falta");
verificar("L18", "Checkout", "Aceptación obligatoria de los Términos y de la Política de privacidad", "Ley 25.326 art. 5; Ley 24.240", chk.terminosObligatorio && chk.consentimientoObligatorio,
  `#terminos required=${chk.terminosObligatorio}; #consentimiento required=${chk.consentimientoObligatorio}`);
verificar("L19", "Checkout", "Aviso del plazo de arrepentimiento antes de confirmar", "Ley 24.240 art. 34", chk.aviso10, chk.aviso10 ? "«Tenés 10 días corridos…» junto al botón de pago" : "Falta");

// Intento de compra sin aceptar: el navegador lo bloquea
const sinAceptar = await b.evaluar(`(() => {
  const f = document.querySelector("#form-checkout");
  const set = (id, v) => { f.elements[id].value = v; };
  set("nombre", "Ana Pérez"); set("email", "ana@correo.com"); set("direccion", "Av. Sarmiento 123"); set("localidad", "Resistencia"); set("cp", "3500");
  return { valido: f.checkValidity(), terminos: f.elements.terminos.validationMessage !== "", consentimiento: f.elements.consentimiento.validationMessage !== "" };
})()`);
verificar("L20", "Checkout", "Sin aceptar los Términos y la Política no se puede confirmar", "Ley 25.326 art. 5 (consentimiento libre, expreso e informado)",
  !sinAceptar.valido && sinAceptar.terminos && sinAceptar.consentimiento, `checkValidity()=${sinAceptar.valido}; las dos casillas informan un error de validación`);

// Compra completa: se registra toda la red desde el clic de confirmación
await b.evaluar(`(() => { const f = document.querySelector("#form-checkout"); f.elements.terminos.checked = true; f.elements.consentimiento.checked = true; })()`);
await b.evaluar(`document.getElementById("checkout").scrollIntoView()`);
await captura("checkout-completo");
pedidos = [];
const urlAntes = await b.evaluar("location.href");
const confirmacion = await b.evaluar(`(async () => {
  document.getElementById("ir-al-pago").click();
  await new Promise((r) => setTimeout(r, 1500));
  return { texto: document.getElementById("confirmacion").textContent.trim(), formularioVacio: document.querySelector("#form-checkout").elements.nombre.value === "" };
})()`);
await espera(1500);
await b.evaluar(`document.getElementById("confirmacion").scrollIntoView({ block: "center" })`);
await espera(300);
await captura("checkout-confirmado");
const pedidosCompra = pedidos.slice();
const urlDespues = await b.evaluar("location.href");
const datosEnUrl = /Ana|correo|Sarmiento|3500/i.test(urlDespues);
verificar("L21", "Checkout", "Al confirmar la compra no sale ningún pedido de red con los datos", "Política de privacidad, cláusula 8; Ley 25.326 art. 9",
  confirmacion.texto.startsWith("¡Listo") && confirmacion.formularioVacio &&
  pedidosCompra.filter((p) => p.conCuerpo || /Ana|correo|Sarmiento/i.test(p.url)).length === 0 && !datosEnUrl,
  `${pedidosCompra.length} pedidos de red durante la confirmación (${pedidosCompra.filter((p) => p.conCuerpo).length} con cuerpo); URL sin datos: ${!datosEnUrl}; formulario borrado: ${confirmacion.formularioVacio}. Mensaje: «${confirmacion.texto.slice(0, 110)}…»`);

// Cookies y almacenamiento al terminar el recorrido
const { cookies } = await b.send("Network.getAllCookies");
const almacen = await b.evaluar(`({ local: localStorage.length, sesion: sessionStorage.length })`);
verificar("L22", "Todo el sitio", "No se crean cookies ni datos en el almacenamiento del navegador", "Política de privacidad, cláusula 9",
  cookies.length === 0 && almacen.local === 0 && almacen.sesion === 0, `${cookies.length} cookies; localStorage: ${almacen.local}; sessionStorage: ${almacen.sesion}`);

// Terceros contactados al cargar la portada: deben coincidir con los declarados en la política
await abrir("index.html");
const terceros = [...new Set(pedidos.map((p) => new URL(p.url).host))].filter((h) => h !== new URL(BASE).host);
const declarados = ["fonts.googleapis.com", "fonts.gstatic.com"];
verificar("L23", "Inicio", "Los únicos terceros que reciben la IP son los declarados en la política (Google Fonts)", "Ley 25.326 art. 6 inc. c; art. 12 (transferencia internacional)",
  terceros.every((h) => declarados.includes(h)), `Hosts externos: ${terceros.join(", ") || "ninguno"}`);

// Conexión segura en todas las páginas visitadas
const docs = Object.entries(seguridad);
verificar("L24", "Todo el sitio", "Todas las páginas se sirven por HTTPS con un certificado válido", "Ley 25.326 art. 9 (seguridad de los datos)",
  docs.length > 0 && docs.every(([u, s]) => u.startsWith("https://") && s.estado === "secure"),
  docs.length ? `${docs.length} documentos; ${docs[0][1].protocolo}, ${docs[0][1].cifrado}, certificado ${docs[0][1].certificado} emitido por ${docs[0][1].emisor}, válido hasta ${docs[0][1].validoHasta}` : "Sin datos");

writeFileSync(join(SALIDA, "auditoria.json"), JSON.stringify({ base: BASE, fecha: new Date().toISOString(), resultados, terceros, seguridad, confirmacion, pedidosCompra, estados }, null, 1));
const fallas = resultados.filter((r) => !r.cumple).length;
console.log(`\n${resultados.length - fallas} de ${resultados.length} verificaciones cumplen`);
b.cerrar();
process.exit(0);
