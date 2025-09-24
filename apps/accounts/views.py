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
        return redirect('dashboard')
    return redirect('accounts:login')


def login_view(request):
    """Connexion simple et efficace"""
    if request.user.is_authenticated:
        return redirect('dashboard')

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
                    return redirect('associations:tableau_bord')
                else:  # resident
                    return redirect('residents:tableau_bord')
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
        return redirect('associations:tableau_bord')
    elif user.role == 'resident':
        return redirect('residents:tableau_bord')
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
        if not request.user.check_password(current_password):
            messages.error(request, "Mot de passe actuel incorrect")
            return render(request, 'accounts/change_password.html')

        if len(new_password) < 8:
            messages.error(request, "Le nouveau mot de passe doit contenir au moins 8 caractères")
            return render(request, 'accounts/change_password.html')

        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return render(request, 'accounts/change_password.html')

        # Mise à jour
        request.user.set_password(new_password)
        request.user.save()

        # Reconnecter l'utilisateur
        user = authenticate(username=request.user.username, password=new_password)
        login(request, user)

        messages.success(request, "Mot de passe mis à jour avec succès")
        return redirect('accounts:profile')

    return render(request, 'accounts/change_password.html')


@login_required
def user_info_api(request):
    """API pour informations utilisateur (pour JS)"""
    if request.method == 'GET':
        user = request.user
        data = {
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'date_joined': user.date_joined.strftime('%d/%m/%Y'),
            'last_login': user.last_login.strftime('%d/%m/%Y à %H:%M') if user.last_login else None
        }

        # Informations spécifiques selon le rôle
        if user.role == 'resident':
            try:
                from apps.associations.models import Logement
                logement = Logement.objects.get(resident=user)
                data['logement'] = {
                    'numero': logement.numero,
                    'association': logement.association.nom,
                    'type': logement.type
                }
            except Logement.DoesNotExist:
                data['logement'] = None

        elif user.role == 'admin_association':
            try:
                from apps.associations.models import Association
                association = Association.objects.get(admin_principal=user)
                data['association'] = {
                    'nom': association.nom,
                    'adresse': association.adresse,
                    'total_logements': association.logements.count()
                }
            except Association.DoesNotExist:
                data['association'] = None

        return JsonResponse(data)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)