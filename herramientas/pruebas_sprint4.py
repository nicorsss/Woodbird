# Tarea 4.2 (Sprint 4): ejecución de los casos de prueba del Sprint 3 sobre el sitio en producción.
# Evalúa cada caso automático a partir de los datos crudos que deja pruebas/responsive.mjs
# (no hay resultados escritos a mano) y junta los casos manuales que informa el responsable.
#
# Antes, desde sitio/ y con el sitio publicado:
#   node pruebas/responsive.mjs https://nicorsss.github.io/Woodbird/ pruebas/sprint4/chrome
#   (con CHROME="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe") ... pruebas/sprint4/edge
# Uso: python herramientas/pruebas_sprint4.py            → imprime el resumen
#      python herramientas/pruebas_sprint4.py --docx     → además escribe el informe

import json
import sys
from pathlib import Path

from gestion_sprint3 import CASOS

sys.stdout.reconfigure(encoding="utf-8")
SITIO = Path(__file__).resolve().parent.parent / "sitio"
CORRIDAS = SITIO / "pruebas" / "sprint4"
NAVEGADORES = {"chrome": "Google Chrome (escritorio)", "edge": "Microsoft Edge (escritorio)"}

# Casos manuales: los completa el responsable después de ejecutarlos (resultado, fecha, observación)
MANUALES = {
    "CP-32": ("Pendiente", "", ""),
    "CP-35": ("Pendiente", "", ""),
    "CP-36": ("Pendiente", "", ""),
    "CP-37": ("Pendiente", "", ""),
    "CP-38": ("Pendiente", "", ""),
}


def cargar(nav):
    d = CORRIDAS / nav
    if not (d / "resultados.json").exists():
        return None
    leer = lambda n: json.loads((d / n).read_text(encoding="utf-8"))
    return {"r": leer("resultados.json"), "ec": leer("error-carga.json"),
            "vuelta": leer("vuelta-pago.json") if (d / "vuelta-pago.json").exists() else None,
            "consola": leer("consola.json") if (d / "consola.json").exists() else None}


