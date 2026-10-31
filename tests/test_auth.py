import pytest
from app import create_app, db
from app.models import User, Producto
from config import TestConfig


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all(); db.create_all()
        a = User(username="admin", nombre="Admin", rol="admin"); a.set_password("Admin123!")
        c = User(username="cliente", nombre="Cliente", rol="cliente"); c.set_password("cliente1")
        p = Producto(nombre="Sillas", tipo="unidad", precio=2.5)
        db.session.add_all([a, c, p]); db.session.commit()
    return app.test_client()


def login(client, u, p):
    return client.post("/login", data={"username": u, "password": p}, follow_redirects=True)


@pytest.mark.parametrize("url", ["/dashboard", "/productos/", "/eventos/", "/productos/nuevo", "/eventos/nuevo"])
def test_urls_protegidas_redirigen_a_login(client, url):
    r = client.get(url)
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_login_incorrecto(client):
    assert b"incorrectos" in login(client, "admin", "mala").data


def test_password_no_se_guarda_en_claro(client):
    with client.application.app_context():
        u = User.query.filter_by(username="admin").first()
        assert u.password_hash != "Admin123!" and u.check_password("Admin123!")


def test_cliente_no_puede_crear_productos(client):
    login(client, "cliente", "cliente1")
    assert client.get("/productos/nuevo").status_code == 403


def test_admin_crud_producto(client):
    login(client, "admin", "Admin123!")
    client.post("/productos/nuevo", data={"nombre": "DJ", "tipo": "servicio", "precio": "300"})
    assert b"DJ" in client.get("/productos/").data


def test_cliente_agenda_evento_y_logout(client):
    login(client, "cliente", "cliente1")
    r = client.post("/eventos/nuevo", data={"nombre": "Boda", "lugar": "Quito",
                    "fecha": "2030-05-01T18:00", "cantidad_1": "10"}, follow_redirects=True)
    assert b"Boda" in r.data and b"25.00" in r.data
    client.post("/logout")
    assert client.get("/eventos/").status_code == 302
