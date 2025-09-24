from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('associations', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_association_plan_actif ON iltizam_associations(plan, actif);",
            reverse_sql="DROP INDEX idx_association_plan_actif ON iltizam_associations;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_logement_association ON iltizam_logements(association_id);",
            reverse_sql="DROP INDEX idx_logement_association ON iltizam_logements;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_logement_resident ON iltizam_logements(resident_id);",
            reverse_sql="DROP INDEX idx_logement_resident ON iltizam_logements;"
        ),
    ]