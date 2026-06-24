from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.authController import *
from app.middleware.authcheck import admin_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def user_login():
    if is_logged_in():
        return redirect(url_for('home.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')
        success, result = login_user(username, password)
        if success:
            flash(f'Welcome back, {result["username"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home.index'))
        flash(result, 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect(url_for('home.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        pw = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if pw != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', username=username, email=email)
        success, msg = register_user(username, email, pw, role='user')
        if success:
            flash(msg + ' Please log in.', 'success')
            return redirect(url_for('auth.user_login'))
        flash(msg, 'danger')
        return render_template('register.html', username=username, email=email)
    return render_template('register.html')

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_logged_in() and is_admin():
        return redirect(url_for('auth.admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        success, result = login_user(username, password, required_role='admin')
        if success:
            flash(f'Admin access granted. Welcome, {result["username"]}!', 'success')
            return redirect(url_for('auth.admin_dashboard'))
        flash(result, 'danger')
    return render_template('admin_login.html')

@auth_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    from app.controllers.tipController import get_all_tips
    from app.controllers.quizController import get_all_questions
    from app.controllers.commentController import get_all_comments
    from app.controllers.categoryController import get_all_categories
    from app.controllers.resourceController import get_pending_resources
    users = get_all_users()
    audit = get_audit_log(30)
    return render_template('admin_dashboard.html',
        users=users, audit=audit,
        total_users=len(users),
        total_tips=len(get_all_tips()),
        total_questions=len(get_all_questions()),
        total_comments=len(get_all_comments()),
        total_categories=len(get_all_categories()),
        pending_resources=len(get_pending_resources())
    )

@auth_bp.route('/admin/users/<int:user_id>/role', methods=['POST'])
@admin_required
def change_role(user_id):
    if session['user_id'] == user_id:
        flash("You can't change your own role.", 'danger')
    else:
        update_user_role(user_id, request.form['role'])
        flash('User role updated.', 'success')
        log_action(session['user_id'], session['username'], 'ROLE_CHANGE', f'Changed user #{user_id} role to {request.form["role"]}', request.remote_addr)
    return redirect(url_for('auth.admin_dashboard'))

@auth_bp.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    if session['user_id'] == user_id:
        flash("You can't deactivate your own account.", 'danger')
    else:
        toggle_user_active(user_id)
        flash('User status updated.', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user_route(user_id):
    if session['user_id'] == user_id:
        flash("You can't delete your own account.", 'danger')
    else:
        log_action(session['user_id'], session['username'], 'DELETE_USER', f'Deleted user #{user_id}', request.remote_addr)
        delete_user(user_id)
        flash('User deleted.', 'info')
    return redirect(url_for('auth.admin_dashboard'))

@auth_bp.route('/logout')
def logout():
    role = session.get('role')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.admin_login') if role == 'admin' else url_for('auth.user_login'))

@auth_bp.route('/profile')
def profile():
    if not is_logged_in():
        return redirect(url_for('auth.user_login'))
    user = current_user()
    return render_template('profile.html', user=user)
