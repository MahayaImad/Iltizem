from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),

    # Profil utilisateur
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),

    # API
    path('api/user-info/', views.user_info_api, name='user_info_api'),
]