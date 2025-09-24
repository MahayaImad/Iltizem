from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from django.utils import timezone

User = get_user_model()


class Association(models.Model):
    """
    Association de résidence - Entité principale du système
    """

    # Plans disponibles selon le cahier des charges
    PLAN_CHOICES = [
        ('basique', 'Basique'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]

    # Informations de base
    nom = models.CharField(max_length=100, verbose_name='Nom de l\'association')
    adresse = models.TextField(verbose_name='Adresse complète')

    # Plan et capacité
    plan = models.CharField(
        max_length=10,
        choices=PLAN_CHOICES,
        default='basique',
        verbose_name='Plan d\'abonnement'
    )
    nombre_logements = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        verbose_name='Nombre de logements'
    )

    # Administration
    admin_principal = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='association_geree',
        limit_choices_to={'role': 'admin_association'},
        verbose_name='Administrateur principal'
    )

    # Multi-admins (Silver+)
    admins_secondaires = models.ManyToManyField(
        User,
        related_name='associations_secondaires',
        blank=True,
        limit_choices_to={'role': 'admin_association'},
        verbose_name='Administrateurs secondaires'
    )

    # Configuration cotisations par défaut
    montant_cotisation_defaut = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Montant cotisation par défaut (DA)'
    )

    # Métadonnées
    actif = models.BooleanField(default=True, verbose_name='Association active')
    date_creation = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Date de création')
    date_modification = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Dernière modification')

    class Meta:
        verbose_name = 'Association'
        verbose_name_plural = 'Associations'
        db_table = 'iltizem_associations'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.get_plan_display()})"

    def get_logements_count(self):
        """Nombre de logements créés"""
        return self.logements.count()

    def get_logements_occupes_count(self):
        """Nombre de logements avec résidents"""
        return self.logements.filter(resident__isnull=False).count()

    def get_taux_occupation(self):
        """Pourcentage d'occupation"""
        total = self.get_logements_count()
        if total == 0:
            return 0
        occupes = self.get_logements_occupes_count()
        return round((occupes / total) * 100, 1)

    def can_use_feature(self, feature):
        """
        Vérifier si le plan permet d'utiliser une fonctionnalité
        Basique: fonctions de base
        Silver: + dépenses, multi-admins, SMS
        Gold: + paiement en ligne, sondages
        """
        features_by_plan = {
            'basique': ['cotisations', 'paiements_manuels', 'emails', 'rapports_simple'],
            'silver': ['cotisations', 'paiements_manuels', 'emails', 'rapports_simple',
                       'depenses', 'multi_admins', 'sms', 'export_excel'],
            'gold': ['cotisations', 'paiements_manuels', 'emails', 'rapports_simple',
                     'depenses', 'multi_admins', 'sms', 'export_excel',
                     'paiement_en_ligne', 'sondages', 'statistiques_avancees']
        }
        return feature in features_by_plan.get(self.plan, [])


class Logement(models.Model):
    """
    Logement dans une association - Simple et efficace
    """

    # Informations de base
    association = models.ForeignKey(
        Association,
        on_delete=models.CASCADE,
        related_name='logements',
        verbose_name='Association'
    )
    numero = models.CharField(max_length=20, verbose_name='Numéro/Nom du logement')

    # Résident (optionnel)
    resident = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logement',
        limit_choices_to={'role': 'resident'},
        verbose_name='Résident'
    )

    # Informations complémentaires
    etage = models.CharField(max_length=10, blank=True, verbose_name='Étage')
    superficie = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name='Surface (m²)'
    )
    nombre_pieces = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name='Nombre de pièces'
    )

    # Cotisation personnalisée (optionnel)
    montant_cotisation_personnalise = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Montant cotisation personnalisé (DA)'
    )

    # Métadonnées
    actif = models.BooleanField(default=True, verbose_name='Logement actif')
    date_creation = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Date de création')
    date_modification = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Dernière modification')

    class Meta:
        verbose_name = 'Logement'
        verbose_name_plural = 'Logements'
        db_table = 'iltizem_logements'
        ordering = ['association', 'numero']
        unique_together = ['association', 'numero']  # Pas de doublons

    def __str__(self):
        resident_info = f" - {self.resident.get_full_name()}" if self.resident else " - Libre"
        return f"{self.association.nom} - {self.numero}{resident_info}"

    def get_montant_cotisation(self):
        """
        Montant de cotisation pour ce logement
        Priorité: montant personnalisé > montant par défaut association
        """
        if self.montant_cotisation_personnalise:
            return self.montant_cotisation_personnalise
        return self.association.montant_cotisation_defaut

    def is_occupe(self):
        """Vérifier si le logement est occupé"""
        return self.resident is not None

    def get_cotisations_en_retard(self):
        """Nombre de cotisations en retard pour ce logement"""
        return self.cotisations.filter(statut='retard').count()

    def get_dernier_paiement(self):
        """Date du dernier paiement"""
        try:
            derniere_cotisation_payee = self.cotisations.filter(
                statut='payee'
            ).latest('periode')
            return derniere_cotisation_payee.paiement.date_paiement
        except:
            return None