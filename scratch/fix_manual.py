
import json
import unicodedata, re

def limpiar(t):
    if not t: return ""
    t = str(t).upper().strip()
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^A-Z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

# Correcciones manuales: (nombre_vereda, comuna_actual) -> nueva_comuna
CORRECCIONES_MANUALES = {
    ("AREA DE EXPANSION EL NORAL", "SAN CRISTOBAL"): "ALTAVISTA",
    ("EL CARMELO", "ALTAVISTA"): "SAN CRISTOBAL",
    ("NARANJAL", "ALTAVISTA"): "SAN CRISTOBAL",
}

with open("medellin_debug.geojson", "r", encoding="utf-8") as f:
    geo = json.load(f)

fixed = 0
for feat in geo["features"]:
    p = feat["properties"]
    nombre_limpio = limpiar(p.get("NOMBRE", ""))
    comuna_actual = p.get("Comuna", "")
    
    key = (nombre_limpio, comuna_actual)
    if key in CORRECCIONES_MANUALES:
        nueva_comuna = CORRECCIONES_MANUALES[key]
        print(f"CORRIGIENDO: {p['NOMBRE']} de {comuna_actual} -> {nueva_comuna}")
        p["Comuna"] = nueva_comuna
        fixed += 1

print(f"\nTotal correcciones aplicadas: {fixed}")

with open("medellin_debug.geojson", "w", encoding="utf-8") as f:
    json.dump(geo, f)

print("GeoJSON guardado.")
