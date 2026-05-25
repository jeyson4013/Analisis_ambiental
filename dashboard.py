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

if "modal_detalle_runs_this_run" not in st.session_state:
    st.session_state["modal_detalle_runs_this_run"] = False
if "modal_detalle_abierto" not in st.session_state:
    st.session_state["modal_detalle_abierto"] = False

if not st.session_state.get("modal_detalle_runs_this_run", False):
    st.session_state["modal_detalle_abierto"] = False

st.session_state["modal_detalle_runs_this_run"] = False

COLORES_COMUNAS = [
    "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#1abc9c",
    "#3498db", "#9b59b6", "#e91e63", "#00bcd4", "#8bc34a",
    "#ff5722", "#607d8b", "#795548", "#ff9800", "#03a9f4",
    "#673ab7", "#009688", "#cddc39", "#ff4081", "#00e676",
    "#ff6d00", "#6200ea", "#00b0ff", "#76ff03", "#ffab40",
]

COLORES_VARIABLES = {
    "Todas":                {"color": "#00DF81", "emoji": "🌐", "bg": "#01341f"},
    "Aire":                 {"color": "#2CC295", "emoji": "💨", "bg": "#023830"},
    "Ríos":                 {"color": "#2FA98C", "emoji": "🌊", "bg": "#02302a"},
    "Ruido":                {"color": "#AACBC4", "emoji": "🔊", "bg": "#283535"},
    "Basuras":              {"color": "#17876D", "emoji": "🗑️", "bg": "#022c22"},
    "Contaminación Visual": {"color": "#707D7D", "emoji": "👁️", "bg": "#252d2d"},
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
    st.session_state["variable_comuna"] = ["Todas"]
if "variable_global_val" not in st.session_state:
    st.session_state["variable_global_val"] = ["Todas"]
if "_abrir_modal_barrio" not in st.session_state:
    st.session_state["_abrir_modal_barrio"] = False
if "_abrir_modal_qr" not in st.session_state:
    st.session_state["_abrir_modal_qr"] = False

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
    # val_actual is a list; show hint about multi-select
    num_vars = len([v for v in val_actual if v != "Todas"])
    if "Todas" in val_actual:
        hint = "Selecciona hasta 3 variables"
    elif num_vars == 1:
        hint = "1 variable activa — puedes añadir hasta 2 más"
    elif num_vars == 2:
        hint = "2 variables activas — puedes añadir 1 más"
    else:
        hint = "3 variables activas (máximo)"
    st.sidebar.caption(hint)

    for i, op in enumerate(opciones):
        info = COLORES_VARIABLES[op]
        is_sel = op in val_actual
        bg = info["bg"] if is_sel else "#032221"
        borde = f"{'3px' if is_sel else '1.5px'} solid {info['color'] if is_sel else '#03624C'}"
        peso = "700" if is_sel else "400"
        st.sidebar.markdown(
            f"<style>"
            f"div.element-container:has(span.vbm-{key_prefix}-{i}) + div.element-container .stButton > button {{"
            f"background:{bg} !important; border:{borde} !important;"
            f"font-weight:{peso} !important; color:#F1F7F6 !important;}}"
            f"</style><span class='vbm-{key_prefix}-{i}'></span>",
            unsafe_allow_html=True
        )
        if st.sidebar.button(f"{info['emoji']} {op}", key=f"{key_prefix}_{op}", width="stretch"):
            current = list(st.session_state[state_key])
            if op == "Todas":
                st.session_state[state_key] = ["Todas"]
            elif op in current:
                current.remove(op)
                st.session_state[state_key] = current if current else ["Todas"]
            else:
                current = [v for v in current if v != "Todas"]
                current.append(op)
                if len(current) > 3:
                    current.pop(0)
                st.session_state[state_key] = current
            
            if st.session_state.get("modal_detalle_abierto") and op != "Todas":
                st.session_state["_var_detalle"] = op
                st.session_state["_abrir_var_detalle"] = True
                
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


def figuras_estadisticas_barrio(df_local, variable_activa, estratos_sel=None, altura=340):
    if df_local.empty:
        return None, None, None
    vars_mostrar = variables if "Todas" in variable_activa else list(variable_activa)

    # Filtrado por estrato (aplica a las tres figuras)
    df_filt = df_local.copy()
    df_filt["Estrato"] = df_filt["11. Estrato"].apply(
        lambda x: f"Estrato {int(x)}" if pd.notna(x) and str(x).isdigit() else str(x)
    )
    if estratos_sel:
        df_filt = df_filt[df_filt["Estrato"].isin(estratos_sel)]

    # --- Fig1: resumen por variable, filtrado por estrato ---
    resultados = []
    for col_var in vars_mostrar:
        df_temp = df_filt.copy()
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
            title="Percepción negativa por variable — clic en barra para detalle",
            color="Porcentaje Negativo",
            color_continuous_scale=[
                [0.0, "#FFC107"],  # Amarillo-ámbar vibrante
                [0.5, "#FF6F00"],  # Naranja vibrante
                [1.0, "#D50000"],  # Rojo vibrante
            ],
            range_color=[0, 100],
            text="Porcentaje Negativo",
        )
        fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig1.update_layout(
            margin=dict(l=8, r=48, t=52, b=8),
            height=altura,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="% negativo", ticksuffix="%", showgrid=False, range=[0, 100]),
            yaxis=dict(title="", showgrid=False),
            font=dict(size=12, color="#021B1A"),
            showlegend=False,
            coloraxis_showscale=False,
        )

    df_long = df_filt.melt(
        id_vars=["Estrato"],
        value_vars=vars_mostrar,
        var_name="Variable",
        value_name="Valor",
    )
    df_long["categoria"] = df_long["Valor"].apply(map_categoria)

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
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Estrato", showgrid=False),
            yaxis=dict(title="%", ticksuffix="%", range=[0, 105], showgrid=False),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.42,
                xanchor="center", x=0.5, title="", font=dict(size=10),
            ),
            font=dict(size=12, color="#021B1A"),
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
            title="Distribución — " + (
                "Todas" if ("Todas" in variable_activa or set(variable_activa) == set(variables))
                else " + ".join(variable_activa)
            ),
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
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color="#021B1A"),
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


