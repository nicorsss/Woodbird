# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es

Woodbird es la tienda online (de demostración) de aves decorativas inspiradas en el tallado en maderas nativas del Chaco. **Las piezas son diseños ficticios generados con IA: no existe tala ni producto físico.** Esta es la tesis de triple impacto del Sprint 1 (el palo santo está protegido por CITES Apéndice II y la Ley 26.331). No escribas textos que presenten las piezas como talladas o enviadas de verdad, salvo en condicional («si la tienda operara…»), como hacen los Términos. Es el proyecto integrador **EcoStart IA** del 3er año de la Tecnicatura en Desarrollo de Software (IES «René Favaloro», 2026). Hay un solo integrante, que es PM y desarrollador. El trabajo se organiza en sprints con entregables por materia: Desarrollo de Sitios Web, Dirección y Gestión de Proyectos, El Emprendedor Digital y Legislación Informática. El tablero Kanban está en https://trello.com/b/iGCwIo1k/woodbird.

Todo el contenido, el código, los comentarios y los mensajes de commit van en español (es-AR).

## Stack y comandos

Es un sitio estático con HTML, CSS y JavaScript sin frameworks. No hay build, linter ni `package.json`. Para verlo hay que servirlo por HTTP (`python -m http.server 8765`), porque el catálogo se carga con Fetch y los scripts son módulos ES: abrir `index.html` como archivo deja el catálogo vacío con un mensaje de error.

Las pruebas de usabilidad responsive (`pruebas/responsive.mjs`, Node 22+ y Chrome, sin dependencias) recorren las tres páginas en 11 anchos y miden desborde, objetivos táctiles, letra, contraste WCAG AA, anclas y checkout sin red. También prueban el catálogo generado, el carrito (agregar, cantidades, quitar, totales), los filtros y la validación del checkout. Antes de medir agregan Cardenal y Carpintero al carrito. Además verifican los enlaces legales, el botón de arrepentimiento en la primera pantalla y, al final, la falla de carga de `productos.json` (bloqueada con `Fetch.failRequest`). Los casos están numerados en `docs/sprint-3/03_Plan_de_Casos_de_Prueba.docx`. Después de cambiar estilos o JS, córrelas:

```
python -m http.server 8765
node pruebas/responsive.mjs http://127.0.0.1:8765/ pruebas/salida
```

## Arquitectura

- **`index.html`** es una sola página con anclas (`#inicio`, `#catalogo`, `#carrito`, `#checkout`). La barra de navegación salta entre esas secciones y lleva el contador del carrito. Las listas de «Diseños nuevos» y del catálogo y las filas del carrito están **vacías en el HTML**: las llena JS. Los precios van en `<data value="…">`.
- **`productos.json`** es la única fuente de productos (campos `id`, `nombre`, `descripcion`, `precio_simulado`, `imagen_ia_url`, `categoria`, `medida_cm`, `stock`). «Diseños nuevos» muestra las 4 piezas con stock de `id` más alto. `stock: false` deja el botón en «Sin stock».
- **`js/`** son módulos ES y `app.js` es el punto de entrada (`<script type="module">`):
  - `utilidades.js` tiene `el()`, que crea nodos con `textContent`. No uses `innerHTML` con datos del JSON.
  - `catalogo.js` hace `fetch` de `productos.json`, genera las tarjetas y resuelve los filtros (objeto `FILTROS`, por el `value` de cada radio) y el buscador.
  - `carrito.js` guarda el estado en un `Map` en memoria, sin `localStorage`. Calcula los totales desde el catálogo, con envío fijo de $5.900 y hasta 10 unidades por pieza. Actualiza las filas en el lugar para no perder el foco y avisa los cambios con `alCambiar()`.
  - `checkout.js` simula el checkout. El formulario **no tiene `action` ni botón submit**. Si el carrito está vacío, bloquea la compra. Aplica las reglas de `REGLAS` (nombre y apellido, dominio del correo, teléfono, CP) con `setCustomValidity()` y valida con `reportValidity()`. Al confirmar, muestra el resultado, ejecuta `reset()` y vacía el carrito. Esto es un requisito legal: `politica-privacidad.html` (Ley 25.326) promete que los datos no salen del navegador. No agregues envíos, `fetch`, `localStorage` ni analytics con datos del formulario sin actualizar también la política.
