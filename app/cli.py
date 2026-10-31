import click
from app import db
from app.models import User, Producto


def register_cli(app):
    @app.cli.command("seed")
    def seed():
        """Crea un admin y productos de ejemplo: flask --app run seed"""
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", nombre="Administrador", rol="admin")
            admin.set_password("Admin123!")
            db.session.add(admin)
        if Producto.query.count() == 0:
            db.session.add_all([
                Producto(nombre="Sillas tiffany", tipo="unidad", precio=2.50, descripcion="Alquiler por unidad"),
                Producto(nombre="Mesas redondas", tipo="unidad", precio=8.00, descripcion="Mesa para 8 personas"),
                Producto(nombre="Servicio de catering", tipo="servicio", precio=15.00, descripcion="Precio por persona"),
                Producto(nombre="DJ y sonido", tipo="servicio", precio=350.00, descripcion="Hasta 5 horas"),
                Producto(nombre="Decoración floral", tipo="servicio", precio=500.00, descripcion="Paquete básico"),
            ])
        db.session.commit()
        click.echo("Seed listo. Admin: admin / Admin123!")
