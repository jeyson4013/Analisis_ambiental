import html
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import unicodedata
import re
import folium
from branca.element import MacroElement
from folium.template import Template
import json
from streamlit_folium import st_folium
from difflib import get_close_matches


class FitBoundsYLimiteZoomSalida(MacroElement):
    """fitBounds al bbox y luego minZoom = zoom actual (sin zoom out más allá de lo relevante)."""

    _template = Template(
        """
        {% macro script(this, kwargs) %}
        (function () {
            var m = {{ this._parent.get_name() }};
            var b = {{ this.bounds|tojson }};
            m.fitBounds(b, {
                padding: [{{ this.pad_px }}, {{ this.pad_px }}],
                maxZoom: {{ this.max_zoom }},
                animate: false
            });
            m.setMinZoom(m.getZoom());
        })();
        {% endmacro %}
        """
    )

    def __init__(self, bounds, pad_px=12, max_zoom=18):
        super().__init__()
        self._name = "FitBoundsYLimiteZoomSalida"
        self.bounds = bounds
        self.pad_px = int(pad_px)
        self.max_zoom = int(max_zoom)

st.set_page_config(page_title="Dashboard Ambiental Medellín", layout="wide")

COLORES_COMUNAS = [
    "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#1abc9c",
    "#3498db", "#9b59b6", "#e91e63", "#00bcd4", "#8bc34a",
    "#ff5722", "#607d8b", "#795548", "#ff9800", "#03a9f4",
    "#673ab7", "#009688", "#cddc39", "#ff4081", "#00e676",
    "#ff6d00", "#6200ea", "#00b0ff", "#76ff03", "#ffab40",
]

COLORES_VARIABLES = {
    "Todas":                {"color": "#7f8c8d", "emoji": "🌐", "bg": "#f2f3f4"},
    "Aire":                 {"color": "#3498db", "emoji": "💨", "bg": "#eaf4fb"},
    "Ríos":                 {"color": "#1abc9c", "emoji": "🌊", "bg": "#e8f8f5"},
    "Ruido":                {"color": "#e67e22", "emoji": "🔊", "bg": "#fef5e7"},
    "Basuras":              {"color": "#8e44ad", "emoji": "🗑️", "bg": "#f5eef8"},
    "Contaminación Visual": {"color": "#c0392b", "emoji": "👁️", "bg": "#fdedec"},
}

if "comuna_click" not in st.session_state:
    st.session_state["comuna_click"] = None
if "barrio_click" not in st.session_state:
    st.session_state["barrio_click"] = None
if "map_center" not in st.session_state:
    st.session_state["map_center"] = [6.2442, -75.5812]
if "map_zoom" not in st.session_state:
    st.session_state["map_zoom"] = 12
if "variable_comuna" not in st.session_state:
    st.session_state["variable_comuna"] = "Todas"
if "variable_global_val" not in st.session_state:
    st.session_state["variable_global_val"] = "Todas"
if "_abrir_modal_barrio" not in st.session_state:
    st.session_state["_abrir_modal_barrio"] = False

def limpiar(texto):
    if not texto: return ""
    texto = str(texto).upper().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^A-Z0-9 ]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()

def encontrar_mejor_match(texto, lista, cutoff=0.7):
    if not texto: return None
    matches = get_close_matches(limpiar(texto), lista, n=1, cutoff=cutoff)
    return matches[0] if matches else None

def map_categoria(x):
    x = str(x).lower()
    if "muy buena" in x: return "Muy buena"
    elif "buena" in x: return "Buena"
    elif "aceptable" in x or "regular" in x: return "Aceptable"
    elif "muy mala" in x: return "Muy mala"
    elif "mala" in x: return "Mala"
    else: return "No sabe"

def centroide_feature(feat):
    try:
        geom = feat["geometry"]
        coords = geom["coordinates"]
        if geom["type"] == "Polygon": pts = coords[0]
        elif geom["type"] == "MultiPolygon": pts = coords[0][0]
        else: return None
        lng = sum(p[0] for p in pts) / len(pts)
        lat = sum(p[1] for p in pts) / len(pts)
        return [lat, lng]
    except Exception: return None

