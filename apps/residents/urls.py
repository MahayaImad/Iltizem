from django.urls import path
from . import views

app_name = 'residents'

urlpatterns = [
    # Tableau de bord
    path('', views.tableau_bord_resident, name='tableau_bord'),

    # Cotisations
    path('cotisations/', views.mes_cotisations, name='cotisations'),
    path('cotisations/details/<int:cotisation_id>/', views.details_cotisation, name='details_cotisation'),

    # Paiements et reçus
    path('paiements/', views.mes_paiements, name='paiements'),
    path('reçus/', views.mes_reçus, name='reçus'),
    path('reçu/<int:paiement_id>/telecharger/', views.telecharger_reçu, name='telecharger_reçu'),

    # Profil
    path('profil/', views.modifier_profil, name='profil'),
    path('changer-mot-de-passe/', views.changer_mot_de_passe, name='changer_mot_de_passe'),

    # Contact
    path('contact/', views.contacter_administration, name='contact'),

    # API pour le dashboard
    path('api/statistiques/', views.statistiques_resident_api, name='api_statistiques'),
]
