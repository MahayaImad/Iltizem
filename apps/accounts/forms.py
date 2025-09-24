from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import re

from .models import User


class LoginForm(forms.Form):
    """Formulaire de connexion simple et efficace"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class UserRegistrationForm(UserCreationForm):
    """Formulaire d'inscription utilisateur"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    telephone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+213XXXXXXXX'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'telephone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Appliquer les classes Bootstrap à tous les champs
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Validation simple du téléphone algérien
            pattern = r'^(\+213|0)[567]\d{8}$'
            if not re.match(pattern, telephone):
                raise ValidationError("Format de téléphone invalide. Utilisez +213XXXXXXXX ou 0XXXXXXXX")
        return telephone


class UserProfileForm(forms.ModelForm):
    """Formulaire de modification du profil utilisateur"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telephone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+213XXXXXXXX'}),
        }