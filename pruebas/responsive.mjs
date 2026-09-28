// Pruebas de usabilidad responsive de Woodbird (Sprint 2, semana 6).
// Recorre index.html y politica-privacidad.html en 11 anchos de pantalla y mide
// desborde, objetivos táctiles, tamaño de letra, contraste, anclas, carrusel y
// checkout. Guarda capturas y resultados.json en la carpeta de salida.
//
// Uso (desde la raíz del repo, con Node 22 o posterior):
//   python -m http.server 8765
//   node pruebas/responsive.mjs http://127.0.0.1:8765/ pruebas/salida
//
// © 2026 Reiss Jorge Nicolás
// SPDX-License-Identifier: GPL-3.0-or-later (ver LICENSE)
import { writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { lanzar } from "./cdp.mjs";

const BASE = process.argv[2] || "http://127.0.0.1:8765/";
const SALIDA = process.argv[3] || "salida";
mkdirSync(join(SALIDA, "capturas"), { recursive: true });

const VISTAS = [
  { id: "320", ancho: 320, alto: 568, disp: "iPhone SE (1.ª gen.) · mínimo WCAG 1.4.10", movil: true },
  { id: "360", ancho: 360, alto: 800, disp: "Android de gama media", movil: true },
  { id: "390", ancho: 390, alto: 844, disp: "iPhone 13/14", movil: true },
  { id: "599", ancho: 599, alto: 900, disp: "Borde inferior del corte de tableta", movil: true },
  { id: "600", ancho: 600, alto: 900, disp: "Corte de tableta", movil: true },
  { id: "768", ancho: 768, alto: 1024, disp: "iPad vertical", movil: true },
  { id: "959", ancho: 959, alto: 800, disp: "Borde inferior del corte de escritorio", movil: true },
  { id: "960", ancho: 960, alto: 800, disp: "Corte de escritorio", movil: false },
  { id: "1024", ancho: 1024, alto: 768, disp: "iPad horizontal / notebook chica", movil: true },
  { id: "1366", ancho: 1366, alto: 768, disp: "Notebook común", movil: false },
  { id: "1920", ancho: 1920, alto: 1080, disp: "Monitor Full HD", movil: false },
];

// Código que se ejecuta dentro de la página y devuelve las mediciones.
const MEDIR = `(() => {
  const vw = document.documentElement.clientWidth, vh = innerHeight;
  const visible = (el) => {
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    return r.width > 1 && r.height > 1 && cs.visibility !== "hidden" && cs.display !== "none";
  };
  const desc = (el) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += "#" + el.id;
    else if (el.className && typeof el.className === "string") s += "." + el.className.trim().split(/\\s+/)[0];
    const t = (el.getAttribute("aria-label") || el.textContent || el.placeholder || "").trim().replace(/\\s+/g, " ").slice(0, 40);
    return t ? s + " «" + t + "»" : s;
  };
  const dentroDeScroll = (el) => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const o = getComputedStyle(p).overflowX;
      if (o === "auto" || o === "scroll" || o === "hidden") return true;
    }
    return false;
  };

  // 1. Desborde horizontal de la página
  const desborde = document.documentElement.scrollWidth - vw;
  const culpables = [...document.querySelectorAll("body *")]
    .filter((el) => visible(el) && !dentroDeScroll(el) && el.getBoundingClientRect().right > vw + 1)
    .map(desc).slice(0, 8);

  // 2. Objetivos táctiles
  const interactivos = [...document.querySelectorAll("a[href], button, input:not([type=hidden]), label[for], select, textarea")]
    .filter((el) => visible(el) && !el.classList.contains("visualmente-oculto"));
  const enLinea = (el) => el.tagName === "A" && getComputedStyle(el).display === "inline";
  const tactilesChicos = interactivos.filter((el) => {
    if (el.tagName === "LABEL" && !el.closest(".chips")) return false; // etiquetas de campo: el objetivo es el input
    if (el.type === "checkbox") return false; // se evalúa aparte
    const r = el.getBoundingClientRect();
    return !enLinea(el) && (r.height < 44 || r.width < 44);
  }).map((el) => { const r = el.getBoundingClientRect(); return desc(el) + " " + Math.round(r.width) + "×" + Math.round(r.height); });
  const enlacesEnLinea = interactivos.filter(enLinea).map((el) => {
    const r = el.getBoundingClientRect(); return { el: desc(el), alto: Math.round(r.height) };
  });
  const casilla = document.querySelector("input#consentimiento");
  let casillaInfo = null;
  if (casilla && visible(casilla)) {
    const r = casilla.getBoundingClientRect();
    const lab = document.querySelector("label[for=consentimiento]").getBoundingClientRect();
    casillaInfo = { ancho: Math.round(r.width), alto: Math.round(r.height), etiquetaAlto: Math.round(lab.height) };
  }

  // 3. Tamaño mínimo de texto
  const textos = [...document.querySelectorAll("body *")].filter((el) =>
    visible(el) && [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()) && !el.closest(".visualmente-oculto"));
  const letraChica = textos.filter((el) => parseFloat(getComputedStyle(el).fontSize) < 12)
    .map((el) => desc(el) + " " + getComputedStyle(el).fontSize);
  const minLetra = Math.min(...textos.map((el) => parseFloat(getComputedStyle(el).fontSize)));

  // 4. Contraste de color (WCAG 2.1, criterio 1.4.3)
  const rgb = (c) => (c.match(/[\\d.]+/g) || []).map(Number);
  const lum = ([r, g, b]) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const fondo = (el) => { for (let p = el; p; p = p.parentElement) { const c = rgb(getComputedStyle(p).backgroundColor); if (c.length >= 3 && (c[3] === undefined || c[3] > 0.9)) return c; } return [255, 255, 255]; };
  const hex = (c) => "#" + c.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, "0")).join("").toUpperCase();
  const pares = new Map();
  for (const el of textos) {
    const cs = getComputedStyle(el), fg = rgb(cs.color), bg = fondo(el);
    const op = parseFloat(cs.opacity);
    // mezcla simple con la opacidad del propio elemento (p. ej. .bajada)
    const fgEf = op < 1 ? fg.slice(0, 3).map((v, i) => v * op + bg[i] * (1 - op)) : fg;
    const l1 = lum(fgEf), l2 = lum(bg), ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    const tam = parseFloat(cs.fontSize), peso = parseInt(cs.fontWeight);
    const grande = tam >= 24 || (tam >= 18.66 && peso >= 700);
    const minimo = grande ? 3 : 4.5;
    const clave = hex(fgEf) + " sobre " + hex(bg);
    const prev = pares.get(clave);
    if (!prev || (ratio < minimo && !prev.falla)) pares.set(clave, { par: clave, ratio: Math.round(ratio * 100) / 100, minimo, falla: ratio < minimo, ejemplo: desc(el) + " (" + cs.fontSize + ")" });
  }

  // 5. Distribución de componentes
  const cols = (sel) => { const el = document.querySelector(sel); return el ? getComputedStyle(el).gridTemplateColumns.split(" ").filter(Boolean).length : null; };
  const nav = document.querySelector("body > nav");
  const navCs = getComputedStyle(nav), navR = nav.getBoundingClientRect();
  const carr = document.querySelector("#carrito"), chk = document.querySelector("#checkout");
  const carrusel = document.querySelector(".carrusel");
  const disposicion = {
    navPosicion: navCs.position,
    navUbicacion: navCs.position === "fixed" ? (Math.round(navR.bottom) >= vh - 1 ? "abajo" : "arriba") : "arriba",
    navAlto: Math.round(navR.height),
    grillaColumnas: cols(".grilla"),
    carruselModo: carrusel ? (getComputedStyle(carrusel).overflowX === "auto" ? "carrusel deslizable" : "grilla fija") : null,
    carruselVisibles: carrusel ? (() => { const cr = carrusel.getBoundingClientRect(); return [...carrusel.children].filter((li) => li.getBoundingClientRect().left < cr.right - 10).length; })() : null,
    carritoModo: carr ? (getComputedStyle(document.querySelector("#carrito tbody tr")).display === "grid" ? "renglones apilados" : "tabla") : null,
    carritoYCheckout: carr && chk ? (Math.abs(carr.getBoundingClientRect().top - chk.getBoundingClientRect().top) < 5 ? "lado a lado" : "apilados") : null,
    buscadorEnLinea: (() => { const m = document.querySelector(".marca"), b = document.querySelector(".buscador"); return m && b ? Math.abs(m.getBoundingClientRect().top - b.getBoundingClientRect().top) < 30 : null; })(),
    checkoutLocalidadYCp: (() => { const l = document.querySelector("#localidad"), c = document.querySelector("#cp"); return l && c ? (Math.abs(l.getBoundingClientRect().top - c.getBoundingClientRect().top) < 2 ? "misma fila" : "filas separadas") : null; })(),
    anchoLinea: (() => { const p = document.querySelector(".documento-legal section p"); return p ? Math.round(p.getBoundingClientRect().width / (parseFloat(getComputedStyle(p).fontSize) * 0.5)) : null; })(),
    carritoFilasAncho: carr ? (() => { const t = carr.querySelector("table").getBoundingClientRect().width;
      return Math.round(Math.min(...[...carr.querySelectorAll("tbody tr, tfoot tr")].filter((tr) => tr.getBoundingClientRect().height > 1).map((tr) => tr.getBoundingClientRect().width / t)) * 100); })() : null,
    alturaPagina: document.documentElement.scrollHeight,
  };

  return { vw, vh, desborde, culpables, tactilesChicos, enlacesEnLinea, casillaInfo, letraChica, minLetra, contraste: [...pares.values()], disposicion };
})()`;

// Navegación por anclas: el título de la sección queda visible y no lo tapa la barra
const ANCLAS = (sel) => `(async () => {
  const out = [];
  for (const a of document.querySelectorAll("${sel}")) {
    const destino = document.querySelector(a.getAttribute("href").replace(/^.*#/, "#"));
    if (!destino) { out.push({ enlace: a.textContent, ok: false, motivo: "destino inexistente" }); continue; }
    a.click();
    await new Promise((r) => setTimeout(r, 900));
    const h = destino.matches("h1, h2") ? destino : destino.querySelector("h1, h2");
    const r = h.getBoundingClientRect();
      const tapa = document.elementFromPoint(Math.min(r.left + 5, innerWidth - 1), r.top + r.height / 2);
    const visibleEnPantalla = r.top >= 0 && r.bottom <= innerHeight;
    const cubierto = !(tapa && (h === tapa || h.contains(tapa)));
    out.push({ enlace: a.textContent, destino: "#" + destino.id, tituloTop: Math.round(r.top), ok: visibleEnPantalla && !cubierto,
      motivo: !visibleEnPantalla ? "título fuera de pantalla (top " + Math.round(r.top) + ")" : cubierto ? "título tapado por " + (tapa?.tagName || "?") : "" });
  }
  scrollTo(0, 0);
  return out;
})()`;

// Final de la página: la barra fija no tapa el último contenido del pie
const PIE = `(async () => {
  scrollTo(0, document.documentElement.scrollHeight);
  await new Promise((r) => setTimeout(r, 400));
  const ult = [...document.querySelectorAll("body > footer > *")].pop();
  const r = ult.getBoundingClientRect(), nav = document.querySelector("body > nav").getBoundingClientRect();
  const fija = getComputedStyle(document.querySelector("body > nav")).position === "fixed";
  scrollTo(0, 0);
  return { ok: !fija || r.bottom <= nav.top + 1, ultimoBottom: Math.round(r.bottom), navTop: Math.round(nav.top) };
})()`;

// Carrusel: se puede deslizar y encaja en cada tarjeta
const CARRUSEL = `(async () => {
  const c = document.querySelector(".carrusel");
  if (getComputedStyle(c).overflowX !== "auto") return { aplica: false };
  const puedeDeslizar = c.scrollWidth > c.clientWidth;
  c.scrollBy({ left: 60, behavior: "instant" });
  await new Promise((r) => setTimeout(r, 700));
  const segunda = c.children[1].getBoundingClientRect().left - c.getBoundingClientRect().left;
  const pos = c.scrollLeft;
  c.scrollTo({ left: 0, behavior: "instant" });
  return { aplica: true, puedeDeslizar, scrollLeftTrasDeslizar: Math.round(pos), encaja: Math.abs(segunda) < 2 || pos === 0 || pos >= c.scrollWidth - c.clientWidth - 1 };
})()`;

// Checkout simulado: valida, confirma, borra y no envía nada por la red
const CHECKOUT = `(async () => {
  const f = document.querySelector("#form-checkout"), b = document.querySelector("#ir-al-pago"), conf = document.querySelector("#confirmacion");
  b.click();
  const vacioBloquea = conf.textContent === "";
  const invalidos = [...f.elements].filter((e) => e.willValidate && !e.checkValidity()).map((e) => e.id);
  const set = (id, v) => { f.elements[id].value = v; };
  set("nombre", "Ana Pérez"); set("email", "ana@correo"); set("direccion", "Av. Sarmiento 123"); set("localidad", "Resistencia"); set("cp", "35000");
  f.elements.consentimiento.checked = true;
  b.click();
  const cpInvalidoBloquea = conf.textContent === "";
  set("cp", "3500");
  f.elements.email.value = "ana@correo.com";
  b.click();
  await new Promise((r) => setTimeout(r, 200));
  const confirma = conf.textContent;
  const confVisible = conf.getBoundingClientRect().height > 0;
  const borrado = ["nombre", "email", "direccion", "localidad", "cp"].every((id) => f.elements[id].value === "") && !f.elements.consentimiento.checked;
  conf.textContent = "";
  return { vacioBloquea, invalidos, cpInvalidoBloquea, confirma, confVisible, borrado };
})()`;

const PAGINAS = [
  { id: "inicio", ruta: "index.html", completo: true, anclas: "body > nav a" },
  { id: "privacidad", ruta: "politica-privacidad.html", completo: false, anclas: ".documento-legal > nav a" },
];

const b = await lanzar();
const peticiones = [];
b.on((m) => {
  if (m.method === "Network.requestWillBeSent") peticiones.push({ url: m.params.request.url, metodo: m.params.request.method, tipo: m.params.type });
  if (m.method === "Network.responseReceived") {
    const p = peticiones.findLast((x) => x.url === m.params.response.url);
    if (p) p.estado = m.params.response.status;
  }
});
await b.send("Network.enable");
await b.send("Page.enable");
await b.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });

