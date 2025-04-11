from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os
import shutil
import requests
import webbrowser

app = Flask(__name__)


def configurar_navegador():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    usuario = data.get('usuario')
    ci_adicional = data.get('ciAdicional')
    clave = data.get('clave')

    driver = configurar_navegador()
    try:
        driver.get("https://srienlinea.sri.gob.ec/auth/realms/Internet/protocol/openid-connect/auth?client_id=app-sri-claves-angular&redirect_uri=https%3A%2F%2Fsrienlinea.sri.gob.ec%2Fsri-en-linea%2F%2Fcontribuyente%2Fperfil&state=3dda99d1-28bc-420d-851e-d1fc44153666&nonce=25f6023d-d371-42f2-aec6-39a38c44c912&response_mode=fragment&response_type=code&scope=openid")
        
        
        driver.find_element(By.ID, "usuario").send_keys(usuario)
        driver.find_element(By.ID, "ciAdicional").send_keys(ci_adicional)
        driver.find_element(By.ID, "password").send_keys(clave)
        driver.find_element(By.ID, "kc-login").click()

        
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Facturación Electrónica']"))
        ).click()

        
        desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        control_sri_folder = os.path.join(desktop_path, 'control-sri')
        if not os.path.exists(control_sri_folder):
            os.makedirs(control_sri_folder)

        # Ir a la sección de comprobantes recibidos
        WebDriverWait(driver, 15).until(
         EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Comprobantes electrónicos recibidos')]"))
        ).click()

        # Obtener opciones de año, mes, día y tipo de comprobante
        select_ano = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "frmPrincipal:ano"))
        ))
        anos = [option.text for option in select_ano.options]

        select_mes = Select(WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.ID, "frmPrincipal:mes"))
        ))
        meses = [{"value": option.get_attribute("value"), "name": option.text} for option in select_mes.options]

        select_dia = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "frmPrincipal:dia"))
        ))
        dias = [option.text for option in select_dia.options]

        select_tipo_comprobante = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "frmPrincipal:cmbTipoComprobante"))
        )
        select_tipo_comprobante_obj = Select(select_tipo_comprobante)

        # Opciones de tipo de comprobante
        opciones_tipo = {
            "1": "Factura",
            "2": "Liquidación de compra de bienes y prestación de servicios",
            "3": "Notas de Crédito",
            "4": "Notas de Débito",
            "5": "Comprobante de Retención"
        }

        nombres_simplificados = {
            "Factura": "Factura",
            "Liquidación de compra de bienes y prestación de servicios": "Liquidación de compra de bienes y prestación de servicios",
            "Notas de Crédito": "Nota de Crédito",
            "Notas de Débito": "Nota de Débito",
            "Comprobante de Retención": "Comprobante de Retención"
        }

        tipos_comprobante = [{"value": key, "name": value} for key, value in opciones_tipo.items()]

        return jsonify({
            "anos": anos,
            "meses": meses,
            "dias": dias,
            "tipos_comprobante": tipos_comprobante,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

# Ruta para procesar la consulta
@app.route('/consultar', methods=['POST'])
def consultar():
    data = request.json
    usuario = data.get('usuario')
    ci_adicional = data.get('ciAdicional')
    clave = data.get('clave')
    anio = data.get('anio')
    mes = data.get('mes')
    dia = data.get('dia')
    tipo_comprobante = data.get('tipoComprobante')

    driver = configurar_navegador()
    try:
        driver.get("https://srienlinea.sri.gob.ec/auth/realms/Internet/protocol/openid-connect/auth?client_id=app-sri-claves-angular&redirect_uri=https%3A%2F%2Fsrienlinea.sri.gob.ec%2Fsri-en-linea%2F%2Fcontribuyente%2Fperfil&state=3dda99d1-28bc-420d-851e-d1fc44153666&nonce=25f6023d-d371-42f2-aec6-39a38c44c912&response_mode=fragment&response_type=code&scope=openid")

        
        driver.find_element(By.ID, "usuario").send_keys(usuario)
        driver.find_element(By.ID, "ciAdicional").send_keys(ci_adicional)
        driver.find_element(By.ID, "password").send_keys(clave)
        driver.find_element(By.ID, "kc-login").click()

        # Esperar a que cargue la página de facturación
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Facturación Electrónica']"))
        ).click()

        # Ir a la sección de comprobantes recibidos
        WebDriverWait(driver, 15).until(
         EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Comprobantes electrónicos recibidos')]"))
        ).click()

        # Seleccionar año, mes, día y tipo de comprobante
        select_mes = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "frmPrincipal:mes"))
        )
        select_mes_obj = Select(select_mes)
        
        meses_numeros_a_nombres = {
         "1": "Enero",
         "2": "Febrero",
         "3": "Marzo",
         "4": "Abril",
         "5": "Mayo",
         "6": "Junio",
         "7": "Julio",
         "8": "Agosto",
         "9": "Septiembre",
         "10": "Octubre",
         "11": "Noviembre",
         "12": "Diciembre"
        }

        mes_nombre = meses_numeros_a_nombres.get(mes)
        if not mes_nombre:
         return jsonify({"error": f"Mes '{mes}' no válido"}), 400

        select_mes_obj.select_by_visible_text(mes_nombre)

        # Verificar si el mes está en las opciones antes de seleccionarlo
        meses_disponibles = [option.text for option in select_mes_obj.options]
        if mes_nombre not in meses_disponibles:
         return jsonify({"error": f"Mes '{mes_nombre}' no disponible en las opciones"}), 400

        # Seleccionar año, día y tipo de comprobante
        Select(driver.find_element(By.ID, "frmPrincipal:ano")).select_by_visible_text(anio)
        Select(driver.find_element(By.ID, "frmPrincipal:dia")).select_by_visible_text(dia)

        # Seleccionar el tipo de comprobante
        select_tipo_comprobante = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "frmPrincipal:cmbTipoComprobante"))
        )
        select_tipo_comprobante_obj = Select(select_tipo_comprobante)

        opciones_tipo = {
            "1" : "Factura",
            "2" : "Liquidación de compra de bienes y prestación de servicios",
            "3" : "Notas de Crédito",
            "4" : "Notas de Débito",
            "5" :"Comprobante de Retención"
        }

        nombres_simplificados = {
            "Factura": "Factura",
            "Liquidación de compra de bienes y prestación de servicios": "Liquidación de compra de bienes y prestación de servicios",
            "Notas de Crédito": "Nota de Crédito",
            "Notas de Débito": "Nota de Débito",
            "Comprobante de Retención": "Comprobante de Retención"
        }

        if tipo_comprobante in opciones_tipo:
            tipo_seleccionado = opciones_tipo[tipo_comprobante]
            tipo_seleccionado_simplificado = nombres_simplificados.get(tipo_seleccionado, tipo_seleccionado)
            select_tipo_comprobante_obj.select_by_visible_text(tipo_seleccionado)
        else:
            return jsonify({"error": "Tipo de comprobante inválido"}), 400

        # Crear carpeta de descarga
        desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        control_sri_folder = os.path.join(desktop_path, 'control-sri')
        if not os.path.exists(control_sri_folder):
            os.makedirs(control_sri_folder)

        desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        download_folder = os.path.join(desktop_path, f'descarga-{tipo_seleccionado.lower().replace(" ", "-")}')
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        # Hacer clic en el botón de consultar
        driver.find_element(By.ID, "frmPrincipal:btnConsultar").click()

        # Esperar a que se carguen los resultados
        time.sleep(5)
    
        select_registros = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ui-paginator-rpp-options"))
        )
        select_registros_obj = Select(select_registros)
        select_registros_obj.select_by_value("50")

        time.sleep(2)

        data = []
        while True:
            elementos = driver.find_elements(By.XPATH, "//tr[contains(@class, 'ui-widget-content')]")
            for elemento in elementos:
                celdas = elemento.find_elements(By.XPATH, ".//td")
                if len(celdas) >= 8:
                    fila = [celda.text.strip() for celda in celdas[:9]]
                    fila[2] = fila[2].replace(f"{tipo_seleccionado_simplificado} ", "")  
                    ruc_empresa = fila[1].split("\n", 1)  

                    if len(ruc_empresa) > 1:
                        ruc = ruc_empresa[0]  
                        empresa = ruc_empresa[1]  
                    else:
                        ruc = fila[1]  
                        empresa = ""

                    fila[1] = ruc  
                    fila.insert(2, empresa)      
                    data.append(fila)
        
            boton_siguiente = driver.find_element(By.XPATH, "//span[contains(@class, 'ui-paginator-next')]")
        
            if "ui-state-disabled" in boton_siguiente.get_attribute("class"):
                break
            else:
                boton_siguiente.click()
                time.sleep(5)

        df = pd.DataFrame(data, columns=[
            "Nr.", "RUC", "Empresa", "Comprobante", "No. Autorización", "Fecha y Hora", "Fecha de Emisión", "Valor sin Impuestos", "IVA", "Importe Total"
        ])
    
        df = df.astype(str)
    
        # Obtener la fecha actual en formato año, mes, día
        fecha_actual = time.strftime("%Y-%m-%d")
        
        # Guardar el archivo Excel en la carpeta control-sri con la fecha en el nombre
        path_excel = os.path.join(control_sri_folder, f"{fecha_actual}_consulta-{tipo_seleccionado.lower().replace(' ', '-')}.xlsx")
        df.to_excel(path_excel, index=False)
        print(f"Archivo guardado en: {path_excel}")

        df_sri = pd.read_excel(os.path.join(control_sri_folder, f"{fecha_actual}_consulta-{tipo_seleccionado.lower().replace(' ', '-')}.xlsx"), dtype=str)
        df_odoo = pd.read_excel(os.path.join(control_sri_folder, "odoo-origen.xlsx"), dtype=str)

        df_odoo["Número"] = df_odoo["Número"].str.replace(r"^FCP:\s*", "", regex=True)
        facturas_sri = set(zip(df_sri["Comprobante"], df_sri["RUC"]))
        facturas_odoo = set(zip(df_odoo["Número"], df_odoo["Empresa/RUC"]))

        print("\n Combinaciones en 'odoo-origen.xlsx':")
        for factura, ruc in facturas_odoo:
            print(f"→ Número: {factura} | Empresa/RUC: {ruc}")

        def comparar_filas(row):
            factura_sri, ruc_sri = row["Comprobante"], row["RUC"]
            coincide = (factura_sri, ruc_sri) in facturas_odoo

            print(f"\nComparando:")
            print(f"✔ Factura SRI: {factura_sri}  |  RUC SRI: {ruc_sri}")
            print(f"↔ ¿Existe en odoo-origen.xlsx?: {'Sí' if coincide else 'No'}")

            return coincide

        df_filtrado = df_sri[~df_sri.apply(lambda row: (row["Comprobante"], row["RUC"]) in facturas_odoo, axis=1)]

        df_matriz = pd.read_excel(os.path.join(control_sri_folder, "MatrizProveedores.xlsx"), dtype=str)

        ruc_a_nombre_corto = dict(zip(df_matriz["RUC"], df_matriz["Nombre Corto"]))

        df_filtrado["nombre-corto"] = df_filtrado["RUC"].map(ruc_a_nombre_corto).fillna("") 

        path_filtrado = os.path.join(control_sri_folder, f"{fecha_actual}_facturas-down.xlsx")
        df_filtrado.to_excel(path_filtrado, index=False)

        print(f"Archivo final sin duplicados guardado en: {path_filtrado}") 

        df_odoo_filtrado = df_odoo[~df_odoo.apply(lambda row: (row["Número"], row["Empresa/RUC"]) in facturas_sri, axis=1)]

        path_odoo_control = os.path.join(control_sri_folder, f"{fecha_actual}_odoo-control.xlsx")
        df_odoo_filtrado.to_excel(path_odoo_control, index=False)

        print(f"Archivo 'odoo-control.xlsx' guardado en: {path_odoo_control}")

        path_filtrado = os.path.join(control_sri_folder, f"{fecha_actual}_facturas-down.xlsx")
        df = pd.read_excel(path_filtrado, dtype={'RUC': str})
        df_unique = df.drop_duplicates(subset=['RUC'])

        resultados = []

        url_base = "https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/ConsolidadoContribuyente/obtenerPorNumerosRuc?&ruc="

        for ruc in df_unique['RUC']:
            response = requests.get(url_base + ruc)
            if response.status_code == 200:
                data = response.json()
                if data:
                    info_fechas = data[0].pop('informacionFechasContribuyente', {})
                    for key, value in info_fechas.items():
                        data[0][f"infoFechas_{key}"] = str(value) if value is not None else ""

            representantes = data[0].pop('representantesLegales', []) or []
            for i, rep in enumerate(representantes):
                for key, value in rep.items():
                    data[0][f"repLegales_{i+1}_{key}"] = str(value) if value is not None else ""

            data[0] = {key: str(value) if value is not None else "" for key, value in data[0].items()}
            resultados.append(data[0])

        df_resultados = pd.DataFrame(resultados)

        with pd.ExcelWriter(os.path.join(control_sri_folder, f"{fecha_actual}_RUC-consulta.xlsx"), engine='openpyxl') as writer:
         df_resultados.to_excel(writer, index=False)

        print("Proceso completado. Los datos han sido guardados en 'RUC-consulta.xlsx'.")

        # Leer el archivo facturas-down.xlsx desde la carpeta control-sri
        path_filtrado = os.path.join(control_sri_folder, f"{fecha_actual}_facturas-down.xlsx")
        df_facturas = pd.read_excel(path_filtrado, dtype=str)
        numeros_autorizacion = df_facturas["No. Autorización"].tolist()

        def ajustar_zoom(driver, zoom_percent):
            driver.execute_script(f"document.body.style.zoom='{zoom_percent}%'")

        def descargar_archivos(numero_autorizacion):
            try:
                fila = df_facturas[df_facturas["No. Autorización"] == numero_autorizacion].iloc[0]

                fecha_emision = fila["Fecha de Emisión"]  
                mes_año = fecha_emision.split("/")[2] + "-" + fecha_emision.split("/")[1]  
                numero_factura = fila["Comprobante"]  
                nombre_corto_proveedor = fila["nombre-corto"] if pd.notna(fila["nombre-corto"]) else fila["Empresa"]  

                nombre_archivo = f"{mes_año}_{numero_factura}_{nombre_corto_proveedor}.pdf"

                xpath_autorizacion = f"//a[contains(text(), '{numero_autorizacion}')]"
                elemento_autorizacion = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath_autorizacion))
                )
                fila_web = elemento_autorizacion.find_element(By.XPATH, "./ancestor::tr")
                enlace_pdf = fila_web.find_element(By.XPATH, ".//a[contains(@id, 'lnkPdf')]")

                enlace_pdf.click()
                time.sleep(5)

                descarga_completa = False
                tiempo_inicio = time.time()
                while not descarga_completa:
                    if os.path.exists(os.path.join(os.path.expanduser('~'), 'Downloads', f"{tipo_seleccionado_simplificado}.pdf")):
                        descarga_completa = True
                    elif time.time() - tiempo_inicio > 30:
                        raise Exception("Tiempo de espera agotado para la descarga.")
                    time.sleep(1)

                pdf_path = os.path.join(download_folder, nombre_archivo)
                shutil.move(
                    os.path.join(os.path.expanduser('~'), 'Downloads', f"{tipo_seleccionado_simplificado}.pdf"),
                    pdf_path
                )

                print(f"Descargado: {nombre_archivo}")
            except Exception as e:
                print(f"No se pudo descargar los archivos para {numero_autorizacion}: {e}")
                raise

        time.sleep(3)

        def avanzar_pagina():
            try:
                boton_siguiente = driver.find_element(By.XPATH, "//span[contains(@class, 'ui-paginator-prev')]")
                if "ui-state-disabled" in boton_siguiente.get_attribute("class"):
                    print("No hay más páginas.")
                    return False
                else:
                    boton_siguiente.click()
                    return True
            except Exception as e:
                print(f"No se pudo avanzar a la siguiente página: {e}")
                return False

        def buscar_y_descargar():
            ajustar_zoom(driver, 25)
            numeros_autorizacion_invertidos = numeros_autorizacion[::-1]

            indice_actual = 0

            while indice_actual < len(numeros_autorizacion_invertidos):
                numero = numeros_autorizacion_invertidos[indice_actual]
                try:
                    descargar_archivos(numero)
                    indice_actual += 1  
                except Exception as e:
                    print(f"Error al descargar {numero}: {e}")
                    
                    if avanzar_pagina():
                        print("Avanzando a la siguiente página...")
                        time.sleep(10)  
                    else:
                        print("No hay más páginas. Terminando la búsqueda.")
                        break 

        ajustar_zoom(driver, 100)
        buscar_y_descargar()
        time.sleep(15)

        return jsonify({"message": "Consulta procesada correctamente", "download_folder": download_folder})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
    