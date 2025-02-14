"""
Fit Fusion - Fitness Tracker App
This Flask app allows users to:
✔️ Register & log in
✔️ Track BMI & calorie maintenance
✔️ Log workouts & monitor progress
✔️ Display fitness graphs using Matplotlib
"""

import os
import io
import base64
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import openai
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "your_secret_key"
# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
db = SQLAlchemy(app)

# ───────────────────────────────────────────────
# 📌 USER DATABASE MODEL
# ───────────────────────────────────────────────
class User(db.Model):
    """Stores user details including fitness stats."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Float, nullable=False)  # Stored in meters
    weight = db.Column(db.Float, nullable=False)  # Stored in kg
    activity_level = db.Column(db.String(20), nullable=False)
    workout_preference = db.Column(db.String(20), nullable=True)
    goal = db.Column(db.String(50), nullable=True)

# ───────────────────────────────────────────────
# 📌 WORKOUT LOG MODEL
# ───────────────────────────────────────────────
class WorkoutLog(db.Model):
    """Stores user workout logs and weight updates."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_type = db.Column(db.String(50), nullable=False)
    exercise = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)  # Stored in kg
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('workouts', lazy=True))

# ───────────────────────────────────────────────
# 📌 FITNESS CALCULATIONS
# ───────────────────────────────────────────────
def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (m)."""
    return round(weight / (height ** 2), 2)

def calculate_tdee(user):
    """Calculate TDEE based on activity level."""
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

# ───────────────────────────────────────────────
# 📌 ROUTES
# ───────────────────────────────────────────────
@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        age = int(request.form['age'])
        gender = request.form['gender']
        height = round(((int(request.form['feet']) * 12) + int(request.form['inches'])) * 0.0254, 2)  # Convert inches to meters
        weight = round(float(request.form['weight_lbs']) * 0.453592, 2)  # Convert lbs to kg
        activity_level = request.form['activity_level']
        workout_preference = request.form.get('workout_preference')

        new_user = User(username=username, email=email, password=password, age=age, gender=gender, height=height, weight=weight, activity_level=activity_level, workout_preference=workout_preference)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Render user dashboard with fitness graph."""
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    bmi = calculate_bmi(user.weight, user.height)
    tdee = calculate_tdee(user)

    workouts = WorkoutLog.query.filter_by(user_id=user.id).order_by(WorkoutLog.date.asc()).all()

    dates = [workout.date.strftime('%Y-%m-%d') for workout in workouts if workout.weight]
    weights = [workout.weight for workout in workouts if workout.weight]
    bmi_values = [calculate_bmi(weight, user.height) for weight in weights]

    if dates:
        plt.figure(figsize=(8, 5))
        plt.plot(dates, [w * 2.20462 for w in weights], marker='s', linestyle='-', color='brown', markersize=6, linewidth=2, label='Weight (lbs)')
        plt.plot(dates, bmi_values, marker='o', linestyle='--', color='red', markersize=6, linewidth=2, label='BMI')

        plt.xlabel('Date', fontsize=12, fontweight='bold')
        plt.ylabel('Weight (lbs) / BMI', fontsize=12, fontweight='bold')
        plt.title("Fitness Progress", fontsize=14, fontweight='bold')

        plt.legend()
        plt.grid(True, linestyle='--', linewidth=0.5)
        plt.xticks(rotation=45)
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
    else:
        plot_url = None  

    return render_template('dashboard.html', user=user, bmi=bmi, plot_url=plot_url, workouts=workouts)

@app.route('/log_workout', methods=['POST'])
def log_workout():
    """Log a user's workout with weight conversion."""
    if 'user_id' not in session:
        flash('Please log in to track workouts.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    workout_type = request.form['workout_type']
    exercise = request.form['exercise']
    sets = int(request.form['sets'])
    reps = int(request.form['reps'])

    weight_lbs = request.form.get('weight')
    weight_kg = round(float(weight_lbs) / 2.20462, 2) if weight_lbs else None

    new_log = WorkoutLog(user_id=user_id, workout_type=workout_type, exercise=exercise, sets=sets, reps=reps, weight=weight_kg)
    db.session.add(new_log)
    db.session.commit()
    
    flash('Workout logged successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
