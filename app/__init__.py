import os
from flask import Flask, render_template
from config import config
from database import init_db

def create_app(config_name='default'):
    app = Flask(__name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    app.config.from_object(config[config_name])

    init_db()

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # Custom error pages
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Register blueprints
    from app.routes.authRoutes import auth_bp
    from app.routes.homeRoutes import home_bp
    from app.routes.tipRoutes import tips_bp
    from app.routes.quizRoutes import quiz_bp
    from app.routes.commentRoutes import comments_bp
    from app.routes.categoryRoutes import categories_bp
    from app.routes.announcementRoutes import announcements_bp
    from app.routes.resourceRoutes import resources_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(tips_bp, url_prefix='/tips')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(comments_bp, url_prefix='/comments')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(announcements_bp, url_prefix='/announcements')
    app.register_blueprint(resources_bp, url_prefix='/resources')

    return app
