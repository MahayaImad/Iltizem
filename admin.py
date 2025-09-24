from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Association, Logement, TypeCotisation, Cotisation, Paiement

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'date_creation']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Iltizam', {'fields': ('role', 'telephone')}),
    )

@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = ['nom', 'plan', 'nombre_logements', 'admin_principal', 'actif']
    list_filter = ['plan', 'actif']
    search_fields = ['nom', 'adresse']

@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ['logement', 'periode', 'montant', 'statut', 'date_echeance']
    list_filter = ['statut', 'type_cotisation', 'periode']
    search_fields = ['logement__numero', 'logement__association__nom']
