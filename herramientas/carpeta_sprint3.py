# Arma la carpeta integradora del Sprint 3 en PDF:
#   sitio/docs/sprint-3/00_Carpeta_Integradora_Sprint_3.pdf
# Junta los documentos 01 a 06 (exportados con Word), páginas propias en HTML (Kanban, desarrollo web,
# código, repositorio, publicación legal) y capturas del sitio. Las capturas de Instagram y del tablero
# se agregan solas si existen en docs/sprint-3/capturas/ (instagram-*.png y tablero.png).
# Uso: python herramientas/carpeta_sprint3.py   (requiere Word, Node 22, Chrome y el sitio servido en :8765)

import html
import json
import subprocess
import urllib.request
from datetime import date
from pathlib import Path

import pymupdf

AQUI = Path(__file__).resolve().parent
SITIO = AQUI.parent / "sitio"
DOCS = SITIO / "docs" / "sprint-3"
TMP = AQUI / "carpeta_tmp"
CAPTURAS = TMP / "capturas"
EXTRA = DOCS / "capturas"          # capturas que aporta el integrante (Instagram, tablero)
SALIDA = DOCS / "00_Carpeta_Integradora_Sprint_3.pdf"
PIE = "Woodbird · Carpeta integradora del Sprint 3"
HOY = date.today().strftime("%d/%m/%Y")

DOCUMENTOS = {
    "01": "01_Terminos_y_Condiciones", "02": "02_Matriz_de_Riesgos", "03": "03_Plan_de_Casos_de_Prueba",
    "04": "04_Registro_de_Solicitudes_de_Cambio", "05": "05_Campana_de_Instagram", "06": "06_Panel_de_KPIs",
}

# ---------------------------------------------------------------------------
# Estilo común de las páginas propias (mismo lenguaje visual que la carpeta del Sprint 2)
# ---------------------------------------------------------------------------
ESTILO = """
@page { size: A4; margin: 18mm 18mm 20mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Archivo", sans-serif; font-size: 10pt; line-height: 1.5; color: #191E14; }
h1, h2, h3 { font-family: "Fraunces", serif; font-weight: 700; line-height: 1.15; margin: 0 0 8pt; }
h1 { font-size: 22pt; } h2 { font-size: 13pt; margin-top: 16pt; } h3 { font-size: 11pt; margin-top: 12pt; }
p { margin: 0 0 8pt; }
.kicker { font-size: 8pt; letter-spacing: 0.14em; text-transform: uppercase; color: #6B6959; font-weight: 600; margin-bottom: 4pt; }
.salto { break-before: page; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 12pt; font-size: 8.5pt; }
th { background: #2F4B3C; color: #fff; text-align: left; padding: 5pt 6pt; font-weight: 600; }
td { padding: 4pt 6pt; border-bottom: 1px solid #D8CEB0; vertical-align: top; }
tr { break-inside: avoid; }
a { color: #47542F; }
figure { margin: 8pt 0 12pt; break-inside: avoid; }
figure img { width: 100%; border: 1px solid #D8CEB0; border-radius: 4pt; display: block; }
figcaption { font-size: 8pt; color: #6B6959; margin-top: 3pt; }
.dos { display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; }
.tres { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8pt; }
.capturas figure img { height: 76mm; width: auto; max-width: 100%; margin: 0 auto; }
.nota { padding: 7pt 10pt; border-left: 3px solid #985E26; background: #F4EEDC; font-size: 9pt; margin: 8pt 0 12pt; }
.ok { color: #1F6B1F; font-weight: 600; } .pend { color: #985E26; font-weight: 600; }
pre { margin: 0; font-family: Consolas, "Courier New", monospace; font-size: 7.4pt; line-height: 1.38; white-space: pre-wrap; }
.codigo { counter-reset: linea; border: 1px solid #D8CEB0; border-radius: 4pt; padding: 6pt 8pt; margin-bottom: 12pt; background: #FCFAF3; }
.codigo span { display: block; counter-increment: linea; padding-left: 30pt; text-indent: -30pt; break-inside: avoid; }
.codigo span::before { content: counter(linea); display: inline-block; width: 24pt; margin-right: 6pt; text-align: right; color: #A9A38C; text-indent: 0; }
.tablero { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6pt; margin: 8pt 0; }
.lista { background: #EFE9D6; border-radius: 4pt; padding: 6pt; }
.lista h4 { margin: 0 0 5pt; font-size: 8.5pt; }
.card { background: #fff; border-radius: 3pt; padding: 4pt 5pt; margin-bottom: 4pt; font-size: 7.2pt; line-height: 1.3; box-shadow: 0 1px 0 #D8CEB0; }
.card small { display: block; color: #6B6959; font-size: 6.6pt; margin-top: 2pt; }
.etq { display: inline-block; height: 4pt; width: 18pt; border-radius: 2pt; margin-right: 2pt; }
"""
FUENTES = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600'
           '&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap">')


