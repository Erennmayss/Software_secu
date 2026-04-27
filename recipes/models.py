from django.db import models
from django.conf import settings
from accounts.models import FoodProduct

class MealPlan(models.Model):
    DAYS_OF_WEEK = [
        ('lundi', 'Lundi'), ('mardi', 'Mardi'), ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'), ('vendredi', 'Vendredi'), ('samedi', 'Samedi'), ('dimanche', 'Dimanche')
    ]
    MEAL_TYPES = [
        ('petit_dej', 'Petit-déjeuner'), ('dejeuner', 'Déjeuner'), ('diner', 'Dîner')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_plans')
    recipe = models.ForeignKey(FoodProduct, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    meal_type = models.CharField(max_length=15, choices=MEAL_TYPES)

    class Meta:
        unique_together = ('user', 'day', 'meal_type') # Une seule recette par type de repas par jour
