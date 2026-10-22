// Carrito de compras: agregar, quitar y cambiar cantidades, con el contador de la
// barra de navegación y los totales actualizados en tiempo real.
// El carrito vive sólo en memoria (se vacía al recargar la página) y no guarda
// ningún dato personal (ver politica-privacidad.html).
//
// © 2026 Reiss Jorge Nicolás
// SPDX-License-Identifier: GPL-3.0-or-later (ver LICENSE)

import { el, precio } from "./utilidades.js";

const ENVIO = 5900;  // envío fijo a Resistencia
const MAXIMO = 10;   // tope de unidades por pieza

const tabla = document.querySelector("#carrito table");
const cuerpo = document.getElementById("filas-carrito");
const vacio = document.getElementById("carrito-vacio");
const continuar = document.getElementById("continuar-compra");
const titulo = document.getElementById("titulo-carrito");
const contador = document.getElementById("contador-carrito");
const enlaceNav = contador.closest("a");
const anuncio = document.getElementById("anuncio-carrito");

const lineas = new Map();   // id del producto → cantidad
let catalogo = new Map();   // id del producto → producto
const oyentes = [];

export function iniciarCarrito(productos) {
  catalogo = new Map(productos.map((p) => [p.id, p]));

  cuerpo.addEventListener("click", (evento) => {
    const boton = evento.target.closest("[data-quitar]");
    if (boton) quitar(Number(boton.dataset.quitar));
  });

  // Mientras se escribe sólo se aceptan cantidades válidas; al salir del campo
  // se corrige lo que haya quedado fuera de rango.
  cuerpo.addEventListener("input", (evento) => {
    const campo = evento.target;
    const cantidad = Number(campo.value);
    if (Number.isInteger(cantidad) && cantidad >= 1 && cantidad <= MAXIMO) {
      fijarCantidad(Number(campo.dataset.cantidad), cantidad);
    }
  });
  cuerpo.addEventListener("change", (evento) => {
    const campo = evento.target;
    const id = Number(campo.dataset.cantidad);
    const cantidad = Math.min(MAXIMO, Math.max(1, Math.round(Number(campo.value)) || 1));
    campo.value = cantidad;
    fijarCantidad(id, cantidad);
  });

  dibujar();
}

export function agregar(id) {
  const producto = catalogo.get(id);
  if (!producto?.stock) return;

  const actual = lineas.get(id) ?? 0;
  if (actual >= MAXIMO) {
    anunciar(`Ya tenés ${MAXIMO} ${producto.nombre} en el carrito, que es el máximo por pieza.`);
    return;
  }
  lineas.set(id, actual + 1);
  anunciar(`Agregaste ${producto.nombre} al carrito.`);
  dibujar();
}

export function quitar(id) {
  if (!lineas.delete(id)) return;
  anunciar(`Quitaste ${catalogo.get(id).nombre} del carrito.`);
  dibujar();
  // El botón presionado desaparece: el foco vuelve al título del carrito
  titulo.focus();
}

export function fijarCantidad(id, cantidad) {
  if (!lineas.has(id) || lineas.get(id) === cantidad) return;
  lineas.set(id, cantidad);
  dibujar();
}

export function vaciar() {
  lineas.clear();
  dibujar();
}

// Totales calculados siempre desde el catálogo, nunca desde lo que muestra la página
export function resumen() {
  const items = [...lineas].map(([id, cantidad]) => {
    const producto = catalogo.get(id);
    return { producto, cantidad, subtotal: producto.precio_simulado * cantidad };
  });
  const piezas = items.reduce((suma, item) => suma + item.cantidad, 0);
  const subtotal = items.reduce((suma, item) => suma + item.subtotal, 0);
  const envio = piezas > 0 ? ENVIO : 0;
  return { items, piezas, subtotal, envio, total: subtotal + envio };
}

export function alCambiar(oyente) {
  oyentes.push(oyente);
}

function fila(producto) {
  const idCampo = `cant-${producto.id}`;
  return el("tr", { "data-id": producto.id },
    el("th", { scope: "row" }, producto.nombre, " ",
      el("small", {}, `${producto.categoria} · ${producto.medida_cm} cm`)),
    el("td", {}, precio(producto.precio_simulado)),
    el("td", { class: "cantidad" },
      el("label", { class: "visualmente-oculto", for: idCampo }, `Cantidad de ${producto.nombre}`),
      el("input", { type: "number", id: idCampo, name: idCampo, value: 1, min: 1, max: MAXIMO, "data-cantidad": producto.id }),
      el("button", { type: "button", class: "quitar", "data-quitar": producto.id, "aria-label": `Quitar ${producto.nombre} del carrito` }, "Quitar")),
    el("td", { class: "subtotal" }));
}

// Actualiza las filas existentes en lugar de rehacer la tabla, para no quitarle
// el foco al campo de cantidad que la persona está usando.
function dibujar() {
  const filas = new Map([...cuerpo.rows].map((tr) => [Number(tr.dataset.id), tr]));
  for (const [id, tr] of filas) {
    if (!lineas.has(id)) tr.remove();
  }
  for (const [id, cantidad] of lineas) {
    const producto = catalogo.get(id);
    const tr = filas.get(id) ?? cuerpo.appendChild(fila(producto));
    const campo = tr.querySelector("input");
    if (document.activeElement !== campo) campo.value = cantidad;
    tr.querySelector(".subtotal").replaceChildren(precio(producto.precio_simulado * cantidad));
  }

  const r = resumen();
  document.getElementById("subtotal-carrito").replaceChildren(precio(r.subtotal));
  document.getElementById("envio-carrito").replaceChildren(precio(r.envio));
  document.getElementById("total-carrito").replaceChildren(precio(r.total));

  const hayPiezas = r.piezas > 0;
  tabla.hidden = !hayPiezas;
  continuar.hidden = !hayPiezas;
  vacio.hidden = hayPiezas;

  contador.textContent = r.piezas;
  contador.hidden = !hayPiezas;
  enlaceNav.setAttribute("aria-label",
    hayPiezas ? `Carrito, ${r.piezas} ${r.piezas === 1 ? "pieza" : "piezas"}` : "Carrito, vacío");
  // Reinicia la animación del contador en cada cambio
  contador.classList.remove("latido");
  void contador.offsetWidth;
  contador.classList.add("latido");

  for (const oyente of oyentes) oyente(r);
}

// Mensaje para lectores de pantalla. Se vacía antes para que un texto repetido
// (agregar dos veces la misma pieza) se vuelva a anunciar.
function anunciar(mensaje) {
  anuncio.textContent = "";
  setTimeout(() => { anuncio.textContent = mensaje; }, 50);
}
