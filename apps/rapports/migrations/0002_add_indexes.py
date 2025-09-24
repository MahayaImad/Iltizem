from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('rapports', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_rapport_periode ON iltizem_rapports(periode);",
            reverse_sql="DROP INDEX idx_rapport_periode ON iltizem_rapports;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_rapport_statut ON iltizem_rapports(statut);",
            reverse_sql="DROP INDEX idx_rapport_statut ON iltizem_rapports;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_rapport_type ON iltizem_rapports(type_rapport);",
            reverse_sql="DROP INDEX idx_rapport_type ON iltizem_rapports;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_rapport_association_periode ON iltizem_rapports(association_id, periode);",
            reverse_sql="DROP INDEX idx_rapport_association_periode ON iltizem_rapports;"
        ),
    ]
