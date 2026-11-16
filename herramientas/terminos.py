# Genera, desde una misma fuente, los Términos y Condiciones de Woodbird:
#   - sitio/terminos-y-condiciones.html (página publicada)
#   - sitio/docs/sprint-3/01_Terminos_y_Condiciones.docx (entregable de Legislación Informática)
# Si se cambia una cláusula, se cambia acá y se vuelve a ejecutar:
#   python herramientas/terminos.py

import html
import re
from pathlib import Path
from urllib.parse import quote

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Inches

RAIZ = Path(__file__).resolve().parent.parent / "sitio"
VERSION = "1.2"
VIGENCIA_ISO = "2026-11-03"
VIGENCIA = "3 de noviembre de 2026"

# Hallazgo H2 de la auditoría del Sprint 4: el dominio woodbird.com.ar no existe; se usa un correo real.
CORREO = "woodbirdshop@gmail.com"
CORREO_ARREPENTIMIENTO = CORREO
INSTAGRAM = "https://www.instagram.com/woodbird.ar/"
MAILTO_ARREPENTIMIENTO = "mailto:{}?subject={}&body={}".format(
    CORREO_ARREPENTIMIENTO,
    quote("Arrepentimiento de compra"),
    quote("Quiero revocar mi compra (artículo 34 de la Ley N° 24.240).\n\n"
          "Número de pedido: WB-\nNombre y apellido: \nMedio de contacto: \n"),
)
VENTANILLA = "https://www.argentina.gob.ar/produccion/defensadelconsumidor/formulario"
TEXTO_VENTANILLA = "Defensa de las y los Consumidores. Para reclamos ingrese aquí"