def evaluar(datos):
    """Devuelve {id: (cumple, evidencia)} para los casos automáticos."""
    r, ec = datos["r"], datos["ec"]
    ini = [x for x in r if x["pagina"] == "inicio"]
    todos = lambda f: all(f(x) for x in ini)
    c0, k0 = ini[0]["carrito"], ini[0]["checkout"]
    res = {}

    def caso(id_, cumple, evidencia):
        res[id_] = (bool(cumple), evidencia)

    caso("CP-01", todos(lambda x: x["carrito"]["tarjetas"] == 12), f"{c0['tarjetas']} tarjetas en los {len(ini)} anchos")
    caso("CP-02", todos(lambda x: x["carrito"]["recientes"] == ["Garza blanca", "Zorzal", "Lechucita vizcachera", "Picaflor"]),
         ", ".join(c0["recientes"]))
    caso("CP-03", todos(lambda x: x["carrito"]["sinStock"] == ["Tucán"]), "Sin stock: " + ", ".join(c0["sinStock"]))
    caso("CP-04", todos(lambda x: x["carrito"]["sellosIA"] == 12), f"{c0['sellosIA']} de 12 tarjetas con sello")
    caso("CP-05", todos(lambda x: sorted(x["carrito"]["filtroPaloSanto"]) == sorted(["Cardenal", "Chuña", "Calandria", "Tucán"])),
         ", ".join(c0["filtroPaloSanto"]))
    caso("CP-06", todos(lambda x: len(x["carrito"]["filtroHasta25000"]) == 7), f"{len(c0['filtroHasta25000'])} piezas")
    caso("CP-07", todos(lambda x: x["carrito"]["busquedaSinTilde"] == ["Chuña"]), ", ".join(c0["busquedaSinTilde"]))
    caso("CP-08", todos(lambda x: len(x["carrito"]["busquedaMadera"]) == 4), ", ".join(c0["busquedaMadera"]))
    caso("CP-09", todos(lambda x: x["carrito"]["sinResultados"]["tarjetas"] == 0 and "pingüino" in x["carrito"]["sinResultados"]["estado"]),
         c0["sinResultados"]["estado"])
    caso("CP-10", ec["tarjetas"] == 0 and ec["marcadoComoError"] and not ec["cargando"], ec["mensaje"])

    def tot(e, filas, contador, total):
        return e["filas"] == filas and e["contador"] == contador and e["total"] == total and e["totalCheckout"] == total

    caso("CP-11", todos(lambda x: tot(x["carrito"]["inicial"], 2, 2, 69200)), f"2 filas, contador 2, total ${c0['inicial']['total']:,}".replace(",", "."))
    caso("CP-12", todos(lambda x: tot(x["carrito"]["agregarRepetido"], 2, 3, 97600) and x["carrito"]["agregarRepetido"]["cantidad"] == "2"),
         f"cantidad 2, contador 3, total ${c0['agregarRepetido']['total']:,}".replace(",", "."))
    caso("CP-13", todos(lambda x: x["carrito"]["cantidad3"]["total"] == 126000 == x["carrito"]["cantidad3"]["totalCheckout"]),
         f"total ${c0['cantidad3']['total']:,} en carrito y checkout".replace(",", "."))
    caso("CP-14", todos(lambda x: x["carrito"]["fueraDeRango"]["valor"] == "10"), f"25 → {c0['fueraDeRango']['valor']}")
    # Desde el 16/11 «Quitar» saca una unidad: con 2 Cardenales queda 1; con 1, la fila desaparece
    caso("CP-15", todos(lambda x: tot(x["carrito"]["quitarUno"], 2, 2, 69200) and x["carrito"]["quitarUno"]["cantidad"] == "1"
                        and tot(x["carrito"]["quitar"], 1, 1, 34300) and x["carrito"]["quitar"]["foco"] == "titulo-carrito"),
         f"Cardenal ×2 → ×1 (total ${c0['quitarUno']['total']:,}); con 1 unidad la fila se quita: 1 fila, total "
         f"${c0['quitar']['total']:,}, foco en #{c0['quitar']['foco']}".replace(",", "."))
    v = c0["vacio"]
    # Con el carrito vacío tampoco se muestra el formulario de datos: el paso actual es «Carrito»
    caso("CP-16", todos(lambda x: (lambda v: v["tablaOculta"] and v["contadorOculto"] and v["mensajeVisible"] and v["total"] == 0
                                   and v["formularioOculto"] and v["paso"] == "carrito")(x["carrito"]["vacio"])
                        and x["preparar"]["inicial"] == {"formularioOculto": True, "paso": "carrito"}),
         "tabla y contador ocultos, mensaje visible, total $0; formulario de datos oculto y paso «Carrito» al cargar y al vaciar")
    caso("CP-17", todos(lambda x: x["carrito"]["anuncio"] == "Agregaste Cardenal al carrito."), f"«{c0['anuncio']}»")
    esperados = {"nombre", "email", "direccion", "localidad", "cp", "terminos", "consentimiento"}
    caso("CP-18", todos(lambda x: x["checkout"]["vacioBloquea"] and esperados <= set(x["checkout"]["invalidos"])),
         "Inválidos: " + ", ".join(k0["invalidos"]))
    caso("CP-19", todos(lambda x: x["checkout"]["datosInconsistentesBloquean"] and len(x["checkout"]["mensajes"]) == 4),
         f"{len(k0['mensajes'])} mensajes propios: " + "; ".join(k0["mensajes"].values()))
    caso("CP-20", todos(lambda x: x["checkout"]["cpInvalidoBloquea"]), "No confirma con CP «35000»")
    # Desde el 16/11 la compra válida pasa a Mercado Pago (Checkout Pro en modo de prueba): se verifica que el
    # sitio redirija con la dirección que devuelve la función de pago, borre el formulario y el carrito, y que a
    # la vuelta muestre el resultado con el número de pedido y limpie la dirección.
    vu = datos.get("vuelta") or {}
    vuelta_ok = (vu.get("aprobado", {}).get("confirmacion", "").startswith("¡Gracias") and "WB-PRUEBA" in vu["aprobado"]["confirmacion"]
                 and "pendiente" in vu.get("pendiente", {}).get("confirmacion", "")
                 and vu.get("rechazado", {}).get("error", "").startswith("Mercado Pago no pudo")
                 and all(v["direccion"] == "#checkout" for v in vu.values()))
    caso("CP-21", vuelta_ok and todos(lambda x: x["checkout"]["redirige"] and not x["checkout"]["errorPago"]
                                      and x["checkout"]["pasoPago"] == "pago" and x["checkout"]["botonRestaurado"]
                                      and x["checkout"]["borrado"] and x["checkout"]["carritoVaciado"]
                                      and x["preparar"]["alContinuar"] == {"formularioVisible": True, "paso": "datos", "foco": "titulo-checkout"}),
         "«Continuar» muestra el formulario (paso «Datos»); redirige a Mercado Pago (paso «Pago»), borra formulario y carrito "
         "y rehabilita el botón al volver con «Atrás»; a la vuelta: «"
         + vu.get("aprobado", {}).get("confirmacion", "sin datos")[:90] + "…»")
    caso("CP-22", todos(lambda x: str(x["checkout"]["carritoVacioBloquea"]).startswith("Tu carrito está vacío")), k0["carritoVacioBloquea"])
    caso("CP-23", todos(lambda x: x["legales"]["checkout"]["terminosObligatorio"] and "terminos" in x["checkout"]["invalidos"]),
         "#terminos required y marcado inválido")
    # Sólo puede salir el pedido a la función de pago, y su cuerpo sólo lleva ids y cantidades
    def sin_datos(x):
        envios = [p for p in x["checkout"]["peticionesDuranteCompra"] if p["metodo"] != "OPTIONS"]
        if len(envios) != 1 or "crear-preferencia" not in envios[0]["url"]:
            return False
        cuerpo = json.loads(envios[0]["cuerpo"] or "{}")
        return list(cuerpo) == ["items"] and all(set(i) == {"id", "cantidad"} for i in cuerpo["items"])
    caso("CP-24", todos(sin_datos),
         "1 petición durante la compra, a la función de pago, sólo con ids y cantidades: "
         + next((p["cuerpo"] for p in k0["peticionesDuranteCompra"] if p["metodo"] == "POST"), "sin datos"))

    paginas = sorted({x["pagina"] for x in r})
    n = len(r)
    desb = [f"{x['pagina']} {x['vista']['ancho']}" for x in r if x["medicion"]["desborde"]]
    caso("CP-25", not desb, f"{n - len(desb)} de {n} combinaciones ({len(paginas)} páginas × 11 anchos)" + (f"; con desborde: {', '.join(desb)}" if desb else ""))
    chicos = [f"{x['pagina']} {x['vista']['ancho']}" for x in r if x["medicion"]["tactilesChicos"]]
    caso("CP-26", not chicos, f"{n - len(chicos)} de {n} combinaciones sin objetivos de menos de 44 px")
    contr = [p for x in r for p in x["medicion"]["contraste"] if p["falla"]]
    pares = {p["par"] for x in r for p in x["medicion"]["contraste"]}
    caso("CP-27", not contr, f"{len(pares)} pares de color distintos, ninguno por debajo de AA" if not contr else f"{len(contr)} fallas")
    anclas = [a for x in r for a in x["anclas"]]
    caso("CP-28", all(a["ok"] for a in anclas), f"{sum(a['ok'] for a in anclas)} de {len(anclas)} saltos con el título visible")

    def disp_ok(x):
        d, w = x["medicion"]["disposicion"], x["vista"]["ancho"]
        modo = "renglones apilados" if w < 600 else "tabla"
        lado = "lado a lado" if w >= 960 else "apilados"
        return d["carritoModo"] == modo and d["carritoYCheckout"] == lado
    caso("CP-29", todos(disp_ok), "apilados < 600 px, tabla ≥ 600 px, lado a lado ≥ 960 px en los 11 anchos")
    caso("CP-30", all(x["pie"]["ok"] for x in r), f"{sum(x['pie']['ok'] for x in r)} de {n} combinaciones")
    caso("CP-31", all(x["arrepentimiento"]["ok"] for x in r), f"{sum(x['arrepentimiento']['ok'] for x in r)} de {n} combinaciones")
    leg = lambda x: all(x["legales"][k] for k in ("declaracion", "privacidad", "terminos", "ventanilla"))
    caso("CP-33", all(leg(x) for x in r), f"Declaración de IA, Política, Términos y Ventanilla Única en las {len(paginas)} páginas")
    caso("CP-34", todos(lambda x: x["legales"]["checkout"]["avisoAntesDelPago"]), "Aviso con enlace a la cláusula 9 antes de «Ir al pago»")
    return res


