from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="cliente")  # admin | cliente
    activo = db.Column(db.Boolean, default=True, nullable=False)

    eventos = db.relationship("Evento", back_populates="cliente")

    def set_password(self, password):
        # Hash con sal (scrypt/pbkdf2 según versión de Werkzeug), mucho más seguro que MD5.
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def es_admin(self):
        return self.rol == "admin"
