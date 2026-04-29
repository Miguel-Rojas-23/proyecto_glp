import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from modules.data_loader import cargar_datos
from modules.filters import aplicar_filtros
from modules.metrics import calcular_kpis
from modules.visualizations import grafico_precio_producto, grafico_radar
from modules.business_logic import calcular_score, clasificar, recomendacion
from modules.utils import normalizar
from modules.arquitectura import arquitectura


# ── CONFIG ─────────────────────────
st.set_page_config(page_title="GLP Perú", layout="wide")


# ── CACHE ─────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    return cargar_datos()


# ── LOAD ─────────────────────────
with st.spinner("⏳ Inicializando dashboard..."):
    df = load_data()

if df.empty:
    st.error("❌ No hay datos")
    st.stop()


# ── VALIDACIÓN COLUMNAS ───────────
columnas_requeridas = [
    "id_region", "producto", "rango_precio",
    "precio_de_venta_(soles)", "indice_demanda",
    "marca", "distrito", "año", "mes"
]

faltantes = [col for col in columnas_requeridas if col not in df.columns]

if faltantes:
    st.error(f"❌ Faltan columnas: {faltantes}")
    st.stop()


# ── FIX NUMÉRICOS ─────────────────
columnas_numericas = [
    "precio_de_venta_(soles)",
    "indice_demanda",
    "año",
    "mes"
]

for col in columnas_numericas:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["precio_de_venta_(soles)", "indice_demanda"])


# ── LIMPIEZA STREAMLIT SAFE ───────
df = df.dropna(subset=["id_region", "producto", "rango_precio"])


# ── SIDEBAR ──────────────────────
with st.sidebar:
    st.title("🎛️ Filtros")

    regiones = sorted(df["id_region"].dropna().unique().tolist())
    productos_top = df["producto"].value_counts().head(10).index.tolist()
    rangos = sorted(df["rango_precio"].dropna().unique().tolist())

    region = st.multiselect("Región", regiones, default=regiones)
    producto = st.multiselect("Producto (Top 10)", productos_top, default=productos_top)
    rango = st.multiselect("Rango", rangos, default=rangos)

    precio_min = float(df["precio_de_venta_(soles)"].min())
    precio_max = float(df["precio_de_venta_(soles)"].max())

    if pd.isna(precio_min) or pd.isna(precio_max):
        st.error("Datos de precio inválidos")
        st.stop()

    precio_range = st.slider(
        "Precio",
        min_value=precio_min,
        max_value=precio_max,
        value=(precio_min, precio_max)
    )


# ── FILTRO ───────────────────────
df_f = aplicar_filtros(df, region, producto, rango, precio_range)

if df_f.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados")
    st.stop()

st.info(f"🔍 Mostrando {len(df_f)} de {len(df)} registros")


# ── HEADER ──────────────────────
st.title("⛽ Dashboard GLP Perú")
st.divider()


# ── SAFE FUNC ───────────────────
def safe(x):
    return 0 if pd.isna(x) else x


# ── KPI ─────────────────────────
kpis = calcular_kpis(df_f)
kpis_full = calcular_kpis(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Registros",
            safe(kpis["registros"]),
            delta=safe(kpis["registros"] - kpis_full["registros"]))

col2.metric("Promedio",
            round(safe(kpis["precio_promedio"]), 2),
            delta=round(safe(kpis["precio_promedio"] - kpis_full["precio_promedio"]), 2))

col3.metric("Máximo", round(safe(kpis["precio_max"]), 2))
col4.metric("Mínimo", round(safe(kpis["precio_min"]), 2))

st.divider()


# ── TABS ────────────────────────
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Arquitectura",
    "Resumen",
    "Geográfico",
    "Análisis",
    "Correlación",
    "Explorador"
])


# ── TAB 0 ───────────────────────
with tab0:
    st.markdown(arquitectura)


# ── TAB 1 ───────────────────────
with tab1:
    fig_producto = grafico_precio_producto(df_f)
    st.plotly_chart(fig_producto, width="stretch")

    dist = df_f["rango_precio"].value_counts().reset_index()
    dist.columns = ["rango", "cantidad"]

    fig_pie = px.pie(
        dist,
        names="rango",
        values="cantidad",
        hole=0.4
    )

    st.plotly_chart(fig_pie, width="stretch")


# ── TAB 2 ───────────────────────
with tab2:
    geo = df_f.groupby("id_region")["precio_de_venta_(soles)"].mean().reset_index()

    fig_geo = px.bar(
        geo,
        x="id_region",
        y="precio_de_venta_(soles)",
        text_auto=".2f"
    )

    st.plotly_chart(fig_geo, width="stretch")


# ── TAB 3 ───────────────────────
with tab3:
    df_plot = df_f.sample(min(5000, len(df_f)), random_state=42)

    top = df_plot["producto"].value_counts().head(5).index
    df_plot["grupo"] = df_plot["producto"].apply(lambda x: x if x in top else "Otros")

    fig_scatter = px.scatter(
        df_plot,
        x="indice_demanda",
        y="precio_de_venta_(soles)",
        color="grupo"
    )

    st.plotly_chart(fig_scatter, width="stretch")


# ── TAB 4 ───────────────────────
with tab4:
    corr = df_f[["precio_de_venta_(soles)", "indice_demanda"]].corr()

    fig_corr = go.Figure(data=go.Heatmap(z=corr.values))
    st.plotly_chart(fig_corr, width="stretch")


# ── TAB 5 ───────────────────────
with tab5:

    productos = df_f["producto"].dropna().unique().tolist()

    producto_sel = st.selectbox("Producto", productos)

    df_p = df_f[df_f["producto"] == producto_sel]

    if not df_p.empty:

        precio = df_p["precio_de_venta_(soles)"].mean()
        demanda = df_p["indice_demanda"].mean()
        variabilidad = df_p["precio_de_venta_(soles)"].std() or 0

        valores = [
            normalizar(precio, df_f["precio_de_venta_(soles)"].min(), df_f["precio_de_venta_(soles)"].max()),
            normalizar(demanda, df_f["indice_demanda"].min(), df_f["indice_demanda"].max()),
            normalizar(variabilidad, 0, df_f["precio_de_venta_(soles)"].std() or 1),
            0.5,
            0.5
        ]

        score = calcular_score(valores)
        estado, color = clasificar(score)

        st.metric("Score", score)
        st.markdown(f"Estado: :{color}[{estado}]")
        st.info(recomendacion(score, valores[0], valores[1], valores[2]))

        fig_radar = grafico_radar(valores, producto_sel)
        st.plotly_chart(fig_radar, width="stretch")