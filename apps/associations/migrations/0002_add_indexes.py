from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('associations', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_association_plan_actif ON iltizem_associations(plan, actif);",
            reverse_sql="DROP INDEX idx_association_plan_actif ON iltizem_associations;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_logement_association ON iltizem_logements(association_id);",
            reverse_sql="DROP INDEX idx_logement_association ON iltizem_logements;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_logement_resident ON iltizem_logements(resident_id);",
            reverse_sql="DROP INDEX idx_logement_resident ON iltizem_logements;"
        ),
    ]