import base64, pathlib, os

def _qr_base64() -> str:
    """Devuelve el QR como cadena base64 PNG (imagen embebida en el código)."""
    # Intentar leer desde archivo si existe
    ruta = pathlib.Path(__file__).parent / "assets" / "qr_dashboard.png"
    if ruta.exists():
        return base64.b64encode(ruta.read_bytes()).decode()
    # Fallback: QR codificado en base64 (imagen compartida por el usuario)
    return QR_B64_FALLBACK

# ── QR en base64 (imagen compartida por el usuario) ──────────────────────────
# Esta cadena es la imagen QR codificada en base64 para que funcione
# sin depender de archivos externos.
QR_B64_FALLBACK = ""  # Se reemplaza por la imagen real al guardarse en assets/


@st.dialog("📲 Código QR del Dashboard", width="small")
def modal_qr():
    st.markdown(
        """
        <div style="text-align:center;padding:8px 0 4px 0;">
            <span style="font-size:0.78rem;letter-spacing:0.12em;text-transform:uppercase;
                color:#2CC295;font-weight:700;">Escanea para compartir</span>
            <p style="font-size:0.82rem;color:#AACBC4;margin:6px 0 14px 0;">
                Abre el dashboard en tu dispositivo móvil
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    ruta_qr = pathlib.Path(__file__).parent / "assets" / "qr_dashboard.png"
    if ruta_qr.exists():
        st.image(str(ruta_qr), use_container_width=True)
    else:
        st.warning(
            "⚠️ No se encontró la imagen del QR.\n\n"
            "Guarda tu imagen QR en: `assets/qr_dashboard.png`"
        )
    st.markdown(
        "<div style='height:8px'></div>",
        unsafe_allow_html=True,
    )
    if st.button("Cerrar", width="stretch", type="primary", key="btn_cerrar_qr"):
        st.rerun()


@st.dialog("📊 Estadísticas del barrio", width="large")
def modal_estadisticas_barrio(df_local, barrio_nombre, comuna_nombre):
    safe_b = html.escape(str(barrio_nombre))
    safe_c = html.escape(str(comuna_nombre))
    _sel_prev = st.session_state.get("_modal_estratos_sel", [])
    _lbl_estrato = "Todos los estratos" if not _sel_prev else " · ".join(_sel_prev)
    _n_resp = len(df_local)
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #021B1A 0%, #03624C 55%, #17876D 100%);
            color: #F1F7F6;
            padding: 1.1rem 1.25rem;
            border-radius: 12px;
            margin-bottom: 0.75rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        ">
            <div style="font-size:0.75rem;letter-spacing:0.14em;text-transform:uppercase;color:#2CC295;">Encuesta — percepción ambiental</div>
            <div style="font-size:1.35rem;font-weight:700;margin-top:0.35rem;color:#F1F7F6;">🏡 {safe_b}</div>
            <div style="font-size:0.95rem;margin-top:0.25rem;color:#AACBC4;">📍 {safe_c}</div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                margin-top:0.65rem;border-top:1px solid rgba(255,255,255,0.15);padding-top:0.5rem;">
                <span style="font-size:0.82rem;color:#AACBC4;">📋 <strong>{_n_resp}</strong> respuestas</span>
                <span style="font-size:0.78rem;color:#707D7D;">{_lbl_estrato}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if df_local.empty:
        st.info("No hay registros en la encuesta para esta zona con los filtros actuales.")
        if st.button("Cerrar", width="stretch"):
            st.rerun()
        return

    # ── Filtro de estrato (afecta "Por estrato" y "Distribución") ──
    st.markdown(
        "<p style='font-size:11px;font-weight:700;color:#2CC295;text-transform:uppercase;"
        "letter-spacing:0.10em;margin:0 0 5px 0;border-bottom:1px solid #03624C;padding-bottom:5px;'>"
        "Filtrar por estrato</p>",
        unsafe_allow_html=True,
    )
    estratos_raw = sorted(
        [int(e) for e in df_local["11. Estrato"].dropna().unique() if str(e).isdigit()]
    )
    estratos_disponibles = [f"Estrato {e}" for e in estratos_raw]
    sel_estratos = st.multiselect(
        "_modal_estratos_label",
        options=estratos_disponibles,
        key="_modal_estratos_sel",
        placeholder="Sin selección = todos los estratos",
        label_visibility="collapsed",
    )
    estratos_sel = sel_estratos if sel_estratos else None

    cfg = {"displayModeBar": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}
    fig1, fig2, fig3 = figuras_estadisticas_barrio(df_local, list(variables), estratos_sel=estratos_sel, altura=340)
    tab1, tab2, tab3 = st.tabs(["📈 Resumen por variable", "🏘️ Por estrato", "🥧 Distribución"])
    with tab1:
        if fig1:
            sel = st.plotly_chart(fig1, width="stretch", config=cfg, on_select="rerun", key="_modal_res_chart")
            if sel and sel.selection and sel.selection.points:
                pt = sel.selection.points[0]
                var_clicked = pt.get("y") or pt.get("label") or ""
                if var_clicked in variables:
                    st.session_state["_var_detalle"] = var_clicked
                    st.session_state["_barrio_detalle"] = barrio_nombre
                    st.session_state["_comuna_detalle"] = comuna_nombre
                    st.session_state["_abrir_var_detalle"] = True
                    st.session_state.pop("_modal_res_chart", None)
                    st.rerun()
        else:
            st.caption("Sin datos para este resumen.")
        st.markdown(
            "<p style='font-size:11px;color:#707D7D;margin:4px 0 6px 0;'>Ver detalle por variable:</p>",
            unsafe_allow_html=True,
        )
        _btn_cols = st.columns(len(variables))
        for _i, _var in enumerate(variables):
            _info = COLORES_VARIABLES.get(_var, {})
            with _btn_cols[_i]:
                if st.button(
                    f"{_info.get('emoji','📊')} {_var}",
                    key=f"_btn_det_{_var}",
                    use_container_width=True,
                ):
                    st.session_state["_var_detalle"] = _var
                    st.session_state["_barrio_detalle"] = barrio_nombre
                    st.session_state["_comuna_detalle"] = comuna_nombre
                    st.session_state["_abrir_var_detalle"] = True
                    st.session_state.pop("_modal_res_chart", None)
                    st.rerun()
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
    if st.button("Cerrar", width="stretch", type="primary"):
        st.rerun()


DETALLES_ANALISIS = {
    "Aire": {
        "titulo": "🌫️ Calidad del Aire",
        "html": """
<p style="font-weight: 700; color: #F1F7F6; margin-top: 0; margin-bottom: 12px; font-size: 1.05rem;">Análisis con datos</p>
<p style="margin-bottom: 10px;">El crecimiento vehicular es uno de los principales factores de contaminación atmosférica.</p>
<p style="margin-bottom: 10px;">Medellín presenta una alta densidad vehicular comparada con otras ciudades.</p>
<p style="margin-bottom: 6px;">El aumento del parque automotor incrementa:</p>
<ul style="margin-top: 0; margin-bottom: 14px; padding-left: 20px; list-style-type: disc;">
    <li style="margin-bottom: 4px;">material particulado,</li>
    <li style="margin-bottom: 4px;">gases contaminantes,</li>
    <li style="margin-bottom: 4px;">afectaciones respiratorias.</li>
</ul>
<p style="margin-bottom: 14px;">Las zonas más urbanizadas y con mayor tráfico son las más impactadas ambientalmente.</p>
<p style="border-top: 1px solid rgba(44, 194, 149, 0.2); padding-top: 12px; margin-top: 12px; font-size: 0.92rem; color: #F1F7F6; line-height: 1.5;">
En Medellín, el crecimiento vehicular y la alta densidad urbana afectan directamente la calidad del aire. El ICVEPC indica que actualmente existe aproximadamente 1 vehículo por cada 2 habitantes, aumentando la presión ambiental sobre la ciudad.
</p>
"""
    },
    "Ríos": {
        "titulo": "🌊 Estado de los Ríos",
        "html": """
<p style="margin-bottom: 12px;">Más de 900 mil toneladas de basura generadas anualmente aumentan el riesgo de contaminación hídrica.</p>
<p style="margin-bottom: 6px;">Menos del 30% de residuos se reutiliza, por lo que gran parte termina:</p>
<ul style="margin-top: 0; margin-bottom: 14px; padding-left: 20px; list-style-type: disc;">
    <li style="margin-bottom: 4px;">en rellenos,</li>
    <li style="margin-bottom: 4px;">quebradas,</li>
    <li style="margin-bottom: 4px;">drenajes urbanos.</li>
</ul>
<p style="margin-bottom: 6px;">El manejo inadecuado de escombros también afecta:</p>
<ul style="margin-top: 0; margin-bottom: 6px; padding-left: 20px; list-style-type: disc;">
    <li style="margin-bottom: 4px;">quebradas,</li>
    <li style="margin-bottom: 4px;">alcantarillado,</li>
    <li style="margin-bottom: 4px;">sistemas de drenaje.</li>
</ul>
"""
    },
    "Ruido": {
        "titulo": "🔊 Contaminación Auditiva",
        "html": """
<p style="margin-bottom: 6px;">El 46% de los homicidios de 2024 estuvieron relacionados con:</p>
<ul style="margin-top: 0; margin-bottom: 14px; padding-left: 20px; list-style-type: disc;">
    <li style="margin-bottom: 4px;">problemas de convivencia,</li>
    <li style="margin-bottom: 4px;">violencia intrafamiliar,</li>
    <li style="margin-bottom: 4px;">feminicidios.</li>
</ul>
<p style="margin-bottom: 6px;">Se registraron:</p>
<ul style="margin-top: 0; margin-bottom: 14px; padding-left: 20px; list-style-type: disc;">
    <li style="margin-bottom: 4px;">12.515 denuncias por violencia intrafamiliar,</li>
    <li style="margin-bottom: 4px;">4.599 casos de lesiones personales.</li>
</ul>
<p style="margin-bottom: 6px;">El ruido se relaciona con:</p>
<ul style="margin-top: 0; margin-bottom: 6px; padding-left: 20px; list-style-type: disc;">
    <li style="margin-bottom: 4px;">conflictos vecinales,</li>
    <li style="margin-bottom: 4px;">estrés urbano,</li>
    <li style="margin-bottom: 4px;">deterioro de convivencia.</li>
</ul>
"""
    },
    "Basuras": {
        "titulo": "🗑️ Manejo de Basuras",
        "html": """
<p style="margin-bottom: 10px;">Medellín generó más de 900.000 toneladas de residuos sólidos en 2023.</p>
<p style="margin-bottom: 10px;">Cada habitante produce más de 1 kg de basura diaria.</p>
<p style="margin-bottom: 10px;">La meta ODS para 2030 es solo 0,3 kg por persona/día, por lo que Medellín produce más de 3 veces la meta internacional.</p>
<p style="margin-bottom: 10px;">Menos del 30% de residuos aprovechables son reutilizados.</p>
<p style="margin-bottom: 10px;">El 80% de la población está satisfecha con la recolección de basura.</p>
<p style="margin-bottom: 6px;">Pero solo:</p>
<ul style="margin-top: 0; margin-bottom: 14px; padding-left: 20px; list-style-type: disc;">
    <li style="margin-bottom: 4px;">33% aprueba la limpieza de calles,</li>
    <li style="margin-bottom: 4px;">31% aprueba el manejo de escombros.</li>
</ul>
<p style="margin-bottom: 6px;">El relleno sanitario La Pradera tendría capacidad solo hasta 2030.</p>
"""
    },
    "Contaminación Visual": {
        "titulo": "👁️ Contaminación Visual",
        "html": """
<ul style="margin-top: 0; margin-bottom: 12px; padding-left: 20px; list-style-type: disc;">
    <li style="margin-bottom: 10px;">
        El crecimiento urbano acelerado genera:
        <ul style="margin-top: 4px; padding-left: 16px; list-style-type: circle; color: #707D7D;">
            <li style="margin-bottom: 2px;">saturación publicitaria,</li>
            <li style="margin-bottom: 2px;">ocupación desordenada del espacio público,</li>
            <li style="margin-bottom: 2px;">acumulación de escombros y cables.</li>
        </ul>
    </li>
    <li style="margin-bottom: 10px;">Solo el 33% de ciudadanos percibe adecuada limpieza de calles.</li>
    <li style="margin-bottom: 6px;">El bajo indicador refleja percepción negativa del entorno urbano.</li>
</ul>
"""
    }
}

@st.dialog("📊 Detalle por variable", width="large")
def modal_detalle_variable(df_local, variable_nombre, barrio_nombre, comuna_nombre):
    st.session_state["modal_detalle_runs_this_run"] = True
    st.session_state["modal_detalle_abierto"] = True
    safe_v = html.escape(str(variable_nombre))
    safe_b = html.escape(str(barrio_nombre))
    safe_c = html.escape(str(comuna_nombre))
    col_color = COLORES_VARIABLES.get(variable_nombre, {}).get("color", "#2CC295")
    col_emoji = COLORES_VARIABLES.get(variable_nombre, {}).get("emoji", "📊")
    _sel_prev_det = st.session_state.get("_det_estratos_sel", [])
    _lbl_estrato_det = "Todos los estratos" if not _sel_prev_det else " · ".join(_sel_prev_det)
    _n_resp_det = len(df_local)
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #021B1A 0%, #03624C 55%, #17876D 100%);
            color: #F1F7F6;
            padding: 1.1rem 1.25rem;
            border-radius: 12px;
            margin-bottom: 0.75rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        ">
            <div style="font-size:0.75rem;letter-spacing:0.14em;text-transform:uppercase;color:{col_color};">Detalle — percepción ambiental</div>
            <div style="font-size:1.35rem;font-weight:700;margin-top:0.35rem;color:#F1F7F6;">{col_emoji} {safe_v}</div>
            <div style="font-size:0.95rem;margin-top:0.25rem;color:#AACBC4;">🏡 {safe_b} · 📍 {safe_c}</div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                margin-top:0.65rem;border-top:1px solid rgba(255,255,255,0.15);padding-top:0.5rem;">
                <span style="font-size:0.82rem;color:#AACBC4;">📋 <strong>{_n_resp_det}</strong> respuestas</span>
                <span style="font-size:0.78rem;color:#707D7D;">{_lbl_estrato_det}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if df_local.empty:
        st.info("No hay registros para esta variable.")
        if st.button("← Volver", width="stretch"):
            st.session_state["modal_detalle_abierto"] = False
            st.session_state["_abrir_modal_barrio"] = True
            st.rerun()
        return

    # ── Filtro de estrato propio ──
    st.markdown(
        "<p style='font-size:11px;font-weight:700;color:#2CC295;text-transform:uppercase;"
        "letter-spacing:0.10em;margin:0 0 5px 0;border-bottom:1px solid #03624C;padding-bottom:5px;'>"
        "Filtrar por estrato</p>",
        unsafe_allow_html=True,
    )
    estratos_raw = sorted(
        [int(e) for e in df_local["11. Estrato"].dropna().unique() if str(e).isdigit()]
    )
    estratos_disponibles = [f"Estrato {e}" for e in estratos_raw]
    sel_estratos_det = st.multiselect(
        "_det_estratos_label",
        options=estratos_disponibles,
        key="_det_estratos_sel",
        placeholder="Sin selección = todos los estratos",
        label_visibility="collapsed",
    )
    estratos_sel_det = sel_estratos_det if sel_estratos_det else None

    cfg = {"displayModeBar": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}
    _, fig2, fig3 = figuras_estadisticas_barrio(
        df_local, [variable_nombre], estratos_sel=estratos_sel_det, altura=360
    )
    tab1, tab2 = st.tabs(["🏘️ Por estrato", "🥧 Distribución"])
    with tab1:
        if fig2:
            st.plotly_chart(fig2, width="stretch", config=cfg)
        else:
            st.caption("Sin datos por estrato.")
    with tab2:
        if fig3:
            col_chart, col_text = st.columns([1, 1], gap="medium")
            with col_chart:
                st.plotly_chart(fig3, use_container_width=True, config=cfg)
            with col_text:
                info_analisis = DETALLES_ANALISIS.get(variable_nombre, {"titulo": variable_nombre, "html": ""})
                titulo_var = info_analisis["titulo"]
                texto_var = info_analisis["html"]
                box_html = f"""<div class="analysis-box" style="background: linear-gradient(135deg, #011211 0%, #02362b 50%, #0e4f40 100%); border: 1.5px solid {col_color}aa; border-radius: 12px; padding: 1.25rem; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05); color: #F1F7F6; max-height: 360px; overflow-y: auto; font-family: inherit; animation: fadeIn 0.4s ease-out;">
<style>
@keyframes fadeIn {{
from {{ opacity: 0; transform: translateY(10px); }}
to {{ opacity: 1; transform: translateY(0); }}
}}
.analysis-box::-webkit-scrollbar {{
width: 6px;
}}
.analysis-box::-webkit-scrollbar-track {{
background: rgba(2, 27, 26, 0.5);
border-radius: 10px;
}}
.analysis-box::-webkit-scrollbar-thumb {{
background: {col_color}88;
border-radius: 10px;
}}
.analysis-box::-webkit-scrollbar-thumb:hover {{
background: {col_color};
}}
</style>
<div style="display: flex; align-items: center; gap: 8px; border-bottom: 1px solid {col_color}44; padding-bottom: 8px; margin-bottom: 12px;">
<span style="font-size: 1.25rem; font-weight: 700;">{titulo_var}</span>
</div>
<div style="font-size: 0.92rem; line-height: 1.6; color: #AACBC4;">
{texto_var}
</div>
</div>"""
                st.markdown(box_html, unsafe_allow_html=True)
        else:
            st.caption("Sin datos para la distribución.")
    st.divider()
    if st.button("← Volver", width="stretch", type="primary"):
        st.session_state["modal_detalle_abierto"] = False
        st.session_state["_abrir_modal_barrio"] = True
        st.rerun()


@st.dialog("ℹ️ Acerca de este dashboard", width="large")
def modal_acerca_de():
    st.markdown("""
<div style="background: linear-gradient(135deg, #021B1A 0%, #03624C 55%, #17876D 100%); color: #F1F7F6; padding: 1.1rem 1.25rem; border-radius: 12px; margin-bottom: 1rem; box-shadow: 0 8px 24px rgba(0,0,0,0.4);">
<div style="font-size:0.75rem;letter-spacing:0.14em;text-transform:uppercase;color:#2CC295;">Dashboard Ambiental · Medellín</div>
<div style="font-size:1.35rem;font-weight:700;margin-top:0.35rem;">🌿 Percepción Ambiental Ciudadana</div>
<div style="font-size:0.9rem;margin-top:0.25rem;color:#AACBC4;">Análisis multivariado de calidad ambiental por barrio y comuna</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="background:#021B1A;border:1px solid #03624C;border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.85rem;">
<p style="color:#2CC295;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;margin:0 0 8px 0;border-bottom:1px solid #03624C;padding-bottom:6px;">📋 Sobre el proyecto</p>
<p style="color:#AACBC4;font-size:0.92rem;line-height:1.65;margin:0;">Este dashboard interactivo visualiza la <strong style="color:#F1F7F6;">percepción ciudadana sobre cinco variables ambientales</strong> en Medellín: calidad del <em>Aire</em>, estado de los <em>Ríos</em>, <em>Ruido</em>, manejo de <em>Basuras</em> y <em>Contaminación Visual</em>. Los datos provienen de la Encuesta de Calidad de Vida 2025 de Medellín Cómo Vamos, aplicada a una muestra representativa de hogares en todas las comunas y corregimientos de la ciudad. El sistema permite explorar geográficamente las respuestas, comparar barrios y estratos socioeconómicos, y detectar patrones espaciales de insatisfacción ambiental.</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="background:#021B1A;border:1px solid #03624C;border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.85rem;">
<p style="color:#2CC295;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;margin:0 0 8px 0;border-bottom:1px solid #03624C;padding-bottom:6px;">⚙️ Estandarización y metodología</p>
<p style="color:#AACBC4;font-size:0.92rem;line-height:1.65;margin:0 0 10px 0;">Las respuestas originales de la encuesta (escala Likert ordinal) fueron <strong style="color:#F1F7F6;">recodificadas y estandarizadas</strong> en tres categorías comparables:</p>
<ul style="color:#AACBC4;font-size:0.92rem;line-height:1.8;margin:0 0 10px 0;padding-left:20px;">
<li><strong style="color:#2ecc71;">Buena</strong> — percepción positiva de la variable ambiental.</li>
<li><strong style="color:#f1c40f;">Regular</strong> — percepción intermedia o neutral.</li>
<li><strong style="color:#e74c3c;">Mala</strong> — percepción negativa o de deterioro.</li>
</ul>
<p style="color:#AACBC4;font-size:0.92rem;line-height:1.65;margin:0;">La normalización siguió el enfoque de <strong style="color:#F1F7F6;">análisis multivariado descriptivo</strong> (Rencher, 2002), agrupando respuestas por barrio y estrato para obtener la categoría dominante en cada unidad geográfica. Los valores faltantes fueron excluidos del cálculo proporcional para no sesgar los índices de percepción. La visualización geográfica se construyó sobre capas GeoJSON oficiales de Medellín, emparejadas con los registros de la encuesta mediante coincidencia difusa de nombres (fuzzy matching).</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="background:#021B1A;border:1px solid #03624C;border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.85rem;">
<p style="color:#2CC295;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;margin:0 0 8px 0;border-bottom:1px solid #03624C;padding-bottom:6px;">📊 Resultados principales</p>
<ul style="color:#AACBC4;font-size:0.92rem;line-height:1.8;margin:0;padding-left:20px;">
<li>La variable <strong style="color:#F1F7F6;">Aire</strong> presenta la mayor dispersión de percepción entre comunas, con zonas de alta densidad vehicular mostrando predominio de calificaciones <em>Malas</em>.</li>
<li>El estado de los <strong style="color:#F1F7F6;">Ríos</strong> refleja una percepción negativa generalizada, vinculada al manejo inadecuado de residuos sólidos y escombros en áreas periféricas.</li>
<li>La <strong style="color:#F1F7F6;">Contaminación por Ruido</strong> concentra la mayor proporción de conflictos vecinales reportados, con correlación directa con la densidad poblacional por barrio.</li>
<li>El manejo de <strong style="color:#F1F7F6;">Basuras</strong> muestra alta satisfacción en recolección (≈80%) pero baja aprobación en limpieza de calles (33%) y gestión de escombros (31%).</li>
<li>La <strong style="color:#F1F7F6;">Contaminación Visual</strong> es la variable con menor percepción negativa absoluta, aunque supera el umbral crítico en comunas de alta densidad comercial.</li>
</ul>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="background:#021B1A;border:1px solid #03624C;border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.85rem;">
<p style="color:#2CC295;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;margin:0 0 8px 0;border-bottom:1px solid #03624C;padding-bottom:6px;">📚 Bibliografía</p>
<ul style="color:#AACBC4;font-size:0.88rem;line-height:1.8;margin:0;padding-left:20px;">
<li>Medellín Cómo Vamos. <em>Medellín se mide: Calidad de Vida y Percepción Ciudadana 2025</em>. Dataset: <code style="background:#032221;padding:1px 5px;border-radius:4px;">ECV_2025_Limpio.csv</code>.</li>
<li>Rencher, A. C. <em>Methods of Multivariate Analysis</em>, 2.ª ed. Wiley, 2002.</li>
<li>Caballero G., L. J. <em>5.1 — Métodos estadísticos para análisis de datos ordinales en ciencias sociales</em>.</li>
</ul>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="background:#021B1A;border:1px solid #03624C;border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.5rem;">
<p style="color:#2CC295;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;margin:0 0 8px 0;border-bottom:1px solid #03624C;padding-bottom:6px;">👥 Creadores y Asesores</p>
<div style="display:flex;gap:2rem;flex-wrap:wrap;">
<div style="flex:1;min-width:200px;">
<p style="color:#F1F7F6;font-size:0.88rem;font-weight:700;margin:0 0 8px 0;text-transform:uppercase;letter-spacing:0.05em;">Creadores</p>
<ul style="color:#AACBC4;font-size:0.88rem;line-height:1.6;margin:0;padding-left:20px;">
<li>Camilo Carmona</li>
<li>Keyner Gil</li>
<li>Jeyson González</li>
<li>Marisol Roche</li>
</ul>
</div>
<div style="flex:1;min-width:200px;">
<p style="color:#F1F7F6;font-size:0.88rem;font-weight:700;margin:0 0 8px 0;text-transform:uppercase;letter-spacing:0.05em;">Asesores</p>
<ul style="color:#AACBC4;font-size:0.88rem;line-height:1.6;margin:0;padding-left:20px;">
<li>Ingry Gómez</li>
<li>Juan Zapata</li>
</ul>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    if st.button("Cerrar", width="stretch", type="primary"):
        st.rerun()


def _sidebar_seccion(titulo: str) -> None:
    st.sidebar.markdown(
        "<p style='margin:14px 0 8px 0;padding:0;font-size:11px;font-weight:700;"
        "color:#2CC295;text-transform:uppercase;letter-spacing:0.10em;border-bottom:1px solid #03624C;padding-bottom:6px;'>"
        + html.escape(titulo)
        + "</p>",
        unsafe_allow_html=True,
    )


# ── SVG del ícono QR (3 finder patterns + bits de datos, colores del tema) ──
_qr_svg = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 21 21' width='14' height='14'%3E"
    "%3Crect x='0' y='0' width='7' height='7' rx='1' fill='%23AACBC4'/%3E"
    "%3Crect x='1.5' y='1.5' width='4' height='4' fill='%23021B1A'/%3E"
    "%3Crect x='2.5' y='2.5' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='14' y='0' width='7' height='7' rx='1' fill='%23AACBC4'/%3E"
    "%3Crect x='15.5' y='1.5' width='4' height='4' fill='%23021B1A'/%3E"
    "%3Crect x='16.5' y='2.5' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='0' y='14' width='7' height='7' rx='1' fill='%23AACBC4'/%3E"
    "%3Crect x='1.5' y='15.5' width='4' height='4' fill='%23021B1A'/%3E"
    "%3Crect x='2.5' y='16.5' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='9' y='0' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='12' y='0' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='9' y='3' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='9' y='9' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='12' y='9' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='9' y='12' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='14' y='9' width='7' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='14' y='12' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='19' y='12' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='14' y='15' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='17' y='15' width='4' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='14' y='19' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3Crect x='19' y='19' width='2' height='2' fill='%23AACBC4'/%3E"
    "%3C/svg%3E"
)