def pagina(cuerpo, estilo_extra=""):
    return (f'<!DOCTYPE html><html lang="es-AR"><head><meta charset="UTF-8">{FUENTES}'
            f"<style>{ESTILO}{estilo_extra}</style></head><body>{cuerpo}</body></html>")


def e(texto):
    return html.escape(str(texto), quote=False)


def img(nombre, pie, carpeta=CAPTURAS):
    return f'<figure><img src="{(carpeta / nombre).as_uri()}"><figcaption>{e(pie)}</figcaption></figure>'


def tabla(encabezados, filas, anchos=None):
    cols = "".join(f'<col style="width:{a}%">' for a in anchos) if anchos else ""
    cab = "".join(f"<th>{e(h)}</th>" for h in encabezados)
    cuerpo = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in f) + "</tr>" for f in filas)
    return f"<table><colgroup>{cols}</colgroup><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table>"


# ---------------------------------------------------------------------------
# Datos: tablero (lectura pública, sin credenciales) y repositorio
# ---------------------------------------------------------------------------
def tablero():
    with urllib.request.urlopen("https://trello.com/b/iGCwIo1k.json") as r:
        return json.load(r)


def git(*args):
    return subprocess.run(["git", *args], cwd=SITIO, capture_output=True, text=True, encoding="utf-8", check=True).stdout


TAREAS_S3 = {  # tarjeta → materia (la etiqueta que le corresponde en el tablero)
    "Consumo asincrónico de productos.json (Fetch API)": "Web",
    "Carrito de compras y validación del checkout": "Web",
    "Imágenes de producto generadas con IA (Sprint 3)": "Web",
    "Registro de solicitudes de cambio de alcance": "Gestión",
    "Reevaluación de la matriz de riesgos (Sprint 3)": "Gestión",
    "Plan de casos de prueba (Test Cases)": "Gestión",
    "Riesgo R1: sobrecarga del único integrante": "Gestión",
    "Riesgo R4: aprobación de la solicitud de cambio SC-01": "Gestión",
    "Publicaciones de la campaña de Instagram": "Emprendedor",
    "Panel de métricas de conversión (KPIs)": "Emprendedor",
    "Términos y Condiciones de uso y compra": "Legislación",
    "Derecho de arrepentimiento y garantía (Ley 24.240)": "Legislación",
    "Entrega de la carpeta del Sprint 3": "Gestión",
}
ROL = {"Gestión": "Project Manager", "Web": "Desarrollador", "Legislación": "Compliance Officer",
       "Emprendedor": "Responsable de Negocio"}
COLOR_ETQ = {"green": "#61BD4F", "orange": "#FF9F1A", "purple": "#C377E0", "yellow": "#F2D600", "red": "#EB5A46", "blue": "#0079BF"}


