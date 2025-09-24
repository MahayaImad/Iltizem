from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Paiement


class PaiementForm(forms.ModelForm):
    """Formulaire d'enregistrement de paiement"""

    class Meta:
        model = Paiement
        fields = ['montant', 'methode', 'reference', 'date_paiement']
        widgets = {
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'methode': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'N° chèque, référence virement...'
            }),
            'date_paiement': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        cotisation = kwargs.pop('cotisation', None)
        super().__init__(*args, **kwargs)

        if cotisation:
            self.fields['montant'].initial = cotisation.montant

        # Date par défaut : aujourd'hui
        self.fields['date_paiement'].initial = date.today()

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant and montant <= 0:
            raise ValidationError("Le montant doit être supérieur à 0.")
        return montant

    def clean_date_paiement(self):
        date_paiement = self.cleaned_data.get('date_paiement')
        if date_paiement and date_paiement > date.today():
            raise ValidationError("La date de paiement ne peut pas être dans le futur.")
        return date_paiement


class FiltresPaiementsForm(forms.Form):
    """Formulaire de filtres pour la liste des paiements"""

    METHODE_CHOICES = [
        ('', 'Toutes les méthodes'),
        ('especes', 'Espèces'),
        ('virement', 'Virement'),
        ('cheque', 'Chèque'),
        ('en_ligne', 'Paiement en ligne'),
    ]

    methode = forms.ChoiceField(
        choices=METHODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Depuis le'
    )

    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Jusqu\'au'
    )

    logement = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numéro de logement'
        })
    )