from decimal import Decimal, InvalidOperation
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Producto
from app.utils.decorators import admin_required

bp = Blueprint("productos", __name__)


def _leer_form():
    nombre = request.form.get("nombre", "").strip()
    tipo = request.form.get("tipo", "")
    descripcion = request.form.get("descripcion", "").strip()
    try:
        precio = Decimal(request.form.get("precio", ""))
        if precio < 0:
            raise InvalidOperation
    except InvalidOperation:
        precio = None
    errores = []
    if not nombre:
        errores.append("El nombre es obligatorio.")
    if tipo not in ("servicio", "unidad"):
        errores.append("Tipo inválido.")
    if precio is None:
        errores.append("Precio inválido.")
    return dict(nombre=nombre, tipo=tipo, precio=precio, descripcion=descripcion), errores


@bp.route("/")
@login_required
def listar():
    q = Producto.query
    if not current_user.es_admin:
        q = q.filter_by(activo=True)
    return render_template("productos/lista.html", productos=q.order_by(Producto.tipo, Producto.nombre).all())


@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    if request.method == "POST":
        datos, errores = _leer_form()
        if errores:
            for e in errores:
                flash(e, "danger")
        else:
            db.session.add(Producto(**datos))
            db.session.commit()
            flash("Producto creado.", "success")
            return redirect(url_for("productos.listar"))
    return render_template("productos/form.html", producto=None)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def editar(id):
    producto = db.get_or_404(Producto, id)
    if request.method == "POST":
        datos, errores = _leer_form()
        if errores:
            for e in errores:
                flash(e, "danger")
        else:
            for k, v in datos.items():
                setattr(producto, k, v)
            producto.activo = bool(request.form.get("activo"))
            db.session.commit()
            flash("Producto actualizado.", "success")
            return redirect(url_for("productos.listar"))
    return render_template("productos/form.html", producto=producto)


@bp.route("/<int:id>/eliminar", methods=["POST"])
@admin_required
def eliminar(id):
    producto = db.get_or_404(Producto, id)
    if producto.items:
        producto.activo = False  # tiene historial: se desactiva, no se borra
        flash("El producto está en eventos existentes; se desactivó en lugar de eliminarse.", "warning")
    else:
        db.session.delete(producto)
        flash("Producto eliminado.", "success")
    db.session.commit()
    return redirect(url_for("productos.listar"))
