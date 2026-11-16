# Genera los entregables de Dirección y Gestión de Proyectos del Sprint 3 (tareas 3.3 y 3.4):
#   sitio/docs/sprint-3/02_Matriz_de_Riesgos.docx
#   sitio/docs/sprint-3/03_Plan_de_Casos_de_Prueba.docx
#   sitio/docs/sprint-3/04_Registro_de_Solicitudes_de_Cambio.docx
# Uso: python herramientas/gestion_sprint3.py

from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Inches

from terminos import VERDE, sombrear, tabla, texto_celda, viñeta

DESTINO = Path(__file__).resolve().parent.parent / "sitio" / "docs" / "sprint-3"
FECHA = "22 de octubre de 2026"
DGP = "Dirección y Gestión de Proyectos Tecnológicos (DGP)"


def nuevo(titulo, actividad, rol="Project Manager"):
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1)
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10.5)
    for nombre in ("Heading 1", "Heading 2"):
        doc.styles[nombre].font.name = "Calibri"
        doc.styles[nombre].font.color.rgb = VERDE

    r = doc.add_paragraph().add_run(titulo)
    r.bold, r.font.size, r.font.color.rgb = True, Pt(18), VERDE
    r = doc.add_paragraph().add_run("Woodbird — Aves decorativas de madera")
    r.font.size, r.font.color.rgb = Pt(12), RGBColor(0x44, 0x44, 0x44)

    t = doc.add_table(rows=0, cols=2)
    t.style = "Table Grid"
    for clave, valor in [("Materia", DGP), ("Actividad", actividad), ("Rol", rol),
                         ("Startup", "Woodbird — Aves decorativas de madera"), ("Autor", "Reiss Jorge Nicolás"),
                         ("Docente", "Ibañez Erick"), ("Fecha", FECHA)]:
        c = t.add_row().cells
        sombrear(c[0], "E3EBE5")
        texto_celda(c[0], clave, negrita=True)
        texto_celda(c[1], valor)
    for fila in t.rows:
        fila.cells[0].width, fila.cells[1].width = Inches(1.4), Inches(5.1)
    doc.add_paragraph()
    return doc


def firma(doc, texto):
    doc.add_heading("Firma", level=1)
    doc.add_paragraph(texto)
    doc.add_paragraph("Project Manager: Reiss Jorge Nicolás")
    doc.add_paragraph("Firma: ______________________________")
    doc.add_paragraph("Fecha: ____ / ____ / 2026")


# ---------------------------------------------------------------------------
# 02 · Matriz de riesgos (reevaluación del Sprint 3)
# ---------------------------------------------------------------------------
# id, riesgo, categoría, P, I, disparador
RIESGOS = [
    ("R1", "Sobrecarga del único integrante, que cubre los cuatro roles del proyecto, y consecuente incumplimiento de entregas.",
     "Equipo", 5, 5, "Dos o más tareas vencidas en la misma semana."),
    ("R2", "Atraso en el inicio del sprint: el trabajo empieza tarde y se comprime contra la fecha de entrega.",
     "Tiempos", 5, 4, "Fin de la semana 7 sin el hito «Fetch API conectada»."),
    ("R3", "La campaña de Instagram no llega a publicarse, aunque la Tarea 3.5 pide publicaciones reales con llamadas a la acción.",
     "Alcance", 4, 3, "Llegar a la semana 9 sin publicaciones."),
    ("R4", "Inconsistencia de alcance entre el Acta (backend y pagos reales) y la consigna (compra simulada). La solicitud SC-01 no tiene respuesta.",
     "Alcance", 3, 4, "Observación del docente o requisito que contradiga el Acta."),
    ("R6", "Las imágenes de producto con IA no se generan y el catálogo sigue con láminas de color.",
     "Técnico / Legal", 5, 2, "Semana 8 sin imágenes en assets/img/."),
    ("R7", "Fallas de funcionamiento o de visualización en navegadores o dispositivos no probados. El JavaScript nuevo no se probó en un teléfono real ni en Firefox o Safari.",
     "Técnico", 2, 3, "Un caso de prueba manual falla en un dispositivo real."),
    ("R8", "Pérdida de fuentes del proyecto: los generadores de documentos y el script de Trello están fuera del repositorio.",
     "Gestión", 2, 3, "Cambio de equipo o borrado de la carpeta de trabajo."),
    ("R9", "Caída o bloqueo de servicios externos (GitHub, Trello, Google Fonts). El token de la API de Trello vence el 22/10.",
     "Técnico", 4, 2, "Servicio inaccesible o token vencido el día de la entrega."),
    ("R10", "El catálogo no carga si el sitio se abre como archivo (file://), porque Fetch y los módulos ES requieren un servidor HTTP.",
     "Técnico", 5, 3, "Catálogo vacío al abrir index.html con doble clic."),
    ("R11", "Falla de carga de productos.json en producción (red caída o JSON mal formado), que deja la tienda sin catálogo.",
     "Técnico", 2, 4, "Grilla vacía o error de JavaScript en la consola."),
    ("R12", "Incoherencia entre las cláusulas legales y el comportamiento del software (envío, tope de unidades, stock, plazos).",
     "Legal", 3, 4, "Un cambio en el carrito o el checkout sin revisión de los Términos y Condiciones."),
    ("R13", "Regresiones al reemplazar el HTML fijo por DOM generado con JavaScript: pruebas que dependen del contenido fijo y pérdida del foco del teclado al redibujar.",
     "Técnico", 3, 3, "Pruebas del Sprint 2 que fallan tras el cambio."),
    ("R14", "Inyección de código (XSS) si los datos del JSON se insertan en la página como HTML.",
     "Seguridad", 2, 4, "Uso de innerHTML con datos externos."),
    ("R15", "Incompatibilidad de navegadores antiguos con módulos ES, await de nivel superior y expresiones regulares Unicode.",
     "Técnico", 2, 3, "Reporte de catálogo vacío en un navegador desactualizado."),
]

