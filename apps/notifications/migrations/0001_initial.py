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
            name='NotificationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50, verbose_name='Nom du template')),
                ('type_notification', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS')], max_length=10, verbose_name='Type')),
                ('sujet', models.CharField(max_length=200, verbose_name='Sujet')),
                ('contenu', models.TextField(verbose_name='Contenu')),
                ('actif', models.BooleanField(default=True, verbose_name='Actif')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
            ],
            options={
                'verbose_name': 'Template de notification',
                'verbose_name_plural': 'Templates de notifications',
                'db_table': 'iltizam_notification_templates',
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_notification', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS')], max_length=10, verbose_name='Type')),
                ('destinataire', models.CharField(max_length=100, verbose_name='Destinataire')),
                ('sujet', models.CharField(max_length=200, verbose_name='Sujet')),
                ('contenu', models.TextField(verbose_name='Contenu')),
                ('statut', models.CharField(choices=[('envoye', 'Envoyé'), ('erreur', 'Erreur'), ('en_attente', 'En attente')], default='en_attente', max_length=15, verbose_name='Statut')),
                ('date_envoi', models.DateTimeField(auto_now_add=True, verbose_name='Date d\'envoi')),
                ('erreur_message', models.TextField(blank=True, verbose_name='Message d\'erreur')),
                ('association', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='associations.association', verbose_name='Association')),
                ('envoye_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Envoyé par')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='notifications.notificationtemplate', verbose_name='Template utilisé')),
            ],
            options={
                'verbose_name': 'Log de notification',
                'verbose_name_plural': 'Logs de notifications',
                'db_table': 'iltizam_notification_logs',
                'ordering': ['-date_envoi'],
            },
        ),
    ]