# ---------------------------------------------------------------------------
# Secciones propias
# ---------------------------------------------------------------------------
def seccion_kanban(d):
    listas = {l["id"]: l["name"] for l in d["lists"] if not l["closed"]}
    miembros = {m["id"]: m["fullName"] for m in d["members"]}
    tarjetas = [c for c in d["cards"] if not c["closed"] and c["name"] in TAREAS_S3]
    orden = {"Por hacer": 0, "En progreso": 1, "Prueba": 2, "Hecho": 3}
    tarjetas.sort(key=lambda c: (orden.get(listas[c["idList"]], 9), c["due"] or ""))
    filas, sin_etiqueta = [], []
    for c in tarjetas:
        materia = TAREAS_S3[c["name"]]
        etiquetas = [l["name"] for l in c["labels"]]
        if materia not in etiquetas:
            sin_etiqueta.append(c["name"])
        vence = date.fromisoformat(c["due"][:10]).strftime("%d/%m/%Y") if c["due"] else "—"
        filas.append((e(c["name"]), materia, ROL[materia], e(", ".join(miembros.get(m, "") for m in c["idMembers"]) or "—"),
                      vence, listas[c["idList"]]))
    nota = ""
    if sin_etiqueta:
        nota = (f'<p class="nota">Etiquetas: {len(sin_etiqueta)} tarjetas del Sprint 3 todavía no tienen la etiqueta de su '
                "materia en Trello. La materia de cada una figura en la tabla.</p>")

    if (EXTRA / "tablero.png").exists():
        vista = img("tablero.png", "Vista del tablero en Trello.", EXTRA)
    else:
        columnas = []
        for nombre in ["Por hacer", "En progreso", "Prueba", "Hecho"]:
            cs = [c for c in tarjetas if listas[c["idList"]] == nombre]
            otras = sum(1 for c in d["cards"] if not c["closed"] and listas.get(c["idList"]) == nombre and c["name"] not in TAREAS_S3)
            html_cs = "".join(
                '<div class="card">' + "".join(f'<span class="etq" style="background:{COLOR_ETQ.get(l["color"], "#ccc")}"></span>' for l in c["labels"])
                + f'<div>{e(c["name"])}</div><small>{date.fromisoformat(c["due"][:10]).strftime("%d/%m") if c["due"] else ""}'
                f'{" ✓" if c["dueComplete"] else ""}</small></div>' for c in cs)
            extra = f'<small style="font-size:7pt;color:#6B6959">y {otras} tarjetas de sprints anteriores</small>' if otras else ""
            columnas.append(f'<div class="lista"><h4>{nombre}</h4>{html_cs}{extra}</div>')
        vista = (f'<div class="tablero">{"".join(columnas)}</div><p style="font-size:8pt;color:#6B6959">Vista reconstruida '
                 f"a partir de los datos públicos del tablero al {HOY}. Trello no muestra el tablero sin iniciar sesión en "
                 "un navegador automatizado.</p>")

    return f"""
<p class="kicker">Dirección y Gestión de Proyectos · Tarea 3.3</p>
<h1>Tablero Kanban y asignación de roles</h1>
<p>Tablero público en Trello: <a href="https://trello.com/b/iGCwIo1k/woodbird">https://trello.com/b/iGCwIo1k/woodbird</a>.
Columnas de control: <strong>Por hacer</strong>, <strong>En progreso</strong>, <strong>Prueba</strong> y <strong>Hecho</strong>.
Las tarjetas del Sprint 3 se cargaron el 22/10 con su responsable y con la fecha límite del cronograma de la consigna. Las
terminadas registran en la descripción el desvío respecto de esa fecha, y los cambios de alcance pasan por el registro de
solicitudes (documento 04).</p>
<h2>Tareas del Sprint 3 y rol que las cumple</h2>
{tabla(["Tarea", "Materia", "Rol", "Responsable", "Fecha límite", "Columna"], filas, [34, 12, 17, 14, 12, 11])}
{nota}
<h2 class="salto">Vista del tablero</h2>
{vista}"""


def seccion_fetch():
    filas = [
        ("<code>app.js</code>", "Punto de entrada (módulo ES). Espera la carga del catálogo y conecta el carrito y el checkout."),
        ("<code>catalogo.js · cargarProductos()</code>", "<code>fetch(\"productos.json\")</code> con <code>async/await</code>; si la respuesta no es 200, lanza un error."),
        ("<code>catalogo.js · tarjeta()</code>", "Genera cada tarjeta en el DOM: lámina con el sello «Imagen con IA», nombre, madera, medida, precio y botón «Agregar» (o «Sin stock»)."),
        ("<code>utilidades.js · el()</code>", "Crea los nodos con <code>textContent</code>, nunca con <code>innerHTML</code>: un dato del JSON no puede inyectar HTML (riesgo R14)."),
        ("<code>catalogo.js · filtrar()</code>", "Filtros por chip y buscador sin tildes sobre los datos en memoria, sin volver a pedir el archivo."),
        ("<code>catalogo.js · mostrarErrorCatalogo()</code>", "Si la carga falla, muestra un mensaje en lugar de una grilla vacía (riesgo R11)."),
    ]
    return f"""
<p class="kicker">Desarrollo de Sitios Web · Tarea 3.1</p>
<h1>Consumo asincrónico y renderizado dinámico del DOM</h1>
<p>El catálogo dejó de estar escrito a mano en <code>index.html</code>. Al cargar la página, el módulo <code>js/app.js</code>
pide <code>productos.json</code> con la Fetch API y <code>async/await</code>, y <code>js/catalogo.js</code> genera en el DOM las
12 tarjetas del catálogo y las 4 de «Diseños nuevos». Cambiar un precio o agregar un producto es editar el JSON: el HTML no se toca.</p>
{tabla(["Pieza del código", "Qué hace"], filas, [32, 68])}
<div class="dos">
{img("02_catalogo_filtro.png", "Figura 6. Catálogo generado desde productos.json, con el filtro «Palo santo» activo (4 piezas; el Tucán, sin stock).")}
{img("03_busqueda.png", "Figura 7. El buscador encuentra «Chuña» aunque se escriba «chuna».")}
</div>
<div class="dos">
{img("01_portada_escritorio.png", "Figura 8. Portada: «Diseños nuevos» también sale del JSON; el contador del carrito muestra 3 piezas.")}
{img("11_error_de_carga.png", "Figura 9. Si productos.json no responde, el sitio lo avisa (caso de prueba CP-10).")}
</div>"""


