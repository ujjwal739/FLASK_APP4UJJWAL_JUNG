from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.controllers.quizController import *
from app.controllers.categoryController import get_all_categories
from app.middleware.authcheck import login_required, admin_required

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/')
def list_questions():
    category_id = request.args.get('category_id', type=int)
    difficulty = request.args.get('difficulty')
    questions = get_all_questions(category_id=category_id, difficulty=difficulty)
    categories = get_all_categories()
    return render_template('quiz.html', questions=questions, categories=categories,
                           selected_category=category_id, selected_difficulty=difficulty)

@quiz_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
    categories = get_all_categories()
    if request.method == 'POST':
        create_question(request.form)
        flash('Quiz question added!', 'success')
        return redirect(url_for('quiz.list_questions'))
    return render_template('quiz_form.html', question=None, categories=categories, action='Create')

@quiz_bp.route('/<int:question_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(question_id):
    question = get_question_by_id(question_id)
    categories = get_all_categories()
    if request.method == 'POST':
        update_question(question_id, request.form)
        flash('Question updated!', 'success')
        return redirect(url_for('quiz.list_questions'))
    return render_template('quiz_form.html', question=question, categories=categories, action='Edit')

@quiz_bp.route('/<int:question_id>/delete', methods=['POST'])
@admin_required
def delete(question_id):
    delete_question(question_id)
    flash('Question deleted.', 'info')
    return redirect(url_for('quiz.list_questions'))

@quiz_bp.route('/check', methods=['POST'])
@login_required
def check():
    data = request.get_json()
    result = check_answer(data['question_id'], data['selected'])
    return jsonify(result)
