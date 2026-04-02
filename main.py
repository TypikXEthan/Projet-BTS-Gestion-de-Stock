from flask import Flask, render_template, request, redirect, session,flash,url_for
import mysql.connector
import hashlib
from datetime import datetime, timedelta
import time

app = Flask(__name__)
app.secret_key = "cle_secrete_bts_rfid"  # clé de session

# Connexion à la base
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="Projet_BTS_RFID"
    )
@app.before_request
def make_session_permanent():
    session.permanent = True
    # On définit la durée d'activité à 60 minutes
    app.permanent_session_lifetime = timedelta(minutes=60)

# -------------------------------
# LOGIN
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    # 1. Vérifier si l'utilisateur est actuellement sous le coup d'une attente
    if "bloque_jusqua" in session:
        temps_restant = int(session["bloque_jusqua"] - time.time())
        if temps_restant > 0:
            return render_template("IHM/login.html", 
                                   erreur=f"Trop de tentatives. Réessayez dans {temps_restant} secondes.",
                                   attente=temps_restant) # On envoie le temps au HTML
        else:
            # Le temps est écoulé, on réinitialise
            session.pop("bloque_jusqua", None)
            session["tentatives"] = 0

    if request.method == "POST":
        utilisateur = request.form["utilisateur"]
        mot_de_passe = request.form["mot_de_passe"]
        mdp_hash = hashlib.sha256(mot_de_passe.encode()).hexdigest()

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_utilisateur, utilisateur, nom, prenom, role, admin
            FROM utilisateurs
            WHERE utilisateur=%s AND mot_de_passe=%s
        """, (utilisateur, mdp_hash))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            # Succès : on nettoie la session
            session.pop("tentatives", None)
            session.pop("bloque_jusqua", None)
            
            session["id_user"] = user["id_utilisateur"]
            session["utilisateur"] = user["utilisateur"]
            session["nom"] = user["nom"]
            session["prenom"] = user["prenom"]
            session["role"] = user["role"]
            session["admin"] = user["admin"]
            return redirect("/dashboard")
        else:
            # Échec : on incrémente le compteur
            session["tentatives"] = session.get("tentatives", 0) + 1
            
            if session["tentatives"] >= 3:
                # On bloque pour 90 secondes à partir de maintenant
                session["bloque_jusqua"] = time.time() + 90
                return render_template("IHM/login.html", 
                                       erreur="Trop d'échecs. Compte bloqué pour 90 secondes.",
                                       attente=90)
            
            return render_template("IHM/login.html", 
                                   erreur=f"Identifiants incorrects ({session['tentatives']}/3)")

    return render_template("IHM/login.html")
# -------------------------------
# DASHBOARD
# -------------------------------
@app.route("/dashboard")
def dashboard():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Matériels disponibles
    cursor.execute("SELECT COUNT(*) AS total FROM materiel_stock WHERE etat = 'Disponible'")
    nb_stock = cursor.fetchone()["total"]

    # Matériels sortis
    cursor.execute("SELECT COUNT(*) AS total FROM materiel_stock WHERE etat = 'Sortie'")
    nb_sorti = cursor.fetchone()["total"]

    # Derniers mouvements (10 derniers)
    cursor.execute("""
        SELECT m.type_mouvement, m.date_heure,
               ms.nom_modele,
               u.nom, u.prenom
        FROM mouvements m
        JOIN materiel_stock ms ON m.id_materiel = ms.id_materiel
        JOIN utilisateurs u ON m.id_utilisateur = u.id_utilisateur
        ORDER BY m.date_heure DESC
        LIMIT 10
    """)
    mouvements = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "IHM/dashboard.html",
        nb_stock=nb_stock,
        nb_sorti=nb_sorti,
        mouvements=mouvements,
        nom=session["nom"],
        prenom=session["prenom"]
    )

# -------------------------------
# MATERIELS
# -------------------------------
@app.route("/materiels")
def materiels():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # =========================
    # RECHERCHE
    # =========================
    recherche = request.args.get("recherche", "")
    params = []
    query = "SELECT * FROM materiel_stock"

    if recherche:
        query += " WHERE nom_modele LIKE %s OR rfid_tag_epc LIKE %s"
        params.extend([f"%{recherche}%", f"%{recherche}%"])

    # =========================
    # PAGINATION
    # =========================
    page = int(request.args.get("page", 1))
    limit = 10
    offset = (page - 1) * limit

    total_query = "SELECT COUNT(*) AS total FROM materiel_stock"
    if recherche:
        total_query += " WHERE nom_modele LIKE %s OR rfid_tag_epc LIKE %s"

    cursor.execute(total_query, params)
    total_rows = cursor.fetchone()["total"]
    total_pages = (total_rows + limit - 1) // limit

    query += " LIMIT %s OFFSET %s"
    cursor.execute(query, params + [limit, offset])
    materiels = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "IHM/materiels.html",
        materiels=materiels,
        page=page,
        total_pages=total_pages,
        recherche=recherche,
        prenom=session["prenom"],
        nom=session["nom"]
    )

# --------------------------
#Historique
#---------------------------
@app.route("/historique")
def historique():
    if "id_user" not in session:
        return redirect("/")

    # 1. On récupère ce que l'utilisateur a tapé (si vide, on aura une chaîne vide)
    recherche = request.args.get('recherche', '').strip()

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 2. On prépare la base de la requête
    sql = """
        SELECT m.id_mouvement, m.type_mouvement, m.date_heure,
               ms.nom_modele,
               u.nom, u.prenom
        FROM mouvements m
        LEFT JOIN materiel_stock ms ON m.id_materiel = ms.id_materiel
        LEFT JOIN utilisateurs u ON m.id_utilisateur = u.id_utilisateur
    """

    # 3. On ajoute le filtre si une recherche est présente
    if recherche:
        sql += """ 
            WHERE ms.nom_modele LIKE %s 
            OR u.nom LIKE %s 
            OR u.prenom LIKE %s 
            OR m.type_mouvement LIKE %s
        """
        params = (f"%{recherche}%", f"%{recherche}%", f"%{recherche}%", f"%{recherche}%")
        sql += " ORDER BY m.date_heure DESC"
        cursor.execute(sql, params)
    else:
        # Requête classique sans filtre
        sql += " ORDER BY m.date_heure DESC"
        cursor.execute(sql)

    mouvements = cursor.fetchall()
    cursor.close()
    db.close()

    # 4. TRÈS IMPORTANT : On renvoie 'recherche' au HTML pour pas que la barre se vide
    return render_template(
        "IHM/historique.html",
        mouvements=mouvements,
        nom=session["nom"],
        prenom=session["prenom"],
        recherche=recherche # On le rajoute ici
    )

# -------------------------------
# UTILISATEURS
# -------------------------------
@app.route("/utilisateurs", methods=["GET", "POST"])
def utilisateurs():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.id_utilisateur, u.nom, u.prenom, u.utilisateur, u.role, u.admin,
               COUNT(ms.id_materiel) AS nb_emprunts
        FROM utilisateurs u
        LEFT JOIN materiel_stock ms ON u.id_utilisateur = ms.id_utilisateur_actuel
        GROUP BY u.id_utilisateur
    """)
    utilisateurs = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("IHM/utilisateurs.html",
                           utilisateurs=utilisateurs,
                           nom=session["nom"],
                           prenom=session["prenom"])

