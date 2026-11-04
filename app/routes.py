
from datetime import datetime, date, time, timedelta
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Cliente, Servico, Profissional, Agendamento

main = Blueprint("main", __name__)


# ==========================================
# HORÁRIO DE FUNCIONAMENTO
# ==========================================

def horario_valido(inicio, fim):
    if inicio.date().weekday() == 6:
        return False

    if inicio.date() != fim.date():
        return False

    abertura = time(8, 0)
    fechamento = time(16, 0) if inicio.weekday() == 5 else time(18, 0)

    intervalo_inicio = time(12, 0)
    intervalo_fim = time(13, 0)

    if inicio.time() < abertura or fim.time() > fechamento:
        return False

    if inicio.time() < intervalo_fim and fim.time() > intervalo_inicio:
        return False

    return True


# ==========================================
# INÍCIO
# ==========================================

@main.route("/")
def inicio():
    return render_template("inicio.html")


@main.route("/teste-banco")
def teste_banco():
    from sqlalchemy import text

    db.session.execute(text("SELECT 1"))
    return "Conexão com PostgreSQL realizada com sucesso!"


# ==========================================
# CLIENTES
# ==========================================

@main.route("/clientes", methods=["GET", "POST"])
def clientes():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not nome or not telefone:
            flash("Nome e telefone são obrigatórios.", "error")
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
            flash("Este e-mail já está cadastrado.", "error")

        except Exception:
            db.session.rollback()
            flash("Não foi possível cadastrar o cliente.", "error")

        return redirect(url_for("main.clientes"))

    lista_clientes = Cliente.query.order_by(Cliente.nome.asc()).all()

    return render_template("clientes.html", clientes=lista_clientes)


# ==========================================
# SERVIÇOS
# ==========================================

@main.route("/servicos", methods=["GET", "POST"])
def servicos():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        preco = request.form.get("preco", "").strip()
        duracao = request.form.get("duracao", "").strip()

        if not nome or not preco or not duracao:
            flash("Preencha todos os campos obrigatórios.", "error")
            return redirect(url_for("main.servicos"))

        try:
            preco = Decimal(preco.replace(",", "."))
            duracao = int(duracao)

            if not preco.is_finite() or preco <= 0 or duracao <= 0:
                raise ValueError

            novo_servico = Servico(
                nome=nome,
                descricao=descricao or None,
                preco=preco,
                duracao=duracao
            )

            db.session.add(novo_servico)
            db.session.commit()
            flash("Serviço cadastrado com sucesso!")

        except (InvalidOperation, ValueError):
            db.session.rollback()
            flash("Informe um preço e uma duração válidos.", "error")

        except Exception:
            db.session.rollback()
            flash("Não foi possível cadastrar o serviço.", "error")

        return redirect(url_for("main.servicos"))

    lista_servicos = Servico.query.order_by(Servico.nome.asc()).all()

    return render_template("servicos.html", servicos=lista_servicos)


@main.route("/servicos/editar/<int:id>", methods=["GET", "POST"])
def editar_servico(id):

    servico = db.session.get(Servico, id)

    if servico is None:
        flash("Serviço não encontrado.", "error")
        return redirect(url_for("main.servicos"))

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        preco = request.form.get("preco", "").strip()
        duracao = request.form.get("duracao", "").strip()

        if not nome or not preco or not duracao:
            flash("Preencha os campos obrigatórios.", "error")
            return redirect(url_for("main.editar_servico", id=id))

        try:
            novo_preco = Decimal(preco.replace(",", "."))
            nova_duracao = int(duracao)

            if not novo_preco.is_finite() or novo_preco <= 0 or nova_duracao <= 0:
                raise ValueError

            servico.nome = nome
            servico.descricao = descricao or None
            servico.preco = novo_preco
            servico.duracao = nova_duracao

            db.session.commit()
            flash("Serviço atualizado com sucesso!")
            return redirect(url_for("main.servicos"))

        except (InvalidOperation, ValueError):
            db.session.rollback()
            flash("Preço ou duração inválidos.", "error")

        except Exception:
            db.session.rollback()
            flash("Não foi possível atualizar o serviço.", "error")

    return render_template("editar_servico.html", servico=servico)


