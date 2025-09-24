from django.db import models
from django.contrib.auth import get_user_model
from django.template import Template, Context
from django.utils import timezone

User = get_user_model()


class NotificationTemplate(models.Model):
    """Templates de notifications réutilisables"""

    TYPE_CHOICES = [
        ('cotisation_due', 'Nouvelle cotisation due'),
        ('rappel_retard', 'Rappel de retard'),
        ('confirmation_paiement', 'Confirmation de paiement'),
        ('bienvenue', 'Message de bienvenue'),
        ('assemblage_generale', 'Convocation assemblée générale'),
        ('maintenance', 'Avis de maintenance'),
        ('personnalise', 'Message personnalisé'),
    ]

    CANAL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Email + SMS'),
    ]

    nom = models.CharField(max_length=100, verbose_name='Nom du template')
    type_notification = models.CharField(
        max_length=30,  # assez grand pour tous les choix
        choices=TYPE_CHOICES,
        verbose_name='Type de notification'
    )
    canal = models.CharField(
        max_length=10,
        choices=CANAL_CHOICES,
        default='email',
        verbose_name='Canal d\'envoi'
    )
    sujet = models.CharField(max_length=200, verbose_name='Sujet (pour emails)')
    message = models.TextField(
        null=True,
        verbose_name='Message',
        help_text='Variables disponibles: {{nom}}, {{montant}}, {{periode}}, {{date_echeance}}, {{association}}'
    )
    actif = models.BooleanField(default=True, verbose_name='Template actif')
    envoyer_automatiquement = models.BooleanField(
        default=False,
        verbose_name='Envoi automatique'
    )
    date_creation = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Date de création')
    date_modification = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Dernière modification')
    cree_par = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Créé par',
        default=1
    )

    class Meta:
        verbose_name = 'Template de notification'
        verbose_name_plural = 'Templates de notification'
        db_table = 'iltizem_notification_templates'
        ordering = ['type_notification', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.get_type_notification_display()})"

    def render_message(self, context_data):
        try:
            template = Template(self.message)
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            return f"Erreur dans le template: {str(e)}"

    def render_sujet(self, context_data):
        try:
            template = Template(self.sujet)
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            return f"Erreur sujet: {str(e)}"


class NotificationLog(models.Model):
    """Journal des notifications envoyées - Traçabilité complète"""

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('envoye', 'Envoyé'),
        ('erreur', 'Erreur'),
        ('annule', 'Annulé'),
    ]

    association = models.ForeignKey(
        'associations.Association',
        on_delete=models.CASCADE,
        related_name='notifications_log',
        verbose_name='Association',
        null = True,
    )
    destinataire = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications_recues',
        verbose_name='Destinataire',
        null=True,
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Template utilisé'
    )
    type_notification = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('sms', 'SMS'), ('push', 'Push')],
        verbose_name="Type de notification",
        default='email',
    )

    canal = models.CharField(max_length=10,default='email', verbose_name='Canal utilisé')
    sujet = models.CharField(max_length=200, verbose_name='Sujet')
    message = models.TextField(null= True, verbose_name='Message envoyé')

    email_destinataire = models.EmailField(blank=True, verbose_name='Email')
    telephone_destinataire = models.CharField(max_length=15, blank=True, verbose_name='Téléphone')

    statut = models.CharField(
        max_length=15,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name='Statut'
    )
    erreur_message = models.TextField(blank=True, verbose_name='Message d\'erreur')

    date_programmee = models.DateTimeField(null=True, verbose_name='Date programmée')
    date_envoi = models.DateTimeField(null=True, blank=True, verbose_name='Date d\'envoi')
    tentatives = models.PositiveIntegerField(default=0, verbose_name='Nombre de tentatives')

    envoye_par = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications_envoyees',
        verbose_name='Envoyé par',
        null = True,
    )
    date_creation = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Date de création')

    class Meta:
        verbose_name = 'Log de notification'
        verbose_name_plural = 'Logs de notifications'
        db_table = 'iltizem_notification_logs'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['association', 'statut']),
            models.Index(fields=['destinataire', 'date_envoi']),
        ]

    def __str__(self):
        return f"{self.destinataire.get_full_name()} - {self.get_statut_display()} - {self.date_creation.strftime('%d/%m/%Y')}"

    def marquer_envoye(self):
        from django.utils import timezone
        self.statut = 'envoye'
        self.date_envoi = timezone.now()
        self.save()

    def marquer_erreur(self, message_erreur):
        self.statut = 'erreur'
        self.erreur_message = message_erreur
        self.tentatives += 1
        self.save()

    def peut_reessayer(self):
        return self.statut == 'erreur' and self.tentatives < 3
