import requests
import time
from django.core.management.base import BaseCommand
from accounts.models import FoodProduct


class Command(BaseCommand):
    help = 'Importe uniquement des recettes sucrées (desserts) depuis Spoonacular'

    def handle(self, *args, **kwargs):
        # 👇 TA CLÉ API SPOONACULAR
        api_key = "63cc5f933b634272a125bd51d4935084"

        self.stdout.write("🍰 Récupération de délicieuses recettes sucrées (desserts)...")
        
        total_imported = 0
        
        # 🔥 UNIQUEMENT les desserts
        query_type = 'dessert'
        
        # 100 desserts maximum
        max_offset = 100
        
        for offset in range(0, max_offset, 100):
            self.stdout.write(f"📥 Téléchargement de 100 desserts - offset {offset}...")
            
            url = (
                f"https://api.spoonacular.com/recipes/complexSearch"
                f"?apiKey={api_key}"
                f"&number=100"
                f"&addRecipeNutrition=true"
                f"&offset={offset}"
                f"&type={query_type}"
            )
            
            try:
                response = requests.get(url)
                
                if response.status_code == 402:
                    self.stdout.write(self.style.ERROR(
                        "🛑 ERREUR : Quota API dépassé ! Vous n'avez plus de points."
                    ))
                    return
                
                if response.status_code == 401:
                    self.stdout.write(self.style.ERROR(
                        "🛑 ERREUR : Clé API invalide ! Vérifiez votre clé Spoonacular."
                    ))
                    return
                
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(
                        f"⚠️ Erreur API ({response.status_code}) : {response.text[:200]}"
                    ))
                    break
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    self.stdout.write("ℹ️ Plus de résultats pour les desserts")
                    break
                
                for r in results:
                    name = r.get('title', 'Sans titre')
                    nutrition = r.get('nutrition', {}).get('nutrients', [])
                    
                    sugar = next(
                        (item['amount'] for item in nutrition if item['name'] == 'Sugar'),
                        0
                    )
                    sodium_mg = next(
                        (item['amount'] for item in nutrition if item['name'] == 'Sodium'),
                        0
                    )
                    salt = (sodium_mg * 2.5) / 1000
                    
                    category = 'sucre'
                    
                    ingredients = [
                        i.get('name', '') 
                        for i in r.get('nutrition', {}).get('ingredients', [])
                    ]
                    ingredients_text = ", ".join(ingredients).lower() if ingredients else ""
                    
                    product, created = FoodProduct.objects.update_or_create(
                        name=name,
                        defaults={
                            'category': category,
                            'ingredients_text': ingredients_text,
                            'image_url': r.get('image', ''),
                            'nutriscore': 'A',
                            'sugars_100g': round(sugar, 2),
                            'salt_100g': round(salt, 3),
                        }
                    )
                    
                    if created:
                        total_imported += 1
                        self.stdout.write(f"   🍰 Ajouté : {name[:50]}...")
                    else:
                        self.stdout.write(f"   🔄 Mis à jour : {name[:50]}...")
                
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur réseau : {e}"))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur inattendue : {e}"))
                break
        
        desserts_count = FoodProduct.objects.filter(category='sucre').count()
        self.stdout.write(self.style.SUCCESS(
            f"\n✨ Import terminé ! ✨\n"
            f"   🍰 Nouveaux desserts importés : {total_imported}\n"
            f"   📚 Total desserts en base : {desserts_count}"
        ))