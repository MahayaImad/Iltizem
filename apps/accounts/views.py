from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse


def login_view(request):
    """Connexion simple et efficace"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
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
            messages.error(request, "Identifiants incorrects")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté")
    return redirect('home')


@login_required
def profile_view(request):
    """Profil utilisateur simple"""
    if request.method == 'POST':
        # Mise à jour des infos de base
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.telephone = request.POST.get('telephone', '')
        request.user.save()

        messages.success(request, "Profil mis à jour")

    return render(request, 'accounts/profile.html')
