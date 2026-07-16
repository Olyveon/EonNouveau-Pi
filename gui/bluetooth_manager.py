import subprocess
import threading
import json
import re
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

_QT_BLUETOOTH_AVAILABLE = True
_QT_BLUETOOTH_ERROR = None
try:
    from PyQt6.QtBluetooth import (
        QBluetoothDeviceDiscoveryAgent,
        QBluetoothDeviceInfo,
        QBluetoothLocalDevice,
        QBluetoothAddress,
        QBluetoothSocket,
        QBluetoothServiceInfo,
        QBluetoothUuid,
    )
except Exception as e:
    _QT_BLUETOOTH_AVAILABLE = False
    _QT_BLUETOOTH_ERROR = str(e)


def _icon_for(info: "QBluetoothDeviceInfo") -> str:
    major = info.majorDeviceClass()
    Major = QBluetoothDeviceInfo.MajorDeviceClass
    mapping = {
        Major.ComputerDevice: "computer",
        Major.PhoneDevice: "phone",
        Major.AudioVideoDevice: "headset",
        Major.PeripheralDevice: "keyboard",
        Major.ImagingDevice: "printer",
        Major.WearableDevice: "watch",
        Major.ToyDevice: "toy",
        Major.HealthDevice: "health",
        Major.NetworkDevice: "network",
    }
    return mapping.get(major, "bluetooth")


