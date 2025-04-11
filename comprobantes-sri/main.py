from app import app
import webbrowser
import threading
import time



if __name__ == "__main__":
    # Iniciar el servidor Flask en un hilo separado
    threading.Thread(target=app.run, kwargs={"debug": False}).start()