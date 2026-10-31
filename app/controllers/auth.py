from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

bp = Blueprint("auth", __name__)


def _next_seguro(destino):
    """Evita open-redirect: solo rutas internas."""
    if destino and destino.startswith("/") and not destino.startswith("//"):
        return destino
    return url_for("main.dashboard")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        user = User.query.filter_by(username=username).first()
        if user and user.activo and user.check_password(request.form.get("password", "")):
            login_user(user)
            return redirect(_next_seguro(request.args.get("next")))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("auth/login.html")


@bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        nombre = request.form.get("nombre", "").strip()
        password = request.form.get("password", "")
        if not username or not nombre or len(password) < 6:
            flash("Completa todos los campos (contraseña mínimo 6 caracteres).", "danger")
        elif User.query.filter_by(username=username).first():
            flash("Ese usuario ya existe.", "danger")
        else:
            user = User(username=username, nombre=nombre, rol="cliente")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Cuenta creada. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/registro.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