def seccion_carrito():
    funciones = [
        ("Agregar", "Botón «Agregar» de cada tarjeta. Una pieza repetida suma cantidad en la misma fila.", "CP-11, CP-12"),
        ("Cambiar cantidad", "Campo numérico de 1 a 10; un valor fuera de rango se corrige al salir del campo.", "CP-13, CP-14"),
        ("Quitar", "Botón «Quitar» por fila; el foco vuelve al título del carrito.", "CP-15"),
        ("Contador flotante", "Insignia en el enlace «Carrito» de la barra: fija abajo en el celular y pegada arriba en escritorio.", "CP-11"),
        ("Total en tiempo real", "Subtotal, envío ($5.900 si hay piezas) y total, iguales en el carrito y en el checkout.", "CP-11, CP-13, CP-16"),
        ("Accesibilidad", "Cada cambio se anuncia a los lectores de pantalla («Agregaste Cardenal al carrito.»).", "CP-17"),
    ]
    reglas = [
        ("Carrito vacío", "No se confirma: «Tu carrito está vacío…».", "CP-22"),
        ("Nombre y apellido", "Al menos dos palabras, sólo letras.", "CP-19"),
        ("Correo", "Con dominio completo (nombre@correo.com).", "CP-19"),
        ("Teléfono (opcional)", "Si se completa, entre 8 y 15 números.", "CP-19"),
        ("Código postal", "4 números.", "CP-20"),
        ("Términos y privacidad", "Las dos casillas son obligatorias (cláusula 1 y Ley 25.326).", "CP-18, CP-23"),
        ("Confirmación", "Número WB-XXXXXX, piezas, total y recordatorio del arrepentimiento; se borran el formulario y el carrito.", "CP-21"),
        ("Sin red", "Durante la compra no hay ninguna petición de red.", "CP-24"),
    ]
    return f"""
<p class="kicker">Desarrollo de Sitios Web · Tarea 3.2</p>
<h1>Carrito de compras e interceptación del checkout</h1>
<p><code>js/carrito.js</code> guarda el carrito en memoria (un <code>Map</code> de producto a cantidad) y recalcula los totales
desde el catálogo, nunca desde lo que muestra la página. <code>js/checkout.js</code> intercepta el clic en «Ir al pago»: el
formulario no tiene <code>action</code> ni botón de envío, así que los datos no salen del navegador.</p>
{tabla(["Función", "Comportamiento", "Prueba"], funciones, [18, 64, 18])}
<h2>Validación del checkout</h2>
<p>Antes de simular la orden se verifica la consistencia de los datos con <code>setCustomValidity()</code>, con un mensaje
propio por campo, y <code>reportValidity()</code>:</p>
{tabla(["Regla", "Qué se verifica", "Prueba"], reglas, [22, 60, 18])}
<h2 class="salto">Demostración funcional</h2>
<div class="dos">
{img("04_carrito_movil.png", "Figura 10. Carrito en el celular (390 px): Cardenal ×2 y Carpintero, total $97.600 y contador «3» en la barra.")}
<div>
{img("05_checkout_completo.png", "Figura 11. Carrito y checkout lado a lado en escritorio, con los datos completos.")}
{img("06_confirmacion.png", "Figura 12. Confirmación del pedido simulado; el formulario y el carrito quedan vacíos.")}
{img("07_carrito_vacio_bloquea.png", "Figura 13. Con el carrito vacío, la compra se bloquea aunque los datos estén completos.")}
</div>
</div>"""


