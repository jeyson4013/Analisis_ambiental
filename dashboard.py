
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import unicodedata
import re
import folium
from streamlit_folium import st_folium
from difflib import get_close_matches

st.set_page_config(page_title="Dashboard Ambiental Medellín", layout="wide")

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

if "barrio_click" not in st.session_state:
    st.session_state["barrio_click"] = None      # None = todos los barrios
if "map_center" not in st.session_state:
    st.session_state["map_center"] = [6.2442, -75.5812]
if "map_zoom" not in st.session_state:
    st.session_state["map_zoom"] = 12

# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────

def limpiar(texto):
    """Normaliza texto: mayúsculas, sin tildes, sin caracteres especiales."""
    if not texto:
        return ""
    texto = str(texto).upper().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^A-Z0-9 ]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def encontrar_mejor_match(barrio, lista, cutoff=0.7):
    barrio_lim = limpiar(barrio)
    matches = get_close_matches(barrio_lim, lista, n=1, cutoff=cutoff)
    return matches[0] if matches else None


def map_categoria(x):
    x = str(x).lower()
    if "muy buena" in x:
        return "Muy buena"
    elif "buena" in x:
        return "Buena"
    elif "aceptable" in x or "regular" in x:
        return "Aceptable"
    elif "muy mala" in x:
        return "Muy mala"
    elif "mala" in x:
        return "Mala"
    else:
        return "No sabe"


def centroide_feature(feat):
    """Devuelve [lat, lng] del centroide aproximado de un GeoJSON feature."""
    try:
        geom = feat["geometry"]
        coords = geom["coordinates"]
        if geom["type"] == "Polygon":
            pts = coords[0]
        elif geom["type"] == "MultiPolygon":
            pts = coords[0][0]
        else:
            return None
        lng = sum(p[0] for p in pts) / len(pts)
        lat = sum(p[1] for p in pts) / len(pts)
        return [lat, lng]
    except Exception:
        return None


# ─────────────────────────────────────────────
# CARGA DE DATOS (con caché para velocidad)
# ─────────────────────────────────────────────

@st.cache_data(show_spinner="Cargando datos del xlsx...")
def cargar_datos():
    df = pd.read_excel("ECV_2025_Limpio.xlsx")
    df = df[df["4. Ubicación geográfica - Municipio"].str.contains("Medell", na=False)]
    df["barrio"] = df["7. Barrio o Vereda"].fillna("Sin información")
    return df


@st.cache_data(show_spinner="Cargando GeoJSON de barrios...")
def cargar_geojson():
    url = (
        "https://raw.githubusercontent.com/juanfrans/estratosBogota/"
        "master/EstratosMedellin.geojson"
    )
    response = requests.get(url, timeout=30)
    geojson = response.json()
    for feature in geojson["features"]:
        nombre = feature["properties"].get("NOMBRE", "")
        feature["properties"]["barrio_limpio"] = limpiar(nombre)
    return geojson


# ─────────────────────────────────────────────
# CARGAR DATA
# ─────────────────────────────────────────────

df_base = cargar_datos()
geojson  = cargar_geojson()

barrios_geo = [f["properties"]["barrio_limpio"] for f in geojson["features"]]

# Mapa normalizado → nombre original del df (para fuzzy matching del click)
barrios_df_lista = df_base["barrio"].dropna().unique().tolist()
barrios_df_norm  = {limpiar(b): b for b in barrios_df_lista}

# ─────────────────────────────────────────────
# SIDEBAR — FILTRO DE ESTRATO
# ─────────────────────────────────────────────

st.sidebar.header("Filtros Globales")

estratos = st.sidebar.multiselect(
    "Selecciona Estrato",
    options=sorted(df_base["11. Estrato"].unique()),
    default=sorted(df_base["11. Estrato"].unique()),
)

st.sidebar.markdown("---")

# Leer barrio activo desde session_state
barrio_activo = st.session_state["barrio_click"]

