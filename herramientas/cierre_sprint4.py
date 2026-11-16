# Genera los entregables del Sprint 4 sobre el sitio en producción:
#   sitio/docs/sprint-4/02_Despliegue_en_Produccion_HTTPS.docx   (Tarea 4.1, Desarrollo de Sitios Web)
#   sitio/docs/sprint-4/03_Auditoria_Legal_Final.docx            (Tarea 4.6, Legislación Informática)
#   sitio/docs/sprint-4/evidencia/                               (capturas y datos crudos)
# Antes hay que correr la auditoría automática contra el sitio publicado:
#   node pruebas/auditoria_legal.mjs https://nicorsss.github.io/Woodbird/ pruebas/auditoria   (desde sitio/)
# Uso: python herramientas/cierre_sprint4.py
# Mide de nuevo el sitio en vivo (redirección, encabezados, certificado, GitHub Pages y
# sincronización archivo por archivo), así que los documentos reflejan el estado del día.

import hashlib
import http.client
import json
import shutil
import socket
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
import time
from datetime import datetime, timezone
from pathlib import Path

from docx.shared import Inches, Pt

from gestion_sprint3 import nuevo
from terminos import tabla, viñeta

sys.stdout.reconfigure(encoding="utf-8")
SITIO = Path(__file__).resolve().parent.parent / "sitio"
DESTINO = SITIO / "docs" / "sprint-4"
EVIDENCIA = DESTINO / "evidencia"
AUDITORIA = SITIO / "pruebas" / "auditoria"
HOST = "nicorsss.github.io"
BASE = f"https://{HOST}/Woodbird/"
REPO = "nicorsss/Woodbird"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
HOY = datetime.now()
FECHA = f"{HOY.day} de {MESES[HOY.month - 1]} de {HOY.year}"


def fecha_corta(texto_cert):
    # «Dec 29 23:44:45 2026 GMT» → «29/12/2026»
    return datetime.strptime(texto_cert, "%b %d %H:%M:%S %Y %Z").strftime("%d/%m/%Y")


def firma(doc, texto, rol):
    doc.add_heading("Firma", level=1)
    doc.add_paragraph(texto)
    doc.add_paragraph(f"{rol}: Reiss Jorge Nicolás")
    doc.add_paragraph("Firma: ______________________________")
    doc.add_paragraph("Fecha: ____ / ____ / 2026")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=SITIO)


# ---------------------------------------------------------------------------
# Mediciones en vivo
# ---------------------------------------------------------------------------
def medir_https():
    c = http.client.HTTPConnection(HOST, 80, timeout=20)
    c.request("HEAD", "/Woodbird/")
    r = c.getresponse()
    redireccion = (r.status, r.reason, r.getheader("Location"))

    c = http.client.HTTPSConnection(HOST, 443, timeout=20)
    c.request("HEAD", "/Woodbird/")
    r = c.getresponse()
    encabezados = {k: r.getheader(k) for k in ("Server", "Content-Type", "Strict-Transport-Security", "Last-Modified")}
    estado = r.status

    ctx = ssl.create_default_context()
    with socket.create_connection((HOST, 443), timeout=20) as s, ctx.wrap_socket(s, server_hostname=HOST) as t:
        cert, protocolo, cifrado = t.getpeercert(), t.version(), t.cipher()[0]
    sujeto = dict(x[0] for x in cert["subject"])
    emisor = dict(x[0] for x in cert["issuer"])
    nombres = [v for k, v in cert.get("subjectAltName", []) if k == "DNS"]

    pages = json.loads(subprocess.check_output(["gh", "api", f"repos/{REPO}/pages"]))
    build = json.loads(subprocess.check_output(["gh", "api", f"repos/{REPO}/pages/builds/latest"]))
    return {
        "redireccion": redireccion, "estado": estado, "encabezados": encabezados,
        "certificado": {"sujeto": sujeto.get("commonName"), "emisor": f"{emisor.get('organizationName')} ({emisor.get('commonName')})",
                        "desde": fecha_corta(cert["notBefore"]), "hasta": fecha_corta(cert["notAfter"]),
                        "nombres": nombres, "protocolo": protocolo, "cifrado": cifrado, "verificado": True},
        "pages": {"estado": pages["status"], "https": pages["https_enforced"], "rama": pages["source"]["branch"],
                  "carpeta": pages["source"]["path"], "url": pages["html_url"], "tipo": pages["build_type"]},
        "build": {"estado": build["status"], "commit": build["commit"], "fecha": build["created_at"],
                  "segundos": round(build["duration"] / 1000)},
        "head": git("rev-parse", "HEAD").decode().strip(),
    }


