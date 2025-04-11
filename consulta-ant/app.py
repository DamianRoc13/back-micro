from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import time
import os
import sys
from werkzeug.utils import secure_filename
from consultorPlacas import consultar_placa
from consultorRUC import consultar_ruc
from EXconsultorCedula import consultar_cedula_ex
from INconsultorCedula import consultar_cedula_in
from consultorFinal import unificar_excel

def get_resource_path(relative_path):
    """
    Obtiene la ruta absoluta a un recurso incluido en el ejecutable.
    """
    if hasattr(sys, '_MEIPASS'):
        # Si se ejecuta desde el .exe, usa la carpeta temporal
        base_path = sys._MEIPASS
    else:
        # Si se ejecuta desde el script, usa la ruta normal
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

app = Flask(__name__)
CORS(app)

# Configuración de rutas
DB_PATH = get_resource_path(os.path.join("db", "DB-CONSULTA.xlsx"))
UPLOAD_FOLDER = get_resource_path("db")
ALLOWED_EXTENSIONS = {'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Diccionario de consultas con funciones
CONSULTAS = {
    "PLACA": consultar_placa,
    "RUC": consultar_ruc,
    "CEDULA-EX": consultar_cedula_ex,
    "CEDULA-IN": consultar_cedula_in,
    "UNIFICAR-EXCEL": unificar_excel
}

# Función para verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para servir el archivo index.html
@app.route('/')
def serve_index():
    return send_from_directory(".", "index.html")

# Ruta para servir archivos estáticos (CSS, JS, imágenes, etc.)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(".", path)

# Ruta para realizar consultas
@app.route('/realizar-consulta', methods=['GET'])
def realizar_consulta():
    tipo_consulta = request.args.get('tipoConsulta')

    if tipo_consulta not in CONSULTAS:
        return jsonify({"success": False, "error": "Tipo de consulta no válido"}), 400

    try:
        # Ejecutar la función de consulta directamente
        resultado = CONSULTAS[tipo_consulta]()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": f"Exception: {str(e)}"}), 500

# Ruta para descargar el archivo Excel actual
@app.route('/descargar-excel', methods=['GET'])
def descargar_excel():
    try:
        return send_file(DB_PATH, as_attachment=True)
    except Exception as e:
        return jsonify({"success": False, "error": f"Error al descargar el archivo: {str(e)}"}), 500

# Ruta para importar un nuevo archivo Excel
@app.route('/importar-excel', methods=['POST'])
def importar_excel():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No se proporcionó ningún archivo"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"success": False, "error": "No se seleccionó ningún archivo"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename("DB-CONSULTA.xlsx")  # Forzar el nombre del archivo
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Guardar el archivo
        file.save(file_path)

        return jsonify({"success": True, "message": "Archivo importado correctamente"})
    else:
        return jsonify({"success": False, "error": "Formato de archivo no permitido. Solo se aceptan archivos .xlsx"}), 400

# Función para abrir el navegador automáticamente


if __name__ == '__main__':
    print("Servidor Flask iniciado. Escuchando en el puerto 5001...")
    app.run(host="0.0.0.0", port=5001, debug=False)