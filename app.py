from flask import Flask, render_template, request, redirect, session, url_for, flash, make_response, send_file
from models import db, User
from waitress import serve
import models
import os
import time
from certificateGenerator import gerar_certificado, gerarNomeArquivo
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

modules_data = [
    {"id": 1, "title": "Módulo 1: O que é Bullying?", "iframe_src": "https://gamma.app/embed/66upk8qpjjj0605"},
    {"id": 2, "title": "Módulo 2: Empatia - A Conexão Humana Essencial", "iframe_src": "https://gamma.app/embed/i8tatd8uogajn9y"},
    {"id": 3, "title": "Módulo 3: O Que Fazer?", "iframe_src": "https://gamma.app/embed/blfhf1mwmn401j8"},
    {"id": 4, "title": "Módulo 4: Cyber-Segurança", "iframe_src": "https://gamma.app/embed/3mi05q4zcdj05pj"},
    {"id": 5, "title": "Módulo 5: Missão Final", "iframe_src": "https://gamma.app/embed/gjxal9c1opw1z7h"},
]

def get_module_text(url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(url)
        
        # Wait for the main content to be loaded. This might need adjustment.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "gamma-container"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
        return soup.get_text()
    except Exception as e:
        print(f"Error fetching module text with Selenium: {e}")
        return ""

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.context_processor
def inject_user_and_cache_buster():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id) if user_id else None
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
    return redirect(url_for('module', module_id=1))

@app.route("/module/<int:module_id>")
def module(module_id):
    if "user_id" not in session:
        return redirect(url_for('login'))

    module_info = next((m for m in modules_data if m['id'] == module_id), None)

    if module_info:
        module_text = get_module_text(module_info['iframe_src'])
        return render_template("module.html", module=module_info, modules_data=modules_data, module_text=module_text)
    else:
        return "Módulo não encontrado", 404

@app.route("/admin")
def admin():
    if "user_id" not in session:
        flash("Por favor, faça o login para acessar esta página.")
        return redirect(url_for("login"))
    
    user = db.session.get(User, session.get("user_id"))
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
    
    user = db.session.get(User, session.get("user_id"))
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        cpf = request.form.get("cpf")
        if not cpf:
            flash("Por favor, insira seu CPF para gerar o certificado.")
            return redirect(url_for("congratulations"))

        try:
            certificate_buffer = gerar_certificado(user.nome, cpf)
            download_name = gerarNomeArquivo(user.nome)
            return send_file(
                certificate_buffer,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/pdf'
            )
        except Exception as e:
            flash(f"Ocorreu um erro ao gerar o certificado: {e}")
            return redirect(url_for("congratulations"))

    return redirect(url_for("congratulations"))


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
