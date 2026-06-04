from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import mysql.connector
import hashlib
from datetime import datetime, timedelta, date
import time
import json
from flask_socketio import SocketIO, emit
import uuid
import os 
from dotenv import load_dotenv 
import re
from flask_mail import Mail, Message  
from flask_apscheduler import APScheduler

# Charger les variables du fichier .env
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION FLASK-MAIL ---
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

# --- CONFIGURATION SCHEDULER (AUTOMATISATION) ---
app.config['SCHEDULER_API_ENABLED'] = True
scheduler = APScheduler()

def verifier_retards_automatique():
    with app.app_context():
        maintenant = datetime.now()
        print(f"[{maintenant}] 🔍 Scan automatique des retards...")
        
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)

            # 1. Sélectionner les réservations dépassées
            query = """
                SELECT r.id_reservation, u.email, u.prenom, m.nom_modele, r.date_limite
                FROM reservations r
                JOIN utilisateurs u ON r.id_utilisateur = u.id_utilisateur
                JOIN materiel_stock m ON r.id_materiel = m.id_materiel
                WHERE r.date_limite < NOW() 
                AND r.statut IN ('Confirmée', 'Récupérée')
            """
            cursor.execute(query)
            retards = cursor.fetchall()
            
            print(f"🔹 Nombre de retards détectés : {len(retards)}")

            for r in retards:
                destinataire = r['email']
                id_res = r['id_reservation']
                
                # 2. Mise à jour du statut en BDD
                cursor.execute("UPDATE reservations SET statut = 'Retard' WHERE id_reservation = %s", (id_res,))
                db.commit() 
                
                # 3. Envoi de l'email avec sécurité
                if destinataire:
                    try:
                        msg = Message(
                            subject="[ALERTE AUTOMATIQUE] Retard de restitution matériel",
                            recipients=[destinataire],
                            body=f"Bonjour {r['prenom']},\n\nLe système a détecté un retard pour : {r['nom_modele']}.\nLa date limite était le : {r['date_limite']}.\n\nMerci de rapporter ce matériel rapidement.\n\nCordialement."
                        )
                        mail.send(msg)
                        print(f"📧 Email envoyé avec succès à : {destinataire}")
                    except Exception as mail_err:
                        print(f"⚠️ Erreur lors de l'envoi à {destinataire} : {mail_err}")
                        
        except Exception as e:
            print(f"❌ Erreur lors du scan des retards : {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

# --- INITIALISATION PLANIFICATEUR ---
scheduler.init_app(app)

# On récupère la clé du .env ou on met une valeur de secours
app.secret_key = os.getenv('SECRET_KEY', 'cle_par_defaut_pas_secure')

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
session_scan = {}

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# Garde la session active 60 minutes
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)

def est_mdp_valide(mdp):
    # Minimum 10 caractères, au moins un caractère spécial
    if len(mdp) < 10:
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", mdp):
        return False
    return True

##### LOGIN #####
@app.route("/", methods=["GET", "POST"])
def login():
    # Gestion du blocage après trop de tentatives
    if "bloque_jusqua" in session:
        temps_restant = int(session["bloque_jusqua"] - time.time())
        if temps_restant > 0:
            return render_template("IHM/login.html", erreur=f"Bloqué. Attendez {temps_restant}s.", attente=temps_restant)
        else:
            session.pop("bloque_jusqua", None)
            session["tentatives"] = 0

    if request.method == "POST":
        utilisateur = request.form["utilisateur"]
        mot_de_passe = request.form["mot_de_passe"]

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # On cherche l'utilisateur par son nom uniquement
        cursor.execute("SELECT * FROM utilisateurs WHERE utilisateur=%s", (utilisateur,))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            # On récupère le sel stocké en BDD
            user_salt = user.get('salt')
            
            # SECURITÉ : On vérifie si l'utilisateur a bien un Salt en BDD
            # Cela évite l'erreur "TypeError: can only concatenate str (not NoneType)"
            if user_salt:
                # Calcul du hash avec le Salt (Nouvelle méthode)
                hash_test = hashlib.sha256((mot_de_passe + user_salt).encode()).hexdigest()
            else:
                # Ancienne méthode si le Salt n'existe pas encore pour cet utilisateur
                hash_test = hashlib.sha256(mot_de_passe.encode()).hexdigest()

            # Comparaison du hash calculé avec celui de la BDD
            if user["mot_de_passe"] == hash_test:
                session.update({
                    "id_user": user["id_utilisateur"], 
                    "utilisateur": user["utilisateur"],
                    "nom": user["nom"], 
                    "prenom": user["prenom"],
                    "role": user["role"], 
                    "admin": user["admin"]
                })
                session.pop("tentatives", None)
                return redirect("/dashboard")

        # Échec de connexion : incrémentation du compteur
        session["tentatives"] = session.get("tentatives", 0) + 1
        
        if session["tentatives"] >= 3:
            # Blocage de 90 secondes après 3 échecs
            session["bloque_jusqua"] = time.time() + 90
            return render_template("IHM/login.html", erreur="Compte bloqué (90s)", attente=90)

        return render_template("IHM/login.html", erreur=f"Identifiants incorrects ({session['tentatives']}/3)")

    return render_template("IHM/login.html")

