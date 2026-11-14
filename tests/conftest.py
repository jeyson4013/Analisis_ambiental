"""Fixtures compartidas de las pruebas del Dashboard Ambiental Medellín.

Plan de pruebas PP-DAM-2026-001 (pruebasdesoftware.md), sección 5.4:
dashboard.py ejecuta la interfaz de Streamlit al importarse, así que NO se
importa. En su lugar se leen del archivo real las funciones puras y las
constantes que necesitan las pruebas (con `ast`) y se ejecutan aisladas.
De esa forma:
  - dashboard.py no se modifica;
  - las pruebas siempre ejercitan el código vigente, no una copia.
"""
import ast
import re
import unicodedata
from difflib import get_close_matches
from pathlib import Path

import pandas as pd
import plotly.express as px
import pytest

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DASHBOARD = RAIZ / "dashboard.py"
RUTA_EXCEL = RAIZ / "ECV_2025_Limpio.xlsx"

FUNCIONES = {
    "limpiar",
    "encontrar_mejor_match",
    "map_categoria",
    "centroide_feature",
    "bounds_from_features",
    "figuras_estadisticas_barrio",
}
CONSTANTES = {"variables", "COLOR_MAP_CATEG", "CAT_ORDER"}


def _cargar_codigo_puro() -> dict:
    arbol = ast.parse(RUTA_DASHBOARD.read_text(encoding="utf-8"))
    seleccion, encontrados = [], set()
    for nodo in arbol.body:
        if isinstance(nodo, ast.FunctionDef) and nodo.name in FUNCIONES:
            seleccion.append(nodo)
            encontrados.add(nodo.name)
        elif isinstance(nodo, ast.Assign):
            for destino in nodo.targets:
                if isinstance(destino, ast.Name) and destino.id in CONSTANTES:
                    seleccion.append(nodo)
                    encontrados.add(destino.id)
    faltantes = (FUNCIONES | CONSTANTES) - encontrados
    assert not faltantes, (
        "dashboard.py ya no define: " + ", ".join(sorted(faltantes))
        + ". Si se renombraron, actualizar FUNCIONES/CONSTANTES en tests/conftest.py."
    )
    espacio = {
        "pd": pd, "px": px, "re": re,
        "unicodedata": unicodedata, "get_close_matches": get_close_matches,
    }
    modulo = ast.Module(body=seleccion, type_ignores=[])
    exec(compile(modulo, str(RUTA_DASHBOARD), "exec"), espacio)
    return espacio


@pytest.fixture(scope="session")
def dash():
    """Espacio de nombres con las funciones puras de dashboard.py."""
    return _cargar_codigo_puro()


@pytest.fixture(scope="session")
def ecv():
    """DataFrame real del Excel (DP-01), tal como lo lee cargar_datos()."""
    return pd.read_excel(RUTA_EXCEL)
