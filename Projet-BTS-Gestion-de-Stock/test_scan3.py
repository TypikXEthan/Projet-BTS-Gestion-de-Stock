import requests
import hashlib

def simuler_lecteur():
    url_base = "https://lavoisierlocal.online"
    
    print("\n" + "═"*45)
    print("      SIMULATEUR RFID (ACCÈS & MATÉRIEL)")
    print("═"*45)
    print("1. Scanner un badge UTILISATEUR (Ouvrir session)")
    print("2. Scanner un tag MATÉRIEL (Mouvement de stock)")
    print("3. Simuler une erreur de lecture (Orange)")
    print("q. Quitter")

    while True:
        choix = input("\n👉 Votre choix : ").strip().lower()

        if choix == 'q': break

        # --- CAS 1 : BADGE UTILISATEUR ---
        if choix == '1':
            uid = input("ID du Badge (ex: 12345678) : ").strip()
            # On envoie vers /verifier_acces
            try:
                res = requests.post(f"{url_base}/verifier_acces", json={"badge_uid": uid}, timeout=5)
                if res.status_code == 200:
                    print(f"✅ ACCÈS OK : Session ouverte pour l'utilisateur.")
                else:
                    print(f"❌ REFUSÉ : {res.status_code} - Badge inconnu.")
            except Exception as e: print(f"💥 Erreur : {e}")

        # --- CAS 2 : TAG MATÉRIEL ---
        elif choix == '2':
            epc = input("EPC du Matériel (ex: PC-PORTABLE-01) : ").strip().upper()
            # On envoie vers /scan_objet
            try:
                res = requests.post(f"{url_base}/scan_objet", json={"rfid_tag_epc": epc}, timeout=5)
                if res.status_code == 200:
                    print(f"📦 OBJET OK : Tag envoyé au flux matériel.")
                elif res.status_code == 404:
                    print(f"⚠️ INCONNU : Ce tag n'existe pas dans l'inventaire.")
                else:
                    print(f"❌ ERREUR : {res.status_code}")
            except Exception as e: print(f"💥 Erreur : {e}")

        # --- CAS 3 : ERREUR LECTURE ---
        elif choix == '3':
            try:
                requests.post(f"{url_base}/erreur_lecture", timeout=5)
                print("⚠️ Signal d'erreur envoyé à la tablette.")
            except Exception as e: print(f"💥 Erreur : {e}")

if __name__ == "__main__":
    simuler_lecteur()
