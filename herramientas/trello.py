# Operaciones acotadas sobre el tablero Trello de Woodbird (iGCwIo1k).
# Uso:
#   python trello.py listar
#   python trello.py mover "<inicio del nombre>" "<lista>"     (a "Hecho" también marca el vencimiento como cumplido)
#   python trello.py comentar "<inicio del nombre>" "<texto>"
#   python trello.py etiquetar "<inicio del nombre>" "<etiqueta>"
#   python trello.py crear "<nombre>" "<lista>" "<AAAA-MM-DD>" ["<descripción>"]   (responsable: Nicolás Reiss)
# Credenciales: TRELLO_KEY y TRELLO_TOKEN en ~/.trello.env (nunca se muestran).
import json, os, sys, urllib.request

TABLERO = "iGCwIo1k"
sys.stdout.reconfigure(encoding="utf-8")


def credenciales():
    env = {}
    with open(os.path.expanduser("~/.trello.env"), encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if "=" in linea and not linea.startswith("#"):
                k, v = linea.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env["TRELLO_KEY"], env["TRELLO_TOKEN"]


KEY, TOKEN = credenciales()


def api(metodo, ruta, cuerpo=None):
    sep = "&" if "?" in ruta else "?"
    req = urllib.request.Request(
        f"https://api.trello.com/1/{ruta}{sep}key={KEY}&token={TOKEN}", method=metodo,
        data=json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None,
        headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def listas():
    return {l["name"]: l["id"] for l in api("GET", f"boards/{TABLERO}/lists")}


def tarjeta(prefijo):
    candidatas = [c for c in api("GET", f"boards/{TABLERO}/cards?fields=name,idList")
                  if c["name"].lower().startswith(prefijo.lower())]
    if len(candidatas) != 1:
        sys.exit(f"Se esperaba una tarjeta que empiece con «{prefijo}» y hay {len(candidatas)}: "
                 + "; ".join(c["name"] for c in candidatas))
    return candidatas[0]


def main(args):
    if args[:1] == ["listar"]:
        nombres = {v: k for k, v in listas().items()}
        for c in api("GET", f"boards/{TABLERO}/cards?fields=name,idList,due,dueComplete"):
            due = c["due"][:10] if c["due"] else "—"
            print(f"{nombres[c['idList']]} | {c['name']} | {due}{' ✓' if c['dueComplete'] else ''}")
    elif len(args) == 3 and args[0] == "mover":
        c, ids = tarjeta(args[1]), listas()
        if args[2] not in ids:
            sys.exit(f"Lista inexistente. Opciones: {', '.join(ids)}")
        cambios = {"idList": ids[args[2]], "pos": "top"}
        if args[2] == "Hecho":
            cambios["dueComplete"] = True
        api("PUT", f"cards/{c['id']}", cambios)
        print(f"Movida a «{args[2]}»: {c['name']}")
    elif len(args) == 3 and args[0] == "comentar":
        c = tarjeta(args[1])
        api("POST", f"cards/{c['id']}/actions/comments", {"text": args[2]})
        print(f"Comentario agregado en: {c['name']}")
    elif len(args) == 3 and args[0] == "etiquetar":
        c = tarjeta(args[1])
        etiquetas = {l["name"]: l["id"] for l in api("GET", f"boards/{TABLERO}/labels")}
        if args[2] not in etiquetas:
            sys.exit(f"Etiqueta inexistente. Opciones: {', '.join(n for n in etiquetas if n)}")
        api("POST", f"cards/{c['id']}/idLabels", {"value": etiquetas[args[2]]})
        print(f"Etiqueta «{args[2]}» en: {c['name']}")
    elif len(args) in (4, 5) and args[0] == "crear":
        ids = listas()
        if args[2] not in ids:
            sys.exit(f"Lista inexistente. Opciones: {', '.join(ids)}")
        existentes = api("GET", f"boards/{TABLERO}/cards?fields=name")
        if any(c["name"] == args[1] for c in existentes):
            sys.exit(f"Ya existe una tarjeta llamada «{args[1]}»")
        miembros = [m["id"] for m in api("GET", f"boards/{TABLERO}/members") if m["username"] == "nicolasreiss"]
        nueva = {"name": args[1], "idList": ids[args[2]], "due": f"{args[3]}T21:00:00.000Z",
                 "dueComplete": args[2] == "Hecho", "idMembers": miembros, "pos": "top"}
        if len(args) == 5:
            nueva["desc"] = args[4]
        api("POST", "cards", nueva)
        print(f"Creada en «{args[2]}»: {args[1]}")
    else:
        sys.exit(__doc__ or "Uso: listar | mover <tarjeta> <lista> | comentar <tarjeta> <texto> | etiquetar <tarjeta> <etiqueta> | crear <nombre> <lista> <AAAA-MM-DD> [<descripción>]")


main(sys.argv[1:])