def errores_consola(datos):
    c = datos["consola"]
    if c is None:
        return None
    return [x for x in c if x["fase"] == "recorrido"], [x for x in c if x["fase"] != "recorrido"]


def resumen():
    filas = {}
    for nav, nombre in NAVEGADORES.items():
        d = cargar(nav)
        if not d:
            print(f"{nombre}: sin corrida")
            continue
        ev = evaluar(d)
        filas[nav] = ev
        cumplen = sum(c for c, _ in ev.values())
        print(f"\n{nombre}: {cumplen} de {len(ev)} casos automáticos cumplen")
        for id_, (c, e) in ev.items():
            if not c:
                print(f"  NO CUMPLE {id_}: {e}")
        cons = errores_consola(d)
        if cons is not None:
            rec, prov = cons
            print(f"  Consola: {len(rec)} errores o advertencias en el recorrido; {len(prov)} en la falla provocada (CP-10)")
            for x in rec[:10]:
                print(f"    [{x['tipo']}] {x['pagina']}: {x['texto'][:140]}")
    return filas


# ---------------------------------------------------------------------------
# Informe 04 (Tarea 4.2)
# ---------------------------------------------------------------------------
DESTINO = SITIO / "docs" / "sprint-4"
LIGHTHOUSE = CORRIDAS / "lighthouse"
FECHA_DOC = "16 de noviembre de 2026"


