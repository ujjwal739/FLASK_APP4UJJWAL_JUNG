from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.announcementController import *
from app.middleware.authcheck import admin_required

announcements_bp = Blueprint('announcements', __name__)

@announcements_bp.route('/')
def list_announcements():
    announcements = get_all_announcements()
    return render_template('announcements.html', announcements=announcements)

@announcements_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
    if request.method == 'POST':
        create_announcement(
            request.form['title'],
            request.form['content'],
            request.form.get('severity', 'info'),
            request.form.get('expires_at') or None,
            session.get('username', 'admin')
        )
        flash('Announcement published!', 'success')
        return redirect(url_for('announcements.list_announcements'))
    return render_template('announcement_form.html', ann=None, action='Create')

@announcements_bp.route('/<int:ann_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(ann_id):
    ann = get_announcement_by_id(ann_id)
    if request.method == 'POST':
        update_announcement(
            ann_id,
            request.form['title'],
            request.form['content'],
            request.form.get('severity', 'info'),
            request.form.get('expires_at') or None,
            1 if request.form.get('is_active') else 0
        )
        flash('Announcement updated!', 'success')
        return redirect(url_for('announcements.list_announcements'))
    return render_template('announcement_form.html', ann=ann, action='Edit')

@announcements_bp.route('/<int:ann_id>/toggle', methods=['POST'])
@admin_required
def toggle(ann_id):
    toggle_announcement(ann_id)
    return redirect(url_for('announcements.list_announcements'))

@announcements_bp.route('/<int:ann_id>/delete', methods=['POST'])
@admin_required
def delete(ann_id):
    delete_announcement(ann_id)
    flash('Announcement deleted.', 'info')
    return redirect(url_for('announcements.list_announcements'))
