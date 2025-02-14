from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "your_secret_key"

# Initialize Database
db = SQLAlchemy(app)

# Define User Model
class User(db.Model):
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

# Define Workout Log Model
class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_type = db.Column(db.String(50), nullable=False)
    exercise = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)  # Store weight changes
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('workouts', lazy=True))

# Function to calculate BMI
def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)

# Function to calculate TDEE (Total Daily Energy Expenditure)
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

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        age = int(request.form['age'])
        gender = request.form['gender']

        # Convert feet/inches to meters
        feet = int(request.form['feet'])
        inches = int(request.form['inches'])
        height = round(((feet * 12) + inches) * 0.0254, 2)

        # Convert pounds to kilograms
        weight_lbs = float(request.form['weight_lbs'])
        weight = round(weight_lbs * 0.453592, 2)

        activity_level = request.form['activity_level']
        workout_preference = request.form.get('workout_preference')

        new_user = User(username=username, email=email, password=password, age=age, gender=gender,
                        height=height, weight=weight, activity_level=activity_level, workout_preference=workout_preference)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Dashboard Route
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

    workouts = WorkoutLog.query.filter_by(user_id=user.id).order_by(WorkoutLog.date.asc()).all()

    # Extract weight data
    dates = [workout.date.strftime('%Y-%m-%d') for workout in workouts if workout.weight]
    weights = [workout.weight for workout in workouts if workout.weight]
    bmi_values = [calculate_bmi(weight, user.height) for weight in weights]

    # Convert weights to lbs
    weights_lbs = [round(weight * 2.20462, 2) for weight in weights]

    # Generate graph even if no weight data
    plt.figure(figsize=(8, 5))

    if weights_lbs:
        plt.plot(dates, weights_lbs, marker='o', linestyle='-', color='brown', label='Weight (lbs)')
        plt.plot(dates, bmi_values, marker='s', linestyle='--', color='red', label='BMI')
    else:
        # Placeholder data if no weight logged
        plt.plot([], [], marker='o', linestyle='-', color='brown', label='Weight (lbs)')
        plt.plot([], [], marker='s', linestyle='--', color='red', label='BMI')

    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Weight (lbs) / BMI', fontsize=12)
    plt.title(f"{user.username}'s Fitness Progress", fontsize=14)
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('dashboard.html', user=user, bmi=bmi, calorie_plans=calorie_plans, plot_url=plot_url, workouts=workouts)


# Log Workout Route
@app.route('/log_workout', methods=['POST'])
def log_workout():
    if 'user_id' not in session:
        flash('Please log in to track workouts.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    workout_type = request.form['workout_type']
    exercise = request.form['exercise']
    sets = int(request.form['sets'])
    reps = int(request.form['reps'])

    # Convert weight from lbs → kg before storing
    weight_lbs = request.form.get('weight')
    weight_kg = round(float(weight_lbs) / 2.20462, 2) if weight_lbs else None

    new_log = WorkoutLog(user_id=user_id, workout_type=workout_type, exercise=exercise, sets=sets, reps=reps, weight=weight_kg)
    db.session.add(new_log)
    db.session.commit()

    flash('Workout logged successfully!', 'success')
    return redirect(url_for('dashboard'))

# Run Flask App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
