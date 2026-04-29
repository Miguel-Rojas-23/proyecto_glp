# Dashboard Analítico GLP Perú

Proyecto de Ciencia de Datos y Analítica desarrollado en Python y Streamlit para el monitoreo y análisis estratégico de precios de combustibles GLP en Perú.

---

# Objetivo

Construir una solución analítica capaz de:

* Integrar y transformar datos de combustibles.
* Aplicar validaciones y métricas de calidad.
* Generar análisis exploratorio y KPIs.
* Visualizar tendencias de precios.
* Facilitar la toma de decisiones logísticas.

---

# Arquitectura del Proyecto

```
PROYECTO_GLP/
│
├── app.py
├── README.md
├── .gitignore
│
├── data/
│   └── dataset_final_glp.parquet
│
├── notebooks/
│   ├── costos_Peru_ver06.ipynb
│   └── servidor_api.py
│
├── modules/
│   ├── arquitectura.py
│   ├── business_logic.py
│   ├── data_loader.py
│   ├── filters.py
│   ├── metrics.py
│   ├── utils.py
│   └── visualizations.py
└── requirements.txt
```

---

# Tecnologías Utilizadas

* Python
* Pandas
* NumPy
* Streamlit
* Plotly
* PyArrow
* Scikit-learn
* Requests
* Flask
* Jupyter Notebook

---

# Funcionalidades

## Pipeline ETL

* Ingesta automatizada desde API REST simulada.
* Limpieza y transformación de datos.
* Validación y auditoría de calidad.
* Integración de datasets.
* Feature engineering.
* Exportación optimizada en formato Parquet.

## Dashboard Interactivo

* KPIs dinámicos.
* Filtros interactivos.
* Scatter plots.
* Tendencias temporales.
* Boxplots.
* Radar charts.
* Matriz de correlación.
* Explorador analítico de productos.

## Calidad de Datos

Se implementan métricas de:

* Completitud
* Unicidad
* Validez
* Consistencia
* Actualidad

---

# Instalación

## 1. Clonar repositorio

```
git clone <URL_DEL_REPOSITORIO>
cd PROYECTO_GLP
```

## 2. Crear entorno virtual

### Windows

```
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalar dependencias

```
pip install -r requirements.txt
```

---

# Ejecución del Proyecto

## 1. Ejecutar API REST simulada

Ubicarse dentro de la carpeta notebooks:

```
cd notebooks
python servidor_api.py
```

## 2. Ejecutar Streamlit

Desde la raíz del proyecto:

```
streamlit run app.py
```

---

# Dataset

El dataset final procesado se almacena en:

```
data/dataset_final_glp.parquet
```

Formato optimizado:

* Apache Parquet
* Compresión Snappy
* Optimización de memoria mediante downcasting

---

# KPIs Principales

* Cantidad de registros
* Precio promedio
* Precio máximo
* Precio mínimo
* Índice de demanda
* Variabilidad de precios
* Score estratégico

---

# Arquitectura Analítica

El proyecto implementa una arquitectura modular compuesta por:

1. API REST simulada con Flask
2. Pipeline ETL automatizado
3. Dataset analítico optimizado
4. Dashboard interactivo en Streamlit
5. Sistema de scoring estratégico

La solución está diseñada para:

* Separación de responsabilidades
* Escalabilidad
* Reutilización de componentes
* Compatibilidad local y cloud
* Análisis orientado a negocio

---

# Mejoras Futuras

* Integración con PostgreSQL.
* Integración con BigQuery.
* Migración de Flask a FastAPI.
* Machine Learning predictivo.
* Detección automática de anomalías.
* Alertas automáticas.
* Mapas geográficos interactivos.
* Automatización mediante servicios cloud.

---

# Autor

Proyecto académico de Ciencia de Datos enfocado en:

* Ingeniería de Datos
* Analítica de Negocio
* Visualización Interactiva
* Inteligencia de Negocio
* Optimización Logística

---

# Licencia

Proyecto desarrollado con fines académicos y educativos.
