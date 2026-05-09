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
        if st.sidebar.button(f"{info['emoji']} {op}", key=f"{key_prefix}_{op}", use_container_width=True):
            st.session_state[state_key] = op
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

def generar_popup_html(df_local, nombre_zona, variable_activa):
    if df_local.empty:
        return "<div style='padding:20px;font-family:sans-serif;'><h4>" + nombre_zona + "</h4><p>Sin datos.</p></div>"
    vars_mostrar = variables if variable_activa == "Todas" else [variable_activa]
    resultados = []
    for col_var in vars_mostrar:
        df_temp = df_local.copy()
        df_temp["categoria"] = df_temp[col_var].apply(map_categoria)
        negativos = df_temp[df_temp["categoria"].isin(["Mala", "Muy mala"])].shape[0]
        total = len(df_temp)
        if total > 0:
            resultados.append({"Variable": col_var, "Porcentaje Negativo": round((negativos/total)*100, 1)})
    html_g1 = ""
    if resultados:
        df_plot1 = pd.DataFrame(resultados).sort_values("Porcentaje Negativo", ascending=True)
        fig1 = px.bar(df_plot1, x="Porcentaje Negativo", y="Variable", orientation='h',
                      title="1. Top Problemas (Percepción Negativa %)",
                      color="Porcentaje Negativo", color_continuous_scale="Reds")
        fig1.update_layout(margin=dict(l=0,r=0,t=40,b=0), height=200, coloraxis_showscale=False)
        html_g1 = fig1.to_html(full_html=False, include_plotlyjs='cdn')
    df_long = df_local.melt(id_vars=["11. Estrato"], value_vars=vars_mostrar, var_name="Variable", value_name="Valor")
    df_long["categoria"] = df_long["Valor"].apply(map_categoria)
    df_plot2 = df_long.groupby(["11. Estrato", "categoria"]).size().reset_index(name="count")
    html_g2 = ""
    if not df_plot2.empty:
        df_plot2["total"] = df_plot2.groupby("11. Estrato")["count"].transform("sum")
        df_plot2["Pct"] = ((df_plot2["count"] / df_plot2["total"]) * 100).round(0)
        fig2 = px.bar(df_plot2, x="11. Estrato", y="Pct", color="categoria", barmode="stack",
                      title="2. Percepción por Estrato",
                      color_discrete_map={"Muy buena":"#2ecc71","Buena":"#27ae60","Aceptable":"#f1c40f","Mala":"#e67e22","Muy mala":"#e74c3c","No sabe":"#bdc3c7"},
                      category_orders={"categoria":["Muy buena","Buena","Aceptable","Mala","Muy mala","No sabe"]})
        fig2.update_layout(margin=dict(l=0,r=0,t=40,b=0), height=250)
        html_g2 = fig2.to_html(full_html=False, include_plotlyjs=False)
    df_pie = df_long["categoria"].value_counts().reset_index()
    df_pie.columns = ["categoria", "count"]
    html_g3 = ""
    if not df_pie.empty:
        fig3 = px.pie(df_pie, values="count", names="categoria",
                      title="3. Distribución (" + variable_activa + ")",
                      color="categoria",
                      color_discrete_map={"Muy buena":"#2ecc71","Buena":"#27ae60","Aceptable":"#f1c40f","Mala":"#e67e22","Muy mala":"#e74c3c","No sabe":"#bdc3c7"})
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        fig3.update_layout(margin=dict(l=0,r=0,t=40,b=0), height=250, showlegend=False)
        html_g3 = fig3.to_html(full_html=False, include_plotlyjs=False)
    return (
        "<div style='width:500px;height:500px;overflow-y:scroll;overflow-x:hidden;font-family:sans-serif;padding:5px;box-sizing:border-box;'>"
        "<h3 style='margin-top:0;text-align:center;color:#2c3e50;position:sticky;top:0;background:white;z-index:10;padding-bottom:10px;border-bottom:1px solid #ccc;'>"
        + nombre_zona + "</h3>" + html_g1 + "<div style='height:15px;'></div>" + html_g2 + "<div style='height:15px;'></div>" + html_g3 + "</div>"
    )

# ── TÍTULO ──
st.title("🌿 Dashboard Ambiental - Medellín")
st.markdown("Explora el mapa. **Haz click en una comuna** para ver sus barrios, luego **haz click en un barrio** para ver gráficas detalladas.")

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
}
</style>
""", unsafe_allow_html=True)

if st.session_state["comuna_click"] is None:
    st.sidebar.markdown("<p style='font-size:13px;color:#555;margin-bottom:4px;'><b>Variable ambiental</b></p>", unsafe_allow_html=True)
    render_variable_btns(opciones_vars, st.session_state["variable_global_val"], "gvar", "variable_global_val")
    variable_select = st.session_state["variable_global_val"]
    st.session_state["variable_comuna"] = "Todas"
else:
    variable_select = "Todas"

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
        st.session_state["variable_comuna"] = "Todas"
        st.rerun()

if st.session_state["barrio_click"]:
    st.sidebar.markdown(
        "<div style='background:#f0f0f0;border-left:5px solid #555;padding:10px 12px;border-radius:6px;margin-top:8px;'>"
        "<span style='font-size:11px;color:#777;text-transform:uppercase;letter-spacing:1px;'>Barrio activo</span><br>"
        "<span style='font-size:14px;font-weight:700;color:#2c3e50;'>🏡 " + st.session_state["barrio_click"] + "</span></div>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("❌ Quitar selección de Barrio", use_container_width=True):
        st.session_state["barrio_click"] = None
        st.rerun()

if st.session_state["comuna_click"] is None:
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='font-size:13px;font-weight:700;color:#2c3e50;margin-bottom:6px;'>🗺️ Comunas</p>", unsafe_allow_html=True)
    cols = st.sidebar.columns(2)
    for i, (comuna, color) in enumerate(color_por_comuna.items()):
        cols[i % 2].markdown(
            "<div style='display:flex;align-items:center;gap:5px;margin-bottom:4px;'>"
            "<span style='display:inline-block;width:10px;height:10px;border-radius:50%;background:" + color + ";'></span>"
            "<span style='font-size:10px;color:#444;'>" + comuna + "</span></div>",
            unsafe_allow_html=True
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