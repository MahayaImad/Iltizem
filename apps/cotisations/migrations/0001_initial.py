from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('associations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeCotisation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50, verbose_name='Nom')),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Montant (DA)')),
                ('periodicite', models.CharField(choices=[('mensuelle', 'Mensuelle'), ('trimestrielle', 'Trimestrielle'), ('annuelle', 'Annuelle')], max_length=15, verbose_name='Périodicité')),
                ('actif', models.BooleanField(default=True, verbose_name='Actif')),
                ('date_creation', models.DateTimeField(default=timezone.now, editable=False, verbose_name='Date de création')),
                ('association', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='types_cotisations', to='associations.association', verbose_name='Association')),
            ],
            options={
                'verbose_name': 'Type de cotisation',
                'verbose_name_plural': 'Types de cotisations',
                'db_table': 'iltizem_types_cotisations',
                'ordering': ['association', 'nom'],
            },
        ),
        migrations.CreateModel(
            name='Cotisation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periode', models.DateField(verbose_name='Période')),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Montant (DA)')),
                ('statut', models.CharField(choices=[('due', 'Due'), ('payee', 'Payée'), ('retard', 'En retard')], default='due', max_length=10, verbose_name='Statut')),
                ('date_echeance', models.DateField(verbose_name='Date d\'échéance')),
                ('date_creation', models.DateTimeField(default=timezone.now, editable=False, verbose_name='Date de création')),
                ('logement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cotisations', to='associations.logement', verbose_name='Logement')),
                ('type_cotisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cotisations', to='cotisations.typecotisation', verbose_name='Type de cotisation')),
            ],
            options={
                'verbose_name': 'Cotisation',
                'verbose_name_plural': 'Cotisations',
                'db_table': 'iltizem_cotisations',
                'ordering': ['-periode', 'logement'],
            },
        ),
        migrations.AddConstraint(
            model_name='cotisation',
            constraint=models.UniqueConstraint(fields=('logement', 'type_cotisation', 'periode'), name='unique_cotisation_periode'),
        ),
    ]