# ---------------------------------------------------------------------------
# Texto del contrato. Bloques: ("p", texto) · ("ul", [textos]) · ("boton", texto, enlace)
# Enlaces con la sintaxis [texto](url): en la web son <a>, en el .docx sólo texto.
# ---------------------------------------------------------------------------
CLAUSULAS = [
    ("partes-y-aceptacion", "Partes y aceptación", [
        ("p", "Estos Términos y Condiciones regulan el uso del sitio web de Woodbird y las compras que se realicen en él. "
              "El proveedor es Woodbird, tienda online de aves decorativas inspiradas en el tallado en maderas nativas y diseñadas con inteligencia artificial, representada por "
              "Reiss Jorge Nicolás, con domicilio en Resistencia, provincia del Chaco, República Argentina, y correo electrónico "
              "[" + CORREO + "](mailto:" + CORREO + "). Quien navega el sitio es el «usuario» y, cuando "
              "compra productos como destinatario final, el «consumidor» en los términos del artículo 1 de la Ley N° 24.240."),
        ("p", "Se trata de un contrato de adhesión a cláusulas generales predispuestas (artículos 984 a 989 del Código Civil y "
              "Comercial de la Nación y artículo 38 de la Ley N° 24.240). Para finalizar una compra, el formulario le solicita "
              "que marque la casilla «Leí y acepto los Términos y Condiciones»: ese acto expresa su aceptación. Quien sólo "
              "navega el sitio, sin comprar, queda sujeto únicamente a las reglas de uso y de propiedad intelectual."),
        ("p", "El contrato se celebra por medios electrónicos, que satisfacen el requisito de la forma escrita (artículo 1106 "
              "del Código Civil y Comercial). Este texto queda publicado en forma permanente en el sitio, donde puede leerlo, "
              "guardarlo o imprimirlo antes y después de comprar."),
    ]),
    ("caracter-de-demostracion", "Carácter de demostración del sitio", [
        ("p", "Woodbird es un proyecto académico de la Tecnicatura Superior en Desarrollo de Software del IES «René Favaloro». "
              "Mientras funcione como demostración, la tienda es una simulación: no se venden ni se entregan productos, no se "
              "cobra ningún importe y los pedidos confirmados no generan obligaciones de pago ni de entrega para ninguna de "
              "las partes."),
        ("p", "Las piezas del catálogo son diseños ficticios generados con inteligencia artificial, inspirados en el tallado "
              "tradicional en maderas nativas del Chaco. No existe una pieza física detrás de cada diseño: Woodbird no tala "
              "ni trabaja madera y no envía productos. Esa es la propuesta de triple impacto del proyecto, porque el palo "
              "santo es una especie protegida (Apéndice II de la CITES y Ley N° 26.331 de presupuestos mínimos de "
              "protección de los bosques nativos)."),
        ("p", "Estos términos están redactados como los de una tienda en funcionamiento, para que el sitio respete desde su "
              "diseño las reglas que se aplicarían a una operación real. Las cláusulas sobre productos, envíos, "
              "arrepentimiento y garantía describen los derechos que tendría el consumidor si Woodbird produjera y vendiera "
              "las piezas. En ese caso, sólo se usaría madera de origen legal y trazable, con las autorizaciones que exigen "
              "la Ley N° 26.331 y, para el palo santo, el régimen de la CITES. Si Woodbird comenzara a vender, lo informará "
              "en el sitio y publicará una nueva versión de este documento antes de aceptar el primer pedido."),
    ]),
    ("uso-del-sitio", "Uso del sitio y reglas de conducta", [
        ("p", "El sitio está dirigido a personas mayores de 18 años. Los menores de edad sólo pueden comprar con la "
              "intervención de su padre, madre o tutor. Al usar el sitio, el usuario se compromete a:"),
        ("ul", [
            "Ingresar en el formulario de compra datos verdaderos, actuales y propios.",
            "Usar el sitio de buena fe, para consultar el catálogo y comprar para sí o para regalar.",
            "No intentar acceder a partes del sitio o del servidor que no estén publicadas, ni alterar su funcionamiento, sus precios o su código.",
            "No usar programas automatizados (robots o extractores) para copiar el catálogo o generar pedidos en forma masiva.",
            "No usar la marca, los textos ni las imágenes del sitio de un modo que haga creer que actúa en nombre de Woodbird.",
        ]),
        ("p", "Si un usuario incumple estas reglas, Woodbird puede rechazar o cancelar los pedidos afectados e informarle el "
              "motivo. Esta facultad no alcanza a los pedidos hechos de buena fe ni limita los derechos que la ley le "
              "reconoce como consumidor."),
    ]),
    ("productos", "Productos e información", [
        ("p", "Cada diseño representa un ave tallada a mano en una sola pieza de madera nativa del Chaco: palo santo, "
              "algarrobo o quebracho. El catálogo informa para cada diseño su nombre, la madera que representa, la altura en "
              "centímetros, una descripción y el precio, conforme al deber de información cierta, clara y detallada del "
              "artículo 4 de la Ley N° 24.240."),
        ("p", "Si las piezas se produjeran, por tratarse de trabajos artesanales en madera natural cada una sería única, y "
              "esto se informaría antes de la compra:"),
        ("ul", [
            "El dibujo de las vetas y el tono de la madera variarían de una pieza a otra y no constituirían un defecto.",
            "La altura real podría diferir hasta en 1 cm de la informada.",
            "El palo santo tendría un aroma propio que se atenúa con el tiempo.",
        ]),
        ("p", "Las imágenes de producto fueron generadas con inteligencia artificial y llevan el sello «Imagen con IA». Son "
              "ilustrativas: muestran el tipo de pieza, pero no la pieza exacta que se entrega. Woodbird queda obligado por la "
              "descripción escrita de cada pieza (madera, medida y características) y por lo que la imagen razonablemente "
              "permita esperar (artículo 8 de la Ley N° 24.240)."),
        ("p", "Las piezas sin unidades disponibles se muestran con la leyenda «Sin stock» y no pueden agregarse al carrito."),
    ]),
    ("precios", "Precios y vigencia de la oferta", [
        ("p", "Los precios se expresan en pesos argentinos y son precios finales, con todos los impuestos incluidos. El costo "
              "de envío se informa por separado en el carrito y en el resumen de pago, antes de confirmar el pedido."),
        ("p", "Los precios y las condiciones obligan a Woodbird mientras estén publicados en el sitio (artículo 7 de la Ley "
              "N° 24.240 y artículo 1108 del Código Civil y Comercial). Un cambio de precio posterior no afecta a los pedidos "
              "ya confirmados."),
    ]),
    ("proceso-de-compra", "Proceso de compra", [
        ("p", "La compra se realiza en tres pasos:"),
        ("ul", [
            "Carrito: el usuario agrega piezas desde el catálogo y puede cambiar la cantidad, hasta 10 unidades por pieza, o "
            "quitarlas. El carrito muestra en todo momento el subtotal, el envío y el total.",
            "Datos: el usuario completa sus datos de contacto y la dirección de entrega, y acepta estos Términos y Condiciones "
            "y la [Política de privacidad](politica-privacidad.html).",
            "Confirmación: al presionar «Ir al pago», el sitio verifica que el carrito no esté vacío y que los datos estén "
            "completos y sean coherentes. Si todo es correcto, muestra la confirmación con un número de pedido (con el formato "
            "WB-XXXXXX), la cantidad de piezas, el total y un recordatorio del derecho de arrepentimiento.",
        ]),
        ("p", "Hasta presionar «Ir al pago», el usuario puede revisar y corregir su pedido. El número de pedido identifica la "
              "compra en cualquier consulta, reclamo, uso de la garantía o arrepentimiento."),
    ]),
    ("medios-de-pago", "Medios de pago", [
        ("p", "En la versión de demostración no se solicita ni se procesa ningún medio de pago. En una operación real, los "
              "medios disponibles se informarán en el resumen de pago antes de confirmar, el cobro se hará a través de un "
              "procesador de pagos autorizado y Woodbird no almacenará los datos de tarjetas."),
    ]),
    ("envios", "Envíos y entrega", [
        ("p", "El envío dentro de la ciudad de Resistencia tiene un costo fijo de $5.900 por pedido, que se suma al total "
              "antes de confirmar. Los pedidos se despachan dentro de los 5 días hábiles de confirmados."),
        ("p", "La entrega se hace en el domicilio que indique el consumidor, que es el lugar de cumplimiento del contrato "
              "(artículo 1109 del Código Civil y Comercial). Hasta la entrega, el riesgo de pérdida o daño de las piezas está "
              "a cargo de Woodbird, y cada pieza viaja embalada para protegerla de golpes. Si la entrega se demora más de lo "
              "informado, el consumidor puede exigir el cumplimiento, aceptar otro producto equivalente o rescindir el "
              "contrato con derecho a la restitución de lo pagado (artículo 10 bis de la Ley N° 24.240)."),
    ]),
    ("arrepentimiento", "Derecho de arrepentimiento (revocación)", [
        ("p", "Como la compra se realiza a distancia, por internet, el consumidor tiene derecho a revocar la aceptación, es "
              "decir, a arrepentirse de la compra, dentro de los diez (10) días corridos contados desde la entrega del "
              "producto o desde la celebración del contrato, lo último que ocurra (artículo 34 de la Ley N° 24.240 y "
              "artículos 1110 a 1116 del Código Civil y Comercial). Si el último día del plazo es inhábil, el plazo vence el "
              "primer día hábil siguiente."),
        ("ul", [
            "No tiene que explicar el motivo.",
            "No tiene ningún costo: los gastos de devolución de la pieza están a cargo de Woodbird (artículo 34 de la Ley "
            "N° 24.240 y artículo 1115 del Código Civil y Comercial).",
            "Es un derecho irrenunciable: ninguna cláusula puede limitarlo ni dejarlo sin efecto.",
            "Si Woodbird no le hubiera informado este derecho, el plazo para ejercerlo no se extingue (artículo 1111 del "
            "Código Civil y Comercial).",
        ]),
        ("p", "Cómo ejercerlo: use el enlace «Botón de arrepentimiento», que está en la parte superior de la página de inicio "
              "y de todas las páginas del sitio (Resolución N° 424/2020 de la Secretaría de Comercio Interior). El botón abre "
              "un correo dirigido a [" + CORREO_ARREPENTIMIENTO + "](mailto:" + CORREO_ARREPENTIMIENTO + ") con el asunto ya "
              "completo: basta con indicar el número de pedido y un medio de contacto. También puede pedirlo por mensaje "
              "directo a [@woodbird.ar en Instagram](" + INSTAGRAM + "). No hace falta registrarse ni hacer ningún otro trámite."),
        ("boton", "Solicitar el arrepentimiento por correo", MAILTO_ARREPENTIMIENTO),
        ("p", "Dentro de las 24 horas, y por el mismo medio, Woodbird le enviará un código de identificación de arrepentimiento "
              "y coordinará el retiro de la pieza en su domicilio, sin cargo. Al recibirla, le reintegrará la totalidad de lo "
              "pagado, envío incluido, por el mismo medio de pago, dentro de los 10 días corridos."),
        ("p", "La pieza debe devolverse en el estado en que se recibió, sin otro uso que el necesario para examinarla. Las "
              "piezas del catálogo no están alcanzadas por las excepciones del artículo 1116 del Código Civil y Comercial: "
              "sólo lo estaría una pieza tallada por encargo según las especificaciones del cliente, un servicio que Woodbird "
              "no ofrece actualmente."),
    ]),
    ("garantia", "Garantía", [
        ("p", "Todas las piezas tienen la garantía legal de los artículos 11 a 18 de la Ley N° 24.240 por los defectos o "
              "vicios de cualquier índole, aunque hayan sido ostensibles o manifiestos al momento de la compra, cuando afecten "
              "la identidad entre lo ofrecido y lo entregado o su correcto funcionamiento. Para las piezas nuevas, la garantía "
              "legal es de seis (6) meses desde la entrega."),
        ("p", "Además, Woodbird otorga una garantía propia que extiende la cobertura a doce (12) meses desde la entrega contra "
              "rajaduras y desprendimientos de la madera. La garantía propia se suma a la legal y no la reemplaza."),
        ("p", "Están cubiertos, entre otros:"),
        ("ul", [
            "Rajaduras o grietas que aparezcan en la madera.",
            "El desprendimiento de la pieza de su base o de su varilla, o de partes talladas.",
            "Fallas de terminación, como zonas sin pulir, astillas o restos de cera o aceite.",
            "Diferencias con lo informado: otra madera, o una medida que difiera en más de 1 cm.",
        ]),
        ("p", "No se consideran defectos las variaciones naturales de veta, tono y aroma informadas en la cláusula de productos, "
              "ni los daños causados por golpes, caídas, humedad, exposición prolongada al sol o a fuentes de calor, o por un "
              "uso distinto del decorativo."),
        ("p", "Para usar la garantía, escriba a [" + CORREO + "](mailto:" + CORREO + ") con el número de "
              "pedido y una foto del defecto. Woodbird retirará la pieza en su domicilio sin costo. Como cada pieza sería única "
              "y tallada a mano, si la reparación no es posible o no resulta satisfactoria, el consumidor puede elegir entre "
              "el cambio por otra pieza de iguales características, la devolución de lo pagado o una quita proporcional del "
              "precio (artículo 17 de la Ley N° 24.240). El tiempo que la pieza esté en reparación se suma al plazo de "
              "garantía (artículo 16)."),
    ]),
    ("propiedad-intelectual", "Propiedad intelectual", [
        ("p", "El código fuente del sitio se publica bajo la licencia GNU GPL, versión 3 o posterior, y la documentación del "
              "proyecto bajo la licencia Creative Commons Atribución-NoComercial-CompartirIgual 4.0 "
              "([detalle de licencias](https://github.com/nicorsss/Woodbird/blob/main/LICENCIA-DOCUMENTACION.md)). El usuario "
              "puede copiar y reutilizar el código y los textos respetando las condiciones de esas licencias (Ley N° 11.723 "
              "de Propiedad Intelectual)."),
        ("p", "La marca y el nombre «Woodbird» no están incluidos en esas licencias y no pueden usarse sin autorización. Las "
              "imágenes de producto generadas con inteligencia artificial se publican sin reclamo de derechos exclusivos."),
    ]),
    ("responsabilidad", "Responsabilidad", [
        ("p", "Woodbird procura que el sitio funcione en forma continua y que la información publicada sea correcta, pero no "
              "puede garantizar que esté disponible sin interrupciones por causas ajenas, como fallas del proveedor de "
              "alojamiento o de la conexión o el dispositivo del usuario. Tampoco es responsable por el contenido de los sitios "
              "de terceros a los que se acceda mediante enlaces."),
        ("p", "Ninguna cláusula de estos términos limita la responsabilidad de Woodbird frente al consumidor por los daños "
              "derivados del producto o del servicio (artículo 40 de la Ley N° 24.240) ni restringe los derechos que la ley "
              "le reconoce. Las cláusulas que lo hicieran se tienen por no convenidas (artículo 37 de la Ley N° 24.240 y "
              "artículo 988 del Código Civil y Comercial)."),
    ]),
    ("datos-personales", "Protección de datos personales", [
        ("p", "Los datos que se ingresan para comprar se tratan según la [Política de privacidad](politica-privacidad.html) "
              "(Ley N° 25.326). Mientras el sitio sea una demostración, no se envían a ningún servidor ni se guardan: se "
              "procesan sólo en su navegador. El carrito tampoco se guarda y se vacía al cerrar o recargar la página."),
    ]),
    ("interpretacion", "Interpretación", [
        ("p", "Estos términos se interpretan en el sentido más favorable al consumidor y, si hay dudas sobre el alcance de una "
              "obligación, se adopta la que le resulte menos gravosa (artículos 3 y 37 de la Ley N° 24.240 y artículos 1094 "
              "y 1095 del Código Civil y Comercial). Si una cláusula fuera declarada nula, el resto mantiene su validez."),
    ]),
    ("reclamos", "Consultas, reclamos y jurisdicción", [
        ("p", "Para consultas o reclamos, escriba a [" + CORREO + "](mailto:" + CORREO + ") o por mensaje directo a [@woodbird.ar en Instagram](" + INSTAGRAM + "). Woodbird "
              "responderá dentro de los 5 días hábiles. El consumidor también puede presentar su reclamo, sin costo:"),
        ("ul", [
            "En la Ventanilla Única Federal de la Dirección Nacional de Defensa del Consumidor y Arbitraje del Consumo, "
            "mediante el enlace «[" + TEXTO_VENTANILLA + "](" + VENTANILLA + ")» que figura al pie de todas las páginas "
            "(Resolución N° 274/2021 de la Secretaría de Comercio Interior).",
            "Ante la autoridad de aplicación de la Ley N° 24.240 en la provincia del Chaco o en la jurisdicción de su domicilio.",
            "En el Servicio de Conciliación Previa en las Relaciones de Consumo (COPREC), creado por la Ley N° 26.993.",
        ]),
        ("p", "Este contrato se rige por las leyes de la República Argentina. Son competentes los tribunales del domicilio real "
              "del consumidor, y cualquier pacto que establezca otra jurisdicción se tiene por no escrito (artículo 1109 del "
              "Código Civil y Comercial)."),
    ]),
    ("modificaciones", "Modificaciones de estos términos", [
        ("p", "Woodbird puede actualizar estos términos. Cada versión indica su número y su fecha de vigencia. Los cambios se "
              "aplican sólo a las compras posteriores a su publicación: cada pedido se rige por la versión vigente al momento "
              "de confirmarlo."),
        ("p", f"Versión {VERSION}, vigente desde el {VIGENCIA}."),
    ]),
]

