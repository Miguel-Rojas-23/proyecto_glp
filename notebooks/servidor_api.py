import subprocess
import sys

# --- BLOQUE DE CONTROL DE DEPENDENCIAS ---
def verificar_librerias():
    librerias = {
        "flask": "Flask",
        "pandas": "pandas",
        "flask_cors": "flask-cors",
        "openpyxl": "openpyxl" # Requerida para leer archivos Excel
    }
    
    for import_name, pkg_name in librerias.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"⚠️ Librería '{pkg_name}' no encontrada. Instalación en curso...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
        else:
            print(f"✅ Librería '{pkg_name}' ya está instalada.")

verificar_librerias()

# Una vez verificadas, procedemos con las importaciones
from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS

# Inicialización de la aplicación Flask
app = Flask(__name__)
# CORS permite que el Notebook (cliente) se comunique con la API (servidor) sin bloqueos de seguridad
CORS(app)

# --- FASE DE PRE-CARGA (ESTIMULACIÓN DE API) ---
# Esta sección se ejecuta UNA SOLA VEZ al abrir la terminal. 
# Mantiene los datos en la memoria RAM para que la respuesta de la API sea instantánea.

print("\n" + "="*50)
print("🚀 INICIANDO SIMULACIÓN DE API DE DATOS (WEB SCRAPPING)")
print("⚠️ IMPORTANTE: No cierre esta terminal mientras use el Notebook.")
print("="*50 + "\n")

print("⏳ Cargando base de datos consolidada desde archivos Excel...")

try:
    # Lectura de archivos locales de Osinergmin 
    # Fuente: https://www.osinergmin.gob.pe/empresas/hidrocarburos/scop/documentos-scop
    df25 = pd.read_excel("GLP-Registro-precios-PIC-PE-V-2025.xlsx")
    df26 = pd.read_excel("GLP-Registro-precios-PIC-PE-V-2026.xlsx")

    # Concatenación de ambos datasets para formar una base histórica única
    # .fillna("") es crucial para evitar errores de JSON con valores Nulos (NaN)
    df_full = pd.concat([df25, df26], ignore_index=True).fillna("")
    
    print(f"✅ Data lista en RAM. Total de registros cargados: {len(df_full)}")
except Exception as e:
    print(f"❌ Error al cargar los archivos: {e}")

# --- ENDPOINT DE SALUD (HEALTH CHECK) ---
# Este es el punto que el Notebook consultará repetidamente.
# Al ser una respuesta pequeña, no consume recursos y evita el "bucle infinito" de espera.
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ready"}), 200

# --- ENDPOINT DE DATOS (INGESTA) ---
# Este endpoint solo se llama una vez desde la "Fase de Ingesta" del Notebook.
@app.route('/api/v1/precios-glp', methods=['GET'])
def get_data():
    # Convertimos el DataFrame una lista de diccionarios (formato JSON)
    # No volvemos a leer los Excel aquí, lo cual ahorra varios minutos de ejecución.
    return jsonify(df_full.to_dict(orient='records'))

# Punto de entrada para ejecutar el servidor local en el puerto 5000
if __name__ == '__main__':
    app.run(port=5000)