# -------------------------------
# DASHBOARD
#-------------------------------
@app.route("/dashboard")
def dashboard():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)
    id_u = session["id_user"]

    # 1. Stats globales
    cursor.execute("SELECT COUNT(*) AS total FROM materiel_stock WHERE etat = 'Disponible'")
    nb_stock = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM materiel_stock WHERE etat = 'Sortie'")
    nb_sorti = cursor.fetchone()["total"]

    # 2. Retards (déjà existant)
    cursor.execute("""
        SELECT r.id_materiel, ms.nom_modele, r.date_limite
        FROM reservations r
        JOIN materiel_stock ms ON r.id_materiel = ms.id_materiel
        WHERE r.id_utilisateur = %s AND r.statut = 'Retard'
    """, (id_u,))
    mes_retards = cursor.fetchall()

    # 3. NOUVEAU : Mes matériels actuels + Alertes de réservations futures
    cursor.execute("""
        SELECT ms.id_materiel, ms.nom_modele, 
               (SELECT r.date_reservation 
                FROM reservations r 
                WHERE r.id_materiel = ms.id_materiel 
                AND r.statut = 'Confirmée' 
                AND r.date_reservation > NOW() 
                ORDER BY r.date_reservation ASC LIMIT 1) as date_prochaine_resa,
               (SELECT u.utilisateur 
                FROM reservations r 
                JOIN utilisateurs u ON r.id_utilisateur = u.id_utilisateur
                WHERE r.id_materiel = ms.id_materiel 
                AND r.statut = 'Confirmée' 
                AND r.date_reservation > NOW() 
                ORDER BY r.date_reservation ASC LIMIT 1) as nom_prochain_user
        FROM materiel_stock ms
        WHERE ms.id_utilisateur_actuel = %s
    """, (id_u,))
    mes_emprunts = cursor.fetchall()

    # 4. Derniers mouvements
    cursor.execute("""
        SELECT m.type_mouvement, m.date_heure, ms.nom_modele, u.nom, u.prenom
        FROM mouvements m
        JOIN materiel_stock ms ON m.id_materiel = ms.id_materiel
        JOIN utilisateurs u ON m.id_utilisateur = u.id_utilisateur
        ORDER BY m.date_heure DESC LIMIT 10
    """)
    mouvements = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "IHM/dashboard.html",
        nb_stock=nb_stock,
        nb_sorti=nb_sorti,
        mouvements=mouvements,
        mes_retards=mes_retards,
        mes_emprunts=mes_emprunts, # <--- Ajouté
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

    recherche = request.args.get("recherche", "").strip()
    params = []
    query = "SELECT * FROM materiel_stock"
    total_query = "SELECT COUNT(*) AS total FROM materiel_stock"

    if recherche:
        # Recherche par modèle, tag RFID ou ID Matériel exact
        condition = " WHERE nom_modele LIKE %s OR rfid_tag_epc LIKE %s OR id_materiel = %s"
        query += condition
        total_query += condition
        # Si la recherche n'est pas un nombre, on passe 0 pour l'id_materiel pour éviter un plantage SQL
        id_recherche = recherche if recherche.isdigit() else 0
        params.extend([f"%{recherche}%", f"%{recherche}%", id_recherche])

    # --- PAGINATION ---
    page = int(request.args.get("page", 1))
    limit = 10
    offset = (page - 1) * limit

    cursor.execute(total_query, params)
    total_rows = cursor.fetchone()["total"]
    total_pages = (total_rows + limit - 1) // limit

    query += " LIMIT %s OFFSET %s"
    cursor.execute(query, params + [limit, offset])
    materiels = cursor.fetchall()

    cursor.close()
    db.close()

    # Double injection (page et page_actuelle) pour parer toute erreur Jinja2
    return render_template(
        "IHM/materiels.html",
        materiels=materiels,
        page=page,
        page_actuelle=page,
        total_pages=total_pages,
        total_elements=total_rows,
        recherche=recherche,
        prenom=session["prenom"],
        nom=session["nom"]
    )


# --------------------------
# 2. HISTORIQUE MATÉRIELS
# ---------------------------
@app.route("/historique")
def historique():
    if "id_user" not in session:
        return redirect("/")
    
    recherche = request.args.get('recherche', '').strip()

    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    sql = """
        SELECT m.id_mouvement, m.id_materiel, m.type_mouvement, m.date_heure,
               ms.nom_modele, u.nom, u.prenom
        FROM mouvements m
        LEFT JOIN materiel_stock ms ON m.id_materiel = ms.id_materiel
        LEFT JOIN utilisateurs u ON m.id_utilisateur = u.id_utilisateur
    """
    
    total_sql = """
        SELECT COUNT(*) AS total 
        FROM mouvements m
        LEFT JOIN materiel_stock ms ON m.id_materiel = ms.id_materiel
        LEFT JOIN utilisateurs u ON m.id_utilisateur = u.id_utilisateur
    """

    params = []
    if recherche:
        # Recherche par modèle, nom, prénom, type, ID matériel ou ID utilisateur
        condition = """ 
            WHERE ms.nom_modele LIKE %s 
            OR u.nom LIKE %s 
            OR u.prenom LIKE %s 
            OR m.type_mouvement LIKE %s
            OR m.id_materiel = %s
            OR m.id_utilisateur = %s
        """
        sql += condition
        total_sql += condition
        id_recherche = recherche if recherche.isdigit() else 0
        params = [f"%{recherche}%", f"%{recherche}%", f"%{recherche}%", f"%{recherche}%", id_recherche, id_recherche]

    # --- PAGINATION ---
    page = int(request.args.get("page", 1))
    limit = 10
    offset = (page - 1) * limit

    cursor.execute(total_sql, params)
    total_rows = cursor.fetchone()["total"]
    total_pages = (total_rows + limit - 1) // limit

    sql += " ORDER BY m.date_heure DESC LIMIT %s OFFSET %s"
    cursor.execute(sql, params + [limit, offset])
    mouvements = cursor.fetchall()
    
    cursor.close()
    db.close()

    return render_template(
        "IHM/historique.html",
        mouvements=mouvements,
        page=page,
        page_actuelle=page,
        total_pages=total_pages,
        total_elements=total_rows,
        nom=session["nom"],
        prenom=session["prenom"],
        recherche=recherche 
    )

