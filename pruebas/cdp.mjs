// Cliente mínimo de Chrome DevTools Protocol, sin dependencias: abre Chrome
// sin interfaz y permite mandarle comandos desde Node.
//
// © 2026 Reiss Jorge Nicolás
// SPDX-License-Identifier: GPL-3.0-or-later (ver LICENSE)
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// Ruta de Chrome: se puede cambiar con la variable de entorno CHROME
const CHROME = process.env.CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe";

export async function lanzar(puerto = 9333) {
  const perfil = mkdtempSync(join(tmpdir(), "wb-chrome-"));
  const proc = spawn(CHROME, [
    "--headless=new", `--remote-debugging-port=${puerto}`, `--user-data-dir=${perfil}`,
    "--no-first-run", "--hide-scrollbars", "--disable-gpu", "about:blank",
  ], { stdio: "ignore" });
  let url;
  for (let i = 0; i < 50 && !url; i++) {
    await new Promise((r) => setTimeout(r, 200));
    try {
      const lista = await (await fetch(`http://127.0.0.1:${puerto}/json/list`)).json();
      url = lista.find((t) => t.type === "page")?.webSocketDebuggerUrl;
    } catch {}
  }
  if (!url) throw new Error("Chrome no respondió");
  const ws = new WebSocket(url);
  await new Promise((r, e) => { ws.onopen = r; ws.onerror = e; });
  let id = 0;
  const pendientes = new Map();
  const oyentes = [];
  ws.onmessage = (m) => {
    const d = JSON.parse(m.data);
    if (d.id && pendientes.has(d.id)) {
      const { res, rej } = pendientes.get(d.id);
      pendientes.delete(d.id);
      d.error ? rej(new Error(JSON.stringify(d.error))) : res(d.result);
    } else if (d.method) oyentes.forEach((f) => f(d));
  };
  const send = (method, params = {}) => new Promise((res, rej) => {
    const n = ++id;
    pendientes.set(n, { res, rej });
    ws.send(JSON.stringify({ id: n, method, params }));
  });
  const evaluar = async (expr) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || "error JS");
    return r.result.value;
  };
  const cerrar = () => { ws.close(); proc.kill(); };
  return { send, evaluar, on: (f) => oyentes.push(f), cerrar };
}
