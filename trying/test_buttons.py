from gpiozero import Button
from signal import pause

botones = {
    "A":      Button(17, pull_up=True),
    "B":      Button(27, pull_up=True),
    "L":      Button(22, pull_up=True),
    "R":      Button(23, pull_up=True),
    "Start":  Button(24, pull_up=True),
    "Select": Button(25, pull_up=True),
}

for nombre, boton in botones.items():
    boton.when_pressed  = lambda n=nombre: print(f"Presionado: {n}")
    boton.when_released = lambda n=nombre: print(f"Soltado:    {n}")

print("Presiona los botones, Ctrl+C para salir")
pause()
