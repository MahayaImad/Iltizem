from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Association, TypeCotisation
from .validators import valider_telephone_algerie


class UserRegistrationForm(UserCreationForm):
    """Formulaire d'inscription utilisateur"""
    email = forms.EmailField(required=True)
    telephone = forms.CharField(
        max_length=15,
        required=False,
        validators=[valider_telephone_algerie]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'telephone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter les classes Bootstrap
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class AssociationForm(forms.ModelForm):
    """Formulaire de création d'association"""

    class Meta:
        model = Association
        fields = ['nom', 'adresse', 'nombre_logements', 'plan']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nombre_logements': forms.NumberInput(attrs={'class': 'form-control'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
        }


class TypeCotisationForm(forms.ModelForm):
    """Formulaire de configuration des cotisations"""

    class Meta:
        model = TypeCotisation
        fields = ['nom', 'montant', 'periodicite']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'periodicite': forms.Select(attrs={'class': 'form-select'}),
        }