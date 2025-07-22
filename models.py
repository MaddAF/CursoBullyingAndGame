from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)


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