const resultados = [];
for (const pag of PAGINAS) {
  for (const v of VISTAS) {
    await b.send("Emulation.setDeviceMetricsOverride", { width: v.ancho, height: v.alto, deviceScaleFactor: 1, mobile: v.movil });
    await b.send("Emulation.setTouchEmulationEnabled", { enabled: v.movil });
    peticiones.length = 0;
    await b.send("Page.navigate", { url: BASE + pag.ruta });
    await new Promise((r) => setTimeout(r, 1800));
    await b.evaluar("document.fonts.ready.then(() => true)");
    const cargaPeticiones = peticiones.map((p) => ({ ...p }));
    const med = await b.evaluar(MEDIR);
    const r = { pagina: pag.id, vista: v, medicion: med, carga: cargaPeticiones };

    // captura de página completa
    const alto = med.disposicion.alturaPagina;
    await b.send("Emulation.setDeviceMetricsOverride", { width: v.ancho, height: alto, deviceScaleFactor: 1, mobile: v.movil });
    await new Promise((res) => setTimeout(res, 300));
    const cap = await b.send("Page.captureScreenshot", { format: "png" });
    writeFileSync(join(SALIDA, "capturas", `${pag.id}-${v.id}-completa.png`), Buffer.from(cap.data, "base64"));
    await b.send("Emulation.setDeviceMetricsOverride", { width: v.ancho, height: v.alto, deviceScaleFactor: 1, mobile: v.movil });
    await new Promise((res) => setTimeout(res, 300));
    const cap2 = await b.send("Page.captureScreenshot", { format: "png" });
    writeFileSync(join(SALIDA, "capturas", `${pag.id}-${v.id}-pantalla.png`), Buffer.from(cap2.data, "base64"));

    r.pie = await b.evaluar(PIE);
    r.anclas = await b.evaluar(ANCLAS(pag.anclas));
    if (pag.completo) {
      r.carrusel = await b.evaluar(CARRUSEL);
      peticiones.length = 0;
      r.checkout = await b.evaluar(CHECKOUT);
      r.checkout.peticionesDuranteCompra = peticiones.map((p) => ({ ...p }));
    }
    resultados.push(r);
    console.log(pag.id, v.id, "desborde", med.desborde, "chicos", med.tactilesChicos.length, "anclas", r.anclas.filter((a) => !a.ok).length, "fallas");
  }
}
b.cerrar();
writeFileSync(join(SALIDA, "resultados.json"), JSON.stringify(resultados, null, 2));
console.log("listo");
