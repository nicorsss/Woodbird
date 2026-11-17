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

// 10500 → "$10.500"
export const pesos = (monto) => "$" + monto.toLocaleString("es-AR");

// Precio legible para personas y con el valor numérico para máquinas
export const precio = (monto) => el("data", { value: monto }, pesos(monto));

// Venta por mayor: desde 100 unidades de una misma pieza rige su precio_mayor
// (la mitad del precio individual). La misma regla está en api/crear-preferencia.js.
export const MAYOR_DESDE = 100;
export const precioUnitario = (producto, cantidad) =>
  cantidad >= MAYOR_DESDE ? producto.precio_mayor : producto.precio_simulado;

// Entrega: retiro en el local sin cargo, o envío por Correo Argentino con tarifa fija
// que pasa a ser gratis desde ENVIO_GRATIS de subtotal. Igual en api/crear-preferencia.js.
export const ENVIO = 5900;
export const ENVIO_GRATIS = 30000;
export const LOCAL = "Juan José Castelli, Chaco";
export const costoEnvio = (entrega, subtotal) =>
  entrega === "retiro" || subtotal >= ENVIO_GRATIS ? 0 : ENVIO;

// Minúsculas y sin tildes, para que «chuna» encuentre «Chuña»
export const normalizar = (texto) =>
  texto.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase().trim();
