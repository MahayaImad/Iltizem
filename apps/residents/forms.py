from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date

from apps.cotisations.models import Cotisation
from apps.paiements.models import Paiement

User = get_user_model()


class ProfilResidentForm(forms.ModelForm):
    """Formulaire de modification du profil résident"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telephone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+213XXXXXXXX'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Vérifier que l'email n'est pas déjà utilisé par un autre utilisateur
            existing_user = User.objects.filter(email=email).exclude(id=self.instance.id).first()
            if existing_user:
                raise ValidationError("Cette adresse email est déjà utilisée.")
        return email


class FiltresCotisationsResidentForm(forms.Form):
    """Formulaire de filtres pour les cotisations du résident"""

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

    annee = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 2020,
            'max': date.today().year + 1,
            'placeholder': 'Année'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Année par défaut : année en cours
        self.fields['annee'].initial = date.today().year


class DemandeContactForm(forms.Form):
    """Formulaire de contact avec l'administration"""

    SUJET_CHOICES = [
        ('question_cotisation', 'Question sur cotisation'),
        ('probleme_paiement', 'Problème de paiement'),
        ('demande_recu', 'Demande de reçu'),
        ('reclamation', 'Réclamation'),
        ('suggestion', 'Suggestion'),
        ('autre', 'Autre'),
    ]

    sujet = forms.ChoiceField(
        choices=SUJET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Sujet'
    )

    titre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Titre de votre demande'
        }),
        label='Titre'
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Décrivez votre demande...'
        }),
        label='Message'
    )

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if message and len(message) < 10:
            raise ValidationError("Le message doit contenir au moins 10 caractères.")
        return message


class ChangePasswordForm(forms.Form):
    """Formulaire de changement de mot de passe pour résident"""

    ancien_mot_de_passe = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ancien mot de passe'
        }),
        label='Ancien mot de passe'
    )

    nouveau_mot_de_passe = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe'
        }),
        label='Nouveau mot de passe',
        help_text='Au moins 8 caractères'
    )

    confirmation_mot_de_passe = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le nouveau mot de passe'
        }),
        label='Confirmation'
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_ancien_mot_de_passe(self):
        ancien_mot_de_passe = self.cleaned_data.get('ancien_mot_de_passe')
        if ancien_mot_de_passe and self.user:
            if not self.user.check_password(ancien_mot_de_passe):
                raise ValidationError("L'ancien mot de passe est incorrect.")
        return ancien_mot_de_passe

    def clean_confirmation_mot_de_passe(self):
        nouveau_mot_de_passe = self.cleaned_data.get('nouveau_mot_de_passe')
        confirmation = self.cleaned_data.get('confirmation_mot_de_passe')

        if nouveau_mot_de_passe and confirmation:
            if nouveau_mot_de_passe != confirmation:
                raise ValidationError("Les mots de passe ne correspondent pas.")

        return confirmation