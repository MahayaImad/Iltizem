from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_cotisation_statut ON iltizem_cotisations(statut);",
            reverse_sql="DROP INDEX idx_cotisation_statut ON iltizem_cotisations;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_cotisation_periode ON iltizem_cotisations(periode);",
            reverse_sql="DROP INDEX idx_cotisation_periode ON iltizem_cotisations;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_cotisation_echeance ON iltizem_cotisations(date_echeance);",
            reverse_sql="DROP INDEX idx_cotisation_echeance ON iltizem_cotisations;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_cotisation_logement_periode ON iltizem_cotisations(logement_id, periode);",
            reverse_sql="DROP INDEX idx_cotisation_logement_periode ON iltizem_cotisations;"
        ),
    ]