def bounds_from_features(features):
    """[[lat_sur_oeste, lng_sur_oeste], [lat_nor_este, lng_nor_este]] para fit_bounds."""
    min_lat, max_lat = 90.0, -90.0
    min_lng, max_lng = 180.0, -180.0
    hay = False
    for f in features:
        geom = f.get("geometry") or {}
        gtype = geom.get("type")
        coords = geom.get("coordinates")
        if not coords:
            continue
        puntos = []
        if gtype == "Polygon":
            for anillo in coords:
                puntos.extend(anillo)
        elif gtype == "MultiPolygon":
            for poligono in coords:
                for anillo in poligono:
                    puntos.extend(anillo)
        else:
            continue
        for p in puntos:
            if len(p) < 2:
                continue
            lng, lat = float(p[0]), float(p[1])
            min_lat, max_lat = min(min_lat, lat), max(max_lat, lat)
            min_lng, max_lng = min(min_lng, lng), max(max_lng, lng)
            hay = True
    if not hay:
        return None
    return [[min_lat, min_lng], [max_lat, max_lng]]

def render_variable_btns(opciones, val_actual, key_prefix, state_key):
    for i, op in enumerate(opciones):
        info = COLORES_VARIABLES[op]
        is_sel = val_actual == op
        bg = info["bg"] if is_sel else "#fafafa"
        borde = f"{'3px' if is_sel else '1.5px'} solid {info['color'] if is_sel else '#ddd'}"
        peso = "700" if is_sel else "400"
        st.sidebar.markdown(
            f"<style>"
            f"div.element-container:has(span.vbm-{key_prefix}-{i}) + div.element-container .stButton > button {{"
            f"background:{bg} !important; border:{borde} !important;"
            f"font-weight:{peso} !important; color:#2c3e50 !important;}}"
            f"</style><span class='vbm-{key_prefix}-{i}'></span>",
            unsafe_allow_html=True
        )
        if st.sidebar.button(f"{info['emoji']} {op}", key=f"{key_prefix}_{op}", width="stretch"):
            st.session_state[state_key] = op
            st.rerun()

@st.cache_data(show_spinner="Cargando datos...")
def cargar_datos():
    df = pd.read_excel("ECV_2025_Limpio.xlsx")
    df = df[df["4. Ubicación geográfica - Municipio"].str.contains("Medell", na=False)]
    
    # Ajuste de nombres conocidos para compatibilidad con el mapa
    df["6. Comuna o Corregimiento"] = df["6. Comuna o Corregimiento"].replace({
        "LAURELES": "LAURELES ESTADIO",
        "Laureles": "LAURELES ESTADIO"
    })
    
    df["barrio"] = df["7. Barrio o Vereda"].fillna("Sin información")
    df["comuna"] = df["6. Comuna o Corregimiento"].fillna("Sin información")
    return df

@st.cache_data(show_spinner="Cargando GeoJSON...")
def cargar_geojson():
    import json
    try:
        with open("medellin_debug.geojson", "r", encoding="utf-8") as f:
            geojson = json.load(f)
    except Exception as e:
        st.error(f"Error cargando GeoJSON local: {e}")
        return {"type": "FeatureCollection", "features": []}
    for f in geojson.get("features", []):
        props = f["properties"]
        props["barrio_limpio"] = limpiar(props.get("NOMBRE", ""))
        c_raw = props.get("Comuna")
        if c_raw:
            # Eliminar prefijo 'COMUNA X ' si existe
            props["comuna_limpia"] = re.sub(r'COMUNA \d+ ', '', limpiar(c_raw))
        else:
            props["comuna_limpia"] = "SIN INFORMACION"
    return geojson

df_base = cargar_datos()
geojson = cargar_geojson()

# Crear un mapeo jerárquico: (Comuna Limpia, Barrio Limpio) -> Comuna Original del DF
mapeo_jerarquico = {}
# Crear mapeo jerárquico para nombres de barrios: (Comuna Limpia, Barrio Limpio) -> Barrio Original
mapeo_barrios = {}

