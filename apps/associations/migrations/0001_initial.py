from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Association',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, verbose_name='Nom')),
                ('adresse', models.TextField(verbose_name='Adresse')),
                ('nombre_logements', models.PositiveIntegerField(verbose_name='Nombre de logements')),
                ('plan', models.CharField(choices=[('basique', 'Basique'), ('silver', 'Silver'), ('gold', 'Gold')], default='basique', max_length=10, verbose_name='Plan')),
                ('actif', models.BooleanField(default=True, verbose_name='Actif')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('admin_principal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='association_administree', to=settings.AUTH_USER_MODEL, verbose_name='Administrateur principal')),
            ],
            options={
                'verbose_name': 'Association',
                'verbose_name_plural': 'Associations',
                'db_table': 'iltizam_associations',
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='Logement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=10, verbose_name='Numéro')),
                ('superficie', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Superficie (m²)')),
                ('association', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logements', to='associations.association', verbose_name='Association')),
                ('resident', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logement', to=settings.AUTH_USER_MODEL, verbose_name='Résident')),
            ],
            options={
                'verbose_name': 'Logement',
                'verbose_name_plural': 'Logements',
                'db_table': 'iltizam_logements',
                'ordering': ['association', 'numero'],
            },
        ),
        migrations.AddConstraint(
            model_name='logement',
            constraint=models.UniqueConstraint(fields=('association', 'numero'), name='unique_logement_association'),
        ),
        migrations.AddConstraint(
            model_name='logement',
            constraint=models.UniqueConstraint(fields=('resident',), condition=models.Q(('resident__isnull', False)), name='unique_resident_logement'),
        ),
    ]