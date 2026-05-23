import serial
import time
from datetime import datetime
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests

# --- CONFIGURATION URL API ---
URL_BASE = "https://lavoisierlocal.online"
HEADERS = {"Content-Type": "application/json"}

# --- CONFIGURATION UHF ---
PORT_UHF = '/dev/serial0'
BAUD_UHF = 115200
ID_SIZE_UHF = 12
TEMPS_OUBLI = 4  # Temps anti-rebond (en secondes)

# --- CONFIGURATION GPIO RELAIS ---
RELAY_PIN = 18
DUREE_OUVERTURE_RELAIS = 3  # Temps d'ouverture de la porte (en secondes)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH) # Fermé par défaut (High ou Low selon votre relais)

# --- INITIALISATION MATÉRIEL ---
# Timeout court (0.02s) pour ne pas bloquer la boucle principale
ser_uhf = serial.Serial(PORT_UHF, baudrate=BAUD_UHF, timeout=0.02)
cmd_scan = bytearray([0xBB, 0x00, 0x22, 0x00, 0x00, 0x22, 0x7E])

reader_hf = SimpleMFRC522()

# Mémoire pour l'anti-doublon et la gestion du relais
tags_en_memoire = {}
relais_expire_a = 0  # Timestamp pour la fermeture automatique du relais

def get_timestamp():
    return datetime.now().strftime("[%H:%M:%S]")

def extraire_id_uhf(raw_data):
    """ Décode la trame UHF M5Stack """
    try:
        start = raw_data.find(b'\xBB\x02\x22')
        if start == -1: return None
        payload_len = raw_data[start + 4]
        epc_len = payload_len - 5
        epc_bytes = raw_data[start + 8 : start + 8 + epc_len]
        epc_hex = epc_bytes.hex().upper()
        return epc_hex.zfill(ID_SIZE_UHF)[-ID_SIZE_UHF:]
    except:
        return None

print("--- SYSTEME RFID DOUBLE (UHF + HF) CONNECTÉ À L'API ---")
print("En attente de tags ou de badges...")

try:
    while True:
        maintenant = time.time()

        # ==========================================================
        # GESTION NON-BLOQUANTE DU RELAIS (Fermeture automatique)
        # ==========================================================
        if relais_expire_a > 0 and maintenant >= relais_expire_a:
            GPIO.output(RELAY_PIN, GPIO.HIGH) # Fermer la porte
            relais_expire_a = 0
            print(f"{get_timestamp()} [RELAIS] Fermeture de la porte.")

        # ==========================================================
        # 1. LECTURE UHF (M5STACK MATÉRIEL) ➔ VERS /scan_objet
        # ==========================================================
        ser_uhf.reset_input_buffer()
        ser_uhf.write(cmd_scan)
        # Lecture rapide sans bloquer le script entier
        data_uhf = ser_uhf.read_until(b'\x7E')
        
        if data_uhf:
            id_uhf = extraire_id_uhf(data_uhf)
            if id_uhf:
                # Anti-doublon actif
                if id_uhf not in tags_en_memoire or (maintenant - tags_en_memoire[id_uhf]) > TEMPS_OUBLI:
                    print(f"{get_timestamp()} [UHF] SCAN MATÉRIEL : {id_uhf}")
                    
                    # ENVOI HTTP VERS /scan_objet
                    try:
                        res = requests.post(f"{URL_BASE}/scan_objet", json={"rfid_tag_epc": id_uhf}, headers=HEADERS, timeout=2)
                        if res.status_code == 200:
                            print(f"   ➔ API 📦: {res.json().get('message')}")
                        else:
                            print(f"   ➔ API ⚠️ ({res.status_code}): {res.text}")
                    except Exception as e:
                        print(f"   ➔ 💥 Erreur envoi UHF : {e}")
                        
                    tags_en_memoire[id_uhf] = maintenant

        # ==========================================================
        # 2. LECTURE HF (RC522 UTILISATEUR) ➔ VERS /verifier_acces
        # ==========================================================
        # read_no_block() est indispensable pour ne pas stopper le scanner UHF
        id_hf, text_hf = reader_hf.read_no_block()
        
        if id_hf:
            id_hf_str = str(id_hf).strip()
            
            if id_hf_str not in tags_en_memoire or (maintenant - tags_en_memoire[id_hf_str]) > TEMPS_OUBLI:
                print(f"{get_timestamp()} [RC522] BADGE UTILISATEUR : {id_hf_str}")
                
                # ENVOI HTTP VERS /verifier_acces
                try:
                    res = requests.post(f"{URL_BASE}/verifier_acces", json={"badge_uid": id_hf_str, "porte": "Porte_Stock"}, headers=HEADERS, timeout=2)
                    if res.status_code == 200:
                        print("   ➔ API 🔓: Accès autorisé ! Activation du relais.")
                        
                        # Action physique non-bloquante : Ouvrir la porte
                        GPIO.output(RELAY_PIN, GPIO.LOW)
                        # On planifie la fermeture dans 3 secondes sans figer le script
                        relais_expire_a = maintenant + DUREE_OUVERTURE_RELAIS
                    else:
                        print(f"   ➔ API 🔒 ({res.status_code}): Badge refusé ou inconnu.")
                except Exception as e:
                    print(f"   ➔ 💥 Erreur envoi HF : {e}")
                    
                tags_en_memoire[id_hf_str] = maintenant

        # Petite pause pour soulager le CPU du Raspberry Pi
        time.sleep(0.02)

except KeyboardInterrupt:
    print("\nArrêt des scanners.")
finally:
    ser_uhf.close()
    GPIO.cleanup()