# Área principal: mapa acotado al alto de la ventana (menos scroll vertical)
# Este st.markdown global aplica CSS a TODA la página (incluye sidebar)
st.markdown(
    f"""
<style>
  .main .block-container {{
    padding-top: 0.35rem !important;
    padding-bottom: 0 !important;
  }}
  div[data-testid="stIFrame"] iframe {{
    max-height: calc(100dvh - 3.5rem) !important;
    height: calc(100dvh - 3.5rem) !important;
    min-height: 280px;
  }}
  /* ── Sidebar: colores globales ── */
  [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {{
    background-color: #021B1A !important;
  }}
  [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{
    color: #AACBC4 !important;
  }}
  [data-testid="stSidebar"] .stCaption p {{
    color: #707D7D !important;
  }}
  [data-testid="stSidebar"] .stButton > button {{
    border-radius: 8px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 13px !important;
    padding: 7px 12px !important;
    height: auto !important;
    box-shadow: none !important;
    transition: border-color 0.15s, background 0.15s !important;
    margin-bottom: 4px !important;
    background: #032221 !important;
    border: 1.5px solid #03624C !important;
    color: #AACBC4 !important;
  }}
  [data-testid="stSidebar"] .stButton > button:hover {{
    border-color: #00DF81 !important;
    color: #F1F7F6 !important;
    background: #03624C !important;
  }}
  [data-testid="stSidebar"] .stButton > button:active,
  [data-testid="stSidebar"] .stButton > button:focus,
  [data-testid="stSidebar"] .stButton > button:focus-visible,
  [data-testid="stSidebar"] .stButton > button:focus:not(:focus-visible) {{
    background: #032221 !important;
    border-color: #03624C !important;
    color: #AACBC4 !important;
    box-shadow: none !important;
    outline: none !important;
  }}
  [data-testid="stSidebar"] [data-testid="column"] .stButton > button {{
    font-size: 12px !important;
    padding: 6px 8px !important;
  }}
  /* ── Ícono QR en el botón "Generar QR" ── */
  [data-testid="stSidebar"] button[title="Ver código QR del dashboard"]::before,
  [data-testid="stSidebar"] button[aria-label="Ver código QR del dashboard"]::before {{
    content: url("{_qr_svg}");
    margin-right: 7px;
    vertical-align: middle;
    display: inline-block;
    line-height: 0;
  }}
</style>
""",
    unsafe_allow_html=True,
)
MAP_ALTO_PX = 700

