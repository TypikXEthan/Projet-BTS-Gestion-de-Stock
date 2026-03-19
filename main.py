from flask import Flask, render_template, request, redirect, session
import mysql.connector
import hashlib
from datetime import datetime, timedelta

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

# -------------------------------
# LOGIN
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
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
            session["id_user"] = user["id_utilisateur"]
            session["utilisateur"] = user["utilisateur"]
            session["nom"] = user["nom"]
            session["prenom"] = user["prenom"]
            session["role"] = user["role"]
            session["admin"] = user["admin"]
            return redirect("/dashboard")
        else:
            return render_template("IHM/login.html", erreur="Identifiants incorrects")

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

    # Matériels en stock
    cursor.execute("SELECT COUNT(*) AS total FROM materiel_stock WHERE stock = 1")
    nb_stock = cursor.fetchone()["total"]

    # Matériels sortis
    cursor.execute("SELECT COUNT(*) AS total FROM materiel_stock WHERE stock = 0")
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
        "IHM/dashboard.html",  # Assurez-vous que le template s'appelle dashboard.html
        nb_stock=nb_stock,
        nb_sorti=nb_sorti,
        mouvements=mouvements,
        nom=session["nom"],
        prenom=session["prenom"]
    )
# -------------------------------
# MATERIELS
# -------------------------------
@app.route("/materiels", methods=["GET", "POST"])
def materiels():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # =========================
    # ACTIONS (POST)
    # =========================
    if request.method == "POST":
        action = request.form.get("action")
        id_materiel = request.form.get("id_materiel")

        if action == "confirmer_materiel" and id_materiel:

            # 🔍 récupérer état actuel
            cursor.execute("SELECT stock FROM materiel_stock WHERE id_materiel=%s", (id_materiel,))
            materiel = cursor.fetchone()

            if materiel:
                ancien_stock = materiel["stock"]
                nouveau_stock = 0 if ancien_stock == 1 else 1

                # 🔄 UPDATE stock
                cursor.execute("""
                    UPDATE materiel_stock 
                    SET stock=%s 
                    WHERE id_materiel=%s
                """, (nouveau_stock, id_materiel))

                # 🧠 déterminer le type de mouvement
                type_mouvement = "Entrée" if nouveau_stock == 1 else "Sortie"

                # 📝 INSERT mouvement
                cursor.execute("""
                    INSERT INTO mouvements (id_materiel, id_utilisateur, type_mouvement, date_heure)
                    VALUES (%s, %s, %s, NOW())
                """, (id_materiel, session["id_user"], type_mouvement))

                db.commit()

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

    # 🎯 convertir stock → texte
    for m in materiels:
        m["statut"] = "En Stock" if m["stock"] == 1 else "Sorti"

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

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Récupérer tous les mouvements avec infos utilisateur + matériel
    cursor.execute("""
        SELECT m.id_mouvement, m.type_mouvement, m.date_heure,
               ms.nom_modele,
               u.nom, u.prenom
        FROM mouvements m
        LEFT JOIN materiel_stock ms ON m.id_materiel = ms.id_materiel
        LEFT JOIN utilisateurs u ON m.id_utilisateur = u.id_utilisateur
        ORDER BY m.date_heure DESC
    """)

    mouvements = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "IHM/historique.html",
        mouvements=mouvements,
        nom=session["nom"],
        prenom=session["prenom"]
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
            UPDATE reservations SET statut='Annulée'
            WHERE id_reservation=%s
        """, (r["id_reservation"],))

        cursor.execute("""
            UPDATE materiel_stock
            SET id_utilisateur_actuel=NULL
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
                    SELECT stock, reservable, actif, id_utilisateur_actuel
                    FROM materiel_stock
                    WHERE id_materiel=%s
                """, (id_materiel,))
                mat = cursor.fetchone()

                if mat and mat["reservable"] == 1 and mat["actif"] == 1:

                    # 🔒 si aujourd’hui → bloquer direct
                    if date_resa.date() == now.date():
                        cursor.execute("""
                            UPDATE materiel_stock
                            SET id_utilisateur_actuel=%s
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
                    SET id_utilisateur_actuel=NULL
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
                    SET stock=0
                    WHERE id_materiel=%s
                """, (id_mat,))

                cursor.execute("""
                    UPDATE reservations 
                    SET statut='Récupérée'
                    WHERE id_reservation=%s
                """, (id_reservation,))

                cursor.execute("""
                    INSERT INTO mouvements (id_materiel, id_utilisateur, type_mouvement, date_heure)
                    VALUES (%s,%s,'Sortie',NOW())
                """, (id_mat, user_id))

                db.commit()

    # =========================
    # GET
    # =========================

    # 📅 limites calendrier
    date_min = date.today().isoformat()
    date_max = (date.today() + timedelta(days=7)).isoformat()

    # 📦 matériels dispo
    cursor.execute("""
        SELECT id_materiel, nom_modele, rfid_tag_epc
        FROM materiel_stock
        WHERE stock=1 AND reservable=1 AND actif=1 AND id_utilisateur_actuel IS NULL
    """)
    materiels = cursor.fetchall()

    # 📋 mes réservations (30 derniers jours)
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

# -------------------------------
# ADMINISTRATION
# -------------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "id_user" not in session or session.get("admin") != 1:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        # =========================
        # 👤 CREER UTILISATEUR
        # =========================
        if action == "creer_utilisateur":
            nom = request.form["nom"]
            prenom = request.form["prenom"]
            identifiant = request.form["identifiant"]
            role = request.form["role"]
            mdp = hashlib.sha256(request.form["mot_de_passe"].encode()).hexdigest()

            cursor.execute("""
                INSERT INTO utilisateurs (nom, prenom, utilisateur, role, mot_de_passe, admin)
                VALUES (%s,%s,%s,%s,%s,0)
            """, (nom, prenom, identifiant, role, mdp))
            db.commit()

        # =========================
        # ❌ SUPPRIMER UTILISATEUR
        # =========================
        elif action == "supprimer_utilisateur":
            cursor.execute("DELETE FROM utilisateurs WHERE id_utilisateur=%s",
                           (request.form["id"],))
            db.commit()

        # =========================
        # 🔥 TOGGLE ADMIN
        # =========================
        elif action == "toggle_admin":
            cursor.execute("""
                UPDATE utilisateurs SET admin=%s WHERE id_utilisateur=%s
            """, (request.form["nouveau_statut"], request.form["id"]))
            db.commit()

        # =========================
        # 🔑 CHANGER MOT DE PASSE
        # =========================
        elif action == "changer_mdp":
            new_mdp = hashlib.sha256(request.form["nouveau_mdp"].encode()).hexdigest()
            cursor.execute("""
                UPDATE utilisateurs SET mot_de_passe=%s WHERE id_utilisateur=%s
            """, (new_mdp, request.form["id"]))
            db.commit()

        # =========================
        # 📦 AJOUT MATERIEL
        # =========================
        elif action == "ajouter_materiel":
            nom_modele = request.form["nom_modele"]
            rfid = request.form["rfid_tag_epc"]
            statut = request.form["statut"]

            stock = 1 if statut == "En Stock" else 0

            cursor.execute("""
                INSERT INTO materiel_stock (nom_modele, rfid_tag_epc, stock)
                VALUES (%s,%s,%s)
            """, (nom_modele, rfid, stock))
            db.commit()

        # =========================
        # ❌ SUPPRIMER MATERIEL
        # =========================
        elif action == "supprimer_materiel":
            cursor.execute("DELETE FROM materiel_stock WHERE id_materiel=%s",
                           (request.form["id_materiel"],))
            db.commit()

        # =========================
        # 🔄 CHANGER STATUT (STOCK)
        # =========================
        elif action == "changer_statut_materiel":
            statut = request.form["nouveau_statut"]
            stock = 1 if statut == "En Stock" else 0

            cursor.execute("""
                UPDATE materiel_stock SET stock=%s WHERE id_materiel=%s
            """, (stock, request.form["id_materiel"]))

            # 🔥 ajouter mouvement
            type_mouvement = "Entrée" if stock == 1 else "Sortie"

            cursor.execute("""
                INSERT INTO mouvements (id_materiel, id_utilisateur, type_mouvement, date_heure)
                VALUES (%s,%s,%s,NOW())
            """, (request.form["id_materiel"], session["id_user"], type_mouvement))

            db.commit()

    # =========================
    # 📊 RECUP DATA
    # =========================
    cursor.execute("SELECT * FROM utilisateurs")
    utilisateurs = cursor.fetchall()

    cursor.execute("SELECT * FROM materiel_stock")
    materiels = cursor.fetchall()

    # 🔥 ajouter statut + dernier mouvement
    cursor.execute("""
        SELECT id_materiel, type_mouvement, date_heure
        FROM mouvements
        ORDER BY date_heure DESC
    """)
    mouvements = cursor.fetchall()

    last_move = {}
    for m in mouvements:
        if m["id_materiel"] not in last_move:
            last_move[m["id_materiel"]] = f"{m['type_mouvement']} le {m['date_heure']}"

    for m in materiels:
        m["statut"] = "En Stock" if m["stock"] == 1 else "Sorti"
        m["dernier_mouvement"] = last_move.get(m["id_materiel"], "-")

    cursor.close()
    db.close()

    return render_template(
        "IHM/admin.html",
        utilisateurs=utilisateurs,
        materiels=materiels,
        nom=session["nom"],
        prenom=session["prenom"]
    )


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
