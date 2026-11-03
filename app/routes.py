from decimal import Decimal, InvalidOperation
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Cliente, Servico

main = Blueprint("main", __name__)


@main.route("/")
def inicio():
    return render_template("inicio.html")
    
@main.route("/teste-banco")
def teste_banco():
    from sqlalchemy import text

    db.session.execute(text("SELECT 1"))

    return "Conexão com PostgreSQL realizada com sucesso!"


@main.route("/clientes", methods=["GET", "POST"])
def clientes():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not nome or not telefone:
            flash("Nome e telefone são obrigatórios.")
            return redirect(url_for("main.clientes"))

        novo_cliente = Cliente(
            nome=nome,
            telefone=telefone,
            email=email if email else None
        )

        try:
            db.session.add(novo_cliente)
            db.session.commit()

            flash("Cliente cadastrado com sucesso!")

        except IntegrityError:
            db.session.rollback()

            flash("Este e-mail já está cadastrado.")

        except Exception:
            db.session.rollback()

            flash("Não foi possível cadastrar o cliente.")

        return redirect(url_for("main.clientes"))

    lista_clientes = Cliente.query.order_by(
        Cliente.nome.asc()
    ).all()

    return render_template(
        "clientes.html",
        clientes=lista_clientes
    )

@main.route("/servicos", methods=["GET", "POST"])
def servicos():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        preco = request.form.get("preco", "").strip()
        duracao = request.form.get("duracao", "").strip()

        if not nome or not preco or not duracao:
            flash("Preencha todos os campos obrigatórios.")
            return redirect(url_for("main.servicos"))

        try:
            preco = Decimal(preco.replace(",", "."))
            duracao = int(duracao)

            if preco <= 0 or duracao <= 0:
                flash("Preço e duração devem ser maiores que zero.")
                return redirect(url_for("main.servicos"))

            novo_servico = Servico(
                nome=nome,
                descricao=descricao if descricao else None,
                preco=preco,
                duracao=duracao
            )

            db.session.add(novo_servico)
            db.session.commit()

            flash("Serviço cadastrado com sucesso!")

        except (InvalidOperation, ValueError):
            db.session.rollback()
            flash("Informe um preço e uma duração válidos.")

        except Exception:
            db.session.rollback()
            flash("Não foi possível cadastrar o serviço.")

        return redirect(url_for("main.servicos"))

    lista_servicos = Servico.query.order_by(
        Servico.nome.asc()
    ).all()

    return render_template(
        "servicos.html",
        servicos=lista_servicos
    )


@main.route("/servicos/editar/<int:id>", methods=["GET", "POST"])
def editar_servico(id):

    servico = db.session.get(Servico, id)

    if servico is None:
        flash("Serviço não encontrado.")
        return redirect(url_for("main.servicos"))

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        preco = request.form.get("preco", "").strip()
        duracao = request.form.get("duracao", "").strip()

        if not nome or not preco or not duracao:
            flash("Preencha todos os campos obrigatórios.")
            return redirect(
                url_for("main.editar_servico", id=id)
            )

        try:
            novo_preco = Decimal(preco.replace(",", "."))
            nova_duracao = int(duracao)

            if novo_preco <= 0 or nova_duracao <= 0:
                flash("Preço e duração devem ser maiores que zero.")
                return redirect(
                    url_for("main.editar_servico", id=id)
                )

            servico.nome = nome
            servico.descricao = descricao if descricao else None
            servico.preco = novo_preco
            servico.duracao = nova_duracao

            db.session.commit()

            flash("Serviço atualizado com sucesso!")

            return redirect(url_for("main.servicos"))

        except (InvalidOperation, ValueError):
            db.session.rollback()
            flash("Informe um preço e uma duração válidos.")

        except Exception:
            db.session.rollback()
            flash("Não foi possível atualizar o serviço.")

    return render_template(
        "editar_servico.html",
        servico=servico
    )


@main.route("/servicos/excluir/<int:id>", methods=["POST"])
def excluir_servico(id):

    servico = db.session.get(Servico, id)

    if servico is None:
        flash("Serviço não encontrado.")
        return redirect(url_for("main.servicos"))

    try:
        db.session.delete(servico)
        db.session.commit()

        flash("Serviço excluído com sucesso!")

    except Exception:
        db.session.rollback()
        flash("Não foi possível excluir o serviço.")

    return redirect(url_for("main.servicos"))
  
