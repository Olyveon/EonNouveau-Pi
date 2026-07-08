import subprocess
import time
import os

NEXT_APP_FILE = "/tmp/next_app.txt"
PID_FILE = "/tmp/current_app.pid"

def clean_temp_files():
    if os.path.exists(NEXT_APP_FILE):
        os.remove(NEXT_APP_FILE)
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def run_gui():
    gui_process = subprocess.Popen(["python3", "main.py", "-platform", "eglfs"], cwd="../gui")
    gui_process.wait()

def run_app():
    if not os.path.exists(NEXT_APP_FILE):
        return False
        
    with open(NEXT_APP_FILE, "r") as f:
        command_str = f.read().strip()
        
    if not command_str:
        return False
        
    print(f"Supervisor: Lanzando aplicación -> {command_str}")
    
    # Lanzamos el comando. Usamos shell=True por si viene con argumentos desde el QML
    # pero usamos "exec" para no tener el wrapper de bash.
    # start_new_session=True convierte a este proceso en líder de grupo,
    # permitiendo que el botón Home mate a todos sus hijos en cascada (ej: emuladores secundarios).
    app_process = subprocess.Popen(f"exec {command_str}", shell=True, start_new_session=True)
    
    # Guardamos su PID para que el botón Home sepa a quién matar
    with open(PID_FILE, "w") as f:
        f.write(str(app_process.pid))
        
    # Esperamos a que la aplicación (RetroArch, etc.) termine
    app_process.wait()
    
    print("Supervisor: La aplicación ha terminado.")
    
    clean_temp_files()
    return True

def main():
    print("Running Supervisor...")
    clean_temp_files()
    
    while True:
        run_gui()
        if os.path.exists(NEXT_APP_FILE):
            run_app()
        else:
            break

if __name__ == "__main__":
    main()