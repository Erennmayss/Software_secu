from django.shortcuts import render
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

    return render(request, 'home.html', {
        'products': products,
        'current_tab': current_tab,
        'query': query or ''
    })