# --------------
# 3. HISTORIQUE ACCES
# ----------------
@app.route('/historique_acces')
def historique_access_page():
    if 'id_user' not in session:
        return redirect(url_for('login'))

    recherche = request.args.get('recherche', '').strip()
    db = get_db()
    cursor = db.cursor(dictionary=True)

    sql = """
        SELECT h.*, u.nom, u.prenom 
        FROM historique_acces h
        LEFT JOIN utilisateurs u ON h.id_utilisateur = u.id_utilisateur
    """
    
    total_sql = """
        SELECT COUNT(*) AS total 
        FROM historique_acces h
        LEFT JOIN utilisateurs u ON h.id_utilisateur = u.id_utilisateur
    """

    params = []
    if recherche:
        condition = """ 
            WHERE u.nom LIKE %s 
            OR u.prenom LIKE %s 
            OR h.statut_acces LIKE %s
        """
        sql += condition
        total_sql += condition
        search_val = f"%{recherche}%"
        params = [search_val, search_val, search_val]

    # --- PAGINATION ---
    page = int(request.args.get("page", 1))
    limit = 10
    offset = (page - 1) * limit

    cursor.execute(total_sql, params)
    total_rows = cursor.fetchone()["total"]
    total_pages = (total_rows + limit - 1) // limit

    sql += " ORDER BY h.date_acces DESC, h.heure_acces DESC LIMIT %s OFFSET %s"
    cursor.execute(sql, params + [limit, offset])
    logs = cursor.fetchall()

    for log in logs:
        if log['statut_acces']:
            log['statut_clean'] = log['statut_acces'].strip().upper()
        else:
            log['statut_clean'] = ""
    
    cursor.close()
    db.close()

    return render_template(
        'IHM/historique_acces.html', 
        logs=logs, 
        page=page,  # Variable uniforme 'page'
        total_pages=total_pages,
        total_elements=total_rows,
        nom=session.get("nom"), 
        prenom=session.get("prenom"),
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



@app.route("/voir_profil_public/<int:id_user_vise>")
def voir_profil_public(id_user_vise):
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 1. Récupérer les informations de base de l'utilisateur visé
    cursor.execute("""
        SELECT nom, prenom, email, telephone, role 
        FROM utilisateurs 
        WHERE id_utilisateur = %s
    """, (id_user_vise,))
    user_vise = cursor.fetchone()

    if not user_vise:
        cursor.close()
        db.close()
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for('utilisateurs'))

    # 2. Récupérer le matériel actuellement en possession de cet utilisateur
    cursor.execute("""
        SELECT nom_modele, rfid_tag_epc 
        FROM materiel_stock 
        WHERE id_utilisateur_actuel = %s
    """, (id_user_vise,))
    materiels = cursor.fetchall()

    # 3. Récupérer les réservations à venir pour cet utilisateur
    cursor.execute("""
        SELECT m.nom_modele, r.date_reservation 
        FROM reservations r
        JOIN materiel_stock m ON r.id_materiel = m.id_materiel
        WHERE r.id_utilisateur = %s AND r.statut IN ('Confirmée', 'En attente')
        ORDER BY r.date_reservation ASC
    """, (id_user_vise,))
    reservations = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("IHM/profil_publique.html", 
                           u=user_vise, 
                           materiels=materiels, 
                           reservations=reservations,
                           nom=session["nom"], 
                           prenom=session["prenom"])


# -------------------------------
# RESERVATIONS
# -------------------------------
@app.route("/reservations", methods=["GET", "POST"])
def reservations():
    # 1. Sécurité session
    if "id_user" not in session:
        return redirect(url_for("login"))

    db = get_db() 
    cursor = db.cursor(dictionary=True)
    
    id_u = session["id_user"]
    aujourdhui = date.today()
    un_mois_en_arriere = aujourdhui - timedelta(days=30)

    # 2. Gestion des actions (Réservation / Annulation)
    if request.method == "POST":
        action = request.form.get("action")

        if action == "reserver":
            id_m = request.form.get("id_materiel")
            d_res = request.form.get("date_reservation")
            d_fin = request.form.get("date_fin")

            # Vérification de l'état réel du matériel
            cursor.execute("SELECT etat FROM materiel_stock WHERE id_materiel = %s", (id_m,))
            materiel = cursor.fetchone()

            if materiel and materiel['etat'].strip().lower() != 'disponible':
                flash(f"Erreur : Ce matériel est actuellement {materiel['etat']} et ne peut être réservé.", "danger")
            else:
                # Vérification si une réservation active existe déjà sur ces dates
                cursor.execute("""
                    SELECT * FROM reservations 
                    WHERE id_materiel = %s 
                    AND statut IN ('Confirmée', 'Récupérée', 'Retard')
                    AND NOT (date_limite < %s OR date_reservation > %s)
                """, (id_m, d_res, d_fin))
                
                if cursor.fetchone():
                    flash("Erreur : Ce créneau est déjà réservé par un autre utilisateur.", "danger")
                else:
                    cursor.execute("""
                        INSERT INTO reservations (id_utilisateur, id_materiel, date_reservation, date_limite, statut)
                        VALUES (%s, %s, %s, %s, 'Confirmée')
                    """, (id_u, id_m, d_res, d_fin))
                    db.commit()
                    flash("Réservation effectuée avec succès !", "success")

        elif action == "annuler":
            id_res = request.form.get("id_reservation")
            cursor.execute("UPDATE reservations SET statut = 'Annulée' WHERE id_reservation = %s", (id_res,))
            db.commit()
            flash("Réservation annulée.", "success")

    # 3. Récupération des matériels pour le menu déroulant
    cursor.execute("SELECT id_materiel, nom_modele, etat FROM materiel_stock")
    liste_materiels = cursor.fetchall()

    # 4. Récupération UNIQUEMENT des réservations actives de moins d'un mois
    cursor.execute("""
        SELECT r.*, m.nom_modele 
        FROM reservations r 
        JOIN materiel_stock m ON r.id_materiel = m.id_materiel 
        WHERE r.id_utilisateur = %s 
        AND r.statut IN ('Confirmée', 'Récupérée', 'Retard')
        AND r.date_reservation >= %s
        ORDER BY r.date_reservation DESC
    """, (id_u, un_mois_en_arriere))
    mes_res = cursor.fetchall()

    # Conversion des dates pour éviter les plantages de template
    for r in mes_res:
        if isinstance(r['date_limite'], datetime):
            r['date_limite'] = r['date_limite'].date()
        if isinstance(r['date_reservation'], datetime):
            r['date_reservation'] = r['date_reservation'].date()

    cursor.close()
    db.close()
    
    return render_template("IHM/reservations.html", 
                           materiels=liste_materiels, 
                           mes_reservations=mes_res,
                           aujourdhui=aujourdhui,
                           date_min=aujourdhui.strftime('%Y-%m-%d'),
                           prenom=session.get("prenom"),
                           nom=session.get("nom"))


