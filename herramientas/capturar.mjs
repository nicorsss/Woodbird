// Exporta páginas HTML locales a PNG con Chrome sin interfaz.
// Uso: node herramientas/capturar.mjs lista.json
//   lista.json: [{ "html": "ruta.html", "png": "ruta.png", "ancho": 1080, "alto": 1350 }, ...]
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { lanzar } from "../sitio/pruebas/cdp.mjs";

const lista = JSON.parse(readFileSync(process.argv[2], "utf-8"));
const b = await lanzar(9334);
await b.send("Page.enable");
for (const { html, png, ancho, alto } of lista) {
  await b.send("Emulation.setDeviceMetricsOverride", { width: ancho, height: alto, deviceScaleFactor: 1, mobile: false });
  await b.send("Page.navigate", { url: pathToFileURL(html).href });
  await new Promise((r) => setTimeout(r, 800));
  await b.evaluar("document.fonts.ready.then(() => new Promise((r) => setTimeout(r, 300)))");
  const desborde = await b.evaluar("document.documentElement.scrollHeight > innerHeight + 1 || document.documentElement.scrollWidth > innerWidth + 1");
  const cap = await b.send("Page.captureScreenshot", { format: "png" });
  writeFileSync(png, Buffer.from(cap.data, "base64"));
  console.log(desborde ? "DESBORDA" : "ok", png.split(/[\\/]/).pop());
}
b.cerrar();
