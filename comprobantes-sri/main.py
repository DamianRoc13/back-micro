from app import app
import webbrowser
import threading
import time

def open_browser():
    # Esperar 1 segundo para asegurarse de que el servidor esté listo
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    # Iniciar el servidor Flask en un hilo separado
    threading.Thread(target=app.run, kwargs={"debug": False}).start()
    
    # Abrir el navegador automáticamente
    open_browser()