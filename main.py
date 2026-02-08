from flask import Flask, render_template, request, redirect, session
import mysql.connector
import hashlib

app = Flask(__name__)
app.secret_key = "secret_test_bts"  # clé pour gérer les sessions

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",          # ton mot de passe BDD
        database="Projet_BTS_RFID"
    )

# -------------------------
# LOGIN
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["utilisateur"]
        mdp = request.form["mot_de_passe"]

        mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM utilisateurs WHERE utilisateur=%s AND mot_de_passe=%s",
            (user, mdp_hash)
        )
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if result:
            session["user"] = user
            return redirect("/dashboard")
        else:
            return "Login incorrect"

    return render_template("IHM/login.html")

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("IHM/dashboard.html")

# -------------------------
# Lancement du serveur
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
