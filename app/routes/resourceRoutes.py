from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.resourceController import *
from app.controllers.categoryController import get_all_categories
from app.middleware.authcheck import login_required, admin_required

resources_bp = Blueprint('resources', __name__)

RESOURCE_TYPES = ['article', 'video', 'tool', 'guide', 'course']

@resources_bp.route('/')
def list_resources():
    category_id = request.args.get('category_id', type=int)
    resource_type = request.args.get('resource_type')
    # Admins see all, users see only approved
    approved_only = session.get('role') != 'admin'
    resources = get_all_resources(category_id=category_id, resource_type=resource_type, approved_only=approved_only)
    categories = get_all_categories()
    pending_count = len(get_pending_resources()) if session.get('role') == 'admin' else 0
    return render_template('resources.html',
        resources=resources, categories=categories,
        resource_types=RESOURCE_TYPES,
        selected_category=category_id,
        selected_type=resource_type,
        pending_count=pending_count
    )

@resources_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
    categories = get_all_categories()
    if request.method == 'POST':
        create_resource(
            request.form['title'], request.form['url'],
            request.form.get('description', ''),
            request.form.get('resource_type', 'article'),
            request.form.get('category_id'),
            session.get('username', 'admin'),
            approved=1
        )
        flash('Resource added!', 'success')
        return redirect(url_for('resources.list_resources'))
    return render_template('resource_form.html', resource=None, categories=categories,
                           resource_types=RESOURCE_TYPES, action='Create')

@resources_bp.route('/suggest', methods=['GET', 'POST'])
@login_required
def suggest():
    categories = get_all_categories()
    if request.method == 'POST':
        create_resource(
            request.form['title'], request.form['url'],
            request.form.get('description', ''),
            request.form.get('resource_type', 'article'),
            request.form.get('category_id'),
            session.get('username', 'user'),
            approved=0  # Pending admin approval
        )
        flash('Resource submitted for review! Admin will approve it shortly.', 'success')
        return redirect(url_for('resources.list_resources'))
    return render_template('resource_form.html', resource=None, categories=categories,
                           resource_types=RESOURCE_TYPES, action='Suggest')

@resources_bp.route('/<int:res_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(res_id):
    resource = get_resource_by_id(res_id)
    categories = get_all_categories()
    if request.method == 'POST':
        update_resource(
            res_id,
            request.form['title'], request.form['url'],
            request.form.get('description', ''),
            request.form.get('resource_type', 'article'),
            request.form.get('category_id'),
            1 if request.form.get('approved') else 0
        )
        flash('Resource updated!', 'success')
        return redirect(url_for('resources.list_resources'))
    return render_template('resource_form.html', resource=resource, categories=categories,
                           resource_types=RESOURCE_TYPES, action='Edit')

@resources_bp.route('/<int:res_id>/toggle', methods=['POST'])
@admin_required
def toggle(res_id):
    toggle_resource_approval(res_id)
    flash('Resource approval status updated.', 'info')
    return redirect(url_for('resources.list_resources'))

@resources_bp.route('/<int:res_id>/delete', methods=['POST'])
@admin_required
def delete(res_id):
    delete_resource(res_id)
    flash('Resource deleted.', 'info')
    return redirect(url_for('resources.list_resources'))
