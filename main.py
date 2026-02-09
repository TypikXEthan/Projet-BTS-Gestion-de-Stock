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

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        utilisateur = request.form["utilisateur"]
        mot_de_passe = request.form["mot_de_passe"]

        mdp_hash = hashlib.sha256(mot_de_passe.encode()).hexdigest()

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_utilisateur, utilisateur, nom, prenom, role
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

            return redirect("/dashboard")
        else:
            return render_template("IHM/login.html", erreur="Identifiants incorrects")

    return render_template("IHM/login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Matériel en stock
    cursor.execute("SELECT COUNT(*) AS total FROM materiel_stock WHERE statut = 'En Stock'")
    nb_stock = cursor.fetchone()["total"]

    # Matériel sorti
    cursor.execute("SELECT COUNT(*) AS total FROM materiel_stock WHERE statut = 'Sorti'")
    nb_sorti = cursor.fetchone()["total"]

    # 10 derniers mouvements peut etre metre 15 
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

# HISTORIQUE
@app.route("/historique", methods=["GET", "POST"])
def historique():
    if "id_user" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Resultat de la recherche
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



# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
