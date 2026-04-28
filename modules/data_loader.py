import pandas as pd
import streamlit as st
from pathlib import Path
import numpy as np
import requests

# ── BASE DEL PROYECTO ──────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── PARQUET ────────────────────────────────────
DATA_PATH = BASE_DIR / "data" / "dataset_final_glp.parquet"

# ── API LOCAL ──────────────────────────────────
API_URL = "http://127.0.0.1:5000/api/v1/precios-glp"


@st.cache_data(show_spinner=False)
def cargar_datos():
    """
    Carga de datos híbrida:
    
    1. Intenta API Flask local
    2. Si falla → usa parquet
    
    📌 NEGOCIO:
    Permite:
    - simulación ETL/API local
    - deploy web en Streamlit Cloud
    
    📌 TÉCNICO:
    Arquitectura híbrida resiliente
    """

    # =================================================
    # 1. INTENTO API LOCAL
    # =================================================
    try:

        st.info("📡 Intentando conexión con API local...")

        response = requests.get(API_URL, timeout=5)

        if response.status_code == 200:

            data = response.json()

            df = pd.DataFrame(data)

            st.success(f"✅ Datos cargados desde API LOCAL ({len(df)} registros)")

            # ── FEATURE ENGINEERING ─────────────────
            if "precio_de_venta_(soles)" in df.columns:

                df["precio_log"] = np.log(
                    pd.to_numeric(
                        df["precio_de_venta_(soles)"],
                        errors="coerce"
                    ).replace(0, np.nan)
                ).fillna(0)

            return df

    except Exception:
        st.warning("⚠️ API local no disponible. Usando parquet...")

    # =================================================
    # 2. FALLBACK → PARQUET
    # =================================================
    try:

        st.info(f"📂 Buscando parquet en:\n{DATA_PATH}")

        if not DATA_PATH.exists():

            st.error(f"❌ No existe:\n{DATA_PATH}")

            return pd.DataFrame()

        df = pd.read_parquet(DATA_PATH)

        st.success(f"✅ Dataset parquet cargado ({len(df)} registros)")

        # ── FEATURE ENGINEERING ─────────────────
        if "precio_de_venta_(soles)" in df.columns:

            df["precio_log"] = np.log(
                pd.to_numeric(
                    df["precio_de_venta_(soles)"],
                    errors="coerce"
                ).replace(0, np.nan)
            ).fillna(0)

        return df

    except Exception as e:

        st.error(f"❌ Error cargando parquet:\n{e}")

        return pd.DataFrame()