NUMERO = {id_: i for i, (id_, _, _) in enumerate(CLAUSULAS, start=1)}

# ---------------------------------------------------------------------------
# Página web
# ---------------------------------------------------------------------------
ENLACE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def a_html(texto):
    partes, ultimo = [], 0
    for m in ENLACE.finditer(texto):
        partes.append(html.escape(texto[ultimo:m.start()], quote=False))
        partes.append(f'<a href="{html.escape(m.group(2))}">{html.escape(m.group(1), quote=False)}</a>')
        ultimo = m.end()
    partes.append(html.escape(texto[ultimo:], quote=False))
    return "".join(partes)


def a_texto(texto):
    return ENLACE.sub(r"\1", texto)


def seccion_html(id_, titulo, bloques):
    n = NUMERO[id_]
    lineas = [f'      <section id="{id_}" aria-labelledby="{id_}-titulo">',
              f'        <h2 id="{id_}-titulo">{n}. {html.escape(titulo)}</h2>']
    for bloque in bloques:
        if bloque[0] == "p":
            lineas.append(f"        <p>{a_html(bloque[1])}</p>")
        elif bloque[0] == "ul":
            lineas.append("        <ul>")
            lineas += [f"          <li>{a_html(item)}</li>" for item in bloque[1]]
            lineas.append("        </ul>")
        elif bloque[0] == "boton":
            lineas.append(f'        <p><a href="{html.escape(bloque[2])}" class="boton">{html.escape(bloque[1])}</a></p>')
    lineas.append("      </section>")
    return "\n".join(lineas)


