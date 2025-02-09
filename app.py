from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitnesspro.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class BMIHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    height_ft = db.Column(db.Float, nullable=False)
    height_in = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

class CalorieTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class BMIForm(FlaskForm):
    height_ft = FloatField('Height (ft)', validators=[DataRequired(message="Please enter the height in feet.")])
    height_in = FloatField('Height (in)', validators=[DataRequired(message="Please enter the height in inches.")])
    weight = FloatField('Weight (lbs)', validators=[DataRequired(message="Please enter the weight in pounds."), NumberRange(min=10, max=1000, message="Weight must be between 10 and 1000 lbs.")])
    submit = SubmitField('Calculate')

class CalorieForm(FlaskForm):
    calories = FloatField('Calories Consumed', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Entry')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters."),
        EqualTo('confirm_password', message='Passwords must match.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/calorie_tracker', methods=['GET', 'POST'])
@login_required
def calorie_tracker():
    form = CalorieForm()
    if form.validate_on_submit():
        new_entry = CalorieTracking(user_id=current_user.id, calories=form.calories.data)
        db.session.add(new_entry)
        db.session.commit()
        flash('Calorie entry added successfully!', 'success')
        return redirect(url_for('calorie_tracker'))
    calorie_history = CalorieTracking.query.filter_by(user_id=current_user.id).order_by(CalorieTracking.date.desc()).all()
    return render_template('calorie_tracker.html', form=form, calorie_history=calorie_history)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    bmi_history = BMIHistory.query.filter_by(user_id=current_user.id).all()
    calorie_history = CalorieTracking.query.filter_by(user_id=current_user.id).all()
    
    # Generate BMI Progress Graph
    dates = [entry.date.strftime('%Y-%m-%d') for entry in bmi_history]
    bmi_values = [entry.bmi for entry in bmi_history]
    
    fig, ax = plt.subplots()
    ax.plot(dates, bmi_values, marker='o', linestyle='-')
    ax.set_title('BMI Progress Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('BMI')
    plt.xticks(rotation=45)
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    
    return render_template('dashboard.html', bmi_history=bmi_history, calorie_history=calorie_history, plot_url=plot_url)

@app.route('/bmi_calculator', methods=['GET', 'POST'])
@login_required
def bmi_calculator():
    form = BMIForm()
    bmi_result = None
    if form.validate_on_submit():
        # Convert height to inches
        total_height_in = (form.height_ft.data * 12) + form.height_in.data
        # Convert height to meters and weight to kg
        height_m = total_height_in * 0.0254
        weight_kg = form.weight.data * 0.453592
        # Calculate BMI
        bmi_result = weight_kg / (height_m ** 2)
        # Save to history
        new_bmi_entry = BMIHistory(user_id=current_user.id, height_ft=form.height_ft.data, height_in=form.height_in.data, weight=form.weight.data, bmi=bmi_result)
        db.session.add(new_bmi_entry)
        db.session.commit()
        flash(f'BMI calculated successfully: {bmi_result:.2f}', 'success')
        return redirect(url_for('bmi_calculator'))
    bmi_history = BMIHistory.query.filter_by(user_id=current_user.id).all()
    return render_template('bmi_calculator.html', form=form, bmi_result=bmi_result, bmi_history=bmi_history)

@app.route('/delete_bmi/<int:entry_id>')
@login_required
def delete_bmi(entry_id):
    bmi_entry = BMIHistory.query.get_or_404(entry_id)
    if bmi_entry.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('bmi_calculator'))
    db.session.delete(bmi_entry)
    db.session.commit()
    flash('BMI entry deleted successfully.', 'success')
    return redirect(url_for('bmi_calculator'))

@app.route('/workout_selection')
@login_required
def workout_selection():
    return render_template('workout_selection.html')

@app.route('/cardio_training')
@login_required
def cardio_training():
    return "Cardio Training Plan Coming Soon"

@app.route('/weight_training')
@login_required
def weight_training():
    return "Weight Training Plan Coming Soon"

@app.route('/strength_training')
@login_required
def strength_training():
    return "Strength Training Plan Coming Soon"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