def seccion_codigo():
    archivos = ["js/app.js", "js/utilidades.js", "js/catalogo.js", "js/carrito.js", "js/checkout.js"]
    bloques = []
    for a in archivos:
        lineas = (SITIO / a).read_text(encoding="utf-8").rstrip("\n").split("\n")
        cuerpo = "".join(f"<span>{e(l) or ' '}</span>" for l in lineas)
        bloques.append(f'<h3>{a} <small style="font-family:Archivo;font-weight:400;color:#6B6959">· {len(lineas)} líneas</small></h3>'
                       f'<div class="codigo"><pre>{cuerpo}</pre></div>')
    return f"""
<p class="kicker">Desarrollo de Sitios Web · Tareas 3.1 y 3.2</p>
<h1>Código JavaScript del Sprint 3</h1>
<p>Cinco módulos ES, sin frameworks ni dependencias, bajo licencia GPL v3 o posterior. Se cargan con
<code>&lt;script type="module" src="js/app.js"&gt;</code>, por lo que el sitio debe servirse por HTTP (GitHub Pages o
<code>python -m http.server</code>).</p>
{"".join(bloques)}"""


def seccion_repositorio():
    log = git("log", "--since=2026-10-05", "--date=format:%d/%m/%Y", "--format=%h\t%ad\t%s").strip().split("\n")
    commits = [tuple(e(x) for x in l.split("\t")) for l in log if l]
    archivos = [
        ("index.html", "Página única: portada, catálogo y carrito vacíos que llena JS, checkout y botón de arrepentimiento.", "GPL v3+"),
        ("terminos-y-condiciones.html", "Términos y Condiciones v1.1 (Ley 24.240), generados con el documento 01.", "GPL v3+"),
        ("politica-privacidad.html", "Política de privacidad (Ley 25.326).", "GPL v3+"),
        ("js/ (5 módulos)", "app, utilidades, catalogo, carrito y checkout.", "GPL v3+"),
        ("css/estilos.css", "Hoja única mobile-first; suma contador, carrito, botón de arrepentimiento y errores.", "GPL v3+"),
        ("productos.json", "Catálogo de 12 diseños: única fuente de los productos.", "GPL v3+"),
        ("pruebas/", "Pruebas automáticas: 3 páginas × 11 anchos, carrito, checkout, reglas legales y falla de carga.", "GPL v3+"),
        ("docs/sprint-3/", "Entregables escritos del Sprint 3 y piezas de Instagram.", "CC BY-NC-SA 4.0"),
    ]
    return f"""
<p class="kicker">Desarrollo de Sitios Web</p>
<h1>Repositorio y código consolidado</h1>
<p>Repositorio: <a href="https://github.com/nicorsss/Woodbird">https://github.com/nicorsss/Woodbird</a> · rama
<code>main</code>. Sitio publicado: <a href="https://nicorsss.github.io/Woodbird/">https://nicorsss.github.io/Woodbird/</a>.
Cada entregable se sube al terminarse: la fecha del commit es el registro objetivo de avance.</p>
<h2>Archivos del sitio al cierre del Sprint 3</h2>
{tabla(["Archivo", "Contenido", "Licencia"], archivos, [24, 60, 16])}
<h2>Commits del Sprint 3</h2>
{tabla(["Commit", "Fecha", "Descripción"], commits, [11, 13, 76])}
<h2>Pruebas</h2>
<p><code>node pruebas/responsive.mjs http://127.0.0.1:8765/ pruebas/salida</code> recorre las 3 páginas en 11 anchos (33
combinaciones) y ejecuta los 33 casos automáticos del plan de pruebas (documento 03). Resultado al {HOY}:
<span class="ok">33 de 33 combinaciones cumplen</span>; los 5 casos manuales quedan para el Sprint 4.</p>"""


PIES_INSTAGRAM = {  # captura → pie de figura (las que no figuran usan el nombre del archivo)
    "instagram-0_perfil": "Figura 1. Perfil de @woodbird.ar: bio con el enlace UTM al sitio, historia destacada «Sobre la IA» y grilla con P1 a P5.",
    "instagram-P1_publicacion": "Figura 2. P1 · Abrimos la tienda, con la etiqueta «Contenido de IA» y la CTA «Ver catálogo · link en bio».",
    "instagram-P2_publicacion": "Figura 3. P2 · Carrusel «Por qué no talamos ni un palo santo» (lámina 1 de 5).",
    "instagram-H1_historia": "Figura 4. H1 · ¿Cuál es tu madera?, con el sticker de encuesta y el enlace «Ver las aves».",
    "instagram-H3_historia": "Figura 5. H3 · ¿Tus aves existen?, con el enlace «Cómo trabajamos»; queda fija en «Sobre la IA».",
}


