# Generación de las imágenes del catálogo de Woodbird con la API de Gemini.
# Uso:
#   python imagenes_ia.py modelos                        (lista los modelos que generan imágenes)
#   python imagenes_ia.py generar <archivo> [<modelo>]   (p. ej. generar cardenal)
#   python imagenes_ia.py todas [<modelo>]               (las que todavía no existen)
#   python imagenes_ia.py importar <archivo> <url o ruta> [<herramienta>] [<modelo>]
#       (guarda una imagen generada fuera de la API, p. ej. con Buzzy o la app de Gemini, y la registra)
#   python imagenes_ia.py carpeta [<herramienta>] [<modelo>]
#       (importa imagenes_nuevas/<archivo>.png|jpg|jpeg|jfif|webp; por defecto, app de Gemini)
# Credencial: GEMINI_API_KEY en ~/.gemini.env (nunca se muestra).
# Cada imagen queda en sitio/assets/img/<archivo>.webp y se anota en imagenes_ia_registro.json
# (herramienta, modelo, fecha y prompt), como exige la Declaración Ética.
import base64, io, json, os, sys, urllib.error, urllib.request
from datetime import datetime
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(AQUI, "..", "sitio", "assets", "img")
REGISTRO = os.path.join(AQUI, "imagenes_ia_registro.json")
MODELO = "gemini-2.5-flash-image"
API = "https://generativelanguage.googleapis.com/v1beta"

CIERRE = ("Plain seamless white background, soft diffused studio lighting, gentle shadow under the base, "
          "{vista}, square format, sharp focus, e-commerce catalog style.")
PROMPTS = {
    "cardenal": "Professional product photograph of a handcrafted wooden sculpture of a red-crested cardinal (Paroaria coronata), carved from a single piece of palo santo wood with its natural olive-green tone and fine grain. The crest is carved with visible gouge marks, the chest is smoothly polished, beeswax finish with a soft satin sheen. The crest is the same olive wood tone as the body, with no red and no paint of any kind. Unpainted, natural wood color only. The bird stands on a small integrated wooden base.",
    "hornero": "Professional product photograph of a handcrafted wooden sculpture of a rufous hornero (Furnarius rufus) singing with its beak open and head raised, carved from Argentine algarrobo wood, warm medium brown with dark grain streaks that follow the curve of the back and wings. Unpainted, natural wood color only. The bird stands on a small integrated wooden base.",
    "carpintero": "Professional product photograph of a monochrome wooden sculpture carved entirely from one single block of red quebracho wood, every part the same dense reddish-brown color with fine grain, like an unpainted museum woodcarving. The sculpture shows a stylized woodpecker clinging vertically to a short carved tree trunk, with a long pointed beak and stiff tail pressed against the trunk. The head, face, crest and neck are plain bare wood exactly like the body, with feather details shown only by carved lines and texture, never by color. No paint, no stain, no dye, no colored markings anywhere. The trunk rests on a flat wooden base.",
    "chuna": "Professional product photograph of a handcrafted wooden sculpture of a red-legged seriema (Cariama cristata) in a walking pose, with long neck and the small upright crest of feathers on its forehead, carved from a single piece of palo santo wood with natural olive-green tone, no joints. Unpainted, natural wood color only. The bird stands on a small integrated wooden base.",
    "benteveo": "Professional product photograph of a handcrafted wooden sculpture of a great kiskadee (Pitangus sulphuratus) perched on a short carved branch, carved from Argentine algarrobo wood, warm medium brown with dark grain. The head stripe is suggested only by a subtle change of surface texture. Unpainted, natural wood color only. The branch rests on a small wooden base.",
    "tero": "Professional product photograph of a handcrafted wooden sculpture of a southern lapwing (Vanellus chilensis) in an alert guarding stance with wings slightly open, carved from red quebracho wood, dense reddish-brown with fine grain, standing on a natural-edge slice of log as a base. Unpainted, natural wood color only.",
    "calandria": "Professional product photograph of a slender handcrafted wooden sculpture of a chalk-browed mockingbird (Mimus saturninus) with its long tail extended, carved from palo santo wood with natural olive-green tone, fine elegant lines. Unpainted, natural wood color only. The bird stands on a small integrated wooden base.",
    "picaflor": "Professional product photograph of a small handcrafted wooden sculpture of a hummingbird hovering in flight with wings spread, held up by a thin wooden rod rising from a small round base, carved from Argentine algarrobo wood, warm medium brown with dark grain. Unpainted, natural wood color only.",
    "lechucita": "Professional product photograph of a handcrafted wooden sculpture of a burrowing owl (Athene cunicularia) facing forward, with large round eyes carved in low relief, carved from red quebracho wood, dense reddish-brown, matte linseed oil finish. Unpainted, natural wood color only. The owl stands on a small integrated wooden base.",
    "tucan": "Professional product photograph of a large handcrafted wooden sculpture of a toco toucan (Ramphastos toco) perched in profile, its huge beak taking up almost half of the figure and carved from the lighter sapwood area, body carved from palo santo wood with natural olive-green tone. Unpainted, natural wood color only, the only color contrast comes from the wood itself. The bird perches on a short wooden branch on a base.",
    "zorzal": "Professional product photograph of a handcrafted wooden sculpture of a rufous-bellied thrush (Turdus rufiventris) with its head tilted to one side, carved from Argentine algarrobo wood, warm medium brown, the chest showing the natural untinted wood grain. Unpainted, natural wood color only. The bird stands on a small integrated wooden base.",
    "garza": "Professional product photograph of a tall handcrafted wooden sculpture of a great egret (Ardea alba) standing on one leg with a long S-curved neck, carved from red quebracho wood, dense reddish-brown with fine grain, on a wide wooden base for stability. Unpainted, natural wood color only, not white.",
}
VISTAS = {"lechucita": "front view", "tucan": "side profile view"}


