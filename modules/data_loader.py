import pandas as pd
import streamlit as st
from pathlib import Path
import numpy as np

# ── RUTA DEL DATASET ─────────────────────────────
# Obtiene la raíz del proyecto automáticamente
BASE_DIR = Path(__file__).resolve().parent.parent

# Ruta al parquet dentro de /data
DATA_PATH = BASE_DIR / "data" / "dataset_final_glp.parquet"

@st.cache_data(show_spinner=False)
def cargar_datos():
    """
    Carga el dataset desde parquet.

    📌 NEGOCIO:
    Se usa parquet porque permite:
    - Mejor rendimiento
    - Menor tamaño
    - Compatible con pipelines ETL

    📌 TÉCNICO:
    - Si no existe el archivo → devuelve DataFrame vacío
    - Se implementa CACHE para mejorar rendimiento

    🆕 MEJORA:
    - Se agrega feature engineering básico
    """

    try:

        if DATA_PATH.exists():

            # ── LECTURA PARQUET ─────────────────────
            df = pd.read_parquet(DATA_PATH)

            # ── FEATURE ENGINEERING ─────────────────
            # 🆕 Transformación para análisis más robusto
            df["precio_log"] = np.log(
                df["precio_de_venta_(soles)"]
                .replace(0, np.nan)
            ).fillna(0)

            print(f"✅ Dataset cargado correctamente: {len(df)} registros")

            return df

        else:
            print(f"❌ Archivo no encontrado: {DATA_PATH}")
            return pd.DataFrame()

    except Exception as e:

        print(f"❌ Error cargando parquet: {e}")

        return pd.DataFrame()