def seccion_evidencia_instagram():
    orden = list(PIES_INSTAGRAM)
    capturas = sorted(EXTRA.glob("instagram-*.png") if EXTRA.exists() else [],
                      key=lambda c: (orden.index(c.stem) if c.stem in orden else len(orden), c.name))
    if capturas:
        figuras = "".join(img(c.name, PIES_INSTAGRAM.get(c.stem, c.stem.replace("instagram-", "").replace("_", " ")), EXTRA)
                          for c in capturas)
        cuerpo = f'<div class="tres capturas">{figuras}</div>'
    else:
        cuerpo = ('<p class="nota"><span class="pend">Pendiente.</span> La cuenta @woodbird.ar se crea y las primeras '
                  "publicaciones (P1, P2, H1 y H3) se hacen el 23/10, antes de la entrega. Las capturas se agregan a esta "
                  "página en cuanto estén publicadas.</p>")
    return f"""
<p class="kicker">El Emprendedor Digital y el Contexto · Tarea 3.5</p>
<h1>Evidencia de publicación en Instagram</h1>
<p>Capturas de la cuenta @woodbird.ar con las piezas de la campaña «Sin talar un árbol» publicadas. Cada una lleva su
llamada a la acción con un enlace etiquetado con UTM hacia el sitio publicado (ver el documento 05).</p>
<p class="nota">La cuenta se creó el 27/10, cuatro días después de lo planificado (riesgo R3), y ese día se publicaron las
ocho piezas del calendario. El 28/10 el usuario pasó de wood_bird_shop a woodbird.ar, y se volvieron a subir H1, que no
tenía el sticker de encuesta, y H3. Las capturas se tomaron el 28/10, desde el celular.</p>
{cuerpo}"""


def seccion_legal():
    requisitos = [
        ("Términos y Condiciones en el footer", "Pie de las tres páginas", "Consigna, semana 9"),
        ("Aceptación de los términos", "Casilla obligatoria en el checkout", "CCyC, arts. 984 a 989"),
        ("Botón de arrepentimiento", "Encabezado de las tres páginas, visible sin desplazarse", "Res. SCI 424/2020"),
        ("Derecho de revocación informado antes de comprar", "Aviso junto a «Ir al pago» y en la confirmación", "Ley 24.240, art. 34; CCyC, art. 1111"),
        ("Enlace a la Ventanilla Única Federal", "Pie: «Defensa de las y los Consumidores. Para reclamos ingrese aquí»", "Res. SCI 274/2021"),
        ("Política de privacidad y consentimiento", "Pie y casilla obligatoria en el checkout", "Ley 25.326"),
    ]
    return f"""
<p class="kicker">Legislación Informática · Tareas 3.7 y 3.8</p>
<h1>Publicación legal en el sitio</h1>
<p>Los Términos y Condiciones (versión 1.1, vigente desde el 22/10/2026) están publicados en
<code>terminos-y-condiciones.html</code> con el mismo texto que el documento 01, porque los dos se generan desde una única
fuente. La tabla resume dónde se cumple cada exigencia en el sitio; las pruebas automáticas CP-31 a CP-34 lo verifican en
las 33 combinaciones.</p>
{tabla(["Exigencia", "Dónde está en el sitio", "Norma"], requisitos, [34, 40, 26])}
<div class="dos">
{img("09_terminos.png", "Figura 14. Página de los términos con el índice de sus 16 cláusulas y el botón de arrepentimiento arriba a la derecha.")}
{img("10_clausula_arrepentimiento.png", "Figura 15. Cláusula 9: plazo de 10 días, sin costo, y botón que abre el correo con el asunto completo.")}
</div>
{img("08_pie_legal_recorte.png", "Figura 16. Pie del sitio con los enlaces a la Declaración ética de IA, la Política de privacidad, los Términos y la Ventanilla Única Federal.")}"""