# ── SIDEBAR ──
# El CSS se inyecta PRIMERO antes de cualquier botón para que aplique a todos
st.sidebar.markdown(f"""
<style>
/* ── Sidebar fondo ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {{
    background-color: #021B1A !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {{
    color: #AACBC4 !important;
}}
[data-testid="stSidebar"] .stCaption p {{
    color: #707D7D !important;
}}

/* ── Botones sidebar: estado normal ── */
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
[data-testid="stSidebar"] [class*="stBaseButton"] {{
    border-radius: 8px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 13px !important;
    padding: 7px 12px !important;
    height: auto !important;
    box-shadow: none !important;
    transition: border-color 0.15s, background 0.15s !important;
    margin-bottom: 4px !important;
    background: #032221 !important;
    background-color: #032221 !important;
    border: 1.5px solid #03624C !important;
    color: #AACBC4 !important;
    outline: none !important;
}}

/* ── Hover ── */
[data-testid="stSidebar"] button:hover,
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover,
[data-testid="stSidebar"] [class*="stBaseButton"]:hover {{
    border-color: #00DF81 !important;
    color: #F1F7F6 !important;
    background: #03624C !important;
    background-color: #03624C !important;
}}

/* ── Active / Focus: sin fondo blanco ── */
[data-testid="stSidebar"] button:active,
[data-testid="stSidebar"] button:focus,
[data-testid="stSidebar"] button:focus-visible,
[data-testid="stSidebar"] .stButton > button:active,
[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:focus-visible,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:active,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:focus,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:focus-visible,
[data-testid="stSidebar"] [class*="stBaseButton"]:active,
[data-testid="stSidebar"] [class*="stBaseButton"]:focus,
[data-testid="stSidebar"] [class*="stBaseButton"]:focus-visible {{
    background: #032221 !important;
    background-color: #032221 !important;
    border-color: #03624C !important;
    color: #AACBC4 !important;
    box-shadow: none !important;
    outline: none !important;
}}

/* ── Botones en columnas del sidebar ── */
[data-testid="stSidebar"] [data-testid="column"] button,
[data-testid="stSidebar"] [data-testid="column"] .stButton > button {{
    font-size: 12px !important;
    padding: 6px 8px !important;
}}
</style>
""", unsafe_allow_html=True)


