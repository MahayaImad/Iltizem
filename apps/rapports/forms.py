from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from .models import RapportMensuel


class GenerationRapportForm(forms.Form):
    """Formulaire de génération de rapport"""

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

    type_rapport = forms.ChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Type de rapport'
    )

    periode = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Période',
        help_text='Sélectionnez le mois/trimestre/année du rapport'
    )

    format_fichier = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Format de fichier'
    )

    inclure_details = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Inclure les détails par logement'
    )

    inclure_graphiques = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Inclure les graphiques (PDF uniquement)'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Date par défaut : mois précédent
        self.fields['periode'].initial = (date.today() - relativedelta(months=1)).replace(day=1)

    def clean_periode(self):
        periode = self.cleaned_data.get('periode')

        # Ne pas générer de rapport pour le futur
        if periode and periode > date.today():
            raise ValidationError("La période ne peut pas être dans le futur.")

        return periode


class FiltresRapportsForm(forms.Form):
    """Formulaire de filtres pour la liste des rapports"""

    TYPE_CHOICES = [
        ('', 'Tous les types'),
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('annuel', 'Annuel'),
        ('personnalise', 'Personnalisé'),
    ]

    STATUT_CHOICES = [
        ('', 'Tous les statuts'),
        ('genere', 'Généré'),
        ('en_cours', 'En cours'),
        ('erreur', 'Erreur'),
    ]

    type_rapport = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    statut = forms.ChoiceField(
        choices=STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Période depuis'
    )

    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Période jusqu\'à'
    )