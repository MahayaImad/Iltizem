from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import RapportMensuel


@admin.register(RapportMensuel)
class RapportMensuelAdmin(admin.ModelAdmin):
    """Interface d'administration pour les rapports"""

    list_display = ['__str__', 'association', 'statut', 'format_fichier', 'get_taille_lisible', 'date_generation',
                    'actions_links']
    list_filter = ['type_rapport', 'statut', 'format_fichier', 'date_generation', 'association']
    search_fields = ['association__nom', 'genere_par__username']
    ordering = ['-date_generation']
    date_hierarchy = 'date_generation'

    # Champs en lecture seule
    readonly_fields = ['date_generation', 'taille_fichier']

    # Grouper les champs
    fieldsets = (
        ('Informations générales', {
            'fields': ('association', 'periode', 'type_rapport', 'format_fichier')
        }),
        ('Fichier et données', {
            'fields': ('fichier', 'donnees_json', 'taille_fichier')
        }),
        ('Métadonnées', {
            'fields': ('statut', 'genere_par', 'date_generation'),
            'classes': ('collapse',)
        }),
    )

    def actions_links(self, obj):
        """Liens d'actions rapides"""
        links = []

        if obj.statut == 'genere' and obj.fichier:
            # Lien de téléchargement
            links.append(
                f'<a href="{obj.fichier.url}" class="button" target="_blank">📥 Télécharger</a>'
            )

        if obj.statut == 'erreur':
            # Lien pour régénérer
            links.append(
                f'<a href="#" class="button">🔄 Régénérer</a>'
            )

        # Lien pour voir les détails
        links.append(
            f'<a href="#" class="button">👁️ Détails</a>'
        )

        return mark_safe(' '.join(links))

    actions_links.short_description = 'Actions'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('association', 'genere_par')