for _, row in df_base.iterrows():
    c_lim = limpiar(row["comuna"])
    b_lim = limpiar(row["barrio"])
    k = (c_lim, b_lim)
    if k not in mapeo_jerarquico:
        mapeo_jerarquico[k] = row["comuna"]
    if k not in mapeo_barrios:
        mapeo_barrios[k] = row["barrio"]

comunas_df_lista = df_base["comuna"].dropna().unique().tolist()
comunas_df_norm = {limpiar(c): c for c in comunas_df_lista}
barrios_df_lista = df_base["barrio"].dropna().unique().tolist()
barrios_df_norm = {limpiar(b): b for b in barrios_df_lista}

for f in geojson.get("features", []):
    props = f["properties"]
    b_limpio = props.get("barrio_limpio")
    c_limpia = props.get("comuna_limpia")
    
    # Intentar match jerárquico exacto primero
    llave = (c_limpia, b_limpio)
    if llave in mapeo_jerarquico:
        props["comuna_df"] = mapeo_jerarquico[llave]
    else:
        # Si no hay match exacto, buscar el mejor barrio dentro de ESA comuna
        barrios_en_esta_comuna = [b for (c, b) in mapeo_jerarquico.keys() if c == c_limpia]
        mejor_b = encontrar_mejor_match(b_limpio, barrios_en_esta_comuna, cutoff=0.7)
        
        if mejor_b:
            props["comuna_df"] = mapeo_jerarquico[(c_limpia, mejor_b)]
        else:
            # Último recurso: match de comuna
            mejor_c = encontrar_mejor_match(c_limpia, list(comunas_df_norm.keys()), cutoff=0.5)
            props["comuna_df"] = comunas_df_norm.get(mejor_c) if mejor_c else "Sin información"

variables = ["Aire", "Ríos", "Ruido", "Basuras", "Contaminación Visual"]
opciones_vars = ["Todas"] + variables

comunas_unicas = sorted([c for c in comunas_df_lista if c != "Sin información"])
color_por_comuna = {c: COLORES_COMUNAS[i % len(COLORES_COMUNAS)] for i, c in enumerate(comunas_unicas)}

COLOR_MAP_CATEG = {
    "Muy buena": "#2ecc71",
    "Buena": "#27ae60",
    "Aceptable": "#f1c40f",
    "Mala": "#e67e22",
    "Muy mala": "#e74c3c",
    "No sabe": "#bdc3c7",
}
CAT_ORDER = ["Muy buena", "Buena", "Aceptable", "Mala", "Muy mala", "No sabe"]