# ── Encabezado Filtros ──
st.sidebar.markdown(
    "<div style='background:linear-gradient(135deg,#021B1A,#03624C);padding:16px 12px 10px 12px;border-radius:10px;margin-bottom:8px;'>"
    "<span style='color:#00DF81;font-size:17px;font-weight:700;letter-spacing:1.5px;'>🔧 Filtros</span></div>",
    unsafe_allow_html=True
)
# ── Botón QR debajo del título ──
# ▦ = U+25A6 SQUARE WITH ORTHOGONAL CROSSHATCH FILL (simula los cuadros del QR)
if st.sidebar.button("▦ Generar QR", key="btn_abrir_qr", width="stretch", help="Ver código QR del dashboard"):
    st.session_state["_abrir_modal_qr"] = True
    st.rerun()
st.sidebar.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)


if st.session_state["comuna_click"] is None:
    _sidebar_seccion("Vista general")
    st.sidebar.caption("Color del mapa según la variable en todas las comunas.")
    render_variable_btns(opciones_vars, st.session_state["variable_global_val"], "gvar", "variable_global_val")
    variable_select = st.session_state["variable_global_val"]
    st.session_state["variable_comuna"] = ["Todas"]
else:
    variable_select = ["Todas"]

if st.session_state["comuna_click"]:
    _sidebar_seccion("Navegación")
    if st.sidebar.button("⬅️ Volver a todas las comunas", key="btn_volver", width="stretch"):
        st.session_state["comuna_click"] = None
        st.session_state["barrio_click"] = None
        st.session_state["map_center"] = [6.2442, -75.5812]
        st.session_state["map_zoom"] = 12
        st.session_state["variable_comuna"] = ["Todas"]
        st.rerun()
    _sidebar_seccion("Variable en el mapa")
    render_variable_btns(opciones_vars, st.session_state["variable_comuna"], "cvar", "variable_comuna")
    variable_select = st.session_state["variable_comuna"]
    _sidebar_seccion("Comuna activa")
    color_c = color_por_comuna.get(st.session_state["comuna_click"], "#888")
    cn = html.escape(str(st.session_state["comuna_click"]))
    st.sidebar.markdown(
        "<div style='background:#032221;border-left:5px solid "
        + color_c
        + ";padding:10px 12px;border-radius:8px;margin-bottom:2px;'>"
        "<span style='font-size:11px;color:#2CC295;text-transform:uppercase;letter-spacing:0.08em;'>"
        "Ubicación</span><br>"
        "<span style='font-size:15px;font-weight:700;color:#F1F7F6;'>📍 "
        + cn
        + "</span></div>",
        unsafe_allow_html=True,
    )
    if st.session_state["barrio_click"]:
        _sidebar_seccion("Barrio activo")
        bn = html.escape(str(st.session_state["barrio_click"]))
        st.sidebar.markdown(
            "<div style='background:#032221;border-left:5px solid #2CC295;padding:10px 12px;border-radius:8px;'>"
            "<span style='font-size:11px;color:#2CC295;text-transform:uppercase;letter-spacing:0.08em;'>"
            "Selección</span><br>"
            "<span style='font-size:14px;font-weight:700;color:#F1F7F6;'>🏡 "
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
            "<span style='font-size:10px;color:#AACBC4;'>"
            + comuna_esc
            + "</span></div>",
            unsafe_allow_html=True,
        )

