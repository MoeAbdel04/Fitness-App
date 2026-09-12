import os
from flask import Flask
from .extensions import db, jwt, cors


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fitfusion.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    from .routes.auth import auth_bp
    from .routes.profile import profile_bp
    from .routes.workouts import workouts_bp
    from .routes.goals import goals_bp
    from .routes.exercises import exercises_bp
    from .routes.nutrition import nutrition_bp
    from .routes.chatbot import chatbot_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(workouts_bp, url_prefix='/api/workouts')
    app.register_blueprint(goals_bp, url_prefix='/api/goals')
    app.register_blueprint(exercises_bp, url_prefix='/api/exercises')
    app.register_blueprint(nutrition_bp, url_prefix='/api/nutrition')
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')

    with app.app_context():
        db.create_all()
        _seed_exercises()

    return app


def _seed_exercises():
    from .models import Exercise
    from .seed_data import EXERCISES

    if Exercise.query.first():
        return
    for item in EXERCISES:
        db.session.add(Exercise(**item))
    db.session.commit()
