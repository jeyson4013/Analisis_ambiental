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
            st.rerun()

@st.cache_data(show_spinner="Cargando datos...")
def cargar_datos():
    df = pd.read_excel("ECV_2025_Limpio.xlsx")
    df = df[df["4. Ubicación geográfica - Municipio"].str.contains("Medell", na=False)]
    df["barrio"] = df["7. Barrio o Vereda"].fillna("Sin información")
    df["comuna"] = df["6. Comuna o Corregimiento"].fillna("Sin información")
    return df

@st.cache_data(show_spinner="Cargando GeoJSON...")
def cargar_geojson():
    url = "https://cdn.jsdelivr.net/gh/juanfrans/estratosBogota@master/EstratosMedellin.geojson"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        geojson = r.json()
    except:
        return {"type": "FeatureCollection", "features": []}
    for f in geojson.get("features", []):
        props = f["properties"]
        props["barrio_limpio"] = limpiar(props.get("NOMBRE", ""))
        c_raw = props.get("Comuna")
        if c_raw:
            props["comuna_limpia"] = re.sub(r'COMUNA \d+ ', '', limpiar(c_raw))
        else:
            props["comuna_limpia"] = "SIN INFORMACION"
    return geojson

df_base = cargar_datos()
geojson = cargar_geojson()

comunas_df_lista = df_base["comuna"].dropna().unique().tolist()
comunas_df_norm = {limpiar(c): c for c in comunas_df_lista}
barrios_df_lista = df_base["barrio"].dropna().unique().tolist()
barrios_df_norm = {limpiar(b): b for b in barrios_df_lista}

for f in geojson.get("features", []):
    c_limpia = f["properties"].get("comuna_limpia")
    mejor_c = encontrar_mejor_match(c_limpia, list(comunas_df_norm.keys()), cutoff=0.5)
    f["properties"]["comuna_df"] = comunas_df_norm.get(mejor_c) if mejor_c else None

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
            resultados.append({"Variable": col_var, "Porcentaje Negativo": round((negativos/total)*100, 1)})
    html_g1 = ""
    if resultados:
        df_plot1 = pd.DataFrame(resultados).sort_values("Porcentaje Negativo", ascending=True)
        color_map_vars = {v: COLORES_VARIABLES.get(v, {}).get("color", "#2CC295") for v in variables}
        fig1 = px.bar(
            df_plot1,
            x="Porcentaje Negativo",
            y="Variable",
            orientation="h",
            title="Percepción negativa por variable — clic en barra para detalle",
            color="Variable",
            color_discrete_map=color_map_vars,
            text="Porcentaje Negativo",
        )
        fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig1.update_layout(
            margin=dict(l=8, r=48, t=52, b=8),
            height=altura,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#F1F7F6",
            xaxis=dict(title="% negativo", ticksuffix="%", showgrid=True, gridcolor="#AACBC4", range=[0, 100]),
            yaxis=dict(title=""),
            font=dict(size=12, color="#021B1A"),
            showlegend=False,
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
            plot_bgcolor="#F1F7F6",
            xaxis=dict(title="Estrato"),
            yaxis=dict(title="%", ticksuffix="%", range=[0, 105]),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.42,
                xanchor="center", x=0.5, title="", font=dict(size=10),
            ),
            font=dict(size=12, color="#021B1A"),
            bargap=0.22,
        )

    df_pie = df_long["categoria"].value_counts().reset_index()
    df_pie.columns = ["categoria", "count"]
    html_g3 = ""
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


@st.dialog("📊 Detalle por variable", width="large")
def modal_detalle_variable(df_local, variable_nombre, barrio_nombre, comuna_nombre):
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
            st.plotly_chart(fig3, width="stretch", config=cfg)
        else:
            st.caption("Sin datos para la distribución.")
    st.divider()
    if st.button("← Volver", width="stretch", type="primary"):
        st.session_state["_abrir_modal_barrio"] = True
        st.rerun()


def _sidebar_seccion(titulo: str) -> None:
    st.sidebar.markdown(
        "<p style='margin:14px 0 8px 0;padding:0;font-size:11px;font-weight:700;"
        "color:#2CC295;text-transform:uppercase;letter-spacing:0.10em;border-bottom:1px solid #03624C;padding-bottom:6px;'>"
        + html.escape(titulo)
        + "</p>",
        unsafe_allow_html=True,
    )

# ── TÍTULO ──
st.title("🌿 Dashboard Ambiental - Medellín")
st.markdown("Explora el mapa. **Haz click en una comuna** para ver sus barrios, luego **haz click en un barrio** para ver gráficas detalladas.")

