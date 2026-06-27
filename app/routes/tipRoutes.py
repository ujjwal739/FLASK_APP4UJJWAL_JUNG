from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.tipController import *
from app.controllers.categoryController import get_all_categories
from app.controllers.commentController import get_comments_for_tip, add_comment
from app.middleware.authcheck import login_required, admin_required

tips_bp = Blueprint('tips', __name__)

@tips_bp.route('/')
def list_tips():
    category_id = request.args.get('category_id', type=int)
    severity = request.args.get('severity')
    tips = get_all_tips(category_id=category_id, severity=severity)
    categories = get_all_categories()
    return render_template('tips.html', tips=tips, categories=categories,
                           selected_category=category_id, selected_severity=severity)

@tips_bp.route('/<int:tip_id>')
def view_tip(tip_id):
    tip = get_tip_by_id(tip_id)
    comments = get_comments_for_tip(tip_id)
    categories = get_all_categories()
    return render_template('tip_detail.html', tip=tip, comments=comments, categories=categories)

@tips_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
    categories = get_all_categories()
    if request.method == 'POST':
        create_tip(request.form['title'], request.form['content'],
                   request.form.get('category_id'), request.form.get('severity', 'medium'))
        flash('Security tip added successfully!', 'success')
        return redirect(url_for('tips.list_tips'))
    return render_template('tip_form.html', tip=None, categories=categories, action='Create')

@tips_bp.route('/<int:tip_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(tip_id):
    tip = get_tip_by_id(tip_id)
    categories = get_all_categories()
    if request.method == 'POST':
        update_tip(tip_id, request.form['title'], request.form['content'],
                   request.form.get('category_id'), request.form.get('severity', 'medium'))
        flash('Tip updated successfully!', 'success')
        return redirect(url_for('tips.list_tips'))
    return render_template('tip_form.html', tip=tip, categories=categories, action='Edit')

@tips_bp.route('/<int:tip_id>/delete', methods=['POST'])
@admin_required
def delete(tip_id):
    delete_tip(tip_id)
    flash('Tip deleted.', 'info')
    return redirect(url_for('tips.list_tips'))

@tips_bp.route('/<int:tip_id>/comment', methods=['POST'])
@login_required
def post_comment(tip_id):
    add_comment(tip_id, request.form['author_name'], request.form['content'])
    flash('Comment posted!', 'success')
    return redirect(url_for('tips.view_tip', tip_id=tip_id))
