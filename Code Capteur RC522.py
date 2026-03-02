import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time

reader = SimpleMFRC522()
# Cette ligne est magique : elle stabilise la communication
reader.reader.spi.max_speed_hz = 500000 

print("--- TEST DE DÉTECTION FORCÉ ---")
print("Posez votre badge DIRECTEMENT sur l'antenne (le cercle blanc)...")

try:
    while True:
        # On utilise une version plus brute de la lecture
        id = reader.read_id()
        if id:
            print(f"SUCCÈS ! ID détecté : {id}")
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()