# accounts/utils.py

def calculate_bmr(age, weight, height, sexe):
    """
    Calcule le métabolisme de base (BMR) selon la formule Mifflin-St Jeor
    
    Args:
        age: âge en années
        weight: poids en kg
        height: taille en cm
        sexe: 'M' pour homme, 'F' pour femme
    
    Returns:
        int: BMR en calories par jour
    """
    if not all([age, weight, height, sexe]):
        return None
    
    try:
        age = int(age)
        weight = float(weight)
        height = float(height)
        
        if sexe == 'M':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        elif sexe == 'F':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            # Valeur par défaut entre homme et femme
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 78
        return round(bmr)
    except (ValueError, TypeError):
        return None


def calculate_daily_calories(bmr, activity_level='sedentary'):
    """
    Calcule les besoins caloriques journaliers selon le niveau d'activité
    
    Args:
        bmr: métabolisme de base
        activity_level: 'sedentary', 'light', 'moderate', 'active', 'very_active'
    
    Returns:
        int: calories par jour
    """
    if not bmr:
        return None
    
    activity_multipliers = {
        'sedentary': 1.2,      # Peu ou pas d'exercice
        'light': 1.375,         # Exercice léger 1-3 jours/semaine
        'moderate': 1.55,       # Exercice modéré 3-5 jours/semaine
        'active': 1.725,        # Exercice intense 6-7 jours/semaine
        'very_active': 1.9,     # Exercice très intense + travail physique
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.2)
    return round(bmr * multiplier)


def get_meal_calories(total_daily_calories):
    """
    Calcule les calories recommandées par repas
    """
    if not total_daily_calories:
        return None
    
    return {
        'breakfast': round(total_daily_calories * 0.25),  # 25% petit-déjeuner
        'lunch': round(total_daily_calories * 0.35),      # 35% déjeuner
        'dinner': round(total_daily_calories * 0.30),     # 30% dîner
        'snacks': round(total_daily_calories * 0.10),     # 10% collations
    }