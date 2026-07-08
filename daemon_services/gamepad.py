import time
import spidev
import threading
import signal
import sys
from evdev import UInput, ecodes, AbsInfo
from gpiozero import Button

# ── Configuración SPI (MCP3008) ────────────────────────────
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def leer_canal(canal):
    datos = spi.xfer2([1, (8 + canal) << 4, 0])
    return ((datos[1] & 3) << 8) + datos[2]

# ── Calibración de Joysticks Magnéticos ────────────────────
X1_MIN, X1_MAX = 206, 804
Y1_MIN, Y1_MAX = 189, 780
X2_MIN, X2_MAX = 4, 1023
Y2_MIN, Y2_MAX = 4, 1023

def mapear(valor, min_in, max_in, min_out=-32768, max_out=32767):
    # Evitar divisiones por cero o valores fuera de rango
    valor = max(min_in, min(valor, max_in))
    if max_in == min_in: return 0
    return int((valor - min_in) / (max_in - min_in) * (max_out - min_out) + min_out)

# ── Gamepad Virtual (Capacidades) ──────────────────────────
capabilities = {
    ecodes.EV_KEY: [
        ecodes.BTN_A, ecodes.BTN_B, ecodes.BTN_X, ecodes.BTN_Y,
        ecodes.BTN_TL, ecodes.BTN_TR,   # L1 y R1
        ecodes.BTN_TL2, ecodes.BTN_TR2, # L2 y R2
        ecodes.BTN_START, ecodes.BTN_SELECT,
        ecodes.BTN_DPAD_UP, ecodes.BTN_DPAD_DOWN, 
        ecodes.BTN_DPAD_LEFT, ecodes.BTN_DPAD_RIGHT
    ],
    ecodes.EV_ABS: [
        (ecodes.ABS_X,  AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (ecodes.ABS_Y,  AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (ecodes.ABS_RX, AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (ecodes.ABS_RY, AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
    ]
}

gamepad = UInput(capabilities, name="Consola_Custom_Gamepad", vendor=0x045E, product=0x028E) # IDs de Xbox 360 para máxima compatibilidad

# ── Botones GPIO (Switches mecánicos con Pull-Up) ──────────
# Mapeo extraído directamente de tu Excel (excluyendo L3 y R3)
botones = {
    Button(14, pull_up=True, bounce_time=0.01): ecodes.BTN_A,
    Button(15, pull_up=True, bounce_time=0.01): ecodes.BTN_B,
    Button(23, pull_up=True, bounce_time=0.01): ecodes.BTN_X,
    Button(18, pull_up=True, bounce_time=0.01): ecodes.BTN_Y,
    
    Button(17, pull_up=True, bounce_time=0.01): ecodes.BTN_START,
    Button(27, pull_up=True, bounce_time=0.01): ecodes.BTN_SELECT,
    
    Button(22, pull_up=True, bounce_time=0.01): ecodes.BTN_DPAD_UP,
    Button(13, pull_up=True, bounce_time=0.01): ecodes.BTN_DPAD_DOWN,
    Button(19, pull_up=True, bounce_time=0.01): ecodes.BTN_DPAD_LEFT,
    Button(26, pull_up=True, bounce_time=0.01): ecodes.BTN_DPAD_RIGHT,
    
    Button(16, pull_up=True, bounce_time=0.01): ecodes.BTN_TL, # L1
    Button(12, pull_up=True, bounce_time=0.01): ecodes.BTN_TR, # R1
}

def presionar(codigo):
    gamepad.write(ecodes.EV_KEY, codigo, 1)
    gamepad.syn()

def soltar(codigo):
    gamepad.write(ecodes.EV_KEY, codigo, 0)
    gamepad.syn()

# Asignar eventos a cada botón
for boton, codigo in botones.items():
    boton.when_pressed  = lambda c=codigo: presionar(c)
    boton.when_released = lambda c=codigo: soltar(c)

# ── Hilo Analógico (Joysticks + Gatillos L2/R2) ────────────
def loop_analogico():
    # Estados para la histéresis de L2 y R2
    l2_presionado = False
    r2_presionado = False
    UMBRAL_ALTO = 800  # Valor para considerar "Pulsado"
    UMBRAL_BAJO = 600  # Valor para considerar "Soltado"

    while True:
        # 1. Leer y mapear Joysticks (Canales 0 a 3)
        x1 = mapear(leer_canal(0), X1_MIN, X1_MAX)
        y1 = mapear(leer_canal(1), Y1_MIN, Y1_MAX)
        x2 = mapear(leer_canal(2), X2_MIN, X2_MAX)
        y2 = mapear(leer_canal(3), Y2_MIN, Y2_MAX)

        gamepad.write(ecodes.EV_ABS, ecodes.ABS_X,  x1)
        gamepad.write(ecodes.EV_ABS, ecodes.ABS_Y,  y1)
        gamepad.write(ecodes.EV_ABS, ecodes.ABS_RX, x2)
        gamepad.write(ecodes.EV_ABS, ecodes.ABS_RY, y2)

        # 2. Leer y evaluar L2 (Canal 4)
        l2_val = leer_canal(4)
        if not l2_presionado and l2_val > UMBRAL_ALTO:
            l2_presionado = True
            gamepad.write(ecodes.EV_KEY, ecodes.BTN_TL2, 1)
        elif l2_presionado and l2_val < UMBRAL_BAJO:
            l2_presionado = False
            gamepad.write(ecodes.EV_KEY, ecodes.BTN_TL2, 0)

        # 3. Leer y evaluar R2 (Canal 5)
        r2_val = leer_canal(5)
        if not r2_presionado and r2_val > UMBRAL_ALTO:
            r2_presionado = True
            gamepad.write(ecodes.EV_KEY, ecodes.BTN_TR2, 1)
        elif r2_presionado and r2_val < UMBRAL_BAJO:
            r2_presionado = False
            gamepad.write(ecodes.EV_KEY, ecodes.BTN_TR2, 0)

        gamepad.syn()
        time.sleep(0.01)  # 100Hz

# Iniciar el hilo de lectura analógica
hilo = threading.Thread(target=loop_analogico, daemon=True)
hilo.start()

# ── Salida limpia ──────────────────────────────────────────
def salir(sig, frame):
    print("\nCerrando gamepad virtual y limpiando SPI...")
    gamepad.close()
    spi.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, salir)
signal.signal(signal.SIGINT, salir)

print("Gamepad virtual activo con botones y analógicos integrados.")
print("Presiona Ctrl+C para salir.")
signal.pause()
