# Campaña de Instagram del Sprint 3 (Tarea 3.5): genera las piezas visuales y el documento.
#   sitio/docs/sprint-3/instagram/*.png            (piezas listas para publicar)
#   sitio/docs/sprint-3/05_Campana_de_Instagram.docx
# Uso: python herramientas/campana_instagram.py   (requiere Node 22 y Chrome)

import json
import subprocess
from pathlib import Path

from docx.shared import Inches, Pt

from gestion_sprint3 import nuevo
from terminos import tabla, viñeta

AQUI = Path(__file__).resolve().parent
DOCS = AQUI.parent / "sitio" / "docs" / "sprint-3"
SALIDA = DOCS / "instagram"
HTML = AQUI / "campana_html"

SITIO = "https://nicorsss.github.io/Woodbird/"
CAMPANA = "sin_talar"


def utm(contenido, ancla="#catalogo"):
    return f"{SITIO}?utm_source=instagram&utm_medium=social&utm_campaign={CAMPANA}&utm_content={contenido}{ancla}"


# Colores de cada madera, los mismos de los wireframes del Sprint 1
MADERAS = {
    "palo santo": ("#47542F", "#5C6B3C", "#C9A55C"),
    "algarrobo": ("#8A6A34", "#A8823F", "#5C6B3C"),
    "quebracho": ("#C4BFA6", "#DCD6BC", "#47542F"),
}


def ave(madera, ancho, giro=-8, base="#CDBE8F"):
    cola, cuerpo, pico = MADERAS[madera]
    return f"""<svg viewBox="0 0 130 100" width="{ancho}" role="img" aria-label="Ave en {madera}">
  <ellipse cx="65" cy="94" rx="22" ry="4" fill="{base}"/>
  <rect x="63" y="74" width="4" height="19" fill="#8A7340"/>
  <g transform="rotate({giro} 60 48)">
    <polygon points="28,46 8,29 16,62" fill="{cola}"/>
    <ellipse cx="58" cy="50" rx="30" ry="21" fill="{cuerpo}"/>
    <ellipse cx="61" cy="53" rx="15" ry="8" fill="{cola}"/>
    <circle cx="83" cy="33" r="15" fill="{cuerpo}"/>
    <polygon points="96,30 111,36 96,42" fill="{pico}"/>
    <circle cx="89" cy="29" r="2" fill="#191E14"/>
  </g>
</svg>"""


SELLO = '<span class="sello">Imagen con IA</span>'

ESTILO = """
:root { --corteza:#191E14; --duramen:#47542F; --musgo:#84955F; --albura:#E7D9AE; --arena:#F4EEDC; --tiza:#FCFAF3; --resina:#985E26; --gris:#6B6959; }
* { box-sizing:border-box; margin:0; }
html, body { width:100%; height:100%; overflow:hidden; }
body { font-family:"Archivo",sans-serif; color:var(--corteza); background:var(--arena); }
.lienzo { position:relative; width:100%; height:100%; padding:88px 84px; display:flex; flex-direction:column; gap:36px; }
h1, h2 { font-family:"Fraunces",serif; font-weight:700; line-height:1.04; letter-spacing:-0.01em; }
h1 { font-size:112px; } h2 { font-size:84px; }
.kicker { font-size:30px; letter-spacing:0.16em; text-transform:uppercase; color:var(--musgo); font-weight:500; }
.texto { font-size:40px; line-height:1.4; max-width:880px; }
.sello { position:absolute; top:44px; left:44px; padding:8px 22px; border-radius:100px; background:var(--corteza); color:var(--albura); font-size:28px; font-weight:500; }
.boton { align-self:flex-start; padding:26px 48px; border-radius:100px; background:var(--duramen); color:var(--tiza); font-size:38px; font-weight:600; }
.boton.claro { background:var(--albura); color:var(--corteza); }
.marca { position:absolute; bottom:52px; left:84px; right:84px; display:flex; justify-content:space-between; font-size:28px; color:var(--gris); }
.oscuro { background:var(--corteza); color:var(--albura); } .oscuro .marca { color:var(--musgo); }
.verde { background:var(--duramen); color:var(--tiza); } .verde .marca, .verde .kicker { color:var(--albura); }
.albura { background:var(--albura); }
.centro { align-items:center; justify-content:center; text-align:center; }
.precio { font-size:64px; font-weight:600; color:var(--resina); }
.ficha { font-size:40px; color:var(--gris); }
.fila { display:flex; gap:28px; }
.tarjeta { flex:1; background:var(--albura); border-radius:28px; display:flex; flex-direction:column; align-items:center; padding:36px 12px 28px; gap:12px; font-size:30px; font-weight:500; color:var(--corteza); }
.lista { display:flex; flex-direction:column; gap:34px; }
.item { display:flex; gap:32px; align-items:flex-start; }
.item .num { flex:none; width:92px; height:92px; border-radius:50%; background:var(--duramen); color:var(--tiza); font-family:"Fraunces",serif; font-size:52px; font-weight:700; display:flex; align-items:center; justify-content:center; }
.item strong { display:block; font-family:"Fraunces",serif; font-size:52px; line-height:1.1; margin-bottom:6px; }
.item span { font-size:34px; line-height:1.35; color:var(--gris); }
.nota { font-size:30px; color:var(--gris); }
.item .cifra { flex:none; width:150px; font-family:"Fraunces",serif; font-size:110px; font-weight:700; color:var(--duramen); line-height:0.9; text-align:center; }
.reserva { margin-top:auto; margin-bottom:180px; align-self:center; width:640px; height:150px; }
"""


