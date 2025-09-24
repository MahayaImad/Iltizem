from django.db import models
class Association(models.Model):
    """Association de résidence"""
    PLAN_CHOICES = [
        ('basique', 'Basique'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]

    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    nombre_logements = models.PositiveIntegerField()
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='basique')
    admin_principal = models.ForeignKey(User, on_delete=models.CASCADE, related_name='association_administree')
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom


class Logement(models.Model):
    """Logement dans une association"""
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='logements')
    numero = models.CharField(max_length=10)
    resident = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='logement')
    superficie = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ['association', 'numero']

    def __str__(self):
        return f"{self.association.nom} - {self.numero}"