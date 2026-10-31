from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Evento, EventoProducto, Producto, User
from app.utils.decorators import admin_required

bp = Blueprint("eventos", __name__)
ESTADOS = ("pendiente", "confirmado", "cancelado")


def _autorizado(evento):
    if not (current_user.es_admin or evento.cliente_id == current_user.id):
        abort(403)


def _productos_disponibles(evento=None):
    ids_actuales = [i.producto_id for i in evento.items] if evento else []
    return (Producto.query
            .filter((Producto.activo.is_(True)) | (Producto.id.in_(ids_actuales)))
            .order_by(Producto.tipo, Producto.nombre).all())


def _leer_form(productos):
    nombre = request.form.get("nombre", "").strip()
    lugar = request.form.get("lugar", "").strip()
    notas = request.form.get("notas", "").strip()
    try:
        fecha = datetime.strptime(request.form.get("fecha", ""), "%Y-%m-%dT%H:%M")
    except ValueError:
        fecha = None
    items = []
    for p in productos:
        try:
            c = int(request.form.get(f"cantidad_{p.id}") or 0)
        except ValueError:
            c = 0
        if c > 0:
            items.append((p, c))
    errores = []
    if not nombre:
        errores.append("El nombre es obligatorio.")
    if not lugar:
        errores.append("El lugar es obligatorio.")
    if fecha is None:
        errores.append("Fecha y hora inválidas.")
    if not items:
        errores.append("Selecciona al menos un producto o servicio.")
    return dict(nombre=nombre, lugar=lugar, notas=notas, fecha=fecha), items, errores


@bp.route("/")
@login_required
def listar():
    q = Evento.query
    if not current_user.es_admin:
        q = q.filter_by(cliente_id=current_user.id)
    return render_template("eventos/lista.html", eventos=q.order_by(Evento.fecha).all())


@bp.route("/<int:id>")
@login_required
def detalle(id):
    evento = db.get_or_404(Evento, id)
    _autorizado(evento)
    return render_template("eventos/detalle.html", evento=evento, estados=ESTADOS)


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    productos = _productos_disponibles()
    if request.method == "POST":
        datos, items, errores = _leer_form(productos)
        if errores:
            for e in errores:
                flash(e, "danger")
        else:
            cliente_id = current_user.id
            if current_user.es_admin and request.form.get("cliente_id"):
                cliente_id = int(request.form["cliente_id"])
            evento = Evento(**datos, cliente_id=cliente_id)
            for p, c in items:
                evento.items.append(EventoProducto(producto=p, cantidad=c, precio_unitario=p.precio))
            db.session.add(evento)
            db.session.commit()
            flash("Evento agendado.", "success")
            return redirect(url_for("eventos.detalle", id=evento.id))
    clientes = User.query.filter_by(rol="cliente").all() if current_user.es_admin else []
    return render_template("eventos/form.html", evento=None, productos=productos,
                           cantidades={}, clientes=clientes)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    evento = db.get_or_404(Evento, id)
    _autorizado(evento)
    productos = _productos_disponibles(evento)
    if request.method == "POST":
        datos, items, errores = _leer_form(productos)
        if errores:
            for e in errores:
                flash(e, "danger")
        else:
            for k, v in datos.items():
                setattr(evento, k, v)
            evento.items.clear()
            for p, c in items:
                evento.items.append(EventoProducto(producto=p, cantidad=c, precio_unitario=p.precio))
            db.session.commit()
            flash("Evento actualizado.", "success")
            return redirect(url_for("eventos.detalle", id=evento.id))
    cantidades = {i.producto_id: i.cantidad for i in evento.items}
    return render_template("eventos/form.html", evento=evento, productos=productos,
                           cantidades=cantidades, clientes=[])


@bp.route("/<int:id>/estado", methods=["POST"])
@admin_required
def cambiar_estado(id):
    evento = db.get_or_404(Evento, id)
    estado = request.form.get("estado")
    if estado in ESTADOS:
        evento.estado = estado
        db.session.commit()
        flash("Estado actualizado.", "success")
    return redirect(url_for("eventos.detalle", id=id))


@bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    evento = db.get_or_404(Evento, id)
    _autorizado(evento)
    db.session.delete(evento)
    db.session.commit()
    flash("Evento eliminado.", "success")
    return redirect(url_for("eventos.listar"))
