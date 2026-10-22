// Funciones compartidas por los módulos del sitio.
//
// © 2026 Reiss Jorge Nicolás
// SPDX-License-Identifier: GPL-3.0-or-later (ver LICENSE)

// Crea un elemento con sus atributos y sus hijos. Los textos se agregan como
// nodos de texto, nunca como HTML, así un dato del JSON no puede inyectar marcado.
export function el(etiqueta, atributos = {}, ...hijos) {
  const nodo = document.createElement(etiqueta);
  for (const [nombre, valor] of Object.entries(atributos)) {
    if (valor === false || valor == null) continue;
    nodo.setAttribute(nombre, valor === true ? "" : valor);
  }
  nodo.append(...hijos);
  return nodo;
}

// 28400 → "$28.400"
export const pesos = (monto) => "$" + monto.toLocaleString("es-AR");

// Precio legible para personas y con el valor numérico para máquinas
export const precio = (monto) => el("data", { value: monto }, pesos(monto));

// Minúsculas y sin tildes, para que «chuna» encuentre «Chuña»
export const normalizar = (texto) =>
  texto.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase().trim();
