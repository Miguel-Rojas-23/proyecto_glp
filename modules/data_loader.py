import pandas as pd
import streamlit as st
from pathlib import Path
import numpy as np

# ── BASE DEL PROYECTO ──────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── RUTA DEL PARQUET ───────────────────────────
DATA_PATH = BASE_DIR / "data" / "dataset_final_glp.parquet"

@st.cache_data(show_spinner=False)
def cargar_datos():

    st.write("📂 Ruta buscada:")
    st.write(DATA_PATH)

    try:

        # ── VALIDACIÓN EXISTENCIA ───────────────
        if not DATA_PATH.exists():

            st.error(f"❌ No existe el archivo:\n{DATA_PATH}")

            return pd.DataFrame()

        # ── LECTURA ────────────────────────────
        df = pd.read_parquet(DATA_PATH)

        st.success(f"✅ Dataset cargado: {len(df)} registros")

        # ── FEATURE ENGINEERING ────────────────
        if "precio_de_venta_(soles)" in df.columns:

            df["precio_log"] = np.log(
                df["precio_de_venta_(soles)"]
                .replace(0, np.nan)
            ).fillna(0)

        return df

    except Exception as e:

        st.error(f"❌ Error leyendo parquet: {e}")

        return pd.DataFrame()