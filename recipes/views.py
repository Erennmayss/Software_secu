from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import FoodProduct

@login_required
def index(request):
    constraints = request.user.health_constraints.all().values_list('name', flat=True)
    
    # ── Gestion des onglets (Salé / Sucré) ──
    current_tab = request.GET.get('tab', 'sale')
    products = FoodProduct.objects.filter(category=current_tab)

    # ── Recherche par nom ──
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    # ── Nouveaux Filtres : Difficulté et Calories ──
    difficulty = request.GET.get('difficulty')
    if difficulty:
        products = products.filter(difficulty__iexact=difficulty)
        
    calories_max = request.GET.get('calories_max')
    if calories_max and calories_max.isdigit():
        products = products.filter(calories__lte=int(calories_max))

    # ── Filtre Favoris ──
    if request.GET.get('favs') == '1':
        products = products.filter(favorites=request.user)

    for c in constraints:
        c = c.lower()
        # 1. Gestion des maladies (règles nutritionnelles)
        if "diabète" in c or "diabete" in c:
            products = products.filter(sugars_100g__lt=5)
        elif "hypertension" in c:
            products = products.filter(salt_100g__lt=0.3)
        # 2. Gestion des allergies et Cœliaque (exclusion d'ingrédients)
        elif "cœliaque" in c or "coeliaque" in c or "gluten" in c:
            products = products.exclude(ingredients_text__icontains="gluten")
            products = products.exclude(ingredients_text__icontains="blé")
            products = products.exclude(ingredients_text__icontains="ble")
        else:
            # Allergie générique (ex: "fraise")
            products = products.exclude(ingredients_text__icontains=c)

    # ── Calcul des statistiques de la base de données ──
    total_recipes = FoodProduct.objects.count()
    total_sucre = FoodProduct.objects.filter(category='sucre').count()
    total_sale = FoodProduct.objects.filter(category='sale').count()

    # ── Favoris de l'utilisateur pour l'affichage des cœurs ──
    user_favorites = request.user.favorite_products.values_list('id', flat=True)

    return render(request, 'home.html', {
        'products': products,
        'current_tab': current_tab,
        'query': query or '',
        'selected_difficulty': difficulty or '',
        'calories_max': calories_max or '',
        'total_recipes': total_recipes,
        'total_sucre': total_sucre,
        'total_sale': total_sale,
        'user_favorites': user_favorites,
        'is_regime_page': False,
    })


@login_required
def regime(request):
    """ 
    Affiche toutes les recettes SANS les filtrer selon les maladies.
    La substitution se fera en Front-End grâce à JavaScript.
    """
    # ── Gestion des onglets (Salé / Sucré) ──
    current_tab = request.GET.get('tab', 'sale')
    products = FoodProduct.objects.filter(category=current_tab)

    # ── Recherche & Filtres ──
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

    # Note : Aucun filtrage d'exclusion de santé ici (contrairement à index)
    
    user_favorites = request.user.favorite_products.values_list('id', flat=True)

    return render(request, 'regime.html', {
        'products': products,
        'current_tab': current_tab,
        'query': query or '',
        'selected_difficulty': difficulty or '',
        'calories_max': calories_max or '',
        'total_recipes': FoodProduct.objects.count(),
        'user_favorites': user_favorites,
        'is_regime_page': True,  # 👈 Active la substitution JavaScript !
    })


@login_required
def toggle_favorite(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(FoodProduct, id=product_id)
        
        if product.favorites.filter(id=request.user.id).exists():
            product.favorites.remove(request.user)
            return JsonResponse({'status': 'removed'})
        else:
            product.favorites.add(request.user)
            return JsonResponse({'status': 'added'})
            
    return JsonResponse({'error': 'Requête invalide'}, status=400)