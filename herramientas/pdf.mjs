// Convierte páginas HTML locales a PDF A4 con Chrome sin interfaz.
// Uso: node herramientas/pdf.mjs lista.json   ([{ "html": "...", "pdf": "..." }, ...])
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { lanzar } from "../sitio/pruebas/cdp.mjs";

const lista = JSON.parse(readFileSync(process.argv[2], "utf-8"));
const b = await lanzar(9337);
await b.send("Page.enable");
for (const { html, pdf } of lista) {
  await b.send("Page.navigate", { url: pathToFileURL(html).href });
  await new Promise((r) => setTimeout(r, 700));
  await b.evaluar("document.fonts.ready.then(() => Promise.all([...document.images].map((i) => i.decode().catch(() => {}))))");
  const r = await b.send("Page.printToPDF", {
    printBackground: true, preferCSSPageSize: true, paperWidth: 8.27, paperHeight: 11.69,
    marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0,
  });
  writeFileSync(pdf, Buffer.from(r.data, "base64"));
  console.log("ok", pdf.split(/[\\/]/).pop());
}
b.cerrar();
