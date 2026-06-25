from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.categoryController import *
from app.middleware.authcheck import admin_required

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/')
def list_categories():
    categories = get_all_categories()
    return render_template('categories.html', categories=categories)

@categories_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
    if request.method == 'POST':
        create_category(request.form['name'], request.form.get('description', ''), request.form.get('icon', '🔒'))
        flash('Category created!', 'success')
        return redirect(url_for('categories.list_categories'))
    return render_template('category_form.html', category=None, action='Create')

@categories_bp.route('/<int:cat_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(cat_id):
    category = get_category_by_id(cat_id)
    if request.method == 'POST':
        update_category(cat_id, request.form['name'], request.form.get('description', ''), request.form.get('icon', '🔒'))
        flash('Category updated!', 'success')
        return redirect(url_for('categories.list_categories'))
    return render_template('category_form.html', category=category, action='Edit')

@categories_bp.route('/<int:cat_id>/delete', methods=['POST'])
@admin_required
def delete(cat_id):
    delete_category(cat_id)
    flash('Category deleted.', 'info')
    return redirect(url_for('categories.list_categories'))
