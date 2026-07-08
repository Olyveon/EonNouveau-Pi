import time
import spidev

spi = spidev.SpiDev()
spi.open(0, 0) # Tu bus SPI0 para los joysticks
spi.max_speed_hz = 1350000

def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

print("Mueve el joystick en círculos por 5 segundos para escanear los límites...")
time.sleep(1)

min_x, max_x = 1023, 0
min_y, max_y = 1023, 0

start_time = time.time()
while time.time() - start_time < 10:
    x = read_adc(0) # Asumiendo Canal 0 para X
    y = read_adc(1) # Asumiendo Canal 1 para Y
    
    if x < min_x: min_x = x
    if x > max_x: max_x = x
    if y < min_y: min_y = y
    if y > max_y: max_y = y
    time.sleep(0.01)

print(f"\nResultados del escaneo Hall:")
print(f"Eje X -> Mín: {min_x}, Máx: {max_x} | Centro aproximado: {(min_x+max_x)//2}")
print(f"Eje Y -> Mín: {min_y}, Máx: {max_y} | Centro aproximado: {(min_y+max_y)//2}")