def pagina():
    indice = "\n".join(
        f'          <li><a href="#{id_}">{NUMERO[id_]}. {html.escape(t)}</a></li>' for id_, t, _ in CLAUSULAS)
    secciones = "\n\n".join(seccion_html(*c) for c in CLAUSULAS)
    return f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Términos y condiciones de uso y de compra de Woodbird, con el derecho de arrepentimiento y la garantía de la Ley N° 24.240.">
  <title>Términos y condiciones · Woodbird</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="css/estilos.css">
</head>
<body>

  <!-- Página generada por herramientas/terminos.py (fuera del repositorio), que también genera
       docs/sprint-3/01_Terminos_y_Condiciones.docx: si se modifica, cambiar la fuente y regenerar. -->

  <header>
    <a href="index.html" class="marca">Woodbird</a>
    <a href="#arrepentimiento" class="arrepentimiento">Botón de arrepentimiento</a>
  </header>

  <nav aria-label="Navegación principal">
    <ul>
      <li><a href="index.html#inicio">Inicio</a></li>
      <li><a href="index.html#catalogo">Catálogo</a></li>
      <li><a href="index.html#carrito">Carrito</a></li>
      <li><a href="index.html#checkout">Cuenta</a></li>
    </ul>
  </nav>

  <main>
    <article class="documento-legal" aria-labelledby="titulo-terminos">
      <header>
        <h1 id="titulo-terminos">Términos y condiciones</h1>
        <p>Condiciones de uso del sitio y de compra, conforme a la Ley N° 24.240 de Defensa del Consumidor y al Código Civil y Comercial de la Nación.</p>
        <p><small>Versión {VERSION} · Vigente desde el <time datetime="{VIGENCIA_ISO}">{VIGENCIA}</time></small></p>
      </header>

      <nav aria-label="Contenido de los términos">
        <h2>Contenido</h2>
        <ol>
{indice}
        </ol>
      </nav>

