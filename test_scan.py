import requests
import time

def simuler_lecteur():
    print("\n" + "═"*40)
    print("      LECTEUR RFID (Simulation)")
    print("     Envoyez un EPC pour scanner")
    print("═"*40)

    while True:
        tag_epc = input("\n👉 EPC détecté (ou 'q' pour quitter) : ").strip().upper()

        if tag_epc.lower() == 'q':
            break

        if not tag_epc:
            continue

        try:
            # On envoie vers la route de scan temporaire
            url = "http://192.168.1.166:5000/scan_objet"
            response = requests.post(url, json={"rfid_tag_epc": tag_epc}, timeout=2)

            if response.status_code == 200:
                print(f"✅ OK : Tag {tag_epc} envoyé à la session.")
            elif response.status_code == 404:
                print(f"⚠️ Erreur : Tag {tag_epc} inconnu en BDD.")
            else:
                print(f"❌ Erreur serveur : {response.status_code}")

        except Exception as e:
            print(f"📡 Erreur de connexion au serveur : {e}")

if __name__ == "__main__":
    simuler_lecteur()