# -------------------------------
# RESERVATIONS
# -------------------------------
@app.route("/reservations", methods=["GET", "POST"])
def reservations():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)
    user_id = session["id_user"]

    from datetime import datetime, timedelta, date

    # =========================
    # 🔥 AUTO ANNULATION
    # =========================
    cursor.execute("""
        SELECT id_reservation, id_materiel
        FROM reservations
        WHERE statut='Confirmée' AND date_limite < NOW()
    """)
    expired = cursor.fetchall()

    for r in expired:
        cursor.execute("""
            UPDATE reservations 
            SET statut='Annulée'
            WHERE id_reservation=%s
        """, (r["id_reservation"],))

        cursor.execute("""
            UPDATE materiel_stock
            SET id_utilisateur_actuel=NULL,
                etat='disponible'
            WHERE id_materiel=%s
        """, (r["id_materiel"],))

    db.commit()

    # =========================
    # POST
    # =========================
    if request.method == "POST":
        action = request.form.get("action")

        # =====================
        # 🔵 RESERVER
        # =====================
        if action == "reserver":
            id_materiel = request.form.get("id_materiel")
            date_reservation = request.form.get("date_reservation")

            if id_materiel and date_reservation:
                date_resa = datetime.strptime(date_reservation, "%Y-%m-%d")
                now = datetime.now()

                # ⛔ date passée
                if date_resa.date() < now.date():
                    return redirect("/reservations")

                # ⛔ max 7 jours
                if date_resa > now + timedelta(days=7):
                    return redirect("/reservations")

                # 📅 date limite = lendemain 8h
                date_limite = date_resa + timedelta(days=1)
                date_limite = date_limite.replace(hour=8, minute=0, second=0)

                # 🔍 check matériel
                cursor.execute("""
                    SELECT etat, reservable, actif, id_utilisateur_actuel
                    FROM materiel_stock
                    WHERE id_materiel=%s
                """, (id_materiel,))
                mat = cursor.fetchone()

                if mat and mat["reservable"] == 1 and mat["actif"] == 1 and mat["etat"] == "disponible":

                    # 🔒 si aujourd’hui → bloquer direct
                    if date_resa.date() == now.date():
                        cursor.execute("""
                            UPDATE materiel_stock
                            SET id_utilisateur_actuel=%s,
                                etat='reserve'
                            WHERE id_materiel=%s
                        """, (user_id, id_materiel))

                    # 💾 insert réservation
                    cursor.execute("""
                        INSERT INTO reservations 
                        (id_materiel, id_utilisateur, date_reservation, date_limite, statut)
                        VALUES (%s,%s,%s,%s,'Confirmée')
                    """, (id_materiel, user_id, date_resa, date_limite))

                    db.commit()

        # =====================
        # 🔴 ANNULER
        # =====================
        elif action == "annuler":
            id_reservation = request.form.get("id_reservation")

            cursor.execute("""
                SELECT id_materiel, id_utilisateur 
                FROM reservations 
                WHERE id_reservation=%s
            """, (id_reservation,))
            res = cursor.fetchone()

            if res and res["id_utilisateur"] == user_id:
                cursor.execute("""
                    UPDATE reservations 
                    SET statut='Annulée'
                    WHERE id_reservation=%s
                """, (id_reservation,))

                cursor.execute("""
                    UPDATE materiel_stock
                    SET id_utilisateur_actuel=NULL,
                        etat='disponible'
                    WHERE id_materiel=%s
                """, (res["id_materiel"],))

                db.commit()

        # =====================
        # 🟢 RECUPERER
        # =====================
        elif action == "recuperer":
            id_reservation = request.form.get("id_reservation")

            cursor.execute("""
                SELECT id_materiel, statut 
                FROM reservations 
                WHERE id_reservation=%s
            """, (id_reservation,))
            res = cursor.fetchone()

            if res and res["statut"] == "Confirmée":
                id_mat = res["id_materiel"]

                cursor.execute("""
                    UPDATE materiel_stock 
                    SET etat='indisponible'
                    WHERE id_materiel=%s
                """, (id_mat,))

                cursor.execute("""
                    UPDATE reservations 
                    SET statut='Récupérée'
                    WHERE id_reservation=%s
                """, (id_reservation,))

                cursor.execute("""
                    INSERT INTO mouvements 
                    (id_materiel, id_utilisateur, type_mouvement, date_heure)
                    VALUES (%s,%s,'Sortie',NOW())
                """, (id_mat, user_id))

                db.commit()

    # =========================
    # GET
    # =========================

    date_min = date.today().isoformat()
    date_max = (date.today() + timedelta(days=7)).isoformat()

    # 📦 matériels disponibles
    cursor.execute("""
        SELECT id_materiel, nom_modele, rfid_tag_epc
        FROM materiel_stock
        WHERE etat='disponible'
        AND reservable=1
        AND actif=1
        AND id_utilisateur_actuel IS NULL
    """)
    materiels = cursor.fetchall()

    # 📋 mes réservations
    cursor.execute("""
        SELECT r.*, ms.nom_modele
        FROM reservations r
        JOIN materiel_stock ms ON r.id_materiel=ms.id_materiel
        WHERE r.id_utilisateur=%s
        AND r.date_reservation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        ORDER BY r.date_reservation DESC
    """, (user_id,))
    mes_reservations = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "IHM/reservations.html",
        materiels=materiels,
        mes_reservations=mes_reservations,
        date_min=date_min,
        date_max=date_max,
        nom=session["nom"],
        prenom=session["prenom"],
        admin=session.get("admin", 0)
    )

