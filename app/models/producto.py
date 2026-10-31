from app import db


class Producto(db.Model):
    """Catálogo: 'servicio' (precio por servicio) o 'unidad' (precio por unidad)."""
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # servicio | unidad
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    descripcion = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True, nullable=False)

    items = db.relationship("EventoProducto", back_populates="producto")
