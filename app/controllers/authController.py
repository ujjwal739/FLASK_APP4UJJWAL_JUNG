import hashlib
import re
from database import get_db, log_action
from flask import session, request
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    """Enforce strong password policy"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    return True, "OK"

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    """Basic XSS prevention"""
    if not text:
        return text
    return text.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def get_user_by_username(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username=?', (username.strip(),)).fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email=?', (email.strip().lower(),)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_db()
    users = conn.execute('SELECT id,username,email,role,is_active,last_login,failed_attempts,created_at FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return users

def is_account_locked(user):
    if 'locked_until' in user.keys() and user['locked_until']:
        locked_until = datetime.fromisoformat(str(user['locked_until']))
        if datetime.now() < locked_until:
            remaining = int((locked_until - datetime.now()).total_seconds() / 60)
            return True, f"Account locked. Try again in {remaining} minutes."
    return False, ""

def register_user(username, email, password, role='user'):
    # Validate inputs
    if not username or len(username.strip()) < 3:
        return False, 'Username must be at least 3 characters.'
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, 'Username can only contain letters, numbers, and underscores.'
    if not validate_email(email):
        return False, 'Invalid email address.'
    valid_pw, msg = validate_password(password)
    if not valid_pw:
        return False, msg

    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, email, password_hash, role) VALUES (?,?,?,?)',
            (username.strip(), email.strip().lower(), hash_password(password), role)
        )
        conn.commit()
        conn.close()
        log_action(None, username, 'REGISTER', f'New {role} account registered')
        return True, 'Account created successfully!'
    except Exception as e:
        conn.close()
        if 'UNIQUE' in str(e) and 'username' in str(e):
            return False, 'Username already taken.'
        if 'UNIQUE' in str(e) and 'email' in str(e):
            return False, 'Email already registered.'
        return False, 'Registration failed. Please try again.'

def login_user(username, password, required_role=None):
    user = get_user_by_username(username)
    if not user:
        return False, 'Invalid username or password.'

    # Check account lock
    locked, lock_msg = is_account_locked(user)
    if locked:
        return False, lock_msg

    # Check active status
    if not user['is_active']:
        return False, 'Your account has been deactivated. Contact admin.'

    # Verify password
    if user['password_hash'] != hash_password(password):
        # Increment failed attempts
        conn = get_db()
        new_attempts = (user['failed_attempts'] or 0) + 1
        locked_until = None
        if new_attempts >= 5:
            locked_until = (datetime.now() + timedelta(minutes=15)).isoformat()
        conn.execute('UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?',
                     (new_attempts, locked_until, user['id']))
        conn.commit()
        conn.close()
        log_action(user['id'], username, 'LOGIN_FAIL', f'Failed attempt #{new_attempts}', request.remote_addr)
        if new_attempts >= 5:
            return False, 'Too many failed attempts. Account locked for 15 minutes.'
        return False, f'Invalid username or password. ({5 - new_attempts} attempts remaining)'

    if required_role and user['role'] != required_role:
        return False, f'Access denied. This login is for {required_role}s only.'

    # Successful login — reset failed attempts
    conn = get_db()
    conn.execute('UPDATE users SET failed_attempts=0, locked_until=NULL, last_login=CURRENT_TIMESTAMP WHERE id=?', (user['id'],))
    conn.commit()
    conn.close()

    session.permanent = True
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']

    log_action(user['id'], username, 'LOGIN', 'Successful login', request.remote_addr)
    return True, user

def logout_user():
    username = session.get('username', 'unknown')
    user_id = session.get('user_id')
    log_action(user_id, username, 'LOGOUT', 'User logged out', request.remote_addr)
    session.clear()

def delete_user(user_id):
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

def update_user_role(user_id, role):
    conn = get_db()
    conn.execute('UPDATE users SET role=? WHERE id=?', (role, user_id))
    conn.commit()
    conn.close()

def toggle_user_active(user_id):
    conn = get_db()
    conn.execute('UPDATE users SET is_active = CASE WHEN is_active=1 THEN 0 ELSE 1 END WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

def get_audit_log(limit=50):
    conn = get_db()
    logs = conn.execute('SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return logs

def is_logged_in():
    return 'user_id' in session

def is_admin():
    return session.get('role') == 'admin'

def current_user():
    if 'user_id' in session:
        return get_user_by_id(session['user_id'])
    return None