if _QT_BLUETOOTH_AVAILABLE:
    class BluetoothBackend(QObject):
        # Señales para enviar datos a QML de forma asíncrona
        device_found = pyqtSignal(str)
        scan_error = pyqtSignal(str)
        pairing_finished = pyqtSignal(str, str)   # mac, status ("paired"/"unpaired"/"error")
        connection_changed = pyqtSignal(str, str) # mac, status ("connected"/"disconnected"/"error")
        devices_paired = pyqtSignal(str) # Envia un JSON con la lista de dispositivos emparejados, incluyendo los actualmente connectados 
        devices_ready = pyqtSignal(str) # Envia un JSON con la lista de dispositivos encontrados durante el scaneo

        def __init__(self, parent=None):
            super().__init__(parent)
            self._devices = {}

            self._agent = QBluetoothDeviceDiscoveryAgent(self)
            self._agent.deviceDiscovered.connect(self._on_device_discovered)
            self._agent.finished.connect(self._on_finished)
            self._agent.errorOccurred.connect(self._on_error)
            self._agent.setLowEnergyDiscoveryTimeout(8000)
            self._socket = None
            
            self._local = QBluetoothLocalDevice()
            self._local.pairingFinished.connect(self._on_pairing_finished)
            self._local.errorOccurred.connect(self._on_pairing_error)

        @pyqtSlot()
        def start_scan(self):
            self._devices.clear()
            if self._agent.isActive():
                self._agent.stop()
            self._agent.start(
                QBluetoothDeviceDiscoveryAgent.DiscoveryMethod.ClassicMethod
                | QBluetoothDeviceDiscoveryAgent.DiscoveryMethod.LowEnergyMethod
            )

        def _pairing_status(self, mac: str) -> str:
            from PyQt6.QtBluetooth import QBluetoothAddress
            pairing = self._local.pairingStatus(QBluetoothAddress(mac))
            Pairing = QBluetoothLocalDevice.Pairing
            return pairing != Pairing.Unpaired  # True if paired or authorized-paired

        def _is_connected(self, mac: str) -> bool:
            # Qt doesn't expose live connection state on Linux; fall back to bluetoothctl.
            try:
                out = subprocess.check_output(
                    ["bluetoothctl", "info", mac], text=True,
                    stderr=subprocess.DEVNULL, timeout=2
                )
                return "Connected: yes" in out
            except Exception:
                return False

        def _on_device_discovered(self, info: QBluetoothDeviceInfo):
            mac = info.address().toString()
            paired = self._pairing_status(mac)
            connected = self._is_connected(mac) if paired else False

            if connected:
                status = "connected"
            elif paired:
                status = "paired"
            else:
                status = "scanned"

            entry = {
                "mac": mac,
                "name": info.name() or "Desconocido",
                "rssi": info.rssi(),
                "status": status,
                "icon": _icon_for(info),
            }
            self._devices[mac] = entry
            self.device_found.emit(json.dumps(entry))

        def _on_finished(self):
            self.devices_ready.emit(json.dumps(list(self._devices.values())))

        def _on_error(self, error):
            self.scan_error.emit(str(error))
            
        @pyqtSlot(str)
        def connect_device(self, mac : str):
            threading.Thread(target=self._connect,args=(mac,), daemon=True).start()

        def _connect(self, mac):
            try:
                result = subprocess.run(
                    ["bluetoothctl", "connect", mac],
                    capture_output=True, text=True, timeout=10
                )
                if "Connection successful" in result.stdout:
                    self.connection_changed.emit(mac, "connected")
                else:
                    self.connection_changed.emit(mac, "error")
            except Exception:
                self.connection_changed.emit(mac, "error")

        @pyqtSlot(str)
        def pair_device(self, mac: str):
            address = QBluetoothAddress(mac)
            self._local.requestPairing(address, QBluetoothLocalDevice.Pairing.Paired)

        def _on_pairing_finished(self, address: QBluetoothAddress, pairing):
            mac = address.toString()
            if pairing != QBluetoothLocalDevice.Pairing.Unpaired:
                self.trust_device(mac)
                self.connect_device(mac)
                self.pairing_finished.emit(mac, "paired")
            else:
                self.pairing_finished.emit(mac, "unpaired")

        def _on_pairing_error(self, address: QBluetoothAddress, error):
            self.pairing_finished.emit(address.toString(), "error")

        @pyqtSlot(str)
        def disconnect_device(self, mac: str):
            try:
                subprocess.run(["bluetoothctl", "disconnect", mac], timeout=10)
                self.connection_changed.emit(mac, "disconnected")
            except Exception:
                pass
        
        @pyqtSlot(str)
        def trust_device(self, mac: str):
            try:
                subprocess.run(["bluetoothctl", "trust", mac], timeout=5)
            except Exception:
                pass

        @pyqtSlot()
        def request_paired_devices(self):
            """Lista los dispositivos emparejados"""

        @pyqtSlot(str)
        def forget_device(self, mac):
            """Elimina el perfil de conexión de Bluetoothctl."""
            try:
                subprocess.run(["bluetoothctl", "remove", mac], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.start_scan() # Refrescar lista para actualizar el estado
            except:
                pass
else:
    class BluetoothBackend(QObject):
        device_found = pyqtSignal(str)
        scan_error = pyqtSignal(str)
        pairing_finished = pyqtSignal(str, str)
        connection_changed = pyqtSignal(str, str)
        devices_paired = pyqtSignal(str)
        devices_ready = pyqtSignal(str)

        def __init__(self, parent=None):
            super().__init__(parent)

        @pyqtSlot()
        def start_scan(self):
            self.scan_error.emit(f"Bluetooth unavailable: {_QT_BLUETOOTH_ERROR}")
            self.devices_ready.emit("[]")

        @pyqtSlot(str)
        def connect_device(self, mac: str):
            self.connection_changed.emit(mac, "error")

        @pyqtSlot(str)
        def pair_device(self, mac: str):
            self.pairing_finished.emit(mac, "error")

        @pyqtSlot(str)
        def disconnect_device(self, mac: str):
            self.connection_changed.emit(mac, "error")

        @pyqtSlot(str)
        def forget_device(self, mac: str):
            pass

        @pyqtSlot()
        def request_paired_devices(self):
            self.devices_paired.emit("[]")

        @pyqtSlot(str)
        def trust_device(self, mac: str):
            pass