RESPUESTA = [
    ("R1", "Mitigar", "Hitos semanales verificables: al menos un commit o una tarjeta movida por semana. Límite de dos tareas en «En progreso».",
     "Concentrar el esfuerzo en las tareas con más peso en la nota y postergar las no críticas mediante solicitudes de cambio (SC-05).", "Project Manager"),
    ("R2", "Mitigar", "Revisión del tablero cada lunes contra el cronograma de la consigna.",
     "Fast tracking: resolver en paralelo las tareas técnicas y legales que se apoyan entre sí (carrito y Términos y Condiciones).", "Project Manager"),
    ("R3", "Evitar", "Preparar las piezas y los textos con CTA antes de la semana 9.",
     "Documentar las piezas maquetadas con métricas proyectadas y declararlas como simuladas, como en el Sprint 2.", "Responsable de Negocio"),
    ("R4", "Mitigar", "Reiterar la solicitud SC-01 adjuntándola a la carpeta del Sprint 3.",
     "Mantener el alcance simulado, que es el que piden las consignas, hasta que el docente decida.", "Project Manager"),
    ("R6", "Aceptar", "Postergar la generación al Sprint 4 (SC-05).",
     "Mantener las láminas de color con el sello «Imagen con IA».", "Desarrollador"),
    ("R7", "Mitigar", "Casos de prueba manuales CP-37 (teléfono real) y CP-38 (Firefox) antes del lanzamiento.",
     "Corregir y volver a ejecutar las pruebas automáticas en los 11 anchos.", "Desarrollador"),
    ("R8", "Mitigar", "Subir los generadores y el script de Trello al repositorio, sin las credenciales.",
     "Regenerar los documentos desde las copias de la carpeta de trabajo.", "Project Manager"),
    ("R9", "Aceptar", "Actualizar el tablero antes del vencimiento y regenerar el token por 30 días.",
     "Entregar capturas del tablero junto con la carpeta.", "Project Manager"),
    ("R10", "Mitigar", "Mensaje de error visible si el catálogo no carga e instrucciones de uso con «python -m http.server» en el README.",
     "El sitio publicado en GitHub Pages se sirve por HTTPS y no está afectado.", "Desarrollador"),
    ("R11", "Mitigar", "Mensaje de error accesible cuando falla la carga (CP-10). Las pruebas cargan el JSON en cada ejecución.",
     "Volver a la versión anterior de productos.json desde el historial de Git.", "Desarrollador"),
    ("R12", "Evitar", "Tabla de coherencia entre cláusulas y código (Términos y Condiciones, sección 5). Casos de prueba con referencia a la cláusula. Regla escrita en CLAUDE.md.",
     "Corregir el código o publicar una nueva versión de los términos antes del lanzamiento.", "Compliance Officer"),
    ("R13", "Mitigar", "Adaptar las pruebas para que carguen el carrito antes de medir. Actualizar las filas del carrito en el lugar, sin reconstruir la tabla.",
     "Volver a la versión estática desde el historial de Git.", "Desarrollador"),
    ("R14", "Evitar", "Crear todos los nodos con textContent mediante la función el(), sin innerHTML.",
     "Revisar el código ante cualquier dato externo nuevo.", "Desarrollador"),
    ("R15", "Aceptar", "Usar sólo funciones con soporte en Chrome, Edge, Firefox y Safari desde 2021.",
     "Mensaje de error y aviso <noscript> en el catálogo.", "Desarrollador"),
]

