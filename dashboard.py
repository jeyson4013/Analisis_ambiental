import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import unicodedata
import re
import folium
from branca.element import MacroElement
from folium.template import Template
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

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "comuna_click" not in st.session_state:
    st.session_state["comuna_click"] = None
if "barrio_click" not in st.session_state:
    st.session_state["barrio_click"] = None
if "map_center" not in st.session_state:
    st.session_state["map_center"] = [6.2442, -75.5812]
if "map_zoom" not in st.session_state:
    st.session_state["map_zoom"] = 12

# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────
def limpiar(texto):
    if not texto: return ""
    texto = str(texto).upper().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^A-Z0-9 ]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()

def encontrar_mejor_match(texto, lista, cutoff=0.7):
    if not texto: return None
    texto_lim = limpiar(texto)
    matches = get_close_matches(texto_lim, lista, n=1, cutoff=cutoff)
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

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando datos del xlsx...")
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
            c_clean = re.sub(r'COMUNA \d+ ', '', limpiar(c_raw))
            props["comuna_limpia"] = c_clean
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

# ─────────────────────────────────────────────
# GENERADOR DE POPUP HTML
# ─────────────────────────────────────────────
def generar_popup_html(df_local, nombre_zona, variable_activa):
    if df_local.empty:
        return f"<div style='padding:20px; font-family:sans-serif;'><h4>{nombre_zona}</h4><p>Sin datos para los filtros actuales.</p></div>"
        
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
                      color_discrete_map={
                          "Muy buena": "#2ecc71", "Buena": "#27ae60",
                          "Aceptable": "#f1c40f", "Mala": "#e67e22",
                          "Muy mala": "#e74c3c", "No sabe": "#bdc3c7"
                      },
                      category_orders={"categoria": ["Muy buena", "Buena", "Aceptable", "Mala", "Muy mala", "No sabe"]})
        fig2.update_layout(margin=dict(l=0,r=0,t=40,b=0), height=250)
        html_g2 = fig2.to_html(full_html=False, include_plotlyjs=False)
        
    df_pie = df_long["categoria"].value_counts().reset_index()
    df_pie.columns = ["categoria", "count"]
    html_g3 = ""
    if not df_pie.empty:
        fig3 = px.pie(df_pie, values="count", names="categoria", 
                      title=f"3. Distribución General ({variable_activa})",
                      color="categoria",
                      color_discrete_map={
                          "Muy buena": "#2ecc71", "Buena": "#27ae60",
                          "Aceptable": "#f1c40f", "Mala": "#e67e22",
                          "Muy mala": "#e74c3c", "No sabe": "#bdc3c7"
                      })
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        fig3.update_layout(margin=dict(l=0,r=0,t=40,b=0), height=250, showlegend=False)
        html_g3 = fig3.to_html(full_html=False, include_plotlyjs=False)
        
    html = f"""
    <div style="width: 500px; height: 500px; overflow-y: scroll; overflow-x: hidden; font-family: sans-serif; padding: 5px; box-sizing: border-box;">
        <h3 style="margin-top:0; text-align:center; color:#2c3e50; position: sticky; top: 0; background: white; z-index: 10; padding-bottom: 10px; border-bottom: 1px solid #ccc;">{nombre_zona}</h3>
        {html_g1}
        <div style="height: 15px;"></div>
        {html_g2}
        <div style="height: 15px;"></div>
        {html_g3}
    </div>
    """
    return html

# ─────────────────────────────────────────────
# UI PRINCIPAL Y SIDEBAR
# ─────────────────────────────────────────────
st.title("Dashboard Ambiental - Medellín")
st.markdown("Explora el mapa interactivo. **Haz click en una comuna** para ver sus barrios, y luego **haz click en un barrio** para ver sus gráficas detalladas.")

st.sidebar.header("Filtros Globales")
estratos = st.sidebar.multiselect(
    "Selecciona Estrato",
    options=sorted(df_base["11. Estrato"].unique()),
    default=sorted(df_base["11. Estrato"].unique()),
)

variable_select = st.sidebar.selectbox("Filtro: Variable a visualizar", ["Todas"] + variables)

if st.session_state["comuna_click"]:
    st.sidebar.markdown("---")
    st.sidebar.success(f"📍 **Comuna:** {st.session_state['comuna_click']}")
    if st.sidebar.button("⬅️ Volver a todas las Comunas", use_container_width=True):
        st.session_state["comuna_click"] = None
        st.session_state["barrio_click"] = None
        st.session_state["map_center"] = [6.2442, -75.5812]
        st.session_state["map_zoom"] = 12
        st.rerun()

if st.session_state["barrio_click"]:
    st.sidebar.info(f"🏡 **Barrio:** {st.session_state['barrio_click']}")
    if st.sidebar.button("❌ Quitar selección de Barrio", use_container_width=True):
        st.session_state["barrio_click"] = None
        st.rerun()

df = df_base[df_base["11. Estrato"].isin(estratos)].copy()

# ─────────────────────────────────────────────
# MAPA JERÁRQUICO
# ─────────────────────────────────────────────
modo = "comunas" if st.session_state["comuna_click"] is None else "barrios"

# 1. Preparar datos para colorear
datos_dict = {}
if variable_select == "Todas":
    agrupador = "comuna" if modo == "comunas" else "barrio"
    df_group = df.groupby(agrupador).agg({"11. Estrato": "mean"}).reset_index()
    for _, row in df_group.iterrows():
        k = limpiar(row[agrupador])
        datos_dict[k] = {"val": round(row["11. Estrato"], 1), "tipo": "estrato"}
