# 🎉 Gestión de Eventos — Flask + MVC + CRUD + Login

Aplicación web para una empresa de eventos: permite **agendar eventos** en una fecha y asociarles
**productos/servicios** (con precio y cantidad) que viven en la base de datos.
Incluye autenticación y **dos roles**: `admin` y `cliente`.

## Características

| Módulo | Administrador | Cliente |
|---|---|---|
| Login / Logout | ✅ | ✅ |
| Registro de cuenta | — | ✅ (rol `cliente` automático) |
| Productos y servicios (CRUD) | ✅ crear, ver, editar, eliminar | 👁 solo ver activos |
| Eventos (CRUD) | ✅ todos los eventos, asignar cliente, cambiar estado | ✅ solo los suyos |
| Total del evento | ✅ | ✅ |

- **Productos**: tipo `unidad` (se cobra por cantidad) o `servicio`, con precio.
- **Eventos**: nombre, fecha y hora, lugar, notas, estado (`pendiente` / `confirmado` / `cancelado`).
- El precio se **congela** en el detalle del evento (si el catálogo cambia, los eventos pasados no se alteran).
- Un producto ya usado en eventos no se borra: se **desactiva**.

## Arquitectura (MVC)

```
eventos_app/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── cli.py               # Comando `flask seed`
│   ├── models/              # M — SQLAlchemy: User, Producto, Evento, EventoProducto
│   ├── controllers/         # C — Blueprints: auth, main, productos, eventos
│   ├── views/               # V — Plantillas Jinja2 (base, auth/, productos/, eventos/)
│   ├── static/css/
│   └── utils/decorators.py  # @admin_required
├── tests/                   # pytest
├── config.py
├── run.py
└── requirements.txt
```

Modelo de datos:

```
users 1───* eventos 1───* evento_productos *───1 productos
```

## Seguridad / Login

- Todas las rutas (excepto `/login` y `/registro`) usan `@login_required`; sin sesión → redirección a `/login?next=...`.
- Rutas de administración usan `@admin_required` → `403` si el rol es cliente.
- **Contraseñas**: se guardan **hasheadas con sal** (`werkzeug.security`, scrypt/PBKDF2).
  > Se evita MD5 deliberadamente: es rápido y vulnerable a ataques de diccionario/rainbow tables.
  > El requisito de "encriptación" se cumple con un hash robusto; la contraseña nunca se guarda en claro.
- **CSRF** en todos los formularios (Flask-WTF) y logout por `POST`.
- Protección contra *open redirect* en el parámetro `next`.

## Instalación y ejecución

```bash
git clone <URL-DEL-REPO> && cd eventos_app
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

flask --app run seed             # crea admin y productos de ejemplo
flask --app run run --debug      # http://127.0.0.1:5000
```

**Usuario administrador de prueba:** `admin` / `Admin123!` (cámbialo en producción).
Los clientes se registran desde `/registro`.

Variables de entorno opcionales: `SECRET_KEY`, `DATABASE_URL` (p. ej. PostgreSQL).

## Pruebas

```bash
pytest -q
```
Cubren: URLs protegidas sin sesión, login incorrecto, hash de contraseña, permisos por rol,
CRUD de productos y flujo de agendar evento + logout.

## Flujo de Git recomendado

```
main      → versión estable
develop   → integración
feature/* → una rama por funcionalidad (feature/crud-productos, feature/login...)
```
Commits con prefijos: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`.

## Hoja de ruta (para escalar)

1. Migraciones con **Flask-Migrate/Alembic** y PostgreSQL.
2. Validación de **disponibilidad** (evitar choques de fecha/lugar/stock de unidades).
3. Capa `services/` para mover lógica de negocio fuera de los controladores.
4. CRUD de usuarios para el admin y recuperación de contraseña.
5. Formularios con Flask-WTF, paginación, búsqueda y calendario visual (FullCalendar).
6. API REST (`/api/v1`) para app móvil, y despliegue con Gunicorn + Docker.
