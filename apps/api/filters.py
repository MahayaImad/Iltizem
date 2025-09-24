import django_filters
from django.db import models
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from apps.associations.models import Association, Logement
from apps.cotisations.models import Cotisation, TypeCotisation
from apps.paiements.models import Paiement
from apps.notifications.models import NotificationLog
from apps.rapports.models import RapportMensuel


class AssociationFilter(django_filters.FilterSet):
    """Filtres pour les associations"""

    plan = django_filters.ChoiceFilter(choices=Association._meta.get_field('plan').choices)
    actif = django_filters.BooleanFilter()
    nom = django_filters.CharFilter(lookup_expr='icontains')
    date_creation = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Association
        fields = ['plan', 'actif', 'nom', 'date_creation']


class CotisationFilter(django_filters.FilterSet):
    """Filtres pour les cotisations"""

    statut = django_filters.ChoiceFilter(choices=Cotisation._meta.get_field('statut').choices)
    periode = django_filters.DateFromToRangeFilter()
    date_echeance = django_filters.DateFromToRangeFilter()
    montant = django_filters.RangeFilter()

    # Filtres par période prédéfinie
    periode_predefined = django_filters.ChoiceFilter(
        choices=[
            ('mois_courant', 'Mois courant'),
            ('mois_precedent', 'Mois précédent'),
            ('trimestre_courant', 'Trimestre courant'),
            ('annee_courante', 'Année courante'),
        ],
        method='filter_periode_predefined'
    )

    def filter_periode_predefined(self, queryset, name, value):
        """Filtrer par période prédéfinie"""
        today = date.today()

        if value == 'mois_courant':
            debut = today.replace(day=1)
            fin = (debut + relativedelta(months=1)) - relativedelta(days=1)
        elif value == 'mois_precedent':
            debut = (today - relativedelta(months=1)).replace(day=1)
            fin = today.replace(day=1) - relativedelta(days=1)
        elif value == 'trimestre_courant':
            trimestre = ((today.month - 1) // 3) + 1
            debut = today.replace(month=(trimestre - 1) * 3 + 1, day=1)
            fin = (debut + relativedelta(months=3)) - relativedelta(days=1)
        elif value == 'annee_courante':
            debut = today.replace(month=1, day=1)
            fin = today.replace(month=12, day=31)
        else:
            return queryset

        return queryset.filter(periode__gte=debut, periode__lte=fin)

    class Meta:
        model = Cotisation
        fields = ['statut', 'periode', 'date_echeance', 'montant', 'periode_predefined']


class PaiementFilter(django_filters.FilterSet):
    """Filtres pour les paiements"""

    methode = django_filters.ChoiceFilter(choices=Paiement._meta.get_field('methode').choices)
    date_paiement = django_filters.DateFromToRangeFilter()
    montant = django_filters.RangeFilter()
    recu_genere = django_filters.BooleanFilter()

    class Meta:
        model = Paiement
        fields = ['methode', 'date_paiement', 'montant', 'recu_genere']


class NotificationLogFilter(django_filters.FilterSet):
    """Filtres pour les logs de notifications"""

    type_notification = django_filters.ChoiceFilter(
        choices=NotificationLog._meta.get_field('type_notification').choices
    )
    statut = django_filters.ChoiceFilter(
        choices=NotificationLog._meta.get_field('statut').choices
    )
    date_envoi = django_filters.DateFromToRangeFilter()
    destinataire = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = NotificationLog
        fields = ['type_notification', 'statut', 'date_envoi', 'destinataire']
