from app import db


class Evento(db.Model):
    __tablename__ = "eventos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, index=True)
    lugar = db.Column(db.String(200), nullable=False)
    notas = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")  # pendiente|confirmado|cancelado
    cliente_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    cliente = db.relationship("User", back_populates="eventos")
    items = db.relationship("EventoProducto", back_populates="evento",
                            cascade="all, delete-orphan")

    @property
    def total(self):
        return sum(i.subtotal for i in self.items)


class EventoProducto(db.Model):
    """Detalle: guarda el precio al momento de reservar (histórico estable)."""
    __tablename__ = "evento_productos"
    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    evento = db.relationship("Evento", back_populates="items")
    producto = db.relationship("Producto", back_populates="items")

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