else:
    agrupador = "comuna" if modo == "comunas" else "barrio"
    df_temp = df.copy()
    df_temp["categoria"] = df_temp[variable_select].apply(map_categoria)
    df_temp["negativo"] = df_temp["categoria"].isin(["Mala", "Muy mala"]).astype(int)
    df_group = df_temp.groupby(agrupador)["negativo"].agg(['mean']).reset_index()
    for _, row in df_group.iterrows():
        k = limpiar(row[agrupador])
        datos_dict[k] = {"val": round(row["mean"] * 100, 1), "tipo": "porcentaje"}

COLORES_ESTRATO = {1: "#e74c3c", 2: "#e67e22", 3: "#f1c40f", 4: "#2ecc71", 5: "#3498db", 6: "#9b59b6"}
def obtener_color_porcentaje(pct):
    if pct < 10: return "#2ecc71"
    elif pct < 25: return "#f1c40f"
    elif pct < 50: return "#e67e22"
    else: return "#e74c3c"

def estilo(feature):
    props = feature["properties"]
    if modo == "comunas":
        llave = limpiar(props.get("comuna_df"))
        peso_borde = 0.5
    else:
        llave = props.get("barrio_limpio")
        peso_borde = 1.0

    info = datos_dict.get(llave, {"val": 0, "tipo": "desconocido"})
    if info["tipo"] == "estrato": color = COLORES_ESTRATO.get(round(info["val"]), "#bdc3c7")
    elif info["tipo"] == "porcentaje": color = obtener_color_porcentaje(info["val"])
    else: color = "#bdc3c7"
        
    if modo == "barrios" and st.session_state["barrio_click"]:
        if llave == limpiar(st.session_state["barrio_click"]):
            return {"fillColor": color, "color": "#000000", "weight": 3, "fillOpacity": 0.9}

    return {"fillColor": color, "color": "#333333", "weight": peso_borde, "fillOpacity": 0.7}

# 2. Construir Mapa
features_mostrar = []
for f in geojson.get("features", []):
    if modo == "comunas":
        features_mostrar.append(f)
    else:
        if f["properties"].get("comuna_df") == st.session_state["comuna_click"]:
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
    if modo == "comunas":
        aliases = ["Comuna:", "Barrio:"]
        fields = ["comuna_df", "NOMBRE"]
    else:
        aliases = ["Barrio:"]
        fields = ["NOMBRE"]
        
    folium.GeoJson(
        geo_filtrado,
        name="capa_base",
        style_function=estilo,
        tooltip=folium.GeoJsonTooltip(fields=fields, aliases=aliases, style="font-size:13px; font-weight:bold;")
    ).add_to(mapa)

# 3. Popup para Barrio Activo
if st.session_state["barrio_click"] and modo == "barrios":
    b_limpio = limpiar(st.session_state["barrio_click"])
    for f in features_mostrar:
        if f["properties"].get("barrio_limpio") == b_limpio:
            centroid = centroide_feature(f)
            if centroid:
                df_popup = df[df["barrio"] == st.session_state["barrio_click"]]
                html_popup = generar_popup_html(df_popup, st.session_state["barrio_click"], variable_select)
                iframe = folium.IFrame(html=html_popup, width=540, height=540)
                popup = folium.Popup(iframe, max_width=550)
                folium.Marker(
                    location=centroid,
                    icon=folium.Icon(color="red", icon="info-sign"),
                    popup=popup
                ).add_to(mapa)
            break

if bbox_capa:
    FitBoundsYLimiteZoomSalida(bbox_capa, pad_px=12, max_zoom=18).add_to(mapa)

if variable_select == "Todas":
    leyenda = """<div style="position:fixed; bottom:30px; right:30px; background:white; padding:10px; border-radius:5px; z-index:999; box-shadow:2px 2px 5px rgba(0,0,0,0.3);">
    <b>Estrato Promedio</b><br>
    <span style='color:#e74c3c'>■</span> 1 <span style='color:#e67e22'>■</span> 2 <span style='color:#f1c40f'>■</span> 3 <br>
    <span style='color:#2ecc71'>■</span> 4 <span style='color:#3498db'>■</span> 5 <span style='color:#9b59b6'>■</span> 6
    </div>"""
else:
    leyenda = """<div style="position:fixed; bottom:30px; right:30px; background:white; padding:10px; border-radius:5px; z-index:999; box-shadow:2px 2px 5px rgba(0,0,0,0.3);">
    <b>% Percepción Negativa</b><br>
    <span style='color:#2ecc71'>■</span> < 10% (Bajo)<br>
    <span style='color:#f1c40f'>■</span> 10% - 25% (Medio)<br>
    <span style='color:#e67e22'>■</span> 25% - 50% (Alto)<br>
    <span style='color:#e74c3c'>■</span> > 50% (Crítico)
    </div>"""
mapa.get_root().html.add_child(folium.Element(leyenda))

# 4. Renderizar
mapa_data = st_folium(
    mapa,
    use_container_width=True,
    height=750,
    returned_objects=["last_active_drawing"],
    key="mapa_medellin"
)

# 5. Manejo de Clicks
if mapa_data and mapa_data.get("last_active_drawing"):
    props = mapa_data["last_active_drawing"].get("properties", {})
    
    if modo == "comunas":
        c_click = props.get("comuna_df")
        if c_click and c_click != st.session_state["comuna_click"]:
            st.session_state["comuna_click"] = c_click
            coords = []
            for f in geojson.get("features", []):
                if f["properties"].get("comuna_df") == c_click:
                    c = centroide_feature(f)
                    if c: coords.append(c)
            if coords:
                lats = [c[0] for c in coords]
                lngs = [c[1] for c in coords]
                st.session_state["map_center"] = [sum(lats)/len(lats), sum(lngs)/len(lngs)]
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

# Espacio extra para que el mapa resalte bien
st.markdown("<br><br>", unsafe_allow_html=True)