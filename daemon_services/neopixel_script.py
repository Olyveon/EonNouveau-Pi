import board
import busio
import neopixel_spi
import time
import math

NUM_LEDS = 8
spi = busio.SPI(clock = board.D7, MOSI = board.D6, MISO = board.D5)
pixels = neopixel_spi.NeoPixel_SPI(spi, NUM_LEDS, brightness = 0.3, auto_write = False)

def hsv_a_rgb(h, s, v):
    if s == 0:
        return (int(v*255), int(v*255), int(v*255))
    h = h % 360
    i = int(h / 60)
    f = (h / 60) - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else:        r, g, b = v, p, q
    return (int(r*255), int(g*255), int(b*255))

offset = 0

print("Neo Pixels are working")

coff = 0
while True:
    off_idx = coff // 10
    pixels[off_idx] = (0, 0, 0)
    for i in range(NUM_LEDS):
        hue = (offset + i * (360 / NUM_LEDS)) % 360
        if i is not off_idx:
            pixels[i] = hsv_a_rgb(hue, 1.0, 1.0)
    pixels.show()
    offset = (offset + 2) % 360
    coff = (coff + 1) % 80
    time.sleep(0.03)
