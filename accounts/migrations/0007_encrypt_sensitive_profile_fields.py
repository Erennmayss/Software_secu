from django.db import migrations, models

from accounts.security import encrypt_value


def encrypt_user_fields(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    for user in User.objects.all():
        updates = []
        if getattr(user, 'restrictions', ''):
            user.restrictions = encrypt_value(user.restrictions)
            updates.append('restrictions')
        if getattr(user, 'aliments_a_eviter', ''):
            user.aliments_a_eviter = encrypt_value(user.aliments_a_eviter)
            updates.append('aliments_a_eviter')
        constraints = list(user.health_constraints.all().values_list('name', flat=True))
        user.health_constraints_snapshot = encrypt_value(','.join(constraints))
        updates.append('health_constraints_snapshot')
        if updates:
            user.save(update_fields=updates)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_activity_level'),
        ('accounts', '0006_sync_activity_level_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='health_constraints_snapshot',
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(encrypt_user_fields, migrations.RunPython.noop),
    ]
