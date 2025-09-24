"""
L'application residents n'a pas besoin de models spécifiques.
Elle utilise les models existants :
- User (resident)
- Logement
- Cotisation
- Paiement
- Association

Ce fichier est créé pour respecter la structure Django standard.
"""

from django.db import models
from django.contrib.auth import get_user_model

# Pas de nouveaux models nécessaires pour les résidents
# Toutes les données sont dans les autres applications

# Si besoin futur d'un model spécifique aux résidents :
# class ProfilResident(models.Model):
#     """Profil étendu pour les résidents"""
#     user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
#     preferences_notifications = models.BooleanField(default=True)
#     date_emmenagement = models.DateField(null=True, blank=True)
#
#     class Meta:
#         verbose_name = 'Profil Résident'
#         verbose_name_plural = 'Profils Résidents'