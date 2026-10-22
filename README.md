# Woodbird

Tienda online de aves decorativas talladas en maderas nativas del Chaco (palo santo, algarrobo, quebracho). Las imágenes de producto son generadas con inteligencia artificial.

Proyecto integrador **EcoStart IA** · Tecnicatura Superior en Desarrollo de Software · IES «René Favaloro» · 3er año, 2026.

- **Integrante:** Reiss Jorge Nicolás (Project Manager y Desarrollador)
- **Sitio publicado:** https://nicorsss.github.io/Woodbird/
- **Tablero Kanban:** https://trello.com/b/iGCwIo1k/woodbird

## Estructura

```
index.html      Página principal (HTML5 semántico)
politica-privacidad.html  Política de privacidad (Ley 25.326)
terminos-y-condiciones.html  Términos y condiciones (Ley 24.240)
productos.json  Catálogo de productos (datos estáticos)
css/            Hojas de estilo
js/             Módulos ES: catálogo (Fetch), carrito y checkout
pruebas/        Pruebas de usabilidad responsive (Node + Chrome)
assets/img/     Imágenes de producto
docs/           Entregables escritos de cada sprint
LICENSE         Licencia del código (GNU GPL v3)
```

Para verlo en local hay que servirlo por HTTP, porque el catálogo se carga con Fetch y los scripts son módulos ES (abrir `index.html` como archivo no funciona):

```
python -m http.server 8765
```

y entrar a http://127.0.0.1:8765/.

## Entregables

### Sprint 1 · Concepción, negocio y planificación (24/08 – 11/09)

**Entrega final:** [Carpeta integradora del Sprint 1 (PDF)](docs/sprint-1/00_Carpeta_Integradora_Sprint_1.pdf), que reúne todos los entregables con portada, índice y enlaces al repositorio y al tablero Kanban.

