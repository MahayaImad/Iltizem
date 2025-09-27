from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from datetime import date


def home_view(request):
    """Page d'accueil - Redirection selon l'authentification"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')  # ✅ CORRIGÉ: était 'dashboard'
    return redirect('accounts:login')


def login_view(request):
    """Connexion simple et efficace"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')  # ✅ CORRIGÉ: était 'dashboard'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Veuillez remplir tous les champs")
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Bienvenue {user.get_full_name() or user.username}!")

                # Redirection selon le rôle
                if user.role == 'super_admin':
                    return redirect('admin:index')
                elif user.role == 'admin_association':
                    return redirect('associations:tableau_bord_association')  # ✅ CORRIGÉ
                else:  # resident
                    return redirect('residents:tableau_bord')  # ✅ CORRIGÉ
            else:
                messages.error(request, "Votre compte est désactivé. Contactez l'administrateur.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Déconnexion"""
    if request.user.is_authenticated:
        messages.info(request, f"À bientôt {request.user.get_full_name() or request.user.username}!")
        logout(request)
    return redirect('accounts:login')


@login_required
def dashboard_redirect(request):
    """Redirection automatique vers le bon dashboard selon le rôle"""
    user = request.user

    if user.role == 'super_admin':
        return redirect('admin:index')
    elif user.role == 'admin_association':
        return redirect('associations:tableau_bord_association')  # ✅ CORRIGÉ
    elif user.role == 'resident':
        return redirect('residents:tableau_bord')  # ✅ CORRIGÉ
    else:
        messages.error(request, "Rôle non reconnu. Contactez l'administrateur.")
        return redirect('accounts:login')


@login_required
def profile_view(request):
    """Profil utilisateur simple"""
    if request.method == 'POST':
        # Mise à jour des infos de base
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()

        # Validation email simple
        if email and '@' not in email:
            messages.error(request, "Email invalide")
            return render(request, 'accounts/profile.html')

        # Mise à jour
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.telephone = telephone
        request.user.save()

        messages.success(request, "Profil mis à jour avec succès")
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html')


@login_required
def change_password_view(request):
    """Changement de mot de passe"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Vérifications
        if not current_password or not new_password or not confirm_password:
            messages.error(request, "Veuillez remplir tous les champs")
            return render(request, 'accounts/change_password.html')

        if new_password != confirm_password:
            messages.error(request, "Les nouveaux mots de passe ne correspondent pas")
            return render(request, 'accounts/change_password.html')

        if len(new_password) < 6:
            messages.error(request, "Le mot de passe doit contenir au moins 6 caractères")
            return render(request, 'accounts/change_password.html')

        # Vérifier l'ancien mot de passe
        if not request.user.check_password(current_password):
            messages.error(request, "Mot de passe actuel incorrect")
            return render(request, 'accounts/change_password.html')

        # Changer le mot de passe
        request.user.set_password(new_password)
        request.user.save()

        messages.success(request, "Mot de passe changé avec succès")
        return redirect('accounts:login')

    return render(request, 'accounts/change_password.html')


@login_required
def user_info_api(request):
    """API pour récupérer les informations utilisateur"""
    user = request.user
    return JsonResponse({
        'username': user.username,
        'full_name': user.get_full_name() or user.username,
        'email': user.email,
        'role': user.get_role_display(),
        'last_login': user.last_login.strftime('%d/%m/%Y à %H:%M') if user.last_login else 'Jamais',
        'date_joined': user.date_joined.strftime('%d/%m/%Y'),
    })


@login_required
def super_admin_dashboard(request):
    """Dashboard pour les super admins - Simple et efficace"""
    if request.user.role != 'super_admin':
        messages.error(request, "Accès refusé.")
        return redirect('accounts:login')

    # Statistiques de base pour le super admin
    from django.contrib.auth import get_user_model

    User = get_user_model()
    stats = {
        'total_users': User.objects.count(),
        'total_admins': User.objects.filter(role='admin_association').count(),
        'total_residents': User.objects.filter(role='resident').count(),
        'users_actifs': User.objects.filter(is_active=True).count(),
    }

    # Ajouter les stats des associations si le modèle existe
    try:
        from apps.associations.models import Association
        stats['total_associations'] = Association.objects.count()
        stats['associations_actives'] = Association.objects.filter(actif=True).count()
    except ImportError:
        pass

    context = {
        'stats': stats,
        'title': 'Dashboard Super Admin',
    }

    return render(request, 'accounts/super_admin_dashboard.html', context)