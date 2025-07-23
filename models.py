from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    nome = db.Column(db.String(150), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    idade = db.Column(db.Integer, nullable=True)
    escola = db.Column(db.String(150), nullable=True)
    nivel = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    nome_responsavel = db.Column(db.String(150), nullable=True)
    telefone_responsavel = db.Column(db.String(20), nullable=True)
    progresso = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

from sqlalchemy import inspect

def recreate_user_table_if_needed():
    inspector = inspect(db.engine)
    if "user" in inspector.get_table_names():
        print("Tabela 'user' existe. Removendo...")
        User.__table__.drop(db.engine)
        print("Tabela 'user' removida com sucesso.")

    print("Criando tabela 'user' com o schema atualizado...")
    User.__table__.create(db.engine)
    print("Tabela 'user' criada com sucesso.")