{secciones}
    </article>
  </main>

  <footer>
    <p><strong>Woodbird</strong> · Aves decorativas inspiradas en el tallado en maderas nativas del Chaco.</p>
    <address>
      Resistencia, Chaco, Argentina ·
      <a href="mailto:{CORREO}">{CORREO}</a> ·
      <a href="{INSTAGRAM}">Instagram @woodbird.ar</a>
    </address>
    <ul>
      <li><a href="declaracion-ia.html">Declaración ética y transparencia de IA</a></li>
      <li><a href="politica-privacidad.html">Política de privacidad</a></li>
      <li><a href="terminos-y-condiciones.html" aria-current="page">Términos y condiciones</a></li>
      <li><a href="{VENTANILLA}">{TEXTO_VENTANILLA}</a></li>
    </ul>
    <p><small>© 2026 Reiss Jorge Nicolás · Proyecto académico, IES «René Favaloro»</small></p>
    <p><small>
      Código bajo licencia <a href="https://github.com/nicorsss/Woodbird/blob/main/LICENSE" rel="license">GNU GPL v3 o posterior</a>.
      Documentación bajo <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es" rel="license">CC BY-NC-SA 4.0</a>.
      La marca «Woodbird» no está incluida en estas licencias
      (<a href="https://github.com/nicorsss/Woodbird/blob/main/LICENCIA-DOCUMENTACION.md">detalle de licencias</a>).
    </small></p>
  </footer>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Documento .docx (mismo formato que la Política de privacidad del Sprint 2)
# ---------------------------------------------------------------------------
VERDE = RGBColor(0x2F, 0x4B, 0x3C)

FICHA = [
    ("Materia", "Legislación Informática (LI)"),
    ("Actividad", "Sprint 3 — Tareas 3.7 y 3.8: Términos y Condiciones de uso y compra, y aplicación de la Ley N° 24.240"),
    ("Rol", "Compliance Officer"),
    ("Startup", "Woodbird — Aves decorativas de madera"),
    ("Autor", "Reiss Jorge Nicolás"),
    ("Docente", "Ibañez Erick"),
    ("Fecha", VIGENCIA),
]

