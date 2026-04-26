from django.contrib.auth.models import AbstractUser
from django.db import models
import random


class HealthConstraint(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    """Utilisateur personnalisé Biodelice."""
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio    = models.CharField(max_length=200, blank=True)
    health_constraints = models.ManyToManyField(HealthConstraint, blank=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.code = str(random.randint(100000, 999999))
        self.save()


class FoodProduct(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, default='sale')
    ingredients_text = models.TextField(blank=True)
    allergens_tags = models.TextField(blank=True)
    nutriscore = models.CharField(max_length=1, blank=True)
    sugars_100g = models.FloatField(default=0)
    salt_100g = models.FloatField(default=0)
    calories = models.IntegerField(default=0)
    difficulty = models.CharField(max_length=20, blank=True)
    image_url = models.URLField(blank=True)
    favorites = models.ManyToManyField('User', related_name='favorite_products', blank=True)

    def __str__(self):
        return self.name
