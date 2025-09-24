from django.contrib import admin

# L'application residents n'a pas de models spécifiques
# L'administration des résidents se fait via l'application accounts

# Si on ajoute des models spécifiques aux résidents plus tard :
# from .models import ProfilResident

# @admin.register(ProfilResident)
# class ProfilResidentAdmin(admin.ModelAdmin):
#     list_display = ['user', 'date_emmenagement', 'preferences_notifications']
#     list_filter = ['preferences_notifications', 'date_emmenagement']
#     search_fields = ['user__username', 'user__first_name', 'user__last_name']

# Enregistrer une action personnalisée pour les utilisateurs résidents
# depuis l'admin des comptes si nécessaire
