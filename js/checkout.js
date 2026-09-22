// Checkout simulado.
// El formulario no se envía: se validan los campos en el navegador y se muestra
// una confirmación. Los datos personales no salen del equipo del usuario ni se
// guardan en ningún lado (ver politica-privacidad.html, cláusulas 2 y 8).

const formulario = document.getElementById("form-checkout");
const boton = document.getElementById("ir-al-pago");
const confirmacion = document.getElementById("confirmacion");

boton.addEventListener("click", () => {
  if (!formulario.reportValidity()) {
    return;
  }

  const nombre = formulario.elements.nombre.value.trim().split(" ")[0];
  confirmacion.textContent =
    `¡Listo, ${nombre}! Tu pedido simulado quedó confirmado. ` +
    "Como es una demostración, no se cobró nada y tus datos no se enviaron ni se guardaron.";

  // Se borran los datos del formulario apenas se usan.
  formulario.reset();
});
