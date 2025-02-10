from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, CalorieTracking
from forms import CaloriePlanForm

calorie_bp = Blueprint('calorie', __name__)

@calorie_bp.route('/calorie_plan', methods=['GET', 'POST'])
@login_required
def calorie_plan():
    form = CaloriePlanForm()
    maintenance_calories = None
    deficit_plan = {}
    
    if form.validate_on_submit():
        total_height_in = (form.height_ft.data * 12) + form.height_in.data
        if form.gender.data == 'male':
            bmr = 66 + (6.23 * form.weight.data) + (12.7 * total_height_in) - (6.8 * form.age.data)
        else:
            bmr = 655 + (4.35 * form.weight.data) + (4.7 * total_height_in) - (4.7 * form.age.data)
        
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very': 1.725
        }
        
        maintenance_calories = bmr * activity_multipliers[form.activity_level.data]
        deficit_plan['light'] = maintenance_calories * 0.9
        deficit_plan['medium'] = maintenance_calories * 0.8
        deficit_plan['extreme'] = maintenance_calories * 0.7
        
        flash('Calorie maintenance and deficit plans calculated successfully!', 'success')
        return render_template('calorie_plan.html', form=form, maintenance_calories=maintenance_calories, deficit_plan=deficit_plan)
    
    return render_template('calorie_plan.html', form=form, maintenance_calories=maintenance_calories, deficit_plan=deficit_plan)
