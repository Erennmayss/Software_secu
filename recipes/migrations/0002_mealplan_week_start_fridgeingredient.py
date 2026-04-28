from django.db import migrations, models
import django.db.models.deletion
import recipes.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0006_sync_activity_level_state'),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealplan',
            name='week_start',
            field=models.DateField(default=recipes.models.monday_of_current_week),
        ),
        migrations.AlterUniqueTogether(
            name='mealplan',
            unique_together={('user', 'week_start', 'day', 'meal_type')},
        ),
        migrations.CreateModel(
            name='FridgeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('normalized_name', models.CharField(db_index=True, max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fridge_ingredients', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['normalized_name'],
                'unique_together': {('user', 'normalized_name')},
            },
        ),
    ]
