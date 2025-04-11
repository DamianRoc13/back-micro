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

# URL de la API para obtener el id_persona
ID_PERSONA_URL = "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_json_consulta_persona.jsp"

# URL de la API para consultar citaciones
CITACIONES_URL = "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_json_citaciones.jsp"

def obtener_id_persona(cedula):
    """
    Obtiene el ps_id_persona para una cédula dada.
    """
    params = {
        "ps_tipo_identificacion": "CED",
        "ps_identificacion": cedula
    }
    
    try:
        response = requests.get(ID_PERSONA_URL, params=params, timeout=15)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
        data = response.json()
        
        # Extraer el id_persona del JSON
        if "id_persona" in data:
            return data["id_persona"]
        else:
            print(f"No se encontró id_persona para la cédula {cedula}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener id_persona para {cedula}: {e}")
        return None

def consultar_api(cedula, id_persona):
    """
    Consulta la API usando la cédula y el id_persona obtenido.
    """
    cedula = str(cedula).zfill(10)

    params = {
        "ps_opcion": "P",
        "ps_id_contrato": "",
        "ps_id_persona": id_persona,  # Usamos el id_persona obtenido
        "ps_placa": "",
        "ps_identificacion": cedula,
        "ps_tipo_identificacion": "CED",
        "_search": "false",
        "nd": "1740430241436",
        "rows": "50",
        "page": "1",
        "sidx": "fecha_emision",
        "sord": "desc"
    }
    
    try:
        response = requests.get(CITACIONES_URL, params=params, timeout=15)
        response.raise_for_status()  
        data = response.json()
        
        if "rows" in data and isinstance(data["rows"], list) and data["records"] > 0:
            return data["rows"]
        else:
            return None  
    
    except requests.exceptions.RequestException as e:
        print(f"Error al consultar {cedula}: {e}")
        return None

def consultar_cedula_ex():
    """
    Función principal para consultar multas por cédula (extranjera).
    """
    # Leer el archivo Excel con las cédulas
    df = pd.read_excel(DB_PATH, sheet_name="CEDULA-EX", dtype=str)

    # Lista para almacenar los resultados
    data_list = []

    # Consultar cada cédula
    for cedula in df["CEDULA"]:
        cedula_str = str(cedula).zfill(10)  # Asegurar que la cédula tenga 10 dígitos
        
        # Obtener el id_persona dinámicamente
        id_persona = obtener_id_persona(cedula_str)
        
        if id_persona:
            print(f"Consultando cédula {cedula_str} con id_persona {id_persona}")
            resultado = consultar_api(cedula_str, id_persona)
            if resultado:
                for row in resultado:
                    row_data = [cedula_str] + row["cell"]
                    data_list.append(row_data)
        else:
            print(f"No se pudo obtener id_persona para la cédula {cedula_str}")

    # Si hay resultados, guardarlos en un archivo Excel
    if data_list:
        column_names = ["Cedula", "N. Citación", "# Infracción", "Entidad", "# Citación", "Placa", "Doc.",
                         "Fecha de emisión", "Fecha de notificación", "Limite de Pago", "Puntaje", "Col_L", "Col_M",
                         "Col_N", "Sanción", "Multa", "Remisión", "Total a pagar", "Artículo/Literal", "Col_T", "Col_U"]

        df_resultado = pd.DataFrame(data_list, columns=column_names[:len(data_list[0])], dtype=str)

        # Eliminar columnas innecesarias
        df_resultado = df_resultado.loc[:, ~df_resultado.columns.str.match(r'^Col_[A-Z]$')]

        # Guardar el archivo
        fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(OUTPUT_DIR, f"ex-ced-con-{fecha_actual}.xlsx")
        df_resultado = df_resultado.astype(str)
        df_resultado.to_excel(output_file, index=False)

        return {"success": True, "message": f"Consulta completada. Archivo guardado en: {output_file}"}
    else:
        return {"success": False, "message": "No se encontraron cédulas con multas."}

# Ejecutar la función principal
if __name__ == "__main__":
    resultado = consultar_cedula_ex()
    print(resultado["message"])