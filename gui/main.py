import sys
import os
import subprocess
import threading
import time
import argparse
import platform
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

    def _is_raspberry_pi() -> bool:
        """Try a few heuristics to detect running on a Raspberry Pi."""
        try:
            model_path = Path("/proc/device-tree/model")
            if model_path.exists():
                txt = model_path.read_text(errors="ignore").lower()
                return "raspberry" in txt
        except Exception:
            pass

        # Fallback to CPU architecture check on linux
        try:
            if sys.platform.startswith("linux") and platform.machine().startswith(("arm", "aarch")):
                return True
        except Exception:
            pass

        return False

    # Parse a couple of debug flags for cursor control but leave other args for Qt
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--show-cursor", dest="show_cursor", action="store_true", help="Force showing the mouse cursor")
    group.add_argument("--hide-cursor", dest="hide_cursor", action="store_true", help="Force hiding the mouse cursor")

    args, remaining = parser.parse_known_args()

    # Build argv for Qt from the unknown args so Qt still receives its platform args (e.g. -platform eglfs)
    qt_argv = [sys.argv[0]] + remaining

    app = QGuiApplication(qt_argv)

    # Decide whether to hide the cursor. Priority: explicit flags > eglfs/platform > heuristics
    env_platform = os.environ.get("QT_QPA_PLATFORM", "").lower()
    using_eglfs = any("eglfs" in a.lower() for a in qt_argv[1:]) or env_platform == "eglfs"

    if args.show_cursor:
        hide_cursor = False
    elif args.hide_cursor:
        hide_cursor = True
    else:
        # Auto-detect: hide when running on eglfs or on Raspberry Pi without DISPLAY
        hide_cursor = using_eglfs or (_is_raspberry_pi() and os.environ.get("DISPLAY") is None)

    if hide_cursor:
        app.setOverrideCursor(Qt.CursorShape.BlankCursor)

    engine = QQmlApplicationEngine()

    manager = ConsoleManager(engine)
    net_manager = NetworkBackend()
    blue_manager = BluetoothBackend()

    # Inject Python class into the QML world
    # QML will recognize the word "backend" as if it were a native component
    context = engine.rootContext()
    if not context:
        print("Error: No se pudo obtener el contexto raíz de QML.")
        sys.exit(-1)

    context.setContextProperty("backend", manager)
    context.setContextProperty("networkBackend", net_manager)
    context.setContextProperty("bluetoothBackend", blue_manager)

    # Load QML file using a path relative to this script so the app runs from any working directory.
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(str(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())