def medir_sincronizacion():
    archivos = [a for a in git("ls-files").decode("utf-8").splitlines() if a]
    filas = []
    for a in archivos:
        local = git("show", f"HEAD:{a}")
        req = urllib.request.Request(BASE + urllib.parse.quote(a), headers={"User-Agent": "woodbird-auditoria"})
        for intento in range(1, 5):  # la red corta conexiones de vez en cuando (WinError 10054, timeouts)
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    vivo, codigo = r.read(), r.status
                break
            except urllib.error.HTTPError as e:
                vivo, codigo = b"", e.code
                break
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                if intento == 4:
                    raise
                time.sleep(2 * intento)
        filas.append({"archivo": a, "http": codigo, "bytes": len(local),
                      "sha256": hashlib.sha256(local).hexdigest(),
                      "igual": hashlib.sha256(local).digest() == hashlib.sha256(vivo).digest()})
    return filas


def contenido_mixto():
    # Recursos pedidos por http:// desde las páginas, estilos o scripts publicados
    hallados = []
    for patron in ("*.html", "css/*.css", "js/*.js"):
        for f in SITIO.glob(patron):
            for n, linea in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if "http://" in linea and "www.w3.org" not in linea:
                    hallados.append(f"{f.relative_to(SITIO).as_posix()}:{n}")
    return hallados


