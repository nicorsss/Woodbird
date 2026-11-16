# Genera los entregables de cierre de Dirección y Gestión de Proyectos (Sprint 4):
#   sitio/docs/sprint-4/05_Gantt_Real_vs_Planificado.png   (Tarea 4.3)
#   sitio/docs/sprint-4/05_Curva_S_Horas.png               (Tarea 4.3)
#   sitio/docs/sprint-4/05_Costos_Reales_y_Desvios.docx    (Tarea 4.3)
#   sitio/docs/sprint-4/06_Acta_de_Cierre.docx             (Tarea 4.4)
# Uso: python herramientas/cierre_proyecto.py
# Las fechas planificadas salen de la EDT (14/09) y del Gantt base (Sprint 2); las reales, de los commits,
# las fechas de los archivos y el tablero de Trello. Las horas reales son una reconstrucción (ver SESIONES).

import sys
from datetime import date, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from docx.shared import Inches

from gestion_sprint3 import nuevo
from terminos import tabla, viñeta
from pruebas_sprint4 import MANUALES

sys.stdout.reconfigure(encoding="utf-8")
DESTINO = Path(__file__).resolve().parent.parent / "sitio" / "docs" / "sprint-4"
FECHA = "16 de noviembre de 2026"
HOY = date(2026, 11, 16)
INICIO = date(2026, 8, 24)            # lunes de la semana 1
CIERRE_PLAN = date(2026, 11, 10)      # entrega del portafolio final según la consigna
URL = "https://nicorsss.github.io/Woodbird/"
REPO = "https://github.com/nicorsss/Woodbird"

VALOR_HORA = 3500                     # el mismo valor de referencia del Panel de KPIs (Sprint 3)


def fin_semana(n):
    """Viernes de la semana n del proyecto (S1 termina el 28/08)."""
    return INICIO + timedelta(days=4 + 7 * (n - 1))


def ini_semana(n):
    return INICIO + timedelta(days=7 * (n - 1))


def d(dia, mes):
    return date(2026, mes, dia)


def pesos(n):
    return ("−" if n < 0 else "") + "$" + f"{abs(n):,.0f}".replace(",", ".")


def num(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",")


def corto(f):
    return f.strftime("%d/%m")


# ---------------------------------------------------------------------------
# Línea base (EDT) frente a ejecución real
# ---------------------------------------------------------------------------
# código, paquete, rama, semana inicio, semana fin, fecha real (None = no ejecutado), nota
PAQUETES = [
    ("4.1", "Acta de Constitución", "Gestión", 1, 1, d(31, 8), ""),
    ("4.2", "EDT / WBS", "Gestión", 2, 2, d(14, 9), ""),
    ("4.3", "Tablero Kanban (Trello)", "Gestión", 3, 3, d(14, 9), ""),
    ("4.4", "Diagrama de Gantt", "Gestión", 4, 4, d(22, 9), ""),
    ("4.5", "Matriz de riesgos", "Gestión", 4, 4, d(22, 9), "Reevaluada el 22/10"),
    ("4.6", "Control de desvíos", "Gestión", 6, 9, d(22, 10), "Controles del 28/09 y 22/10"),
    ("4.7", "Seguimiento ágil", "Gestión", 1, 11, d(16, 11), "Sin registros del 05/10 al 21/10 ni del 04/11 al 15/11"),
    ("4.8", "Cierre y presentación final", "Gestión", 11, 11, d(16, 11), "Portafolio el 16/11; pitch a coordinar"),
    ("1.1", "Wireframes", "Software", 1, 1, d(8, 9), ""),
    ("1.2", "Entorno y repositorio Git", "Software", 2, 2, d(22, 9), ""),
    ("1.3", "HTML5 semántico", "Software", 3, 3, d(22, 9), ""),
    ("1.4", "CSS responsive", "Software", 4, 5, d(22, 9), ""),
    ("1.5", "productos.json", "Software", 5, 5, d(22, 9), ""),
    ("1.6", "Pruebas responsive", "Software", 6, 6, d(28, 9), ""),
    ("1.7", "Backend y base de datos", "Software", 7, 8, None, "No ejecutado: reemplazado por productos.json con Fetch API (22/10) y una función serverless de pago (16/11), SC-01"),
    ("1.8", "Integración de pagos", "Software", 9, 9, d(22, 10), "Checkout simulado el 22/10 (SC-01); Mercado Pago Checkout Pro de prueba agregado el 16/11"),
    ("1.9", "Pruebas funcionales de compra", "Software", 10, 10, d(16, 11), "Automáticas el 03/11; manuales el 16/11"),
    ("1.10", "Corrección de errores y build final", "Software", 11, 11, d(3, 11), "Ícono, srcset y consola sin errores"),
    ("2.1", "Marca INPI y dominio NIC", "Legal", 1, 1, d(8, 9), ""),
    ("2.2", "Declaración ética de IA", "Legal", 2, 2, d(8, 9), ""),
    ("2.3", "Política de privacidad", "Legal", 5, 5, d(22, 9), ""),
    ("2.4", "Licenciamiento", "Legal", 6, 6, d(23, 9), ""),
    ("2.5", "Revisión normativa (Términos y arrepentimiento)", "Legal", 8, 8, d(22, 10), ""),
    ("2.6", "Publicación legal final y auditoría", "Legal", 11, 11, d(3, 11), "Auditoría 49/49; 50/50 el 16/11"),
    ("3.1", "Lienzo Canvas", "Negocio", 1, 1, d(8, 9), ""),
    ("3.2", "Triple impacto", "Negocio", 2, 2, d(14, 9), ""),
    ("3.3", "Informe Startup vs. Tradicional", "Negocio", 4, 5, d(23, 9), ""),
    ("3.4", "Embudo de conversión", "Negocio", 5, 5, d(22, 9), ""),
    ("3.5", "Campaña de Instagram", "Negocio", 7, 9, d(27, 10), "Maqueta el 22/09; publicada el 27/10"),
    ("3.6", "Cierre comercial (métricas finales)", "Negocio", 11, 11, d(16, 11), ""),
]
# Entregables exigidos por las consignas que no estaban en la EDT
EXTRAS = [
    ("—", "Carpeta integradora Sprint 1", "Fuera de la EDT", d(11, 9), d(23, 9)),
    ("—", "Carpeta integradora Sprint 2", "Fuera de la EDT", d(2, 10), d(2, 10)),
    ("—", "Carpeta integradora Sprint 3", "Fuera de la EDT", d(23, 10), d(28, 10)),
    ("—", "Imágenes de producto con IA (R6)", "Fuera de la EDT", d(29, 9), d(3, 11)),
    ("—", "Despliegue HTTPS (4.1 de la consigna)", "Fuera de la EDT", d(10, 11), d(3, 11)),
]