MARCO = [
    ("Ley N° 24.240, arts. 1 a 4", "Relación de consumo. Deber de información cierta, clara y detallada.",
     "Cláusulas 1 y 4: identificación del proveedor y ficha de cada pieza (madera, medida, precio, variaciones naturales)."),
    ("Ley N° 24.240, arts. 7 y 8", "La oferta obliga mientras se difunde; las precisiones de la publicidad integran el contrato.",
     "Cláusulas 4 y 5: precio vigente mientras se publica; las imágenes con IA son ilustrativas y rige la descripción."),
    ("Ley N° 24.240, art. 10 bis", "Opciones del consumidor ante el incumplimiento del proveedor.",
     "Cláusula 8: demora en la entrega."),
    ("Ley N° 24.240, arts. 11 a 18", "Garantía legal: 6 meses para cosas muebles nuevas, reparación, sustitución o devolución.",
     "Cláusula 10: garantía legal más garantía propia de 12 meses contra rajaduras."),
    ("Ley N° 24.240, art. 34", "Revocación de la aceptación en ventas a distancia: 10 días corridos, sin gastos, irrenunciable.",
     "Cláusula 9 y botón de arrepentimiento."),
    ("Ley N° 24.240, arts. 37, 38 y 40", "Cláusulas abusivas no convenidas; contratos de adhesión; responsabilidad por daños.",
     "Cláusulas 12 y 14: ninguna limitación alcanza los derechos del consumidor."),
    ("CCyC, arts. 984 a 989", "Contratos celebrados por adhesión: cláusulas claras, completas y autosuficientes.",
     "Cláusula 1: texto publicado en forma permanente, en lenguaje llano y sin reenvíos a textos no accesibles."),
    ("CCyC, arts. 1094, 1095 y 1106 a 1109", "Interpretación pro consumidor; contratos por medios electrónicos; lugar de cumplimiento y jurisdicción.",
     "Cláusulas 1, 8, 14 y 15."),
    ("CCyC, arts. 1110 a 1116", "Revocación en contratos a distancia: plazo, deber de informar, efectos, gastos y excepciones.",
     "Cláusula 9."),
    ("Res. SCI N° 424/2020", "Botón de arrepentimiento: enlace visible desde la página de inicio, sin registración; código de identificación en 24 h.",
     "Enlace «Botón de arrepentimiento» en el encabezado de todas las páginas."),
    ("Res. SCI N° 274/2021", "Enlace obligatorio a la Ventanilla Única Federal de reclamos.",
     "Enlace «Defensa de las y los Consumidores. Para reclamos ingrese aquí» en el pie de todas las páginas."),
    ("Ley N° 26.331 y CITES, Apéndice II", "Protección de los bosques nativos; el comercio de palo santo exige permisos.",
     "Cláusula 2: las piezas son diseños ficticios. Si se produjeran, sólo con madera de origen legal y trazable."),
    ("Ley N° 26.993", "Servicio de Conciliación Previa en las Relaciones de Consumo (COPREC).", "Cláusula 15."),
    ("Ley N° 25.326", "Protección de datos personales.", "Cláusula 13: remite a la Política de privacidad (Sprint 2)."),
    ("Ley N° 11.723", "Propiedad intelectual.", "Cláusula 11: licencias GPL y CC BY-NC-SA; la marca queda excluida."),
]

REVOCACION = [
    ("Plazo de 10 días corridos desde la entrega o la celebración, lo último que ocurra", "LDC art. 34; CCyC art. 1110",
     "Cláusula 9. Se recuerda en el aviso junto a «Ir al pago» y en el mensaje de confirmación del pedido."),
    ("Informar el derecho en forma clara antes y en el documento de la venta", "LDC art. 34; CCyC art. 1111",
     "Aviso en el checkout, cláusula 9 y mensaje de confirmación con el número de pedido."),
    ("Sin gastos para el consumidor", "LDC art. 34; CCyC art. 1115",
     "Retiro de la pieza a cargo de Woodbird y reintegro total, envío incluido."),
    ("Irrenunciable", "LDC art. 34; CCyC art. 1110", "Cláusula 9: ninguna cláusula puede limitarlo."),
    ("Enlace de acceso directo, visible y destacado desde la página de inicio", "Res. SCI 424/2020",
     "«Botón de arrepentimiento» en el encabezado, visible en la primera pantalla en todos los anchos."),
    ("Sin registración previa ni otro trámite", "Res. SCI 424/2020",
     "El botón abre un correo con el asunto completo; el sitio no tiene cuentas de usuario."),
    ("Código de identificación dentro de las 24 h, por el mismo medio", "Res. SCI 424/2020",
     "Cláusula 9: respuesta por correo electrónico."),
]

