from functools import wraps
from flask import session, redirect, url_for

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('public.login'))
        return f(*args, **kwargs)
    return decorated_function