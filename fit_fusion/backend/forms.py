from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class BMIForm(FlaskForm):
    height_ft = FloatField('Height (ft)', validators=[DataRequired()])
    height_in = FloatField('Height (in)', validators=[DataRequired()])
    weight = FloatField('Weight (lbs)', validators=[DataRequired(), NumberRange(min=10, max=1000)])
    submit = SubmitField('Calculate BMI')

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
    submit = SubmitField('Calculate Maintenance and Plan')
