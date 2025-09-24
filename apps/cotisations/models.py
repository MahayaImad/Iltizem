from django.db import models
class TypeCotisation(models.Model):
    """Type de cotisation (mensuelle, trimestrielle, etc.)"""
    PERIODICITE_CHOICES = [
        ('mensuelle', 'Mensuelle'),
        ('trimestrielle', 'Trimestrielle'),
        ('annuelle', 'Annuelle'),
    ]

    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='types_cotisations')
    nom = models.CharField(max_length=50)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    periodicite = models.CharField(max_length=15, choices=PERIODICITE_CHOICES)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} - {self.montant} DA"


class Cotisation(models.Model):
    """Cotisation due par un résident"""
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE, related_name='cotisations')
    type_cotisation = models.ForeignKey(TypeCotisation, on_delete=models.CASCADE)
    periode = models.DateField()  # Mois/trimestre/année concerné
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=10, choices=[
        ('due', 'Due'),
        ('payee', 'Payée'),
        ('retard', 'En retard'),
    ], default='due')
    date_echeance = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['logement', 'type_cotisation', 'periode']

    def __str__(self):
        return f"{self.logement} - {self.periode} - {self.montant} DA"
