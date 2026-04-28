from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from accounts.utils import normalize_health_constraint


DAY_ORDER = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
ANIMAL_PRODUCT_KEYWORDS = ['lait', 'milk', 'fromage', 'cheese', 'beurre', 'butter', 'cream', 'creme', 'oeuf', 'egg', 'poulet', 'chicken', 'boeuf', 'beef', 'porc', 'pork', 'fish', 'poisson']

CONSTRAINT_RULES = {
    'diabetes': {
        'exclude_keywords': ['sucre', 'sugar', 'miel', 'honey', 'sirop', 'syrup'],
        'max_sugars_100g': 5,
    },
    'hypertension': {
        'exclude_keywords': ['sel', 'salt', 'bouillon cube', 'soy sauce', 'sauce soja'],
        'max_salt_100g': 0.3,
    },
    'vegan': {
        'exclude_keywords': ['lactose', *ANIMAL_PRODUCT_KEYWORDS],
    },
    'gluten': {
        'exclude_keywords': ['gluten', 'ble', 'blé', 'wheat', 'farine de ble', 'bread', 'pasta'],
    },
}


@dataclass
class RecipeAdaptation:
    allowed: bool
    matched_constraints: list[str]
    blocked_reasons: list[str]


def normalize_ingredient_tokens(raw_text: str | None) -> list[str]:
    if not raw_text:
        return []
    normalized = raw_text.replace('\n', ',')
    return [item.strip().lower() for item in normalized.split(',') if item.strip()]


def normalize_fridge_ingredient(name: str) -> str:
    return (name or '').strip().lower()


def parse_week_start(raw_value: str | None) -> date:
    if raw_value:
        try:
            parsed = datetime.strptime(raw_value, '%Y-%m-%d').date()
            return parsed - timedelta(days=parsed.weekday())
        except ValueError:
            pass
    today = date.today()
    return today - timedelta(days=today.weekday())


def get_user_constraint_keys(user) -> list[str]:
    keys = []
    for constraint in user.health_constraints.all():
        normalized = normalize_health_constraint(constraint.name)
        keys.append(normalized)
    return sorted(set(keys))


def recipe_matches_constraints(recipe, constraint_keys: list[str]) -> RecipeAdaptation:
    if not constraint_keys:
        return RecipeAdaptation(True, [], [])

    ingredient_tokens = normalize_ingredient_tokens(getattr(recipe, 'ingredients_text', ''))
    allowed = True
    blocked_reasons = []

    for constraint_key in constraint_keys:
        rules = CONSTRAINT_RULES.get(constraint_key, {})

        max_sugars = rules.get('max_sugars_100g')
        if max_sugars is not None and getattr(recipe, 'sugars_100g', 0) > max_sugars:
            allowed = False
            blocked_reasons.append(f'{constraint_key}: sucre trop eleve')

        max_salt = rules.get('max_salt_100g')
        if max_salt is not None and getattr(recipe, 'salt_100g', 0) > max_salt:
            allowed = False
            blocked_reasons.append(f'{constraint_key}: sel trop eleve')

        for keyword in rules.get('exclude_keywords', []):
            if any(keyword in token for token in ingredient_tokens):
                allowed = False
                blocked_reasons.append(f'{constraint_key}: ingredient exclu ({keyword})')
                break

    return RecipeAdaptation(allowed, constraint_keys, blocked_reasons)


def build_fridge_match(recipe, fridge_ingredients: list[str]) -> int:
    if not fridge_ingredients:
        return 0
    ingredient_tokens = normalize_ingredient_tokens(getattr(recipe, 'ingredients_text', ''))
    return sum(1 for item in fridge_ingredients if any(item in token for token in ingredient_tokens))