def plan_fin(p):
    # El cierre (4.8, 3.6, 1.10, 2.6) se compromete para la entrega del portafolio: martes 10/11
    return CIERRE_PLAN if p[4] == 11 else fin_semana(p[4])


def desvio(plan, real):
    return None if real is None else (real - plan).days


def txt_desvio(x):
    if x is None:
        return "—"
    return "0 d" if x == 0 else (f"+{x} d" if x > 0 else f"−{-x} d")


# ---------------------------------------------------------------------------
# Horas reales reconstruidas
# ---------------------------------------------------------------------------
# fecha, sprint, horas, trabajo, evidencia
SESIONES = [
    (d(31, 8), 1, 2.0, "Acta de Constitución", "Fecha del archivo del Acta"),
    (d(8, 9), 1, 6.0, "Canvas, wireframes, marca y dominios, declaración ética de IA", "Archivos del 08/09 (01:39 y 16:33 a 16:51): dos sesiones"),
    (d(14, 9), 1, 3.5, "EDT, triple impacto y tablero Kanban", "Archivos del 14/09 y creación del tablero"),
    (d(22, 9), 2, 5.0, "Repositorio, HTML5, CSS, productos.json, Gantt, riesgos, privacidad y embudo", "7 commits (16:24 a 17:54) y el trabajo previo a cada uno"),
    (d(23, 9), 2, 3.0, "Licenciamiento, informe comparativo y carpeta del Sprint 1", "5 commits"),
    (d(28, 9), 2, 3.0, "Pruebas responsive, control de desvíos y SC-01", "3 commits"),
    (d(29, 9), 2, 1.0, "Prueba en teléfono real y GitHub Pages", "2 commits"),
    (d(2, 10), 2, 1.0, "Carpeta del Sprint 2 y entrega en Drive", "Entrega en Drive"),
    (d(5, 10), 3, 0.5, "Script de Trello", "1 commit"),
    (d(22, 10), 3, 6.0, "Fetch API, carrito, checkout, Términos, casos de prueba, riesgos, campaña y KPIs", "6 commits (14:32 a 17:41) y los documentos del día"),
    (d(27, 10), 3, 2.0, "Cuenta de Instagram y publicación de las 8 piezas", "Fecha de las publicaciones"),
    (d(28, 10), 3, 1.5, "Carpeta del Sprint 3 con la evidencia de Instagram", "Commit 5a7edc9"),
    (d(3, 11), 4, 6.0, "Imágenes con IA, despliegue, auditoría legal, pruebas automáticas y Lighthouse", "7 commits (12:51 a 16:49) y la generación en Gemini"),
    (d(16, 11), 4, 10.5, "Pago con Mercado Pago (función en Vercel), corrección del carrito y del checkout, Términos 1.3 y Política 1.2, pruebas manuales, métricas finales, costos, Acta de Cierre, portafolio y pitch", "Commits del 16/11 (9ab919a a 3a7ed2e) y el pago aprobado con un comprador de prueba"),
]
HORAS_REALES = sum(s[2] for s in SESIONES)

# Presupuesto del Acta de Constitución (31/08): rubro, planificado, real, explicación
RUBROS = [
    ("Desarrollo y diseño del sistema (horas)", 80000, round(HORAS_REALES * VALOR_HORA),
     f"{num(HORAS_REALES)} h reales × {pesos(VALOR_HORA)}. El Acta no estimó horas: a ese valor, $80.000 alcanzan para "
     f"{num(80000 / VALOR_HORA)} h, la mitad de lo que llevó el proyecto."),
    ("Infraestructura, hosting y dominio", 30000, 0,
     "GitHub Pages y el plan Hobby de Vercel (la función de pago) son gratuitos e incluyen HTTPS. No se registró el dominio woodbird.com.ar (hallazgo H2 de la auditoría): "
     "el contacto pasó a una cuenta de Gmail."),
    ("Servicios de pagos", 20000, 0,
     "Mercado Pago Checkout Pro se integró con credenciales de prueba, que no tienen costo ni cobran dinero real: las piezas son ficticias (SC-01, SC-06). En producción, Mercado Pago cobra una comisión por venta, no un abono."),
    ("Recursos gráficos, pruebas y contingencias", 20000, 0,
     "Imágenes generadas con el plan gratuito de Gemini; pruebas con Chrome, Edge, Lighthouse y Node, todos gratuitos."),
]
PLAN_TOTAL = sum(r[1] for r in RUBROS)
REAL_TOTAL = sum(r[2] for r in RUBROS)
HORAS_PLAN = 80000 / VALOR_HORA


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
COLORES = {"Gestión": "#47542F", "Software": "#2F6B8A", "Legal": "#8A4F2F", "Negocio": "#6B5A8A", "Fuera de la EDT": "#6B6959"}
TINTA, GRILLA = "#191E14", "#E4DCC4"