def figuras_estadisticas_barrio(df_local, variable_activa, altura=340):
    """
    Construye hasta tres figuras Plotly (resumen, estrato, distribución).
    altura: usa valores moderados para caber en modal sin scroll.
    """
    if df_local.empty:
        return None, None, None
    vars_mostrar = variables if variable_activa == "Todas" else [variable_activa]
    resultados = []
    for col_var in vars_mostrar:
        df_temp = df_local.copy()
        df_temp["categoria"] = df_temp[col_var].apply(map_categoria)
        negativos = df_temp[df_temp["categoria"].isin(["Mala", "Muy mala"])].shape[0]
        total = len(df_temp)
        if total > 0:
            resultados.append(
                {"Variable": col_var, "Porcentaje Negativo": round((negativos / total) * 100, 1)}
            )
    fig1 = None
    if resultados:
        df_plot1 = pd.DataFrame(resultados).sort_values("Porcentaje Negativo", ascending=True)
        fig1 = px.bar(
            df_plot1,
            x="Porcentaje Negativo",
            y="Variable",
            orientation="h",
            title="Percepción negativa por variable",
            color="Porcentaje Negativo",
            color_continuous_scale="Reds",
            text="Porcentaje Negativo",
        )
        fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig1.update_layout(
            margin=dict(l=8, r=48, t=48, b=8),
            height=altura,
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#f8fafc",
            xaxis=dict(title="% negativo", ticksuffix="%", showgrid=True, gridcolor="#e2e8f0"),
            yaxis=dict(title=""),
            font=dict(size=12, color="#1e293b"),
        )
    df_long = df_local.melt(
        id_vars=["11. Estrato"],
        value_vars=vars_mostrar,
        var_name="Variable",
        value_name="Valor",
    )
    df_long["categoria"] = df_long["Valor"].apply(map_categoria)
    df_long["Estrato"] = df_long["11. Estrato"].apply(
        lambda x: f"Estrato {int(x)}" if pd.notna(x) and str(x).isdigit() else str(x)
    )
    df_plot2 = df_long.groupby(["Estrato", "categoria"]).size().reset_index(name="count")
    fig2 = None
    if not df_plot2.empty:
        df_plot2["total"] = df_plot2.groupby("Estrato")["count"].transform("sum")
        df_plot2["Pct"] = ((df_plot2["count"] / df_plot2["total"]) * 100).round(1)
        estratos_order = sorted(
            df_plot2["Estrato"].unique(),
            key=lambda x: int(x.split()[-1]) if x.split()[-1].isdigit() else 99,
        )
        fig2 = px.bar(
            df_plot2,
            x="Estrato",
            y="Pct",
            color="categoria",
            barmode="stack",
            title="Percepción por estrato",
            color_discrete_map=COLOR_MAP_CATEG,
            category_orders={"categoria": CAT_ORDER, "Estrato": estratos_order},
            text="Pct",
        )
        fig2.update_traces(
            texttemplate="%{text:.0f}%",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=10, color="white"),
        )
        fig2.update_layout(
            margin=dict(l=8, r=8, t=48, b=72),
            height=altura + 40,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#f8fafc",
            xaxis=dict(title="Estrato"),
            yaxis=dict(title="%", ticksuffix="%", range=[0, 105]),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.42,
                xanchor="center",
                x=0.5,
                title="",
                font=dict(size=10),
            ),
            font=dict(size=12, color="#1e293b"),
            bargap=0.22,
        )
    df_pie = df_long["categoria"].value_counts().reset_index()
    df_pie.columns = ["categoria", "count"]
    fig3 = None
    if not df_pie.empty:
        fig3 = px.pie(
            df_pie,
            values="count",
            names="categoria",
            title="Distribución — " + str(variable_activa),
            color="categoria",
            color_discrete_map=COLOR_MAP_CATEG,
        )
        fig3.update_traces(
            textposition="inside",
            textinfo="percent+label",
            textfont=dict(size=11),
        )
        fig3.update_layout(
            margin=dict(l=8, r=8, t=48, b=8),
            height=altura,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color="#1e293b"),
        )
    return fig1, fig2, fig3


def filtrar_datos_barrio_seleccionado(df_source: pd.DataFrame) -> pd.DataFrame:
    bc = st.session_state.get("barrio_click")
    cc = st.session_state.get("comuna_click")
    if not bc or not cc:
        return pd.DataFrame()
    df_popup = df_source[
        (df_source["barrio"] == bc) & (df_source["comuna"].apply(limpiar) == limpiar(cc))
    ]
    if df_popup.empty:
        df_popup = df_source[df_source["barrio"] == bc]
    return df_popup


def resolver_feature_barrio(features_mostrar):
    bc = st.session_state.get("barrio_click")
    if not bc or not features_mostrar:
        return None
    for f in features_mostrar:
        props = f.get("properties") or {}
        key = (props.get("comuna_limpia"), props.get("barrio_limpio"))
        if mapeo_barrios.get(key) == bc:
            return f
    b_limpio = limpiar(bc)
    for f in features_mostrar:
        if f.get("properties", {}).get("barrio_limpio") == b_limpio:
            return f
    return None


