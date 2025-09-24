from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('paiements', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_paiement_methode ON iltizam_paiements(methode);",
            reverse_sql="DROP INDEX idx_paiement_methode ON iltizam_paiements;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_paiement_date ON iltizam_paiements(date_paiement);",
            reverse_sql="DROP INDEX idx_paiement_date ON iltizam_paiements;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_paiement_enregistrement ON iltizam_paiements(date_enregistrement);",
            reverse_sql="DROP INDEX idx_paiement_enregistrement ON iltizam_paiements;"
        ),
    ]