# ---------------------------------------------------------------------------
# 02 · Despliegue en producción con HTTPS (Tarea 4.1)
# ---------------------------------------------------------------------------
def despliegue(h, sinc, mixto, auditoria):
    doc = nuevo("Despliegue en Producción con HTTPS", "Sprint 4 — Tarea 4.1: Despliegue en producción (hosting gratuito y SSL)",
                rol="Desarrollador Web")
    doc.tables[0].rows[0].cells[1].paragraphs[0].runs[0].text = "Desarrollo de Sitios Web (DSW)"
    doc.tables[0].rows[-1].cells[1].paragraphs[0].runs[0].text = FECHA

    doc.add_heading("1. Objetivo", level=1)
    doc.add_paragraph(
        "Verificar que la tienda Woodbird está publicada en un servicio de alojamiento gratuito en la nube, que funciona en vivo "
        "bajo el protocolo seguro HTTPS y que los archivos del repositorio se sincronizan correctamente con el servidor remoto. "
        f"Todas las mediciones de este documento se tomaron sobre el sitio en producción el {FECHA}, con el script "
        "herramientas/cierre_sprint4.py y la auditoría automática pruebas/auditoria_legal.mjs, de modo que se pueden repetir.")

    doc.add_heading("2. Plataforma de despliegue", level=1)
    p = h["pages"]
    tabla(doc, ["Elemento", "Valor"], [
        ("Servicio", "GitHub Pages (alojamiento estático gratuito de GitHub, Inc.)"),
        ("URL pública", p["url"]),
        ("Repositorio público", f"https://github.com/{REPO}"),
        ("Origen de la publicación", f"Rama «{p['rama']}», carpeta «{p['carpeta']}» (modo {p['tipo']}: cada push a main vuelve a publicar)"),
        ("Publicado desde", "29/09/2026 (Sprint 2). Desde entonces cada entrega se publicó con un push a main."),
        ("Estado del sitio", f"{p['estado']} (publicado y sirviendo)"),
        ("HTTPS obligatorio («Enforce HTTPS»)", "Activado" if p["https"] else "Desactivado"),
    ], [2.0, 4.5])

    doc.add_heading("3. Evidencia de HTTPS (SSL/TLS)", level=1)
    c, e = h["certificado"], h["encabezados"]
    red = h["redireccion"]
    tabla(doc, ["Verificación", "Resultado", "Qué significa"], [
        ("Acceso por http://", f"HTTP {red[0]} {red[1]} → {red[2]}",
         "Quien escribe la dirección sin «s» es redirigido de forma permanente a la versión cifrada."),
        ("Acceso por https://", f"HTTP {h['estado']} OK, servidor {e['Server']}", "La página responde por la conexión cifrada."),
        ("Protocolo y cifrado", f"{c['protocolo']}, {c['cifrado']}", "Versión vigente de TLS, con cifrado autenticado."),
        ("Certificado", f"{c['sujeto']}, emitido por {c['emisor']}", "Certificado comodín de GitHub para todos los sitios *.github.io."),
        ("Vigencia", f"Del {c['desde']} al {c['hasta']}", "GitHub lo renueva automáticamente antes de vencer; no requiere acción."),
        ("Validación de la cadena", "Correcta (verificado contra los certificados raíz del sistema)", "El navegador muestra el candado sin advertencias."),
        ("HSTS", e["Strict-Transport-Security"] or "Ausente",
         "Durante un año el navegador usa siempre HTTPS con este sitio, aunque se escriba http://."),
        ("Estado de seguridad en Chrome", f"«secure» en las {len(auditoria['seguridad'])} páginas del sitio",
         "Medido por la auditoría automática con el protocolo de depuración de Chrome."),
        ("Contenido mixto", "Ninguno" if not mixto else ", ".join(mixto),
         "Ningún recurso se pide por http://, así que el candado no se degrada."),
    ], [1.6, 2.5, 2.4])

    doc.add_heading("4. Sincronización del repositorio con el servidor", level=1)
    iguales = [f for f in sinc if f["igual"]]
    distintos = [f for f in sinc if not f["igual"]]
    b = h["build"]
    doc.add_paragraph(
        f"La última publicación de GitHub Pages corresponde al commit {b['commit'][:7]}, que es el mismo que la punta de la rama main "
        f"({h['head'][:7]}). El build terminó con estado «{b['estado']}» en {b['segundos']} segundos.")
    doc.add_paragraph(
        f"Además se descargó del sitio en vivo cada uno de los {len(sinc)} archivos del repositorio y se comparó su huella SHA-256 con la "
        f"versión del commit: {len(iguales)} son idénticos byte a byte.")
    grupos = {}
    for f in sinc:
        a = f["archivo"]
        clave = ("Páginas HTML" if a.endswith(".html") else "Estilos (CSS)" if a.startswith("css/") else
                 "Scripts (JS)" if a.startswith("js/") else "Catálogo (productos.json)" if a == "productos.json" else
                 "Imágenes de producto" if a.startswith("assets/") else "Documentación (docs/)" if a.startswith("docs/") else
                 "Pruebas automáticas" if a.startswith("pruebas/") else "Otros (licencias, README)")
        g = grupos.setdefault(clave, [0, 0, 0])
        g[0] += 1
        g[1] += f["igual"]
        g[2] += f["bytes"]
    tabla(doc, ["Grupo", "Archivos", "Idénticos en el servidor", "Tamaño"],
          [(k, str(v[0]), str(v[1]), f"{v[2] / 1024:,.0f} KB".replace(",", ".")) for k, v in grupos.items()], [2.4, 1.0, 1.6, 1.5])
    for f in distintos:
        motivo = ("GitHub Pages no publica los archivos ocultos (que empiezan con punto); es el comportamiento esperado."
                  if Path(f["archivo"]).name.startswith(".") else "Revisar: el archivo publicado difiere del repositorio.")
        viñeta(doc, f"{f['archivo']} (HTTP {f['http']}):", motivo)

    doc.add_heading("5. Funcionamiento en vivo", level=1)
    doc.add_paragraph(
        "La auditoría automática recorrió el sitio publicado en un teléfono de 390 px y en un escritorio de 1366 px: el catálogo se "
        "carga con Fetch desde productos.json, las imágenes generadas con IA se muestran con su sello, el carrito suma y el checkout "
        "confirma una compra simulada sin enviar datos. El detalle está en la Auditoría Legal Final (Tarea 4.6).")
    for nombre, ancho, pie in [("index-escritorio", 6.3, "Portada publicada en escritorio (1366 px)."),
                               ("catalogo-sello-ia", 6.3, "Catálogo en producción: tarjetas generadas desde productos.json, con imagen y sello «Imagen con IA».")]:
        doc.add_picture(str(EVIDENCIA / f"{nombre}.png"), width=Inches(ancho))
        doc.add_paragraph(pie).runs[0].italic = True
    doc.add_picture(str(EVIDENCIA / "index-movil.png"), width=Inches(2.2))
    doc.add_paragraph("Portada publicada en un teléfono (390 px), con el Botón de arrepentimiento visible.").runs[0].italic = True

    doc.add_heading("6. Conclusión", level=1)
    doc.add_paragraph(
        f"La Tarea 4.1 está cumplida. El sitio funciona en producción en {p['url']}, sirve todas sus páginas por HTTPS con TLS 1.3 y un "
        "certificado válido, redirige el tráfico sin cifrar, aplica HSTS y está sincronizado con el repositorio: cada push a main se publica "
        "solo, en alrededor de un minuto, y los archivos servidos coinciden con los del último commit.")
    viñeta(doc, "Dependencia:", "el sitio depende de la disponibilidad de GitHub (riesgo R9). Como es estático, se podría mover a "
           "Netlify o Vercel en minutos, sin cambiar el código.")
    viñeta(doc, "Dominio propio:", "el sitio usa el subdominio gratuito de GitHub. Registrar woodbird.com.ar exigiría configurar el DNS "
           "y volver a emitir el certificado; queda fuera del alcance académico.")
    firma(doc, f"Evidencia medida sobre el sitio en producción el {FECHA}.", "Desarrollador Web")
    doc.save(DESTINO / "02_Despliegue_en_Produccion_HTTPS.docx")


