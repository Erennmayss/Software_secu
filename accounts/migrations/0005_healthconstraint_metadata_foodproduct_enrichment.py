from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_age_user_aliments_a_eviter_user_culinary_level_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodproduct',
            name='carbs',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='foodproduct',
            name='fats',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='foodproduct',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='recipes/'),
        ),
        migrations.AddField(
            model_name='foodproduct',
            name='preparation_steps',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='foodproduct',
            name='proteins',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='healthconstraint',
            name='color',
            field=models.CharField(default='#e8621a', max_length=20),
        ),
        migrations.AddField(
            model_name='healthconstraint',
            name='constraint_type',
            field=models.CharField(choices=[('disease', 'Maladie'), ('allergen', 'Allergene')], default='disease', max_length=20),
        ),
        migrations.AddField(
            model_name='healthconstraint',
            name='icon',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='foodproduct',
            name='category',
            field=models.CharField(choices=[('sale', 'Sale'), ('sucre', 'Sucre'), ('healthy', 'Healthy'), ('vegan', 'Vegan')], default='sale', max_length=50),
        ),
        migrations.AlterField(
            model_name='foodproduct',
            name='difficulty',
            field=models.CharField(blank=True, choices=[('easy', 'Facile'), ('medium', 'Modere'), ('hard', 'Complexe')], max_length=20),
        ),
        migrations.AlterField(
            model_name='foodproduct',
            name='nutriscore',
            field=models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1),
        ),
    ]
