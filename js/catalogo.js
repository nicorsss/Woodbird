// Catálogo: lee productos.json de forma asincrónica y genera las tarjetas en el DOM.
// También resuelve los filtros por chip y el buscador del encabezado.
//
// © 2026 Reiss Jorge Nicolás
// SPDX-License-Identifier: GPL-3.0-or-later (ver LICENSE)

import { el, normalizar, precio } from "./utilidades.js";

const listaCatalogo = document.getElementById("lista-catalogo");
const listaRecientes = document.getElementById("lista-recientes");
const estado = document.getElementById("estado-catalogo");
const filtros = document.getElementById("filtros-catalogo");
const buscador = document.querySelector(".buscador");
const campoBusqueda = document.getElementById("buscar");

// Cada chip de filtro (value del radio) con su condición
const FILTROS = {
  "todas": () => true,
  "palo-santo": (p) => p.categoria === "Palo santo",
  "hasta-25000": (p) => p.precio_simulado <= 25000,
};

const RECIENTES = 4;

export async function cargarProductos(url = "productos.json") {
  const respuesta = await fetch(url);
  if (!respuesta.ok) {
    throw new Error(`No se pudo leer ${url} (HTTP ${respuesta.status})`);
  }
  return respuesta.json();
}

// Contingencia del riesgo R6: mientras no existan las imágenes de imagen_ia_url,
// la tarjeta muestra una lámina de color con el sello de transparencia.
function figura(producto) {
  return el("figure", {},
    el("div", { class: "lamina", role: "img", "aria-label": `${producto.nombre}: imagen en preparación` }),
    el("figcaption", {}, "Imagen con IA"));
}

function tarjeta(producto, conBoton) {
  const articulo = el("article", { class: "tarjeta" },
    figura(producto),
    el("h3", {}, producto.nombre),
    el("p", {}, `${producto.categoria} · ${producto.medida_cm} cm`),
    el("p", { class: "precio" }, precio(producto.precio_simulado)));

  if (conBoton) {
    articulo.append(producto.stock
      ? el("button", { type: "button", "data-agregar": producto.id, "aria-label": `Agregar ${producto.nombre} al carrito` }, "Agregar")
      : el("button", { type: "button", disabled: true }, "Sin stock"));
  }
  return el("li", {}, articulo);
}

function filtrar(productos) {
  const condicion = FILTROS[filtros.elements.filtro.value] ?? FILTROS.todas;
  const busqueda = normalizar(campoBusqueda.value);
  return productos.filter((p) =>
    condicion(p) && normalizar(`${p.nombre} ${p.categoria}`).includes(busqueda));
}

function dibujarCatalogo(productos) {
  const visibles = filtrar(productos);
  listaCatalogo.replaceChildren(...visibles.map((p) => tarjeta(p, true)));

  if (visibles.length === 0) {
    estado.textContent = campoBusqueda.value.trim()
      ? `No hay piezas que coincidan con «${campoBusqueda.value.trim()}».`
      : "No hay piezas con ese filtro.";
  } else {
    estado.textContent = `Mostrando ${visibles.length} de ${productos.length} piezas.`;
  }
}

export function iniciarCatalogo(productos, { alAgregar }) {
  // Las piezas más nuevas son las de id más alto
  const recientes = productos.filter((p) => p.stock).slice(-RECIENTES).reverse();
  listaRecientes.replaceChildren(...recientes.map((p) => tarjeta(p, false)));
  listaRecientes.removeAttribute("aria-busy");

  dibujarCatalogo(productos);
  listaCatalogo.removeAttribute("aria-busy");

  // Un solo oyente para todos los botones, aunque la grilla se vuelva a dibujar
  listaCatalogo.addEventListener("click", (evento) => {
    const boton = evento.target.closest("[data-agregar]");
    if (!boton) return;
    alAgregar(Number(boton.dataset.agregar));
    boton.textContent = "Agregado ✓";
    setTimeout(() => { boton.textContent = "Agregar"; }, 1200);
  });

  filtros.addEventListener("change", () => dibujarCatalogo(productos));
  campoBusqueda.addEventListener("input", () => dibujarCatalogo(productos));
  buscador.addEventListener("submit", (evento) => {
    evento.preventDefault();
    dibujarCatalogo(productos);
    document.getElementById("catalogo").scrollIntoView();
  });
}

export function mostrarErrorCatalogo(error) {
  console.error("Woodbird: no se pudo cargar el catálogo.", error,
    "Si abriste index.html como archivo, servilo con «python -m http.server».");
  for (const lista of [listaCatalogo, listaRecientes]) lista.removeAttribute("aria-busy");
  estado.textContent = "No pudimos cargar el catálogo. Revisá tu conexión y recargá la página.";
  estado.classList.add("error");
}
