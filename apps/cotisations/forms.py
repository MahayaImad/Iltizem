from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from .models import TypeCotisation, Cotisation


class TypeCotisationForm(forms.ModelForm):
    """Formulaire de configuration des types de cotisations"""

    class Meta:
        model = TypeCotisation
        fields = ['nom', 'montant', 'periodicite', 'actif']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Cotisation mensuelle, Charges trimestrielles'
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'periodicite': forms.Select(attrs={
                'class': 'form-select'
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant and montant <= 0:
            raise ValidationError("Le montant doit être supérieur à 0.")
        return montant


class GenerationCotisationsForm(forms.Form):
    """Formulaire pour générer les cotisations"""

    type_cotisation = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Type de cotisation'
    )

    periode = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Période (début)',
        help_text='Sélectionnez le mois/trimestre/année de la cotisation'
    )

    def __init__(self, *args, **kwargs):
        association = kwargs.pop('association', None)
        super().__init__(*args, **kwargs)

        if association:
            self.fields['type_cotisation'].queryset = association.types_cotisations.filter(actif=True)

        # Date par défaut : premier jour du mois prochain
        self.fields['periode'].initial = (date.today() + relativedelta(months=1)).replace(day=1)

    def clean_periode(self):
        periode = self.cleaned_data.get('periode')

        # La période ne peut pas être dans le passé (sauf mois en cours)
        if periode and periode < date.today().replace(day=1):
            raise ValidationError("La période ne peut pas être antérieure au mois en cours.")

        return periode


class FiltresCotisationsForm(forms.Form):
    """Formulaire de filtres pour la liste des cotisations"""

    STATUT_CHOICES = [
        ('', 'Tous les statuts'),
        ('due', 'Due'),
        ('payee', 'Payée'),
        ('retard', 'En retard'),
    ]

    statut = forms.ChoiceField(
        choices=STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    logement = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numéro de logement'
        })
    )

    periode_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Période depuis'
    )

    periode_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Période jusqu\'à'
    )