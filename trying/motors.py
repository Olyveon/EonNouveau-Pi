from gpiozero import OutputDevice
from time import sleep

# Configuramos los motores usando los pines de tu excel
motor_derecho = OutputDevice(24)
motor_izquierdo = OutputDevice(25)

print("Iniciando prueba de vibración...")
print("Presiona Ctrl+C para detener el script.")

try:
    while True:
        print("Motores: ENCENDIDOS")
        motor_derecho.on()
        motor_izquierdo.on()
        
        sleep(5) # Espera 2 segundos
        
        print("Motores: APAGADOS")
        motor_derecho.off()
        motor_izquierdo.off()
        sleep(5)

except KeyboardInterrupt:
    # Esta sección garantiza que si cancelas el script, 
    # los motores no se queden vibrando infinitamente
    print("\nDeteniendo prueba y apagando motores de forma segura...")
    motor_derecho.off()
    motor_izquierdo.off()
    print("Prueba finalizada.")
