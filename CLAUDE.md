# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es

Woodbird es la tienda online (de demostración) de aves talladas en maderas nativas del Chaco. Es el proyecto integrador **EcoStart IA** del 3er año de la Tecnicatura en Desarrollo de Software (IES «René Favaloro», 2026). Hay un solo integrante, que es PM y desarrollador. El trabajo se organiza en sprints con entregables por materia: Desarrollo de Sitios Web, Dirección y Gestión de Proyectos, El Emprendedor Digital y Legislación Informática. El tablero Kanban está en https://trello.com/b/iGCwIo1k/woodbird.

Todo el contenido, el código, los comentarios y los mensajes de commit van en español (es-AR).

## Stack y comandos

Es un sitio estático con HTML, CSS y JavaScript sin frameworks. No hay build, linter, tests ni `package.json`. Para verlo, abre `index.html` en el navegador. No hay que ejecutar nada más.

## Arquitectura

- **`index.html`** es una sola página con anclas (`#inicio`, `#catalogo`, `#carrito`, `#checkout`). La barra de navegación salta entre esas secciones. El catálogo y el carrito tienen **el contenido escrito a mano en el HTML**, con precios en `<data value="…">`.
- **`productos.json`** es el catálogo de datos (campos `id`, `nombre`, `descripcion`, `precio_simulado`, `imagen_ia_url`, `categoria`, `medida_cm`, `stock`). Por ahora ningún script lo carga. Si cambias productos o precios, mantén sincronizados el JSON y las tarjetas del HTML.
- **`css/estilos.css`** es la única hoja de estilos. Es *mobile-first* y está organizada en secciones numeradas. Los tokens de diseño son variables en `:root` (paleta «palo santo», tipografías Fraunces y Archivo, unidad base `--u: 4px`). Los breakpoints son `600px` (tableta) y `960px` (escritorio). Solo usa Flexbox y Grid. Hay reglas de estilo con intención: el ámbar (`--resina`) se usa solo en precios, «Agregar» va con contorno (no relleno) y los objetivos táctiles miden `--alto-tactil`.
- **`js/checkout.js`** simula el checkout. El formulario **no tiene `action` ni botón submit**: valida en el navegador con `reportValidity()`, muestra una confirmación y ejecuta `reset()`. Esto es un requisito legal: `politica-privacidad.html` (Ley 25.326) promete que los datos no salen del navegador. No agregues envíos, `fetch`, `localStorage` ni analytics con datos del formulario sin actualizar también la política.
- **`politica-privacidad.html`** es una página aparte que reutiliza la misma hoja de estilos (sección 9 del CSS) y enlaza de vuelta con `index.html#…`.

## Convenciones del proyecto

- **Transparencia de IA:** las imágenes de producto son generadas con IA y cada una lleva `<figcaption>Imagen con IA</figcaption>`. El pie enlaza la Declaración Ética de IA. Mantén esto en cualquier producto o imagen nueva.
- **Accesibilidad:** HTML5 semántico. Cada sección tiene `aria-labelledby`, las etiquetas ocultas usan `.visualmente-oculto` y se respeta `prefers-reduced-motion`.
- **Licencias:** el código es `GPL-3.0-or-later` (archivo `LICENSE`, con encabezado SPDX en los CSS y JS), la documentación de `docs/` es CC BY-NC-SA 4.0 y las imágenes generadas con IA quedan sin reclamo de derechos. El pie de ambas páginas HTML repite el aviso. Todo archivo de código nuevo lleva el mismo encabezado SPDX. El detalle está en `LICENCIA-DOCUMENTACION.md`.
- Las imágenes referenciadas (`assets/img/*.webp`) todavía no están en el repositorio; solo existe `.gitkeep`.

## Entregables y documentación

- Los entregables escritos (.docx, .png, .html) van en `docs/sprint-N/` con prefijo numérico (`01_…`, `02_…`). Suelen ser copias de los archivos de trabajo de la carpeta padre (`../`), que está fuera del repositorio.
- Cuando se completa un entregable, actualiza la tabla **Entregables** del `README.md` (enlace y columna «Estado»).
- Los commits van directo a `main`, en español, y describen el entregable junto con el sprint, por ejemplo: `Diagrama de Gantt y matriz de riesgos (Sprint 2, semana 4)`.
