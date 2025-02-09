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
    height = db.Column(db.Float, nullable=False)
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
    height = FloatField('Height (cm)', validators=[DataRequired(), NumberRange(min=50, max=300)])
    weight = FloatField('Weight (kg)', validators=[DataRequired(), NumberRange(min=10, max=500)])
    submit = SubmitField('Calculate')

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
        height_m = form.height.data / 100
        bmi_result = form.weight.data / (height_m ** 2)
        new_bmi_entry = BMIHistory(user_id=current_user.id, height=form.height.data, weight=form.weight.data, bmi=bmi_result)
        db.session.add(new_bmi_entry)
        db.session.commit()
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

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
