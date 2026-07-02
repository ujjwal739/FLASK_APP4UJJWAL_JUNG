from functools import wraps
from flask import session, redirect, url_for, flash, request, abort

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.user_login', next=request.url))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as an administrator.', 'danger')
            return redirect(url_for('auth.admin_login'))
        if session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

# Timeout checks optimized
