from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cotisations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Montant (DA)')),
                ('methode', models.CharField(choices=[('especes', 'Espèces'), ('virement', 'Virement'), ('cheque', 'Chèque'), ('en_ligne', 'Paiement en ligne')], max_length=10, verbose_name='Méthode de paiement')),
                ('reference', models.CharField(blank=True, max_length=50, verbose_name='Référence')),
                ('date_paiement', models.DateField(verbose_name='Date de paiement')),
                ('date_enregistrement', models.DateTimeField(auto_now_add=True, verbose_name='Date d\'enregistrement')),
                ('recu_genere', models.BooleanField(default=False, verbose_name='Reçu généré')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('cotisation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paiement', to='cotisations.cotisation', verbose_name='Cotisation')),
                ('enregistre_par', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paiements_enregistres', to=settings.AUTH_USER_MODEL, verbose_name='Enregistré par')),
            ],
            options={
                'verbose_name': 'Paiement',
                'verbose_name_plural': 'Paiements',
                'db_table': 'iltizam_paiements',
                'ordering': ['-date_enregistrement'],
            },
        ),
    ]