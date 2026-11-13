"""Pruebas de integridad de los datos reales (DP-01) — CP-35 y CP-36.

Casos NUEVOS propuestos por el ingeniero de pruebas automatizadas, no
incluidos en la versión 1.0 del plan. Se incorporan a la matriz de
trazabilidad como R-02 → CDP-03 → CP-35 y R-04 → CDP-06 → CP-36.
"""
import pandas as pd

VARIABLES = ["Aire", "Ríos", "Ruido", "Basuras", "Contaminación Visual"]
CATEGORIAS = {"Muy buena", "Buena", "Aceptable", "Mala", "Muy mala", "No sabe"}


def test_cp35_valores_reales_pertenecen_al_catalogo_de_6_categorias(ecv):
    """Cada respuesta del Excel debe ser una de las 6 categorías esperadas."""
    for variable in VARIABLES:
        desconocidos = set(ecv[variable].dropna().unique()) - CATEGORIAS
        assert not desconocidos, f"{variable}: valores fuera del catálogo {desconocidos}"
        assert ecv[variable].isna().sum() == 0, f"{variable}: tiene nulos"


def test_cp35b_map_categoria_es_identidad_sobre_datos_reales(dash, ecv):
    """Ninguna respuesta real cae por error en la rama 'No sabe' de map_categoria."""
    for variable in VARIABLES:
        for valor in ecv[variable].unique():
            assert dash["map_categoria"](valor) == valor, f"{variable}: {valor!r}"


def test_cp36_estrato_real_es_entero_entre_1_y_6_sin_nulos(ecv):
    """Hoy el Excel guarda enteros: DEF-001 (CP-18) es latente, no activo."""
    estrato = ecv["11. Estrato"]
    assert estrato.isna().sum() == 0
    assert pd.api.types.is_integer_dtype(estrato)
    assert set(estrato.unique()) <= {1, 2, 3, 4, 5, 6}
