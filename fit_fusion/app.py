import os
from dotenv import load_dotenv
load_dotenv()  # Loads environment variables from .env file

import openai  # This code assumes openai==0.28.1 is installed
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Mail configuration (for welcome emails)
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "your_email@domain.com")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "your_email_password")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER", "your_email@domain.com")

mail = Mail(app)
db = SQLAlchemy(app)

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")

# Models
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

# Utility functions
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

def height_to_feet_inches(meters):
    total_inches = round(meters / 0.0254)
    feet = total_inches // 12
    inches = total_inches % 12
    return f"{feet}' {inches}\""

# Register custom filter for templates
app.jinja_env.filters['height_to_feet_inches'] = height_to_feet_inches

# Routes
@app.route('/')
def home():
    return render_template('index.html')

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
                        height=height, weight=weight, activity_level=activity_level,
                        workout_preference=workout_preference)
        db.session.add(new_user)
        db.session.commit()

        # Send welcome email
        try:
            msg = Message("Welcome to Fit Fusion!",
                          recipients=[email])
            msg.body = f"Hello {username},\n\nThank you for signing up for Fit Fusion. We're excited to help you reach your fitness goals!\n\nBest,\nThe Fit Fusion Team"
            mail.send(msg)
        except Exception as e:
            flash(f"User registered, but failed to send welcome email: {str(e)}", "warning")

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

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

