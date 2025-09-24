from django.db import models

class Paiement(models.Model):
    """Paiement effectué par un résident"""
    METHODE_CHOICES = [
        ('especes', 'Espèces'),
        ('virement', 'Virement'),
        ('cheque', 'Chèque'),
        ('en_ligne', 'Paiement en ligne'),
    ]

    cotisation = models.OneToOneField(Cotisation, on_delete=models.CASCADE, related_name='paiement')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode = models.CharField(max_length=10, choices=METHODE_CHOICES)
    reference = models.CharField(max_length=50, blank=True)  # N° chèque, référence virement
    date_paiement = models.DateField()
    enregistre_par = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paiements_enregistres')
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    recu_genere = models.BooleanField(default=False)

    def __str__(self):
        return f"Paiement {self.cotisation} - {self.montant} DA"
