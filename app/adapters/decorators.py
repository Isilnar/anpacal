from functools import wraps

from flask import redirect, url_for
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return redirect(url_for("auth.user_not_allowed"))

        return f(*args, **kwargs)

    return decorated_function
