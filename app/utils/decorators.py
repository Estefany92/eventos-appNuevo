from functools import wraps
from flask import abort
from flask_login import current_user, login_required


def admin_required(f):
    """Requiere sesión iniciada y rol administrador."""
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.es_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper
