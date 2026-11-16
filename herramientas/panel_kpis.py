# Panel de métricas de conversión del Sprint 3 (Tarea 3.6).
#   sitio/docs/sprint-3/06_Panel_de_KPIs.png    (panel visual)
#   sitio/docs/sprint-3/06_Panel_de_KPIs.docx
# Uso: python herramientas/panel_kpis.py   (requiere Node 22 y Chrome)
# Los valores son simulados: salen del embudo proyectado del Sprint 2 y de supuestos declarados.

import json
import subprocess
from pathlib import Path

from docx.shared import Inches

from gestion_sprint3 import nuevo
from terminos import sombrear, tabla, viñeta

AQUI = Path(__file__).resolve().parent
DOCS = AQUI.parent / "sitio" / "docs" / "sprint-3"
PRODUCTOS = json.loads((AQUI.parent / "sitio" / "productos.json").read_text(encoding="utf-8"))

# --- Datos simulados del primer mes (embudo del Sprint 2) -------------------
INSTAGRAM = [("Cuentas alcanzadas", 6000), ("Visitas al perfil", 360), ("Clics al sitio", 108)]
SITIO = [("Clics al sitio", 108), ("Llegan al catálogo", 65), ("Agregan al carrito", 13),
         ("Completan datos", 8), ("Compras simuladas", 3)]
SEMANAS = [("Sem. 1", 900, 14), ("Sem. 2", 1400, 24), ("Sem. 3", 1700, 32), ("Sem. 4", 2000, 38)]
INTERACCIONES = 240  # me gusta + comentarios + guardados + compartidos en el mes

# --- Supuestos del CAC teórico -------------------------------------------------
HORAS = 12           # 12 piezas del mes ≈ 1 h cada una (diseño, texto y publicación)
VALOR_HORA = 3500    # valor hora de referencia de un perfil junior de contenidos
PAUTA = 0            # campaña orgánica: sin publicidad paga
HERRAMIENTAS = 0     # las piezas se generan con el propio script y Chrome

ENVIO = 5900
con_stock = [p["precio_simulado"] for p in PRODUCTOS if p["stock"]]
TICKET = round((sum(con_stock) / len(con_stock) + ENVIO) / 100) * 100  # una pieza por pedido

alcance, visitas, clics = (v for _, v in INSTAGRAM)
compras = SITIO[-1][1]
CTR = clics / alcance * 100
CONVERSION = compras / clics * 100
COSTO = HORAS * VALOR_HORA + PAUTA + HERRAMIENTAS
CAC = round(COSTO / compras)
ENGAGEMENT = INTERACCIONES / alcance * 100
ABANDONO = (1 - compras / SITIO[2][1]) * 100
META_CAC = round(TICKET * 0.30 / 100) * 100


def pct(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",") + " %"


def pesos(n):
    return "$" + f"{n:,.0f}".replace(",", ".")


# id, nombre, fórmula, fuente, frecuencia, meta, valor, estado
ESTADOS = {"ok": ("✓", "Cumple", "#0ca30c"), "alerta": ("!", "Alerta", "#fab219"), "mal": ("✕", "No cumple", "#d03b3b")}


def semaforo(valor, verde, amarillo, menor_es_mejor=False):
    valor = round(valor, 2)  # 108 ÷ 6000 × 100 da 1,7999… en punto flotante
    if menor_es_mejor:
        return "ok" if valor <= verde else "alerta" if valor <= amarillo else "mal"
    return "ok" if valor >= verde else "alerta" if valor >= amarillo else "mal"


KPIS = [
    ("CTR (tasa de clics)", "Clics al sitio ÷ cuentas alcanzadas × 100", "Estadísticas de Instagram (toques en el enlace) y UTM",
     "Semanal", "≥ 1,8 % · alerta 1,0–1,8 % · < 1,0 %", pct(CTR), semaforo(CTR, 1.8, 1.0)),
    ("Tasa de conversión simulada", "Compras simuladas ÷ clics al sitio × 100", "Pruebas de usuario que entran por el enlace con UTM",
     "Mensual", "≥ 2,8 % · alerta 1,5–2,8 % · < 1,5 %", pct(CONVERSION), semaforo(round(CONVERSION, 1), 2.8, 1.5)),
    ("CAC teórico", "(Horas × valor hora + pauta + herramientas) ÷ clientes nuevos", "Registro de horas del equipo y supuestos declarados",
     "Mensual", f"≤ {pesos(META_CAC)} (30 % del ticket) · alerta hasta $15.000 · más", pesos(CAC), semaforo(CAC, META_CAC, 15000, True)),
    ("Tasa de interacción", "Interacciones ÷ cuentas alcanzadas × 100", "Estadísticas de Instagram", "Semanal",
     "≥ 4 % · alerta 2–4 % · < 2 %", pct(ENGAGEMENT), semaforo(ENGAGEMENT, 4, 2)),
    ("Abandono de carrito", "1 − compras ÷ sesiones que agregan al carrito", "Pruebas de usuario", "Mensual",
     "≤ 70 % · alerta 70–80 % · más de 80 %", pct(ABANDONO, 0), semaforo(ABANDONO, 70, 80, True)),
    ("Ticket promedio", "Precio medio de las piezas con stock + envío", "productos.json", "Al cambiar precios",
     "Referencia para el CAC", pesos(TICKET), None),
]

# --- Panel visual (HTML → PNG) -------------------------------------------------
TINTA, SECUNDARIA, GRILLA, SERIE, FONDO = "#191E14", "#6B6959", "#E4DCC4", "#47542F", "#FCFAF3"


def barras(titulo, filas, ancho=700):
    alto_fila, x0, ancho_barra = 64, 210, ancho - 210 - 120
    maximo = filas[0][1]
    svg = [f'<svg viewBox="0 0 {ancho} {len(filas) * alto_fila + 10}" width="100%">']
    for i, (nombre, valor) in enumerate(filas):
        y = i * alto_fila + 10
        largo = max(ancho_barra * valor / maximo, 4)
        paso = "" if i == 0 else f" · {pct(valor / filas[i - 1][1] * 100, 0)} pasa"
        svg.append(f'<text x="0" y="{y + 26}" font-size="20" fill="{TINTA}">{nombre}</text>')
        svg.append(f'<path d="M{x0},{y + 8} h{largo - 4} a4,4 0 0 1 4,4 v20 a4,4 0 0 1 -4,4 h-{largo - 4} z" fill="{SERIE}"/>')
        svg.append(f'<text x="{x0 + largo + 10}" y="{y + 27}" font-size="20" font-weight="600" fill="{TINTA}">'
                   f'{f"{valor:,}".replace(",", ".")}</text>')
        if paso:
            svg.append(f'<text x="{x0}" y="{y + 56}" font-size="16" fill="{SECUNDARIA}">{paso.strip(" ·")}</text>')
    svg.append("</svg>")
    return f'<section class="grafico"><h2>{titulo}</h2>{"".join(svg)}</section>'


def linea_ctr(ancho=700, alto=300):
    m = {"izq": 70, "der": 110, "arr": 20, "abj": 50}
    w, h = ancho - m["izq"] - m["der"], alto - m["arr"] - m["abj"]
    tope = 2.5
    xs = [m["izq"] + i * w / (len(SEMANAS) - 1) for i in range(len(SEMANAS))]
    ys = [m["arr"] + h - (c / a * 100) / tope * h for _, a, c in SEMANAS]
    meta_y = m["arr"] + h - 1.8 / tope * h
    partes = [f'<svg viewBox="0 0 {ancho} {alto}" width="100%">']
    for v in (0, 0.5, 1.0, 1.5, 2.0, 2.5):
        y = m["arr"] + h - v / tope * h
        partes.append(f'<line x1="{m["izq"]}" x2="{m["izq"] + w}" y1="{y}" y2="{y}" stroke="{GRILLA}" stroke-width="1"/>')
        partes.append(f'<text x="{m["izq"] - 12}" y="{y + 6}" font-size="16" text-anchor="end" fill="{SECUNDARIA}">{pct(v)}</text>')
    partes.append(f'<line x1="{m["izq"]}" x2="{m["izq"] + w}" y1="{meta_y}" y2="{meta_y}" stroke="{SECUNDARIA}" stroke-width="2" stroke-dasharray="6 6"/>')
    partes.append(f'<text x="{m["izq"] + w + 10}" y="{meta_y + 6}" font-size="16" fill="{SECUNDARIA}">Meta 1,8 %</text>')
    partes.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in zip(xs, ys))}" fill="none" stroke="{SERIE}" stroke-width="2.5"/>')
    for (s, a, c), x, y in zip(SEMANAS, xs, ys):
        partes.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{SERIE}" stroke="{FONDO}" stroke-width="2"/>')
        partes.append(f'<text x="{x}" y="{alto - 18}" font-size="16" text-anchor="middle" fill="{SECUNDARIA}">{s}</text>')
    s, a, c = SEMANAS[-1]
    partes.append(f'<text x="{xs[-1] + 12}" y="{ys[-1] - 12}" font-size="20" font-weight="600" fill="{TINTA}">{pct(c / a * 100)}</text>')
    partes.append("</svg>")
    return f'<section class="grafico"><h2>CTR semanal</h2>{"".join(partes)}</section>'


def ficha(nombre, valor, meta, estado):
    chip = ""
    if estado:
        icono, etiqueta, color = ESTADOS[estado]
        chip = (f'<span class="chip"><span class="punto" style="background:{color}">{icono}</span>{etiqueta}</span>')
    return f'<div class="ficha"><p class="nombre">{nombre}</p><p class="valor">{valor}</p><p class="meta">{meta}</p>{chip}</div>'


def panel_html():
    fichas = "".join([
        ficha("CTR", pct(CTR), "Meta ≥ 1,8 %", KPIS[0][6]),
        ficha("Conversión simulada", pct(CONVERSION), "Meta ≥ 2,8 %", KPIS[1][6]),
        ficha("CAC teórico", pesos(CAC), f"Meta ≤ {pesos(META_CAC)}", KPIS[2][6]),
        ficha("Ticket promedio", pesos(TICKET), "Una pieza + envío", None),
    ])
    return f"""<!DOCTYPE html><html lang="es-AR"><head><meta charset="UTF-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap">
<style>
* {{ box-sizing:border-box; margin:0; }}
body {{ width:1600px; min-height:1250px; padding:48px 56px; background:{FONDO}; color:{TINTA}; font-family:"Archivo",sans-serif; }}
header {{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:32px; }}
h1 {{ font-family:"Fraunces",serif; font-size:44px; }}
header p {{ font-size:20px; color:{SECUNDARIA}; }}
.fichas {{ display:grid; grid-template-columns:repeat(4,1fr); gap:24px; margin-bottom:32px; }}
.ficha {{ padding:24px 28px; border:1px solid {GRILLA}; border-radius:12px; background:#fff; }}
.nombre {{ font-size:20px; color:{SECUNDARIA}; }}
.valor {{ font-family:"Fraunces",serif; font-size:56px; font-weight:700; line-height:1.15; }}
.meta {{ font-size:18px; color:{SECUNDARIA}; margin-bottom:12px; }}
.chip {{ display:inline-flex; align-items:center; gap:8px; font-size:18px; font-weight:500; }}
.punto {{ width:24px; height:24px; border-radius:50%; color:#fff; font-size:15px; font-weight:700; display:inline-flex; align-items:center; justify-content:center; }}
.graficos {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:24px 48px; }}
.grafico {{ padding:24px 28px; border:1px solid {GRILLA}; border-radius:12px; background:#fff; }}
.grafico h2 {{ font-size:22px; font-weight:600; margin-bottom:16px; }}
.grafico svg {{ font-family:"Archivo",sans-serif; display:block; }}
footer {{ margin-top:20px; font-size:17px; color:{SECUNDARIA}; }}
</style></head><body>
<header><h1>Panel de KPIs · Woodbird</h1><p>Campaña «Sin talar un árbol» · Mes 1 · Valores simulados</p></header>
<div class="fichas">{fichas}</div>
<div class="graficos">
{barras("Embudo en Instagram", INSTAGRAM)}
{barras("Embudo en el sitio", SITIO)}
{linea_ctr()}
<section class="grafico"><h2>Lectura del mes</h2>
<p style="font-size:20px;line-height:1.5">El CTR llega a la meta en la semana 3. La conversión cumple, pero el CAC está en alerta:
con 3 compras, cada cliente cuesta el {round(CAC / TICKET * 100)} % del ticket. Como el contenido orgánico se reutiliza, el CAC baja
a medida que crece el alcance. La mayor fuga está entre el catálogo y el carrito (80 % no agrega): mejorarla depende de las
imágenes de producto (Sprint 4).</p></section>
</div>
<footer>Proyección del Sprint 2 con supuestos declarados. Fuentes previstas: estadísticas de Instagram y parámetros UTM; las etapas del sitio se miden con pruebas de usuario porque el sitio no usa analítica (Política de privacidad, cláusulas 8 y 9).</footer>
</body></html>"""