- **`css/estilos.css`** es la única hoja de estilos. Es *mobile-first* y está organizada en secciones numeradas. Los tokens de diseño son variables en `:root` (paleta «palo santo», tipografías Fraunces y Archivo, unidad base `--u: 4px`). Los breakpoints son `600px` (tableta) y `960px` (escritorio). Solo usa Flexbox y Grid. Hay reglas de estilo con intención: el ámbar (`--resina`) se usa solo en precios, «Agregar» va con contorno (no relleno) y los objetivos táctiles miden `--alto-tactil`.
- **`politica-privacidad.html`** y **`terminos-y-condiciones.html`** son páginas aparte que reutilizan la misma hoja de estilos (sección 9 del CSS) y enlazan de vuelta con `index.html#…`. Los términos **no se editan a mano**: los genera `../herramientas/terminos.py` (fuera del repo), que escribe a la vez la página y `docs/sprint-3/01_Terminos_y_Condiciones.docx`. Para cambiar una cláusula, cambia la fuente y vuelve a ejecutar el script.
- **Enlaces legales obligatorios en las tres páginas:** el «Botón de arrepentimiento» va en el encabezado, visible sin desplazarse (Res. SCI 424/2020; la prueba `ARREPENTIMIENTO` lo verifica). El pie lleva la Declaración ética de IA, la Política de privacidad, los Términos y condiciones y el enlace «Defensa de las y los Consumidores. Para reclamos ingrese aquí» (Res. SCI 274/2021). El checkout exige aceptar los términos (`#terminos`) y la política (`#consentimiento`), y avisa el plazo de arrepentimiento de 10 días. Si cambias el carrito, el checkout o los envíos, revisa que las cláusulas 4 a 10 sigan diciendo lo mismo que el código.

## Convenciones del proyecto

- **Transparencia de IA:** las imágenes de producto son generadas con IA y cada una lleva `<figcaption>Imagen con IA</figcaption>`. El pie enlaza la Declaración Ética de IA. Mantén esto en cualquier producto o imagen nueva.
- **Accesibilidad:** HTML5 semántico. Cada sección tiene `aria-labelledby`, las etiquetas ocultas usan `.visualmente-oculto` y se respeta `prefers-reduced-motion`.
- **Licencias:** el código es `GPL-3.0-or-later` (archivo `LICENSE`, con encabezado SPDX en los CSS y JS), la documentación de `docs/` es CC BY-NC-SA 4.0 y las imágenes generadas con IA quedan sin reclamo de derechos. El pie de ambas páginas HTML repite el aviso. Todo archivo de código nuevo lleva el mismo encabezado SPDX. El detalle está en `LICENCIA-DOCUMENTACION.md`.
- Las imágenes de producto todavía no existen (riesgo R6, pasan al Sprint 3). Por la contingencia del 28/09, las tarjetas usan `<div class="lamina" role="img">` en lugar de `<img>`, con el mismo sello. Las rutas previstas están en `productos.json` (`imagen_ia_url`, `assets/img/*.webp`). Al generarlas, se vuelve a `<img>` con `alt` descriptivo.

## Entregables y documentación

- Los entregables escritos (.docx, .png, .html) van en `docs/sprint-N/` con prefijo numérico (`01_…`, `02_…`). Suelen ser copias de los archivos de trabajo de la carpeta padre (`../`), que está fuera del repositorio.
- Cuando se completa un entregable, actualiza la tabla **Entregables** del `README.md` (enlace y columna «Estado»).
- Los commits van directo a `main`, en español, y describen el entregable junto con el sprint, por ejemplo: `Diagrama de Gantt y matriz de riesgos (Sprint 2, semana 4)`.
