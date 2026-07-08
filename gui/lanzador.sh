#!/bin/bash

# Este bucle infinito ejecutará la interfaz, y si detecta que se mandó un app a ejecutar, 
# la abrirá. Al cerrarse la app, el bucle reiniciará la interfaz gráfica.

while true; do
    # Borramos por seguridad archivos previos
    rm -f /tmp/run_app.sh

    echo "Iniciando Interfaz Consola..."
    python3 main.py -platform eglfs

    # Verificamos si la interfaz cerró porque pidió lanzar un juego
    if [ -f /tmp/run_app.sh ]; then
        echo "Lanzando aplicación externa..."
        
        # Ejecutamos el archivo de manera bloqueante (el script espera a que retroarch cierre)
        /tmp/run_app.sh
        
        # Al cerrar el juego/app, limpiamos el archivo para evitar ciclos
        rm -f /tmp/run_app.sh
    else
        # Si el archivo no existe, significa que salimos del app de Python 
        # intencionalmente por error fatal o un cierre total.
        echo "Saliendo del bucle..."
        break
    fi
done