| Materia | Entregable |
|---|---|
| Dirección y Gestión de Proyectos | [Acta de Constitución](docs/sprint-1/01_Acta_de_Constitucion.docx) |
| Dirección y Gestión de Proyectos | [EDT / WBS](docs/sprint-1/02_EDT_WBS.docx) |
| Dirección y Gestión de Proyectos | [Tablero Kanban (Trello)](https://trello.com/b/iGCwIo1k/woodbird) |
| El Emprendedor Digital | [Lienzo de Modelo de Negocio](docs/sprint-1/03_Lienzo_Modelo_de_Negocio.png) |
| El Emprendedor Digital | [Declaración de Triple Impacto](docs/sprint-1/04_Declaracion_Triple_Impacto.docx) |
| Desarrollo de Sitios Web | [Wireframes](docs/sprint-1/05_Diseno_Interfaz_Wireframes.html) |
| Desarrollo de Sitios Web | [Estructura HTML5 semántica](index.html) |
| Legislación Informática | [Informe de Marca y Dominios](docs/sprint-1/06_Informe_Marca_y_Dominios.docx) |
| Legislación Informática | [Declaración Ética de IA](docs/sprint-1/07_Declaracion_Etica_IA.docx) |

### Sprint 2 · Maquetación, datos y privacidad (14/09 – 02/10)

**Entrega final:** [Carpeta integradora del Sprint 2 (PDF)](docs/sprint-2/00_Carpeta_Integradora_Sprint_2.pdf), que reúne todos los entregables con portada, índice, asignación de roles por tarea, el código final de CSS y JSON y los enlaces al repositorio y al tablero Kanban.

| Materia | Entregable | Estado |
|---|---|---|
| Desarrollo de Sitios Web | [CSS responsive (Flexbox + Grid)](css/estilos.css) | Hecho |
| Desarrollo de Sitios Web | [Catálogo en JSON](productos.json) | Hecho |
| Desarrollo de Sitios Web | [Pruebas de usabilidad responsive](docs/sprint-2/07_Pruebas_Usabilidad_Responsive.docx) · [script](pruebas/responsive.mjs) | Hecho: 22 de 22 combinaciones cumplen, después de 6 correcciones; teléfono real (Samsung Galaxy A16, Chrome) OK el 29/09 |
| Dirección y Gestión de Proyectos | [Diagrama de Gantt y control de desvíos](docs/sprint-2/01_Diagrama_de_Gantt_y_Control_de_Desvios.docx) | Control final hecho el 28/09: 21 de 21 paquetes terminados |
| Dirección y Gestión de Proyectos | [Matriz de riesgos](docs/sprint-2/02_Matriz_de_Riesgos.docx) | Actualizada el 29/09: 6 cerrados (R7 con la prueba en un Samsung Galaxy A16 con Chrome), 2 en monitoreo (R1, R9) y R4 pendiente de aprobación |
| Dirección y Gestión de Proyectos | [Solicitud de cambio de alcance SC-01](docs/sprint-2/08_Solicitud_de_Cambio_de_Alcance.docx) | Redactada el 28/09; pendiente de aprobación del docente |
| El Emprendedor Digital | [Informe comparativo: Startup vs. Empresa Tradicional](docs/sprint-2/06_Informe_Startup_vs_Empresa_Tradicional.docx) | Hecho |
| El Emprendedor Digital | [Estrategia de canales y embudo de conversión](docs/sprint-2/04_Estrategia_de_Canales_y_Embudo.docx) · [maqueta de Instagram](docs/sprint-2/04_Instagram_Maqueta.png) | Hecho |
| Legislación Informática | [Política de privacidad (Ley 25.326)](docs/sprint-2/03_Politica_de_Privacidad.docx) · [publicada en el sitio](politica-privacidad.html) | Hecho |
| Legislación Informática | [Justificación del modelo de licenciamiento](docs/sprint-2/05_Justificacion_de_Licencia.docx) · [LICENSE](LICENSE) · [aviso en el sitio](index.html) | Hecho |

### Sprint 3 · Interactividad, asincronismo y contratos (05/10 – 23/10)

| Materia | Entregable | Estado |
|---|---|---|
| Desarrollo de Sitios Web | Consumo asincrónico de `productos.json` y tarjetas generadas en el DOM · [catalogo.js](js/catalogo.js) | Hecho el 22/10: 12 tarjetas desde el JSON, con filtros y buscador |
| Desarrollo de Sitios Web | Carrito de compras y validación del checkout · [carrito.js](js/carrito.js) · [checkout.js](js/checkout.js) | Hecho el 22/10: 33 de 33 combinaciones de las [pruebas](pruebas/responsive.mjs) cumplen |
| Dirección y Gestión de Proyectos | [Matriz de riesgos (reevaluación)](docs/sprint-3/02_Matriz_de_Riesgos.docx) | Hecho el 22/10: 6 riesgos nuevos de la integración de JS; R1 y R2 activos (Alto) |
| Dirección y Gestión de Proyectos | [Plan de casos de prueba](docs/sprint-3/03_Plan_de_Casos_de_Prueba.docx) | 38 casos: 33 automáticos cumplen, 5 manuales para el Sprint 4 |
| Dirección y Gestión de Proyectos | [Registro de solicitudes de cambio](docs/sprint-3/04_Registro_de_Solicitudes_de_Cambio.docx) · [Kanban](https://trello.com/b/iGCwIo1k/woodbird) | SC-02 a SC-04 aprobadas; SC-05 propuesta; SC-01 sin respuesta del docente |
| Legislación Informática | [Términos y Condiciones de uso y compra](docs/sprint-3/01_Terminos_y_Condiciones.docx) · [publicados en el sitio](terminos-y-condiciones.html) | Hecho el 22/10: enlazados en el pie y aceptación obligatoria en el checkout |
| Legislación Informática | Ley 24.240: derecho de arrepentimiento y garantía (cláusulas [9](terminos-y-condiciones.html#arrepentimiento) y [10](terminos-y-condiciones.html#garantia)) | Hecho el 22/10: botón de arrepentimiento en el encabezado (Res. 424/2020) y enlace a la Ventanilla Única Federal (Res. 274/2021) |

## Licencia

- **Código fuente** (`*.html`, `css/`, `js/`, `productos.json`): [GNU GPL, versión 3 o posterior](LICENSE).
- **Documentación** (`docs/`, este README): [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es).
- **Imágenes generadas con IA** (`assets/img/`): sin reclamo de derechos exclusivos.
- La marca «Woodbird» no está incluida en ninguna de estas licencias.

Detalle en [LICENCIA-DOCUMENTACION.md](LICENCIA-DOCUMENTACION.md).
