from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

# Imports des modèles liés
User = get_user_model()
# Import dynamique pour éviter les imports circulaires
from apps.cotisations.models import Cotisation


class Paiement(models.Model):
    """
    Paiement effectué par un résident
    Enregistrement simple et traçable
    """

    # Méthodes de paiement disponibles
    METHODE_CHOICES = [
        ('especes', 'Espèces'),
        ('virement', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('carte', 'Carte bancaire'),
        ('en_ligne', 'Paiement en ligne'),  # Gold uniquement
        ('compensation', 'Compensation'),  # Pour ajustements
    ]

    # Relations principales
    cotisation = models.OneToOneField(
        Cotisation,
        on_delete=models.CASCADE,
        related_name='paiement',
        verbose_name='Cotisation payée'
    )

    # Informations de paiement
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Montant payé (DA)'
    )
    methode = models.CharField(
        max_length=15,
        choices=METHODE_CHOICES,
        verbose_name='Méthode de paiement'
    )

    # Informations complémentaires selon la méthode
    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Référence (N° chèque, virement, etc.)'
    )

    # Dates
    date_paiement = models.DateField(verbose_name='Date du paiement')

    # Traçabilité
    enregistre_par = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='paiements_enregistres',
        verbose_name='Enregistré par'
    )
    date_enregistrement = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'enregistrement'
    )

    # Reçu et confirmation
    recu_genere = models.BooleanField(
        default=False,
        verbose_name='Reçu généré'
    )
    numero_recu = models.CharField(
        max_length=20,
        blank=True,
        unique=True,
        verbose_name='Numéro de reçu'
    )

    # Notes optionnelles
    notes = models.TextField(
        blank=True,
        verbose_name='Notes/Commentaires'
    )

    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        db_table = 'iltizem_paiements'
        ordering = ['-date_enregistrement']
        indexes = [
            models.Index(fields=['date_paiement', 'methode']),
            models.Index(fields=['enregistre_par', 'date_enregistrement']),
        ]

    def __str__(self):
        return f"Paiement {self.cotisation} - {self.montant} DA ({self.get_methode_display()})"

    def get_resident(self):
        """Raccourci pour accéder au résident"""
        return self.cotisation.get_resident()

    def get_association(self):
        """Raccourci pour accéder à l'association"""
        return self.cotisation.get_association()

    def get_logement(self):
        """Raccourci pour accéder au logement"""
        return self.cotisation.logement

    def is_paiement_complet(self):
        """Vérifier si le paiement couvre entièrement la cotisation"""
        return self.montant >= self.cotisation.montant

    def get_difference(self):
        """Différence entre montant payé et montant dû"""
        return self.montant - self.cotisation.montant

    def save(self, *args, **kwargs):
        """
        Override save pour actions automatiques
        """
        # Générer numéro de reçu si pas encore fait
        if not self.numero_recu:
            self.numero_recu = self._generer_numero_recu()

        # Marquer la cotisation comme payée
        if self.pk is None:  # Nouveau paiement
            self.cotisation.marquer_payee()

        super().save(*args, **kwargs)

    def _generer_numero_recu(self):
        """
        Générer un numéro de reçu unique
        Format: ASSO-YYYY-NNNN
        """
        association = self.get_association()
        annee = timezone.now().year

        # Compter les paiements de cette année pour cette association
        count = Paiement.objects.filter(
            cotisation__logement__association=association,
            date_enregistrement__year=annee
        ).count() + 1

        # Préfixe association (3 premiers caractères en majuscules)
        prefixe = association.nom[:3].upper().replace(' ', '')

        return f"{prefixe}-{annee}-{count:04d}"

    def generer_recu_pdf(self):
        """
        Marquer le reçu comme généré
        La génération du PDF sera faite dans les vues
        """
        self.recu_genere = True
        self.save()

    def get_context_recu(self):
        """
        Contexte pour la génération du reçu PDF
        """
        resident = self.get_resident()
        association = self.get_association()
        logement = self.get_logement()

        return {
            'paiement': self,
            'resident': resident,
            'association': association,
            'logement': logement,
            'cotisation': self.cotisation,
            'date_generation': timezone.now(),
            'numero_recu': self.numero_recu,
        }

    def get_context_notification(self):
        """
        Contexte pour les notifications de confirmation de paiement
        """
        resident = self.get_resident()
        association = self.get_association()

        return {
            'nom': resident.get_full_name() if resident else 'Résident',
            'prenom': resident.first_name if resident else '',
            'logement': self.cotisation.logement.numero,
            'montant': self.montant,
            'periode': self.cotisation.periode.strftime('%B %Y'),
            'date_paiement': self.date_paiement.strftime('%d/%m/%Y'),
            'methode': self.get_methode_display(),
            'reference': self.reference,
            'numero_recu': self.numero_recu,
            'association': association.nom,
        }


class HistoriquePaiement(models.Model):
    """
    Historique des modifications de paiements
    Pour traçabilité complète (optionnel - peut être ajouté plus tard)
    """

    ACTION_CHOICES = [
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
        ('annulation', 'Annulation'),
    ]

    # Relations
    paiement = models.ForeignKey(
        Paiement,
        on_delete=models.CASCADE,
        related_name='historique',
        verbose_name='Paiement'
    )

    # Action effectuée
    action = models.CharField(
        max_length=15,
        choices=ACTION_CHOICES,
        verbose_name='Action'
    )

    # Données avant modification (JSON)
    anciennes_donnees = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Anciennes données'
    )
    nouvelles_donnees = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Nouvelles données'
    )

    # Justification
    raison = models.TextField(
        blank=True,
        verbose_name='Raison de la modification'
    )

    # Traçabilité
    effectue_par = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Effectué par'
    )
    date_action = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de l\'action'
    )

    class Meta:
        verbose_name = 'Historique de paiement'
        verbose_name_plural = 'Historiques des paiements'
        db_table = 'iltizem_historique_paiements'
        ordering = ['-date_action']

    def __str__(self):
        return f"{self.get_action_display()} - {self.paiement} - {self.date_action.strftime('%d/%m/%Y %H:%M')}"