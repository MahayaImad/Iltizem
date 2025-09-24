"""
L'application API n'a pas besoin de models spécifiques.
Elle expose les models existants via les serializers :
- User (accounts)
- Association, Logement (associations)
- TypeCotisation, Cotisation (cotisations)
- Paiement (paiements)
- NotificationTemplate, NotificationLog (notifications)
- RapportMensuel (rapports)

Ce fichier est créé pour respecter la structure Django standard.
"""

from django.db import models

# Pas de nouveaux models nécessaires pour l'API
# Toutes les données sont exposées via les autres applications

# Si besoin futur d'un model spécifique à l'API :
# class APIKey(models.Model):
#     """Clés API pour authentification externe"""
#     nom = models.CharField(max_length=100)
#     cle = models.CharField(max_length=64, unique=True)
#     actif = models.BooleanField(default=True)
#     date_creation = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         verbose_name = 'Clé API'
#         verbose_name_plural = 'Clés API'
