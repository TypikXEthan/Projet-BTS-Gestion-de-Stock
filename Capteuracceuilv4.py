import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import time
import hashlib

# --- CONFIGURATION ---
#URL_VM = "http://172.29.241.141:5000/verifier_acces"
URL_VM = "https://lavoisierlocal.online/verifier_acces"
PORTE_ID = "Porte_Stockage"  # <--- Change l'identifiant ici pour chaque porte
RELAY_PIN = 18

# Configuration GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH) # Relais ouvert par défaut

reader = SimpleMFRC522()

print(f"--- LECTEUR RFID [{PORTE_ID}] PRÊT ---")
print("En attente d'un badge...")

try:
    while True:
        # 1. Lecture physique du badge
        id_badge, text = reader.read()
        
        # 2. HACHAGE SHA-256 (Sécurité)
        badge_uid_raw = str(id_badge).strip()
        badge_hash = hashlib.sha256(badge_uid_raw.encode()).hexdigest()
        
        print(f"\n[SCAN] Badge détecté sur {PORTE_ID}")

        # 3. Envoi du HASH et de l'ID de la porte au Flask
        try:
            # On envoie les deux infos dans le JSON
            payload = {
                "badge_uid": badge_hash, 
                "porte": PORTE_ID
            }
            
            response = requests.post(URL_VM, json=payload, timeout=5)
            
            if response.status_code == 200:
                user = response.json()
                print(f"✅ ACCÈS ACCORDÉ : {user.get('prenom', 'Utilisateur')} {user.get('nom', '')}")
                
                # Action sur le relais (Déverrouillage)
                GPIO.output(RELAY_PIN, GPIO.LOW)
                time.sleep(22) # Temps d'ouverture
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                
            elif response.status_code == 403:
                print(f"❌ ACCÈS REFUSÉ pour {PORTE_ID}")
            else:
                print(f"⚠️ Erreur Serveur : {response.status_code}")
                
        except Exception as e:
            print(f"!! Erreur de connexion au serveur : {e}")

        time.sleep(1)
        print("\nPrêt pour le prochain scan...")

except KeyboardInterrupt:
    print("\nArrêt du programme...")
finally:
    GPIO.cleanup()