@st.dialog("📊 Estadísticas del barrio", width="large")
def modal_estadisticas_barrio(df_local, barrio_nombre, comuna_nombre, variable_activa):
    safe_b = html.escape(str(barrio_nombre))
    safe_c = html.escape(str(comuna_nombre))
    safe_v = html.escape(str(variable_activa))
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0c4a6e 100%);
            color: #f8fafc;
            padding: 1.1rem 1.25rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.25);
        ">
            <div style="font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; opacity: 0.85;">Encuesta — percepción ambiental</div>
            <div style="font-size: 1.35rem; font-weight: 700; margin-top: 0.35rem;">🏡 {safe_b}</div>
            <div style="font-size: 0.95rem; opacity: 0.9; margin-top: 0.25rem;">📍 {safe_c}</div>
            <div style="margin-top: 0.6rem; font-size: 0.9rem;"><span style="opacity:0.85">Variable:</span> <b>{safe_v}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if df_local.empty:
        st.info("No hay registros en la encuesta para esta zona con los filtros actuales.")
        if st.button("Cerrar", width="stretch"):
            st.rerun()
        return
    fig1, fig2, fig3 = figuras_estadisticas_barrio(df_local, variable_activa, altura=360)
    tab1, tab2, tab3 = st.tabs(["📈 Resumen por variable", "🏘️ Por estrato", "🥧 Distribución"])
    cfg = {"displayModeBar": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}
    with tab1:
        if fig1:
            st.plotly_chart(fig1, width="stretch", config=cfg)
        else:
            st.caption("Sin datos para este resumen.")
    with tab2:
        if fig2:
            st.plotly_chart(fig2, width="stretch", config=cfg)
        else:
            st.caption("Sin datos por estrato.")
    with tab3:
        if fig3:
            st.plotly_chart(fig3, width="stretch", config=cfg)
        else:
            st.caption("Sin datos para la distribución.")
    st.divider()
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("Cerrar", width="stretch", type="primary"):
            st.rerun()
    with c2:
        st.caption(f"**{len(df_local)}** respuestas en esta selección")


def _sidebar_seccion(titulo: str) -> None:
    st.sidebar.markdown(
        "<p style='margin:14px 0 8px 0;padding:0;font-size:11px;font-weight:600;"
        "color:#64748b;text-transform:uppercase;letter-spacing:0.08em;border-bottom:1px solid #e2e8f0;padding-bottom:6px;'>"
        + html.escape(titulo)
        + "</p>",
        unsafe_allow_html=True,
    )


# Área principal: mapa acotado al alto de la ventana (menos scroll vertical)
st.markdown(
    """
<style>
  .main .block-container {
    padding-top: 0.35rem !important;
    padding-bottom: 0 !important;
  }
  div[data-testid="stIFrame"] iframe {
    max-height: calc(100dvh - 3.5rem) !important;
    height: calc(100dvh - 3.5rem) !important;
    min-height: 280px;
  }
</style>
""",
    unsafe_allow_html=True,
)
MAP_ALTO_PX = 700

# ── SIDEBAR ──
st.sidebar.markdown(
    "<div style='background:linear-gradient(135deg,#1a1a2e,#16213e);padding:16px 12px 10px 12px;border-radius:10px;margin-bottom:12px;'>"
    "<span style='color:white;font-size:17px;font-weight:700;letter-spacing:1px;'>🔧 Filtros</span></div>",
    unsafe_allow_html=True
)
st.sidebar.markdown("""
<style>
[data-testid="stSidebar"] .stButton > button {
    border-radius: 8px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 13px !important;
    padding: 7px 12px !important;
    height: auto !important;
    box-shadow: none !important;
    transition: border-color 0.15s !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] [data-testid="column"] .stButton > button {
    font-size: 12px !important;
    padding: 6px 8px !important;
}
</style>
""", unsafe_allow_html=True)

if st.session_state["comuna_click"] is None:
    _sidebar_seccion("Vista general")
    st.sidebar.caption("Color del mapa según la variable en todas las comunas.")
    render_variable_btns(opciones_vars, st.session_state["variable_global_val"], "gvar", "variable_global_val")
    variable_select = st.session_state["variable_global_val"]
    st.session_state["variable_comuna"] = "Todas"
else:
    variable_select = "Todas"

