ACTIVITY_FACTORS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9,
}


def calculate_bmi(weight_kg, height_m):
    if not weight_kg or not height_m:
        return None
    return round(weight_kg / (height_m ** 2), 2)


def calculate_tdee(user):
    height_cm = user.height * 100.0
    if user.gender.lower() == 'male':
        bmr = (10 * user.weight) + (6.25 * height_cm) - (5 * user.age) + 5
    else:
        bmr = (10 * user.weight) + (6.25 * height_cm) - (5 * user.age) - 161
    factor = ACTIVITY_FACTORS.get(user.activity_level, 1.2)
    return round(bmr * factor)


def kg_to_lbs(kg):
    return round(kg / 0.453592, 1) if kg is not None else None


def lbs_to_kg(lbs):
    return round(float(lbs) * 0.453592, 2) if lbs not in (None, '') else None


def meters_to_feet_inches(meters):
    total_inches = round(meters / 0.0254)
    feet = total_inches // 12
    inches = total_inches % 12
    return feet, inches


def feet_inches_to_meters(feet, inches):
    return round(((float(feet) * 12) + float(inches)) * 0.0254, 2)
