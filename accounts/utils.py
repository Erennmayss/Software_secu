from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9,
}

LEVEL_ORDER = {
    'beginner': 1,
    'intermediate': 2,
    'advanced': 3,
}

LEVEL_ALIASES = {
    'debutant': 'beginner',
    'beginner': 'beginner',
    'facile': 'beginner',
    'easy': 'beginner',
    'simple': 'beginner',
    'intermediaire': 'intermediate',
    'intermediate': 'intermediate',
    'moyen': 'intermediate',
    'standard': 'intermediate',
    'avance': 'advanced',
    'advanced': 'advanced',
    'expert': 'advanced',
    'complexe': 'advanced',
}

RESTRICTION_MAP = {
    'sans_lactose': ['lactose'],
    'sans_gluten': ['gluten'],
    'sans_noix': ['noix'],
    'vegan': ['vegan', 'viande', 'poisson'],
    'vegetarien': ['vegetarien', 'viande', 'poisson'],
    'hallal': ['hallal', 'porc', 'alcool'],
    'sans_alcool': ['alcool'],
}

STRICT_KEYWORDS = {
    'gluten': ['gluten', 'ble', 'wheat', 'farine', 'bread', 'pasta'],
    'lactose': ['lait', 'milk', 'cream', 'fromage', 'cheese', 'butter', 'beurre', 'yogurt'],
    'noix': ['noix', 'almond', 'amande', 'pecan', 'pistach', 'cashew', 'cacahu', 'peanut'],
    'oeuf': ['oeuf', 'egg', 'eggs'],
    'porc': ['porc', 'pork', 'ham', 'bacon', 'lardon'],
    'alcool': ['rum', 'wine', 'vin', 'beer', 'biere', 'liqueur', 'whisky', 'vodka'],
    'poisson': ['poisson', 'fish', 'saumon', 'thon', 'crevette', 'shrimp', 'crab', 'crabe'],
    'viande': ['beef', 'boeuf', 'bacon', 'ham', 'poulet', 'chicken', 'porc', 'veal', 'agneau'],
    'vegetarien': ['beef', 'boeuf', 'bacon', 'ham', 'poulet', 'chicken', 'porc', 'veal', 'agneau', 'poisson', 'fish'],
    'vegan': ['beef', 'boeuf', 'bacon', 'ham', 'poulet', 'chicken', 'porc', 'veal', 'agneau', 'poisson', 'fish', 'milk', 'cheese', 'butter', 'egg', 'oeuf', 'cream'],
}

SATURATED_FAT_KEYWORDS = [
    'butter', 'beurre', 'cream', 'creme', 'cheese', 'fromage', 'bacon', 'sausage',
    'saucisse', 'charcut', 'fried', 'frit', 'chocolate', 'chocolat', 'coconut oil',
]


@dataclass
class UserNutritionProfile:
    bmr: int | None
    tdee: int | None
    daily_calories: int | None
    target_recipe_calories: int | None
    activity_level: str
    cooking_level: str
    avoid_foods: list[str]
    health_constraints: list[str]
    restrictions: list[str]
    strict_keywords: list[str]


