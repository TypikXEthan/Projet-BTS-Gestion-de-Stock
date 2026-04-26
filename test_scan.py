import requests
import time

def envoyer_scan():
    print("\n" + "="*40)
    print("      SCANNER RFID ACTIF (Simulation)")
    print("="*40)
    
    tag_epc = input("Tag détecté (EPC) : ").strip()
    if not tag_epc: return

    try:
        # On envoie juste l'info au serveur
        url = "http://127.0.0.1:5000/scan_objet"
        response = requests.post(url, json={"rfid_tag_epc": tag_epc}, timeout=2)
        
        if response.status_code == 200:
            resultat = response.json()
            print(f"✅ Succès : Le matériel est maintenant en : {resultat['nouveau_etat']}")
        elif response.status_code == 404:
            print(f"❌ Erreur : Tag {tag_epc} inconnu en base.")
        else:
            print(f"⚠️ Erreur Serveur : {response.status_code}")

    except Exception as e:
        print(f"📡 Erreur de connexion au serveur : {e}")

if __name__ == "__main__":
    while True:
        envoyer_scan()
