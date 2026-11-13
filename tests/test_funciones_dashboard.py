"""Pruebas unitarias automatizadas (A-08) — plan PP-DAM-2026-001.

Cubre CP-01 a CP-14, CP-17 y CP-18 (responsable: ingeniero de pruebas
automatizadas) más pruebas opcionales de TI-06 (R-09).

Ejecutar desde la raíz del repositorio:  pytest -v
"""
import math

import pandas as pd
import pytest
from difflib import SequenceMatcher

VARIABLES = ["Aire", "Ríos", "Ruido", "Basuras", "Contaminación Visual"]


def df_barrio(respuestas, estratos=None, variable="Aire"):
    """DataFrame sintético (DP-03): `respuestas` va en `variable`; el resto de
    variables y el estrato (por defecto 3) se rellenan con valores neutros."""
    n = len(respuestas)
    datos = {v: ["Buena"] * n for v in VARIABLES}
    datos[variable] = list(respuestas)
    datos["11. Estrato"] = list(estratos) if estratos is not None else [3] * n
    return pd.DataFrame(datos)


# ───────────────────── R-01 · limpiar() / encontrar_mejor_match() ─────────────────────

def test_cp01_limpiar_tildes_y_mayusculas(dash):
    assert dash["limpiar"]("Laureles Estadío") == "LAURELES ESTADIO"


def test_cp02_limpiar_simbolos_y_espacios(dash):
    assert dash["limpiar"]("  La  Candelaria!! ") == "LA CANDELARIA"


@pytest.mark.parametrize("entrada", ["", None])
def test_cp03_limpiar_vacio_y_nulo(dash, entrada):
    assert dash["limpiar"](entrada) == ""


def test_cp04_limpiar_enie_y_guion(dash):
    assert dash["limpiar"]("Castilla-Ñ") == "CASTILLA N"


def test_cp05_match_valor_limite_del_cutoff(dash):
    """AVL sobre cutoff=0.7: similitud exactamente 0.7 acepta; 0.6 rechaza."""
    candidato = "ABCDEFGHIJ"
    en_limite, bajo_limite = "ABCDEFGXXX", "ABCDEFXXXX"
    assert SequenceMatcher(None, en_limite, candidato).ratio() == pytest.approx(0.7)
    assert SequenceMatcher(None, bajo_limite, candidato).ratio() == pytest.approx(0.6)
    assert dash["encontrar_mejor_match"](en_limite, [candidato]) == candidato
    assert dash["encontrar_mejor_match"](bajo_limite, [candidato]) is None


def test_cp05b_match_texto_vacio_devuelve_none(dash):
    assert dash["encontrar_mejor_match"]("", ["CENTRO"]) is None
    assert dash["encontrar_mejor_match"](None, ["CENTRO"]) is None


def test_cp05c_match_normaliza_antes_de_comparar(dash):
    assert dash["encontrar_mejor_match"]("Belén", ["BELEN"]) == "BELEN"


# ───────────────────────────── R-02 · map_categoria() ─────────────────────────────

@pytest.mark.parametrize("entrada, esperado", [
    ("Muy buena", "Muy buena"), ("MUY BUENA", "Muy buena"),
    ("Buena", "Buena"), ("buena ", "Buena"),
    ("Aceptable", "Aceptable"), ("Regular", "Aceptable"),
    ("Muy mala", "Muy mala"),
    ("Mala", "Mala"),
])
def test_cp08_map_categoria_clases_validas(dash, entrada, esperado):
    assert dash["map_categoria"](entrada) == esperado


@pytest.mark.parametrize("entrada", [float("nan"), None, pd.NA, "", "NS/NR", "No sabe"])
def test_cp09_map_categoria_invalidos_son_no_sabe(dash, entrada):
    assert dash["map_categoria"](entrada) == "No sabe"


@pytest.mark.parametrize("entrada", ["MUY MALA", "Muy Mala "])
def test_cp10_muy_mala_no_se_confunde_con_mala(dash, entrada):
    assert dash["map_categoria"](entrada) == "Muy mala"