def gantt():
    filas = [(c, n, r, ini_semana(a), plan_fin((c, n, r, a, b, real, x)), real) for c, n, r, a, b, real, x in PAQUETES]
    filas += [(c, n, r, p - timedelta(days=4), p, real) for c, n, r, p, real in EXTRAS]
    fig, ax = plt.subplots(figsize=(13, 12), dpi=150)
    for i, (c, n, rama, ini, fin, real) in enumerate(filas):
        y = len(filas) - i
        col = COLORES[rama]
        ax.barh(y, (fin - ini).days + 1, left=matplotlib.dates.date2num(ini), height=0.55, color=col, alpha=0.28)
        if real is None:
            ax.text(matplotlib.dates.date2num(fin) + 2, y, "no ejecutado (SC-01)", va="center", fontsize=8, color="#d03b3b")
            continue
        x_fin, x_real = matplotlib.dates.date2num(fin), matplotlib.dates.date2num(real)
        if real != fin:
            ax.plot([x_fin, x_real], [y, y], color="#d03b3b" if real > fin else "#0ca30c", lw=1.6)
        ax.plot(x_real, y, marker="D", color=col, markersize=7, markeredgecolor="white")
    etiquetas = [f"{c}  {n}" if c != "—" else n for c, n, *_ in filas]
    ax.set_yticks(range(len(filas), 0, -1), etiquetas, fontsize=8.5)
    ax.xaxis_date()
    semanas = [ini_semana(n) for n in range(1, 14)]
    ax.set_xticks([matplotlib.dates.date2num(s) for s in semanas], [f"S{n}\n{corto(s)}" for n, s in enumerate(semanas, 1)], fontsize=8)
    ax.axvline(matplotlib.dates.date2num(CIERRE_PLAN), color=TINTA, ls="--", lw=1)
    ax.text(matplotlib.dates.date2num(CIERRE_PLAN) + 0.5, len(filas) + 0.6, "Cierre planificado 10/11", fontsize=8)
    ax.axvline(matplotlib.dates.date2num(HOY), color="#d03b3b", ls=":", lw=1)
    ax.text(matplotlib.dates.date2num(HOY) + 0.5, len(filas) + 1.3, "Cierre real 16/11", fontsize=8, color="#d03b3b")
    for a, b in ((d(5, 10), d(21, 10)), (d(4, 11), d(15, 11))):
        ax.axvspan(matplotlib.dates.date2num(a), matplotlib.dates.date2num(b), color="#d03b3b", alpha=0.05)
    ax.text(matplotlib.dates.date2num(d(6, 10)), 0.2, "sin avances", fontsize=7.5, color="#d03b3b")
    ax.text(matplotlib.dates.date2num(d(5, 11)), 0.2, "sin avances", fontsize=7.5, color="#d03b3b")
    ax.set_xlim(matplotlib.dates.date2num(INICIO - timedelta(days=1)), matplotlib.dates.date2num(d(20, 11)))
    ax.set_ylim(-0.3, len(filas) + 1.8)
    ax.grid(axis="x", color=GRILLA)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    leyenda = [Line2D([], [], color=c, lw=8, alpha=0.4, label=r) for r, c in COLORES.items()]
    leyenda += [Line2D([], [], marker="D", color="#555", lw=0, label="Finalización real"),
                Line2D([], [], color="#d03b3b", label="Atraso"), Line2D([], [], color="#0ca30c", label="Adelanto")]
    ax.legend(handles=leyenda, loc="lower left", fontsize=8, ncol=4, frameon=False, bbox_to_anchor=(0, -0.09))
    ax.set_title("Woodbird · Gantt planificado (barras) frente a real (rombos) · 24/08 al 16/11/2026", fontsize=12, loc="left", color=TINTA)
    fig.tight_layout()
    fig.savefig(DESTINO / "05_Gantt_Real_vs_Planificado.png")
    plt.close(fig)