GARANTIA = [
    ("Plazo", "6 meses desde la entrega para cosas muebles nuevas (art. 11).",
     "6 meses de garantía legal más garantía propia de 12 meses contra rajaduras y desprendimientos."),
    ("Qué cubre", "Vicios o defectos, aun ostensibles, que afecten la identidad entre lo ofrecido y lo entregado o el funcionamiento (art. 11).",
     "Defectos propios de una talla en madera: rajaduras, desprendimientos, fallas de terminación, otra madera u otra medida."),
    ("Información previa", "Deber de información (art. 4).",
     "Las variaciones naturales de veta, tono y aroma se informan antes de comprar y no son defectos."),
    ("Reparación no satisfactoria", "Sustitución, devolución del importe o quita proporcional, a elección del consumidor (art. 17).",
     "Igual; como cada pieza es única, la sustitución es por otra de iguales características."),
    ("Prolongación", "El tiempo sin uso por la reparación se suma al plazo (art. 16).", "Cláusula 10."),
    ("Responsables", "Responsabilidad solidaria de productores, importadores, distribuidores y vendedores (art. 13).",
     "Woodbird talla y vende: es el único responsable frente al consumidor."),
]

COHERENCIA = [
    ("1. Aceptación", "Para comprar hay que aceptar los términos.",
     "index.html: casilla #terminos con required; js/checkout.js la valida con reportValidity()."),
    ("4. Sin stock", "Las piezas sin stock no se pueden agregar.",
     "js/catalogo.js deshabilita el botón si stock es false; js/carrito.js agregar() rechaza esas piezas."),
    ("4. Imágenes con IA", "Cada imagen lleva el sello «Imagen con IA».",
     "js/catalogo.js, figura(): el sello se genera en todas las tarjetas."),
    ("5. Precio final y envío informado", "El envío se informa antes de confirmar.",
     "js/carrito.js, resumen(): subtotal, envío ($5.900) y total, visibles en el carrito y en el checkout."),
    ("6. Hasta 10 unidades", "Tope por pieza.", "js/carrito.js, constante MAXIMO; el campo corrige valores fuera de rango."),
    ("6. Verificación previa", "No se confirma con el carrito vacío ni con datos incoherentes.",
     "js/checkout.js: bloqueo con carrito vacío y reglas de nombre, correo, teléfono y código postal."),
    ("6 y 9. Número de pedido y recordatorio", "La confirmación identifica el pedido y recuerda el arrepentimiento.",
     "js/checkout.js: número WB-XXXXXX y aviso de 10 días en el mensaje de confirmación."),
    ("9. Botón de arrepentimiento", "Acceso directo desde la página de inicio.",
     "Encabezado de index.html, politica-privacidad.html y terminos-y-condiciones.html."),
    ("13. Datos personales", "Los datos no salen del navegador.",
     "La compra no hace peticiones de red (verificado por pruebas/responsive.mjs en 11 anchos)."),
    ("15. Reclamos", "Enlace a la Ventanilla Única Federal.", "Pie de las tres páginas del sitio."),
]


def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def texto_celda(celda, texto, negrita=False, color=None):
    p = celda.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(texto)
    r.bold = negrita
    r.font.size = Pt(9)
    if color:
        r.font.color.rgb = color


