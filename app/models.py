
from datetime import datetime

from app import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    telefone = db.Column(
        db.String(20),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=True
    )

    data_cadastro = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )

    def __repr__(self):
        return f"<Cliente {self.nome}>"

class Servico(db.Model):
    __tablename__ = "servicos"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    descricao = db.Column(
        db.Text,
        nullable=True
    )

    preco = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    duracao = db.Column(
        db.Integer,
        nullable=False
    )

    ativo = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    def __repr__(self):
        return f"<Servico {self.nome}>"