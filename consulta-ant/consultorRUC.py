import pandas as pd
import requests
import os
import re
from datetime import datetime
from utils import get_resource_path
# Configuración de rutas

DB_PATH = get_resource_path(os.path.join("db", "DB-CONSULTA.xlsx"))
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")  # Ruta al escritorio del usuario
OUTPUT_DIR = os.path.join(DESKTOP_PATH, "consultas")  # Carpeta "consultas" en el escritorio

# Crear la carpeta de consultas si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# URL de la API
API_URL = "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_json_citaciones.jsp"

def consultar_api(ruc):
    """
    Consulta la API para obtener información de multas por RUC.
    """
    ruc = str(ruc).zfill(13)  # Asegurar que el RUC tenga 13 dígitos

    params = {
        "ps_opcion": "P",
        "ps_id_contrato": "",
        "ps_id_persona": "19664470",
        "ps_placa": "",
        "ps_identificacion": ruc,
        "ps_tipo_identificacion": "RUC",
        "_search": "false",
        "nd": "1740414553893",
        "rows": "50",
        "page": "1",
        "sidx": "fecha_emision",
        "sord": "desc"
    }

    try:
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if "rows" in data and isinstance(data["rows"], list) and data["records"] > 0:
            return data["rows"]
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error al consultar {ruc}: {e}")
        return None

def consultar_ruc():
    """
    Función principal para consultar multas por RUC.
    """
    # Leer el archivo Excel con los RUCs
    df = pd.read_excel(DB_PATH, sheet_name="RUC", dtype=str)

    # Lista para almacenar los resultados
    data_list = []

    # Consultar cada RUC
    for ruc in df["RUC"]:
        resultado = consultar_api(ruc)
        if resultado:
            for row in resultado:
                row_data = [ruc] + row["cell"]
                data_list.append(row_data)

    # Si hay resultados, guardarlos en un archivo Excel
    if data_list:
        column_names = ["RUC", "N. Citación", "# Infracción", "Entidad", "# Citación", "Placa", "Doc.",
                       "Fecha de emisión", "Fecha de notificación", "Limite de Pago", "Puntaje", "Col_L", "Col_M",
                       "Col_N", "Sanción", "Multa", "Remisión", "Total a pagar", "Artículo/Literal", "Col_T", "Col_U"]

        df_resultado = pd.DataFrame(data_list, columns=column_names[:len(data_list[0])], dtype=str)

        # Eliminar columnas innecesarias
        df_resultado = df_resultado.loc[:, ~df_resultado.columns.str.match(r'^Col_[A-Z]$')]

        # Guardar el archivo
        fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(OUTPUT_DIR, f"RUC-CON-{fecha_actual}.xlsx")
        df_resultado = df_resultado.astype(str)
        df_resultado.to_excel(output_file, index=False)

        return {"success": True, "message": f"Consulta completada. Archivo guardado en: {output_file}"}
    else:
        return {"success": False, "message": "No se encontraron RUCs con multas."}