def pagina(cuerpo, clase="", aviso="Diseño ficticio · Tienda de demostración"):
    return f"""<!DOCTYPE html><html lang="es-AR"><head><meta charset="UTF-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap">
<style>{ESTILO}</style></head><body class="{clase}"><div class="lienzo {clase}">{cuerpo}
<div class="marca"><span>@woodbird.ar</span><span>{aviso}</span></div></div></body></html>"""


FEED, HISTORIA = (1080, 1350), (1080, 1920)
HASHTAGS = "#Woodbird #AvesDelChaco #MaderasDelChaco #TripleImpacto #ImagenConIA"

# id, formato, tamaño, pilar, html, texto de la publicación, CTA, utm_content (o None)
PIEZAS = [
    ("P1", "Imagen única", FEED, "Transparencia y marca", pagina(f"""
{SELLO}
<div style="margin-top:70px"><h1>Abrimos la tienda</h1></div>
<p class="texto">Doce aves del Chaco, diseñadas con inteligencia artificial. Sin talar un solo árbol.</p>
<div class="fila">
  <div class="tarjeta">{ave("palo santo", 250)}Palo santo</div>
  <div class="tarjeta">{ave("algarrobo", 250, -4)}Algarrobo</div>
  <div class="tarjeta">{ave("quebracho", 250, -12)}Quebracho</div>
</div>
<span class="boton" style="margin-top:auto;margin-bottom:90px">Ver catálogo · link en bio</span>"""),
     "Abrimos Woodbird 🪶 Doce aves inspiradas en el tallado en palo santo, algarrobo y quebracho del Chaco. Todas son "
     "diseños generados con inteligencia artificial: no talamos ni un árbol para hacerlas. Elegí la tuya en el catálogo.",
     "Mirá el catálogo: link en la bio", "p1_lanzamiento"),

    ("P2-1", "Carrusel · lámina 1 de 5", FEED, "Maderas y territorio", pagina("""
<p class="kicker">Maderas del Chaco · 1/5</p>
<h1 style="margin-top:auto">Por qué no talamos ni un palo santo</h1>
<p class="texto" style="margin-bottom:120px;color:var(--musgo)">Deslizá →</p>""", "oscuro"),
     "El palo santo es una especie protegida del bosque chaqueño. Te contamos por qué nuestras aves existen sólo como "
     "diseños y qué significa eso para el monte. Deslizá 👉",
     "Última lámina: «Conocé las 12 aves · link en bio»", "p2_maderas"),
    ("P2-2", "Carrusel · lámina 2 de 5", FEED, "Maderas y territorio", pagina("""
<p class="kicker" style="color:var(--duramen)">Maderas del Chaco · 2/5</p>
<h2 style="margin-top:40px">El palo santo está protegido</h2>
<p class="texto"><em>Gonopterodendron sarmientoi</em> crece sólo en el Gran Chaco. Su comercio está regulado por el
Apéndice II de la CITES, y los bosques donde vive, por la Ley 26.331 de bosques nativos.</p>
<div style="margin-top:auto;margin-bottom:90px;align-self:flex-end">""" + ave("palo santo", 360) + "</div>"),
     None, None, None),
    ("P2-3", "Carrusel · lámina 3 de 5", FEED, "Maderas y territorio", pagina(f"""
{SELLO}
<p class="kicker" style="color:var(--duramen);margin-top:70px">Maderas del Chaco · 3/5</p>
<h2>Por eso, cada ave de Woodbird es un diseño</h2>
<p class="texto">La generamos con inteligencia artificial, inspirada en el tallado tradicional. Sin tala, sin aserrín
y sin envíos.</p>
<div style="margin-top:auto;margin-bottom:80px;align-self:center">{ave("palo santo", 420)}</div>""", "albura"),
     None, None, None),
    ("P2-4", "Carrusel · lámina 4 de 5", FEED, "Maderas y territorio", pagina("""
<p class="kicker" style="color:var(--duramen)">Maderas del Chaco · 4/5</p>
<h2>Triple impacto</h2>
<div class="lista" style="margin-top:20px">
  <div class="item"><span class="cifra">0</span><div><strong>Ambiental</strong><span>árboles talados y kilómetros de envío para hacer el catálogo.</span></div></div>
  <div class="item"><span class="cifra">12</span><div><strong>Social</strong><span>aves que ponen en vidriera un oficio del nordeste argentino.</span></div></div>
  <div class="item"><span class="cifra">∞</span><div><strong>Económico</strong><span>un catálogo que crece sin consumir materia prima.</span></div></div>
</div>"""),
     None, None, None),
    ("P2-5", "Carrusel · lámina 5 de 5", FEED, "Maderas y territorio", pagina(f"""
<p class="kicker">Maderas del Chaco · 5/5</p>
<h1 style="margin-top:auto">Conocé las 12 aves</h1>
<p class="texto">Palo santo, algarrobo y quebracho, sin tocar el monte.</p>
<span class="boton claro" style="margin-bottom:120px">Ver catálogo · link en bio</span>""", "verde"),
     None, None, None),

    ("P3", "Imagen de producto", FEED, "Producto", pagina(f"""
{SELLO}
<div style="margin-top:60px;align-self:center">{ave("palo santo", 640)}</div>
<div><h2>Cardenal</h2><p class="ficha">Palo santo · 22 cm</p></div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:70px">
  <span class="precio">$28.400</span><span class="boton">Agregalo · link en bio</span></div>""", "albura"),
     "Cardenal · Palo santo · 22 cm. Copete marcado a gubia y pecho pulido, en un diseño generado con IA. $28.400 en "
     "nuestra tienda de demostración. ¿Lo sumás a tu carrito?",
     "Agregalo desde el link en la bio", "p3_cardenal"),

    ("P4", "Imagen de producto", FEED, "Producto", pagina(f"""
{SELLO}
<div style="margin-top:60px;align-self:center">{ave("algarrobo", 640, -4)}</div>
<div><h2>Hornero</h2><p class="ficha">Algarrobo · 18 cm</p></div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:70px">
  <span class="precio">$19.700</span><span class="boton">Agregalo · link en bio</span></div>""", "albura"),
     "Hornero · Algarrobo · 18 cm. En actitud de canto, con las vetas oscuras siguiendo la curva del lomo. Un diseño "
     "generado con IA, $19.700 en la tienda de demostración.",
     "Agregalo desde el link en la bio", "p4_hornero"),

    ("P5", "Imagen única", FEED, "Transparencia y marca", pagina("""
<p class="kicker" style="color:var(--duramen)">Cómo comprar</p>
<h2>Tu ave en 3 pasos</h2>
<div class="lista">
  <div class="item"><span class="num">1</span><div><strong>Elegí</strong><span>Agregá tus aves al carrito: ves el envío y el total antes de seguir.</span></div></div>
  <div class="item"><span class="num">2</span><div><strong>Completá</strong><span>Tus datos se usan sólo en tu navegador: no se envían ni se guardan.</span></div></div>
  <div class="item"><span class="num">3</span><div><strong>Confirmá</strong><span>Recibís un número de pedido. Tenés 10 días para arrepentirte, sin costo.</span></div></div>
</div>
<span class="boton" style="margin-top:auto;margin-bottom:90px">Probalo · link en bio</span>"""),
     "Comprar en Woodbird lleva tres pasos. Es una tienda de demostración: no se cobra nada y tus datos no salen de tu "
     "navegador. Y, como en cualquier compra online, tenés 10 días para arrepentirte con el Botón de arrepentimiento.",
     "Probalo: link en la bio", "p5_como_comprar"),

    ("H1", "Historia con encuesta", HISTORIA, "Maderas y territorio", pagina(f"""
<p class="kicker" style="margin-top:120px">Encuesta</p>
<h1>¿Cuál es tu madera?</h1>
<div class="fila" style="margin-top:40px">
  <div class="tarjeta">{ave("palo santo", 240)}Palo santo</div>
  <div class="tarjeta">{ave("algarrobo", 240, -4)}Algarrobo</div>
  <div class="tarjeta">{ave("quebracho", 240, -12)}Quebracho</div>
</div>
<div class="reserva"></div>""", "oscuro"),
     "Sticker de encuesta sobre la franja inferior libre: «Palo santo / Algarrobo / Quebracho». Sticker de enlace: "
     "«Ver las aves».", "Sticker «Ver las aves»", "h1_encuesta"),
    ("H2", "Historia de producto", HISTORIA, "Producto", pagina(f"""
{SELLO}
<p class="kicker" style="color:var(--duramen);margin-top:150px">Nuevo diseño</p>
<h1>Garza blanca</h1>
<p class="ficha">Quebracho · 34 cm · <span style="color:var(--resina);font-weight:600">$42.300</span></p>
<div style="align-self:center;margin-top:40px">{ave("quebracho", 760, -12)}</div>
<div class="reserva"></div>""", "albura"),
     "Sticker de enlace sobre la franja inferior libre: «Ver pieza».", "Sticker «Ver pieza»", "h2_garza"),
    ("H3", "Historia destacada «Sobre la IA»", HISTORIA, "Transparencia y marca", pagina("""
<p class="kicker" style="margin-top:150px">Sobre la IA</p>
<h1>¿Tus aves existen?</h1>
<p class="texto" style="font-size:48px">No como objetos: son diseños generados con inteligencia artificial, inspirados en
el tallado del Chaco. Así cuidamos el palo santo, una especie protegida.</p>
<p class="texto" style="font-size:40px;color:var(--musgo)">Cada imagen lleva el sello «Imagen con IA».</p>
<div class="reserva"></div>""", "oscuro"),
     "Sticker de enlace sobre la franja inferior libre: «Cómo trabajamos». Se fija en la historia destacada «Sobre la IA».",
     "Sticker «Cómo trabajamos»", ("h3_sobre_ia", "#inicio")),
]