def curva_s():
    dias = [INICIO + timedelta(days=i) for i in range((HOY - INICIO).days + 1)]
    total_plan_dias = (CIERRE_PLAN - INICIO).days
    plan = [min(HORAS_PLAN, HORAS_PLAN * (x - INICIO).days / total_plan_dias) for x in dias]
    acum, real = 0, []
    for x in dias:
        acum += sum(s[2] for s in SESIONES if s[0] == x)
        real.append(acum)
    fig, ax = plt.subplots(figsize=(11, 5), dpi=150)
    ax.plot(dias, plan, color="#6B6959", ls="--", lw=2, label=f"Planificado: {num(HORAS_PLAN)} h repartidas en 11 semanas (presupuesto del Acta)")
    ax.step(dias, real, where="post", color="#47542F", lw=2.5, label=f"Real: {num(HORAS_REALES)} h en {len(SESIONES)} jornadas")
    for s in SESIONES:
        if s[2] >= 5:
            ax.annotate(f"{corto(s[0])}: {num(s[2])} h", (s[0], real[(s[0] - INICIO).days]), textcoords="offset points",
                        xytext=(-60, 8), fontsize=8, color=TINTA)
    ax.axvline(CIERRE_PLAN, color=TINTA, ls=":", lw=1)
    ax.set_ylabel("Horas acumuladas")
    ax.grid(color=GRILLA)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.set_title("Curva S de esfuerzo: horas acumuladas planificadas frente a reales", loc="left", fontsize=12, color=TINTA)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d/%m"))
    fig.tight_layout()
    fig.savefig(DESTINO / "05_Curva_S_Horas.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 05 · Costos reales y análisis de desvíos (Tarea 4.3)
# ---------------------------------------------------------------------------
def costos():
    doc = nuevo("COSTOS REALES Y ANÁLISIS DE DESVÍOS", "Sprint 4 — Tarea 4.3: Liquidación final del presupuesto y desvíos frente a la EDT y el Gantt")
    doc.tables[0].rows[-1].cells[1].paragraphs[0].runs[0].text = FECHA

    doc.add_heading("1. Resumen", level=1)
    ejecutados = [p for p in PAQUETES if p[5] is not None]
    atrasados = [p for p in ejecutados if desvio(plan_fin(p), p[5]) > 0]
    doc.add_paragraph(
        f"El proyecto se planificó entre el 24/08 y el 10/11/2026 (11 semanas) con un presupuesto de {pesos(PLAN_TOTAL)} "
        f"según el Acta de Constitución. Se cerró el 16/11, con 6 días de atraso, y un costo real de {pesos(REAL_TOTAL)}: "
        f"{num((REAL_TOTAL - PLAN_TOTAL) / PLAN_TOTAL * 100)} % frente a lo presupuestado. De los {len(PAQUETES)} paquetes de la EDT, "
        f"{len(ejecutados)} se ejecutaron ({len(atrasados)} con atraso) y uno, el backend con base de datos, se reemplazó por "
        f"una solución sin servidor dentro de la solicitud de cambio SC-01.")
    doc.add_paragraph(
        f"El número total oculta dos desvíos de signo contrario. Los rubros de infraestructura, pagos y recursos gráficos "
        f"no se gastaron ({pesos(70000)} de ahorro), pero el ahorro no viene de la eficiencia sino de una reducción de alcance: "
        f"no hay dominio propio ni pasarela de pagos real. En cambio, las horas de desarrollo costaron el doble de lo previsto: "
        f"{num(HORAS_REALES)} h frente a {num(HORAS_PLAN)} h.")

    doc.add_heading("2. Metodología", level=1)
    viñeta(doc, "Presupuesto planificado.", "Los cuatro rubros del Acta de Constitución del 31/08 ($150.000).")
    viñeta(doc, "Valor hora.", f"{pesos(VALOR_HORA)}, el mismo valor de referencia de un perfil junior que usa el Panel de KPIs "
                              f"del Sprint 3 para el CAC. Con él, el rubro de desarrollo equivale a {num(HORAS_PLAN)} horas planificadas.")
    viñeta(doc, "Horas reales.", "El proyecto no llevó un registro de horas (timesheet). Se reconstruyeron por jornada a partir de "
                                 "la hora del primer y del último commit, las fechas de los archivos y los movimientos del tablero. "
                                 "Se estima un margen de error de ±25 %. La falta de registro es una de las lecciones aprendidas.")
    viñeta(doc, "Cronograma.", "Fecha planificada: viernes de la última semana del paquete en la EDT; para los paquetes de cierre, "
                               "la fecha de entrega de la consigna (10/11). Fecha real: commit o archivo que terminó el entregable.")

    doc.add_heading("3. Liquidación final del presupuesto", level=1)
    filas = [(r, pesos(p), pesos(x), pesos(x - p), f"{num((x - p) / p * 100, 0)} %", e) for r, p, x, e in RUBROS]
    filas.append(("Total", pesos(PLAN_TOTAL), pesos(REAL_TOTAL), pesos(REAL_TOTAL - PLAN_TOTAL),
                  f"{num((REAL_TOTAL - PLAN_TOTAL) / PLAN_TOTAL * 100, 0)} %", ""))
    tabla(doc, ["Rubro", "Planificado", "Real", "Desvío", "%", "Explicación"], filas, [1.4, 0.8, 0.8, 0.8, 0.5, 2.2])

    doc.add_heading("4. Horas reales por sprint", level=1)
    por_sprint = {}
    for s in SESIONES:
        por_sprint[s[1]] = por_sprint.get(s[1], 0) + s[2]
    semanas = {1: 3, 2: 3, 3: 3, 4: 2}
    filas = []
    for n, h in por_sprint.items():
        plan = HORAS_PLAN * semanas[n] / 11
        dias = len([s for s in SESIONES if s[1] == n])
        filas.append((f"Sprint {n}", f"{semanas[n]} semanas", num(plan), num(h), f"{'+' if h > plan else ''}{num(h - plan)}",
                      pesos(h * VALOR_HORA), f"{dias} jornadas"))
    filas.append(("Total", "11 semanas", num(HORAS_PLAN), num(HORAS_REALES), f"+{num(HORAS_REALES - HORAS_PLAN)}",
                  pesos(REAL_TOTAL), f"{len(SESIONES)} jornadas"))
    tabla(doc, ["Sprint", "Duración", "Horas plan", "Horas reales", "Desvío", "Costo real", "Trabajo"], filas,
          [0.8, 0.9, 0.8, 0.9, 0.8, 1.1, 1.2])
    doc.add_paragraph("Detalle de las jornadas reconstruidas:")
    tabla(doc, ["Fecha", "Horas", "Trabajo", "Evidencia"],
          [(corto(f), num(h), t, e) for f, _, h, t, e in SESIONES], [0.6, 0.5, 3.0, 2.4])
    doc.add_picture(str(DESTINO / "05_Curva_S_Horas.png"), width=Inches(6.5))
    doc.add_paragraph(
        "La curva planificada sube de manera pareja; la real avanza en escalones. Todo el proyecto se hizo en 14 jornadas, y "
        f"las cuatro más largas ({', '.join(corto(s[0]) for s in sorted(SESIONES, key=lambda s: -s[2])[:4])}) concentran el "
        f"{num(sum(sorted((s[2] for s in SESIONES), reverse=True)[:4]) / HORAS_REALES * 100, 0)} % de las horas. Entre los escalones hay mesetas largas "
        "sin avances: del 05/10 al 21/10 y del 04/11 al 15/11. Esa forma es la que explica los atrasos: el esfuerzo total "
        "alcanzó, pero llegó tarde.")

    doc.add_heading("5. Cronograma: Gantt planificado frente a real", level=1)
    doc.add_picture(str(DESTINO / "05_Gantt_Real_vs_Planificado.png"), width=Inches(6.5))
    filas = []
    for p in PAQUETES:
        c, n, rama, a, b, real, nota = p
        pf = plan_fin(p)
        dv = desvio(pf, real)
        estado = "No ejecutado" if real is None else ("Con atraso" if dv > 0 else "En fecha" if dv == 0 else "Adelantado")
        sem = f"S{a}" if a == b else f"S{a}–S{b}"
        filas.append((c, n, f"{sem} ({corto(pf)})", corto(real) if real else "—", txt_desvio(dv), estado + (f". {nota}" if nota else "")))
    for c, n, rama, pf, real in EXTRAS:
        dv = desvio(pf, real)
        filas.append((c, n, corto(pf), corto(real), txt_desvio(dv), "Exigido por la consigna, fuera de la EDT"))
    tabla(doc, ["Cód.", "Paquete", "Planificado", "Real", "Desvío", "Estado"], filas, [0.45, 1.8, 1.0, 0.6, 0.6, 2.05])
    desv = [desvio(plan_fin(p), p[5]) for p in ejecutados]
    s12 = [desvio(plan_fin(p), p[5]) for p in ejecutados if p[4] <= 6]
    s34 = [desvio(plan_fin(p), p[5]) for p in ejecutados if p[4] > 6]
    doc.add_paragraph(
        f"De los {len(ejecutados)} paquetes ejecutados, {len(atrasados)} terminaron con atraso y "
        f"{len(ejecutados) - len(atrasados)} en fecha o adelantados. El desvío promedio fue de {num(sum(desv) / len(desv))} días "
        f"corridos: {num(sum(s12) / len(s12))} días en los paquetes de las semanas 1 a 6 y {num(sum(s34) / len(s34))} días en los "
        f"de las semanas 7 a 11. Las cuatro carpetas o entregas de cierre de sprint, que no figuraban en la EDT, acumularon "
        f"12, 0, 5 y 6 días de atraso.")

    doc.add_heading("6. Justificación de los desvíos", level=1)
    tabla(doc, ["Desvío", "Tipo", "Causa", "Efecto"], [
        (f"Horas de desarrollo +{num((HORAS_REALES / HORAS_PLAN - 1) * 100, 0)} %", "Económico",
         "El Acta asignó $80.000 a desarrollo sin estimar horas por paquete. La EDT tampoco las tiene.",
         "La línea base de esfuerzo era irreal desde el inicio: el desvío es de estimación más que de ejecución."),
        ("Infraestructura, pagos y gráficos −100 %", "Económico (alcance)",
         "Se eligieron servicios gratuitos (GitHub Pages, Vercel, Gemini) y Mercado Pago con credenciales de prueba, sin cobros reales (SC-01).",
         "Ahorro de $70.000, a cambio de no tener dominio propio ni cobrar ventas reales."),
        ("Sprint 1: +3 a +18 días", "Temporal",
         "Trabajo concentrado en la fecha de corrección y un repositorio que quedó vacío 18 días en el camino crítico.",
         "Corregido en el Sprint 2 con fast tracking: los paquetes S4–S6 cerraron antes de lo previsto."),
        ("Sprint 3: +4 a +13 días", "Temporal",
         "17 días sin avances (05/10 al 21/10). Todo el sprint se resolvió el 22/10 (riesgos R1 y R2).",
         "Carpeta entregada el 28/10 (+5 d); campaña de Instagram publicada el 27/10 de una sola vez."),
        ("Sprint 4: +6 días", "Temporal",
         "Las tareas técnicas y legales cerraron el 03/11, una semana antes; después hubo 12 días sin avances.",
         "El pago con Mercado Pago, los costos, el Acta de Cierre, las métricas, las pruebas manuales y el portafolio se hicieron el 16/11."),
        ("Backend y base de datos", "Alcance",
         "Las consignas del Sprint 3 piden consumir un JSON con Fetch API. El único código de servidor es la función de pago (16/11).",
         "Paquete 1.7 no ejecutado; la SC-01 que lo formaliza sigue sin respuesta del docente (riesgo R4)."),
    ], [1.3, 0.9, 2.2, 2.1])

    doc.add_heading("7. Indicadores de desempeño", level=1)
    va = len(ejecutados) / len(PAQUETES)
    al_10 = len([p for p in ejecutados if p[5] <= CIERRE_PLAN])
    tabla(doc, ["Indicador", "Valor", "Lectura"], [
        ("Avance físico (paquetes ejecutados)", f"{len(ejecutados)} de {len(PAQUETES)} ({num(va * 100, 0)} %)", "Uno reemplazado por cambio de alcance."),
        ("Índice de desempeño del cronograma (SPI) al 10/11", num(al_10 / len(PAQUETES), 2),
         f"Al 10/11 había {al_10} paquetes terminados de {len(PAQUETES)} planificados; los de cierre se completaron el 16/11."),
        ("Esfuerzo real ÷ esfuerzo planificado", num(HORAS_REALES / HORAS_PLAN, 2), "Se trabajó más del doble de lo estimado en el Acta."),
        ("Costo real ÷ presupuesto (CPI inverso)", num(REAL_TOTAL / PLAN_TOTAL, 2),
         f"{num((REAL_TOTAL / PLAN_TOTAL - 1) * 100, 0)} % por encima del presupuesto total; los servicios gratuitos compensaron parte de las horas."),
        ("Atraso de la entrega final", "6 días corridos", "Entrega comprometida el 10/11; real el 16/11."),
    ], [2.3, 1.4, 2.8])

    doc.add_heading("8. Conclusión", level=1)
    doc.add_paragraph(
        f"En lo económico, el proyecto cerró un {num((REAL_TOTAL / PLAN_TOTAL - 1) * 100, 0)} % por encima del presupuesto total, y no más por compensación: el esfuerzo de desarrollo se "
        "subestimó a menos de la mitad y los servicios pagos previstos se reemplazaron por alternativas gratuitas o de prueba. En lo "
        "temporal, el problema no fue la cantidad de horas sino su distribución: se trabajó en 14 jornadas aisladas, con dos "
        "mesetas de 17 y 12 días sin avances, y cada meseta terminó en una entrega atrasada. El producto se entregó completo "
        "y funcionando en producción; lo que falló fue la constancia del seguimiento.")
    doc.add_heading("9. Recomendaciones para un próximo proyecto", level=1)
    viñeta(doc, "Estimar en horas por paquete.", "Cada paquete de la EDT con su estimación; el presupuesto de desarrollo es la suma, no un monto global.")
    viñeta(doc, "Registrar horas el mismo día.", "Una planilla de una línea por jornada evita reconstruirlas al final con ±25 % de error.")
    viñeta(doc, "Hitos semanales obligatorios.", "Una semana sin commit ni tarjeta movida dispara la contingencia del riesgo R1, sin esperar a la entrega.")
    viñeta(doc, "Presupuestar el alcance real.", "Si el sitio será estático, no presupuestar dominio y pasarela; si se presupuestan, contratarlos.")
    doc.save(DESTINO / "05_Costos_Reales_y_Desvios.docx")


# ---------------------------------------------------------------------------
# 06 · Acta de Cierre del Proyecto (Tarea 4.4)
# ---------------------------------------------------------------------------
def estado_manual(cp):
    est, fecha, obs = MANUALES[cp]
    return est + (f" ({fecha})" if fecha else "") + (f". {obs}" if obs else "")


def acta():
    doc = nuevo("ACTA DE CIERRE DEL PROYECTO", "Sprint 4 — Tarea 4.4: Acta de Cierre del Proyecto (Project Closure Document)")
    doc.tables[0].rows[-1].cells[1].paragraphs[0].runs[0].text = FECHA

    doc.add_heading("1. Datos del proyecto", level=1)
    tabla(doc, ["Campo", "Detalle"], [
        ("Proyecto", "Woodbird — Tienda web de aves decorativas de madera (Proyecto Integrador «EcoStart IA»)"),
        ("Institución", "IES N° 810 «René Favaloro» · Tecnicatura Superior en Desarrollo de Software, 3er año"),
        ("Equipo", "Reiss Jorge Nicolás: Project Manager, Desarrollador, Responsable Legal (Compliance) y Responsable de Negocio"),
        ("Cliente / sponsor", "Cátedra del Proyecto Integrador · Docente Ibañez Erick"),
        ("Inicio", "24/08/2026 (semana 1); Acta de Constitución del 31/08/2026"),
        ("Cierre planificado", "10/11/2026 (portafolio final y pitch)"),
        ("Cierre real", "16/11/2026 (portafolio final). El pitch queda a coordinar con el docente."),
        ("Producto", f"Sitio en producción: {URL}"),
        ("Repositorio", REPO),
        ("Tablero", "https://trello.com/b/iGCwIo1k/woodbird"),
    ], [1.5, 5.0])

    doc.add_heading("2. Cumplimiento de los objetivos del Acta de Constitución", level=1)
    tabla(doc, ["Objetivo (Acta del 31/08)", "Resultado", "Estado"], [
        ("MVP funcional dentro del período académico", f"Publicado en GitHub Pages con HTTPS desde el 29/09; versión final del 03/11.", "Cumplido"),
        ("Catálogo de al menos 10 productos con nombre, imagen, descripción y precio",
         "12 piezas cargadas desde productos.json con Fetch API, con imagen generada con IA, filtros y buscador.", "Cumplido (12/10)"),
        ("Carrito que permita agregar, quitar y modificar cantidades",
         "Carrito persistente con tope de unidades, control de stock y totales con envío (CP-11 a CP-16).", "Cumplido"),
        ("Sistema de pago que simule o procese una transacción",
         "Mercado Pago Checkout Pro con credenciales de prueba: el pago de un comprador de prueba se aprobó el 16/11 y el sitio muestra el resultado con el número de pedido WB-XXXXXX. No se cobra dinero real (SC-01).", "Cumplido en modo de prueba"),
        ("Checkout con datos del comprador y confirmación",
         "Formulario validado, consentimiento de privacidad, aceptación de Términos y aviso de arrepentimiento.", "Cumplido"),
        ("Pruebas funcionales antes de la presentación final",
         "38 casos: 33 automáticos que pasan en Chrome y Edge sobre el sitio en vivo, y 5 manuales (sección 4).", "Cumplido"),
        ("Presentar una versión funcional al finalizar el período",
         "Portafolio final entregado el 16/11, 6 días después de la fecha prevista.", "Cumplido con atraso"),
    ], [2.2, 3.3, 1.0])

    doc.add_heading("3. Entrega del producto al cliente", level=1)
    doc.add_paragraph("Se entrega al cliente simulado (la cátedra) el siguiente producto, en su versión final:")
    tabla(doc, ["Entregable", "Ubicación", "Estado"], [
        ("Sitio de comercio electrónico (catálogo, carrito, checkout y pago de prueba con Mercado Pago)", URL, "En producción, HTTPS"),
        ("Función de pago (crea la preferencia de Mercado Pago)", "https://woodbird-h7cb.vercel.app (api/crear-preferencia.js)", "En producción, credenciales de prueba"),
        ("Código fuente y documentación de los 4 sprints", f"{REPO} (docs/sprint-1 a sprint-4)", "Público"),
        ("Instrumentos legales en el sitio", "Declaración de IA, Política de Privacidad v1.2, Términos y Condiciones v1.3, botón de arrepentimiento", "Auditoría 50/50"),
        ("Cuenta comercial de Instagram", "@woodbird.ar (8 piezas publicadas)", "Activa"),
        ("Tablero Kanban", "Trello «Woodbird»", "Todas las tarjetas en Hecho, salvo SC-01"),
        ("Generadores de documentos y pruebas", "herramientas/ en el repositorio (cierre del riesgo R8)", "Versionados"),
    ], [2.2, 3.0, 1.3])
    doc.add_paragraph("Criterios de aceptación verificados: el sitio responde por HTTPS con certificado válido, el contenido "
                      "publicado es idéntico al del repositorio, la consola no registra errores, los 33 casos automáticos "
                      "cumplen en dos navegadores, Lighthouse da 100 en accesibilidad, buenas prácticas y SEO, y la auditoría "
                      "legal cumple las 50 verificaciones.")

    doc.add_heading("4. Pruebas manuales previas a la entrega", level=1)
    nombres = {"CP-32": "Correo de arrepentimiento", "CP-35": "Recorrido con teclado", "CP-36": "Lector de pantalla (NVDA)",
               "CP-37": "Teléfono real (Samsung Galaxy A16)", "CP-38": "Firefox y Safari"}
    tabla(doc, ["Caso", "Prueba", "Resultado"], [(cp, nombres[cp], estado_manual(cp)) for cp in nombres], [0.7, 2.2, 3.6])

    doc.add_heading("5. Estado final de riesgos", level=1)
    tabla(doc, ["Riesgo", "Estado al cierre", "Comentario"], [
        ("R1 Sobrecarga del único integrante", "Materializado. Cerrado con el proyecto",
         "Atrasos en los cuatro sprints. Es la causa estructural de los desvíos (ver 05_Costos)."),
        ("R2 Inicio tardío de cada sprint", "Materializado. Cerrado", "Mesetas del 05/10 al 21/10 y del 04/11 al 15/11."),
        ("R3 Campaña de Instagram sin publicar", "Cerrado", "Publicada el 27/10; métricas reales en el documento 07."),
        ("R4 Alcance del Acta frente a la consigna (SC-01)", "Abierto", "Sin respuesta del docente. Se entrega con Mercado Pago en modo de prueba, sin cobros reales."),
        ("R6 Imágenes con IA", "Cerrado (03/11)", "12 imágenes con registro de herramienta y prompt."),
        ("R7 Navegadores y dispositivos no probados", "Cerrado", "CP-37 y CP-38 (sección 4)."),
        ("R8 Herramientas fuera del repositorio", "Cerrado (16/11)", "Los generadores se versionaron en herramientas/, sin credenciales."),
        ("R9 Servicios externos y token de Trello", "Cerrado", "El token vence el 21/11; el tablero queda como evidencia."),
        ("R10 a R15 (técnicos, legales y de seguridad)", "Cerrados", "Sin incidentes en producción; consola sin errores; sin innerHTML."),
    ], [2.1, 1.5, 2.9])

    doc.add_heading("6. Solicitudes de cambio", level=1)
    tabla(doc, ["Solicitud", "Decisión", "Estado al cierre"], [
        ("SC-01 Alcance simulado (sin base de datos ni cobros reales)", "Pendiente del docente", "Abierta; el pago usa Mercado Pago de prueba"),
        ("SC-02 Filtros y buscador", "Aprobada por el PM", "Implementada"),
        ("SC-03 Botón de arrepentimiento y Ventanilla Única", "Aprobada por el PM", "Implementada"),
        ("SC-04 Garantía propia de 12 meses", "Aprobada por el PM", "En Términos y Condiciones"),
        ("SC-05 Imágenes con IA al Sprint 4", "Aprobada por el PM", "Implementada el 03/11"),
        ("SC-06 Piezas como diseños de IA, sin tala", "Aprobada por el PM", "Implementada"),
    ], [2.8, 1.6, 2.1])

    doc.add_heading("7. Costos y cronograma", level=1)
    doc.add_paragraph(
        f"Presupuesto {pesos(PLAN_TOTAL)}; costo real {pesos(REAL_TOTAL)} ({num(HORAS_REALES)} h × {pesos(VALOR_HORA)}). "
        f"Cierre planificado 10/11; real 16/11 (+6 días). El detalle está en 05_Costos_Reales_y_Desvios.docx.")

    doc.add_heading("8. Evaluación de desempeño del equipo", level=1)
    doc.add_paragraph("El equipo es unipersonal, así que la evaluación se hace por rol, sobre una escala de 1 a 5.")
    tabla(doc, ["Rol", "Puntaje", "Fortalezas", "Aspectos a mejorar"], [
        ("Desarrollador", "4", "Sitio accesible y probado de forma automática; 0 errores de consola; Lighthouse 100 en tres categorías.",
         "Del backend previsto en el Acta sólo se hizo la función de pago; pruebas manuales hechas al final."),
        ("Responsable Legal", "4", "Términos, privacidad y arrepentimiento coherentes con el software, incluido Mercado Pago; auditoría 50/50.",
         "Cuatro hallazgos detectados recién en la auditoría final (H1 a H4)."),
        ("Responsable de Negocio", "3", "Propuesta de triple impacto clara; campaña de 8 piezas con CTA.",
         "Campaña publicada de una sola vez y tarde; poco tiempo para medir."),
        ("Project Manager", "2", "Riesgos, cambios y desvíos documentados con honestidad; lecciones registradas en cada sprint.",
         "No logró sostener el ritmo: cuatro entregas atrasadas y dos mesetas largas sin avances."),
    ], [1.3, 0.6, 2.4, 2.2])

    doc.add_heading("9. Lecciones aprendidas", level=1)
    tabla(doc, ["Situación", "Impacto", "Lección", "Recomendación"], [
        ("El trabajo se concentró en pocas jornadas antes de cada entrega", "4 entregas con atraso (12, 0, 5 y 6 días)",
         "La constancia importa más que el esfuerzo total", "Hito semanal obligatorio y verificable"),
        ("Entregables exigidos que no estaban en la EDT ni en el tablero", "Carpeta del Sprint 1 e imágenes atrasadas",
         "Lo que no está en el tablero no se hace", "Cargar cada consigna completa en Trello el primer día"),
        ("El Acta presupuestó sin estimar horas", f"Desvío de +{num((HORAS_REALES / HORAS_PLAN - 1) * 100, 0)} % en horas",
         "Un presupuesto sin estimación no sirve de línea base", "Estimar horas por paquete y registrar las reales"),
        ("Alcance del Acta distinto del de las consignas", "SC-01 abierta todo el proyecto",
         "Las diferencias de alcance hay que resolverlas al inicio", "Validar el Acta con el docente antes de la EDT"),
        ("Contingencias escritas para R6 y R3", "Las imágenes y la campaña no frenaron el camino crítico",
         "Una contingencia definida a tiempo evita bloqueos", "Mantener la matriz de riesgos viva en cada sprint"),
        ("Pruebas y auditoría automatizadas", "Se re-verificó todo el sitio en minutos tras cada corrección",
         "Automatizar la verificación ahorra tiempo al final", "Automatizar desde el primer sprint"),
        ("Afirmaciones legales sin verificar (dominio inexistente, enlaces)", "Hallazgos H1 y H2 en la auditoría final",
         "Lo que dice un documento legal debe poder comprobarse en el sitio", "Auditar en cada publicación, no sólo al final"),
    ], [1.7, 1.5, 1.6, 1.7])

    doc.add_heading("10. Pendientes transferidos", level=1)
    viñeta(doc, "SC-01.", "Respuesta del docente sobre el alcance simulado. Si se aprueba, se cierra R4.")
    viñeta(doc, "Dominio propio.", "Registrar woodbird.com.ar en NIC Argentina si el emprendimiento sigue (presupuesto previsto: $30.000).")
    viñeta(doc, "Fuentes locales.", "Alojar las fuentes en el sitio para subir el rendimiento móvil de las páginas legales (87 → ~100).")
    viñeta(doc, "Cobros reales.", "Pasar Mercado Pago a credenciales de producción (y quitar MP_MONTO_PRUEBA) sólo si las piezas pasan a fabricarse y venderse.")

    doc.add_heading("11. Aceptación y cierre", level=1)
    doc.add_paragraph("Con la firma de esta acta, el Project Manager declara cerrado el proyecto Woodbird y entrega el producto y su "
                      "documentación al cliente. El cliente deja constancia de su conformidad o de sus observaciones.")
    doc.add_paragraph("Project Manager: Reiss Jorge Nicolás          Firma: ______________________")
    doc.add_paragraph("Cliente / sponsor (docente): Ibañez Erick          Firma: ______________________")
    doc.add_paragraph("Observaciones del cliente: ____________________________________________________________")
    doc.add_paragraph("Fecha: ____ / ____ / 2026")
    doc.save(DESTINO / "06_Acta_de_Cierre.docx")


if __name__ == "__main__":
    gantt()
    curva_s()
    costos()
    acta()
    print(f"Horas reales {num(HORAS_REALES)} (plan {num(HORAS_PLAN)}); costo {pesos(REAL_TOTAL)} de {pesos(PLAN_TOTAL)}")
    ej = [p for p in PAQUETES if p[5]]
    print("Paquetes ejecutados:", len(ej), "con atraso:", sum(desvio(plan_fin(p), p[5]) > 0 for p in ej))
    print("Listo: 05_Gantt, 05_Curva_S, 05_Costos, 06_Acta")
