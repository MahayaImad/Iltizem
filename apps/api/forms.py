"""
L'application API utilise principalement les serializers DRF.
Les forms sont utilisés uniquement pour l'interface d'administration
ou des cas spécifiques.
"""

from django import forms
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class APITokenForm(forms.Form):
    """Formulaire pour générer un token API pour un utilisateur"""

    utilisateur = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Utilisateur'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les utilisateurs selon leur rôle
        self.fields['utilisateur'].queryset = User.objects.filter(
            is_active=True,
            role__in=['super_admin', 'admin_association']
        )

    def save(self):
        """Créer ou récupérer le token pour l'utilisateur"""
        utilisateur = self.cleaned_data['utilisateur']
        token, created = Token.objects.get_or_create(user=utilisateur)
        return token, created


class APISettingsForm(forms.Form):
    """Formulaire de configuration des paramètres API"""

    rate_limit_enabled = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Activer la limitation de débit'
    )

    requests_per_minute = forms.IntegerField(
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Requêtes par minute',
        initial=60
    )

    api_version = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Version API',
        initial='v1'
    )

    maintenance_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Mode maintenance'
    )
