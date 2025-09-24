from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import NotificationTemplate, NotificationLog


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Interface d'administration pour les templates de notifications"""

    list_display = ['nom', 'type_notification', 'actif', 'get_usage_count', 'date_creation']
    list_filter = ['type_notification', 'actif', 'date_creation']
    search_fields = ['nom', 'sujet', 'contenu']
    ordering = ['nom']

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'type_notification', 'actif')
        }),
        ('Contenu', {
            'fields': ('sujet', 'contenu'),
            'description': 'Utilisez {{variable}} pour les variables dynamiques comme {{resident.first_name}}, {{cotisation.montant}}, etc.'
        }),
    )

    def get_usage_count(self, obj):
        """Afficher le nombre d'utilisations du template"""
        count = obj.notificationlog_set.count()
        if count > 0:
            url = reverse('admin:notifications_notificationlog_changelist') + f'?template__id={obj.id}'
            return format_html('<a href="{}">{} utilisations</a>', url, count)
        return '0 utilisation'

    get_usage_count.short_description = 'Utilisations'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Interface d'administration pour les logs de notifications"""

    list_display = ['destinataire', 'type_notification', 'sujet', 'statut', 'date_envoi', 'template', 'get_association']
    list_filter = ['type_notification', 'statut', 'date_envoi', 'template']
    search_fields = ['destinataire', 'sujet', 'contenu']
    ordering = ['-date_envoi']
    date_hierarchy = 'date_envoi'

    # Champs en lecture seule
    readonly_fields = ['date_envoi']

    def get_association(self, obj):
        """Afficher l'association"""
        if obj.association:
            return obj.association.nom
        return '-'

    get_association.short_description = 'Association'

    # Actions personnalisées
    actions = ['marquer_comme_envoye', 'retry_erreurs']

    def marquer_comme_envoye(self, request, queryset):
        """Marquer comme envoyé"""
        updated = queryset.update(statut='envoye')
        self.message_user(request, f'{updated} notification(s) marquée(s) comme envoyée(s).')

    marquer_comme_envoye.short_description = "Marquer comme envoyé"

    def retry_erreurs(self, request, queryset):
        """Réessayer les notifications en erreur"""
        erreurs = queryset.filter(statut='erreur')
        updated = erreurs.update(statut='en_attente')
        self.message_user(request, f'{updated} notification(s) remise(s) en attente.')

    retry_erreurs.short_description = "Réessayer les erreurs"