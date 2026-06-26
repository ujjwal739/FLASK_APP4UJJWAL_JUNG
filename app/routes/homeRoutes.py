from flask import Blueprint, render_template
from app.controllers.tipController import get_all_tips
from app.controllers.quizController import get_all_questions
from app.controllers.categoryController import get_all_categories
from app.controllers.commentController import get_all_comments
from app.controllers.announcementController import get_active_announcements
from app.controllers.resourceController import get_all_resources

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    tips = get_all_tips()
    questions = get_all_questions()
    categories = get_all_categories()
    comments = get_all_comments()
    announcements = get_active_announcements()
    resources = get_all_resources()
    return render_template('home.html',
        tips=tips, questions=questions,
        categories=categories, comments=comments,
        announcements=announcements,
        total_tips=len(tips), total_questions=len(questions),
        total_categories=len(categories), total_comments=len(comments),
        total_resources=len(resources)
    )
