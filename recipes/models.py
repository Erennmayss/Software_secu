from datetime import date, timedelta

from django.db import models
from django.conf import settings
from accounts.models import FoodProduct


def monday_of_current_week():
    today = date.today()
    return today - timedelta(days=today.weekday())

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
    week_start = models.DateField(default=monday_of_current_week)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    meal_type = models.CharField(max_length=15, choices=MEAL_TYPES)

    class Meta:
        unique_together = ('user', 'week_start', 'day', 'meal_type') # Une seule recette par type de repas par jour et par semaine


class FridgeIngredient(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fridge_ingredients')
    name = models.CharField(max_length=120)
    normalized_name = models.CharField(max_length=120, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'normalized_name')
        ordering = ['normalized_name']

    def save(self, *args, **kwargs):
        self.normalized_name = (self.name or '').strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user_id}:{self.name}'
