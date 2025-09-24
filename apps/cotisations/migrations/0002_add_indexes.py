from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_cotisation_statut ON iltizam_cotisations(statut);",
            reverse_sql="DROP INDEX idx_cotisation_statut ON iltizam_cotisations;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_cotisation_periode ON iltizam_cotisations(periode);",
            reverse_sql="DROP INDEX idx_cotisation_periode ON iltizam_cotisations;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_cotisation_echeance ON iltizam_cotisations(date_echeance);",
            reverse_sql="DROP INDEX idx_cotisation_echeance ON iltizam_cotisations;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_cotisation_logement_periode ON iltizam_cotisations(logement_id, periode);",
            reverse_sql="DROP INDEX idx_cotisation_logement_periode ON iltizam_cotisations;"
        ),
    ]
