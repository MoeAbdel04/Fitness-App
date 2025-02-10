from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitnesspro.db'

# Initialize database and login manager
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import blueprints (to be created later)
from auth import auth_bp
from bmi import bmi_bp
from calorie import calorie_bp
from workout import workout_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(bmi_bp)
app.register_blueprint(calorie_bp)
app.register_blueprint(workout_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