def normalize_text_list(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    return [item.strip().lower() for item in raw_value.split(',') if item.strip()]


def normalize_health_constraint(name: str) -> str:
    value = (name or '').strip().lower()
    aliases = {
        'diabete': 'diabetes',
        'diabète': 'diabetes',
        'hypertension': 'hypertension',
        'cholesterol': 'cholesterol',
        'cholestérol': 'cholesterol',
        'celiaque': 'gluten',
        'cœliaque': 'gluten',
        'coeliaque': 'gluten',
        'gluten': 'gluten',
        'allergie': 'allergy',
    }
    return aliases.get(value, value)


def normalize_cooking_level(value: str | None) -> str:
    return LEVEL_ALIASES.get((value or '').strip().lower(), 'intermediate')


def normalize_recipe_level(recipe) -> str:
    difficulty = normalize_cooking_level(getattr(recipe, 'difficulty', ''))
    ingredients_count = len(split_ingredients(getattr(recipe, 'ingredients_text', '')))

    if difficulty == 'advanced' or ingredients_count >= 12:
        return 'advanced'
    if difficulty == 'beginner' or ingredients_count <= 6:
        return 'beginner'
    return 'intermediate'


def split_ingredients(ingredients_text: str | None) -> list[str]:
    if not ingredients_text:
        return []
    return [item.strip().lower() for item in ingredients_text.split(',') if item.strip()]


def calculate_bmr(age, weight, height, sexe):
    if not all([age, weight, height, sexe]):
        return None

    try:
        age = int(age)
        weight = float(weight)
        height = float(height)
    except (ValueError, TypeError):
        return None

    base = (10 * weight) + (6.25 * height) - (5 * age)
    if sexe == 'M':
        base += 5
    elif sexe == 'F':
        base -= 161
    else:
        base -= 78
    return round(base)


def calculate_daily_calories(bmr, activity_level='moderate'):
    if not bmr:
        return None
    return round(bmr * ACTIVITY_MULTIPLIERS.get(activity_level or 'moderate', 1.55))


def get_meal_calories(total_daily_calories):
    if not total_daily_calories:
        return None
    return {
        'breakfast': round(total_daily_calories * 0.25),
        'lunch': round(total_daily_calories * 0.35),
        'dinner': round(total_daily_calories * 0.30),
        'snacks': round(total_daily_calories * 0.10),
    }


def build_user_nutrition_profile(user) -> UserNutritionProfile:
    activity_level = getattr(user, 'activity_level', '') or 'moderate'
    cooking_level = normalize_cooking_level(getattr(user, 'culinary_level', ''))
    avoid_foods = normalize_text_list(getattr(user, 'aliments_a_eviter', ''))
    restrictions = normalize_text_list(getattr(user, 'restrictions', ''))
    health_constraints = [
        normalize_health_constraint(constraint.name)
        for constraint in user.health_constraints.all()
    ]

    strict_keywords = set(avoid_foods)
    for restriction in restrictions:
        strict_keywords.update(RESTRICTION_MAP.get(restriction, []))
    for constraint in health_constraints:
        if constraint not in {'diabetes', 'hypertension', 'cholesterol'}:
            strict_keywords.add(constraint)

    bmr = calculate_bmr(user.age, user.weight, user.height, user.sexe)
    tdee = calculate_daily_calories(bmr, activity_level) if bmr else None
    daily_calories = tdee or 2000
    target_recipe_calories = round(daily_calories / 3)

    return UserNutritionProfile(
        bmr=bmr,
        tdee=tdee,
        daily_calories=daily_calories,
        target_recipe_calories=target_recipe_calories,
        activity_level=activity_level,
        cooking_level=cooking_level,
        avoid_foods=avoid_foods,
        health_constraints=health_constraints,
        restrictions=restrictions,
        strict_keywords=sorted(strict_keywords),
    )


def ingredient_matches_any(ingredients: Iterable[str], keywords: Iterable[str]) -> list[str]:
    matches = []
    for ingredient in ingredients:
        lower = ingredient.lower()
        for keyword in keywords:
            if keyword and keyword in lower:
                matches.append(keyword)
    return sorted(set(matches))


def calorie_component(recipe_calories: int, target_recipe_calories: int | None) -> tuple[float, str]:
    if not target_recipe_calories:
        return 1.0, 'Profil calorique incomplet'

    delta = abs(recipe_calories - target_recipe_calories)
    ratio = delta / max(target_recipe_calories, 1)
    if ratio <= 0.15:
        return 1.0, 'Calories tres proches de votre objectif'
    if ratio <= 0.30:
        return 0.75, 'Calories assez proches de votre objectif'
    if ratio <= 0.45:
        return 0.45, 'Calories un peu eloignees de votre objectif'
    return 0.15, 'Calories peu adaptees a votre objectif'


def cooking_component(recipe_level: str, user_level: str, ingredient_count: int) -> tuple[float, str]:
    recipe_rank = LEVEL_ORDER.get(recipe_level, 2)
    user_rank = LEVEL_ORDER.get(user_level, 2)

    if user_level == 'beginner' and ingredient_count > 8:
        return 0.35, 'Recette chargee pour un niveau debutant'
    if recipe_rank == user_rank:
        return 1.0, 'Difficulte adaptee a votre niveau'
    if recipe_rank < user_rank:
        return 0.9, 'Recette plus simple que votre niveau'
    if recipe_rank - user_rank == 1:
        return 0.55, 'Recette legerement au-dessus de votre niveau'
    return 0.2, 'Recette technique pour votre niveau actuel'


def health_component(recipe, ingredients: list[str], normalized_constraints: list[str]) -> tuple[float, str, bool]:
    if not normalized_constraints:
        return 1.0, 'Aucune restriction sante active', False

    issues = []
    strict_excluded = False

    if 'diabetes' in normalized_constraints and getattr(recipe, 'sugars_100g', 0) > 12:
        issues.append('trop sucree pour le diabete')
    elif 'diabetes' in normalized_constraints and getattr(recipe, 'sugars_100g', 0) > 7:
        issues.append('sucre a surveiller')

    if 'hypertension' in normalized_constraints and getattr(recipe, 'salt_100g', 0) > 1:
        issues.append('trop salee pour l hypertension')
    elif 'hypertension' in normalized_constraints and getattr(recipe, 'salt_100g', 0) > 0.5:
        issues.append('sel a surveiller')

    if 'cholesterol' in normalized_constraints:
        fat_hits = ingredient_matches_any(ingredients, SATURATED_FAT_KEYWORDS)
        if len(fat_hits) >= 2:
            issues.append('ingredients riches en graisses saturees')
        elif fat_hits:
            issues.append('graisses saturees a surveiller')

    strict_constraints = [item for item in normalized_constraints if item not in {'diabetes', 'hypertension', 'cholesterol'}]
    for keyword in strict_constraints:
        keyword_hits = ingredient_matches_any(ingredients, STRICT_KEYWORDS.get(keyword, [keyword]))
        if keyword_hits:
            strict_excluded = True
            issues.append(f'contient un element interdit: {", ".join(keyword_hits[:2])}')

    if strict_excluded:
        return 0.0, '; '.join(issues), True
    if not issues:
        return 1.0, 'Compatible avec vos restrictions sante', False
    if len(issues) == 1 and 'surveiller' in issues[0]:
        return 0.65, issues[0], False
    return 0.3, '; '.join(issues), False


def avoid_foods_component(ingredients: list[str], avoid_foods: list[str], restrictions: list[str]) -> tuple[float, str, bool]:
    all_keywords = set(avoid_foods)
    for restriction in restrictions:
        all_keywords.update(RESTRICTION_MAP.get(restriction, []))

    matched = []
    for keyword in all_keywords:
        matched.extend(ingredient_matches_any(ingredients, STRICT_KEYWORDS.get(keyword, [keyword])))

    matched = sorted(set(matched))
    if matched:
        return 0.0, f"Ingredients a eviter detectes: {', '.join(matched[:3])}", True
    if all_keywords:
        return 1.0, 'Respecte vos aliments a eviter', False
    return 1.0, 'Aucun aliment a eviter configure', False


def serialize_regime_recipe(recipe, profile: UserNutritionProfile, toggles: dict[str, bool]) -> dict | None:
    ingredients = split_ingredients(getattr(recipe, 'ingredients_text', ''))
    recipe_level = normalize_recipe_level(recipe)
    ingredient_count = len(ingredients)

    components = {}
    active_components = []
    hard_excluded = False
    reasons = []

    if toggles.get('calories', True):
        score, reason = calorie_component(getattr(recipe, 'calories', 0), profile.target_recipe_calories)
        components['calories'] = round(score * 100)
        active_components.append(score)
        reasons.append(reason)

    if toggles.get('avoid_foods', True):
        score, reason, excluded = avoid_foods_component(ingredients, profile.avoid_foods, profile.restrictions)
        components['avoid_foods'] = round(score * 100)
        active_components.append(score)
        reasons.append(reason)
        hard_excluded = hard_excluded or excluded

    if toggles.get('health', True):
        score, reason, excluded = health_component(recipe, ingredients, profile.health_constraints)
        components['health'] = round(score * 100)
        active_components.append(score)
        reasons.append(reason)
        hard_excluded = hard_excluded or excluded

    if toggles.get('cooking', True):
        score, reason = cooking_component(recipe_level, profile.cooking_level, ingredient_count)
        components['cooking'] = round(score * 100)
        active_components.append(score)
        reasons.append(reason)

    if hard_excluded:
        return None

    score = round((sum(active_components) / len(active_components)) * 100) if active_components else 100
    return {
        'id': recipe.id,
        'name': recipe.name,
        'image_url': recipe.image_url,
        'category': recipe.category,
        'calories': recipe.calories,
        'difficulty': getattr(recipe, 'difficulty', ''),
        'normalized_difficulty': recipe_level,
        'nutriscore': recipe.nutriscore,
        'sugars_100g': recipe.sugars_100g,
        'salt_100g': recipe.salt_100g,
        'ingredients': ingredients,
        'ingredient_count': ingredient_count,
        'score': score,
        'score_breakdown': components,
        'reasons': reasons,
        'is_favorite': False,
    }