if st.session_state["comuna_click"]:
    _sidebar_seccion("Navegación")
    if st.sidebar.button("⬅️ Volver a todas las comunas", key="btn_volver", width="stretch"):
        st.session_state["comuna_click"] = None
        st.session_state["barrio_click"] = None
        st.session_state["map_center"] = [6.2442, -75.5812]
        st.session_state["map_zoom"] = 12
        st.session_state["variable_comuna"] = "Todas"
        st.rerun()
    _sidebar_seccion("Variable en el mapa")
    render_variable_btns(opciones_vars, st.session_state["variable_comuna"], "cvar", "variable_comuna")
    variable_select = st.session_state["variable_comuna"]
    _sidebar_seccion("Comuna activa")
    color_c = color_por_comuna.get(st.session_state["comuna_click"], "#888")
    cn = html.escape(str(st.session_state["comuna_click"]))
    st.sidebar.markdown(
        "<div style='background:"
        + color_c
        + "22;border-left:5px solid "
        + color_c
        + ";padding:10px 12px;border-radius:8px;margin-bottom:2px;'>"
        "<span style='font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:0.06em;'>"
        "Ubicación</span><br>"
        "<span style='font-size:15px;font-weight:700;color:#0f172a;'>📍 "
        + cn
        + "</span></div>",
        unsafe_allow_html=True,
    )
    if st.session_state["barrio_click"]:
        _sidebar_seccion("Barrio activo")
        bn = html.escape(str(st.session_state["barrio_click"]))
        st.sidebar.markdown(
            "<div style='background:#f1f5f9;border-left:5px solid #334155;padding:10px 12px;border-radius:8px;'>"
            "<span style='font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;'>"
            "Selección</span><br>"
            "<span style='font-size:14px;font-weight:700;color:#0f172a;'>🏡 "
            + bn
            + "</span></div>",
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.sidebar.button("❌ Quitar", key="sb_quitar_barrio", width="stretch"):
            st.session_state["barrio_click"] = None
            st.rerun()
        if st.sidebar.button("📊 Estadísticas", key="btn_abrir_modal_stats", width="stretch"):
            st.session_state["_abrir_modal_barrio"] = True
            st.rerun()

if st.session_state["comuna_click"] is None:
    _sidebar_seccion("Referencia de comunas")
    cols = st.sidebar.columns(2)
    for i, (comuna, color) in enumerate(color_por_comuna.items()):
        comuna_esc = html.escape(str(comuna))
        cols[i % 2].markdown(
            "<div style='display:flex;align-items:center;gap:5px;margin-bottom:4px;'>"
            "<span style='display:inline-block;width:10px;height:10px;border-radius:50%;background:"
            + color
            + ";'></span>"
            "<span style='font-size:10px;color:#444;'>"
            + comuna_esc
            + "</span></div>",
            unsafe_allow_html=True,
        )

# ── MAPA ──
modo = "comunas" if st.session_state["comuna_click"] is None else "barrios"

def obtener_color_porcentaje(pct):
    if pct < 10: return "#2ecc71"
    elif pct < 25: return "#f1c40f"
    elif pct < 50: return "#e67e22"
    else: return "#e74c3c"

COLORES_ESTRATO = {1:"#e74c3c",2:"#e67e22",3:"#f1c40f",4:"#2ecc71",5:"#3498db",6:"#9b59b6"}

datos_dict = {}
if modo == "barrios":
    df_comuna = df_base[df_base["comuna"] == st.session_state["comuna_click"]]
    if variable_select == "Todas":
        df_temp = df_comuna.copy()
        for var in variables:
            df_temp["neg_" + var] = df_temp[var].apply(map_categoria).isin(["Mala", "Muy mala"]).astype(int)
        df_temp["prom_neg"] = df_temp[["neg_" + var for var in variables]].mean(axis=1)
        df_group = df_temp.groupby("barrio")["prom_neg"].mean().reset_index()
        for _, row in df_group.iterrows():
            datos_dict[limpiar(row["barrio"])] = {"val": round(row["prom_neg"] * 100, 1), "tipo": "porcentaje"}
    else:
        df_temp = df_comuna.copy()
        df_temp["categoria"] = df_temp[variable_select].apply(map_categoria)
        df_temp["negativo"] = df_temp["categoria"].isin(["Mala", "Muy mala"]).astype(int)
        df_group = df_temp.groupby("barrio")["negativo"].agg(["mean"]).reset_index()
        for _, row in df_group.iterrows():
            datos_dict[limpiar(row["barrio"])] = {"val": round(row["mean"] * 100, 1), "tipo": "porcentaje"}

def estilo(feature):
    props = feature["properties"]
    if modo == "comunas":
        color = color_por_comuna.get(props.get("comuna_df"), "#bdc3c7")
        return {"fillColor": color, "color": "#ffffff", "weight": 1.5, "fillOpacity": 0.75}
    else:
        llave = props.get("barrio_limpio")
        info = datos_dict.get(llave, {"val": 0, "tipo": "desconocido"})
        if info["tipo"] == "estrato":
            color = COLORES_ESTRATO.get(round(info["val"]), "#bdc3c7")
        elif info["tipo"] == "porcentaje":
            color = obtener_color_porcentaje(info["val"])
        else:
            color = "#bdc3c7"
        if st.session_state["barrio_click"] and llave == limpiar(st.session_state["barrio_click"]):
            return {"fillColor": color, "color": "#000000", "weight": 3, "fillOpacity": 0.95}
        return {"fillColor": color, "color": "#ffffff", "weight": 1, "fillOpacity": 0.75}

features_mostrar = []
comuna_click_limpia = limpiar(st.session_state["comuna_click"]) if st.session_state["comuna_click"] else None
for f in geojson.get("features", []):
    if modo == "comunas":
        features_mostrar.append(f)
    else:
        # Comparar con limpiar() para evitar diferencias de mayúsculas
        comuna_df_limpia = limpiar(f["properties"].get("comuna_df", ""))
        c_limpia_geo = limpiar(f["properties"].get("comuna_limpia", ""))
        if comuna_df_limpia == comuna_click_limpia or c_limpia_geo == comuna_click_limpia:
            features_mostrar.append(f)

geo_filtrado = {"type": "FeatureCollection", "features": features_mostrar}

bbox_capa = bounds_from_features(features_mostrar) if features_mostrar else None

if bbox_capa:
    mn_lat, mn_lng = bbox_capa[0]
    mx_lat, mx_lng = bbox_capa[1]
    lat_pad = max((mx_lat - mn_lat) * 0.02, 0.002)
    lng_pad = max((mx_lng - mn_lng) * 0.02, 0.002)
    centro_lat = (mn_lat + mx_lat) / 2
    centro_lng = (mn_lng + mx_lng) / 2
    mapa = folium.Map(
        location=[centro_lat, centro_lng],
        zoom_start=st.session_state["map_zoom"],
        tiles="CartoDB positron",
        max_bounds=True,
        min_lat=mn_lat - lat_pad,
        max_lat=mx_lat + lat_pad,
        min_lon=mn_lng - lng_pad,
        max_lon=mx_lng + lng_pad,
        max_bounds_viscosity=1.0,
    )
else:
    mapa = folium.Map(
        location=st.session_state["map_center"],
        zoom_start=st.session_state["map_zoom"],
        tiles="CartoDB positron",
    )

if features_mostrar:
    fields = ["comuna_df", "NOMBRE"] if modo == "comunas" else ["NOMBRE"]
    aliases = ["Comuna:", "Barrio:"] if modo == "comunas" else ["Barrio:"]
    folium.GeoJson(geo_filtrado, name="capa_base", style_function=estilo,
                   tooltip=folium.GeoJsonTooltip(fields=fields, aliases=aliases, style="font-size:13px;font-weight:bold;")
    ).add_to(mapa)

if st.session_state["barrio_click"] and modo == "barrios":
    feat_barrio = resolver_feature_barrio(features_mostrar)
    if feat_barrio:
        centroid = centroide_feature(feat_barrio)
        if centroid:
            folium.Marker(
                location=centroid,
                icon=folium.Icon(color="red", icon="info-sign"),
                tooltip="Barrio seleccionado — estadísticas en el modal",
                popup=folium.Popup(
                    "<div style='font-family:sans-serif;padding:8px;text-align:center;'>"
                    "<b>Barrio seleccionado</b><br><small>Usa el modal de estadísticas "
                    "(se abre al elegir el barrio o desde el botón en la barra lateral).</small></div>",
                    max_width=280,
                ),
            ).add_to(mapa)

if bbox_capa:
    FitBoundsYLimiteZoomSalida(bbox_capa, pad_px=12, max_zoom=18).add_to(mapa)

if modo == "barrios":
    if variable_select == "Todas":
        leyenda = ("<div style='position:fixed;bottom:30px;right:30px;background:white;padding:10px;border-radius:5px;z-index:999;box-shadow:2px 2px 5px rgba(0,0,0,0.3);'>"
                   "<b>🌐 % Negativo: Todas las Variables</b><br>"
                   "<span style='color:#2ecc71'>■</span> &lt;10% — Bajo<br>"
                   "<span style='color:#f1c40f'>■</span> 10-25% — Medio<br>"
                   "<span style='color:#e67e22'>■</span> 25-50% — Alto<br>"
                   "<span style='color:#e74c3c'>■</span> &gt;50% — Crítico</div>")
    else:
        emoji_v = COLORES_VARIABLES.get(variable_select, {}).get("emoji", "")
        leyenda = ("<div style='position:fixed;bottom:30px;right:30px;background:white;padding:10px;border-radius:5px;z-index:999;box-shadow:2px 2px 5px rgba(0,0,0,0.3);'>"
                   "<b>" + emoji_v + " % Negativo: " + variable_select + "</b><br>"
                   "<span style='color:#2ecc71'>■</span> &lt;10% — Bajo<br>"
                   "<span style='color:#f1c40f'>■</span> 10-25% — Medio<br>"
                   "<span style='color:#e67e22'>■</span> 25-50% — Alto<br>"
                   "<span style='color:#e74c3c'>■</span> &gt;50% — Crítico</div>")
    mapa.get_root().html.add_child(folium.Element(leyenda))

st.markdown("### Vivir en la ciudad ¿Qué tan sano es nuestro entorno para todos?")

mapa_data = st_folium(
    mapa,
    use_container_width=True,
    height=MAP_ALTO_PX,
    returned_objects=["last_active_drawing"],
    key="mapa_medellin",
)

if mapa_data and mapa_data.get("last_active_drawing"):
    props = mapa_data["last_active_drawing"].get("properties", {})
    if modo == "comunas":
        c_click = props.get("comuna_df")
        if c_click and c_click != st.session_state["comuna_click"]:
            st.session_state["comuna_click"] = c_click
            coords = [centroide_feature(f) for f in geojson.get("features", []) if f["properties"].get("comuna_df") == c_click]
            coords = [c for c in coords if c]
            if coords:
                st.session_state["map_center"] = [sum(c[0] for c in coords)/len(coords), sum(c[1] for c in coords)/len(coords)]
            st.session_state["map_zoom"] = 13
            st.session_state["barrio_click"] = None
            st.rerun()
    elif modo == "barrios":
        b_limpio = props.get("barrio_limpio")
        c_limpia = props.get("comuna_limpia")
        if b_limpio:
            # Buscar el nombre original del barrio dentro de la comuna actual
            key = (c_limpia, b_limpio)
            if key in mapeo_barrios:
                nombre_final = mapeo_barrios[key]
            else:
                # Fuzzy match SOLO dentro de la misma comuna del GeoJSON
                barrios_en_esta_comuna = [b for (c, b) in mapeo_barrios.keys() if c == c_limpia]
                if barrios_en_esta_comuna:
                    match = encontrar_mejor_match(b_limpio, barrios_en_esta_comuna)
                    nombre_final = mapeo_barrios.get((c_limpia, match)) if match else None
                else:
                    # Si no hay barrios de esa comuna en el Excel, usar nombre del GeoJSON
                    nombre_final = props.get("NOMBRE", b_limpio)
                
            if nombre_final and nombre_final != st.session_state["barrio_click"]:
                st.session_state["barrio_click"] = nombre_final
                st.session_state["_abrir_modal_barrio"] = True
                st.rerun()

if st.session_state.pop("_abrir_modal_barrio", False):
    if (
        modo == "barrios"
        and st.session_state.get("barrio_click")
        and st.session_state.get("comuna_click")
    ):
        _df_modal = filtrar_datos_barrio_seleccionado(df_base)
        modal_estadisticas_barrio(
            _df_modal,
            st.session_state["barrio_click"],
            st.session_state["comuna_click"],
            variable_select,
        )
