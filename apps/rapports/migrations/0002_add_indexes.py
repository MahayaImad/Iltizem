from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('rapports', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_rapport_periode ON iltizam_rapports(periode);",
            reverse_sql="DROP INDEX idx_rapport_periode ON iltizam_rapports;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_rapport_statut ON iltizam_rapports(statut);",
            reverse_sql="DROP INDEX idx_rapport_statut ON iltizam_rapports;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_rapport_type ON iltizam_rapports(type_rapport);",
            reverse_sql="DROP INDEX idx_rapport_type ON iltizam_rapports;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_rapport_association_periode ON iltizam_rapports(association_id, periode);",
            reverse_sql="DROP INDEX idx_rapport_association_periode ON iltizam_rapports;"
        ),
    ]
