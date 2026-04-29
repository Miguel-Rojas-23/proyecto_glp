import pandas as pd
import streamlit as st
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "dataset_final_glp.parquet"


@st.cache_data(show_spinner=False)
def cargar_datos():

    if not DATA_PATH.exists():
        return pd.DataFrame()

    df = pd.read_parquet(DATA_PATH)

    # normalización columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # conversión segura
    if "precio_de_venta_(soles)" in df.columns:
        df["precio_de_venta_(soles)"] = pd.to_numeric(
            df["precio_de_venta_(soles)"],
            errors="coerce"
        )

        df["precio_log"] = np.log1p(df["precio_de_venta_(soles)"])

    return df