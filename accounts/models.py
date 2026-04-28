from django.contrib.auth.models import AbstractUser
from django.db import models
import random

from .fields import EncryptedTextField


class HealthConstraint(models.Model):
    TYPE_DISEASE = 'disease'
    TYPE_ALLERGEN = 'allergen'
    TYPE_CHOICES = [
        (TYPE_DISEASE, 'Maladie'),
        (TYPE_ALLERGEN, 'Allergene'),
    ]

    name = models.CharField(max_length=100, unique=True)
    constraint_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_DISEASE)
    color = models.CharField(max_length=20, default='#e8621a')
    icon = models.CharField(max_length=50, blank=True, default='')
    
    def __str__(self):
        return self.name

# accounts/models.py - Ajoute ces champs à la classe User

class User(AbstractUser):
    """Utilisateur personnalisé Biodelice."""
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.CharField(max_length=200, blank=True)
    health_constraints = models.ManyToManyField(HealthConstraint, blank=True)
    
    # Nouveaux champs pour l'onboarding
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)  # poids en kg
    height = models.FloatField(null=True, blank=True)  # taille en cm
    sexe = models.CharField(max_length=10, choices=[('M', 'Homme'), ('F', 'Femme'), ('autre', 'Autre')], blank=True)
    
    restrictions = EncryptedTextField(blank=True)  # restrictions religieuses/allergies
    aliments_a_eviter = EncryptedTextField(blank=True)  # aliments à éviter
    health_constraints_snapshot = EncryptedTextField(blank=True)
    activity_level = models.CharField(max_length=20, blank=True, default='moderate')
    culinary_level = models.CharField(max_length=20, choices=[
        ('debutant', 'Débutant'),
        ('intermediaire', 'Intermédiaire'),
        ('avance', 'Avancé')
    ], blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.code = str(random.randint(100000, 999999))
        self.save()


class FoodProduct(models.Model):
    CATEGORY_CHOICES = [
        ('sale', 'Sale'),
        ('sucre', 'Sucre'),
        ('healthy', 'Healthy'),
        ('vegan', 'Vegan'),
    ]
    DIFFICULTY_CHOICES = [
        ('easy', 'Facile'),
        ('medium', 'Modere'),
        ('hard', 'Complexe'),
    ]
    NUTRISCORE_CHOICES = [(grade, grade) for grade in ['A', 'B', 'C', 'D', 'E']]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='sale')
    ingredients_text = models.TextField(blank=True)
    preparation_steps = models.TextField(blank=True)
    allergens_tags = models.TextField(blank=True)
    nutriscore = models.CharField(max_length=1, choices=NUTRISCORE_CHOICES, blank=True)
    sugars_100g = models.FloatField(default=0)
    salt_100g = models.FloatField(default=0)
    calories = models.IntegerField(default=0)
    proteins = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fats = models.FloatField(default=0)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, blank=True)
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    favorites = models.ManyToManyField('User', related_name='favorite_products', blank=True)

    def __str__(self):
        return self.name
