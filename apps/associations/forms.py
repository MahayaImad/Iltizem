from django import forms
from django.core.exceptions import ValidationError
from .models import Association, Logement


class AssociationForm(forms.ModelForm):
    """Formulaire de création/modification d'association"""

    class Meta:
        model = Association
        fields = ['nom', 'adresse', 'nombre_logements', 'plan']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'association'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse complète de la résidence'
            }),
            'nombre_logements': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 1000
            }),
            'plan': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def clean_nombre_logements(self):
        nombre = self.cleaned_data.get('nombre_logements')
        if nombre and nombre < 1:
            raise ValidationError("Le nombre de logements doit être supérieur à 0.")
        if nombre and nombre > 1000:
            raise ValidationError("Le nombre de logements ne peut pas dépasser 1000.")
        return nombre


class LogementForm(forms.ModelForm):
    """Formulaire de gestion des logements"""

    class Meta:
        model = Logement
        fields = ['numero', 'resident', 'superficie']
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: A101, B205, Villa 15'
            }),
            'resident': forms.Select(attrs={
                'class': 'form-select'
            }),
            'superficie': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Superficie en m²'
            }),
        }

    def __init__(self, *args, **kwargs):
        association = kwargs.pop('association', None)
        super().__init__(*args, **kwargs)

        if association:
            # Filtrer les résidents disponibles (sans logement ou avec ce logement)
            from apps.accounts.models import User
            residents_disponibles = User.objects.filter(
                role='resident'
            ).exclude(
                logement__isnull=False
            )

            # Ajouter le résident actuel s'il existe
            if self.instance.resident:
                residents_disponibles = residents_disponibles | User.objects.filter(
                    id=self.instance.resident.id
                )

            self.fields['resident'].queryset = residents_disponibles
            self.fields['resident'].empty_label = "Sélectionner un résident"


class LogementBulkForm(forms.Form):
    """Formulaire pour créer plusieurs logements en une fois"""

    PATTERN_CHOICES = [
        ('numeric', 'Numérique (1, 2, 3...)'),
        ('alpha_numeric', 'Alpha-numérique (A1, A2, A3...)'),
        ('floor_apt', 'Étage-Appartement (101, 102, 201, 202...)'),
    ]

    pattern = forms.ChoiceField(
        choices=PATTERN_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Type de numérotation'
    )

    debut = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 1, A1, 101'
        }),
        label='Numéro de début'
    )

    fin = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 50, A50, 505'
        }),
        label='Numéro de fin'
    )

    prefixe = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Apt, Villa'
        }),
        label='Préfixe (optionnel)'
    )