# ── Botón Acerca de (parte inferior del sidebar) ──
if "_abrir_modal_acerca" not in st.session_state:
    st.session_state["_abrir_modal_acerca"] = False

st.sidebar.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<div style='border-top:1px solid #03624C;margin-bottom:8px;'></div>",
    unsafe_allow_html=True,
)
if st.sidebar.button("ℹ️ Acerca de", key="btn_acerca_de", width="stretch", help="Información del proyecto y metodología"):
    st.session_state["_abrir_modal_acerca"] = True
    st.rerun()

# ── MAPA ──
modo = "comunas" if st.session_state["comuna_click"] is None else "barrios"

COLORES_ESTRATO = {1:"#e74c3c",2:"#e67e22",3:"#f1c40f",4:"#2ecc71",5:"#3498db",6:"#9b59b6"}

datos_dict = {}
if modo == "barrios":
    df_comuna = df_base[df_base["comuna"] == st.session_state["comuna_click"]]
    vars_activas = variables if "Todas" in variable_select else list(variable_select)
    df_long = df_comuna.melt(
        id_vars=["barrio"],
        value_vars=vars_activas,
        var_name="Variable",
        value_name="Valor",
    )
    df_long["categoria"] = df_long["Valor"].apply(map_categoria)
    df_dom = df_long.groupby(["barrio", "categoria"]).size().reset_index(name="count")
    df_dom = df_dom.loc[df_dom.groupby("barrio")["count"].idxmax()]
    for _, row in df_dom.iterrows():
        datos_dict[limpiar(row["barrio"])] = {"val": row["categoria"], "tipo": "categoria"}

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
        elif info["tipo"] == "categoria":
            color = COLOR_MAP_CATEG.get(info["val"], "#bdc3c7")
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
    if "Todas" in variable_select:
        label_leyenda = "🌐 Categoría predominante: Todas las variables"
    else:
        emojis = " ".join(COLORES_VARIABLES.get(v, {}).get("emoji", "") for v in variable_select)
        label_leyenda = emojis + " Categoría predominante: " + " + ".join(variable_select)
    leyenda = (
        "<div style='position:fixed;bottom:30px;right:30px;background:white;padding:10px 14px;"
        "border-radius:6px;z-index:999;box-shadow:2px 2px 6px rgba(0,0,0,0.3);font-size:13px;'>"
        "<b>" + label_leyenda + "</b><br><br>"
        "<span style='color:#2ecc71'>■</span> Muy buena<br>"
        "<span style='color:#27ae60'>■</span> Buena<br>"
        "<span style='color:#f1c40f'>■</span> Aceptable<br>"
        "<span style='color:#e67e22'>■</span> Mala<br>"
        "<span style='color:#e74c3c'>■</span> Muy mala<br>"
        "<span style='color:#bdc3c7'>■</span> Sin información</div>"
    )
    mapa.get_root().html.add_child(folium.Element(leyenda))

