from django import forms
from django.core.exceptions import ValidationError
from .models import NotificationTemplate, NotificationLog


class NotificationTemplateForm(forms.ModelForm):
    """Formulaire de création/modification de templates"""

    class Meta:
        model = NotificationTemplate
        fields = ['nom', 'type_notification', 'sujet', 'contenu', 'actif']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Rappel Retard, Confirmation Paiement'
            }),
            'type_notification': forms.Select(attrs={'class': 'form-select'}),
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet du message'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Contenu du message...\nUtilisez {{variable}} pour les données dynamiques'
            }),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_contenu(self):
        """Valider le template Django"""
        contenu = self.cleaned_data.get('contenu')
        if contenu:
            try:
                from django.template import Template
                Template(contenu)
            except Exception as e:
                raise ValidationError(f"Erreur dans le template: {e}")
        return contenu


class EnvoiNotificationForm(forms.Form):
    """Formulaire d'envoi de notification ponctuelle"""

    template = forms.ModelChoiceField(
        queryset=NotificationTemplate.objects.filter(actif=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Template'
    )

    destinataires = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Emails séparés par des virgules ou sélection par critères'
        }),
        label='Destinataires',
        help_text='Entrez les emails séparés par des virgules'
    )

    CRITERE_CHOICES = [
        ('tous', 'Tous les résidents'),
        ('retard', 'Résidents en retard'),
        ('association', 'Résidents d\'une association'),
        ('manuel', 'Liste manuelle'),
    ]

    critere = forms.ChoiceField(
        choices=CRITERE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Critère de sélection'
    )

    association = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Association (si applicable)'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.role == 'admin_association':
            from apps.associations.models import Association
            try:
                association = Association.objects.get(admin_principal=user)
                self.fields['association'].queryset = Association.objects.filter(id=association.id)
                self.fields['association'].initial = association
            except Association.DoesNotExist:
                self.fields['association'].queryset = Association.objects.none()
        else:
            from apps.associations.models import Association
            self.fields['association'].queryset = Association.objects.filter(actif=True)


class FiltresNotificationLogForm(forms.Form):
    """Formulaire de filtres pour les logs de notifications"""

    TYPE_CHOICES = [
        ('', 'Tous les types'),
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]

    STATUT_CHOICES = [
        ('', 'Tous les statuts'),
        ('envoye', 'Envoyé'),
        ('erreur', 'Erreur'),
        ('en_attente', 'En attente'),
    ]

    type_notification = forms.ChoiceField(
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
        })
    )

    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )