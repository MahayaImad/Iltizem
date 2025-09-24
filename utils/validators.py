from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

def valider_telephone_algerie(value):
    """Valider un numéro de téléphone algérien"""
    pattern = r'^(\+213|0)[567]\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Numéro de téléphone invalide. Format: +213XXXXXXXX ou 0XXXXXXXX'),
            code='invalid'
        )

def valider_montant_positif(value):
    """Valider qu'un montant est positif"""
    if value <= 0:
        raise ValidationError(
            _('Le montant doit être supérieur à 0'),
            code='invalid'
        )