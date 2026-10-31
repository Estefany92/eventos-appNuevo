from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=Config):
    """Application factory: permite crear la app con distintas configuraciones."""
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para acceder a esta sección."
    login_manager.login_message_category = "warning"

    from app.models import User  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.controllers.auth import bp as auth_bp
    from app.controllers.main import bp as main_bp
    from app.controllers.productos import bp as productos_bp
    from app.controllers.eventos import bp as eventos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(productos_bp, url_prefix="/productos")
    app.register_blueprint(eventos_bp, url_prefix="/eventos")

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template("403.html"), 403

    from app.cli import register_cli
    register_cli(app)

    with app.app_context():
        db.create_all()

    return app