st.markdown(
    "<h3 style='color:#2CC295;font-weight:700;letter-spacing:0.01em;margin-bottom:0.3rem;'>"
    "Vivir en la ciudad — ¿Qué tan sano es nuestro entorno para todos?</h3>",
    unsafe_allow_html=True,
)

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

if st.session_state.pop("_abrir_var_detalle", False):
    var_det = st.session_state.get("_var_detalle")
    barrio_det = st.session_state.get("_barrio_detalle") or st.session_state.get("barrio_click")
    comuna_det = st.session_state.get("_comuna_detalle") or st.session_state.get("comuna_click")
    if var_det and barrio_det and comuna_det:
        st.session_state.pop("_det_estratos_sel", None)
        _df_modal = filtrar_datos_barrio_seleccionado(df_base)
        modal_detalle_variable(_df_modal, var_det, barrio_det, comuna_det)

elif st.session_state.pop("_abrir_modal_barrio", False):
    if (
        modo == "barrios"
        and st.session_state.get("barrio_click")
        and st.session_state.get("comuna_click")
    ):
        st.session_state.pop("_modal_res_chart", None)
        st.session_state["_modal_estratos_sel"] = []
        _df_modal = filtrar_datos_barrio_seleccionado(df_base)
        modal_estadisticas_barrio(
            _df_modal,
            st.session_state["barrio_click"],
            st.session_state["comuna_click"],
        )

if st.session_state.pop("_abrir_modal_qr", False):
    modal_qr()

if st.session_state.pop("_abrir_modal_acerca", False):
    modal_acerca_de()

if not st.session_state.get("modal_detalle_runs_this_run", False):
    st.session_state["modal_detalle_abierto"] = False
