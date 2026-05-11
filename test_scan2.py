import requests

def simuler_lecteur():
    # CORRECTION ICI : L'URL doit pointer vers l'API /scan_objet de ton domaine
    url = "https://lavoisierlocal.online/scan_objet"

    print("\n" + "═"*45)
    print("      SIMULATEUR CAPTEUR RFID (VPS)")
    print(f"      Cible : {url}")
    print("═"*45)

    while True:
        tag_epc = input("\n👉 EPC détecté (ou 'q' pour quitter) : ").strip().upper()

        if tag_epc.lower() == 'q':
            break

        if not tag_epc:
            continue

        try:
            # Envoi vers le VPS
            # Note : On met verify=True si ton certificat SSL est valide (ce qui devrait être le cas)
            response = requests.post(url, json={"rfid_tag_epc": tag_epc}, timeout=5)

            if response.status_code == 200:
                print(f"✅ [200 OK] : Tag {tag_epc} reçu par le VPS.")
                print("   Vérifie l'écran de la tablette en direct !")

            elif response.status_code == 403:
                info = response.json()
                print(f"⛔ [403 REFUSÉ] : {info.get('message', 'Action interdite')}")

            elif response.status_code == 404:
                print(f"⚠️ [404] : Tag {tag_epc} inconnu sur le serveur.")

            else:
                print(f"❌ Erreur serveur (Code {response.status_code})")
                print(f"Réponse : {response.text}")

        except requests.exceptions.SSLError:
            print("🔐 Erreur SSL : Problème avec le certificat HTTPS du VPS.")
        except requests.exceptions.ConnectionError:
            print("📡 Erreur : Impossible de joindre le VPS. Vérifie ta connexion.")
        except Exception as e:
            print(f"💥 Erreur : {e}")

if __name__ == "__main__":
    simuler_lecteur()
