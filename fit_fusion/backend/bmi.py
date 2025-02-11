from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, BMIHistory
from forms import BMIForm

bmi_bp = Blueprint('bmi', __name__)

@bmi_bp.route('/bmi_calculator', methods=['GET', 'POST'])
@login_required
def bmi_calculator():
    form = BMIForm()
    bmi_result = None
    
    if form.validate_on_submit():
        total_height_in = (form.height_ft.data * 12) + form.height_in.data
        height_m = total_height_in * 0.0254
        weight_kg = form.weight.data * 0.453592
        bmi_result = weight_kg / (height_m ** 2)
        
        new_bmi_entry = BMIHistory(user_id=current_user.id, height_ft=form.height_ft.data,
                                   height_in=form.height_in.data, weight=form.weight.data, bmi=bmi_result)
        db.session.add(new_bmi_entry)
        db.session.commit()
        flash(f'BMI calculated successfully: {bmi_result:.2f}', 'success')
        return redirect(url_for('bmi.bmi_calculator'))
    
    bmi_history = BMIHistory.query.filter_by(user_id=current_user.id).all()
    return render_template('bmi_calculator.html', form=form, bmi_result=bmi_result, bmi_history=bmi_history)

@bmi_bp.route('/delete_bmi/<int:entry_id>')
@login_required
def delete_bmi(entry_id):
    bmi_entry = BMIHistory.query.get_or_404(entry_id)
    if bmi_entry.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('bmi.bmi_calculator'))
    
    db.session.delete(bmi_entry)
    db.session.commit()
    flash('BMI entry deleted successfully.', 'success')
    return redirect(url_for('bmi.bmi_calculator'))