SEGUIMIENTO = [
    ("R1", "Sí. Entre el 05/10 y el 21/10 no hubo avances registrados: ningún commit ni movimiento en el tablero. Las tareas 3.1, 3.2, 3.7 y 3.8 se resolvieron el 22/10. La entrega del 23/10 no se cumplió: la carpeta se entrega el 28/10.",
     "Contingencia aplicada el 22/10: se priorizaron las tareas técnicas y legales, que son las que más pesan en la evaluación, y se propuso postergar las imágenes (SC-05).",
     "Activo. Alto. Se mantiene en el Sprint 4 con hitos semanales obligatorios."),
    ("R2", "Sí. El trabajo empezó 17 días después del inicio del sprint (05/10 → 22/10). Desvío: Fetch +13 días; Términos y Condiciones +6 días; campaña de Instagram +4 días; entrega de la carpeta +5 días (23/10 → 28/10).",
     "Fast tracking: carrito y Términos y Condiciones se resolvieron el mismo día, con la tabla de coherencia como vínculo entre ambos. No alcanzó para la campaña de Instagram, y la entrega se corrió al 28/10 para incluir la evidencia de publicación.",
     "Cerrado para el Sprint 3, con atraso. Pasa al Sprint 4 con hitos semanales."),
    ("R3", "Parcialmente. La cuenta no se creó el 23/10, sino el 27/10, y ese día se publicaron las ocho piezas juntas, sin escalonarlas.",
     "Se publicó la campaña completa antes de entregar. El 28/10 se corrigieron el usuario (wood_bird_shop → woodbird.ar) y la historia H1, que no tenía la encuesta. Capturas en la carpeta.",
     "Cerrado. La medición con datos reales pasa al Sprint 4."),
    ("R4", "Sin cambios: al 28/10 el docente no respondió la SC-01.", "Se reitera con la carpeta del Sprint 3 (Registro de solicitudes de cambio).", "Abierto. Project Manager."),
    ("R6", "Sí: no se generaron las imágenes.", "Contingencia vigente: las láminas mantienen el sello «Imagen con IA». La SC-05, aprobada el 22/10, pasa la tarea al Sprint 4.", "Aceptado para el Sprint 3."),
    ("R7", "No. Las pruebas automáticas cumplen en 33 de 33 combinaciones.", "Pendientes: CP-37 (teléfono real) y CP-38 (Firefox).", "Monitoreo. Bajo."),
    ("R8", "No. Detectado el 22/10.", "Pendiente: versionar las herramientas en el Sprint 4.", "Abierto. Bajo."),
    ("R9", "Parcialmente: el token de Trello venció el 22/10.", "Se regeneró ese mismo día y se cargaron las etiquetas de las tarjetas del Sprint 3. El nuevo token vence alrededor del 21/11.", "Monitoreo: renovarlo antes del 21/11."),
    ("R10", "Sí, durante el diseño de la integración. No llegó a producción.", "Mensaje de error, instrucciones en README y CLAUDE.md. El sitio publicado funciona.", "Cerrado."),
    ("R11", "No.", "CP-10 verificado: sin productos.json, el sitio muestra «No pudimos cargar el catálogo…» y no queda en estado de carga.", "Monitoreo."),
    ("R12", "Sí. Al preparar la campaña de Instagram (22/10) se detectó que la portada, el catálogo y los Términos v1.0 presentaban las piezas como talladas y enviadas, en contradicción con la Declaración de triple impacto del Sprint 1.",
     "Se corrigió con la SC-06: Términos v1.1 (cláusulas 2 y 4), portada y descripciones del catálogo. Tabla de coherencia publicada. Los casos de prueba CP-03, CP-14, CP-21, CP-23, CP-31 y CP-34 verifican las cláusulas.", "Monitoreo. Compliance Officer."),
    ("R13", "Sí: las pruebas del Sprint 2 suponían el carrito precargado en el HTML.", "Las pruebas se adaptaron y se sumaron 3 pruebas funcionales. El carrito conserva el foco al cambiar cantidades.", "Cerrado."),
    ("R14", "No.", "Evitado por diseño: el código no usa innerHTML.", "Cerrado."),
    ("R15", "No.", "Respuesta aplicada por diseño.", "Monitoreo. Bajo."),
]


def nivel(p, i):
    n = p * i
    return n, "Alto" if n >= 15 else "Medio" if n >= 8 else "Bajo"


COLOR_NIVEL = {"Alto": "F4C7C3", "Medio": "FCE8B2", "Bajo": "D9EAD3"}


