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

class BMIHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    height_ft = db.Column(db.Float, nullable=False)
    height_in = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

class BMIForm(FlaskForm):
    height_ft = FloatField('Height (ft)', validators=[DataRequired()])
    height_in = FloatField('Height (in)', validators=[DataRequired()])
    weight = FloatField('Weight (lbs)', validators=[DataRequired(), NumberRange(min=10, max=1000)])
    submit = SubmitField('Calculate BMI')

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
    bmi_history = BMIHistory.query.filter_by(user_id=current_user.id).all()

    dates = [entry.date.strftime('%Y-%m-%d') for entry in bmi_history]
    bmi_values = [entry.bmi for entry in bmi_history]

    if dates and bmi_values:
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
    else:
        plot_url = None

    return render_template('dashboard.html', bmi_history=bmi_history, plot_url=plot_url)

@app.route('/bmi_calculator', methods=['GET', 'POST'])
@login_required
def bmi_calculator():
    form = BMIForm()
    bmi_result = None

    if form.validate_on_submit():
        total_height_in = (form.height_ft.data * 12) + form.height_in.data
        height_m = total_height_in * 0.0254
        weight_kg = form.weight.data * 0.453592
        bmi_result = weight_kg / (height_m ** 2)

        new_bmi_entry = BMIHistory(
            user_id=current_user.id,
            height_ft=form.height_ft.data,
            height_in=form.height_in.data,
            weight=form.weight.data,
            bmi=bmi_result
        )
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
