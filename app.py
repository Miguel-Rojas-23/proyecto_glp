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
@st.cache_data
def load_data():
    return cargar_datos()

# ── LOAD ─────────────────────────
with st.spinner("⏳ Cargando datos..."):
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

# ── FIX NUMÉRICOS (🔥 IMPORTANTE)
columnas_numericas = [
    "precio_de_venta_(soles)",
    "indice_demanda",
    "año",
    "mes"
]

for col in columnas_numericas:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 🔥 FIX CRÍTICO: eliminar nulos en columnas clave
df = df.dropna(subset=["precio_de_venta_(soles)", "indice_demanda"])

st.success(f"✅ {len(df)} registros cargados correctamente")

# ── SIDEBAR ──────────────────────
with st.sidebar:
    st.title("🎛️ Filtros")

    region = st.multiselect(
        "Región",
        df["id_region"].unique(),
        default=df["id_region"].unique()
    )

    top_productos = df["producto"].value_counts().head(10).index

    producto = st.multiselect(
        "Producto (Top 10)",
        top_productos,
        default=top_productos
    )

    rango = st.multiselect(
        "Rango",
        df["rango_precio"].unique(),
        default=df["rango_precio"].unique()
    )

    precio_min = df["precio_de_venta_(soles)"].min(skipna=True)
    precio_max = df["precio_de_venta_(soles)"].max(skipna=True)

    precio_range = st.slider(
        "Precio",
        float(precio_min),
        float(precio_max),
        (float(precio_min), float(precio_max))
    )

# ── FILTRO ───────────────────────
df_f = aplicar_filtros(df, region, producto, rango, precio_range)

if df_f.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados")
    st.stop()

if len(df_f) < len(df):
    st.info(f"🔍 Mostrando {len(df_f)} de {len(df)} registros")

# ── HEADER ──────────────────────
st.title("⛽ Dashboard GLP Perú")
st.divider()

# ── KPI SAFE FUNCTION (🔥)
def safe(val):
    return 0 if pd.isna(val) else val

