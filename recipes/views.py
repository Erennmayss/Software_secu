import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from accounts.models import FoodProduct
from accounts.rate_limit import rate_limit
from .models import FridgeIngredient, MealPlan
from .services import (
    DAY_ORDER,
    build_fridge_match,
    get_user_constraint_keys,
    parse_week_start,
    recipe_matches_constraints,
)


def _serialize_plan_queryset(plans):
    plan_dict = {}
    for plan in plans:
        plan_dict.setdefault(plan.day, {})
        plan_dict[plan.day][plan.meal_type] = {
            'id': plan.recipe.id,
            'name': plan.recipe.name,
            'calories': plan.recipe.calories,
            'image': plan.recipe.image.url if getattr(plan.recipe, 'image', None) else plan.recipe.image_url,
        }
    return plan_dict


def _filter_products_for_user(request, current_tab):
    products = FoodProduct.objects.filter(category=current_tab)

    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    difficulty = request.GET.get('difficulty')
    if difficulty:
        products = products.filter(difficulty__iexact=difficulty)

    calories_max = request.GET.get('calories_max')
    if calories_max and calories_max.isdigit():
        products = products.filter(calories__lte=int(calories_max))

    if request.GET.get('favs') == '1':
        products = products.filter(favorites=request.user)

    constraint_keys = get_user_constraint_keys(request.user)
    fridge_ingredients = list(
        request.user.fridge_ingredients.values_list('normalized_name', flat=True)
    )

    filtered = []
    for product in products:
        adaptation = recipe_matches_constraints(product, constraint_keys)
        if adaptation.allowed:
            product.fridge_match_count = build_fridge_match(product, fridge_ingredients)
            filtered.append(product)

    filtered.sort(key=lambda item: (-getattr(item, 'fridge_match_count', 0), item.name.lower()))
    return filtered, difficulty, calories_max


@login_required
def index(request):
    current_tab = request.GET.get('tab', 'sale')
    products, difficulty, calories_max = _filter_products_for_user(request, current_tab)

    total_recipes = FoodProduct.objects.count()
    return render(request, 'home.html', {
        'products': products,
        'current_tab': current_tab,
        'query': request.GET.get('q', ''),
        'selected_difficulty': difficulty or '',
        'calories_max': calories_max or '',
        'total_recipes': total_recipes,
        'total_sucre': FoodProduct.objects.filter(category='sucre').count(),
        'total_sale': FoodProduct.objects.filter(category='sale').count(),
        'user_favorites': request.user.favorite_products.values_list('id', flat=True),
    })


@login_required
def regime(request):
    current_tab = request.GET.get('tab', 'sale')
    products, difficulty, calories_max = _filter_products_for_user(request, current_tab)

    return render(request, 'regime.html', {
        'products': products,
        'current_tab': current_tab,
        'query': request.GET.get('q', ''),
        'selected_difficulty': difficulty or '',
        'calories_max': calories_max or '',
        'total_recipes': FoodProduct.objects.count(),
        'user_favorites': request.user.favorite_products.values_list('id', flat=True),
    })


@login_required
@rate_limit('favorite-toggle', limit=60, window_seconds=60, by_user=True)
def toggle_favorite(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(FoodProduct, id=product_id)
        if product.favorites.filter(id=request.user.id).exists():
            product.favorites.remove(request.user)
            return JsonResponse({'status': 'removed'})
        product.favorites.add(request.user)
        return JsonResponse({'status': 'added'})

    return JsonResponse({'error': 'Requete invalide'}, status=400)


@login_required
def planner(request):
    user = request.user
    daily_calories = 2000
    has_profile_data = False

    if user.weight and user.height and user.age and user.sexe:
        has_profile_data = True
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age)
        bmr += 5 if user.sexe == 'M' else -161
        daily_calories = int(bmr * 1.375)

    week_start = parse_week_start(request.GET.get('week_start'))
    plans = MealPlan.objects.filter(user=user, week_start=week_start).select_related('recipe')
    fridge_ingredients = list(user.fridge_ingredients.values_list('name', flat=True))

    return render(request, 'planner.html', {
        'daily_calories': daily_calories,
        'has_profile_data': has_profile_data,
        'favorites': user.favorite_products.all(),
        'plan_dict': json.dumps(_serialize_plan_queryset(plans)),
        'days': DAY_ORDER,
        'meals': ['petit_dej', 'dejeuner', 'diner'],
        'all_recipes': FoodProduct.objects.all(),
        'current_week_start': week_start.isoformat(),
        'fridge_ingredients_json': json.dumps(fridge_ingredients),
    })


@login_required
def planner_state(request):
    week_start = parse_week_start(request.GET.get('week_start'))
    plans = MealPlan.objects.filter(user=request.user, week_start=week_start).select_related('recipe')
    return JsonResponse({
        'success': True,
        'week_start': week_start.isoformat(),
        'plan': _serialize_plan_queryset(plans),
    })


@login_required
@rate_limit('planner-update', limit=180, window_seconds=60, by_user=True)
def update_planner(request):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=400)

    data = json.loads(request.body)
    week_start = parse_week_start(data.get('week_start'))
    if data.get('action') == 'add':
        MealPlan.objects.update_or_create(
            user=request.user,
            week_start=week_start,
            day=data['day'],
            meal_type=data['meal_type'],
            defaults={'recipe_id': data['recipe_id']},
        )
        return JsonResponse({'success': True, 'replaced': True, 'week_start': week_start.isoformat()})

    if data.get('action') == 'remove':
        MealPlan.objects.filter(
            user=request.user,
            week_start=week_start,
            day=data['day'],
            meal_type=data['meal_type'],
        ).delete()
        return JsonResponse({'success': True, 'week_start': week_start.isoformat()})

    return JsonResponse({'success': False, 'error': 'Action inconnue'}, status=400)


@login_required
@rate_limit('fridge-api', limit=120, window_seconds=300, by_user=True, methods=('POST',))
def fridge_ingredients_api(request):
    if request.method == 'GET':
        ingredients = list(
            request.user.fridge_ingredients.values('id', 'name', 'normalized_name')
        )
        return JsonResponse({'success': True, 'ingredients': ingredients})

    if request.method == 'POST':
        payload = json.loads(request.body)
        name = (payload.get('name') or '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Ingredient requis.'}, status=400)

        ingredient, created = FridgeIngredient.objects.get_or_create(
            user=request.user,
            normalized_name=name.lower(),
            defaults={'name': name},
        )
        if not created:
            ingredient.name = name
            ingredient.save(update_fields=['name'])
        return JsonResponse({
            'success': True,
            'created': created,
            'ingredient': {'id': ingredient.id, 'name': ingredient.name, 'normalized_name': ingredient.normalized_name},
        })

    return JsonResponse({'success': False, 'error': 'Methode non autorisee.'}, status=405)


@login_required
@rate_limit('fridge-delete', limit=120, window_seconds=300, by_user=True, methods=('DELETE',))
def fridge_ingredient_delete(request, ingredient_id):
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Methode non autorisee.'}, status=405)
    ingredient = get_object_or_404(FridgeIngredient, pk=ingredient_id, user=request.user)
    ingredient.delete()
    return JsonResponse({'success': True})