def matriz():
    doc = nuevo("MATRIZ Y REGISTRO DE RIESGOS",
                "Sprint 3 — Tarea 3.4: Reevaluación de la matriz de riesgos tras la integración de JavaScript (corte 28/10)")
    doc.add_heading("1. Objeto y metodología", level=1)
    doc.add_paragraph(
        "Este documento reevalúa la matriz de riesgos del Sprint 2 a la luz de lo ocurrido en el Sprint 3, que incorporó la "
        "carga asincrónica del catálogo, el carrito de compras en JavaScript y los Términos y Condiciones. Se conservan los "
        "riesgos abiertos del Sprint 2 con su nueva evaluación y se agregan los riesgos propios de la integración de "
        "JavaScript (R10 a R15). La versión anterior está en docs/sprint-2/02_Matriz_de_Riesgos.docx.")
    doc.add_paragraph(
        "Se usa la misma escala: probabilidad e impacto de 1 a 5 y nivel = P × I, clasificado como Alto (15 a 25), Medio "
        "(8 a 12) o Bajo (1 a 6). La evaluación es la inherente, antes de aplicar la respuesta. El estado posterior figura "
        "en la sección 5. R5 (consentimiento, Ley 25.326) quedó cerrado en el Sprint 2 y no se vuelve a evaluar.")

    doc.add_heading("2. Registro de riesgos", level=1)
    filas = []
    for id_, riesgo, cat, p, i, disp in RIESGOS:
        n, cl = nivel(p, i)
        filas.append((id_, riesgo, cat, str(p), str(i), f"{n} {cl}", disp))
    t = tabla(doc, ["ID", "Riesgo", "Categoría", "P", "I", "Nivel", "Disparador"], filas, [0.4, 2.4, 0.8, 0.3, 0.3, 0.6, 1.7])
    for fila, (_, _, _, p, i, _) in zip(t.rows[1:], RIESGOS):
        sombrear(fila.cells[5], COLOR_NIVEL[nivel(p, i)[1]])

    doc.add_heading("3. Matriz de probabilidad e impacto", level=1)
    doc.add_paragraph("Ubicación de cada riesgo según su evaluación. Las celdas se colorean por nivel.")
    m = doc.add_table(rows=6, cols=6)
    m.style = "Table Grid"
    sombrear(m.cell(0, 0), "2F4B3C")
    texto_celda(m.cell(0, 0), "P \\ I", negrita=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    for i in range(1, 6):
        sombrear(m.cell(0, i), "2F4B3C")
        texto_celda(m.cell(0, i), f"Impacto {i}", negrita=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    for fila, p in enumerate(range(5, 0, -1), start=1):
        texto_celda(m.cell(fila, 0), f"Probabilidad {p}", negrita=True)
        for i in range(1, 6):
            sombrear(m.cell(fila, i), COLOR_NIVEL[nivel(p, i)[1]])
            texto_celda(m.cell(fila, i), ", ".join(r[0] for r in RIESGOS if r[3] == p and r[4] == i))
    doc.add_paragraph()

    doc.add_heading("4. Plan de respuesta", level=1)
    tabla(doc, ["ID", "Estrategia", "Plan de acción (preventivo)", "Plan de contingencia", "Responsable"],
          RESPUESTA, [0.45, 0.7, 2.25, 2.1, 1.0])

    doc.add_heading("5. Seguimiento al 28/10", level=1)
    doc.add_paragraph("Para cada riesgo: si se materializó, qué respuesta se aplicó y en qué estado queda.")
    tabla(doc, ["ID", "¿Se materializó?", "Respuesta aplicada y evidencia", "Estado al 28/10"],
          SEGUIMIENTO, [0.45, 2.0, 2.55, 1.5])

    doc.add_heading("6. Análisis de la integración de JavaScript", level=1)
    doc.add_paragraph(
        "La integración de JavaScript trajo seis riesgos nuevos. Tres de ellos (R10, R13 y R14) se trataron en el diseño, "
        "antes de que pudieran afectar al sitio publicado:")
    viñeta(doc, "Ejecución local.", "Fetch y los módulos ES no funcionan al abrir index.html como archivo. En lugar de "
                                    "una grilla vacía, el sitio muestra un mensaje de error, y el README explica cómo "
                                    "servirlo por HTTP.")
    viñeta(doc, "Pruebas acopladas al HTML.", "Las pruebas del Sprint 2 medían un carrito escrito a mano. Ahora cargan "
                                              "dos piezas antes de medir y suman pruebas funcionales del carrito, los "
                                              "filtros, el checkout, las reglas legales y la falla de carga del catálogo.")
    viñeta(doc, "Seguridad del DOM.", "Las tarjetas se construyen nodo por nodo con textContent, por lo que un dato del "
                                      "JSON nunca se interpreta como HTML.")
    doc.add_paragraph(
        "La lección principal del sprint no es técnica, sino de gestión: R1 y R2 se volvieron a materializar con más "
        "fuerza que en el Sprint 2. La consecuencia para el Sprint 4, que es la última etapa, es planificar con hitos "
        "semanales verificables en el repositorio y en el tablero, en lugar de un único hito al cierre.")

    firma(doc, "Declaro revisados los riesgos del Sprint 3 al 28/10. R1 y R2 se materializaron: la carpeta se entrega el "
               "28/10, cinco días después de la fecha prevista. Queda activo R1 (Alto) y abiertos R4 y R8, con "
               "responsable asignado.")
    return doc


# ---------------------------------------------------------------------------
# 03 · Plan de casos de prueba
# ---------------------------------------------------------------------------
A, M = "Automática", "Manual"
OK, PEND = "Cumple", "Pendiente (Sprint 4)"
# id, caso, pasos y datos, resultado esperado, regla o cláusula, tipo, resultado al 22/10
CASOS = [
    ("Catálogo", [
        ("CP-01", "Carga asincrónica del catálogo", "Abrir index.html servido por HTTP.",
         "Se generan 12 tarjetas desde productos.json. El estado dice «Mostrando 12 de 12 piezas».", "Tarea 3.1", A, OK),
        ("CP-02", "Diseños nuevos", "Abrir la página de inicio.",
         "Se muestran las 4 piezas con stock de id más alto: Garza blanca, Zorzal, Lechucita vizcachera y Picaflor.", "Tarea 3.1", A, OK),
        ("CP-03", "Pieza sin stock", "Buscar la tarjeta del Tucán (stock: false).",
         "El botón dice «Sin stock», está deshabilitado y la pieza no se puede agregar.", "Cláusula 4", A, OK),
        ("CP-04", "Sello de IA", "Revisar todas las tarjetas.", "Las 12 tarjetas llevan el sello «Imagen con IA».",
         "Cláusula 4; Declaración Ética de IA", A, OK),
        ("CP-05", "Filtro por madera", "Elegir el chip «Palo santo».",
         "4 piezas: Cardenal, Chuña, Calandria y Tucán.", "Regla de negocio", A, OK),
        ("CP-06", "Filtro por precio", "Elegir el chip «Hasta $25.000».", "7 piezas, todas de $25.000 o menos.", "Regla de negocio", A, OK),
        ("CP-07", "Búsqueda sin tildes", "Escribir «chuna» en el buscador.", "Aparece la Chuña.", "Usabilidad", A, OK),
        ("CP-08", "Búsqueda por madera", "Escribir «quebracho».", "4 piezas de quebracho.", "Usabilidad", A, OK),
        ("CP-09", "Búsqueda sin resultados", "Escribir «pingüino».",
         "Ninguna tarjeta y el mensaje «No hay piezas que coincidan con «pingüino».»", "Usabilidad", A, OK),
        ("CP-10", "Falla de carga del catálogo", "Bloquear la petición de productos.json y recargar.",
         "Mensaje «No pudimos cargar el catálogo…» marcado como error. La grilla no queda en estado de carga.", "Riesgo R11", A, OK),
    ]),
    ("Carrito", [
        ("CP-11", "Agregar piezas", "Agregar Cardenal ($28.400) y Carpintero ($34.900).",
         "2 filas, contador 2, subtotal $63.300, envío $5.900 y total $69.200, igual en el carrito y en el checkout.", "Tarea 3.2; cláusulas 5 y 8", A, OK),
        ("CP-12", "Agregar una pieza repetida", "Agregar otra vez el Cardenal.",
         "La fila pasa a cantidad 2 (no se duplica). Contador 3, total $97.600.", "Tarea 3.2", A, OK),
        ("CP-13", "Cambiar la cantidad", "Escribir 3 en la cantidad del Cardenal.",
         "Total $126.000 en el carrito y en el checkout, al instante.", "Tarea 3.2", A, OK),
        ("CP-14", "Cantidad fuera de rango", "Escribir 25 en la cantidad.", "Se corrige a 10, el tope por pieza.", "Cláusula 6", A, OK),
        ("CP-15", "Quitar una pieza", "Presionar «Quitar» en el Carpintero.",
         "Queda 1 fila, total $34.300, y el foco pasa al título del carrito.", "Tarea 3.2; accesibilidad", A, OK),
        ("CP-16", "Carrito vacío", "Quitar todas las piezas.",
         "Se oculta la tabla, se muestra «Tu carrito está vacío», el contador se oculta y el envío pasa a $0.", "Cláusula 8", A, OK),
        ("CP-17", "Aviso para lectores de pantalla", "Agregar el Cardenal.",
         "La región de estado anuncia «Agregaste Cardenal al carrito.»", "Accesibilidad", A, OK),
    ]),
    ("Checkout", [
        ("CP-18", "Formulario vacío", "Presionar «Ir al pago» sin completar nada.",
         "No se confirma. Quedan marcados como inválidos nombre, correo, dirección, localidad, código postal, términos y consentimiento.", "Tarea 3.2", A, OK),
        ("CP-19", "Datos inconsistentes", "Nombre «Ana», correo «ana@correo», teléfono «12-34», CP «35000».",
         "No se confirma y cada campo muestra su propio mensaje (nombre y apellido, dominio del correo, 8 a 15 números, CP de 4 números).", "Tarea 3.2", A, OK),
        ("CP-20", "Código postal inválido", "Corregir todo menos el CP.", "No se confirma.", "Tarea 3.2", A, OK),
        ("CP-21", "Compra válida", "Datos correctos, términos y consentimiento aceptados.",
         "Confirmación con número WB-XXXXXX, piezas, total y recordatorio del arrepentimiento. Formulario y carrito vacíos.", "Cláusulas 6 y 9", A, OK),
        ("CP-22", "Carrito vacío con formulario completo", "Completar todo con el carrito vacío.",
         "No se confirma y aparece el mensaje «Tu carrito está vacío…»", "Cláusula 6", A, OK),
        ("CP-23", "Aceptación de los términos", "Dejar sin marcar la casilla de términos.",
         "No se confirma: la casilla es obligatoria.", "Cláusula 1", A, OK),
        ("CP-24", "Datos sin salir del navegador", "Registrar las peticiones de red durante la compra.",
         "Cero peticiones.", "Ley 25.326; cláusula 13", A, OK),
    ]),
    ("Navegación adaptable", [
        ("CP-25", "Sin desborde horizontal", "3 páginas × 11 anchos, de 320 a 1920 px.", "Ningún desborde en las 33 combinaciones.", "WCAG 1.4.10", A, OK),
        ("CP-26", "Objetivos táctiles", "Medir botones, enlaces y campos.", "Todos miden al menos 44 px de alto.", "WCAG 2.5.5", A, OK),
        ("CP-27", "Contraste", "Medir cada par de texto y fondo.", "Todos cumplen WCAG AA.", "WCAG 1.4.3", A, OK),
        ("CP-28", "Navegación por anclas", "Usar cada enlace de la barra y de los índices.",
         "El título de destino queda visible y no lo tapa la barra fija.", "Usabilidad", A, OK),
        ("CP-29", "Disposición del carrito", "Comparar los anchos.",
         "Renglones apilados por debajo de 600 px, tabla desde 600 px, carrito y checkout lado a lado desde 960 px.", "Diseño responsive", A, OK),
        ("CP-30", "Pie visible", "Bajar hasta el final en móvil.", "La barra inferior fija no tapa el pie.", "Usabilidad", A, OK),
    ]),
    ("Reglas legales", [
        ("CP-31", "Botón de arrepentimiento", "Abrir cada página en cada ancho, sin desplazarse.",
         "El enlace «Botón de arrepentimiento» se ve en la primera pantalla en las 33 combinaciones.", "Res. SCI 424/2020; cláusula 9", A, OK),
        ("CP-32", "Correo de arrepentimiento", "Presionar «Solicitar el arrepentimiento por correo».",
         "Se abre el cliente de correo con destinatario y asunto completos. Se verificó en forma automática que el enlace lleva asunto; falta abrirlo en un cliente real.", "Res. SCI 424/2020", M, PEND),
        ("CP-33", "Enlaces legales del pie", "Revisar el pie de las 3 páginas.",
         "Política de privacidad, Términos y condiciones y «Defensa de las y los Consumidores. Para reclamos ingrese aquí».", "Res. SCI 274/2021", A, OK),
        ("CP-34", "Aviso de arrepentimiento antes de pagar", "Revisar el checkout.",
         "El aviso de 10 días, con enlace a la cláusula 9, aparece antes del botón «Ir al pago».", "Ley 24.240, art. 34; CCyC, art. 1111", A, OK),
    ]),
    ("Pruebas manuales previas al lanzamiento", [
        ("CP-35", "Recorrido con teclado", "Comprar usando sólo Tab, Enter y la barra espaciadora.",
         "Todo es alcanzable, el foco siempre es visible y no hay trampas de foco.", "WCAG 2.1.1 y 2.4.7", M, PEND),
        ("CP-36", "Lector de pantalla", "Recorrer catálogo, carrito y checkout con NVDA.",
         "Se anuncian los cambios del carrito, los errores y la confirmación.", "WCAG 4.1.3", M, PEND),
        ("CP-37", "Teléfono real", "Comprar en el sitio publicado desde un teléfono (Samsung Galaxy A16, Chrome).",
         "Igual comportamiento que en las pruebas automáticas.", "Riesgo R7", M, PEND),
        ("CP-38", "Otros navegadores", "Repetir CP-01, CP-11 y CP-21 en Firefox y Safari.", "Igual comportamiento.", "Riesgos R7 y R15", M, PEND),
    ]),
]


def plan_pruebas():
    doc = nuevo("PLAN DE CASOS DE PRUEBA",
                "Sprint 3 — Tarea 3.4: Plan de pruebas inicial (carrito, navegación adaptable y reglas de negocio)",
                rol="Project Manager / QA")
    todos = [c for _, casos in CASOS for c in casos]
    auto = [c for c in todos if c[5] == A]
    manual = [c for c in todos if c[5] == M]

    doc.add_heading("1. Objeto y alcance", level=1)
    doc.add_paragraph(
        "Este plan define los casos de prueba que verifican, antes del lanzamiento del Sprint 4, el funcionamiento del "
        "carrito de compras, la navegación adaptable y el cumplimiento de las reglas de negocio y de las cláusulas legales. "
        "Cada caso indica la regla o la cláusula que verifica, para mantener la coherencia entre el software y los Términos "
        "y Condiciones que pide el criterio integrador del sprint.")
    doc.add_paragraph(
        "Quedan fuera del alcance el pago real y el envío de datos a un servidor, que no existen en la versión de "
        "demostración, así como la carga de trabajo y el rendimiento.")

    doc.add_heading("2. Estrategia y entorno", level=1)
    viñeta(doc, "Pruebas automáticas.", f"{len(auto)} casos se ejecutan con pruebas/responsive.mjs, que maneja Chrome "
           "sin interfaz por el protocolo DevTools, sin dependencias. Recorre index.html, politica-privacidad.html y "
           "terminos-y-condiciones.html en 11 anchos (de 320 a 1920 px), con movimiento reducido, y guarda capturas y "
           "resultados.json.")
    viñeta(doc, "Pruebas manuales.", f"{len(manual)} casos requieren a una persona, un dispositivo real u otro navegador. "
           "Se ejecutan en el Sprint 4, antes del lanzamiento.")
    viñeta(doc, "Entorno.", "Sitio servido con «python -m http.server 8765». Node 22 y Chrome en Windows 10. Los datos "
           "salen de productos.json: Cardenal $28.400, Carpintero $34.900, Tucán sin stock y envío $5.900.")
    viñeta(doc, "Ejecución.", "Después de cada cambio en el HTML, el CSS o el JavaScript, con el comando "
           "«node pruebas/responsive.mjs http://127.0.0.1:8765/ pruebas/salida».")

    doc.add_heading("3. Casos de prueba", level=1)
    for n, (grupo, casos) in enumerate(CASOS, start=1):
        doc.add_heading(f"3.{n}. {grupo}", level=2)
        t = tabla(doc, ["ID", "Caso", "Pasos y datos", "Resultado esperado", "Regla / cláusula", "Tipo", "Resultado al 22/10"],
                  casos, [0.5, 0.95, 1.25, 1.75, 0.8, 0.6, 0.65])
        for fila, caso in zip(t.rows[1:], casos):
            sombrear(fila.cells[6], "D9EAD3" if caso[6] == OK else "FCE8B2")

    doc.add_heading("4. Resumen de la ejecución al 22/10", level=1)
    cumplen = sum(1 for c in todos if c[6] == OK)
    tabla(doc, ["Tipo", "Casos", "Cumplen", "Fallan", "Pendientes"], [
        ("Automáticas", str(len(auto)), str(sum(1 for c in auto if c[6] == OK)), "0", "0"),
        ("Manuales", str(len(manual)), "0", "0", str(len(manual))),
        ("Total", str(len(todos)), str(cumplen), "0", str(len(todos) - cumplen)),
    ], [1.5, 1.2, 1.2, 1.2, 1.4])
    doc.add_paragraph(
        "Las pruebas automáticas se ejecutaron sobre las 33 combinaciones de página y ancho, y todas cumplen. Al diseñar el "
        "plan se encontraron y corrigieron los siguientes defectos:")
    viñeta(doc, "Mensaje del código postal.", "El navegador mostraba un texto genérico («Utiliza un formato que coincida "
           "con el solicitado»). Se agregó una regla con mensaje propio. Corregido el 22/10.")
    viñeta(doc, "Encabezado a 600 px.", "Al agregar el botón de arrepentimiento, el encabezado quedaba en tres filas "
           "desordenadas. Se reorganizó: marca y botón en la primera fila y buscador debajo; desde 960 px, una sola fila. "
           "Corregido el 22/10.")
    viñeta(doc, "Defectos de la propia prueba.", "Dos verificaciones legales fallaban por errores del script (precedencia "
           "de operadores y un selector que tomaba el enlace equivocado), no del sitio. Se corrigieron y se volvió a ejecutar "
           "todo.")

    doc.add_heading("5. Criterios de aceptación para el lanzamiento", level=1)
    for item in [
        "El 100 % de los casos automáticos cumple en las 33 combinaciones.",
        "Los casos manuales CP-32, CP-35, CP-36, CP-37 y CP-38 están ejecutados y documentados con capturas.",
        "No hay defectos abiertos que impidan comprar ni que contradigan una cláusula de los Términos y Condiciones.",
        "Cada cambio de alcance aprobado en el Sprint 4 suma sus casos de prueba a este plan.",
    ]:
        viñeta(doc, None, item)
    return doc


# ---------------------------------------------------------------------------
# 04 · Registro de solicitudes de cambio
# ---------------------------------------------------------------------------
REGISTRO = [
    ("SC-01", "28/09", "Alinear el Acta con la consigna: compra simulada, sin backend ni pagos reales.",
     "PM (riesgo R4)", "Libera las semanas 7 y 9 del Acta.", "Docente", "Presentada. Sin respuesta al 28/10; se reitera."),
    ("SC-02", "22/10", "Hacer funcionales los filtros por chip y el buscador del catálogo.",
     "Desarrollador", "≈ 1 h, absorbida el 22/10.", "PM", "Aprobada e implementada."),
    ("SC-03", "22/10", "Agregar el botón de arrepentimiento en el encabezado y el enlace a la Ventanilla Única Federal en el pie.",
     "Compliance Officer", "≈ 2 h, absorbidas el 22/10.", "PM (obligación legal)", "Aprobada e implementada."),
    ("SC-04", "22/10", "Ofrecer una garantía propia de 12 meses contra rajaduras, además de la legal de 6 meses.",
     "Responsable de Negocio", "Sin impacto en el desarrollo (sólo texto contractual).", "PM", "Aprobada e incluida en la cláusula 10."),
    ("SC-05", "22/10", "Postergar al Sprint 4 la generación de las 12 imágenes de producto con IA (riesgo R6).",
     "PM (riesgo R1)", "Hacerla en el Sprint 3 costaría ≈ 6 h y pondría en riesgo la entrega del 23/10.", "PM", "Aprobada el 22/10. La tarea pasa al Sprint 4."),
    ("SC-06", "22/10", "Alinear el sitio, el catálogo y los Términos (v1.1) con la Declaración de triple impacto: las piezas son diseños ficticios, sin tala ni envío físico.",
     "Responsable de Negocio (riesgo R12)", "≈ 1 h, absorbida el 22/10.", "PM", "Aprobada e implementada."),
]


def registro_cambios():
    doc = nuevo("REGISTRO DE SOLICITUDES DE CAMBIO DE ALCANCE",
                "Sprint 3 — Tarea 3.3: Control de cambios de alcance y su impacto sobre la fecha de entrega")

    doc.add_heading("1. Procedimiento de control de cambios", level=1)
    doc.add_paragraph(
        "Toda funcionalidad nueva o toda tarea que se quite del plan pasa por este procedimiento antes de implementarse:")
    for negrita, resto in [
        ("Solicitud.", "Cualquier rol (desarrollador, Compliance Officer, responsable de negocio) registra el cambio en "
                       "esta tabla y como tarjeta en el tablero Kanban."),
        ("Evaluación.", "El Project Manager estima el esfuerzo en horas y lo compara con la holgura que queda hasta la "
                        "fecha de entrega. También evalúa el impacto en costo, calidad, riesgos y aspectos legales."),
        ("Decisión.", "Según la sección 7 del Acta, el PM decide sobre los cambios que no alteran el alcance general. Los "
                      "que lo alteran los decide el docente. Una obligación legal no es opcional: se aprueba y se replanifica."),
        ("Cierre.", "El cambio aprobado se implementa con su commit y se agregan sus casos de prueba al plan de pruebas."),
    ]:
        viñeta(doc, negrita, resto)

    doc.add_heading("2. Registro", level=1)
    tabla(doc, ["N.º", "Fecha", "Cambio", "Origen", "Impacto temporal", "Decide", "Estado al 28/10"],
          REGISTRO, [0.45, 0.45, 1.75, 0.85, 1.25, 0.7, 1.05])

    doc.add_heading("3. Impacto sobre la fecha de entrega del 23/10", level=1)
    doc.add_paragraph(
        "Al 22/10, con la entrega al día siguiente, la holgura disponible es de alrededor de un día y medio de trabajo. "
        "Lo que queda pendiente es la campaña de Instagram (3.5), el panel de KPIs (3.6) y la carpeta integradora, unas "
        "8 horas en total. Sobre esa base:")
    tabla(doc, ["Cambio", "Esfuerzo", "Holgura después del cambio", "Conclusión"], [
        ("SC-02 Filtros y buscador", "≈ 1 h", "Positiva", "Se absorbe: completa controles que ya estaban visibles y no funcionaban."),
        ("SC-03 Botón de arrepentimiento", "≈ 2 h", "Positiva", "Se absorbe. Es una obligación legal (Res. SCI 424/2020 y 274/2021)."),
        ("SC-04 Garantía propia", "0 h de desarrollo", "Sin cambios", "Se absorbe. Es una decisión de negocio que diferencia a la marca."),
        ("SC-05 Imágenes con IA", "≈ 6 h si se hicieran ahora", "Negativa: no alcanza para 3.5, 3.6 y la carpeta",
         "Se posterga al Sprint 4. Mientras tanto se mantienen las láminas con el sello."),
    ], [1.6, 1.0, 1.6, 2.3])
    doc.add_paragraph(
        "Resultado al 28/10: los cambios absorbidos no movieron la fecha, pero la campaña de Instagram (3.5) sí. La cuenta "
        "y sus publicaciones recién se hicieron el 27/10, y la carpeta se entrega el 28/10, con cinco días de atraso. El "
        "atraso no se origina en un cambio de alcance, sino en los riesgos R1 a R3 (ver la matriz de riesgos).")

    doc.add_heading("4. Detalle de las solicitudes del Sprint 3", level=1)
    detalles = [
        ("SC-02 · Filtros y buscador funcionales",
         "El HTML del Sprint 2 tenía chips de filtro y un buscador que no hacían nada: un defecto de usabilidad visible. Al "
         "generar las tarjetas con JavaScript, filtrarlas costaba poco. Impacto: alcance +1 funcionalidad, calidad mejor, sin "
         "efecto legal. Verificación: CP-05 a CP-09."),
        ("SC-03 · Botón de arrepentimiento y enlace a la Ventanilla Única",
         "Al redactar la cláusula de arrepentimiento (Tarea 3.8) surgió que la Res. SCI 424/2020 exige un botón visible desde "
         "la página de inicio, y la Res. SCI 274/2021, un enlace a la Ventanilla Única Federal. La consigna no los pedía, pero "
         "la coherencia entre contrato y software sí. Impacto: cambia el encabezado de las tres páginas y suma una prueba "
         "automática. Verificación: CP-31 a CP-34."),
        ("SC-04 · Garantía propia de 12 meses",
         "El riesgo principal de una talla en madera nativa es que se raje al cambiar el clima. Extender la garantía contra "
         "rajaduras refuerza la propuesta de valor sin costo de desarrollo. Impacto: costo teórico de reposición, a "
         "considerar en el modelo de negocio del Sprint 4."),
        ("SC-05 · Imágenes con IA al Sprint 4",
         "Generar 12 imágenes coherentes, registrar la herramienta y el prompt de cada una (Declaración Ética de IA) y "
         "reemplazar las láminas por etiquetas <img> con texto alternativo lleva unas 6 horas. Hacerlo el 22/10 dejaría sin "
         "tiempo a las tareas 3.5 y 3.6, que se evalúan en este sprint. Impacto: el riesgo R6 se acepta un sprint más."),
    ]
    for titulo, texto in detalles:
        doc.add_heading(titulo, level=2)
        doc.add_paragraph(texto)

    doc.add_heading("5. Seguimiento en el tablero Kanban", level=1)
    doc.add_paragraph(
        "El 22/10 se cargaron en el tablero las tarjetas del Sprint 3, con responsable y la fecha planificada según el "
        "cronograma de la consigna. Las cuatro tareas terminadas (3.1, 3.2, 3.7 y 3.8) registran en su descripción el "
        "desvío respecto de esa fecha. Tablero: https://trello.com/b/iGCwIo1k/woodbird.")

    firma(doc, "Registro actualizado al 28/10. La SC-01 se reitera ante el docente junto con la carpeta del Sprint 3.")
    return doc


if __name__ == "__main__":
    DESTINO.mkdir(parents=True, exist_ok=True)
    matriz().save(DESTINO / "02_Matriz_de_Riesgos.docx")
    plan_pruebas().save(DESTINO / "03_Plan_de_Casos_de_Prueba.docx")
    registro_cambios().save(DESTINO / "04_Registro_de_Solicitudes_de_Cambio.docx")
    print("Generados 02_Matriz_de_Riesgos, 03_Plan_de_Casos_de_Prueba y 04_Registro_de_Solicitudes_de_Cambio")
