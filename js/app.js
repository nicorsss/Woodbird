// Punto de entrada: carga el catálogo y conecta el carrito y el checkout.
//
// © 2026 Reiss Jorge Nicolás
// SPDX-License-Identifier: GPL-3.0-or-later (ver LICENSE)

import { cargarProductos, iniciarCatalogo, mostrarErrorCatalogo } from "./catalogo.js";
import { agregar, iniciarCarrito } from "./carrito.js";
import "./checkout.js";

try {
  const productos = await cargarProductos();
  iniciarCarrito(productos);
  iniciarCatalogo(productos, { alAgregar: agregar });
} catch (error) {
  mostrarErrorCatalogo(error);
}
