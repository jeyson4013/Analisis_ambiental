
import json

# Corrección: mapeo correcto basado en los datos del Excel
# Excel dice: estas veredas pertenecen a estos corregimientos
EXCEL_CORRECTO = {
    "PALMITAS": ["LA ALDEA", "LA SUIZA", "PALMITAS SECTOR CENTRAL", "POTRERA MISERENGA", "URQUITA", "VOLCANA GUAYABAL"],
    "SANTA ELENA": ["BARRO BLANCO", "EL CERRO", "EL PLACER", "LAS PALMAS", "MEDIA LUNA", "SANTA ELENA SECTOR CENTRAL"],
    "ALTAVISTA": ["AGUAS FRIAS", "ALTAVISTA SECTOR CENTRAL", "BUGA PATIO BONITO", "EL CORAZON EL MORRO", "EL JARDIN", "LA ESPERANZA", "SAN JOSE DEL MANZANILLO", "SAN PABLO", "AREA DE EXPANSION ALTAVISTA", "AREA DE EXPANSION BELEN RINCON"],
    "SAN CRISTOBAL": ["BOQUERON", "CABECERA URBANA CORREGIMIENTO SAN CRISTOBAL", "EDUARDO SANTOS", "EL LLANO", "EL PATIO", "EL PICACHO", "EL UVITO", "LA CUCHILLA", "LA ILUSION", "LA LOMA", "LA PALMA", "LAS PLAYAS", "PAJARITO", "PEDREGAL ALTO", "SAN JOSE DE LA MONTANA", "TRAVESIAS", "YOLOMBO", "AREA DE EXPANSION PAJARITO", "AREA DE EXPANSION SAN CRISTOBAL"],
    "SAN ANTONIO DE PRADO": ["EL SALADO", "LA FLORIDA", "LA VERDE", "MONTANITA", "POTRERITO", "SAN ANTONIO DE PRADO", "AREA DE EXPANSION SAN ANTONIO DE PRADO", "YARUMALITO", "SAN JOSE", "EL ASTILLERO"],
}

import unicodedata, re
def limpiar(t):
    if not t: return ""
    t = str(t).upper().strip()
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^A-Z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

# Crear mapa inverso: vereda_limpia -> corregimiento correcto
vereda_a_corregimiento = {}
for corr, veredas in EXCEL_CORRECTO.items():
    for v in veredas:
        vereda_a_corregimiento[limpiar(v)] = corr

with open("medellin_debug.geojson", "r", encoding="utf-8") as f:
    geo = json.load(f)

corregimientos = set(EXCEL_CORRECTO.keys())
fixed = 0
total_corr = 0

for feat in geo["features"]:
    props = feat["properties"]
    c_actual = props.get("Comuna", "")
    
    if c_actual in corregimientos:
        total_corr += 1
        nombre_limpio = limpiar(props.get("NOMBRE", ""))
        
        # Buscar el corregimiento correcto para esta vereda
        corr_correcto = vereda_a_corregimiento.get(nombre_limpio)
        
        if corr_correcto and corr_correcto != c_actual:
            print(f"CORRIGIENDO: '{props['NOMBRE']}' de {c_actual} -> {corr_correcto}")
            props["Comuna"] = corr_correcto
            fixed += 1

print(f"\nTotal polígonos en corregimientos: {total_corr}")
print(f"Corregidos: {fixed}")

with open("medellin_debug.geojson", "w", encoding="utf-8") as f:
    json.dump(geo, f)

print("GeoJSON guardado correctamente.")
