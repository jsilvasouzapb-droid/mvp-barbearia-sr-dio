
import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "chave-temporaria-desenvolvimento"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:Saopaulo8@localhost:5432/barbearia_sr_dio"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