# ---------------------------------------------------------------------------
# Portada e índice
# ---------------------------------------------------------------------------
def portada():
    filas = [("Integrante", "<strong>Reiss Jorge Nicolás</strong>"),
             ("Roles", "Project Manager, Desarrollador, Compliance Officer y Responsable de Negocio"),
             ("Docente", "Prof. Erick Gaston Ibañez"),
             ("Repositorio", '<a href="https://github.com/nicorsss/Woodbird">github.com/nicorsss/Woodbird</a>'),
             ("Sitio publicado", '<a href="https://nicorsss.github.io/Woodbird/">nicorsss.github.io/Woodbird</a>'),
             ("Tablero Kanban", '<a href="https://trello.com/b/iGCwIo1k/woodbird">trello.com/b/iGCwIo1k/woodbird</a>')]
    datos = "".join(f'<tr><td style="color:#6B6959;width:28%">{k}</td><td>{v}</td></tr>' for k, v in filas)
    return f"""
<div style="height:250mm;display:flex;flex-direction:column">
<p class="kicker" style="color:#47542F">Proyecto integrado interdisciplinar 2026 · EcoStart IA</p>
<div style="margin-top:42mm">
<h1 style="font-size:46pt;margin:0">Woodbird</h1>
<p style="color:#6B6959;font-size:11pt">Aves decorativas inspiradas en el tallado en maderas nativas del Chaco</p>
<div style="width:22mm;height:2.5pt;background:#985E26;margin:10mm 0"></div>
<h1 style="font-size:24pt;margin:0 0 4pt">Carpeta integradora del Sprint 3</h1>
<p style="font-size:12pt;margin:0">Interactividad web, asincronismo y contratos</p>
<p style="color:#6B6959">Período: 05/10 al 23/10/2026 · Semanas 7 a 9 · Entregada el 28/10/2026</p>
</div>
<table style="margin-top:auto;font-size:9.5pt"><tbody>{datos}</tbody></table>
<p style="font-size:8.5pt;color:#6B6959">Tecnicatura Superior en Desarrollo de Software · IES «René Favaloro» · 3er año, 2026</p>
</div>"""


def indice(entradas):
    filas = []
    for materia, items in entradas:
        filas.append(f'<tr><td colspan="2" style="padding-top:10pt;font-weight:700;font-size:8.5pt;letter-spacing:0.08em;'
                     f'border-bottom:2px solid #47542F">{e(materia.upper())}</td></tr>')
        filas += [f'<tr><td>{e(t)}</td><td style="text-align:right;width:14%">{p}</td></tr>' for t, p in items]
    pendientes = []
    if not (EXTRA.exists() and list(EXTRA.glob("instagram-*.png"))):
        pendientes.append("las capturas de las publicaciones de Instagram")
    nota_pend = (f'<p class="nota"><strong>Pendiente al {HOY}:</strong> {" y ".join(pendientes)}. La carpeta se regenera al '
                 "incorporarlas.</p>") if pendientes else ""
    return f"""
<h1>Índice</h1>
<table style="font-size:10pt"><thead><tr><th>Entregable</th><th style="text-align:right">Página</th></tr></thead>
<tbody>{"".join(filas)}</tbody></table>
<p style="font-size:9pt"><strong>Asignación de roles.</strong> El equipo tiene un solo integrante, Reiss Jorge Nicolás, que
cumple los cuatro roles: Project Manager (Dirección y Gestión de Proyectos), Desarrollador (Desarrollo de Sitios Web),
Compliance Officer (Legislación Informática) y Responsable de Negocio (El Emprendedor Digital). La asignación de cada tarea
está en la página del tablero Kanban.</p>
{nota_pend}"""


# ---------------------------------------------------------------------------
# Armado
# ---------------------------------------------------------------------------
def exportar_word():
    ps = TMP / "exportar.ps1"
    lineas = ["$w = New-Object -ComObject Word.Application", "$w.Visible = $false"]
    for n in DOCUMENTOS.values():
        lineas += [f'$d = $w.Documents.Open("{DOCS / (n + ".docx")}", $false, $true)',
                   f'$d.ExportAsFixedFormat("{TMP / (n + ".pdf")}", 17)', "$d.Close($false)"]
    lineas.append("$w.Quit()")
    ps.write_text("\n".join(lineas), encoding="utf-8-sig")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)], check=True)


def a_pdf(paginas):
    lista = []
    for nombre, cuerpo in paginas.items():
        h = TMP / f"{nombre}.html"
        h.write_text(pagina(cuerpo), encoding="utf-8")
        lista.append({"html": str(h), "pdf": str(TMP / f"{nombre}.pdf")})
    (TMP / "lista_pdf.json").write_text(json.dumps(lista), encoding="utf-8")
    subprocess.run(["node", str(AQUI / "pdf.mjs"), str(TMP / "lista_pdf.json")], check=True)


