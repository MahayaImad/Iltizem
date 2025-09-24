from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
import json

User = get_user_model()


class RapportMensuel(models.Model):
    """Rapports générés pour les associations"""

    TYPE_CHOICES = [
        ('mensuel', 'Rapport mensuel'),
        ('trimestriel', 'Rapport trimestriel'),
        ('annuel', 'Rapport annuel'),
        ('personnalise', 'Rapport personnalisé'),
    ]

    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]

    STATUT_CHOICES = [
        ('genere', 'Généré'),
        ('en_cours', 'En cours'),
        ('erreur', 'Erreur'),
    ]

    # Informations de base
    association = models.ForeignKey('associations.Association', on_delete=models.CASCADE, related_name='rapports',
                                    verbose_name='Association')
    periode = models.DateField(verbose_name='Période (mois/année)')
    type_rapport = models.CharField(max_length=15, choices=TYPE_CHOICES, default='mensuel',
                                    verbose_name='Type de rapport')
    format_fichier = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf', verbose_name='Format')

    # Fichier et données
    fichier = models.FileField(upload_to='rapports/%Y/%m/', blank=True, verbose_name='Fichier généré')
    donnees_json = models.JSONField(null=True, blank=True, verbose_name='Données JSON')

    # Métadonnées
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='en_cours', verbose_name='Statut')
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name='Date de génération')
    taille_fichier = models.PositiveIntegerField(null=True, blank=True, verbose_name='Taille (octets)')
    genere_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Généré par')

    class Meta:
        verbose_name = 'Rapport'
        verbose_name_plural = 'Rapports'
        db_table = 'iltizem_rapports'
        ordering = ['-date_generation']
        constraints = [
            models.UniqueConstraint(
                fields=['association', 'periode', 'type_rapport'],
                name='unique_rapport_periode'
            )
        ]

    def __str__(self):
        return f"Rapport {self.get_type_rapport_display()} - {self.association.nom} - {self.periode.strftime('%m/%Y')}"

    def get_donnees(self):
        """Récupérer les données JSON décodées"""
        if self.donnees_json:
            return self.donnees_json
        return {}

    def set_donnees(self, data):
        """Enregistrer les données en JSON"""
        self.donnees_json = data
        self.save()

    def get_taille_lisible(self):
        """Taille du fichier en format lisible"""
        if not self.taille_fichier:
            return '-'

        if self.taille_fichier < 1024:
            return f"{self.taille_fichier} octets"
        elif self.taille_fichier < 1024 * 1024:
            return f"{self.taille_fichier / 1024:.1f} KB"
        else:
            return f"{self.taille_fichier / (1024 * 1024):.1f} MB"
