from evdev import UInput, ecodes
from gpiozero import Button
import signal
import sys

# Definir los botones del gamepad virtual
capabilities = {
    ecodes.EV_KEY: [
        ecodes.BTN_A,
        ecodes.BTN_B,
        ecodes.BTN_TL,   # L
        ecodes.BTN_TR,   # R
        ecodes.BTN_START,
        ecodes.BTN_SELECT,
    ]
}

# Crear gamepad virtual
gamepad = UInput(capabilities, name="RetroConsola Gamepad")

# Mapeo GPIO → botón
botones = {
    Button(17, pull_up=True, bounce_time=0.05): ecodes.BTN_A,
    Button(27, pull_up=True, bounce_time=0.05): ecodes.BTN_B,
    Button(22, pull_up=True, bounce_time=0.05): ecodes.BTN_TL,
    Button(23, pull_up=True, bounce_time=0.05): ecodes.BTN_TR,
    Button(24, pull_up=True, bounce_time=0.05): ecodes.BTN_START,
    Button(25, pull_up=True, bounce_time=0.05): ecodes.BTN_SELECT,
}

def presionar(codigo):
    gamepad.write(ecodes.EV_KEY, codigo, 1)
    gamepad.syn()

def soltar(codigo):
    gamepad.write(ecodes.EV_KEY, codigo, 0)
    gamepad.syn()

for boton, codigo in botones.items():
    boton.when_pressed  = lambda c=codigo: presionar(c)
    boton.when_released = lambda c=codigo: soltar(c)

def salir(sig, frame):
    gamepad.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, salir)
signal.signal(signal.SIGINT, salir)

print("Gamepad virtual activo, Ctrl+C para salir")
signal.pause()
