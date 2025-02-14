from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    activity_level = db.Column(db.String(20), nullable=False)
    workout_preference = db.Column(db.String(20), nullable=True)
    goal = db.Column(db.String(50), nullable=True)  # New field for workout goal

class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_type = db.Column(db.String(50), nullable=False)
    exercise = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('workouts', lazy=True))

def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)

def calculate_tdee(user):
    if user.gender.lower() == 'male':
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) + 5
    else:
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) - 161
    
    activity_factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    return round(bmr * activity_factors.get(user.activity_level, 1.2))

def generate_workout_plan(user):
    """Generate a workout plan based on user goal"""
    plans = {
        "fat_loss": ["HIIT Workouts", "Treadmill Running", "Jump Rope", "Cycling"],
        "muscle_gain": ["Bench Press", "Deadlifts", "Squats", "Overhead Press"],
        "strength_training": ["Pull-ups", "Planks", "Kettlebell Swings", "Farmer's Walk"]
    }
    return plans.get(user.goal, ["General Fitness Routine"])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/set_goal', methods=['POST'])
def set_goal():
    if 'user_id' not in session:
        flash('Please log in to set your fitness goal.', 'warning')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    user.goal = request.form['goal']
    
    db.session.commit()
    flash('Your goal has been updated!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    bmi = calculate_bmi(user.weight, user.height)
    tdee = calculate_tdee(user)
    
    calorie_plans = {
        'maintenance': tdee,
        'light_deficit': tdee - 250,
        'medium_deficit': tdee - 500,
        'extreme_deficit': tdee - 750
    }

    workouts = WorkoutLog.query.filter_by(user_id=user.id).order_by(WorkoutLog.date.desc()).all()
    workout_plan = generate_workout_plan(user)

    return render_template('dashboard.html', user=user, bmi=bmi, calorie_plans=calorie_plans, plot_url=url_for('workout_chart'), workouts=workouts, workout_plan=workout_plan)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
