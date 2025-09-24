from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('associations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RapportMensuel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periode', models.DateField(verbose_name='Période (mois/année)')),
                ('type_rapport', models.CharField(choices=[('mensuel', 'Rapport mensuel'), ('trimestriel', 'Rapport trimestriel'), ('annuel', 'Rapport annuel'), ('personnalise', 'Rapport personnalisé')], default='mensuel', max_length=15, verbose_name='Type de rapport')),
                ('format_fichier', models.CharField(choices=[('pdf', 'PDF'), ('excel', 'Excel'), ('csv', 'CSV')], default='pdf', max_length=10, verbose_name='Format')),
                ('fichier', models.FileField(blank=True, upload_to='rapports/%Y/%m/', verbose_name='Fichier généré')),
                ('donnees_json', models.JSONField(blank=True, null=True, verbose_name='Données JSON')),
                ('statut', models.CharField(choices=[('genere', 'Généré'), ('en_cours', 'En cours'), ('erreur', 'Erreur')], default='en_cours', max_length=10, verbose_name='Statut')),
                ('date_generation', models.DateTimeField(auto_now_add=True, verbose_name='Date de génération')),
                ('taille_fichier', models.PositiveIntegerField(blank=True, null=True, verbose_name='Taille (octets)')),
                ('association', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rapports', to='associations.association', verbose_name='Association')),
                ('genere_par', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Généré par')),
            ],
            options={
                'verbose_name': 'Rapport',
                'verbose_name_plural': 'Rapports',
                'db_table': 'iltizam_rapports',
                'ordering': ['-date_generation'],
            },
        ),
        migrations.AddConstraint(
            model_name='rapportmensuel',
            constraint=models.UniqueConstraint(fields=('association', 'periode', 'type_rapport'), name='unique_rapport_periode'),
        ),
    ]
