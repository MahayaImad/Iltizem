from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from .models import TypeCotisation, Cotisation


@admin.register(TypeCotisation)
class TypeCotisationAdmin(admin.ModelAdmin):
    """Interface d'administration pour les types de cotisations"""

    list_display = ['nom', 'association', 'montant', 'periodicite', 'actif', 'get_cotisations_count']
    list_filter = ['periodicite', 'actif', 'association__plan']
    search_fields = ['nom', 'association__nom']
    ordering = ['association', 'nom']

    def get_cotisations_count(self, obj):
        """Afficher le nombre de cotisations générées"""
        count = obj.cotisations.count()
        return format_html(
            '<span>{} cotisations</span>',
            count
        )

    get_cotisations_count.short_description = 'Cotisations générées'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('association').annotate(
            cotisations_count=Count('cotisations')
        )


@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    """Interface d'administration pour les cotisations"""

    list_display = ['get_logement', 'get_resident', 'periode', 'montant', 'statut', 'date_echeance', 'est_en_retard']
    list_filter = ['statut', 'type_cotisation', 'periode', 'logement__association']
    search_fields = ['logement__numero', 'logement__resident__username', 'logement__association__nom']
    ordering = ['-periode', 'logement__association', 'logement__numero']
    date_hierarchy = 'periode'

    def get_logement(self, obj):
        return f"{obj.logement.association.nom} - {obj.logement.numero}"

    get_logement.short_description = 'Logement'

    def get_resident(self, obj):
        if obj.logement.resident:
            return obj.logement.resident.get_full_name() or obj.logement.resident.username
        return '-'

    get_resident.short_description = 'Résident'

    def est_en_retard(self, obj):
        if obj.statut == 'retard':
            return format_html('<span style="color: red;">✗ En retard</span>')
        elif obj.statut == 'payee':
            return format_html('<span style="color: green;">✓ Payée</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Due</span>')

    est_en_retard.short_description = 'État'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'logement__association',
            'logement__resident',
            'type_cotisation'
        )