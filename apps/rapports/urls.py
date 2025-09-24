from django.urls import path
from . import views

app_name = 'rapports'

urlpatterns = [
    path('', views.liste_rapports, name='liste'),
    path('generer/', views.generer_rapport, name='generer'),
    path('telecharger/<int:rapport_id>/', views.telecharger_rapport, name='telecharger'),
    path('details/<int:rapport_id>/', views.details_rapport, name='details'),
    path('supprimer/<int:rapport_id>/', views.supprimer_rapport, name='supprimer'),
    path('statistiques/', views.statistiques_rapports, name='statistiques'),
]