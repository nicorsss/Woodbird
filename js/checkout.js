// Checkout con Mercado Pago (Checkout Pro).
// Los campos se validan en el navegador y no se envían a ningún lado: al servidor
// de pago (api/crear-preferencia.js, en Vercel) sólo viajan los ids y las
// cantidades del carrito. El servidor arma la preferencia con los precios de
// productos.json y devuelve la dirección de pago de Mercado Pago, donde la
// persona paga. Al terminar, Mercado Pago la devuelve a index.html?pago=…#checkout.
//
// © 2026 Reiss Jorge Nicolás
// SPDX-License-Identifier: GPL-3.0-or-later (ver LICENSE)

import { alCambiar, resumen, vaciar } from "./carrito.js";
import { precio } from "./utilidades.js";

const formulario = document.getElementById("form-checkout");
const boton = document.getElementById("ir-al-pago");
const confirmacion = document.getElementById("confirmacion");
const error = document.getElementById("error-pago");
const total = document.getElementById("total-checkout");
const espera = document.getElementById("checkout-espera");
const continuar = document.querySelector("#continuar-compra a");
const titulo = document.getElementById("titulo-checkout");

// Dirección de la función de pago desplegada en Vercel
const API_PAGO = "https://woodbird-h7cb.vercel.app/api/crear-preferencia";

const VUELTAS = {
  aprobado: "¡Gracias! Mercado Pago aprobó tu pago y te envió el comprobante por correo.",
  pendiente: "Tu pago quedó pendiente en Mercado Pago. Cuando se acredite, Mercado Pago te avisa por correo.",
  rechazado: "Mercado Pago no pudo procesar el pago y no se te cobró nada. Podés volver a intentarlo con otro medio.",
};

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

// Paso actual de la compra: carrito → datos → pago
function marcarPaso(paso) {
  for (const li of document.querySelectorAll("[data-paso]")) {
    if (li.dataset.paso === paso) li.setAttribute("aria-current", "step");
    else li.removeAttribute("aria-current");
  }
}

// El formulario de datos se muestra recién cuando el carrito está listo
function mostrarFormulario(visible) {
  formulario.hidden = !visible;
  espera.hidden = visible;
  marcarPaso(visible ? "datos" : "carrito");
}

continuar.addEventListener("click", (evento) => {
  // El salto se hace a mano para que el foco quede en el título y no lo pise el ancla
  evento.preventDefault();
  confirmacion.textContent = "";
  error.textContent = "";
  mostrarFormulario(true);
  document.getElementById("checkout").scrollIntoView({ block: "start" });
  titulo.focus({ preventScroll: true });
  history.replaceState(null, "", "#checkout");
});

// El total del checkout sigue al carrito en tiempo real
alCambiar((pedido) => {
  total.replaceChildren(precio(pedido.total));
  if (pedido.piezas > 0) error.textContent = "";
  // Si el carrito queda vacío, se vuelve al primer paso
  else if (!formulario.hidden && !boton.disabled) mostrarFormulario(false);
});

boton.addEventListener("click", async () => {
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

  boton.disabled = true;
  boton.textContent = "Conectando con Mercado Pago…";
  marcarPaso("pago");
  try {
    const respuesta = await fetch(API_PAGO, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        items: pedido.items.map(({ producto, cantidad }) => ({ id: producto.id, cantidad })),
      }),
    });
    const datos = await respuesta.json().catch(() => ({}));
    if (!respuesta.ok || !datos.url) {
      throw new Error(datos.error ?? "Mercado Pago no pudo iniciar el pago. Probá de nuevo en unos minutos.");
    }

    // Se borran los datos del formulario antes de salir hacia Mercado Pago
    formulario.reset();
    vaciar();
    window.location.assign(datos.url);
  } catch (falla) {
    restaurarBoton();
    marcarPaso("datos");
    // Un TypeError de fetch es una falla de red; su mensaje viene en inglés
    error.textContent = falla instanceof TypeError
      ? "No pudimos conectar con Mercado Pago. Revisá tu conexión y probá de nuevo."
      : falla.message;
  }
});

function restaurarBoton() {
  boton.disabled = false;
  boton.textContent = "Ir al pago";
}

// Si la persona vuelve desde Mercado Pago con «Atrás», el navegador puede restaurar la
// página tal como quedó (con el botón bloqueado): se rehabilita y se vuelve al carrito.
window.addEventListener("pageshow", (evento) => {
  if (!evento.persisted || !boton.disabled) return;
  restaurarBoton();
  if (resumen().piezas === 0) mostrarFormulario(false);
});

// Vuelta desde Mercado Pago: muestra el resultado y limpia la dirección
const vuelta = new URLSearchParams(window.location.search);
const estado = vuelta.get("pago");
if (VUELTAS[estado]) {
  espera.hidden = true;
  marcarPaso("pago");
  const numero = vuelta.get("external_reference");
  (estado === "rechazado" ? error : confirmacion).textContent =
    VUELTAS[estado] + (numero && estado !== "rechazado"
      ? ` Tu número de pedido es ${numero}: guardalo para cualquier consulta. Si te arrepentís, tenés 10 días corridos ` +
        "desde la entrega: usá el Botón de arrepentimiento con ese número."
      : "");
  history.replaceState(null, "", window.location.pathname + "#checkout");
}
