from django.urls import path
from . import views

app_name = 'paiements'

urlpatterns = [
    path('', views.liste_paiements, name='liste'),
    path('enregistrer/<int:cotisation_id>/', views.enregistrer_paiement, name='enregistrer'),
    path('recu/<int:paiement_id>/', views.generer_recu, name='recu'),
]
