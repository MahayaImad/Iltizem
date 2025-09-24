from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.liste_notifications, name='liste'),
    path('templates/', views.gestion_templates, name='templates'),
    path('templates/nouveau/', views.creer_template, name='nouveau_template'),
    path('templates/<int:template_id>/modifier/', views.modifier_template, name='modifier_template'),
    path('envoyer/', views.envoyer_notification, name='envoyer'),
    path('logs/', views.logs_notifications, name='logs'),
    path('rappels/', views.envoyer_rappels, name='rappels'),
    path('test-email/', views.test_email, name='test_email'),
]