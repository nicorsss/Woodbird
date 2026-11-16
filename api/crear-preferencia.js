// Función de Vercel que crea una preferencia de pago de Mercado Pago (Checkout Pro).
//
// El sitio sigue publicado en GitHub Pages. Esta función es lo único que corre en
// un servidor, porque el Access Token de Mercado Pago no puede quedar en el
// navegador. Recibe sólo los ids y las cantidades del carrito: los precios, el
// stock y el envío salen de productos.json, nunca de lo que mande el navegador.
// No recibe ni guarda datos personales: la persona los carga en Mercado Pago.
//
// Variables de entorno (en el panel de Vercel):
//   MP_ACCESS_TOKEN  credencial de Mercado Pago (de prueba o de producción)
//   SITIO_URL        dirección pública del sitio, con barra final
//                    (por defecto https://nicorsss.github.io/Woodbird/)
//   MP_MONTO_PRUEBA  opcional: si existe, cada ítem (y el envío) se cobra este
//                    monto, por ejemplo 0.01, para probar pagos con montos mínimos.
//                    Sin la variable se cobran los precios de productos.json.
//
// © 2026 Reiss Jorge Nicolás
// SPDX-License-Identifier: GPL-3.0-or-later (ver LICENSE)

import productos from "../productos.json" with { type: "json" };

const ENVIO = 5900;  // igual que js/carrito.js
const MAXIMO = 10;   // tope de unidades por pieza, igual que js/carrito.js
const SITIO = process.env.SITIO_URL ?? "https://nicorsss.github.io/Woodbird/";
const ORIGEN = new URL(SITIO).origin;
const PRUEBA = Number(process.env.MP_MONTO_PRUEBA) || 0;
const catalogo = new Map(productos.map((p) => [p.id, p]));

// Arma los ítems de la preferencia, o devuelve un texto de error
function armarItems(lineas) {
  if (!Array.isArray(lineas) || lineas.length === 0 || lineas.length > catalogo.size) {
    return "El carrito está vacío o no es válido.";
  }
  const vistos = new Set();
  const items = [];
  for (const { id, cantidad } of lineas) {
    const producto = catalogo.get(id);
    if (!producto) return "Una de las piezas del carrito ya no está en el catálogo.";
    if (!producto.stock) return `${producto.nombre} no tiene stock.`;
    if (vistos.has(id)) return "El carrito repite una pieza.";
    if (!Number.isInteger(cantidad) || cantidad < 1 || cantidad > MAXIMO) {
      return `La cantidad de ${producto.nombre} tiene que ser de 1 a ${MAXIMO}.`;
    }
    vistos.add(id);
    items.push({
      id: String(producto.id),
      title: `Woodbird · ${producto.nombre}${PRUEBA ? " (monto de prueba)" : ""}`,
      description: `${producto.categoria} · ${producto.medida_cm} cm`,
      picture_url: new URL(producto.imagen_ia_url, SITIO).href,
      category_id: "home",
      quantity: cantidad,
      currency_id: "ARS",
      unit_price: PRUEBA || producto.precio_simulado,
    });
  }
  items.push({
    id: "envio",
    title: "Envío",
    quantity: 1,
    currency_id: "ARS",
    unit_price: PRUEBA || ENVIO,
  });
  return items;
}

export default async function handler(req, res) {
  // Se acepta el sitio publicado y, para las pruebas, un servidor local
  const origen = req.headers?.origin ?? "";
  const local = /^http:\/\/(127\.0\.0\.1|localhost)(:\d+)?$/.test(origen);
  res.setHeader("Access-Control-Allow-Origin", local ? origen : ORIGEN);
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Vary", "Origin");

  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Método no permitido." });

  const token = process.env.MP_ACCESS_TOKEN;
  if (!token) return res.status(500).json({ error: "El pago no está configurado." });

  const items = armarItems(req.body?.items);
  if (typeof items === "string") return res.status(400).json({ error: items });

  const numero = "WB-" + Date.now().toString(36).slice(-6).toUpperCase();
  const volver = (estado) => `${SITIO}?pago=${estado}#checkout`;

  const respuesta = await fetch("https://api.mercadopago.com/checkout/preferences", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "X-Idempotency-Key": crypto.randomUUID(),
    },
    body: JSON.stringify({
      items,
      external_reference: numero,
      statement_descriptor: "WOODBIRD",
      back_urls: {
        success: volver("aprobado"),
        pending: volver("pendiente"),
        failure: volver("rechazado"),
      },
      auto_return: "approved",
    }),
  });

  if (!respuesta.ok) {
    console.error("Mercado Pago respondió", respuesta.status, await respuesta.text());
    return res.status(502).json({ error: "Mercado Pago no pudo iniciar el pago. Probá de nuevo en unos minutos." });
  }

  const preferencia = await respuesta.json();
  return res.status(200).json({ numero, url: preferencia.init_point });
}
