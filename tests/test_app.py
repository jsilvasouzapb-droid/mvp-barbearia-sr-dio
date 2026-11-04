
import pytest

from app import create_app, db
from app.models import Cliente, Servico, Profissional


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "chave-de-teste",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ENGINE_OPTIONS": {}
    })

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_pagina_inicial(client):
    resposta = client.get("/")
    assert resposta.status_code == 200


def test_pagina_clientes(client):
    resposta = client.get("/clientes")
    assert resposta.status_code == 200


def test_cadastro_cliente(client, app):
    resposta = client.post("/clientes", data={
        "nome": "João da Silva",
        "telefone": "85999999999",
        "email": "joao@example.com"
    })

    assert resposta.status_code == 302

    with app.app_context():
        cliente = Cliente.query.filter_by(
            email="joao@example.com"
        ).first()

        assert cliente is not None
        assert cliente.nome == "João da Silva"


def test_cliente_sem_nome(client):
    resposta = client.post("/clientes", data={
        "nome": "",
        "telefone": "85999999999"
    })

    assert resposta.status_code == 302


def test_pagina_servicos(client):
    resposta = client.get("/servicos")
    assert resposta.status_code == 200


def test_cadastro_servico(client, app):
    resposta = client.post("/servicos", data={
        "nome": "Corte masculino",
        "descricao": "Corte tradicional",
        "preco": "35.00",
        "duracao": "30"
    })

    assert resposta.status_code == 302

    with app.app_context():
        servico = Servico.query.filter_by(
            nome="Corte masculino"
        ).first()

        assert servico is not None
        assert float(servico.preco) == 35.00


def test_servico_com_preco_invalido(client, app):
    resposta = client.post("/servicos", data={
        "nome": "Corte",
        "preco": "-10",
        "duracao": "30"
    })

    assert resposta.status_code == 302

    with app.app_context():
        assert Servico.query.count() == 0


def test_pagina_profissionais(client):
    resposta = client.get("/profissionais")
    assert resposta.status_code == 200


def test_cadastro_profissional(client, app):
    resposta = client.post("/profissionais", data={
        "nome": "Carlos",
        "telefone": "85988888888"
    })

    assert resposta.status_code == 302

    with app.app_context():
        profissional = Profissional.query.filter_by(
            nome="Carlos"
        ).first()

        assert profissional is not None


def test_pagina_agendamento(client):
    resposta = client.get("/agendamento")
    assert resposta.status_code == 200


def test_teste_banco(client):
    resposta = client.get("/teste-banco")
    assert resposta.status_code == 200
