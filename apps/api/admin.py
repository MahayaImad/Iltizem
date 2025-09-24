from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin as BaseTokenAdmin


# Personnaliser l'admin des tokens
class TokenAdmin(BaseTokenAdmin):
    """Interface d'administration personnalisée pour les tokens API"""

    list_display = ['key_preview', 'user', 'user_role', 'created', 'is_active']
    list_filter = ['created', 'user__role', 'user__is_active']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created']

    def key_preview(self, obj):
        """Afficher un aperçu de la clé (premiers et derniers caractères)"""
        if len(obj.key) >= 8:
            preview = f"{obj.key[:4]}...{obj.key[-4:]}"
            return format_html(
                '<code style="background: #f8f9fa; padding: 2px 4px; border-radius: 3px;">{}</code>',
                preview
            )
        return obj.key[:8] + '...'

    key_preview.short_description = 'Clé API'

    def user_role(self, obj):
        """Afficher le rôle de l'utilisateur"""
        role_colors = {
            'super_admin': 'danger',
            'admin_association': 'primary',
            'resident': 'secondary',
        }
        color = role_colors.get(obj.user.role, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.user.get_role_display()
        )

    user_role.short_description = 'Rôle'

    def is_active(self, obj):
        """Indiquer si l'utilisateur est actif"""
        if obj.user.is_active:
            return format_html('<span style="color: green;">✓ Actif</span>')
        return format_html('<span style="color: red;">✗ Inactif</span>')

    is_active.short_description = 'Statut'

    # Actions personnalisées
    actions = ['regenerer_tokens']

    def regenerer_tokens(self, request, queryset):
        """Régénérer les tokens sélectionnés"""
        count = 0
        for token in queryset:
            token.delete()
            Token.objects.create(user=token.user)
            count += 1

        self.message_user(request, f'{count} token(s) régénéré(s).')

    regenerer_tokens.short_description = "Régénérer les tokens sélectionnés"


# Désinscrire l'admin par défaut et réinscrire le nôtre
admin.site.unregister(Token)
admin.site.register(Token, TokenAdmin)
