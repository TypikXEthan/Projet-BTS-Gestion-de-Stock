from flask import Flask, render_template, request, redirect, session
import mysql.connector
import hashlib

app = Flask(__name__)
app.secret_key = "cle_secrete_bts_rfid"  # clé de session
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="Projet_BTS_RFID"
)


#Connexion
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
            WHERE utilisateur = %s AND mot_de_passe = %s
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

# Page DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Materiel dans le stock
    cursor.execute("SELECT COUNT(*) AS total FROM materiel_stock WHERE statut = 'En Stock'")
    nb_stock = cursor.fetchone()["total"]

    # Matériel qui est sorti
    cursor.execute("SELECT COUNT(*) AS total FROM materiel_stock WHERE statut = 'Sorti'")
    nb_sorti = cursor.fetchone()["total"]

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

#Page HISTORIQUE
@app.route("/historique", methods=["GET", "POST"])
def historique():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    recherche = request.args.get("recherche", "").strip()
    query = """
        SELECT m.type_mouvement, m.date_heure,
               ms.nom_modele,
               u.nom, u.prenom
        FROM mouvements m
        JOIN materiel_stock ms ON m.id_materiel = ms.id_materiel
        JOIN utilisateurs u ON m.id_utilisateur = u.id_utilisateur
    """
    params = ()
    if recherche:
        query += """
            WHERE ms.nom_modele LIKE %s
               OR u.nom LIKE %s
               OR u.prenom LIKE %s
               OR DATE(m.date_heure) = %s
        """
        params = (f"%{recherche}%", f"%{recherche}%", f"%{recherche}%", recherche)

    query += " ORDER BY m.date_heure DESC"
    cursor.execute(query, params)
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
# Page MATERIELS
@app.route("/materiels")
def materiels():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Recherche
    recherche = request.args.get("recherche", "").strip()

    # Pagination page 1,2,3...
    page = int(request.args.get("page", 1))
    limit = 20
    offset = (page - 1) * limit

    base_query = """
        FROM materiel_stock ms
        LEFT JOIN utilisateurs u
            ON ms.id_utilisateur_actuel = u.id_utilisateur
    """

    where = ""
    params = []

    if recherche:
        where = " WHERE ms.nom_modele LIKE %s OR ms.rfid_tag_epc LIKE %s "
        params.extend([f"%{recherche}%", f"%{recherche}%"])

    # Compter le total du materiel 
    cursor.execute("SELECT COUNT(*) AS total " + base_query + where, params)
    total = cursor.fetchone()["total"]
    total_pages = (total + limit - 1) // limit

    # Récupération des matériels et info 
    query = """
        SELECT ms.id_materiel, ms.nom_modele, ms.rfid_tag_epc,
               ms.statut, u.nom, u.prenom
    """ + base_query + where + """
        ORDER BY ms.nom_modele
        LIMIT %s OFFSET %s
    """

    cursor.execute(query, params + [limit, offset])
    materiels = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "IHM/materiels.html",
        materiels=materiels,
        nom=session["nom"],
        prenom=session["prenom"],
        recherche=recherche,
        page=page,
        total_pages=total_pages
    )

#Page D'UTILISATEURS
@app.route("/utilisateurs")
def utilisateurs():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            u.id_utilisateur,
            u.nom,
            u.prenom,
            u.utilisateur,
            u.role,
            u.admin,
            COUNT(ms.id_materiel) AS nb_emprunts
        FROM utilisateurs u
        LEFT JOIN materiel_stock ms
            ON u.id_utilisateur = ms.id_utilisateur_actuel
        GROUP BY u.id_utilisateur
    """)
    utilisateurs = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "IHM/utilisateurs.html",
        utilisateurs=utilisateurs,
        nom=session["nom"],
        prenom=session["prenom"]
    )
#Page ADMINISTRATION 

@app.route("/admin", methods=["GET", "POST"])
def admin():

    # Sécurité se connecte que si l'utilisateur est en admin
    if "id_user" not in session or session.get("admin") != 1:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # TRAITEMENT DES ACTIONS en post
    if request.method == "POST":

        action = request.form.get("action")

        # CREER  un utilisateur 
        if action == "creer_utilisateur":
            nom = request.form["nom"]
            prenom = request.form["prenom"]
            identifiant = request.form["identifiant"]
            role = request.form["role"]
            mot_de_passe = hashlib.sha256(
                request.form["mot_de_passe"].encode()
            ).hexdigest()

            cursor.execute("""
                INSERT INTO utilisateurs
                (nom, prenom, utilisateur, role, mot_de_passe, admin)
                VALUES (%s, %s, %s, %s, %s, 0)
            """, (nom, prenom, identifiant, role, mot_de_passe))
            db.commit()

        # SUPPRIMER UN  UTILISATEUR
        elif action == "supprimer_utilisateur":
            id_user = request.form["id"]
            cursor.execute("DELETE FROM utilisateurs WHERE id_utilisateur = %s", (id_user,))
            db.commit()

        # CHANGER LE MOT DE PASSE
        elif action == "changer_mdp":
            id_user = request.form["id"]
            nouveau_mdp = hashlib.sha256(
                request.form["nouveau_mdp"].encode()
            ).hexdigest()

            cursor.execute("""
                UPDATE utilisateurs
                SET mot_de_passe = %s
                WHERE id_utilisateur = %s
            """, (nouveau_mdp, id_user))
            db.commit()

        # TOGGLE ADMIN
        elif action == "toggle_admin":
            id_user = request.form["id"]
            nouveau_statut = request.form["nouveau_statut"]

            cursor.execute("""
                UPDATE utilisateurs
                SET admin = %s
                WHERE id_utilisateur = %s
            """, (nouveau_statut, id_user))
            db.commit()

        # AJOUTER MATERIEL
        elif action == "ajouter_materiel":
            nom_modele = request.form["nom_modele"]
            rfid = request.form["rfid"]

            cursor.execute("""
                INSERT INTO materiel_stock
                (nom_modele, rfid_tag_epc, statut)
                VALUES (%s, %s, 'En Stock')
            """, (nom_modele, rfid))
            db.commit()

    # AFFICHAGE DES DONNEES

    cursor.execute("SELECT * FROM utilisateurs")
    utilisateurs = cursor.fetchall()

    cursor.execute("SELECT * FROM materiel_stock")
    materiels = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "IHM/admin.html",
        utilisateurs=utilisateurs,
        materiels=materiels,
        nom=session["nom"],
        prenom=session["prenom"]
    )

# Déconnexion
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# MAIN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
