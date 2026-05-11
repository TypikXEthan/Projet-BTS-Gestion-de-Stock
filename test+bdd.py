import serial
import time
import requests
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

# --- CONFIGURATION ---
# On définit la base de l'URL sans la route finale
URL_BASE = "https://lavoisierlocal.online" 

PORT_UHF = '/dev/serial0'
BAUD_UHF = 115200
TEMPS_OUBLI = 4  

# --- INITIALISATION ---
try:
    ser_uhf = serial.Serial(PORT_UHF, baudrate=BAUD_UHF, timeout=0.1)
    # Commande standard pour l'inventaire simple (protocole UHF habituel)
    cmd_scan = bytearray([0xBB, 0x00, 0x22, 0x00, 0x00, 0x22, 0x7E])
except Exception as e:
    print(f"Erreur : Port série UHF inaccessible ({e})")
    ser_uhf = None

reader_hf = SimpleMFRC522()

tags_memoire = {}
dernier_id_affiche = ""

def extraire_id_uhf(raw_data):
    """ Extrait l'ID UHF proprement selon le protocole MagicRF/M6E """
    try:
        start = raw_data.find(b'\xBB\x02\x22')
        if start == -1: return None
        # Le protocole varie selon le capteur, on vérifie la longueur
        payload_len = raw_data[start + 4]
        epc_len = payload_len - 5
        epc_bytes = raw_data[start + 8 : start + 8 + epc_len]
        return epc_bytes.hex().upper()
    except:
        return None

print(f"📡 Système prêt. Envoi vers : {URL_BASE}")
print("Appuyez sur Ctrl+C pour arrêter.\n")

try:
    while True:
        maintenant = time.time()

        # --- 1. SCAN UHF (Objets) ---
        if ser_uhf:
            ser_uhf.reset_input_buffer()
            ser_uhf.write(cmd_scan)
            data = ser_uhf.read_until(b'\x7E')
            
            id_uhf = extraire_id_uhf(data)
            if id_uhf:
                if id_uhf not in tags_memoire or (maintenant - tags_memoire[id_uhf]) > TEMPS_OUBLI:
                    if id_uhf != dernier_id_affiche:
                        print("\n" + "="*40)
                    
                    print(f"🚀 [UHF] Envoi objet : {id_uhf}")
                    
                    try:
                        # CORRECTION : On pointe vers /scan_objet
                        res = requests.post(f"{URL_BASE}/scan_objet", 
                                          json={"rfid_tag_epc": id_uhf}, 
                                          timeout=3)
                        print(f"Statut : {res.status_code}")
                        tags_memoire[id_uhf] = maintenant
                        dernier_id_affiche = id_uhf
                    except Exception as e:
                        print(f"⚠️ Erreur VPS (UHF) : {e}")

        # --- 2. SCAN RC522 (Badges NFC/HF) ---
        id_hf, text = reader_hf.read_no_block()
        if id_hf:
            id_s = str(id_hf)
            if id_s not in tags_memoire or (maintenant - tags_memoire[id_s]) > TEMPS_OUBLI:
                if id_s != dernier_id_affiche:
                    print("\n" + "="*40)

                print(f"💳 [RC522] Envoi badge : {id_s}")

                try:
                    # CORRECTION : On pointe vers /verifier_acces
                    res = requests.post(f"{URL_BASE}/verifier_acces", 
                                      json={"badge_uid": id_s}, 
                                      timeout=3)
                    print(f"Statut : {res.status_code}")
                    tags_memoire[id_s] = maintenant
                    dernier_id_affiche = id_s
                except Exception as e:
                    print(f"⚠️ Erreur VPS (RC522) : {e}")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nArrêt par l'utilisateur.")
finally:
    if ser_uhf: ser_uhf.close()
    GPIO.cleanup()
