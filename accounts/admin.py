from django.contrib import admin
from .models import User, FoodProduct, HealthConstraint

admin.site.register(User)
admin.site.register(HealthConstraint)

@admin.register(FoodProduct)
class FoodProductAdmin(admin.ModelAdmin):
    # Affiche ces colonnes dans le tableau
    list_display = ('name', 'category', 'calories', 'difficulty', 'nutriscore')
    # Ajoute un menu sur le côté pour filtrer par salé/sucré et difficulté
    list_filter = ('category', 'difficulty')
    # Ajoute une barre de recherche
    search_fields = ('name', 'ingredients_text')