def generar_png():
    carpeta = AQUI / "campana_html"
    carpeta.mkdir(exist_ok=True)
    html = carpeta / "panel_kpis.html"
    html.write_text(panel_html(), encoding="utf-8")
    lista = carpeta / "lista_panel.json"
    lista.write_text(json.dumps([{"html": str(html), "png": str(DOCS / "06_Panel_de_KPIs.png"), "ancho": 1600, "alto": 1250}]),
                     encoding="utf-8")
    subprocess.run(["node", str(AQUI / "capturar.mjs"), str(lista)], check=True)


def documento():
    doc = nuevo("PANEL DE MÉTRICAS DE CONVERSIÓN (KPIs)",
                "Sprint 3 — Tarea 3.6: Definición del panel de indicadores clave de rendimiento del e-commerce",
                rol="Responsable de Negocio")
    doc.add_heading("1. Objeto", level=1)
    doc.add_paragraph(
        "Este panel define cómo se mide la eficiencia del e-commerce de Woodbird: qué indicadores se siguen, cómo se "
        "calculan, de dónde salen los datos, cada cuánto se revisan y qué valor se considera bueno. Cierra el ciclo de la "
        "campaña de Instagram (Tarea 3.5): cada pieza lleva un enlace con parámetros UTM y cada etapa del embudo tiene "
        "su indicador.")
    doc.add_paragraph(
        "Los valores del primer mes son simulados. Salen del embudo proyectado en la Estrategia de canales del Sprint 2 y "
        "de los supuestos de la sección 4. La cuenta @woodbird.ar se activó el 27/10: cuando junte una semana completa de "
        "estadísticas (Sprint 4), los valores simulados se reemplazan por los datos reales y se comparan contra estas metas.")

    doc.add_heading("2. Panel", level=1)
    doc.add_picture(str(DOCS / "06_Panel_de_KPIs.png"), width=Inches(6.5))
    doc.add_paragraph("Figura 1. Panel del mes 1. Los datos de los gráficos figuran en la sección 5 como tabla.")

    doc.add_heading("3. Indicadores", level=1)
    filas = []
    for nombre, formula, fuente, frecuencia, meta, valor, estado in KPIS:
        etiqueta = f"{ESTADOS[estado][0]} {ESTADOS[estado][1]}" if estado else "—"
        filas.append((nombre, formula, fuente, frecuencia, meta, valor, etiqueta))
    t = tabla(doc, ["KPI", "Fórmula", "Fuente", "Frecuencia", "Meta y umbrales", "Mes 1 (simulado)", "Estado"],
              filas, [0.9, 1.2, 1.1, 0.6, 1.1, 0.7, 0.6])
    for fila, kpi in zip(t.rows[1:], KPIS):
        if kpi[6]:
            sombrear(fila.cells[6], {"ok": "D9EAD3", "alerta": "FCE8B2", "mal": "F4C7C3"}[kpi[6]])

    doc.add_heading("4. CAC teórico: supuestos y cálculo", level=1)
    tabla(doc, ["Concepto", "Supuesto", "Importe"], [
        ("Producción de contenido", f"{HORAS} piezas en el mes, ≈ 1 h cada una, a {pesos(VALOR_HORA)} la hora (referencia de un perfil junior)", pesos(HORAS * VALOR_HORA)),
        ("Publicidad paga", "Campaña orgánica: la consigna pide tráfico orgánico", pesos(PAUTA)),
        ("Herramientas", "Las piezas se generan con un script propio y Chrome, sin licencias", pesos(HERRAMIENTAS)),
        ("Costo total de adquisición", "", pesos(COSTO)),
        ("Clientes nuevos", "Compras simuladas del mes (embudo del Sprint 2)", str(compras)),
        ("CAC teórico", "Costo total ÷ clientes nuevos", pesos(CAC)),
        ("Ticket promedio", f"Precio medio de las {len(con_stock)} piezas con stock + envío de {pesos(ENVIO)}", pesos(TICKET)),
        ("CAC ÷ ticket", "Proporción del ingreso que se va en conseguir al cliente", pct(CAC / TICKET * 100, 0)),
    ], [1.6, 3.6, 1.3])
    doc.add_paragraph(
        f"Lectura. Con 3 clientes en el primer mes, cada cliente cuesta el {round(CAC / TICKET * 100)} % del ticket: "
        f"el CAC queda en alerta. La meta es bajarlo a {pesos(META_CAC)} (30 % del ticket). Como el costo es casi todo de "
        "producción de contenido, que se reutiliza, el CAC baja al crecer el alcance sin producir más piezas. Con la "
        f"misma inversión, se llega a la meta con {-(-COSTO // META_CAC)} compras por mes.")

    doc.add_heading("5. Datos de los gráficos", level=1)
    tabla(doc, ["Etapa", "Volumen", "Pasa a la siguiente"], [
        (n, f"{v:,}".replace(",", "."), "—" if i == len(INSTAGRAM + SITIO[1:]) - 1 else pct((INSTAGRAM + SITIO[1:])[i + 1][1] / v * 100, 0))
        for i, (n, v) in enumerate(INSTAGRAM + SITIO[1:])
    ], [2.6, 1.6, 2.3])
    tabla(doc, ["Semana", "Cuentas alcanzadas", "Clics al sitio", "CTR"],
          [(s, f"{a:,}".replace(",", "."), str(c), pct(c / a * 100, 2)) for s, a, c in SEMANAS], [1.4, 1.8, 1.6, 1.7])

    doc.add_heading("6. Cómo se usa el panel", level=1)
    for negrita, resto in [
        ("Revisión semanal.", "Cada lunes, junto con el tablero Kanban: CTR e interacción por pieza, a partir de las "
                              "estadísticas de Instagram y el parámetro utm_content."),
        ("Revisión mensual.", "Conversión, abandono de carrito y CAC, con una ronda de pruebas de usuario que entran por el "
                              "enlace de la biografía."),
        ("Decisiones.", "Un KPI en alerta dos semanas seguidas abre una acción en el tablero. Por ejemplo, un CTR bajo "
                        "lleva a cambiar el texto de la CTA, y un abandono alto, a revisar el carrito."),
        ("Privacidad.", "El sitio no instala analítica ni cookies. Medir dentro del sitio con una herramienta exigiría "
                        "antes una nueva versión de la Política de privacidad y el consentimiento del usuario."),
    ]:
        viñeta(doc, negrita, resto)
    return doc


if __name__ == "__main__":
    generar_png()
    documento().save(DOCS / "06_Panel_de_KPIs.docx")
    print(f"CTR {pct(CTR)} · conversión {pct(CONVERSION)} · CAC {pesos(CAC)} · ticket {pesos(TICKET)} · "
          f"interacción {pct(ENGAGEMENT)} · abandono {pct(ABANDONO, 0)}")
