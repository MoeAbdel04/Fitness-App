from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, NumberRange
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

class CalorieTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

class CaloriePlanForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=10, max=100)])
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    height_ft = FloatField('Height (ft)', validators=[DataRequired()])
    height_in = FloatField('Height (in)', validators=[DataRequired()])
    weight = FloatField('Weight (lbs)', validators=[DataRequired(), NumberRange(min=50, max=1000)])
    activity_level = SelectField('Activity Level', choices=[
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('light', 'Lightly active (light exercise/sports 1-3 days/week)'),
        ('moderate', 'Moderately active (moderate exercise/sports 3-5 days/week)'),
        ('very', 'Very active (hard exercise/sports 6-7 days a week)')
    ], validators=[DataRequired()])
    submit = SubmitField('Calculate Maintenance')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    calorie_history = CalorieTracking.query.filter_by(user_id=current_user.id).all()

    # Generate a sample graph for calorie history (if required)
    dates = [entry.date.strftime('%Y-%m-%d') for entry in calorie_history]
    calories = [entry.calories for entry in calorie_history]

    if dates and calories:
        fig, ax = plt.subplots()
        ax.plot(dates, calories, marker='o', linestyle='-')
        ax.set_title('Calorie History Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Calories')
        plt.xticks(rotation=45)
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
    else:
        plot_url = None

    return render_template('dashboard.html', calorie_history=calorie_history, plot_url=plot_url)

@app.route('/calorie_plan', methods=['GET', 'POST'])
@login_required
def calorie_plan():
    form = CaloriePlanForm()
    maintenance_calories = None
    deficit_plan = {}

    if form.validate_on_submit():
        # Calculate BMR
        total_height_in = (form.height_ft.data * 12) + form.height_in.data
        if form.gender.data == 'male':
            bmr = 66 + (6.23 * form.weight.data) + (12.7 * total_height_in) - (6.8 * form.age.data)
        else:
            bmr = 655 + (4.35 * form.weight.data) + (4.7 * total_height_in) - (4.7 * form.age.data)

        # Calculate TDEE (Total Daily Energy Expenditure)
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very': 1.725
        }
        maintenance_calories = bmr * activity_multipliers[form.activity_level.data]

        # Calculate deficit plans
        deficit_plan['light'] = maintenance_calories * 0.9
        deficit_plan['medium'] = maintenance_calories * 0.8
        deficit_plan['extreme'] = maintenance_calories * 0.7

        flash('Calorie maintenance and deficit plans calculated successfully!', 'success')

    return render_template('calorie_plan.html', form=form, maintenance_calories=maintenance_calories, deficit_plan=deficit_plan)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
