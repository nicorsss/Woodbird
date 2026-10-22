// Checkout simulado.
// El formulario no se envía: se validan los campos en el navegador y se muestra
// una confirmación. Los datos personales no salen del equipo del usuario ni se
// guardan en ningún lado (ver politica-privacidad.html, cláusulas 2 y 8).
//
// © 2026 Reiss Jorge Nicolás
// SPDX-License-Identifier: GPL-3.0-or-later (ver LICENSE)

import { alCambiar, resumen, vaciar } from "./carrito.js";
import { pesos, precio } from "./utilidades.js";

const formulario = document.getElementById("form-checkout");
const boton = document.getElementById("ir-al-pago");
const confirmacion = document.getElementById("confirmacion");
const error = document.getElementById("error-pago");
const total = document.getElementById("total-checkout");

// Reglas de consistencia que los atributos del HTML no alcanzan a expresar.
// Un campo vacío devuelve "" y lo resuelve `required`, con su propio mensaje.
const PALABRA = "\\p{L}+(?:['’-]\\p{L}+)*";
const REGLAS = {
  nombre: (valor) =>
    !valor || new RegExp(`^${PALABRA}(?:\\s+${PALABRA})+$`, "u").test(valor)
      ? "" : "Escribí tu nombre y tu apellido, sólo con letras.",
  email: (valor) =>
    !valor || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(valor)
      ? "" : "El correo tiene que incluir el dominio completo, por ejemplo nombre@correo.com.",
  telefono: (valor) =>
    !valor || /^\d{8,15}$/.test(valor.replace(/[\s()+-]/g, ""))
      ? "" : "El teléfono tiene que tener entre 8 y 15 números, con la característica.",
  cp: (valor) =>
    !valor || /^\d{4}$/.test(valor)
      ? "" : "El código postal tiene 4 números, por ejemplo 3500.",
};

function aplicarRegla(campo) {
  const regla = REGLAS[campo.name];
  if (regla) campo.setCustomValidity(regla(campo.value.trim()));
}

// El mensaje de error se recalcula mientras la persona corrige el campo
formulario.addEventListener("input", (evento) => aplicarRegla(evento.target));

// El total del checkout sigue al carrito en tiempo real
alCambiar((pedido) => {
  total.replaceChildren(precio(pedido.total));
  if (pedido.piezas > 0) error.textContent = "";
});

boton.addEventListener("click", () => {
  confirmacion.textContent = "";
  error.textContent = "";

  const pedido = resumen();
  if (pedido.piezas === 0) {
    error.textContent = "Tu carrito está vacío: agregá al menos una pieza del catálogo antes de pagar.";
    return;
  }

  for (const campo of formulario.elements) aplicarRegla(campo);
  if (!formulario.reportValidity()) {
    return;
  }

  const nombre = formulario.elements.nombre.value.trim().split(/\s+/)[0];
  const numero = "WB-" + Date.now().toString(36).slice(-6).toUpperCase();
  const piezas = `${pedido.piezas} ${pedido.piezas === 1 ? "pieza" : "piezas"}`;
  confirmacion.textContent =
    `¡Listo, ${nombre}! Tu pedido simulado ${numero} (${piezas}, ${pesos(pedido.total)} con envío) quedó confirmado. ` +
    "Como es una demostración, no se cobró nada y tus datos no se enviaron ni se guardaron. " +
    `Si te arrepentís, tenés 10 días corridos desde la entrega: usá el Botón de arrepentimiento con el número ${numero}.`;

  // Se borran los datos del formulario apenas se usan, y el carrito queda vacío.
  formulario.reset();
  vaciar();
});
