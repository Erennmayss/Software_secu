from django.contrib import admin
from .models import MealPlan, FridgeIngredient


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'week_start', 'day', 'meal_type')
    list_filter = ('week_start', 'day', 'meal_type')
    search_fields = ('user__email', 'recipe__name')
    ordering = ('-week_start', 'day', 'meal_type')
    raw_id_fields = ('user', 'recipe')


@admin.register(FridgeIngredient)
class FridgeIngredientAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'normalized_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'name', 'normalized_name')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)