kpis = calcular_kpis(df_f)
kpis_full = calcular_kpis(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Registros", safe(kpis["registros"]),
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
    st.text(arquitectura)

# ── TAB 1 ───────────────────────
with tab1:
    fig_producto = grafico_precio_producto(df_f)

    fig_producto.update_layout(
        title="💰 Precio Promedio por Producto"
    )

    st.plotly_chart(fig_producto, use_container_width=True)

    dist = df_f["rango_precio"].value_counts().reset_index()
    dist.columns = ["rango", "cantidad"]

    fig_pie = px.pie(
    dist,
    names="rango",
    values="cantidad",
    hole=0.4,
    title="📊 Distribución por Rango de Precio"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ── TAB 2 ───────────────────────
with tab2:
    geo = df_f.groupby("id_region")["precio_de_venta_(soles)"].mean().reset_index()

    fig_geo = px.bar(
    geo,
    x="id_region",
    y="precio_de_venta_(soles)",
    text_auto=".2f",
    title="🗺️ Precio Promedio por Región"
    )
    st.plotly_chart(fig_geo, use_container_width=True)

# ── TAB 3 ───────────────────────
with tab3:
    st.subheader("📊 Análisis de Mercado")

    df_plot = df_f.sample(5000, random_state=42).copy() if len(df_f) > 5000 else df_f.copy()

    # 🔥 FIX: evitar saturación de colores
    top_n = 5
    top_productos_scatter = df_plot["producto"].value_counts().head(top_n).index

    df_plot["grupo_producto"] = df_plot["producto"].apply(
        lambda x: x if x in top_productos_scatter else "Otros"
    )

    # ── SCATTER ──
    st.markdown("### 📍 Relación Precio vs Demanda")

    fig_scatter = px.scatter(
    df_plot,
    x="indice_demanda",
    y="precio_de_venta_(soles)",
    color="grupo_producto",
    opacity=0.75,
    hover_data={
        "grupo_producto": False,
        "producto": True,
        "marca": True,
        "distrito": True,
        "precio_de_venta_(soles)": ":.2f",
        "indice_demanda": ":.2f"
        }
    )

    # 🔥 MEJORAS VISUALES
    fig_scatter.update_traces(
        marker=dict(
            size=11,          # tamaño círculos
            line=dict(width=1)
        )
    )

    fig_scatter.update_layout(
        height=650,
        font=dict(size=14),
        legend_title="Producto",
        xaxis_title="Índice de Demanda",
        yaxis_title="Precio de Venta (S/.)"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    # ── TENDENCIA ──
    producto_trend = st.selectbox("Producto tendencia", df_f["producto"].unique())

    st.markdown("### 📈 Tendencia de Precio en el Tiempo")

    trend = df_f[df_f["producto"] == producto_trend]

    if not trend.empty:
        trend = trend.groupby(["año", "mes"])["precio_de_venta_(soles)"].mean().reset_index()

        trend["periodo"] = pd.to_datetime(
            trend["año"].astype(int).astype(str) + "-" + trend["mes"].astype(int).astype(str) + "-01"
        )

        trend = trend.sort_values("periodo")

        fig_line = px.line(
            trend,
            x="periodo",
            y="precio_de_venta_(soles)",
            markers=True
        )

        fig_line.update_traces(line=dict(width=3))  # 🔥 línea más gruesa

        st.plotly_chart(fig_line, use_container_width=True)

    # ── BOXPLOT ──
    st.markdown("### 📦 Distribución de Precios por Marca")

    fig_box = px.box(
    df_f,
    x="marca",
    y="precio_de_venta_(soles)",
    color="marca",
    points="outliers"
    )

    # 🔥 aumentar tamaño de puntos
    fig_box.update_traces(
        marker=dict(
            size=9,
            opacity=0.7,
            line=dict(width=1)
        )
    )

    fig_box.update_layout(
        height=650,
        font=dict(size=14),
        xaxis_title="Marca",
        yaxis_title="Precio de Venta (S/.)"
    )

    st.plotly_chart(fig_box, use_container_width=True)
# ── TAB 4 ───────────────────────
with tab4:
    corr_data = df_f[["precio_de_venta_(soles)", "indice_demanda"]].dropna()

    corr = corr_data.corr()

    fig_corr = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        text=corr.values,
        texttemplate="%{text:.2f}",
        zmin=-1,
        zmax=1
    ))
    fig_corr.update_layout(
    title="🔥 Matriz de Correlación"
    )

    st.plotly_chart(fig_corr, use_container_width=True)

# ── TAB 5 ───────────────────────
with tab5:
    producto_sel = st.selectbox("Producto", df_f["producto"].unique())
    df_p = df_f[df_f["producto"] == producto_sel]

    if not df_p.empty:

        precio = df_p["precio_de_venta_(soles)"].mean()
        demanda = df_p["indice_demanda"].mean()
        variabilidad = df_p["precio_de_venta_(soles)"].std()

        if pd.isna(variabilidad):
            variabilidad = 0

        std_global = df_f["precio_de_venta_(soles)"].std()
        if std_global == 0 or pd.isna(std_global):
            std_global = 1

        valores = [
            normalizar(precio, df_f["precio_de_venta_(soles)"].min(), df_f["precio_de_venta_(soles)"].max()),
            normalizar(demanda, df_f["indice_demanda"].min(), df_f["indice_demanda"].max()),
            normalizar(variabilidad, 0, std_global),
            normalizar(len(df_p), 0, len(df_f)),
            0.5
        ]

        score = calcular_score(valores)
        estado, color = clasificar(score)

        st.metric("Score", round(score, 2))
        st.markdown(f"Estado: :{color}[{estado}]")
        st.info(recomendacion(score, *valores[:3]))

        fig_radar = grafico_radar(valores, producto_sel)

        if fig_radar is not None:
            fig_radar.update_layout(
                title=f"🛡️ Perfil Analítico del Producto: {producto_sel}"
        )

        if fig_radar is not None:
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.warning("No se pudo generar el radar")