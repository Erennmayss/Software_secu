from django.test import TestCase
from django.urls import reverse

from accounts.models import FoodProduct, HealthConstraint, User


class UserRegimeApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='chef',
            email='chef@example.com',
            password='secret123',
            age=30,
            weight=70,
            height=175,
            sexe='M',
            activity_level='moderate',
            culinary_level='debutant',
            aliments_a_eviter='peanut',
        )
        self.user.health_constraints.add(HealthConstraint.objects.create(name='diabete'))
        self.client.login(email='chef@example.com', password='secret123')

        FoodProduct.objects.create(
            name='Salade fraiche',
            category='sale',
            ingredients_text='lettuce, tomato, olive oil',
            sugars_100g=2,
            salt_100g=0.2,
            calories=220,
            difficulty='facile',
            image_url='https://example.com/salad.jpg',
        )
        FoodProduct.objects.create(
            name='Dessert sucre',
            category='sale',
            ingredients_text='milk, peanut, sugar',
            sugars_100g=22,
            salt_100g=0.3,
            calories=480,
            difficulty='advanced',
            image_url='https://example.com/dessert.jpg',
        )

    def test_api_returns_profile_and_filtered_recipes(self):
        response = self.client.get(reverse('recipes:user_regime_api'), {'tab': 'sale'})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['activity_level'], 'moderate')
        self.assertEqual(payload['cooking_level'], 'beginner')
        self.assertEqual(payload['stats']['count'], 1)
        self.assertEqual(payload['recipes'][0]['name'], 'Salade fraiche')
        self.assertIn('score', payload['recipes'][0])

    def test_disabling_filters_changes_visible_results(self):
        response = self.client.get(
            reverse('recipes:user_regime_api'),
            {
                'tab': 'sale',
                'toggle_avoid_foods': '0',
                'toggle_health': '0',
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['stats']['count'], 2)