def clave():
    with open(os.path.expanduser("~/.gemini.env"), encoding="utf-8-sig") as f:
        for linea in f:
            linea = linea.strip()
            if linea.startswith("GEMINI_API_KEY="):
                return linea.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("Falta GEMINI_API_KEY en ~/.gemini.env")


def api(ruta, cuerpo=None):
    req = urllib.request.Request(
        f"{API}/{ruta}", method="POST" if cuerpo is not None else "GET",
        data=json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None,
        headers={"Content-Type": "application/json; charset=utf-8", "x-goog-api-key": clave()})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        error = json.loads(e.read() or b"{}").get("error", {})
        sys.exit(f"Error {e.code} ({error.get('status', '')}): {error.get('message', '')}")


def prompt_de(nombre):
    return PROMPTS[nombre] + " " + CIERRE.format(vista=VISTAS.get(nombre, "three-quarter view"))


def modelos():
    for m in api("models?pageSize=200")["models"]:
        if "image" in m["name"] and "generateContent" in m.get("supportedGenerationMethods", []):
            print(m["name"].removeprefix("models/"), "|", m.get("displayName", ""))


def generar(nombre, modelo=MODELO):
    prompt = prompt_de(nombre)
    r = api(f"models/{modelo}:generateContent", {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}},
    })
    partes = r.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    datos = next((p["inlineData"]["data"] for p in partes if "inlineData" in p), None)
    if not datos:
        sys.exit(f"{nombre}: el modelo no devolvió imagen ({r.get('candidates', [{}])[0].get('finishReason', r.get('promptFeedback'))})")
    guardar(nombre, base64.b64decode(datos), "Google Gemini API", modelo, prompt)


def importar(nombre, url, herramienta="Buzzy", modelo="Nano Banana 2"):
    if nombre not in PROMPTS:
        sys.exit(f"Archivo desconocido: {nombre}")
    if os.path.exists(url):
        with open(url, "rb") as f:
            crudo = f.read()
    else:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "woodbird-imagenes"}), timeout=120) as r:
            crudo = r.read()
    guardar(nombre, crudo, herramienta, modelo, prompt_de(nombre))


def carpeta(herramienta="Google Gemini (app)", modelo="Nano Banana"):
    origen = os.path.join(AQUI, "imagenes_nuevas")
    for archivo in sorted(os.listdir(origen)):
        nombre, ext = os.path.splitext(archivo)
        if ext.lower() in (".png", ".jpg", ".jpeg", ".jfif", ".webp"):
            if nombre.lower() not in PROMPTS:
                print(f"Se ignora {archivo}: el nombre no coincide con ningún producto")
                continue
            importar(nombre.lower(), os.path.join(origen, archivo), herramienta, modelo)


# Tarea 4.2: las tarjetas muestran la imagen a 376 px como máximo, así que además del original de 1024 px se
# guardan versiones de 384 y 768 px (pantallas de alta densidad) que el sitio ofrece con srcset.
ANCHOS = (384, 768)


def variantes(img, nombre):
    for ancho in ANCHOS:
        copia = img.copy()
        copia.thumbnail((ancho, ancho), Image.LANCZOS)
        copia.save(os.path.join(DESTINO, f"{nombre}-{ancho}.webp"), "WEBP", quality=80)


def guardar(nombre, crudo, herramienta, modelo, prompt):
    img = Image.open(io.BytesIO(crudo)).convert("RGB")
    img.thumbnail((1024, 1024))
    os.makedirs(DESTINO, exist_ok=True)
    ruta = os.path.join(DESTINO, f"{nombre}.webp")
    img.save(ruta, "WEBP", quality=82)
    variantes(img, nombre)

    registro = json.load(open(REGISTRO, encoding="utf-8")) if os.path.exists(REGISTRO) else []
    registro = [e for e in registro if e["archivo"] != f"{nombre}.webp"]
    registro.append({"archivo": f"{nombre}.webp", "herramienta": herramienta, "modelo": modelo,
                     "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "prompt": prompt})
    with open(REGISTRO, "w", encoding="utf-8") as f:
        json.dump(sorted(registro, key=lambda e: list(PROMPTS).index(e["archivo"][:-5])), f, ensure_ascii=False, indent=2)
    print(f"{nombre}.webp ({img.width}x{img.height}, {os.path.getsize(ruta) // 1024} KB)")


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else ""
    if accion == "modelos":
        modelos()
    elif accion == "generar" and len(sys.argv) > 2:
        generar(sys.argv[2], *sys.argv[3:4])
    elif accion == "importar" and len(sys.argv) > 3:
        importar(sys.argv[2], sys.argv[3], *sys.argv[4:6])
    elif accion == "carpeta":
        carpeta(*sys.argv[2:4])
    elif accion == "variantes":  # rehace las versiones chicas a partir de las imágenes ya publicadas
        for nombre in PROMPTS:
            ruta = os.path.join(DESTINO, f"{nombre}.webp")
            if os.path.exists(ruta):
                variantes(Image.open(ruta).convert("RGB"), nombre)
                print(nombre, *(f"{a}px {os.path.getsize(os.path.join(DESTINO, f'{nombre}-{a}.webp')) // 1024} KB" for a in ANCHOS))
    elif accion == "todas":
        for nombre in PROMPTS:
            if not os.path.exists(os.path.join(DESTINO, f"{nombre}.webp")):
                generar(nombre, *sys.argv[2:3])
    else:
        sys.exit(__doc__ or "Uso: python imagenes_ia.py modelos | generar <archivo> [<modelo>] | todas [<modelo>] | variantes")