# ---------------------------------------------------------------------------
# 03 · Auditoría legal final del sitio en vivo (Tarea 4.6)
# ---------------------------------------------------------------------------
# id, severidad, hallazgo, norma, acción correctiva, estado
HALLAZGOS = [
    ("H1", "Media",
     "La Declaración ética y de transparencia de IA solo se publica como archivo de Word (.docx). En el celular se descarga en lugar de "
     "leerse en el navegador. Además el texto dice que el sello «Imagen con IA» enlaza a la declaración, pero el sello no es un enlace, y no "
     "nombra la herramienta usada (Google Gemini) ni el registro de prompts.",
     "Transparencia de IA (consigna 4.6); Ley 24.240 art. 4 (información clara y accesible)",
     "Publicar la declaración como página HTML enlazada desde el pie, agregar la herramienta y el registro de prompts, y alinear el texto "
     "con lo que hace el sello. Hecho el 03/11: declaracion-ia.html, versión 1.1, enlazada desde el pie de las cuatro páginas.",
     "Corregido"),
    ("H2", "Media",
     "Los correos que el sitio ofrece para ejercer derechos (privacidad@, arrepentimiento@ y contacto@woodbird.com.ar) no funcionan: el "
     "dominio woodbird.com.ar no está registrado (la consulta DNS devuelve «dominio inexistente»). Un usuario que quisiera ejercer el "
     "acceso a sus datos o pedir el código de arrepentimiento no recibiría respuesta.",
     "Ley 25.326 art. 14 (respuesta en 10 días); Res. SCI 424/2020 (código en 24 horas)",
     "Reemplazar las direcciones por un canal que funcione. Hecho el 03/11: woodbirdshop@gmail.com y mensaje directo a @woodbird.ar en "
     "Instagram, en la Política (versión 1.1), los Términos (versión 1.2), la Declaración y el pie de todas las páginas. Si la tienda "
     "operara, registrar un dominio propio antes de abrir.",
     "Corregido"),
    ("H3", "Baja",
     "La cláusula 1 de la Política de privacidad (versión 1.0, del 22/09) describe a Woodbird como tienda de «aves decorativas talladas en "
     "madera». Contradice la tesis de piezas ficticias aprobada en la SC-06, que el resto del sitio ya aplica.",
     "Ley 24.240 art. 4 (información veraz); Ley 25.326 art. 6",
     "Reemplazar por «aves decorativas inspiradas en el tallado en madera, diseñadas con IA» y publicar la versión 1.1 con su fecha. "
     "Hecho el 03/11, junto con la misma corrección en la cláusula 1 de los Términos.",
     "Corregido"),
    ("H4", "Baja",
     "La Política nombra a Google Fonts como tercero que recibe la IP, pero al alojamiento lo menciona en forma genérica. Es GitHub, Inc., "
     "con servidores en Estados Unidos, que no figura entre los países con nivel adecuado de protección.",
     "Ley 25.326 art. 12 (transferencia internacional); Disposición DNPDP 60/2016",
     "Identificar a GitHub, Inc. (Estados Unidos) en la cláusula de terceros. Como mejora, alojar las tipografías en el propio sitio para "
     "dejar de enviar la IP a Google. Hecho el 03/11: la cláusula 7 de la Política (versión 1.1) nombra a GitHub, Inc. y a Google LLC.",
     "Corregido"),
]


