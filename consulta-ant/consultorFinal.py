import os
import pandas as pd
import re
from datetime import datetime
from utils import get_resource_path

def determinar_tipo(identificacion):
    """
    Determina el tipo de identificación (PLACA, CÉDULA, RUC).
    """
    identificacion = str(identificacion).strip()
    if any(c.isalpha() for c in identificacion) and any(c.isdigit() for c in identificacion):
        return "PLACA"
    elif identificacion.isdigit():
        if len(identificacion) == 10:
            return "CEDULA"
        elif len(identificacion) == 13:
            return "RUC"
    return "Desconocido"

def unificar_excel():
    """
    Función principal para unificar archivos Excel de consultas.
    """
    DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")  # Ruta al escritorio del usuario
    carpeta = os.path.join(DESKTOP_PATH, "consultas")  # Carpeta "consultas" en el escritorio

    # Crear la carpeta de consultas si no existe
    os.makedirs(carpeta, exist_ok=True)
    if not os.path.exists(carpeta):
        return {"success": False, "message": f"Error: La carpeta '{carpeta}' no existe."}
    
    archivos = [f for f in os.listdir(carpeta) if f.endswith(".xlsx") or f.endswith(".xls")]
    df_lista = []
    
    for archivo in archivos:
        ruta = os.path.join(carpeta, archivo)
        df_temp = pd.read_excel(ruta)
        primera_columna = df_temp.columns[0]
        df = pd.read_excel(ruta, dtype={primera_columna: str, "# Infracción": str})
        
        if primera_columna.lower() in ["placas", "cedula", "ruc"]:
            df.rename(columns={primera_columna: "Identificación"}, inplace=True)
        
        df["Identificación"] = df["Identificación"].astype(str)
        if "# Infracción" in df.columns:
            df["# Infracción"] = df["# Infracción"].astype(str)
        
        if "Tipo de consulta" not in df.columns:
            df.insert(0, "Tipo de consulta", df["Identificación"].apply(determinar_tipo))
        
        df_lista.append(df)
    
    if df_lista:
        df_final = pd.concat(df_lista, ignore_index=True)
        
        if "# Infracción" in df_final.columns:
            df_final = df_final.drop_duplicates(subset=["# Infracción"], keep="first")
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(carpeta, f"Consulta_Unificada_{fecha_actual}.xlsx")
        df_final = df_final.astype(str)
        df_final.to_excel(output_file, index=False)
        return {"success": True, "message": f"Consulta completada. Archivo guardado en: {output_file}"}
    else:
        return {"success": False, "message": "No se encontraron archivos Excel en la carpeta."}