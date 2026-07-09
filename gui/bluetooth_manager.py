import subprocess
import threading
import json
import re
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

class BluetoothBackend(QObject):
    # Señales para enviar datos a QML de forma asíncrona
    networks_ready = pyqtSignal(str) # Envía un JSON con la lista de redes
    connection_status = pyqtSignal(str, str, str) # Icono, Nombre de red (SSID), Dirección IP
    connect_result = pyqtSignal(bool, str) # Éxito o Fracaso, y el mensaje de error

    def __init__(self):
        super().__init__()

    @pyqtSlot()
    def request_status(self):
        """Solicita el estado actual. Corre en segundo plano para no congelar la UI."""
        threading.Thread(target=self._get_status, daemon=True).start()

    def _get_status(self):
        try:
            # nmcli -t -f NAME,TYPE,DEVICE connection show --active
            out = subprocess.check_output(["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "connection", "show", "--active"], text=True)
            lines = out.strip().split('\n')
            
            ssid = "Sin conexión"
            ip = "---.---.---.---"
            icon = "🚫"
            
            for line in lines:
                if not line: continue
                parts = line.split(':')
                if len(parts) >= 3:
                    name, net_type, dev = parts[0], parts[1], parts[2]
                    
                    # Verificamos si es inalámbrica o de red por cable
                    if net_type in ['802-11-wireless', '802-3-ethernet']:
                        ssid = name
                        icon = "🌐" if net_type == '802-3-ethernet' else "📶"
                        
                        # Sacamos la IP de esa interfaz específica
                        try:
                            ip_out = subprocess.check_output(["nmcli", "-t", "-f", "IP4.ADDRESS", "device", "show", dev], text=True)
                            ip_lines = ip_out.strip().split('\n')
                            if ip_lines and ip_lines[0]:
                                ip = ip_lines[0].replace('IP4.ADDRESS[1]:', '').split('/')[0]
                        except:
                            ip = "Obteniendo..."
                        break
            #ssid = "Prueba"
            self.connection_status.emit(icon, ssid, ip)
        except Exception as e:
            self.connection_status.emit("🚫", "Error de red", str(e))

    @pyqtSlot()
    def scan_networks(self):
        """Escanea redes Wi-Fi en segundo plano."""
        threading.Thread(target=self._scan, daemon=True).start()

    def _scan(self):
        try:
            # Forzamos al sistema a escanear el aire primero. 
            subprocess.run(["nmcli", "dev", "wifi", "rescan"], timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass 

        networks = []
        try:
            # Obtenemos las conexiones guardadas para saber cuáles están "known"
            known_out = subprocess.check_output(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"], text=True, stderr=subprocess.DEVNULL)
            known_ssids = [line.split(':')[0] for line in known_out.strip().split('\n') if ':802-11-wireless' in line]

            # Listamos redes visibles
            out = subprocess.check_output(["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi", "list"], text=True, stderr=subprocess.DEVNULL)
            seen = set()
            for line in out.strip().split('\n'):
                if not line: continue
                
                parts = re.split(r'(?<!\\):', line)
                if len(parts) >= 3:
                    ssid = parts[0].replace('\\:', ':').strip()
                    if not ssid or ssid in seen or ssid == "--": 
                        continue
                    seen.add(ssid)
                    
                    sig_val = int(parts[1]) if parts[1].isdigit() else 0
                    if sig_val > 75: signal_text = "Fuerte"
                    elif sig_val > 45: signal_text = "Media"
                    else: signal_text = "Débil"
                    
                    sec = parts[2]
                    secured = ("WPA" in sec) or ("WEP" in sec) or ("802.1X" in sec)
                    
                    networks.append({
                        "ssid": ssid,
                        "strength": signal_text,
                        "secured": secured,
                        "known": ssid in known_ssids
                    })
            
            self.networks_ready.emit(json.dumps(networks))
        except Exception as e:
            self.networks_ready.emit(json.dumps([]))

    @pyqtSlot(str, str)
    def connect_network(self, ssid, password):
        """Intenta conectarse. Si es conocida y no hay password, usa el perfil guardado."""
        threading.Thread(target=self._connect, args=(ssid, password), daemon=True).start()

    def _connect(self, ssid, password):
        try:
            # Si pasamos password, conectamos con ella (actualiza la guardada si existe)
            if password:
                res = subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password], capture_output=True, text=True)
            else:
                # Si no hay password, nmcli intentará usar la conexión guardada automáticamente
                res = subprocess.run(["nmcli", "dev", "wifi", "connect", ssid], capture_output=True, text=True)
                
            if res.returncode == 0:
                self.connect_result.emit(True, f"Conexión exitosa a {ssid}")
                self._get_status()
            else:
                # Si falla sin password y es conocida, quizá la clave cambió
                self.connect_result.emit(False, "Error al conectar. Si la red es guardada, intenta 'Olvidar' y reconectar.")
        except Exception as e:
            self.connect_result.emit(False, str(e))

    @pyqtSlot(str)
    def forget_network(self, ssid):
        """Elimina el perfil de conexión de NetworkManager."""
        threading.Thread(target=self._forget, args=(ssid,), daemon=True).start()

    def _forget(self, ssid):
        try:
            subprocess.run(["nmcli", "connection", "delete", ssid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._get_status()
            self._scan() # Refrescar lista para actualizar el estado "known"
        except:
            pass

    @pyqtSlot()
    def disconnect_network(self):
        """Desconecta la red Wi-Fi actual por completo."""
        threading.Thread(target=self._disconnect, daemon=True).start()
        
    def _disconnect(self):
        # Tomamos wlan0 por defecto para raspberry pi
        subprocess.run(["nmcli", "dev", "disconnect", "wlan0"])
        self._get_status()
