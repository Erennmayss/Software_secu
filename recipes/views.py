import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from accounts.models import FoodProduct
from .models import MealPlan


@login_required
def index(request):
    constraints = request.user.health_constraints.all().values_list('name', flat=True)

    current_tab = request.GET.get('tab', 'sale')
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

    for constraint in constraints:
        normalized = constraint.lower()
        if "diabète" in normalized or "diabete" in normalized:
            products = products.filter(sugars_100g__lt=5)
        elif "hypertension" in normalized:
            products = products.filter(salt_100g__lt=0.3)
        elif "cœliaque" in normalized or "coeliaque" in normalized or "gluten" in normalized:
            products = products.exclude(ingredients_text__icontains="gluten")
            products = products.exclude(ingredients_text__icontains="blé")
            products = products.exclude(ingredients_text__icontains="ble")
        else:
            products = products.exclude(ingredients_text__icontains=normalized)

    return render(request, 'home.html', {
        'products': products,
        'current_tab': current_tab,
        'query': query or '',
        'selected_difficulty': difficulty or '',
        'calories_max': calories_max or '',
        'total_recipes': FoodProduct.objects.count(),
        'total_sucre': FoodProduct.objects.filter(category='sucre').count(),
        'total_sale': FoodProduct.objects.filter(category='sale').count(),
        'user_favorites': request.user.favorite_products.values_list('id', flat=True),
    })


@login_required
def regime(request):
    current_tab = request.GET.get('tab', 'sale')
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

    return render(request, 'regime.html', {
        'products': products,
        'current_tab': current_tab,
        'query': query or '',
        'selected_difficulty': difficulty or '',
        'calories_max': calories_max or '',
        'total_recipes': FoodProduct.objects.count(),
        'user_favorites': request.user.favorite_products.values_list('id', flat=True),
    })


@login_required
def toggle_favorite(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(FoodProduct, id=product_id)
        if product.favorites.filter(id=request.user.id).exists():
            product.favorites.remove(request.user)
            return JsonResponse({'status': 'removed'})
        product.favorites.add(request.user)
        return JsonResponse({'status': 'added'})

    return JsonResponse({'error': 'Requête invalide'}, status=400)


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

    favorites = user.favorite_products.all()
    plans = MealPlan.objects.filter(user=user).select_related('recipe')

    plan_dict = {}
    for plan in plans:
        plan_dict.setdefault(plan.day, {})
        plan_dict[plan.day][plan.meal_type] = {
            'id': plan.recipe.id,
            'name': plan.recipe.name,
            'calories': plan.recipe.calories,
            'image': plan.recipe.image_url,
        }

    return render(request, 'planner.html', {
        'daily_calories': daily_calories,
        'has_profile_data': has_profile_data,
        'favorites': favorites,
        'plan_dict': json.dumps(plan_dict),
        'days': ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'],
        'meals': ['petit_dej', 'dejeuner', 'diner'],
        'all_recipes': FoodProduct.objects.all(),
    })


@login_required
def update_planner(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get('action') == 'add':
            MealPlan.objects.update_or_create(
                user=request.user,
                day=data['day'],
                meal_type=data['meal_type'],
                defaults={'recipe_id': data['recipe_id']},
            )
        elif data.get('action') == 'remove':
            MealPlan.objects.filter(
                user=request.user,
                day=data['day'],
                meal_type=data['meal_type'],
            ).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