# On-site Forgot Password Feature (No email verification)
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            session['reset_email'] = email
            flash('Email verified. You can now reset your password on-site.', 'info')
            return redirect(url_for('reset_password'))
        else:
            flash('No account found with that email address.', 'warning')
            return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        flash('Please use the forgot password form first.', 'warning')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        new_password = request.form.get('password')
        email = session.get('reset_email')
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            session.pop('reset_email', None)
            flash('Your password has been updated. Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('forgot_password'))
    return render_template('reset_password.html')

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
    dates = [workout.date.strftime('%Y-%m-%d') for workout in workouts if workout.weight]
    weights = [workout.weight for workout in workouts if workout.weight]
    bmi_values = [calculate_bmi(weight, user.height) for weight in weights]
    if dates:
        plt.figure(figsize=(8, 5))
        plt.plot(dates, [w * 2.20462 for w in weights], marker='s', linestyle='-', color='brown', markersize=6, linewidth=2, label='Weight (lbs)')
        plt.plot(dates, bmi_values, marker='s', linestyle='--', color='red', markersize=6, linewidth=2, label='BMI')
        plt.xlabel('Date', fontsize=12, fontweight='bold')
        plt.ylabel('Weight (lbs) / BMI', fontsize=12, fontweight='bold')
        plt.title(f"{user.username}'s Fitness Progress", fontsize=14, fontweight='bold')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', linewidth=0.5)
        plt.tight_layout()
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
    else:
        plot_url = None
    if user.workout_preference:
        pref = user.workout_preference.lower()
        if 'cardio' in pref:
            recommended_workout = "Try a 30-minute run or cycling session."
        elif 'weight' in pref:
            recommended_workout = "Consider a full-body strength training routine."
        elif 'strength' in pref:
            recommended_workout = "Focus on compound lifts like squats, deadlifts, and bench press."
        else:
            recommended_workout = "Keep up the great work with your fitness routine!"
    else:
        recommended_workout = "Keep up the great work with your fitness routine!"
    return render_template('dashboard.html', user=user, bmi=bmi, calorie_plans=calorie_plans,
                           plot_url=plot_url, workouts=workouts, recommended_workout=recommended_workout)

@app.route('/workout_chart')
def workout_chart():
    if 'user_id' not in session:
        flash('Please log in to view progress.', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    workouts = WorkoutLog.query.filter_by(user_id=user.id).order_by(WorkoutLog.date.asc()).all()
    dates = [workout.date.strftime('%Y-%m-%d') for workout in workouts if workout.weight]
    weights = [workout.weight for workout in workouts if workout.weight]
    bmi_values = [calculate_bmi(weight, user.height) for weight in weights]
    if not dates:
        flash('No valid weight data available to generate the graph.', 'warning')
        return redirect(url_for('dashboard'))
    plt.figure(figsize=(8, 5))
    plt.plot(dates, [w * 2.20462 for w in weights], marker='s', linestyle='-', color='brown', markersize=6, linewidth=2, label='Weight (lbs)')
    plt.plot(dates, bmi_values, marker='s', linestyle='--', color='red', markersize=6, linewidth=2, label='BMI')
    plt.xlabel('Date', fontsize=12, fontweight='bold')
    plt.ylabel('Weight (lbs) / BMI', fontsize=12, fontweight='bold')
    plt.title(f"{user.username}'s Fitness Progress", fontsize=14, fontweight='bold')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('dashboard.html', plot_url=plot_url)

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
    weight_lbs = request.form.get('weight')
    weight_kg = round(float(weight_lbs) / 2.20462, 2) if weight_lbs else None
    new_log = WorkoutLog(user_id=user_id, workout_type=workout_type, exercise=exercise,
                         sets=sets, reps=reps, weight=weight_kg)
    db.session.add(new_log)
    db.session.commit()
    flash('Workout logged successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to view profile.', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        age = int(request.form['age'])
        gender = request.form['gender']
        feet = int(request.form['feet'])
        inches = int(request.form['inches'])
        height = round(((feet * 12) + inches) * 0.0254, 2)
        weight_lbs = float(request.form['weight_lbs'])
        weight = round(weight_lbs * 0.453592, 2)
        activity_level = request.form['activity_level']
        workout_preference = request.form.get('workout_preference')
        goal = request.form.get('goal')
        user.username = username
        user.email = email
        user.age = age
        user.gender = gender
        user.height = height
        user.weight = weight
        user.activity_level = activity_level
        user.workout_preference = workout_preference
        user.goal = goal
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    total_inches = round(user.height / 0.0254)
    feet = total_inches // 12
    inches = total_inches % 12
    weight_lbs = round(user.weight * 2.20462, 1)
    return render_template('profile.html', user=user, feet=feet, inches=inches, weight_lbs=weight_lbs)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# New route for Tutorials & Interactive Q&A
@app.route('/tutorials')
def tutorials():
    return render_template('tutorials.html')

# New route for Multimedia Integration
@app.route('/multimedia')
def multimedia():
    return render_template('multimedia.html')

# New route for Real-Time Exercise Analysis (if needed)
@app.route('/exercise')
def exercise():
    return render_template('exercise.html')

# New route for Downloading User Data as JSON
@app.route('/download_data')
def download_data():
    if 'user_id' not in session:
        flash('Please log in to download your data.', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    user_data = {
        "username": user.username,
        "email": user.email,
        "age": user.age,
        "gender": user.gender,
        "height": user.height,
        "weight": user.weight,
        "activity_level": user.activity_level,
        "workout_preference": user.workout_preference,
        "goal": user.goal,
    }
    workout_logs = []
    for log in user.workouts:
        workout_logs.append({
            "workout_type": log.workout_type,
            "exercise": log.exercise,
            "sets": log.sets,
            "reps": log.reps,
            "weight": log.weight,
            "date": log.date.strftime("%Y-%m-%d %H:%M:%S")
        })
    user_data["workout_logs"] = workout_logs
    json_data = json.dumps(user_data, indent=4)
    return Response(json_data, mimetype='application/json',
                    headers={"Content-Disposition": "attachment;filename=user_data.json"})

# New route for Privacy Tab (Display user personal info and data download)
@app.route('/privacy')
def privacy():
    if 'user_id' not in session:
        flash('Please log in to view privacy information.', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('privacy.html', user=user)

# Chat API route for Fit Bot using the old ChatCompletion interface
@app.route('/chat_api', methods=['POST'])
def chat_api():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user_message = request.json.get('message', '')
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Fit Bot, an AI fitness assistant. Provide helpful advice on workouts, nutrition, "
                        "and overall fitness. If the user's question is related to exercise techniques or proper form, "
                        "reference the interactive tutorials available in the app."
                    )
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        ai_response = response.choices[0].message.content.strip()
        return jsonify({"response": f"Fit Bot: {ai_response}"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