# ── SIDEBAR ──
st.sidebar.markdown(
    "<div style='background:linear-gradient(135deg,#021B1A,#03624C);padding:16px 12px 10px 12px;border-radius:10px;margin-bottom:12px;'>"
    "<span style='color:#00DF81;font-size:17px;font-weight:700;letter-spacing:1.5px;'>🔧 Filtros</span></div>",
    unsafe_allow_html=True
)
st.sidebar.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
    background-color: #021B1A !important;
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
    color: #AACBC4 !important;
}
[data-testid="stSidebar"] .stCaption p {
    color: #707D7D !important;
}
[data-testid="stSidebar"] .stButton > button {
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
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: #00DF81 !important;
    color: #F1F7F6 !important;
    background: #03624C !important;
}
[data-testid="stSidebar"] [data-testid="column"] .stButton > button {
    font-size: 12px !important;
    padding: 6px 8px !important;
}
</style>
""", unsafe_allow_html=True)

if st.session_state["comuna_click"] is None:
    st.sidebar.markdown("<p style='font-size:13px;color:#555;margin-bottom:4px;'><b>Variable ambiental</b></p>", unsafe_allow_html=True)
    render_variable_btns(opciones_vars, st.session_state["variable_global_val"], "gvar", "variable_global_val")
    variable_select = st.session_state["variable_global_val"]
    st.session_state["variable_comuna"] = ["Todas"]
else:
    variable_select = ["Todas"]

if st.session_state["comuna_click"]:
    st.sidebar.markdown("---")
    color_c = color_por_comuna.get(st.session_state["comuna_click"], "#888")
    st.sidebar.markdown(
        "<div style='background:" + color_c + "22;border-left:5px solid " + color_c + ";padding:10px 12px;border-radius:6px;'>"
        "<span style='font-size:11px;color:#777;text-transform:uppercase;letter-spacing:1px;'>Comuna activa</span><br>"
        "<span style='font-size:15px;font-weight:700;color:#2c3e50;'>📍 " + st.session_state["comuna_click"] + "</span></div>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown("<br><p style='font-size:13px;color:#555;margin-bottom:4px;'><b>🔍 Variable en esta comuna</b></p>", unsafe_allow_html=True)
    render_variable_btns(opciones_vars, st.session_state["variable_comuna"], "cvar", "variable_comuna")
    variable_select = st.session_state["variable_comuna"]
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("⬅️ Volver a todas las Comunas", key="btn_volver", use_container_width=True):
        st.session_state["comuna_click"] = None
        st.session_state["barrio_click"] = None
        st.session_state["map_center"] = [6.2442, -75.5812]
        st.session_state["map_zoom"] = 12
        st.session_state["variable_comuna"] = ["Todas"]
        st.rerun()

if st.session_state["barrio_click"]:
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
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='font-size:13px;font-weight:700;color:#2c3e50;margin-bottom:6px;'>🗺️ Comunas</p>", unsafe_allow_html=True)
    cols = st.sidebar.columns(2)
    for i, (comuna, color) in enumerate(color_por_comuna.items()):
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

mapa = folium.Map(location=st.session_state["map_center"], zoom_start=st.session_state["map_zoom"], tiles="CartoDB positron")

features_mostrar = []
for f in geojson.get("features", []):
    if modo == "comunas":
        features_mostrar.append(f)
    elif f["properties"].get("comuna_df") == st.session_state["comuna_click"]:
        features_mostrar.append(f)

geo_filtrado = {"type": "FeatureCollection", "features": features_mostrar}

if features_mostrar:
    fields = ["comuna_df", "NOMBRE"] if modo == "comunas" else ["NOMBRE"]
    aliases = ["Comuna:", "Barrio:"] if modo == "comunas" else ["Barrio:"]
    folium.GeoJson(geo_filtrado, name="capa_base", style_function=estilo,
                   tooltip=folium.GeoJsonTooltip(fields=fields, aliases=aliases, style="font-size:13px;font-weight:bold;")
    ).add_to(mapa)

if st.session_state["barrio_click"] and modo == "barrios":
    b_limpio = limpiar(st.session_state["barrio_click"])
    for f in features_mostrar:
        if f["properties"].get("barrio_limpio") == b_limpio:
            centroid = centroide_feature(f)
            if centroid:
                df_popup = df_base[df_base["barrio"] == st.session_state["barrio_click"]]
                html_popup = generar_popup_html(df_popup, st.session_state["barrio_click"], variable_select)
                iframe = folium.IFrame(html=html_popup, width=540, height=540)
                folium.Marker(location=centroid, icon=folium.Icon(color="red", icon="info-sign"),
                              popup=folium.Popup(iframe, max_width=550)).add_to(mapa)
            break

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

mapa_data = st_folium(mapa, use_container_width=True, height=750, returned_objects=["last_active_drawing"], key="mapa_medellin")

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
        if b_limpio:
            match = encontrar_mejor_match(b_limpio, list(barrios_df_norm.keys()))
            nombre_final = barrios_df_norm.get(match)
            if nombre_final and nombre_final != st.session_state["barrio_click"]:
                st.session_state["barrio_click"] = nombre_final
                st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)