@main.route("/servicos/excluir/<int:id>", methods=["POST"])
def excluir_servico(id):

    servico = db.session.get(Servico, id)

    if servico is None:
        flash("Serviço não encontrado.", "error")
        return redirect(url_for("main.servicos"))

    try:
        if Agendamento.query.filter_by(servico_id=id).first():
            flash("Não é possível excluir um serviço com agendamentos.", "error")
            return redirect(url_for("main.servicos"))

        db.session.delete(servico)
        db.session.commit()
        flash("Serviço excluído com sucesso!")

    except Exception:
        db.session.rollback()
        flash("Não foi possível excluir o serviço.", "error")

    return redirect(url_for("main.servicos"))


# ==========================================
# PROFISSIONAIS
# ==========================================

@main.route("/profissionais", methods=["GET", "POST"])
def profissionais():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()

        if not nome:
            flash("O nome do profissional é obrigatório.", "error")
            return redirect(url_for("main.profissionais"))

        profissional = Profissional(
            nome=nome,
            telefone=telefone or None
        )

        try:
            db.session.add(profissional)
            db.session.commit()
            flash("Profissional cadastrado com sucesso!")

        except Exception:
            db.session.rollback()
            flash("Não foi possível cadastrar o profissional.", "error")

        return redirect(url_for("main.profissionais"))

    lista = Profissional.query.order_by(Profissional.nome.asc()).all()

    return render_template("profissionais.html", profissionais=lista)


# ==========================================
# AGENDAMENTOS
# ==========================================

@main.route("/agendamento", methods=["GET", "POST"])
def agendamento():

    if request.method == "POST":

        try:
            cliente_id = int(request.form.get("cliente_id", ""))
            servico_id = int(request.form.get("servico_id", ""))
            profissional_id = int(request.form.get("profissional_id", ""))

            data_atendimento = date.fromisoformat(
                request.form.get("data", "")
            )

            horario = time.fromisoformat(
                request.form.get("horario", "")
            )

            inicio = datetime.combine(data_atendimento, horario)

        except (ValueError, TypeError):
            flash("Confira os dados do agendamento.", "error")
            return redirect(url_for("main.agendamento"))

        cliente = db.session.get(Cliente, cliente_id)
        servico = db.session.get(Servico, servico_id)
        profissional = db.session.get(Profissional, profissional_id)

        if not cliente or not servico or not profissional:
            flash("Cliente, serviço ou profissional inválido.", "error")
            return redirect(url_for("main.agendamento"))

        if not servico.ativo or not profissional.ativo:
            flash("Serviço ou profissional indisponível.", "error")
            return redirect(url_for("main.agendamento"))

        if inicio <= datetime.now():
            flash("Escolha uma data e horário futuros.", "error")
            return redirect(url_for("main.agendamento"))

        fim = inicio + timedelta(minutes=servico.duracao)

        if not horario_valido(inicio, fim):
            flash("Horário fora do funcionamento ou durante o intervalo.", "error")
            return redirect(url_for("main.agendamento"))

        conflitos = Agendamento.query.filter(
            Agendamento.profissional_id == profissional_id,
            Agendamento.status == "Agendado",
            Agendamento.data_hora < fim,
            Agendamento.data_hora + timedelta(
                minutes=servico.duracao
            ) > inicio
        ).all()

        for existente in conflitos:
            fim_existente = existente.data_hora + timedelta(
                minutes=existente.servico.duracao
            )

            if existente.data_hora < fim and fim_existente > inicio:
                flash("Este profissional já possui atendimento nesse horário.", "error")
                return redirect(url_for("main.agendamento"))

        novo = Agendamento(
            cliente_id=cliente_id,
            servico_id=servico_id,
            profissional_id=profissional_id,
            data_hora=inicio
        )

        try:
            db.session.add(novo)
            db.session.commit()
            flash("Agendamento realizado com sucesso!")

        except Exception:
            db.session.rollback()
            flash("Não foi possível salvar o agendamento.", "error")

        return redirect(url_for("main.agendamento"))

    lista_clientes = Cliente.query.order_by(Cliente.nome.asc()).all()

    lista_servicos = Servico.query.filter_by(
        ativo=True
    ).order_by(Servico.nome.asc()).all()

    lista_profissionais = Profissional.query.filter_by(
        ativo=True
    ).order_by(Profissional.nome.asc()).all()

    return render_template(
        "agendamento.html",
        clientes=lista_clientes,
        servicos=lista_servicos,
        profissionais=lista_profissionais
    )