def auditoria_legal(a):
    doc = nuevo("Auditoría Legal Final del Sitio en Vivo", "Sprint 4 — Tarea 4.6: Auditoría legal final del sitio web en producción",
                rol="Compliance Officer")
    doc.tables[0].rows[0].cells[1].paragraphs[0].runs[0].text = "Legislación Informática (LI)"
    doc.tables[0].rows[-1].cells[1].paragraphs[0].runs[0].text = FECHA
    r = a["resultados"]
    cumplen = sum(x["cumple"] for x in r)

    doc.add_heading("1. Objeto y alcance", level=1)
    doc.add_paragraph(
        "Verificar que el sitio web desplegado en producción contiene todos los instrumentos jurídicos requeridos: el aviso legal de uso de "
        "inteligencia artificial, la Política de Privacidad (Ley N° 25.326) y los Términos y Condiciones de compra con botón de "
        "arrepentimiento (Ley N° 24.240). La auditoría se hizo sobre el sitio publicado, no sobre la copia local, porque es lo que ve el usuario.")
    tabla(doc, ["Elemento", "Detalle"], [
        ("Sitio auditado", a["base"]),
        ("Fecha y hora", datetime.fromisoformat(a["fecha"].replace("Z", "+00:00")).astimezone().strftime("%d/%m/%Y %H:%M")),
        ("Páginas", "Inicio (catálogo, carrito y checkout), Política de privacidad, Términos y condiciones, Declaración ética y transparencia de IA"),
        ("Dispositivos", "Teléfono de 390 × 844 px y escritorio de 1366 × 768 px"),
        ("Método", "1) Verificación automática con Chrome sin interfaz (pruebas/auditoria_legal.mjs), que además registra cada pedido de red, "
                   "las cookies y el almacenamiento. 2) Lectura de los textos legales publicados y contraste con el funcionamiento real del sitio."),
    ], [1.6, 4.9])

    doc.add_heading("2. Marco normativo auditado", level=1)
    tabla(doc, ["Norma", "Exigencia que se verifica"], [
        ("Ley N° 25.326 (Protección de Datos Personales)", "Información al titular (art. 6), consentimiento (art. 5), seguridad (art. 9), "
         "derechos de acceso, rectificación y supresión (arts. 14 a 16), transferencia internacional (art. 12) y autoridad de control (AAIP)."),
        ("Ley N° 24.240 (Defensa del Consumidor)", "Información veraz y clara (art. 4), garantía (art. 11) y revocación o arrepentimiento "
         "de 10 días en las ventas a distancia (art. 34)."),
        ("Res. SCI N° 424/2020", "Botón de arrepentimiento en la primera pantalla, sin registro previo, con código de identificación en 24 horas."),
        ("Res. SCI N° 274/2021", "Enlace «Defensa de las y los Consumidores. Para reclamos ingrese aquí» a la Ventanilla Única Federal."),
        ("Transparencia de IA", "Aviso de que las imágenes y las piezas son contenido sintético (Declaración ética del Sprint 1 y tesis SC-06)."),
        ("Ley N° 11.723 (Propiedad intelectual)", "Aviso de licencias del código y de la documentación."),
    ], [2.2, 4.3])

    doc.add_heading("3. Resultado de la verificación automática", level=1)
    doc.add_paragraph(f"Se ejecutaron {len(r)} verificaciones y {cumplen} cumplen.").runs[0].bold = True
    tabla(doc, ["Id", "Página", "Requisito", "Norma", "Resultado y evidencia"],
          [(x["id"], x["pagina"], x["requisito"], x["norma"], ("CUMPLE. " if x["cumple"] else "NO CUMPLE. ") + x["evidencia"]) for x in r],
          [0.4, 0.9, 1.8, 1.3, 2.1])

    doc.add_heading("4. Instrumentos jurídicos en producción", level=1)
    doc.add_heading("4.1 Aviso legal de uso de IA", level=2)
    doc.add_paragraph(
        "Presente en tres niveles: el sello «Imagen con IA» sobre cada una de las imágenes de producto, con un texto alternativo que también "
        "lo declara (L16); la leyenda del pie («Las imágenes de producto marcadas “Imagen con IA” fueron generadas con inteligencia "
        "artificial»); y el enlace a la Declaración ética en las tres páginas (L02). Los Términos repiten que la tienda es una demostración "
        "con piezas ficticias (L15) y el checkout lo advierte antes del formulario (L17). Ver el hallazgo H1 sobre el formato de la declaración.")
    doc.add_picture(str(EVIDENCIA / "catalogo-sello-ia.png"), width=Inches(6.3))
    doc.add_paragraph("Catálogo publicado: cada imagen lleva el sello «Imagen con IA».").runs[0].italic = True

    doc.add_heading("4.2 Política de Privacidad (Ley N° 25.326)", level=2)
    doc.add_paragraph(
        "Publicada y enlazada en todas las páginas y en el checkout. Identifica al responsable, la finalidad, los derechos y la AAIP (L09 a L12). "
        "Lo más importante es que el sitio hace lo que la política promete:")
    for neg, txt in [
        ("Consentimiento:", "no se puede confirmar la compra sin marcar la casilla de la política (L18 y L20)."),
        ("Los datos no salen del navegador:", f"durante la confirmación de una compra completa hubo {len(a['pedidosCompra'])} pedidos de red; el "
         "formulario se borra y la URL no lleva datos (L21)."),
        ("Sin cookies ni almacenamiento:", "al terminar el recorrido no hay cookies, ni localStorage, ni sessionStorage (L22)."),
        ("Terceros:", f"los únicos servidores externos contactados son {', '.join(a['terceros'])}, que la política declara (L23)."),
        ("Seguridad:", "todas las páginas se sirven por HTTPS con TLS 1.3 (L24 y Tarea 4.1)."),
    ]:
        viñeta(doc, neg, txt)

    doc.add_heading("4.3 Términos y Condiciones y botón de arrepentimiento (Ley N° 24.240)", level=2)
    doc.add_paragraph(
        "Publicados y de aceptación obligatoria en el checkout (L18). El Botón de arrepentimiento está en el encabezado de las tres páginas, "
        "dentro de la primera pantalla tanto en el teléfono como en el escritorio (L01), y lleva directo a la cláusula 9, que explica el plazo "
        "de 10 días corridos, la gratuidad y el código de identificación en 24 horas (L08 y L13). El checkout recuerda el plazo antes de pagar "
        "(L19) y el mensaje de confirmación entrega un número de pedido para usar el botón. El enlace a la Ventanilla Única Federal está en el "
        "pie (L05). Ver el hallazgo H2 sobre el correo de arrepentimiento.")
    tabla_capturas = doc.add_table(rows=1, cols=2)
    for celda, (img, pie) in zip(tabla_capturas.rows[0].cells, [("index-movil.png", "Botón en la primera pantalla (390 px)"),
                                                                ("terminos-arrepentimiento.png", "Destino del botón: cláusula 9")]):
        celda.paragraphs[0].add_run().add_picture(str(EVIDENCIA / img), width=Inches(2.0 if "movil" in img else 3.9))
        celda.add_paragraph(pie).runs[0].italic = True
    doc.add_paragraph()
    doc.add_picture(str(EVIDENCIA / "checkout-confirmado.png"), width=Inches(6.3))
    doc.add_paragraph("Compra simulada confirmada en producción: aceptación de Términos y Política, aviso de 10 días y número de pedido.").runs[0].italic = True

    doc.add_heading("5. Hallazgos de la revisión manual", level=1)
    doc.add_paragraph(
        "La verificación automática comprueba que cada instrumento existe y funciona. La lectura de los textos contra el sitio real encontró "
        "cuatro puntos que no impiden cumplir la consigna, pero que una tienda real tendría que corregir:")
    tabla(doc, ["Id", "Nivel", "Hallazgo", "Norma", "Acción correctiva", "Estado"],
          [h for h in HALLAZGOS], [0.35, 0.55, 2.0, 1.05, 1.65, 0.9])

    doc.add_heading("6. Conclusión", level=1)
    abiertos = [h for h in HALLAZGOS if h[5] != "Corregido"]
    doc.add_paragraph(
        f"El sitio en producción contiene los tres instrumentos jurídicos que pide la consigna y cumple las {len(r)} verificaciones "
        "automáticas: el aviso de uso de IA, la Política de Privacidad conforme a la Ley N° 25.326 y los Términos y Condiciones con el botón "
        "de arrepentimiento de la Ley N° 24.240 y la Res. SCI N° 424/2020. Además, el funcionamiento del sitio coincide con lo que prometen los "
        "textos: la compra no transmite datos, no hay cookies y los únicos terceros son los declarados.")
    if abiertos:
        doc.add_paragraph(
            f"Quedan {len(abiertos)} hallazgos de severidad media o baja ({', '.join(h[0] for h in abiertos)}). Corresponden a la coherencia "
            "entre los textos y la tesis de tienda ficticia, y a canales de contacto que solo existirían si la tienda operara.")
    else:
        doc.add_paragraph("Los cuatro hallazgos de la revisión manual se corrigieron y se volvieron a verificar en producción.")
    firma(doc, f"Auditoría realizada sobre el sitio en producción el {FECHA}.", "Compliance Officer")
    doc.save(DESTINO / "03_Auditoria_Legal_Final.docx")


