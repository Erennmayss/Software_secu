import requests
import time
from django.core.management.base import BaseCommand
from accounts.models import FoodProduct

class Command(BaseCommand):
    help = 'Importe de vraies recettes depuis Spoonacular'

    def handle(self, *args, **kwargs):
        # 👇 COLLEZ VOTRE VRAIE CLÉ ENTRE LES GUILLEMETS CI-DESSOUS
        api_key = "be268a6924484a2c9668d8b6e5c31cc2"

        self.stdout.write("Récupération de délicieuses recettes...")
        
        # On boucle pour demander plusieurs pages (offset)
        # 5 pages de 100 = 500 recettes. (Attention au quota gratuit de Spoonacular : 150 points/jour)
        for offset in range(0, 500, 100):
            self.stdout.write(f"Téléchargement des recettes {offset} à {offset+100}...")
            url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={api_key}&number=100&addRecipeNutrition=true&offset={offset}"
            
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"Erreur API ({response.status_code}) : {response.text}"))
                    break # Arrête la boucle si le quota est dépassé
                    
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break # Plus de résultats

                for r in results:
                    name = r.get('title')
                    nutrition = r.get('nutrition', {}).get('nutrients', [])
                    
                    # Extraction spécifique pour tes filtres Santé
                    sugar = next((item['amount'] for item in nutrition if item['name'] == 'Sugar'), 0)
                    # Le sel est calculé à partir du sodium (Sel = Sodium * 2.5 / 1000)
                    sodium_mg = next((item['amount'] for item in nutrition if item['name'] == 'Sodium'), 0)
                    salt = (sodium_mg * 2.5) / 1000 
                    
                    # Déterminer si c'est sucré ou salé
                    dish_types = r.get('dishTypes', [])
                    category = 'sucre' if 'dessert' in dish_types else 'sale'
                    
                    # Les ingrédients pour le filtrage Allergies/Cœliaque
                    ingredients = [i.get('name') for i in r.get('nutrition', {}).get('ingredients', [])]
                    
                    FoodProduct.objects.update_or_create(
                        name=name,
                        defaults={
                            'category': category,
                            'ingredients_text': ", ".join(ingredients).lower(),
                            'image_url': r.get('image'),
                            'nutriscore': 'A',
                            'sugars_100g': sugar,
                            'salt_100g': salt,
                        }
                    )
                time.sleep(1) # Petite pause pour ne pas spammer l'API
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur : {e}"))
                break
                
        self.stdout.write(self.style.SUCCESS(f"Succès ! {FoodProduct.objects.count()} vraies recettes importées au total."))