@app.route("/all_reservations")
def all_reservations():
    """Affiche TOUTES les réservations avec barre de recherche et pagination."""
    if "id_user" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    id_u = session["id_user"]
    aujourdhui = date.today()

    # 1. Récupération des paramètres de recherche et pagination
    recherche = request.args.get('search', '').strip()
    try:
        page = int(request.args.get('page', 1))
        if page < 1: page = 1
    except ValueError:
        page = 1

    elements_par_page = 10
    offset = (page - 1) * elements_par_page

    # 2. Construction de la requête SQL avec filtres dynamiques
    # On cherche par ID de réservation, nom du modèle ou correspondances sur les dates
    query_base = """
        FROM reservations r 
        JOIN materiel_stock m ON r.id_materiel = m.id_materiel 
        WHERE r.id_utilisateur = %s
    """
    params = [id_u]

    if recherche:
        query_base += """ AND (
            CAST(r.id_reservation AS CHAR) LIKE %s 
            OR m.nom_modele LIKE %s 
            OR DATE_FORMAT(r.date_reservation, '%%d/%%m/%%Y') LIKE %s
            OR DATE_FORMAT(r.date_limite, '%%d/%%m/%%Y') LIKE %s
            OR DATE_FORMAT(r.date_reservation, '%%Y-%%m-%%d') LIKE %s
            OR DATE_FORMAT(r.date_limite, '%%Y-%%m-%%d') LIKE %s
        )"""
        terme_recherche = f"%{recherche}%"
        params.extend([terme_recherche, terme_recherche, terme_recherche, terme_recherche, terme_recherche, terme_recherche])

    # 3. Compter le nombre total de lignes pour la pagination
    cursor.execute(f"SELECT COUNT(*) as total {query_base}", tuple(params))
    total_elements = cursor.fetchone()['total']
    total_pages = (total_elements + elements_par_page - 1) // elements_par_page

    # 4. Récupérer les données limitées pour la page actuelle
    query_data = f"""
        SELECT r.*, m.nom_modele 
        {query_base}
        ORDER BY r.date_reservation DESC
        LIMIT %s OFFSET %s
    """
    params_data = list(params)
    params_data.extend([elements_par_page, offset])
    
    cursor.execute(query_data, tuple(params_data))
    toutes_les_res = cursor.fetchall()

    # Nettoyage des dates pour le rendu HTML
    for r in toutes_les_res:
        if isinstance(r['date_limite'], datetime):
            r['date_limite'] = r['date_limite'].date()
        if isinstance(r['date_reservation'], datetime):
            r['date_reservation'] = r['date_reservation'].date()

    cursor.close()
    db.close()

    return render_template("IHM/all_reservations.html", 
                           mes_reservations=toutes_les_res,
                           aujourdhui=aujourdhui,
                           prenom=session.get("prenom"),
                           nom=session.get("nom"),
                           search=recherche,
                           page_actuelle=page,
                           total_pages=total_pages,
                           total_elements=total_elements)


