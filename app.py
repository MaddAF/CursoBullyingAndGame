from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import db, User
from waitress import serve

import os

app = Flask(__name__)

@app.route("/Modulo1")
def home():
    return render_template("index.html")



app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Change in production

# Replace with your actual Render PostgreSQL URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ensure tables are created
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return render_template("home.html", user=user)
    return redirect(url_for("login"))

@app.route("/Game")
def game():
    return render_template("game.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("register"))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            return redirect(url_for("home"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.")
    return redirect(url_for("login"))
    

if __name__ == "__main__":
    with app.app_context():
        # ONE-TIME safe column fix for password_hash
        with db.engine.connect() as conn:
            conn.execute('ALTER TABLE "user" ALTER COLUMN password_hash TYPE TEXT;')

    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)