#-----------------
#Administration
#-----------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "id_user" not in session or session.get("admin") != 1:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        # --- MODIFIER HORAIRES ---
        if action == "modifier_horaires_globaux":
            h_debut = request.form.get("h_debut")
            h_fin = request.form.get("h_fin")
            cursor.execute("UPDATE portes SET heure_debut = %s, heure_fin = %s WHERE statut_acces = 'CONFIG'", (h_debut, h_fin))
            db.commit()
            flash("Horaires mis à jour", "success")

        # --- CRÉER UTILISATEUR (AVEC HACHAGE MDP ET BADGE) ---
        elif action == "creer_utilisateur":
            mdp_clair = request.form.get("mot_de_passe")
            badge_clair = request.form.get("badge_uid") # Récupération du badge
            
            # Hachage du mot de passe
            mdp_hash = hashlib.sha256(mdp_clair.encode()).hexdigest()
            # Hachage du Badge UID
            badge_hash = hashlib.sha256(badge_clair.encode()).hexdigest() if badge_clair else None
            
            cursor.execute("""
                INSERT INTO utilisateurs (utilisateur, mot_de_passe, badge_uid, nom, prenom, email, telephone, role, admin) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (request.form.get("utilisateur"), mdp_hash, badge_hash,
                  request.form.get("nom"), request.form.get("prenom"), request.form.get("email"),
                  request.form.get("telephone"), request.form.get("role"), request.form.get("admin_status")))
            db.commit()
            flash("Utilisateur créé (données hachées)", "success")

        # --- MODIFIER UTILISATEUR (AVEC HACHAGE SI NOUVEAU MDP OU BADGE) ---
        elif action == "modifier_utilisateur_complet":
            id_u = request.form.get("id_utilisateur")
            nouveau_mdp = request.form.get("nouveau_mdp")
            nouveau_badge = request.form.get("badge_uid")
            
            cursor.execute("""
                UPDATE utilisateurs SET utilisateur=%s, nom=%s, prenom=%s, email=%s, telephone=%s, role=%s, admin=%s
                WHERE id_utilisateur=%s
            """, (request.form.get("utilisateur"), request.form.get("nom"), request.form.get("prenom"),
                  request.form.get("email"), request.form.get("telephone"),
                  request.form.get("role"), request.form.get("admin_status"), id_u))
            
            # Hachage si nouveau badge saisi
            if nouveau_badge and nouveau_badge.strip() != "":
                b_hash = hashlib.sha256(nouveau_badge.encode()).hexdigest()
                cursor.execute("UPDATE utilisateurs SET badge_uid=%s WHERE id_utilisateur=%s", (b_hash, id_u))

            # Hachage si nouveau MDP saisi
            if nouveau_mdp and nouveau_mdp.strip() != "":
                mdp_hash = hashlib.sha256(nouveau_mdp.encode()).hexdigest()
                cursor.execute("UPDATE utilisateurs SET mot_de_passe=%s WHERE id_utilisateur=%s", (mdp_hash, id_u))
                
            db.commit()
            flash("Profil mis à jour", "success")

        # --- LE RESTE DU CODE (SUPPRESSION / MATÉRIEL) RESTE IDENTIQUE ---
        elif action == "supprimer_utilisateur":
            id_u = request.form.get("id_utilisateur")
            if int(id_u) == session.get('id_user'):
                flash("Impossible de supprimer votre propre compte !", "danger")
            else:
                cursor.execute("DELETE FROM utilisateurs WHERE id_utilisateur = %s", (id_u,))
                db.commit()
                flash("Utilisateur supprimé", "warning")

        elif action == "ajouter_materiel":
            cursor.execute("INSERT INTO materiel_stock (id_materiel, nom_modele, rfid_tag_epc, etat, actif, reservable) VALUES (%s,%s,%s,%s,1,1)",
                           (request.form.get("id_inventaire"), request.form.get("nom_modele"), request.form.get("rfid_tag"), request.form.get("etat")))
            db.commit()
        
        elif action == "modifier_materiel_complet":
            id_mat = request.form.get("id_materiel")
            statut = request.form.get("nouveau_statut")
            dest_id = request.form.get("id_utilisateur_actuel") or None
            cursor.execute("UPDATE materiel_stock SET nom_modele=%s, rfid_tag_epc=%s, etat=%s, id_utilisateur_actuel=%s WHERE id_materiel=%s",
                           (request.form.get("nom_modele"), request.form.get("rfid_tag_epc"), statut, dest_id, id_mat))
            db.commit()

    cursor.execute("SELECT heure_debut, heure_fin FROM portes WHERE statut_acces = 'CONFIG' LIMIT 1")
    conf = cursor.fetchone()
    horaires = {"debut": str(conf['heure_debut'])[:5] if conf else "08:00", "fin": str(conf['heure_fin'])[:5] if conf else "18:00"}
    cursor.execute("SELECT * FROM utilisateurs ORDER BY nom ASC")
    utilisateurs = cursor.fetchall()
    cursor.execute("SELECT m.*, u.nom as nom_user, u.prenom as prenom_user FROM materiel_stock m LEFT JOIN utilisateurs u ON m.id_utilisateur_actuel = u.id_utilisateur")
    materiels = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("IHM/admin.html", utilisateurs=utilisateurs, materiels=materiels, horaires=horaires, nom=session.get("nom"), prenom=session.get("prenom"))

#------------------
#prets
#-------------------
@app.route("/pret", methods=["GET", "POST"])
def pret():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    user_id = session["id_user"]

    # =========================
    # ACTIONS
    # =========================
    if request.method == "POST":
        action = request.form.get("action")

        # 🔵 FAIRE UNE DEMANDE
        if action == "demande":
            id_materiel = request.form["id_materiel"]
            id_destinataire = request.form["id_destinataire"]

            cursor.execute("""
                INSERT INTO prets (id_materiel, id_preteur, id_emprunteur)
                VALUES (%s,%s,%s)
            """, (id_materiel, user_id, id_destinataire))

            db.commit()

        # 🟢 ACCEPTER UNE DEMANDE
        elif action == "accepter":
            id_pret = request.form["id_pret"]

            # récupérer infos du prêt
            cursor.execute("""
                SELECT id_materiel, id_emprunteur
                FROM prets
                WHERE id_pret=%s
            """, (id_pret,))
            pret = cursor.fetchone()

            if pret:
                # transfert du matériel
                cursor.execute("""
                    UPDATE materiel_stock
                    SET id_utilisateur_actuel=%s,
                        etat='indisponible'
                    WHERE id_materiel=%s
                """, (pret["id_emprunteur"], pret["id_materiel"]))

                # mise à jour du prêt
                cursor.execute("""
                    UPDATE prets
                    SET statut='accepte',
                        date_validation=NOW()
                    WHERE id_pret=%s
                """, (id_pret,))

                db.commit()

        # 🔴 REFUSER UNE DEMANDE
        elif action == "refuser":
            id_pret = request.form["id_pret"]

            cursor.execute("""
                UPDATE prets
                SET statut='refuse',
                    date_validation=NOW()
                WHERE id_pret=%s
            """, (id_pret,))

            db.commit()

    # =========================
    # DATA
    # =========================

    # 📦 matériels que je possède
    cursor.execute("""
        SELECT id_materiel, nom_modele
        FROM materiel_stock
        WHERE id_utilisateur_actuel=%s
    """, (user_id,))
    mes_materiels = cursor.fetchall()

    # 👥 autres utilisateurs
    cursor.execute("""
        SELECT id_utilisateur, nom, prenom
        FROM utilisateurs
        WHERE id_utilisateur != %s
    """, (user_id,))
    utilisateurs = cursor.fetchall()

    # 📥 demandes reçues (moins de 1 mois)
    cursor.execute("""
        SELECT p.*, m.nom_modele, u.nom, u.prenom
        FROM prets p
        JOIN materiel_stock m ON p.id_materiel = m.id_materiel
        JOIN utilisateurs u ON p.id_preteur = u.id_utilisateur
        WHERE p.id_emprunteur=%s
        AND p.statut='en_attente'
        AND p.date_demande >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
    """, (user_id,))
    demandes_recues = cursor.fetchall()

    # 📤 demandes envoyées (moins de 1 mois)
    cursor.execute("""
        SELECT p.*, m.nom_modele, u.nom, u.prenom
        FROM prets p
        JOIN materiel_stock m ON p.id_materiel = m.id_materiel
        JOIN utilisateurs u ON p.id_emprunteur = u.id_utilisateur
        WHERE p.id_preteur=%s
        AND p.date_demande >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
        ORDER BY p.date_demande DESC
    """, (user_id,))
    demandes_envoyees = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "IHM/pret.html",
        mes_materiels=mes_materiels,
        utilisateurs=utilisateurs,
        demandes_recues=demandes_recues,
        demandes_envoyees=demandes_envoyees,
        nom=session["nom"],
        prenom=session["prenom"]
    )
#--------------------
#Profil
@app.route("/profil")
@app.route("/profil/<int:user_id>")
def profil(user_id=None):
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # LOGIQUE : Si user_id est dans l'URL, on prend celui-là. 
    # Sinon, on prend celui de la personne connectée (session).
    target_id = user_id if user_id is not None else session["id_user"]

    # 1. Infos de l'utilisateur cible (soit moi, soit un autre)
    cursor.execute("SELECT * FROM utilisateurs WHERE id_utilisateur = %s", (target_id,))
    user_info = cursor.fetchone()

    # Si l'utilisateur n'existe pas en BDD
    if not user_info:
        cursor.close()
        db.close()
        return "Utilisateur introuvable", 404

    # 2. Matériel possédé par cet utilisateur
    cursor.execute("""
        SELECT id_materiel, nom_modele, rfid_tag_epc, etat 
        FROM materiel_stock 
        WHERE id_utilisateur_actuel = %s
    """, (target_id,))
    materiels_possedes = cursor.fetchall()

    # 3. Réservations de cet utilisateur
    cursor.execute("""
        SELECT r.id_reservation, m.nom_modele, r.date_reservation, r.statut, r.date_limite
        FROM reservations r
        JOIN materiel_stock m ON r.id_materiel = m.id_materiel
        WHERE r.id_utilisateur = %s AND r.statut = 'confirmée'
    """, (target_id,))
    reservations = cursor.fetchall()

    cursor.close()
    db.close()

    # On renvoie la même page profil.html, mais avec les données de target_id
    return render_template("IHM/profil.html", 
                           u=user_info, 
                           possedes=materiels_possedes, 
                           reservations=reservations,
                           nom=session["nom"],      # Pour la top-bar
                           prenom=session["prenom"]) # Pour la top-bar

# -------------------------------
# LOGOUT
# -------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
#app.run(host="0.0.0.0", port=5000, ssl_context=("cert.pem", "key.pem"))

