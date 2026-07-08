import os
import signal
import time
from gpiozero import Button

# Archivo donde el supervisor guarda el PID del juego/app actual
PID_FILE = "/tmp/current_app.pid"

# ==========================================
# CONFIGURACIÓN DE PINES
# ==========================================
# ¡Ajusta este pin al pin real donde conectaste el botón Home en la Raspberry Pi!
PIN_BOTON_HOME = 2

def close_app():
    print("Sistema: ¡Botón HOME presionado!")
    
    # 1. Comprobamos si hay un juego corriendo
    if not os.path.exists(PID_FILE):
        print("Sistema: No hay ninguna app abierta. Ignorando pulsación.")
        return
        
    try:
        # 2. Leemos el PID
        with open(PID_FILE, "r") as f:
            pid_str = f.read().strip()
            
        if not pid_str.isdigit():
            return
            
        pid = int(pid_str)
        
        os.killpg(pid, signal.SIGKILL)
        
        
    except FileNotFoundError:
        print("Sistema: Archivo PID desapareció antes de leerlo.")
    except ProcessLookupError:
        print(f"Sistema: El proceso {pid} ya había muerto.")
    except Exception as e:
        print(f"Sistema: Error al intentar matar el proceso: {e}")

btn_home = Button(PIN_BOTON_HOME, pull_up=True, bounce_time=0.05)
btn_home.when_pressed = close_app

try:
    signal.pause()
except KeyboardInterrupt:
    print("\nSystem buttons closed")
