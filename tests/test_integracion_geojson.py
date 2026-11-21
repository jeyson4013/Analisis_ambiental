"""Pruebas de integración GeoJSON ↔ Excel (CP-06, CP-07) — plan PP-DAM-2026-001, riesgo R-01 (Crítico).

dashboard.py hace el emparejamiento barrio→comuna a nivel de módulo (no en una función), así que
aquí se reproduce el mismo algoritmo (líneas "mapeo_jerarquico" de dashboard.py) usando las funciones
reales limpiar() y encontrar_mejor_match() extraídas por conftest.py. Si se cambia el algoritmo en
dashboard.py, hay que actualizar asignar_comunas() de este archivo.

Ejecutar desde la raíz:  python -m pytest tests/test_integracion_geojson.py -v
"""
import json
import re
from collections import defaultdict
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
RUTA_GEOJSON = RAIZ / "medellin_debug.geojson"


@pytest.fixture(scope="module")
def asignaciones(dash, ecv):
    limpiar, match = dash["limpiar"], dash["encontrar_mejor_match"]

    df = ecv[ecv["4. Ubicación geográfica - Municipio"].str.contains("Medell", na=False)].copy()
    df["6. Comuna o Corregimiento"] = df["6. Comuna o Corregimiento"].replace(
        {"LAURELES": "LAURELES ESTADIO", "Laureles": "LAURELES ESTADIO"})
    df["barrio"] = df["7. Barrio o Vereda"].fillna("Sin información")
    df["comuna"] = df["6. Comuna o Corregimiento"].fillna("Sin información")

    mapeo = {}
    for c, b in zip(df["comuna"], df["barrio"]):
        mapeo.setdefault((limpiar(c), limpiar(b)), c)
    comunas_norm = {limpiar(c): c for c in df["comuna"].dropna().unique()}

    resultado = []
    for f in json.loads(RUTA_GEOJSON.read_text(encoding="utf-8"))["features"]:
        p = f["properties"]
        b = limpiar(p.get("NOMBRE", ""))
        c_raw = p.get("Comuna")
        c = re.sub(r"COMUNA \d+ ", "", limpiar(c_raw)) if c_raw else "SIN INFORMACION"
        if (c, b) in mapeo:
            asignada = mapeo[(c, b)]
        else:
            mejor_b = match(b, [bb for (cc, bb) in mapeo if cc == c], cutoff=0.7)
            if mejor_b:
                asignada = mapeo[(c, mejor_b)]
            else:
                mejor_c = match(c, list(comunas_norm), cutoff=0.5)
                asignada = comunas_norm.get(mejor_c) if mejor_c else "Sin información"
        resultado.append({"barrio": p.get("NOMBRE"), "comuna_poligono": c, "comuna_asignada": asignada})
    return resultado, limpiar


def test_cp06_ningun_barrio_queda_en_comuna_ajena(asignaciones):
    """CP-06: cada polígono del GeoJSON recibe la comuna del Excel que corresponde a su propia comuna."""
    resultado, limpiar = asignaciones
    assert len(resultado) == 332
    errores = [r for r in resultado if limpiar(r["comuna_asignada"]) != r["comuna_poligono"]]
    assert errores == [], f"{len(errores)} barrios asignados a una comuna ajena: {errores[:10]}"


def test_cp07_barrios_homonimos_conservan_su_comuna(asignaciones):
    """CP-07: un nombre de barrio repetido en varias comunas no 'salta' a otra comuna."""
    resultado, limpiar = asignaciones
    por_nombre = defaultdict(list)
    for r in resultado:
        por_nombre[limpiar(r["barrio"])].append(r)
    homonimos = {n: rs for n, rs in por_nombre.items()
                 if len({r["comuna_poligono"] for r in rs}) > 1}
    for nombre, rs in homonimos.items():
        for r in rs:
            assert limpiar(r["comuna_asignada"]) == r["comuna_poligono"], (nombre, r)