if barrio_activo:
    st.sidebar.success(f"📍 **Barrio activo:**\n\n{barrio_activo}")
    if st.sidebar.button("❌ Limpiar selección del mapa", use_container_width=True):
        st.session_state["barrio_click"] = None
        st.session_state["map_center"]   = [6.2442, -75.5812]
        st.session_state["map_zoom"]     = 12
        st.rerun()
else:
    st.sidebar.info("Haz click en un barrio del mapa para filtrar las gráficas.")

# Aplicar filtro de estrato
df = df_base[df_base["11. Estrato"].isin(estratos)].copy()

# ─────────────────────────────────────────────
# TÍTULO
# ─────────────────────────────────────────────

st.title("Dashboard Ambiental - Medellín")
st.markdown("Análisis basado en la Encuesta de Calidad de Vida 2025")

variables = ["Aire", "Ríos", "Ruido", "Basuras", "Contaminación Visual"]

# ─────────────────────────────────────────────
# MÉTRICAS
# ─────────────────────────────────────────────

df_metricas = df[df["barrio"] == barrio_activo] if barrio_activo else df

st.subheader("Indicadores Generales")
col1, col2, col3 = st.columns(3)
col1.metric("Total hogares", len(df_metricas))
col2.metric("Estratos analizados", df_metricas["11. Estrato"].nunique())
col3.metric("Variables ambientales", len(variables))

# ─────────────────────────────────────────────
# 🗺️ MAPA INTERACTIVO — actúa como filtro
# ─────────────────────────────────────────────

st.markdown("---")
st.subheader("🗺️ Mapa de Barrios — haz click para filtrar las gráficas")

if barrio_activo:
    n_hogares = len(df[df["barrio"] == barrio_activo])
    st.info(f"📍 Mostrando datos para **{barrio_activo}** ({n_hogares} hogares en estratos seleccionados)")

# ── Datos para colorear el mapa ────────────────────────────────────────────
df_group = (
    df.groupby("barrio")
    .agg({"11. Estrato": "mean"})
    .reset_index()
)
df_group["match"] = df_group["barrio"].apply(
    lambda x: encontrar_mejor_match(x, barrios_geo)
)
datos_dict = {}
for _, row in df_group.iterrows():
    if row["match"]:
        datos_dict[row["match"]] = round(row["11. Estrato"])

# ── Barrio activo → forma normalizada (para resaltar en el mapa) ───────────
barrio_activo_limpio = (
    encontrar_mejor_match(barrio_activo, barrios_geo)
    if barrio_activo else None
)

# ── Paleta de colores ──────────────────────────────────────────────────────
COLORES_ESTRATO = {
    1: "#e74c3c",
    2: "#e67e22",
    3: "#f1c40f",
    4: "#2ecc71",
    5: "#3498db",
    6: "#9b59b6",
    0: "#bdc3c7",
}


def estilo(feature):
    blim    = feature["properties"]["barrio_limpio"]
    estrato = datos_dict.get(blim, 0)
    color   = COLORES_ESTRATO.get(estrato, "#bdc3c7")
    if barrio_activo_limpio and blim == barrio_activo_limpio:
        return {"fillColor": color, "color": "#ffffff", "weight": 3.5, "fillOpacity": 0.95}
    return {"fillColor": color, "color": "#555555", "weight": 0.7, "fillOpacity": 0.65}


# ── Usar el centro/zoom guardado en session_state ──────────────────────────
centro   = st.session_state["map_center"]
zoom_ini = st.session_state["map_zoom"]

# ── Construir mapa ─────────────────────────────────────────────────────────
mapa = folium.Map(location=centro, zoom_start=zoom_ini, tiles="CartoDB positron")

folium.GeoJson(
    geojson,
    name="barrios",
    style_function=estilo,
    tooltip=folium.GeoJsonTooltip(
        fields=["NOMBRE"],
        aliases=["Barrio:"],
        style="font-size:13px; font-weight:bold;",
    ),
).add_to(mapa)

