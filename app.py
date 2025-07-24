from flask import Flask, render_template, request, redirect, session, url_for, flash, make_response, send_file
from models import db, User
from waitress import serve
import models
import os
import time
from certificateGenerator import gerar_certificado

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.context_processor
def inject_user_and_cache_buster():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    return dict(user=user, cache_buster=int(time.time()))

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")

@app.route("/game")
def game():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("game.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        idade = request.form["idade"]
        escola = request.form["escola"]
        nivel = request.form["nivel"]
        email = request.form["email"]
        nome_responsavel = request.form["nome_responsavel"]
        telefone_responsavel = request.form["telefone_responsavel"]
        is_admin = "is_admin" in request.form

        if User.query.filter_by(username=username).first():
            flash("Nome de usuário já existe.")
            return redirect(url_for("register"))
            
        user = User(username=username, nome=nome, telefone=telefone, idade=idade, escola=escola, nivel=nivel, email=email, nome_responsavel=nome_responsavel, telefone_responsavel=telefone_responsavel, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Cadastro realizado com sucesso! Por favor, faça o login.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Login realizado com sucesso!")
            return redirect(url_for("modules_hub"))
        flash("Credenciais inválidas.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Você foi desconectado.")
    return redirect(url_for("login"))

@app.route("/modules")
def modules_hub():
    if "user_id" not in session:
        return redirect(url_for('login'))
    return render_template("modules_hub.html")

@app.route("/modulo1")
def modulo1():
    if "user_id" not in session:
        return redirect(url_for('login'))
    return render_template("modulo1.html")

@app.route("/modulo2")
def modulo2():
    if "user_id" not in session:
        return redirect(url_for('login'))
    return render_template("modulo2.html")

@app.route("/modulo3")
def modulo3():
    if "user_id" not in session:
        return redirect(url_for('login'))
    return render_template("modulo3.html")

@app.route("/modulo4")
def modulo4():
    if "user_id" not in session:
        return redirect(url_for('login'))
    return render_template("modulo4.html")

@app.route("/modulo5")
def modulo5():
    if "user_id" not in session:
        return redirect(url_for('login'))
    return render_template("modulo5.html")

@app.route("/admin")
def admin():
    if "user_id" not in session:
        flash("Por favor, faça o login para acessar esta página.")
        return redirect(url_for("login"))
    
    user = User.query.get(session.get("user_id"))
    if not user or not user.is_admin:
        flash("Acesso não autorizado.")
        return redirect(url_for("home"))

    users = User.query.all()
    return render_template("admin.html", users=users)

@app.route("/congratulations")
def congratulations():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("congratulations.html")

@app.route("/download_certificate", methods=["GET", "POST"])
def download_certificate():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user = User.query.get(session.get("user_id"))
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        cpf = request.form.get("cpf")
        if not cpf:
            flash("Por favor, insira seu CPF para gerar o certificado.")
            return redirect(url_for("congratulations"))

        try:
            certificate_buffer = gerar_certificado(user.nome, cpf)
            return send_file(
                certificate_buffer,
                as_attachment=True,
                download_name=f"certificado_{user.username}.pdf",
                mimetype='application/pdf'
            )
        except Exception as e:
            flash(f"Ocorreu um erro ao gerar o certificado: {e}")
            return redirect(url_for("congratulations"))

    return redirect(url_for("congratulations"))


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