# planificada, pieza, formato, motivo, publicada
CALENDARIO = [
    ("Jue 23/10", "P1 · Abrimos la tienda", "Feed", "Al crear la cuenta, antes de la entrega del Sprint 3", "Lun 27/10"),
    ("Jue 23/10", "H3 · ¿Tus aves existen?", "Historia (se fija en destacadas)", "Mismo día que P1, para explicar el uso de IA",
     "Lun 27/10; resubida el 28/10"),
    ("Jue 23/10", "P2 · Por qué no talamos ni un palo santo", "Carrusel", "Publicación central de la campaña", "Lun 27/10"),
    ("Jue 23/10", "H1 · ¿Cuál es tu madera?", "Historia con encuesta", "Interacción para el algoritmo",
     "Lun 27/10; resubida el 28/10"),
    ("Sáb 25/10", "P3 · Cardenal", "Feed (programada)", "Programada con Meta Business Suite", "Lun 27/10"),
    ("Lun 27/10", "P4 · Hornero", "Feed (programada)", "Programada con Meta Business Suite", "Lun 27/10"),
    ("Lun 27/10", "H2 · Garza blanca", "Historia con enlace", "Acompaña a P4", "Lun 27/10"),
    ("Mié 29/10", "P5 · Tu ave en 3 pasos", "Feed (programada)", "Cierra la primera semana con la conversión", "Lun 27/10"),
]


