from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'associations', views.AssociationViewSet)
router.register(r'cotisations', views.CotisationViewSet)
router.register(r'paiements', views.PaiementViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', views.StatsView.as_view(), name='stats'),
]
