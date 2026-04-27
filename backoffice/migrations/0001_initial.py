from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0005_healthconstraint_metadata_foodproduct_enrichment'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubstitutionRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forbidden_ingredient', models.CharField(max_length=255)),
                ('substitute', models.CharField(max_length=255)),
                ('difficulty', models.CharField(choices=[('easy', 'Facile'), ('moderate', 'Modere'), ('complex', 'Complexe')], default='easy', max_length=20)),
                ('target_constraint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='substitution_rules', to='accounts.healthconstraint')),
            ],
            options={
                'ordering': ['target_constraint__name', 'forbidden_ingredient'],
                'unique_together': {('target_constraint', 'forbidden_ingredient', 'substitute')},
            },
        ),
    ]
