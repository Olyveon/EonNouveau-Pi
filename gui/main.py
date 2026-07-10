import sys
import os
import subprocess
import threading
import time
from pathlib import Path
from PyQt6.QtGui import QGuiApplication, QCursor, QFontDatabase
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QObject, pyqtSlot, Qt

from network_manager import NetworkBackend
from bluetooth_manager import BluetoothBackend

class ConsoleManager(QObject):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    @pyqtSlot(str)
    def launch_app(self, command):
        with open("/tmp/next_app.txt", "w") as f:
            f.write(command)
        QGuiApplication.quit()


# --- GUI BOOT ---
if __name__ == "__main__":
    # Activar el teclado virtual ANTES de instanciar QGuiApplication
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    
    app = QGuiApplication(sys.argv)
    
    app.setOverrideCursor(Qt.CursorShape.BlankCursor)
    engine = QQmlApplicationEngine()

    manager = ConsoleManager(engine)
    net_manager = NetworkBackend()
    blue_manager = BluetoothBackend()

    # Inject Python class into the QML world
    # QML will recognize the word "backend" as if it were a native component
    context = engine.rootContext()
    context.setContextProperty("backend", manager)
    context.setContextProperty("networkBackend", net_manager)
    context.setContextProperty("bluetoothBackend", blue_manager)

    # Load QML file
    engine.load("main.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())