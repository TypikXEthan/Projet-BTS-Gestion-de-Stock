from flask import Flask, render_template, request, redirect, session,flash,url_for,jsonify
import mysql.connector
import hashlib
from datetime import datetime, timedelta,date
import time
import json
from flask_socketio import SocketIO,emit

app = Flask(__name__)
app.secret_key = "cle_secrete_bts_rfid"  # clé de session
socketio = SocketIO(app, cors_allowed_origins="*")
session_scan ={}

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
#recherche
    recherche = request.args.get("recherche", "")
    params = []
    query = "SELECT * FROM materiel_stock"

    if recherche:
        query += " WHERE nom_modele LIKE %s OR rfid_tag_epc LIKE %s"
        params.extend([f"%{recherche}%", f"%{recherche}%"])
#pagination
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
#recuperer ce que l'utilisateur tape
    recherche = request.args.get('recherche', '').strip()

    db = get_db()
    cursor = db.cursor(dictionary=True)
#preparation requetes 
    sql = """
        SELECT m.id_mouvement, m.type_mouvement, m.date_heure,
               ms.nom_modele,
               u.nom, u.prenom
        FROM mouvements m
        LEFT JOIN materiel_stock ms ON m.id_materiel = ms.id_materiel
        LEFT JOIN utilisateurs u ON m.id_utilisateur = u.id_utilisateur
    """

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
#affichage classique si aucune requetes
        sql += " ORDER BY m.date_heure DESC"
        cursor.execute(sql)

    mouvements = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template(
        "IHM/historique.html",
        mouvements=mouvements,
        nom=session["nom"],
        prenom=session["prenom"],
        recherche=recherche 
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

    if request.method == "POST":
        action = request.form.get("action")

        if action == "reserver":
            id_mat = request.form.get("id_materiel")
            d_debut = request.form.get("date_reservation")
            d_fin = request.form.get("date_fin")

            # Verifie si il n'existe deja pas pour eviter les conflits 
            cursor.execute("""
                SELECT COUNT(*) as conflit FROM reservations 
                WHERE id_materiel = %s 
                AND statut IN ('Confirmée', 'Récupérée', 'Retard')
                AND NOT (date_limite < %s OR date_reservation > %s)
            """, (id_mat, d_debut, d_fin))
            
            res_conflit = cursor.fetchone()
            #mess erreur
            if res_conflit['conflit'] > 0:
                flash(f"Erreur : Le matériel ID {id_mat} est déjà réservé sur ces dates. Veuillez consulter la liste des réservations.", "danger")
            else:
                # ok alors envoye dans la bdd
                cursor.execute("""
                    INSERT INTO reservations (id_materiel, id_utilisateur, date_reservation, date_limite, statut)
                    VALUES (%s, %s, %s, %s, 'Confirmée')
                """, (id_mat, user_id, d_debut, d_fin))
                db.commit()
                flash("✅ Réservation validée avec succès !", "success")

        return redirect(url_for('reservations'))

    cursor.execute("SELECT id_materiel, nom_modele FROM materiel_stock WHERE actif=1 AND reservable=1")
    materiels = cursor.fetchall()

    cursor.execute("""
        SELECT r.*, ms.nom_modele FROM reservations r
        JOIN materiel_stock ms ON r.id_materiel = ms.id_materiel
        WHERE r.id_utilisateur = %s 
        ORDER BY r.date_reservation DESC
    """, (user_id,))
    mes_res = cursor.fetchall()

    for r in mes_res:
        if isinstance(r['date_limite'], datetime):
            r['date_limite'] = r['date_limite'].date()
        if isinstance(r['date_reservation'], datetime):
            r['date_reservation'] = r['date_reservation'].date()

    db.close()
    return render_template("IHM/reservations.html", 
                           materiels=materiels, 
                           mes_reservations=mes_res,
                           aujourdhui=date.today(),
                           prenom=session.get("prenom"),
                           nom=session.get("nom"))



#-----------------
#Administration
#-----------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Verifie que l'utilsateur est bien admin=1 dans labdd 
    if "id_user" not in session or session.get("admin") != 1:
        flash("Accès réservé aux administrateurs.", "danger")
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        #Horraire access modifier
        if action == "modifier_horaires_globaux":
            h_debut = request.form.get("h_debut")
            h_fin = request.form.get("h_fin")
            cursor.execute("UPDATE portes SET heure_debut = %s, heure_fin = %s", (h_debut, h_fin))
            db.commit()
            flash("Horaires de passage mis à jour avec succès.", "success")

        # Creer utilisateur
        elif action == "creer_utilisateur":
            nom = request.form.get("nom")
            prenom = request.form.get("prenom")
            login_user = request.form.get("utilisateur")
            mdp_clair = request.form.get("mot_de_passe")
            badge_clair = request.form.get("badge_uid")
            email = request.form.get("email")
            tel = request.form.get("telephone")
            role = request.form.get("role")
            admin_status = request.form.get("admin_status")

            # Hachage du mot de passe et du badge
            mdp_hash = hashlib.sha256(mdp_clair.encode()).hexdigest()
            badge_hash = hashlib.sha256(badge_clair.encode()).hexdigest() if badge_clair else None

            try:
                cursor.execute("""
                    INSERT INTO utilisateurs (utilisateur, mot_de_passe, badge_uid, nom, prenom, email, telephone, role, admin) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (login_user, mdp_hash, badge_hash, nom, prenom, email, tel, role, admin_status))
                db.commit()
                flash(f"L'utilisateur {prenom} {nom} a été créé.", "success")
            except mysql.connector.Error as err:
                flash(f"Erreur lors de la création : {err}", "danger")

        #Modifier un utilisateur
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
                m_hash = hashlib.sha256(nouveau_mdp.encode()).hexdigest()
                cursor.execute("UPDATE utilisateurs SET mot_de_passe=%s WHERE id_utilisateur=%s", (m_hash, id_u))
                
            db.commit()
            flash("Profil utilisateur mis à jour.", "info")

        # SUPPRIMER UN UTILISATEUR 
        elif action == "supprimer_utilisateur":
            id_u = request.form.get("id_utilisateur")
            if int(id_u) == session.get('id_user'):
                flash("Vous ne pouvez pas supprimer votre propre compte admin !", "danger")
            else:
                cursor.execute("DELETE FROM utilisateurs WHERE id_utilisateur = %s", (id_u,))
                db.commit()
                flash("Utilisateur supprimé définitivement.", "warning")

        # AJOUT MATÉRIEL
        elif action == "ajouter_materiel":
            id_inv = request.form.get("id_inventaire")
            nom_m = request.form.get("nom_modele")
            tag_r = request.form.get("rfid_tag")
            etat_m = request.form.get("etat")
            
            cursor.execute("""
                INSERT INTO materiel_stock (id_materiel, nom_modele, rfid_tag_epc, etat, actif, reservable) 
                VALUES (%s, %s, %s, %s, 1, 1)
            """, (id_inv, nom_m, tag_r, etat_m))
            db.commit()
            flash("Nouveau matériel ajouté au stock.", "success")

        #MODIF MATÉRIEL
        elif action == "modifier_materiel_complet":
            id_m = request.form.get("id_materiel")
            u_actuel = request.form.get("id_utilisateur_actuel")
            # Si u_actuel est vide, on met NULL en BDD
            u_actuel = u_actuel if u_actuel != "" else None
            
            cursor.execute("""
                UPDATE materiel_stock 
                SET nom_modele=%s, rfid_tag_epc=%s, etat=%s, id_utilisateur_actuel=%s 
                WHERE id_materiel=%s
            """, (request.form.get("nom_modele"), request.form.get("rfid_tag_epc"), 
                  request.form.get("nouveau_statut"), u_actuel, id_m))
            db.commit()
            flash("Fiche matériel mise à jour.", "info")

        return redirect(url_for('admin'))
    
    # Horaires
    cursor.execute("SELECT heure_debut as debut, heure_fin as fin FROM portes LIMIT 1")
    horaires = cursor.fetchone()
    if not horaires: horaires = {'debut': '08:00', 'fin': '18:00'}

    # Liste utilisateurs
    cursor.execute("SELECT * FROM utilisateurs ORDER BY nom ASC")
    utilisateurs_list = cursor.fetchall()

    # Liste matériels
    cursor.execute("SELECT * FROM materiel_stock ORDER BY id_materiel ASC")
    materiels_list = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "IHM/admin.html",
        horaires=horaires,
        utilisateurs=utilisateurs_list,
        materiels=materiels_list,
        prenom=session.get("prenom"),
        nom=session.get("nom")
    )
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

        # ACCEPTER UNE DEMANDE
        elif action == "accepter":
            id_pret = request.form["id_pret"]

            cursor.execute("""
                SELECT id_materiel, id_emprunteur
                FROM prets
                WHERE id_pret=%s
            """, (id_pret,))
            pret = cursor.fetchone()

            if pret:
                cursor.execute("""
                    UPDATE materiel_stock
                    SET id_utilisateur_actuel=%s,
                        etat='indisponible'
                    WHERE id_materiel=%s
                """, (pret["id_emprunteur"], pret["id_materiel"]))

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

    cursor.execute("""
        SELECT id_materiel, nom_modele
        FROM materiel_stock
        WHERE id_utilisateur_actuel=%s
    """, (user_id,))
    mes_materiels = cursor.fetchall()

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
#--------------------
@app.route("/profil", methods=["GET", "POST"])
@app.route("/profil/<int:user_id>", methods=["GET", "POST"])
def profil(user_id=None):
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)
    target_id = user_id if user_id is not None else session["id_user"]

    # --- PARTIE MODIFICATION (POST) ---
    if request.method == "POST":
        email = request.form.get("email")
        tel = request.form.get("telephone")
        nouveau_mdp = request.form.get("nouveau_mdp")

        # Mise à jour des infos de base
        cursor.execute("""
            UPDATE utilisateurs 
            SET email = %s, telephone = %s 
            WHERE id_utilisateur = %s
        """, (email, tel, target_id))

        # Mise à jour du mot de passe si rempli
        if nouveau_mdp and nouveau_mdp.strip() != "":
            import hashlib
            h_mdp = hashlib.sha256(nouveau_mdp.encode()).hexdigest()
            cursor.execute("UPDATE utilisateurs SET mot_de_passe = %s WHERE id_utilisateur = %s", (h_mdp, target_id))
        
        db.commit()
        flash("Profil mis à jour avec succès !", "success")
        return redirect(url_for('profil', user_id=user_id))

    # --- PARTIE AFFICHAGE (GET) ---
    cursor.execute("SELECT * FROM utilisateurs WHERE id_utilisateur = %s", (target_id,))
    user_info = cursor.fetchone()

    if not user_info:
        return "Utilisateur introuvable", 404

    cursor.execute("SELECT id_materiel, nom_modele, rfid_tag_epc, etat FROM materiel_stock WHERE id_utilisateur_actuel = %s", (target_id,))
    materiels_possedes = cursor.fetchall()

    cursor.execute("""
        SELECT r.id_reservation, m.nom_modele, r.date_reservation, r.statut, r.date_limite
        FROM reservations r
        JOIN materiel_stock m ON r.id_materiel = m.id_materiel
        WHERE r.id_utilisateur = %s AND r.statut = 'confirmée'
    """, (target_id,))
    reservations = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("IHM/profil.html", u=user_info, possedes=materiels_possedes, reservations=reservations, nom=session["nom"], prenom=session["prenom"])



#--------------
#HISTORIQUE ACCEES
#----------------
@app.route('/historique_acces')
def historique_access_page():
    if 'id_user' not in session:
        return redirect(url_for('login'))

    # 1. Récupération de la recherche
    recherche = request.args.get('recherche', '').strip()

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 2. Construction de la requête SQL avec filtres
    # On utilise des LEFT JOIN pour ne pas perdre les "Inconnus" (id_utilisateur IS NULL)
    sql = """
        SELECT h.*, u.nom, u.prenom 
        FROM historique_acces h
        LEFT JOIN utilisateurs u ON h.id_utilisateur = u.id_utilisateur
    """

    params = []
    if recherche:
        sql += """ 
            WHERE u.nom LIKE %s 
            OR u.prenom LIKE %s 
            OR h.id_porte_physique LIKE %s 
            OR h.statut_acces LIKE %s
        """
        search_val = f"%{recherche}%"
        params = [search_val, search_val, search_val, search_val]

    # 3. Tri par les plus récents
    sql += " ORDER BY h.date_acces DESC, h.heure_acces DESC LIMIT 100"
    
    cursor.execute(sql, params)
    logs = cursor.fetchall()
    
    cursor.close()
    db.close()

    return render_template(
        'IHM/historique_acces.html', 
        logs=logs, 
        nom=session.get("nom"), 
        prenom=session.get("prenom"),
        recherche=recherche  # On renvoie la recherche pour qu'elle reste dans l'input
    )

@app.route("/reservation_materiel_liste/<int:id_mat>")
def reservation_materiel_liste(id_mat):
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 1. Récupérer les infos du matériel cliqué
    cursor.execute("SELECT * FROM materiel_stock WHERE id_materiel = %s", (id_mat,))
    materiel = cursor.fetchone()

    if not materiel:
        flash("Matériel introuvable", "danger")
        return redirect("/materiels")

    # 2. Récupérer les réservations en cours et futures pour ce matériel
    # On fait une jointure pour savoir QUI a réservé
    cursor.execute("""
        SELECT r.*, u.nom, u.prenom 
        FROM reservations r
        JOIN utilisateurs u ON r.id_utilisateur = u.id_utilisateur
        WHERE r.id_materiel = %s 
        AND r.statut IN ('Confirmée', 'Récupérée', 'Retard')
        ORDER BY r.date_reservation ASC
    """, (id_mat,))
    reservations_futures = cursor.fetchall()

    db.close()
    
    return render_template(
        "IHM/reservation_materiel_liste.html",
        materiel=materiel,
        reservations=reservations_futures,
        aujourdhui=date.today(),
        prenom=session["prenom"],
        nom=session["nom"]
    )
#----------------------------
#######TABLETTE##############
#----------------------------
@app.route("/tablette")
def ecran_accueil():
    return render_template("Ecran/accueil.html")

@app.route('/verifier_acces', methods=['POST'])
def verifier_acces():
    data = request.json
    badge_uid = str(data.get('badge_uid')).strip()
    
    # 1. Préparation des infos de date/heure pour la BDD
    maintenant = datetime.now()
    date_j = maintenant.date()
    heure_j = maintenant.strftime("%H:%M:%S")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # 2. Vérification de l'utilisateur
        cursor.execute("SELECT id_utilisateur, nom, prenom FROM utilisateurs WHERE badge_uid = %s", (badge_uid,))
        user = cursor.fetchone()

        if user:
            # ✅ ACCÈS AUTORISÉ
            # Enregistrement en BDD
            cursor.execute("""
                INSERT INTO historique_acces (id_utilisateur, id_porte_physique, date_acces, heure_acces, statut_acces)
                VALUES (%s, %s, %s, %s, %s)
            """, (user['id_utilisateur'], "PORTE_PRINCIPALE", date_j, heure_j, "Autorisé"))
            db.commit()

            # --- ENVOI DES INFOS À LA TABLETTE ---
            # IMPORTANT : On ajoute 'redirect' pour éviter le "undefined"
            socketio.emit('resultat_badge', {
                'status': 'vert',
                'nom': user['nom'],
                'prenom': user['prenom'],
                'redirect': '/tablette/flux_materiel'  # C'est cette ligne qui manquait !
            })
            
            return jsonify({"status": "autorise"}), 200

        else:
            # ❌ ACCÈS REFUSÉ (Badge inconnu)
            cursor.execute("""
                INSERT INTO historique_acces (id_utilisateur, id_porte_physique, date_acces, heure_acces, statut_acces)
                VALUES (NULL, %s, %s, %s, %s)
            """, ("PORTE_PRINCIPALE", date_j, heure_j, "Refusé - Inconnu"))
            db.commit()

            # Signal rouge à la tablette
            socketio.emit('resultat_badge', {
                'status': 'rouge'
            })
            
            return jsonify({"status": "refuse"}), 403

    except Exception as e:
        print(f"Erreur Serveur: {e}")
        return jsonify({"status": "erreur"}), 500
    finally:
        cursor.close()
        db.close()

@app.route("/tablette/flux_materiel")
def flux_materiel():
    return render_template("Ecran/flux_materiel.html")

@app.route("/scan_objet", methods=['POST'])
def scan_objet():
    global session_scan
    data = request.json
    tag_epc = data.get('rfid_tag_epc')
    
    if not tag_epc:
        return jsonify({"status": "error", "message": "Tag manquant"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_materiel, nom_modele, etat FROM materiel_stock WHERE rfid_tag_epc = %s", (tag_epc,))
        item = cursor.fetchone()
        
        if item:
            # Si l'objet est déjà dans la liste temporaire, on bascule son état prévu
            if tag_epc in session_scan:
                nouveau = "Disponible" if session_scan[tag_epc]['etat'] == "Sortie" else "Sortie"
                session_scan[tag_epc]['etat'] = nouveau
            else:
                # Sinon, on regarde son état actuel en BDD pour proposer l'inverse
                etat_actuel = str(item['etat']).strip().capitalize()
                nouveau = "Sortie" if etat_actuel == "Disponible" else "Disponible"
                session_scan[tag_epc] = {
                    'id': item['id_materiel'],
                    'nom': item['nom_modele'],
                    'etat': nouveau
                }
            
            # Envoi à la tablette via SocketIO (on utilise tag_epc comme ID pour le DOM)
            socketio.emit('mouvement_stock', {
                'id': tag_epc,
                'nom': item['nom_modele'],
                'etat': session_scan[tag_epc]['etat']
            })
            return jsonify({"status": "ok"}), 200
            
        return jsonify({"status": "not_found"}), 404
    finally:
        cursor.close()
        db.close()


@app.route("/supprimer_de_session", methods=['POST'])
def supprimer_de_session():
    global session_scan
    tag_epc = request.json.get('rfid_tag_epc')
    if tag_epc in session_scan:
        del session_scan[tag_epc]
    return jsonify({"status": "ok"})

@app.route("/valider_session_finale", methods=['POST'])
def valider_session_finale():
    global session_scan
    data = request.json
    user_login = data.get('user')
    password = data.get('password')
    tags_selectionnes = data.get('tags', [])

    # --- MODIFICATION ICI : Autoriser la fermeture si rien n'est scanné ---
    if not tags_selectionnes:
        session_scan = {} # On vide la session temporaire
        return jsonify({"status": "ok", "message": "Session fermée sans mouvement"})
    # ---------------------------------------------------------------------

    # Si il y a des tags, on vérifie l'identité normalement
    mdp_hash = hashlib.sha256(password.encode()).hexdigest()
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # 1. Vérification de l'utilisateur qui valide
        cursor.execute("SELECT id_utilisateur FROM utilisateurs WHERE utilisateur=%s AND mot_de_passe=%s", (user_login, mdp_hash))
        valideur = cursor.fetchone()
        
        if not valideur:
            return jsonify({"status": "error", "message": "Identifiants incorrects"}), 403

        id_u = valideur['id_utilisateur']

        # 2. Traitement de chaque matériel choisi
        for tag in tags_selectionnes:
            if tag in session_scan:
                infos = session_scan[tag]
                nouvel_utilisateur = None if infos['etat'] == "Disponible" else id_u

                query = """
                    UPDATE materiel_stock 
                    SET etat = %s, id_utilisateur_actuel = %s 
                    WHERE rfid_tag_epc = %s
                """
                cursor.execute(query, (infos['etat'], nouvel_utilisateur, tag))

                cursor.execute("""
                    INSERT INTO mouvements (id_materiel, id_utilisateur, type_mouvement, date_heure)
                    VALUES (%s, %s, %s, NOW())
                """, (infos['id'], id_u, "Entrée" if infos['etat'] == "Disponible" else "Sortie"))

        db.commit()
        session_scan = {} # Reset la session de scan
        return jsonify({"status": "ok"})

    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        db.close()

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
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
