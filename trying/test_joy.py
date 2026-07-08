import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0 (CE0)
spi.max_speed_hz = 1350000

def leer_canal(canal):
    datos = spi.xfer2([1, (8 + canal) << 4, 0])
    return ((datos[1] & 3) << 8) + datos[2]

try:
    while True:
        x1 = leer_canal(0)  # Joystick 1 eje X
        y1 = leer_canal(1)  # Joystick 1 eje Y
        y2 = leer_canal(2)  # Joystick 2 eje X
        x2 = leer_canal(3)  # Joystick 2 eje Y
        print(f"J1 X:{x1:4d} Y:{y1:4d} | J2 X:{x2:4d} Y:{y2:4d}")
        time.sleep(0.1)
except KeyboardInterrupt:
    spi.close()
