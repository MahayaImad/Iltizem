from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

# Imports des modèles liés
User = get_user_model()
# Import dynamique pour éviter les imports circulaires
from apps.associations.models import Association, Logement


class TypeCotisation(models.Model):
    """
    Type de cotisation (mensuelle, trimestrielle, etc.)
    Configuration par association - Simple et efficace
    """
    PERIODICITE_CHOICES = [
        ('mensuelle', 'Mensuelle'),
        ('trimestrielle', 'Trimestrielle'),
        ('semestrielle', 'Semestrielle'),
        ('annuelle', 'Annuelle'),
    ]

    # Relations
    association = models.ForeignKey(
        Association,
        on_delete=models.CASCADE,
        related_name='types_cotisations',
        verbose_name='Association'
    )

    # Configuration
    nom = models.CharField(max_length=50, verbose_name='Nom du type')
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Montant (DA)'
    )
    periodicite = models.CharField(
        max_length=15,
        choices=PERIODICITE_CHOICES,
        verbose_name='Périodicité'
    )

    # Description optionnelle
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )

    # Statut
    actif = models.BooleanField(default=True, verbose_name='Type actif')

    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Date de création')
    cree_par = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Créé par',
        default=1
    )

    class Meta:
        verbose_name = 'Type de cotisation'
        verbose_name_plural = 'Types de cotisations'
        db_table = 'iltizem_types_cotisations'
        ordering = ['association', 'nom']
        unique_together = ['association', 'nom']  # Pas de doublons par association

    def __str__(self):
        return f"{self.nom} - {self.montant} DA ({self.get_periodicite_display()})"

    def get_next_period(self, current_period):
        """
        Calculer la prochaine période selon la périodicité
        current_period: date de la période actuelle
        """
        if self.periodicite == 'mensuelle':
            return current_period + relativedelta(months=1)
        elif self.periodicite == 'trimestrielle':
            return current_period + relativedelta(months=3)
        elif self.periodicite == 'semestrielle':
            return current_period + relativedelta(months=6)
        elif self.periodicite == 'annuelle':
            return current_period + relativedelta(years=1)
        return current_period

    def get_echeance_from_periode(self, periode):
        """
        Calculer la date d'échéance depuis la période
        Exemple: période janvier 2024 -> échéance 31 janvier 2024
        """
        if self.periodicite == 'mensuelle':
            # Dernier jour du mois
            next_month = periode + relativedelta(months=1)
            return (next_month - timedelta(days=1))
        elif self.periodicite == 'trimestrielle':
            # Fin du trimestre (90 jours après)
            return periode + relativedelta(months=3) - timedelta(days=1)
        elif self.periodicite == 'semestrielle':
            # Fin du semestre
            return periode + relativedelta(months=6) - timedelta(days=1)
        elif self.periodicite == 'annuelle':
            # Fin de l'année
            return periode + relativedelta(years=1) - timedelta(days=1)
        return periode + timedelta(days=30)  # Par défaut 30 jours


class Cotisation(models.Model):
    """
    Cotisation due par un résident
    Entité centrale du système - Simple et complète
    """

    # Statuts possibles
    STATUT_CHOICES = [
        ('due', 'Due'),
        ('payee', 'Payée'),
        ('retard', 'En retard'),
        ('annulee', 'Annulée'),
    ]

    # Relations principales
    logement = models.ForeignKey(
        Logement,
        on_delete=models.CASCADE,
        related_name='cotisations',
        verbose_name='Logement'
    )
    type_cotisation = models.ForeignKey(
        TypeCotisation,
        on_delete=models.CASCADE,
        verbose_name='Type de cotisation'
    )

    # Période et montant
    periode = models.DateField(verbose_name='Période (mois/trimestre/année)')
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Montant (DA)'
    )

    # Dates importantes
    date_echeance = models.DateField(verbose_name='Date d\'échéance')

    # Statut
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='due',
        verbose_name='Statut'
    )

    # Description optionnelle
    description = models.TextField(
        blank=True,
        verbose_name='Description/Note'
    )

    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Date de création')
    date_modification = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Dernière modification')
    cree_par = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Créé par',
        default=1
    )

    class Meta:
        verbose_name = 'Cotisation'
        verbose_name_plural = 'Cotisations'
        db_table = 'iltizem_cotisations'
        ordering = ['-periode', '-date_creation']
        unique_together = ['logement', 'type_cotisation', 'periode']  # Une seule cotisation par logement/type/période
        indexes = [
            models.Index(fields=['statut', 'date_echeance']),
            models.Index(fields=['logement', 'periode']),
        ]

    def __str__(self):
        return f"{self.logement} - {self.periode.strftime('%B %Y')} - {self.montant} DA"

    def is_en_retard(self):
        """Vérifier si la cotisation est en retard"""
        return self.date_echeance < date.today() and self.statut == 'due'

    def get_jours_retard(self):
        """Nombre de jours de retard"""
        if self.is_en_retard():
            return (date.today() - self.date_echeance).days
        return 0

    def get_resident(self):
        """Raccourci pour accéder au résident"""
        return self.logement.resident

    def get_association(self):
        """Raccourci pour accéder à l'association"""
        return self.logement.association

    def marquer_payee(self):
        """Marquer la cotisation comme payée (appelé lors d'un paiement)"""
        self.statut = 'payee'
        self.save()

    def save(self, *args, **kwargs):
        """
        Override save pour mettre à jour automatiquement le statut retard
        """
        # Mise à jour automatique du statut en retard
        if self.statut == 'due' and self.date_echeance < date.today():
            self.statut = 'retard'
        elif self.statut == 'retard' and self.date_echeance >= date.today():
            self.statut = 'due'

        super().save(*args, **kwargs)

    def get_context_notification(self):
        """
        Contexte pour les templates de notification
        Variables utilisables dans les templates
        """
        resident = self.get_resident()
        association = self.get_association()

        return {
            'nom': resident.get_full_name() if resident else 'Résident',
            'prenom': resident.first_name if resident else '',
            'nom_famille': resident.last_name if resident else '',
            'logement': self.logement.numero,
            'montant': self.montant,
            'periode': self.periode.strftime('%B %Y'),
            'date_echeance': self.date_echeance.strftime('%d/%m/%Y'),
            'jours_retard': self.get_jours_retard(),
            'association': association.nom,
            'type_cotisation': self.type_cotisation.nom,
            'statut': self.get_statut_display(),
        }