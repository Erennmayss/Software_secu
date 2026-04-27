from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_healthconstraint_metadata_foodproduct_enrichment'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE accounts_user
                    ADD COLUMN IF NOT EXISTS activity_level varchar(20) NOT NULL DEFAULT 'modere';
                    """,
                    reverse_sql="""
                    ALTER TABLE accounts_user
                    DROP COLUMN IF EXISTS activity_level;
                    """,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='user',
                    name='activity_level',
                    field=models.CharField(blank=True, default='modere', max_length=20),
                ),
            ],
        ),
    ]