#-----------------
#Administration
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Vérification de sécurité
    if "id_user" not in session or session.get("admin") != 1:
        flash("Accès réservé aux administrateurs.", "danger")
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        # --- SUPPRIMER RÉSERVATION ---
        if action == "supprimer_reservation":
            id_res = request.form.get("id_reservation")
            try:
                cursor.execute("DELETE FROM reservations WHERE id_reservation = %s", (id_res,))
                db.commit()
                flash("Réservation annulée avec succès.", "warning")
            except mysql.connector.Error as err:
                flash(f"Erreur lors de l'annulation : {err}", "danger")

        # --- GÉRER HORAIRES ---
        elif action == "modifier_horaires_globaux":
            h_debut = request.form.get("h_debut")
            h_fin = request.form.get("h_fin")
            cursor.execute("UPDATE portes SET heure_debut = %s, heure_fin = %s", (h_debut, h_fin))
            db.commit()
            flash("Horaires de passage mis à jour avec succès.", "success")

        # --- CRÉER UTILISATEUR (AVEC SALT) ---
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

            # --- VALIDATION DU MOT DE PASSE ---
            if len(mdp_clair) < 10 or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", mdp_clair):
                flash("Erreur : Le mot de passe doit contenir au moins 10 caractères et un caractère spécial.", "danger")
                return redirect(url_for('admin'))

            nouveau_salt = uuid.uuid4().hex
            mdp_hash = hashlib.sha256((mdp_clair + nouveau_salt).encode()).hexdigest()
            badge_hash = hashlib.sha256(badge_clair.encode()).hexdigest() if badge_clair else None

            try:
                cursor.execute("""
                    INSERT INTO utilisateurs (utilisateur, mot_de_passe, salt, badge_uid, nom, prenom, email, telephone, role, admin) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (login_user, mdp_hash, nouveau_salt, badge_hash, nom, prenom, email, tel, role, admin_status))
                db.commit()
                flash(f"L'utilisateur {prenom} {nom} a été créé.", "success")
            except mysql.connector.Error as err:
                flash(f"Erreur lors de la création : {err}", "danger")

        # --- MODIFIER UTILISATEUR (AVEC SALT) ---
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
            
            if nouveau_badge and nouveau_badge.strip() != "":
                b_hash = hashlib.sha256(nouveau_badge.encode()).hexdigest()
                cursor.execute("UPDATE utilisateurs SET badge_uid=%s WHERE id_utilisateur=%s", (b_hash, id_u))

            if nouveau_mdp and nouveau_mdp.strip() != "":
                if len(nouveau_mdp) < 10 or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", nouveau_mdp):
                    flash("Erreur : Le nouveau mot de passe doit contenir 10 caractères et un caractère spécial.", "danger")
                    return redirect(url_for('admin'))

                nouveau_sel = uuid.uuid4().hex
                m_hash = hashlib.sha256((nouveau_mdp + nouveau_sel).encode()).hexdigest()
                cursor.execute("UPDATE utilisateurs SET mot_de_passe=%s, salt=%s WHERE id_utilisateur=%s", 
                               (m_hash, nouveau_sel, id_u))
                
            db.commit()
            flash("Profil utilisateur mis à jour.", "info")

        # --- SUPPRIMER UTILISATEUR ---
        elif action == "supprimer_utilisateur":
            id_u = request.form.get("id_utilisateur")
            if int(id_u) == session.get('id_user'):
                flash("Vous ne pouvez pas supprimer votre propre compte !", "danger")
            else:
                try:
                    cursor.execute("DELETE FROM utilisateurs WHERE id_utilisateur = %s", (id_u,))
                    db.commit()
                    flash("Utilisateur supprimé.", "warning")
                except mysql.connector.Error as err:
                    flash(f"Impossible de supprimer l'utilisateur (historique existant) : {err}", "danger")

        # --- MATÉRIEL : AJOUTER ---
        elif action == "ajouter_materiel":
            cursor.execute("""
                INSERT INTO materiel_stock (id_materiel, nom_modele, rfid_tag_epc, etat, actif, reservable) 
                VALUES (%s, %s, %s, %s, 1, 1)
            """, (request.form.get("id_inventaire"), request.form.get("nom_modele"), request.form.get("rfid_tag"), request.form.get("etat")))
            db.commit()
            flash("Matériel ajouté.", "success")

        # 👇 ICI : LE NOUVEAU BLOC POUR SUPPRIMER LE MATÉRIEL
        elif action == "supprimer_materiel":
            id_m = request.form.get("id_materiel")
            try:
                cursor.execute("DELETE FROM materiel_stock WHERE id_materiel = %s", (id_m,))
                db.commit()
                flash("Le matériel a définitivement été supprimé de l'inventaire.", "warning")
            except mysql.connector.Error as err:
                # Évite le plantage si le matériel est actuellement lié à des réservations ou à un journal d'accès
                flash("Erreur : Impossible de supprimer ce matériel car il possède un historique (réservations ou mouvements).", "danger")

        # --- MATÉRIEL : MODIFIER ---
        elif action == "modifier_materiel_complet":
            id_m = request.form.get("id_materiel")
            u_act = request.form.get("id_utilisateur_actuel")
            u_act = u_act if u_act != "" else None
            cursor.execute("""
                UPDATE materiel_stock SET nom_modele=%s, rfid_tag_epc=%s, etat=%s, id_utilisateur_actuel=%s WHERE id_materiel=%s
            """, (request.form.get("nom_modele"), request.form.get("rfid_tag_epc"), request.form.get("nouveau_statut"), u_act, id_m))
            db.commit()
            flash("Matériel mis à jour.", "info")

        return redirect(url_for('admin'))

    # --- AFFICHAGE ---
    cursor.execute("SELECT heure_debut as debut, heure_fin as fin FROM portes LIMIT 1")
    horaires = cursor.fetchone() or {'debut': '08:00', 'fin': '18:00'}
    
    cursor.execute("SELECT * FROM utilisateurs ORDER BY nom ASC")
    utilisateurs_list = cursor.fetchall()

    cursor.execute("SELECT * FROM materiel_stock ORDER BY id_materiel ASC")
    materiels_list = cursor.fetchall()

    cursor.execute("""
        SELECT r.id_reservation, 
               r.id_materiel, 
               r.date_reservation, 
               r.date_limite, 
               r.statut, 
               u.nom, 
               u.prenom, 
               m.nom_modele
        FROM reservations r
        JOIN utilisateurs u ON r.id_utilisateur = u.id_utilisateur
        JOIN materiel_stock m ON r.id_materiel = m.id_materiel
        WHERE r.statut NOT IN ('Annulée', 'Rendu')
        ORDER BY r.date_reservation DESC
    """)
    reservations_list = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("IHM/admin.html", 
                           horaires=horaires, 
                           utilisateurs=utilisateurs_list, 
                           materiels=materiels_list, 
                           reservations=reservations_list, 
                           prenom=session.get("prenom"), 
                           nom=session.get("nom"))

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

    if request.method == "POST":
        action = request.form.get("action")

        # FAIRE UNE DEMANDE
        if action == "demande":
            id_materiel = request.form["id_materiel"]
            id_destinataire = request.form["id_destinataire"]

            cursor.execute("""
                INSERT INTO prets (id_materiel, id_preteur, id_emprunteur)
                VALUES (%s,%s,%s)
            """, (id_materiel, user_id, id_destinataire))

            db.commit()

        # ACCEPTER DEMANDE
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

        # 🔴 REFUSER  DEMANDE
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

    # � demandes reçues 1 mois max
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

    # 📤 demandes envoyées 1 mois max
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

        # Update du mot de passe avec Salt et Robustesse
        if nouveau_mdp and nouveau_mdp.strip() != "":
            import re
            import uuid
            # Vérification 10 caractères + 1 spécial
            if len(nouveau_mdp) < 10 or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", nouveau_mdp):
                flash("Le nouveau mot de passe doit contenir au moins 10 caractères et un caractère spécial.", "danger")
                return redirect(url_for('profil', user_id=user_id))

            # Génération d'un nouveau Salt
            nouveau_sel = uuid.uuid4().hex
            h_mdp = hashlib.sha256((nouveau_mdp + nouveau_sel).encode()).hexdigest()
            
            cursor.execute("""
                UPDATE utilisateurs 
                SET mot_de_passe = %s, salt = %s 
                WHERE id_utilisateur = %s
            """, (h_mdp, nouveau_sel, target_id))
        
        db.commit()
        flash("Profil mis à jour avec succès !", "success")
        return redirect(url_for('profil', user_id=user_id))

    # ... reste du code (SELECT infos users) ...
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




@app.route("/reservation_materiel_liste/<int:id_mat>")
def reservation_materiel_liste(id_mat):
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Récupérer les infos du matériel cliqué
    cursor.execute("SELECT * FROM materiel_stock WHERE id_materiel = %s", (id_mat,))
    materiel = cursor.fetchone()

    if not materiel:
        flash("Matériel introuvable", "danger")
        return redirect("/materiels")

    # Récupérer les réservations en cours et futures pour ce matériel
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
    """Affiche la page d'accueil de la tablette (Attente de badge)."""
    return render_template("Ecran/accueil.html")

@app.route('/verifier_acces', methods=['POST'])
def verifier_acces():
    """Appelé UNIQUEMENT depuis l'écran d'accueil pour ouvrir une session."""
    data = request.json
    badge_uid_raw = str(data.get('badge_uid')).strip()
    badge_hash = hashlib.sha256(badge_uid_raw.encode()).hexdigest()

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    try:
        cursor.execute("SELECT id_utilisateur, nom, prenom FROM utilisateurs WHERE badge_uid = %s", (badge_hash,))
        user = cursor.fetchone()

        if user:
            prenom_f = user.get('prenom') or "Utilisateur"
            nom_f = user.get('nom') or ""

            # Cet événement ne doit être écouté QUE par l'écran d'accueil (accueil.html)
            socketio.emit('resultat_badge', {
                'status': 'vert',
                'nom': nom_f,
                'prenom': prenom_f,
                'badge_uid': badge_uid_raw,
                'redirect': f'/tablette/flux_materiel?badge_uid={badge_uid_raw}'
            })
            return jsonify({"status": "autorise"}), 200
        else:
            # 1. Alerte visuelle immédiate envoyée à l'écran de la tablette via SocketIO
            socketio.emit('resultat_badge', {
                'status': 'rouge',
                'message': 'Badge non enregistré dans le système.'
            })
            
            # 2. Récupération dynamique de TOUS les e-mails des administrateurs (admin = 1)
            try:
                cursor.execute("SELECT email FROM utilisateurs WHERE admin = 1")
                admins = cursor.fetchall()
                
                # On extrait les adresses e-mails valides et non vides
                liste_destinataires = [row['email'] for row in admins if row['email'] and '@' in row['email']]
                
                if liste_destinataires:
                    maintenant = datetime.now()
                    date_str = maintenant.strftime('%d/%m/%Y')
                    heure_str = maintenant.strftime('%H:%M:%S')

                    # On crée le message d'alerte
                    msg = Message(
                        subject="[ALERTE SECURITE] Tentative d'accès - Badge inconnu",
                        recipients=liste_destinataires,  # Flask-Mail gère automatiquement une liste d'adresses !
                        body=f"Bonjour,\n\nUne tentative d'accès avec un badge non enregistré a été détectée sur la tablette.\n\n"
                             f" Date : {date_str}\n"
                             f" Heure : {heure_str}\n"
                             f" UID du badge (Brut) : {badge_uid_raw}\n"
                             f" Hash SHA-256 recherché : {badge_hash}\n\n"
                             f"Cordialement,\nLe système de gestion RFID."
                    )
                    mail.send(msg)
                    print(f" E-mail d'alerte sécurité envoyé aux administrateurs : {liste_destinataires}")
                else:
                    print(" Aucun administrateur avec une adresse e-mail valide n'a été trouvé.")
                    
            except Exception as mail_err:
                print(f"Impossible d'envoyer l'e-mail d'alerte aux administrateurs : {mail_err}")

            return jsonify({"status": "refuse", "message": "Badge non enregistré dans le système."}), 403
            
    finally:
        cursor.close()
        db.close()


@app.route('/erreur_lecture', methods=['POST'])
def erreur_lecture():
    """Route appelée par le matériel physique en cas de problème de lecture RFID."""
    socketio.emit('resultat_badge', {
        'status': 'erreur_technique',
        'message': 'Lecture physique du badge impossible.'
    })
    return jsonify({"status": "ok"}), 200


@app.route("/tablette/flux_materiel")
def flux_materiel():
    """Affiche l'interface de scan pour l'utilisateur connecté."""
    return render_template("Ecran/flux_materiel.html")


# ==============================================================================
# 2. GESTION DES SCANS EN TEMPS RÉEL (PANIER VIRTUEL)
# ==============================================================================
@app.route("/scan_objet", methods=['POST'])
def scan_objet():
    """Modifie l'état IMMÉDIATEMENT. Si c'est une entrée, retire l'utilisateur direct."""
    global session_scan
    data = request.json
    tag_epc = data.get('rfid_tag_epc')

    if not tag_epc:
        return jsonify({"status": "error", "message": "Tag RFID non détecté."}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)
    try:
        # 1. Trouver le matériel associé au tag
        cursor.execute("SELECT id_materiel, nom_modele, etat FROM materiel_stock WHERE rfid_tag_epc = %s", (tag_epc,))
        item = cursor.fetchone()
        
        if not item:
            return jsonify({"status": "not_found", "message": "Équipement absent de l'inventaire."}), 404

        id_m = item['id_materiel']
        etat_bdd = str(item['etat']).strip().capitalize()
        
        # 2. Détermination du futur état ciblé par ce scan
        futur_etat = "Disponible"
        if tag_epc in session_scan:
            if session_scan[tag_epc]['etat'] == "Disponible":
                futur_etat = "Sortie"
        else:
            if etat_bdd == "Disponible":
                futur_etat = "Sortie"

        # 3. MISE À JOUR STRICTE ET IMMÉDIATE EN BDD
        if futur_etat == "Disponible":
            # Si le matos rentre : on le rend dispo ET on vire l'utilisateur actuel direct !
            cursor.execute("UPDATE materiel_stock SET etat='Disponible', id_utilisateur_actuel=NULL WHERE id_materiel=%s", (id_m,))
        else:
            # Si le matos sort : on change juste l'état. L'attribution à l'user se fera au badge.
            cursor.execute("UPDATE materiel_stock SET etat='Sortie' WHERE id_materiel=%s", (id_m,))
        
        db.commit() # Application immédiate en BDD

        # 4. Mise à jour de la session pour l'affichage tablette
        if tag_epc in session_scan:
            session_scan[tag_epc]['etat'] = futur_etat
        else:
            session_scan[tag_epc] = {
                'id': id_m,
                'nom': item['nom_modele'],
                'etat': futur_etat
            }
        
        # Envoi à l'interface graphique
        socketio.emit('mouvement_stock', {
            'id': id_m, 
            'nom': item['nom_modele'],
            'etat': session_scan[tag_epc]['etat']
        })
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        db.close()


@app.route("/valider_session_finale", methods=['POST'])
def valider_session_finale():
    """Attribue uniquement les matériels cochés et en 'Sortie' à l'utilisateur du badge."""
    global session_scan
    data = request.json
    badge_uid_raw = data.get('badge_uid')
    tags_selectionnes = [str(t) for t in data.get('tags', [])]
    statut_local = data.get('statut_local')

    # Si rien n'est coché à l'écran, on reset le dictionnaire de session et c'est tout
    if not tags_selectionnes:
        session_scan = {} 
        return jsonify({"status": "ok", "message": "Aucun équipement sélectionné."})

    if not badge_uid_raw or badge_uid_raw == "SESSION_TABLETTE":
        return jsonify({"status": "error", "message": "Veuillez scanner votre badge pour valider."}), 400

    badge_hash = hashlib.sha256(str(badge_uid_raw).strip().encode()).hexdigest()
    
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)
    
    try:
        # 1. Qui est le prof / l'utilisateur qui badge ?
        cursor.execute("SELECT id_utilisateur, utilisateur FROM utilisateurs WHERE badge_uid = %s", (badge_hash,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"status": "error", "message": "Badge non reconnu."}), 403

        id_u = user['id_utilisateur']
        erreurs_reservations = {}

        # 2. Contrôle des réservations (uniquement pour les Sorties cochées)
        for tag_epc, infos in session_scan.items():
            id_m = str(infos['id'])
            if id_m in tags_selectionnes and infos['etat'] == "Sortie":
                cursor.execute("""
                    SELECT r.id_utilisateur, u.utilisateur, r.date_reservation 
                    FROM reservations r
                    JOIN utilisateurs u ON r.id_utilisateur = u.id_utilisateur
                    WHERE r.id_materiel = %s 
                    AND r.statut IN ('Confirmée', 'Retard') 
                    AND DATE(r.date_reservation) <= CURDATE()
                    ORDER BY r.date_reservation ASC LIMIT 1
                """, (id_m,))
                res = cursor.fetchone()

                if res and id_u != res['id_utilisateur']:
                    date_fr = res['date_reservation'].strftime('%d/%m/%Y')
                    erreurs_reservations[id_m] = {
                        "nom_bloquant": res['utilisateur'],
                        "date_bloquante": date_fr
                    }

        if erreurs_reservations:
            return jsonify({
                "status": "bloque_reservation", 
                "message": "Certains matériels cochés sont réservés par d'autres utilisateurs.",
                "details": erreurs_reservations
            }), 200

        # 3. Attente du choix de fermeture du local (OUI/NON)
        if statut_local is None:
            return jsonify({"status": "attente_statut_local", "utilisateur": user['utilisateur']})

        # 4. ÉTAPE FINALE : ATTRIBUTION DE CE QUI EST COCHÉ
        for tag_epc, infos in list(session_scan.items()):
            id_m = str(infos['id'])
            
            if id_m in tags_selectionnes:
                if infos['etat'] == "Sortie":
                    # --- CAS DE LA SORTIE COCHÉE ---
                    # Calcul de la date limite
                    cursor.execute("""
                        SELECT date_reservation FROM reservations 
                        WHERE id_materiel=%s AND statut IN ('Confirmée', 'Retard') AND date_reservation > NOW() 
                        ORDER BY date_reservation ASC LIMIT 1
                    """, (id_m,))
                    prochaine_res = cursor.fetchone()
                    date_limite = prochaine_res['date_reservation'] if prochaine_res else (datetime.now() + timedelta(days=2))

                    # C'est ICI qu'on attribue enfin le matos à l'utilisateur !
                    cursor.execute("UPDATE materiel_stock SET id_utilisateur_actuel=%s WHERE id_materiel=%s", (id_u, id_m))
                    
                    # Mise à jour ou création de la réservation liée à cet emprunt
                    cursor.execute("""
                        UPDATE reservations SET statut='Récupérée', date_emprunt=NOW(), date_limite=%s 
                        WHERE id_materiel=%s AND id_utilisateur=%s AND statut IN ('Confirmée', 'Retard')
                    """, (date_limite, id_m, id_u))
                    
                    if cursor.rowcount == 0:
                        cursor.execute("""
                            INSERT INTO reservations (id_materiel, id_utilisateur, date_reservation, date_emprunt, date_limite, statut) 
                            VALUES (%s, %s, NOW(), NOW(), %s, 'Récupérée')
                        """, (id_m, id_u, date_limite))

                else: 
                    # --- CAS DE L'ENTRÉE COCHÉE ---
                    # L'id_utilisateur_actuel est DEJA mis à NULL via la route /scan_objet.
                    # Ici, on vient juste clôturer proprement la ligne de réservation historique de l'ancien emprunteur
                    # Note : On cherche l'ancienne ligne 'Récupérée' ou 'Retard' pour ce matériel
                    cursor.execute("""
                        UPDATE reservations SET statut='Rendu' 
                        WHERE id_materiel=%s AND statut IN ('Récupérée', 'Retard')
                    """, (id_m,))

                # Dans tous les cas, on enregistre l'historique dans la table mouvements au nom du badgeur
                cursor.execute("""
                    INSERT INTO mouvements (id_materiel, id_utilisateur, type_mouvement, date_heure) 
                    VALUES (%s, %s, %s, NOW())
                """, (id_m, id_u, "Entrée" if infos['etat'] == "Disponible" else "Sortie"))
                
                # On retire l'objet traité de la session temporaire
                del session_scan[tag_epc]

        db.commit()
        return jsonify({"status": "ok", "message": f"Session enregistrée au nom de {user['utilisateur']}."})

    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        db.close()