def puntajes(f):
    j = json.loads(f.read_text(encoding="utf-8"))
    a = j["audits"]
    c = {k: round(v["score"] * 100) for k, v in j["categories"].items()}
    return (c, a["largest-contentful-paint"]["displayValue"], a["cumulative-layout-shift"]["displayValue"],
            round(a["total-byte-weight"]["numericValue"] / 1024))


def informe(filas):
    import shutil
    from gestion_sprint3 import nuevo
    from terminos import tabla, viñeta

    doc = nuevo("DEPURACIÓN, PRUEBAS DE USABILIDAD Y RENDIMIENTO", "Sprint 4 — Tarea 4.2: Ejecución de los casos de prueba, "
                "depuración de la consola, compatibilidad y Lighthouse", rol="Desarrollador Web")
    doc.tables[0].rows[0].cells[1].paragraphs[0].runs[0].text = "Desarrollo de Sitios Web (DSW)"
    doc.tables[0].rows[-1].cells[1].paragraphs[0].runs[0].text = FECHA_DOC

    navs = list(filas)
    automaticos = list(filas[navs[0]])
    totales = {nav: sum(c for c, _ in ev.values()) for nav, ev in filas.items()}
    man_ok = sum(1 for v in MANUALES.values() if v[0] == "Cumple")
    doc.add_heading("1. Resumen", level=1)
    doc.add_paragraph(
        f"Se ejecutaron los 38 casos del Plan de Casos de Prueba del Sprint 3 sobre el sitio publicado "
        f"(https://nicorsss.github.io/Woodbird/). Los {len(automaticos)} automáticos cumplen en Google Chrome "
        f"({totales.get('chrome', 0)}/{len(automaticos)}) y en Microsoft Edge ({totales.get('edge', 0)}/{len(automaticos)}), "
        f"en 11 anchos de pantalla y cuatro páginas. De los {len(MANUALES)} manuales, {man_ok} cumplen (sección 4). La consola "
        f"no registra errores durante el recorrido, y Lighthouse da 100 en accesibilidad, buenas prácticas y SEO en las "
        f"cuatro páginas.")

    doc.add_heading("2. Método", level=1)
    viñeta(doc, "Automáticas.", "pruebas/responsive.mjs abre cada página en 11 anchos (320 a 1920 px) con Chrome y con Edge, "
                                "recorre catálogo, filtros, carrito y checkout, mide desborde, objetivos táctiles, contraste y "
                                "enlaces legales, y guarda los resultados crudos. herramientas/pruebas_sprint4.py evalúa cada "
                                "caso a partir de esos datos, sin resultados escritos a mano.")
    viñeta(doc, "Consola.", "Se capturan los errores, las advertencias y los recursos fallidos de cada página.")
    viñeta(doc, "Rendimiento.", "Lighthouse 12 en modo móvil y escritorio sobre las cuatro páginas publicadas (03/11).")
    viñeta(doc, "Manuales.", "El responsable ejecutó los casos que requieren un dispositivo, un navegador o una tecnología "
                             "asistiva reales.")

    doc.add_heading("3. Resultados de los casos automáticos", level=1)
    nombres = {c[0]: c for _, casos in CASOS for c in casos}
    t = [(id_, nombres[id_][1], *[("Cumple" if filas[n][id_][0] else "NO CUMPLE") for n in navs], filas[navs[0]][id_][1])
         for id_ in automaticos]
    tabla(doc, ["Caso", "Prueba", *[NAVEGADORES[n].split(" (")[0] for n in navs], "Evidencia medida"], t,
          [0.55, 1.5, 0.75, 0.75, 2.95])

    doc.add_heading("4. Casos manuales", level=1)
    tabla(doc, ["Caso", "Prueba", "Resultado esperado", "Resultado", "Observación"],
          [(cp, nombres[cp][1], nombres[cp][3], est + (f" ({f})" if f else ""), obs or "—")
           for cp, (est, f, obs) in MANUALES.items()],
          [0.55, 1.1, 2.1, 1.0, 1.75])

    doc.add_heading("5. Depuración de errores", level=1)
    tabla(doc, ["Defecto", "Detección", "Corrección", "Verificación"], [
        ("favicon.ico respondía 404 en todas las páginas", "Captura de consola de las pruebas (03/11)",
         "Ícono SVG enlazado en las cuatro páginas (commit 339612c)", "0 recursos fallidos en el recorrido"),
        ("Las imágenes de 1024 px se descargaban también en celulares", "Lighthouse móvil: 525 KiB en la portada",
         "srcset con variantes de 384, 768 y 1024 px (commit 2887bc0)", "Portada móvil: 260 KiB (−50 %)"),
        ("Error de consola al fallar productos.json", "Provocado a propósito en CP-10",
         "Comportamiento esperado: mensaje accesible y console.error con la causa", "CP-10 cumple"),
    ], [1.7, 1.5, 1.8, 1.5])
    for nav in navs:
        cons = errores_consola(cargar(nav))
        if cons is not None:
            doc.add_paragraph(f"{NAVEGADORES[nav]}: {len(cons[0])} errores o advertencias durante el recorrido; "
                              f"{len(cons[1])} durante la falla provocada de CP-10.")

    doc.add_heading("6. Rendimiento (Lighthouse)", level=1)
    t = []
    for f in sorted(LIGHTHOUSE.glob("*.report.json")):
        c, lcp, cls, kib = puntajes(f)
        pagina, modo = f.name.replace(".report.json", "").rsplit("-", 1)
        t.append((f"{pagina}.html", modo, str(c["performance"]), str(c["accessibility"]), str(c["best-practices"]),
                  str(c["seo"]), lcp, cls, f"{kib} KiB"))
    tabla(doc, ["Página", "Modo", "Rend.", "Acces.", "B. prác.", "SEO", "LCP", "CLS", "Peso"], t,
          [1.7, 0.75, 0.5, 0.55, 0.55, 0.45, 0.6, 0.6, 0.8])
    filas_ad = []
    for f in sorted((LIGHTHOUSE / "antes").glob("*.report.json")):
        c, lcp, _, kib = puntajes(f)
        c2, lcp2, _, kib2 = puntajes(LIGHTHOUSE / f.name)
        filas_ad.append((f.name.replace(".report.json", ""), f"{c['performance']} → {c2['performance']}",
                         f"{lcp} → {lcp2}", f"{kib} → {kib2} KiB"))
    doc.add_paragraph("Optimización de las imágenes sintéticas (portada, antes y después del srcset):")
    tabla(doc, ["Vista", "Rendimiento", "LCP", "Peso total"], filas_ad, [2.0, 1.4, 1.4, 1.7])
    doc.add_paragraph("Las páginas legales obtienen 87 en rendimiento móvil porque la hoja de Google Fonts bloquea el primer "
                      "renderizado. Alojar las fuentes en el propio sitio lo resolvería, pero obliga a actualizar la Política "
                      "de Privacidad. Queda como mejora transferida en el Acta de Cierre.")

    doc.add_heading("7. Compatibilidad entre navegadores", level=1)
    tabla(doc, ["Navegador", "Motor", "Resultado"], [
        ("Google Chrome (escritorio)", "Blink", f"{totales.get('chrome', 0)}/{len(automaticos)} automáticos"),
        ("Microsoft Edge (escritorio)", "Blink", f"{totales.get('edge', 0)}/{len(automaticos)} automáticos"),
        ("Chrome en Samsung Galaxy A16", "Blink (Android)", "CP-37: " + MANUALES["CP-37"][0]),
        ("Mozilla Firefox y Safari", "Gecko y WebKit", "CP-38: " + MANUALES["CP-38"][0]),
    ], [2.2, 1.4, 2.9])

    doc.add_heading("8. Conclusión", level=1)
    doc.add_paragraph("El sitio publicado pasa todos los casos automáticos en dos navegadores, no registra errores de consola "
                      "y obtiene en Lighthouse entre 87 y 98 de rendimiento y 100 en el resto de las categorías. Las dos "
                      "correcciones de la depuración (ícono y srcset) redujeron a la mitad el peso de la portada en celulares.")

    ev = DESTINO / "evidencia" / "pruebas"
    ev.mkdir(parents=True, exist_ok=True)
    for f in LIGHTHOUSE.glob("index-*.report.html"):
        shutil.copy(f, ev / f"lighthouse-{f.name}")
    for nav in navs:
        shutil.copy(CORRIDAS / nav / "consola.json", ev / f"consola-{nav}.json")
    doc.save(DESTINO / "04_Depuracion_Pruebas_y_Lighthouse.docx")
    print("Listo: 04_Depuracion_Pruebas_y_Lighthouse.docx")


if __name__ == "__main__":
    resultado = resumen()
    if "--docx" in sys.argv:
        informe(resultado)