# ── Leyenda ────────────────────────────────────────────────────────────────
leyenda_html = """
<div style="
    position: fixed;
    bottom: 30px; right: 30px;
    background: white;
    padding: 12px 16px;
    border-radius: 10px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
    font-family: sans-serif;
    font-size: 13px;
    z-index: 9999;
">
<b>Estrato promedio</b><br>
<span style='color:#e74c3c'>■</span> Estrato 1<br>
<span style='color:#e67e22'>■</span> Estrato 2<br>
<span style='color:#f1c40f'>■</span> Estrato 3<br>
<span style='color:#2ecc71'>■</span> Estrato 4<br>
<span style='color:#3498db'>■</span> Estrato 5<br>
<span style='color:#9b59b6'>■</span> Estrato 6<br>
<span style='color:#bdc3c7'>■</span> Sin dato
</div>
"""
mapa.get_root().html.add_child(folium.Element(leyenda_html))

# ── Renderizar mapa — captura click Y posición actual de la vista ──────────
mapa_data = st_folium(
    mapa,
    width=None,
    height=520,
    returned_objects=["last_object_clicked_tooltip"],
    key="mapa_medellin",
)

# ── Procesar click: extraer nombre del barrio ──────────────────────────────
if mapa_data and mapa_data.get("last_object_clicked_tooltip"):
    tooltip_data = mapa_data["last_object_clicked_tooltip"]

    if isinstance(tooltip_data, dict):
        nombre_click = (
            tooltip_data.get("NOMBRE")
            or tooltip_data.get("Barrio:")
            or tooltip_data.get("barrio_limpio")
        )
    elif isinstance(tooltip_data, str):
        nombre_click = tooltip_data.strip()
        # Quitar prefijo del alias: "Barrio: Laureles" → "Laureles"
        for prefijo in ["Barrio:", "barrio:", "BARRIO:"]:
            if nombre_click.startswith(prefijo):
                nombre_click = nombre_click[len(prefijo):].strip()
                break
    else:
        nombre_click = None

    # Fuzzy match contra nombres reales del df para que el filtro funcione
    if nombre_click:
        match_norm  = encontrar_mejor_match(nombre_click, list(barrios_df_norm.keys()))
        nombre_final = barrios_df_norm.get(match_norm) if match_norm else None

        if nombre_final and nombre_final != barrio_activo:
            # Calcular nuevo centro/zoom para el barrio seleccionado
            for feat in geojson["features"]:
                if feat["properties"]["barrio_limpio"] == limpiar(nombre_click):
                    c = centroide_feature(feat)
                    if c:
                        st.session_state["map_center"] = c
                        st.session_state["map_zoom"]   = 15
                    break
            st.session_state["barrio_click"] = nombre_final
            st.rerun()

# ─────────────────────────────────────────────
# FILTRO DE DATOS PARA GRÁFICAS
# ─────────────────────────────────────────────

df_barrio = df[df["barrio"] == barrio_activo].copy() if barrio_activo else df.copy()

# ─────────────────────────────────────────────
# FILTROS DE ANÁLISIS (variable + estrato)
# ─────────────────────────────────────────────

st.markdown("---")
titulo_graficas = (
    f"## 📊 Análisis de **{barrio_activo}**"
    if barrio_activo
    else "## 📊 Análisis — Medellín completo"
)
st.markdown(titulo_graficas)

col_f1, col_f2 = st.columns(2)

with col_f1:
    variable_select = st.selectbox(
        "Selecciona variable ambiental",
        ["Todas"] + variables,
        key="var_bar",
    )

with col_f2:
    opciones_estrato = sorted(df_barrio["11. Estrato"].unique())
    if not opciones_estrato:
        opciones_estrato = sorted(df["11. Estrato"].unique())
    estrato_select = st.selectbox(
        "Selecciona estrato",
        ["Todos"] + opciones_estrato,
        key="estrato_bar",
    )

# Filtrar por estrato
if estrato_select == "Todos":
    df_filtrado = df_barrio.copy()
else:
    df_filtrado = df_barrio[df_barrio["11. Estrato"] == estrato_select].copy()

# Variables a mostrar según el filtro
variables_a_mostrar = variables if variable_select == "Todas" else [variable_select]

