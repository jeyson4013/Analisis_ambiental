
import json

with open("medellin_debug.geojson", "r", encoding="utf-8") as f:
    geo = json.load(f)

buscar = ["NORAL", "CARMELO", "NARANJAL"]
print("=== Zonas a revisar ===")
for feat in geo["features"]:
    p = feat["properties"]
    nombre = p.get("NOMBRE", "")
    if any(b in nombre.upper() for b in buscar):
        print(f"NOMBRE: {nombre} | COMUNA: {p.get('Comuna', '')}")

print()
print("=== Estado actual de todos los corregimientos ===")
corregimientos = ["PALMITAS", "SANTA ELENA", "ALTAVISTA", "SAN CRISTOBAL", "SAN ANTONIO DE PRADO"]
for corr in corregimientos:
    zonas = [f["properties"]["NOMBRE"] for f in geo["features"] if f["properties"].get("Comuna") == corr]
    print(f"\n{corr}:")
    for z in sorted(zonas):
        print(f"  - {z}")