def enlace(utm_c):
    if utm_c is None:
        return ""
    return utm(*utm_c) if isinstance(utm_c, tuple) else utm(utm_c)


def generar_png():
    HTML.mkdir(exist_ok=True)
    SALIDA.mkdir(parents=True, exist_ok=True)
    lista = []
    for id_, _, (ancho, alto), _, html, *_ in PIEZAS:
        h = HTML / f"{id_}.html"
        h.write_text(html, encoding="utf-8")
        lista.append({"html": str(h), "png": str(SALIDA / f"{id_}.png"), "ancho": ancho, "alto": alto})
    (HTML / "lista.json").write_text(json.dumps(lista), encoding="utf-8")
    subprocess.run(["node", str(AQUI / "capturar.mjs"), str(HTML / "lista.json")], check=True)


def documento():
    doc = nuevo("CAMPAÑA DE MARKETING DIGITAL EN INSTAGRAM",
                "Sprint 3 — Tarea 3.5: Despliegue de la campaña «Sin talar un árbol» en Instagram",
                rol="Responsable de Negocio")
    doc.styles["Normal"].font.size = Pt(10.5)

    doc.add_heading("1. Objetivo", level=1)
    doc.add_paragraph(
        "Ejecutar la estrategia de contenidos definida en el Sprint 2 para la cuenta @woodbird.ar, con piezas que "
        "comunican el valor de triple impacto de Woodbird: aves inspiradas en el tallado en maderas nativas del Chaco, "
        "que existen sólo como diseños generados con IA para no talar palo santo, una especie protegida. Cada pieza "
        "termina en una llamada a la acción (CTA) con un enlace etiquetado con parámetros UTM, para atraer tráfico "
        "orgánico al sitio y medirlo en el panel de KPIs (Tarea 3.6).")
    doc.add_paragraph(
        "La campaña se llama «Sin talar un árbol» (utm_campaign=sin_talar) y continúa la de lanzamiento planificada en el "
        "Sprint 2. Respeta la Declaración Ética de IA: toda imagen de producto lleva el sello «Imagen con IA» y la etiqueta "
        "#ImagenConIA, y cada pieza aclara que se trata de un diseño ficticio de una tienda de demostración.")

    doc.add_heading("2. Cuenta y enlace", level=1)
    tabla(doc, ["Elemento", "Definición"], [
        ("Usuario", "@woodbird.ar (cuenta profesional, categoría Artículos de decoración)."),
        ("Biografía", "Aves decorativas inspiradas en el tallado en maderas nativas del Chaco · Palo santo · Algarrobo · "
                      "Quebracho · Diseños generados con IA, sin talar un árbol · Tienda de demostración · Mirá el catálogo 👇"),
        ("Enlace de la biografía", utm("bio")),
        ("Dominio", "Mientras woodbird.com.ar no esté registrado, los enlaces apuntan al sitio publicado en GitHub Pages."),
        ("Historias destacadas", "Maderas · Sobre la IA · Cómo comprar · Preguntas"),
    ], [1.6, 4.9])

    doc.add_heading("3. Línea editorial aplicada", level=1)
    pilares = {}
    for p in PIEZAS:
        pilares.setdefault(p[3], set()).add(p[0].split("-")[0])
    tabla(doc, ["Pilar", "Peso planificado", "Piezas de la campaña"], [
        ("Producto", "40 %", ", ".join(sorted(pilares["Producto"]))),
        ("Maderas y territorio", "35 %", ", ".join(sorted(pilares["Maderas y territorio"]))),
        ("Transparencia y marca", "25 %", ", ".join(sorted(pilares["Transparencia y marca"]))),
    ], [2.0, 1.5, 3.0])

    doc.add_heading("4. Calendario de publicación", level=1)
    doc.add_paragraph(
        "El plan era publicar cuatro piezas el 23/10, antes de la entrega del Sprint 3, y programar el resto con Meta "
        "Business Suite, a razón de tres publicaciones por semana más historias, como fija la estrategia. La cuenta se "
        "creó recién el 27/10 (riesgo R3), y ese día se publicaron las ocho piezas juntas. Se abrió con el usuario "
        "wood_bird_shop, que el 28/10 se cambió por @woodbird.ar, el que figura en las piezas. Ese mismo día se volvieron "
        "a subir H1, a la que le faltaban el sticker de encuesta y el enlace «Ver las aves», y H3. Las capturas están en "
        "la página «Evidencia de publicación en Instagram» de la carpeta.")
    tabla(doc, ["Planificada", "Pieza", "Formato", "Motivo", "Publicada"], CALENDARIO, [0.85, 1.9, 1.35, 1.5, 0.9])

    doc.add_heading("5. Piezas", level=1)
    vistas = set()
    for id_, formato, (ancho, alto), pilar, _, texto, cta, utm_c in PIEZAS:
        base = id_.split("-")[0]
        if base == "P2" and base in vistas:
            continue
        vistas.add(base)
        if base == "P2":
            doc.add_heading("P2 · Carrusel «Por qué no talamos ni un palo santo» (5 láminas)", level=2)
            tabla_img = doc.add_table(rows=1, cols=5)
            for celda, n in zip(tabla_img.rows[0].cells, range(1, 6)):
                celda.paragraphs[0].add_run().add_picture(str(SALIDA / f"P2-{n}.png"), width=Inches(1.22))
        else:
            doc.add_heading(f"{id_} · {formato}", level=2)
            doc.add_picture(str(SALIDA / f"{id_}.png"), width=Inches(2.2 if alto == 1350 else 1.6))
        filas = [("Pilar", pilar), ("Texto" if base[0] == "P" else "Indicaciones", texto + ("" if base[0] == "H" else f"\n\n{HASHTAGS}")),
                 ("Llamada a la acción", cta), ("Enlace", enlace(utm_c))]
        tabla(doc, ["Campo", "Contenido"], filas, [1.4, 5.1])

    doc.add_heading("6. Lista de control antes de publicar", level=1)
    for item in [
        "La pieza de producto lleva el sello «Imagen con IA», y el texto, la etiqueta #ImagenConIA.",
        "El precio coincide con productos.json y con el sitio publicado.",
        "El enlace lleva los parámetros UTM de la pieza y abre la sección correcta del sitio.",
        "El texto no presenta las aves como objetos físicos que se tallan o se envían (SC-06).",
        "Después de publicar, se guarda una captura con la fecha para la carpeta y para el panel de KPIs.",
    ]:
        viñeta(doc, None, item)

    doc.add_heading("7. Medición", level=1)
    doc.add_paragraph(
        "Las estadísticas de la cuenta profesional informan, por publicación, las cuentas alcanzadas, las visitas al "
        "perfil y los toques en el enlace. El parámetro utm_content identifica qué pieza originó cada visita. El sitio no "
        "usa analítica (Política de privacidad, cláusulas 8 y 9), por lo que las etapas internas del embudo se miden con "
        "pruebas de usuario. Las fórmulas, las metas y la lectura de cada indicador están en el panel de KPIs (documento "
        "06 de esta carpeta).")
    return doc


if __name__ == "__main__":
    generar_png()
    documento().save(DOCS / "05_Campana_de_Instagram.docx")
    print("Generados las piezas de docs/sprint-3/instagram/ y 05_Campana_de_Instagram.docx")
