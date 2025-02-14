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
        'very active': 1.9
    }
    return round(bmr * activity_factors.get(user.activity_level, 1.2))

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
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        activity_level = request.form['activity_level']
        workout_preference = request.form.get('workout_preference')
        
        new_user = User(username=username, email=email, password=password, age=age, gender=gender, height=height, weight=weight, activity_level=activity_level, workout_preference=workout_preference)
        db.session.add(new_user)
        db.session.commit()
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

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

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

    return render_template('dashboard.html', user=user, bmi=bmi, calorie_plans=calorie_plans, plot_url=url_for('workout_chart'))

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

    new_log = WorkoutLog(user_id=user_id, workout_type=workout_type, exercise=exercise, sets=sets, reps=reps)
    db.session.add(new_log)
    db.session.commit()
    
    flash('Workout logged successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/workout_chart')
def workout_chart():
    if 'user_id' not in session:
        flash('Please log in to view progress.', 'warning')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    workouts = user.workouts

    if not workouts:
        return "No workout data available"

    dates = [workout.date.strftime('%Y-%m-%d') for workout in workouts]
    reps = [workout.reps for workout in workouts]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, reps, marker='o', linestyle='-', color='blue', label='Reps Progress')
    plt.xlabel('Date')
    plt.ylabel('Reps')
    plt.title('Workout Progress Over Time')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('dashboard.html', plot_url=plot_url)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
