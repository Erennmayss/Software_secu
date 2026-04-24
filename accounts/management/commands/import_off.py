import requests
import time
from django.core.management.base import BaseCommand
from accounts.models import FoodProduct

class Command(BaseCommand):
    help = 'Importe de vraies recettes depuis Spoonacular'

    def handle(self, *args, **kwargs):
        # 👇 COLLEZ VOTRE VRAIE CLÉ ENTRE LES GUILLEMETS CI-DESSOUS
        api_key = "VOTRE_NOUVELLE_CLE_API_ICI"

        self.stdout.write("Récupération de délicieuses recettes...")
        
        for query_type in ['main course', 'dessert']:
            # 200 plats salés, 100 desserts (pour économiser vos points !)
            max_offset = 200 if query_type == 'main course' else 100
            for offset in range(0, max_offset, 100):
                self.stdout.write(f"Téléchargement de 100 recettes ({query_type}) - offset {offset}...")
                url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={api_key}&number=100&addRecipeNutrition=true&offset={offset}&type={query_type}"
                
                try:
                    response = requests.get(url)
                    if response.status_code == 402:
                        self.stdout.write(self.style.ERROR("🛑 ERREUR : Vous n'avez plus de points sur cette clé API (Quota dépassé) !"))
                        return
                    if response.status_code != 200:
                        self.stdout.write(self.style.ERROR(f"Erreur API ({response.status_code}) : {response.text}"))
                        break 
                        
                    data = response.json()
                    results = data.get('results', [])
                    
                    if not results:
                        break 

                for r in results:
                    name = r.get('title')
                    nutrition = r.get('nutrition', {}).get('nutrients', [])
                        
                        sugar = next((item['amount'] for item in nutrition if item['name'] == 'Sugar'), 0)
                        sodium_mg = next((item['amount'] for item in nutrition if item['name'] == 'Sodium'), 0)
                        salt = (sodium_mg * 2.5) / 1000 
                        
                        category = 'sucre' if query_type == 'dessert' else 'sale'
                        
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
                    time.sleep(1)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erreur : {e}"))
                    break
                
        self.stdout.write(self.style.SUCCESS(f"Succès ! {FoodProduct.objects.count()} vraies recettes importées au total."))