# ─────────────── R-03 · % de percepción negativa (figuras_estadisticas_barrio) ───────────────

def porcentaje_negativo(dash, df, variable="Aire"):
    fig1, _, _ = dash["figuras_estadisticas_barrio"](df, [variable])
    assert fig1 is not None
    return float(fig1.data[0].x[0])


def test_cp11_cero_negativas_da_cero_por_ciento(dash):
    assert porcentaje_negativo(dash, df_barrio(["Buena"] * 10)) == 0.0


def test_cp12_todas_negativas_da_cien_por_ciento(dash):
    assert porcentaje_negativo(dash, df_barrio(["Mala"] * 5 + ["Muy mala"] * 5)) == 100.0


def test_cp13_un_tercio_negativo(dash):
    """1 Mala + 1 Buena + 1 No sabe → 33.3 (el denominador incluye 'No sabe')."""
    assert porcentaje_negativo(dash, df_barrio(["Mala", "Buena", "No sabe"])) == 33.3


def test_cp14_dataframe_vacio_devuelve_tres_none(dash):
    vacio = df_barrio([])
    assert vacio.empty
    assert dash["figuras_estadisticas_barrio"](vacio, ["Aire"]) == (None, None, None)


# ───────────────────────── R-04 · etiquetas de estrato ─────────────────────────

def etiquetas_estrato(dash, estratos):
    _, fig2, _ = dash["figuras_estadisticas_barrio"](
        df_barrio(["Buena"] * len(estratos), estratos=estratos), ["Aire"]
    )
    assert fig2 is not None
    return {str(x) for traza in fig2.data for x in traza.x}


def test_cp17_estratos_enteros(dash):
    assert etiquetas_estrato(dash, [1, 2, 3]) == {"Estrato 1", "Estrato 2", "Estrato 3"}


@pytest.mark.xfail(
    strict=True,
    reason="DEF-001 (R-04): con estrato decimal (1.0) str(x).isdigit() es False y la "
           "etiqueta queda '1.0' en vez de 'Estrato 1'. Quitar este xfail al corregirlo.",
)
def test_cp18_estratos_decimales(dash):
    etiquetas = etiquetas_estrato(dash, [1.0, 2.0, 2.0, 1.0])
    assert {"Estrato 1", "Estrato 2"} <= etiquetas


# ───────────────────── TI-06 · geometría (R-09, prueba opcional) ─────────────────────

CUADRADO = [[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]


def test_ti06_centroide_poligono(dash):
    feat = {"geometry": {"type": "Polygon", "coordinates": [CUADRADO]}}
    lat, lng = dash["centroide_feature"](feat)
    assert (lat, lng) == pytest.approx((0.8, 0.8))  # promedio simple de los 5 vértices


def test_ti06_centroide_multipoligono_usa_primer_poligono(dash):
    feat = {"geometry": {"type": "MultiPolygon", "coordinates": [[CUADRADO]]}}
    assert dash["centroide_feature"](feat) is not None


@pytest.mark.parametrize("feat", [
    {"geometry": {"type": "Point", "coordinates": [0, 0]}},
    {"geometry": None},
    {},
])
def test_ti06_centroide_geometria_no_soportada_devuelve_none(dash, feat):
    assert dash["centroide_feature"](feat) is None


def test_ti06_bounds_caja_envolvente(dash):
    feats = [{"geometry": {"type": "Polygon", "coordinates": [CUADRADO]}},
             {"geometry": {"type": "Polygon", "coordinates": [[[5, -1], [6, -1], [6, 1], [5, -1]]]}}]
    # GeoJSON es [lng, lat]; el resultado es [[lat_min, lng_min], [lat_max, lng_max]]
    assert dash["bounds_from_features"](feats) == [[-1.0, 0.0], [2.0, 6.0]]


def test_ti06_bounds_sin_geometrias_devuelve_none(dash):
    assert dash["bounds_from_features"]([]) is None
    assert dash["bounds_from_features"]([{"geometry": None}]) is None
