# utils.py
import os
import sys

def get_resource_path(relative_path):
    """
    Obtiene la ruta absoluta a un recurso incluido en el ejecutable.
    """
    if hasattr(sys, '_MEIPASS'):
        # Si se ejecuta desde el .exe, usa la carpeta temporal
        base_path = sys._MEIPASS
    else:
        # Si se ejecuta desde el script, usa la ruta normal
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)