def tabla(doc, encabezados, filas, anchos):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    for celda, enc in zip(t.rows[0].cells, encabezados):
        sombrear(celda, "2F4B3C")
        texto_celda(celda, enc, negrita=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    for fila in filas:
        celdas = t.add_row().cells
        for i, (celda, valor) in enumerate(zip(celdas, fila)):
            texto_celda(celda, valor, negrita=(i == 0))
    # Sin esto Word ajusta las columnas al contenido e ignora los anchos
    t.autofit = False
    for columna, ancho in zip(t.columns, anchos):
        columna.width = Inches(ancho)
    for fila in t.rows:
        for celda, ancho in zip(fila.cells, anchos):
            celda.width = Inches(ancho)
    doc.add_paragraph()
    return t


def viñeta(doc, negrita, resto):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    if negrita:
        p.add_run(negrita + " ").bold = True
    p.add_run(resto)


def documento():
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)
    for nombre in ("Heading 1", "Heading 2"):
        estilo = doc.styles[nombre]
        estilo.font.name = "Calibri"
        estilo.font.color.rgb = VERDE

    p = doc.add_paragraph()
    r = p.add_run("TÉRMINOS Y CONDICIONES DE USO Y COMPRA")
    r.bold = True
    r.font.size = Pt(18)
    r.font.color.rgb = VERDE
    p = doc.add_paragraph()
    r = p.add_run("Woodbird — Aves decorativas de madera")
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    t = doc.add_table(rows=0, cols=2)
    t.style = "Table Grid"
    for clave, valor in FICHA:
        c = t.add_row().cells
        sombrear(c[0], "E3EBE5")
        texto_celda(c[0], clave, negrita=True)
        texto_celda(c[1], valor)
    for fila in t.rows:
        fila.cells[0].width, fila.cells[1].width = Inches(1.4), Inches(5.1)
    doc.add_paragraph()

    doc.add_heading("1. Objeto del documento", level=1)
    doc.add_paragraph(
        "Este documento contiene el contrato informático de adhesión de la plataforma web Woodbird (Tarea 3.7) y "
        "fundamenta cómo se aplican en él las normas de Defensa del Consumidor de la Ley N° 24.240, en particular el "
        "derecho de revocación o arrepentimiento y la garantía de los artículos comercializados (Tarea 3.8).")
    doc.add_paragraph(
        "El texto de la sección 3 es el mismo que se publica en el sitio, en la página terminos-y-condiciones.html, "
        "enlazada desde el pie de todas las páginas y desde la casilla de aceptación del checkout. Ambos se generan desde "
        "una misma fuente, para que no puedan diferir.")

    doc.add_heading("2. Marco normativo aplicable", level=1)
    tabla(doc, ["Norma", "Qué establece", "Aplicación en Woodbird"], MARCO, [1.5, 2.5, 2.5])

    doc.add_heading("3. Texto de los Términos y Condiciones", level=1)
    for id_, titulo, bloques in CLAUSULAS:
        doc.add_heading(f"{NUMERO[id_]}. {titulo}", level=2)
        for bloque in bloques:
            if bloque[0] == "p":
                doc.add_paragraph(a_texto(bloque[1]))
            elif bloque[0] == "ul":
                for item in bloque[1]:
                    viñeta(doc, None, a_texto(item))
            elif bloque[0] == "boton":
                p = doc.add_paragraph()
                r = p.add_run(f"[Botón en la página: «{bloque[1]}», que abre un correo a {CORREO_ARREPENTIMIENTO}]")
                r.italic = True

    doc.add_heading("4. Aplicación de la Ley N° 24.240 de Defensa del Consumidor", level=1)
    doc.add_heading("4.1. Derecho de revocación o arrepentimiento", level=2)
    doc.add_paragraph(
        "La compra en Woodbird es una contratación a distancia: el consumidor no ve la pieza antes de comprarla. Por eso la "
        "ley le reconoce el derecho de arrepentirse sin dar motivos. Cada requisito legal se cumple así:")
    tabla(doc, ["Requisito", "Fuente", "Cómo se cumple en Woodbird"], REVOCACION, [2.3, 1.5, 2.7])
    doc.add_heading("4.2. Garantía de los artículos comercializados", level=2)
    doc.add_paragraph(
        "Las aves son cosas muebles no consumibles y nuevas, por lo que tienen la garantía legal de seis meses. Woodbird "
        "suma una garantía propia, que la ley permite (art. 11: las partes pueden convenir un plazo mayor), pensada para el "
        "riesgo principal de una talla en madera nativa: que la pieza se raje al cambiar de clima.")
    tabla(doc, ["Aspecto", "Ley N° 24.240", "Woodbird"], GARANTIA, [1.3, 2.6, 2.6])

    doc.add_heading("5. Coherencia entre el contrato y el software", level=1)
    doc.add_paragraph(
        "El criterio integrador del Sprint 3 pide coherencia técnica entre la interacción del software y las cláusulas "
        "legales. Cada promesa del contrato está respaldada por el código del sitio:")
    tabla(doc, ["Cláusula", "Qué promete", "Dónde lo cumple el código"], COHERENCIA, [1.5, 2.2, 2.8])

    doc.add_heading("6. Publicación en el sitio", level=1)
    viñeta(doc, "Página de los términos.", "terminos-y-condiciones.html, con el texto completo de la sección 3 y un índice de cláusulas.")
    viñeta(doc, "Enlace permanente.", "En el pie de todas las páginas, junto a la Política de privacidad y la Declaración ética de IA.")
    viñeta(doc, "Botón de arrepentimiento.", "En el encabezado de todas las páginas; lleva a la cláusula 9 y a su botón de correo.")
    viñeta(doc, "Ventanilla Única Federal.", "Enlace «" + TEXTO_VENTANILLA + "» en el pie de todas las páginas.")
    viñeta(doc, "Checkout.", "Casilla obligatoria de aceptación de los términos, aviso del plazo de arrepentimiento junto "
                              "al botón «Ir al pago» y recordatorio en el mensaje de confirmación.")

    doc.add_heading("7. Requisitos pendientes antes de una operación real", level=1)
    doc.add_paragraph("Mientras Woodbird funcione como simulación no hay ventas. Si el proyecto pasara a operar, antes del "
                      "primer pedido habría que:")
    for item in [
        "Completar los datos de identificación del proveedor: razón social, CUIT y domicilio legal.",
        "Registrar un dominio propio y habilitar casillas de contacto y de arrepentimiento, con un responsable que responda dentro de las 24 h.",
        "Contratar el transporte y el seguro para los retiros por arrepentimiento y por garantía.",
        "Definir los medios de pago y el procesador, y el procedimiento de reintegro.",
        "Publicar una nueva versión de estos términos e informar el cambio en el sitio.",
    ]:
        viñeta(doc, None, item)
    return doc


if __name__ == "__main__":
    (RAIZ / "terminos-y-condiciones.html").write_text(pagina(), encoding="utf-8", newline="\n")
    destino = RAIZ / "docs" / "sprint-3"
    destino.mkdir(parents=True, exist_ok=True)
    documento().save(destino / "01_Terminos_y_Condiciones.docx")
    print("Generados terminos-y-condiciones.html y docs/sprint-3/01_Terminos_y_Condiciones.docx")
