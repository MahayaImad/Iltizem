from django.db import models
from django.contrib.auth import get_user_model
from django.template import Template, Context
from django.core.exceptions import ValidationError

User = get_user_model()


class NotificationTemplate(models.Model):
    """Templates de notifications réutilisables"""

    TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]

    nom = models.CharField(max_length=50, verbose_name='Nom du template')
    type_notification = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Type')
    sujet = models.CharField(max_length=200, verbose_name='Sujet')
    contenu = models.TextField(verbose_name='Contenu', help_text='Utilisez {{variable}} pour les variables dynamiques')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')

    class Meta:
        verbose_name = 'Template de notification'
        verbose_name_plural = 'Templates de notifications'
        db_table = 'iltizam_notification_templates'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.get_type_notification_display()})"

    def clean(self):
        """Validation du template Django"""
        try:
            Template(self.contenu)
        except Exception as e:
            raise ValidationError(f"Erreur dans le template: {e}")

    def render(self, context_data):
        """Rendu du template avec les données"""
        template = Template(self.contenu)
        context = Context(context_data)
        return template.render(context)


class NotificationLog(models.Model):
    """Journal des notifications envoyées"""

    TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]

    STATUT_CHOICES = [
        ('envoye', 'Envoyé'),
        ('erreur', 'Erreur'),
        ('en_attente', 'En attente'),
    ]

    type_notification = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Type')
    destinataire = models.CharField(max_length=100, verbose_name='Destinataire')
    sujet = models.CharField(max_length=200, verbose_name='Sujet')
    contenu = models.TextField(verbose_name='Contenu')
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='en_attente', verbose_name='Statut')
    date_envoi = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'envoi')
    erreur_message = models.TextField(blank=True, verbose_name='Message d\'erreur')

    # Relations
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name='Template utilisé')
    association = models.ForeignKey('associations.Association', on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Association')
    envoye_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Envoyé par')

    class Meta:
        verbose_name = 'Log de notification'
        verbose_name_plural = 'Logs de notifications'
        db_table = 'iltizam_notification_logs'
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.get_type_notification_display()} à {self.destinataire} - {self.get_statut_display()}"
