from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Paiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    """Interface d'administration pour les paiements"""

    list_display = ['get_cotisation_info', 'montant', 'methode', 'date_paiement', 'enregistre_par', 'recu_genere',
                    'actions_links']
    list_filter = ['methode', 'date_paiement', 'recu_genere', 'cotisation__logement__association']
    search_fields = ['cotisation__logement__numero', 'cotisation__logement__resident__username', 'reference']
    ordering = ['-date_enregistrement']
    date_hierarchy = 'date_paiement'

    # Champs en lecture seule
    readonly_fields = ['date_enregistrement', 'enregistre_par']

    def get_cotisation_info(self, obj):
        """Afficher les infos de la cotisation"""
        cotisation = obj.cotisation
        return format_html(
            '<strong>{}</strong><br/><small>{} - {}</small>',
            cotisation.logement,
            cotisation.periode.strftime('%m/%Y'),
            cotisation.get_statut_display()
        )

    get_cotisation_info.short_description = 'Cotisation'

    def actions_links(self, obj):
        """Liens d'actions rapides"""
        links = []

        if obj.recu_genere:
            # Lien pour télécharger le reçu
            links.append(
                f'<a href="#" class="button">📄 Reçu</a>'
            )
        else:
            # Lien pour générer le reçu
            links.append(
                f'<a href="#" class="button">📄 Générer reçu</a>'
            )

        return mark_safe(' '.join(links))

    actions_links.short_description = 'Actions'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cotisation__logement__association',
            'cotisation__logement__resident',
            'enregistre_par'
        )

    def save_model(self, request, obj, form, change):
        """Enregistrer l'utilisateur qui effectue l'action"""
        if not change:  # Création
            obj.enregistre_par = request.user
        super().save_model(request, obj, form, change)