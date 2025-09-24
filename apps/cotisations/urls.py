from django.urls import path
from . import views

app_name = 'cotisations'

urlpatterns = [
    path('', views.liste_cotisations, name='liste'),
    path('generer/', views.generer_cotisations, name='generer'),
    path('parametres/', views.parametres_cotisations, name='parametres'),
]