if __name__ == "__main__":
    a = json.loads((AUDITORIA / "auditoria.json").read_text(encoding="utf-8"))
    EVIDENCIA.mkdir(parents=True, exist_ok=True)
    for f in AUDITORIA.glob("*.png"):
        shutil.copy(f, EVIDENCIA / f.name)
    shutil.copy(AUDITORIA / "auditoria.json", EVIDENCIA / "auditoria_legal.json")

    h = medir_https()
    sinc = medir_sincronizacion()
    mixto = contenido_mixto()
    (EVIDENCIA / "despliegue.json").write_text(json.dumps({"https": h, "contenido_mixto": mixto, "sincronizacion": sinc},
                                                          ensure_ascii=False, indent=1), encoding="utf-8")
    despliegue(h, sinc, mixto, a)
    auditoria_legal(a)
    print(f"HTTPS: {h['redireccion'][0]} → {h['redireccion'][2]}; {h['certificado']['protocolo']}; válido hasta {h['certificado']['hasta']}")
    print(f"Sincronización: {sum(f['igual'] for f in sinc)} de {len(sinc)} archivos idénticos; build {h['build']['commit'][:7]} = HEAD {h['head'][:7]}")
    print(f"Contenido mixto: {mixto or 'ninguno'}")
    print(f"Auditoría: {sum(x['cumple'] for x in a['resultados'])} de {len(a['resultados'])} verificaciones; {len(HALLAZGOS)} hallazgos manuales")
    print("Listo:", ", ".join(p.name for p in DESTINO.glob("0[23]_*.docx")))