# --- RELANCE RETARDS (ADMIN) ---
@app.route("/relancer_retard/<int:id_res>")
def relancer_retard(id_res):
    if "id_user" not in session or session.get("admin") != 1:
        flash("Accès refusé.", "danger")
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.email, u.prenom, m.nom_modele, r.date_limite
            FROM reservations r
            JOIN utilisateurs u ON r.id_utilisateur = u.id_utilisateur
            JOIN materiel_stock m ON r.id_materiel = m.id_materiel
            WHERE r.id_reservation = %s
        """, (id_res,))
        info = cursor.fetchone()

        if info and info['email']:
            msg = Message(
                subject="[RAPPEL] Matériel non rendu - BTS RFID",
                recipients=[info['email']],
                body=f"Bonjour {info['prenom']},\n\nSauf erreur de notre part, vous n'avez pas encore rendu le matériel suivant : {info['nom_modele']}.\n\nLe retour était prévu pour le : {info['date_limite']}.\n\nMerci de bien vouloir le rapporter rapidement.\n\nCordialement,\nL'administration."
            )
            mail.send(msg)
            flash(f"Email envoyé à {info['email']}.", "success")
        else:
            flash("Erreur : Email introuvable.", "danger")
    except Exception as e:
        print(f"❌ Erreur relance manuelle : {e}")
        flash("Erreur lors de l'envoi de l'email.", "danger")
    finally:
        cursor.close()
        db.close()
        
    return redirect(url_for('admin'))

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --- BLOC DE LANCEMENT ---
if __name__ == "__main__":
    # 1. Lancement du planificateur pour les relances automatiques
    if not scheduler.running:
        # On vérifie les retards toutes les 30 minutes
        scheduler.add_job(
            id='job_retards', 
            func=verifier_retards_automatique, 
            trigger='interval', 
            minutes=30
        )
        scheduler.start()
        print("✅ Scheduler démarré (vérification des retards toutes les 30 min)")

    # 2. LANCEMENT DU SERVEUR AVEC SOCKET.IO
    print("🚀 Serveur Flask-SocketIO lancé sur le port 5000...")
    
    socketio.run(
        app, 
        host="0.0.0.0", 
        port=5000, 
        debug=True, 
        allow_unsafe_werkzeug=True,
        use_reloader=False # Empêche d'exécuter le script deux fois au démarrage en local
    )
