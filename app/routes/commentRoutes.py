from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.commentController import *
from app.middleware.authcheck import admin_required

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/')
def list_comments():
    comments = get_all_comments()
    return render_template('comments.html', comments=comments)

@comments_bp.route('/<int:comment_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(comment_id):
    conn = __import__('database').get_db()
    comment = conn.execute('SELECT * FROM comments WHERE id=?', (comment_id,)).fetchone()
    conn.close()
    if request.method == 'POST':
        update_comment(comment_id, request.form['author_name'], request.form['content'])
        flash('Comment updated!', 'success')
        return redirect(url_for('comments.list_comments'))
    return render_template('comment_form.html', comment=comment)

@comments_bp.route('/<int:comment_id>/delete', methods=['POST'])
@admin_required
def delete(comment_id):
    delete_comment(comment_id)
    flash('Comment deleted.', 'info')
    return redirect(url_for('comments.list_comments'))

@comments_bp.route('/<int:comment_id>/toggle', methods=['POST'])
@admin_required
def toggle(comment_id):
    toggle_approve(comment_id)
    return redirect(url_for('comments.list_comments'))