def recortar_pie():
    # Sólo la franja del pie de la captura 08, para que entre en la página de publicación legal
    from PIL import Image
    im = Image.open(CAPTURAS / "08_pie_legal.png")
    im.crop((0, im.height - 250, im.width, im.height)).save(CAPTURAS / "08_pie_legal_recorte.png")


def main():
    TMP.mkdir(exist_ok=True)
    recortar_pie()
    exportar_word()
    a_pdf({
        "s_kanban": seccion_kanban(tablero()), "s_fetch": seccion_fetch(), "s_carrito": seccion_carrito(),
        "s_codigo": seccion_codigo(), "s_repo": seccion_repositorio(), "s_instagram": seccion_evidencia_instagram(),
        "s_legal": seccion_legal(),
    })

    # (materia, título, archivo pdf)
    orden = [
        ("Dirección y Gestión de Proyectos", "Tablero Kanban y asignación de roles", "s_kanban"),
        ("Dirección y Gestión de Proyectos", "Registro de solicitudes de cambio de alcance", DOCUMENTOS["04"]),
        ("Dirección y Gestión de Proyectos", "Matriz de riesgos (reevaluación)", DOCUMENTOS["02"]),
        ("Dirección y Gestión de Proyectos", "Plan de casos de prueba", DOCUMENTOS["03"]),
        ("El Emprendedor Digital y el Contexto", "Campaña de Instagram «Sin talar un árbol»", DOCUMENTOS["05"]),
        ("El Emprendedor Digital y el Contexto", "Evidencia de publicación en Instagram", "s_instagram"),
        ("El Emprendedor Digital y el Contexto", "Panel de métricas de conversión (KPIs)", DOCUMENTOS["06"]),
        ("Desarrollo de Sitios Web", "Consumo asincrónico y renderizado dinámico del DOM", "s_fetch"),
        ("Desarrollo de Sitios Web", "Carrito de compras y validación del checkout", "s_carrito"),
        ("Desarrollo de Sitios Web", "Código JavaScript del Sprint 3", "s_codigo"),
        ("Desarrollo de Sitios Web", "Repositorio y código consolidado", "s_repo"),
        ("Legislación Informática", "Términos y Condiciones y Ley 24.240", DOCUMENTOS["01"]),
        ("Legislación Informática", "Publicación legal en el sitio", "s_legal"),
    ]
    partes = [(m, t, pymupdf.open(TMP / f"{a}.pdf")) for m, t, a in orden]

    entradas, pagina_actual = [], 3     # portada (1) e índice (2)
    for materia, titulo, doc in partes:
        if not entradas or entradas[-1][0] != materia:
            entradas.append((materia, []))
        entradas[-1][1].append((titulo, pagina_actual))
        pagina_actual += len(doc)
    a_pdf({"portada": portada(), "indice": indice(entradas)})

    final = pymupdf.open()
    final.insert_pdf(pymupdf.open(TMP / "portada.pdf"))
    final.insert_pdf(pymupdf.open(TMP / "indice.pdf"))
    assert len(final) == 2, "el índice ocupa más de una página"
    toc = [[1, "Portada", 1], [1, "Índice", 2]]
    for materia, items in entradas:
        toc.append([1, materia, items[0][1]])
        toc += [[2, t, p] for t, p in items]
    for _, _, doc in partes:
        final.insert_pdf(doc)

    total = len(final)
    for n, pag in enumerate(final, start=1):
        if n == 1:
            continue
        r = pag.rect
        pag.insert_text((50, r.height - 22), PIE, fontname="helv", fontsize=7.5, color=(0.42, 0.41, 0.35))
        texto = f"{n} / {total}"
        pag.insert_text((r.width - 50 - pymupdf.get_text_length(texto, "helv", 7.5), r.height - 22), texto,
                        fontname="helv", fontsize=7.5, color=(0.42, 0.41, 0.35))
    final.set_toc(toc)
    final.set_metadata({"title": "Woodbird — Carpeta integradora del Sprint 3", "author": "Reiss Jorge Nicolás",
                        "subject": "Proyecto integrador EcoStart IA — IES René Favaloro"})
    final.save(SALIDA, garbage=4, deflate=True)
    print(f"{SALIDA.name}: {total} páginas")


if __name__ == "__main__":
    main()