# ─────────────────────────────────────────────
# GRÁFICA 1 — PROBLEMAS AMBIENTALES
# ─────────────────────────────────────────────

st.subheader("Problemas ambientales percibidos")

resultados = []
for col_var in variables_a_mostrar:
    df_temp = df_filtrado.copy()
    df_temp["categoria"] = df_temp[col_var].apply(map_categoria)
    negativos = df_temp[df_temp["categoria"].isin(["Mala", "Muy mala"])].shape[0]
    total = len(df_temp)
    if total > 0:
        resultados.append({
            "Variable": col_var,
            "Porcentaje Negativo": round((negativos / total) * 100, 0),
        })

if resultados:
    df_plot = pd.DataFrame(resultados).sort_values("Porcentaje Negativo", ascending=False)
    
    titulo_g1 = f"Percepción negativa — {barrio_activo if barrio_activo else 'Medellín'} "
    titulo_g1 += f"(Estrato: {estrato_select})"

    fig1 = px.bar(
        df_plot,
        x="Variable",
        y="Porcentaje Negativo",
        text="Porcentaje Negativo",
        color="Porcentaje Negativo",
        color_continuous_scale="Reds",
        title=titulo_g1,
    )
    fig1.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(range=[0, 105], title="Porcentaje (%)")
    )
    if len(df_plot) == 1:
        fig1.update_traces(width=0.3)
        
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("No hay datos para mostrar con los filtros actuales.")

# ─────────────────────────────────────────────
# GRÁFICA 2 — PERCEPCIÓN POR ESTRATO
# ─────────────────────────────────────────────

st.subheader("Percepción ambiental por estrato")

df_long = df_filtrado.melt(
    id_vars=["11. Estrato"],
    value_vars=variables_a_mostrar,
    var_name="Variable",
    value_name="Valor",
)
df_long["categoria"] = df_long["Valor"].apply(map_categoria)
df_plot2 = (
    df_long.groupby(["11. Estrato", "categoria"])
    .size()
    .reset_index(name="count")
)

if not df_plot2.empty:
    df_plot2["total"] = df_plot2.groupby("11. Estrato")["count"].transform("sum")
    df_plot2["Pct"]   = ((df_plot2["count"] / df_plot2["total"]) * 100).round(0)
    
    titulo_g2 = f"Distribución porcentual por estrato — {barrio_activo if barrio_activo else 'Medellín'}"
    if variable_select != "Todas":
        titulo_g2 += f" ({variable_select})"

    fig2 = px.bar(
        df_plot2,
        x="11. Estrato",
        y="Pct",
        color="categoria",
        barmode="stack",
        text="Pct",
        title=titulo_g2,
        category_orders={"categoria": ["Muy buena", "Buena", "Aceptable", "Mala", "Muy mala", "No sabe"]}
    )
    fig2.update_layout(
        yaxis=dict(range=[0, 105], title="Porcentaje (%)")
    )
    # Limitar el ancho de la barra si solo hay un estrato seleccionado
    if df_plot2["11. Estrato"].nunique() == 1:
        fig2.update_traces(width=0.3)
        
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No hay datos de estrato para mostrar.")

# ─────────────────────────────────────────────
# GRÁFICA 3 — DISTRIBUCIÓN GENERAL
# ─────────────────────────────────────────────

st.subheader("Distribución general de percepción")

if not df_filtrado.empty and not df_long.empty:
    titulo_g3 = f"Distribución de percepción — {barrio_activo if barrio_activo else 'Medellín'} "
    titulo_g3 += f"(Estrato: {estrato_select} | Variable: {variable_select})"
    
    fig3 = px.histogram(
        df_long,
        x="categoria",
        color_discrete_sequence=["#3498db"],
        title=titulo_g3,
        category_orders={"categoria": ["Muy buena", "Buena", "Aceptable", "Mala", "Muy mala", "No sabe"]}
    )
    fig3.update_layout(xaxis_title="Categoría de Percepción", yaxis_title="Cantidad de Respuestas")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No hay datos para mostrar con los filtros actuales.")