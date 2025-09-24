from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Interface d'administration personnalisée pour les utilisateurs"""

    list_display = ['username', 'email', 'get_full_name', 'role', 'telephone', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telephone']
    ordering = ['-date_joined']

    # Grouper les champs dans l'interface d'édition
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Iltizam', {
            'fields': ('role', 'telephone'),
            'classes': ('wide',)
        }),
    )

    # Champs pour la création d'utilisateur
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations Iltizam', {
            'fields': ('email', 'first_name', 'last_name', 'role', 'telephone'),
            'classes': ('wide',)
        }),
    )

    def get_full_name(self, obj):
        """Afficher le nom complet"""
        return obj.get_full_name() or '-'

    get_full_name.short_description = 'Nom complet'

    # Actions personnalisées
    actions = ['activer_utilisateurs', 'desactiver_utilisateurs']

    def activer_utilisateurs(self, request, queryset):
        """Activer les utilisateurs sélectionnés"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} utilisateur(s) activé(s).')

    activer_utilisateurs.short_description = "Activer les utilisateurs sélectionnés"

    def desactiver_utilisateurs(self, request, queryset):
        """Désactiver les utilisateurs sélectionnés"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} utilisateur(s) désactivé(s).')

    desactiver_utilisateurs.short_description = "Désactiver les utilisateurs sélectionnés"
