import plotly.express as px
import plotly.graph_objects as go


def grafico_precio_producto(df):
    """
    📌 NEGOCIO:
    Permite comparar precios promedio por producto
    → ayuda a detectar cuál es más rentable

    🆕 MEJORA:
    - Mejora visual (orden y etiquetas)
    """

    resumen = df.groupby("producto")["precio_de_venta_(soles)"].mean().reset_index()
    resumen = resumen.sort_values("precio_de_venta_(soles)", ascending=False)

    fig = px.bar(
        resumen,
        x="producto",
        y="precio_de_venta_(soles)",
        text_auto=".2f",
        color="precio_de_venta_(soles)"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Producto", yaxis_title="Precio Promedio")

    return fig


def grafico_radar(valores, producto):
    
    """
    📌 NEGOCIO:
    Visualiza perfil estratégico del producto

    🆕 MEJORA:
    - Mejora de legibilidad en radar
    """

    if valores is None or len(valores) == 0:
        return None

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=valores + [valores[0]],
        theta=[
            "Precio",
            "Demanda",
            "Estabilidad",
            "Presencia",
            "Ranking",
            "Precio"
        ],
        fill='toself',
        name=producto
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        height=500
    )

    return fig