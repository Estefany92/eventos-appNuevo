from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Evento, Producto

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    q = Evento.query.filter(Evento.fecha >= datetime.now())
    if not current_user.es_admin:
        q = q.filter_by(cliente_id=current_user.id)
    proximos = q.order_by(Evento.fecha).limit(5).all()
    return render_template("dashboard.html", proximos=proximos,
                           total_productos=Producto.query.filter_by(activo=True).count())
