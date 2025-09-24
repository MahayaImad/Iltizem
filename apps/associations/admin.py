from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Association, Logement


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    """Interface d'administration pour les associations"""

    list_display = ['nom', 'plan', 'nombre_logements', 'get_logements_count', 'admin_principal', 'actif',
                    'date_creation']
    list_filter = ['plan', 'actif', 'date_creation']
    search_fields = ['nom', 'adresse', 'admin_principal__username']
    ordering = ['-date_creation']

    # Champs en lecture seule
    readonly_fields = ['date_creation']

    # Grouper les champs
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'adresse', 'nombre_logements')
        }),
        ('Configuration', {
            'fields': ('plan', 'admin_principal', 'actif')
        }),
        ('Métadonnées', {
            'fields': ('date_creation',),
            'classes': ('collapse',)
        }),
    )

    def get_logements_count(self, obj):
        """Afficher le nombre de logements créés"""
        count = obj.logements.count()
        total = obj.nombre_logements
        if count == total:
            color = 'green'
        elif count > total * 0.8:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{}/{}</span>',
            color, count, total
        )

    get_logements_count.short_description = 'Logements créés'

    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request).select_related('admin_principal').annotate(
            logements_count=Count('logements')
        )


@admin.register(Logement)
class LogementAdmin(admin.ModelAdmin):
    """Interface d'administration pour les logements"""

    list_display = ['numero', 'association', 'resident', 'superficie', 'est_occupe']
    list_filter = ['association', 'association__plan']
    search_fields = ['numero', 'association__nom', 'resident__username', 'resident__first_name', 'resident__last_name']
    ordering = ['association', 'numero']

    # Filtres personnalisés
    def est_occupe(self, obj):
        """Indiquer si le logement est occupé"""
        if obj.resident:
            return format_html('<span style="color: green;">✓ Occupé</span>')
        return format_html('<span style="color: red;">✗ Libre</span>')

    est_occupe.short_description = 'Statut'

    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request).select_related('association', 'resident')
