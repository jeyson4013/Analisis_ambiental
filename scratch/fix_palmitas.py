import json

with open('medellin_debug.geojson', 'r', encoding='utf-8') as f:
    geo = json.load(f)

corregidos = []
for feat in geo['features']:
    props = feat.get('properties', {})
    nombre = str(props.get('NOMBRE', '')).upper()
    if nombre in ('LA SUCIA', 'LA FRISOLA'):
        anterior = props['Comuna']
        props['Comuna'] = 'PALMITAS'
        corregidos.append(f"{nombre}: {anterior} -> PALMITAS")

with open('medellin_debug.geojson', 'w', encoding='utf-8') as f:
    json.dump(geo, f, ensure_ascii=False)

print("Correcciones realizadas:")
for c in corregidos:
    print(f"  {c}")

# Verificar
print("\nVerificacion:")
with open('medellin_debug.geojson', 'r', encoding='utf-8') as f:
    geo2 = json.load(f)
for feat in geo2['features']:
    props = feat.get('properties', {})
    nombre = str(props.get('NOMBRE', '')).upper()
    if nombre in ('LA SUCIA', 'LA FRISOLA', 'PALMITAS SECTOR CENTRAL'):
        print(f"  {nombre} -> {props['Comuna']}")
