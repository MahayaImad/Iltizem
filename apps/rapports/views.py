from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
from django.db.models import Count, Sum
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import os

from .models import RapportMensuel
from .forms import GenerationRapportForm, FiltresRapportsForm
from .utils import generer_rapport_pdf, generer_rapport_excel, generer_rapport_csv
from apps.associations.models import Association


@login_required
def liste_rapports(request):
    """Liste des rapports avec filtres"""
    if request.user.role not in ['super_admin', 'admin_association']:
        messages.error(request, "Accès non autorisé")
        return redirect('home')

    # Filtrer selon le rôle
    if request.user.role == 'admin_association':
        try:
            association = Association.objects.get(admin_principal=request.user)
            rapports = RapportMensuel.objects.filter(association=association)
        except Association.DoesNotExist:
            rapports = RapportMensuel.objects.none()
    else:
        rapports = RapportMensuel.objects.all()

    # Appliquer les filtres
    form = FiltresRapportsForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('type_rapport'):
            rapports = rapports.filter(type_rapport=form.cleaned_data['type_rapport'])
        if form.cleaned_data.get('statut'):
            rapports = rapports.filter(statut=form.cleaned_data['statut'])
        if form.cleaned_data.get('date_debut'):
            rapports = rapports.filter(periode__gte=form.cleaned_data['date_debut'])
        if form.cleaned_data.get('date_fin'):
            rapports = rapports.filter(periode__lte=form.cleaned_data['date_fin'])

    rapports = rapports.order_by('-date_generation')[:50]  # Limiter pour performance

    context = {
        'rapports': rapports,
        'form': form,
        'stats': {
            'total': rapports.count(),
            'generes': rapports.filter(statut='genere').count(),
            'en_cours': rapports.filter(statut='en_cours').count(),
            'erreurs': rapports.filter(statut='erreur').count(),
        }
    }

    return render(request, 'rapports/liste.html', context)


@login_required
def generer_rapport(request):
    """Générer un nouveau rapport"""
    if request.user.role not in ['super_admin', 'admin_association']:
        messages.error(request, "Accès non autorisé")
        return redirect('home')

    if request.method == 'POST':
        form = GenerationRapportForm(request.POST)
        if form.is_valid():
            # Déterminer l'association
            if request.user.role == 'admin_association':
                try:
                    association = Association.objects.get(admin_principal=request.user)
                except Association.DoesNotExist:
                    messages.error(request, "Association non trouvée")
                    return redirect('rapports:liste')
            else:
                # Pour super admin, prendre la première association (à améliorer)
                association = Association.objects.first()
                if not association:
                    messages.error(request, "Aucune association disponible")
                    return redirect('rapports:liste')

            # Vérifier si le rapport existe déjà
            periode = form.cleaned_data['periode']
            type_rapport = form.cleaned_data['type_rapport']

            rapport_existant = RapportMensuel.objects.filter(
                association=association,
                periode=periode,
                type_rapport=type_rapport
            ).first()

            if rapport_existant:
                messages.warning(request, "Ce rapport existe déjà. Téléchargement du rapport existant.")
                return redirect('rapports:telecharger', rapport_id=rapport_existant.id)

            # Créer le rapport
            rapport = RapportMensuel.objects.create(
                association=association,
                periode=periode,
                type_rapport=type_rapport,
                format_fichier=form.cleaned_data['format_fichier'],
                genere_par=request.user
            )

            # Générer le fichier selon le format
            try:
                options = {
                    'inclure_details': form.cleaned_data.get('inclure_details', False),
                    'inclure_graphiques': form.cleaned_data.get('inclure_graphiques', False),
                }

                if rapport.format_fichier == 'pdf':
                    fichier_path = generer_rapport_pdf(rapport, options)
                elif rapport.format_fichier == 'excel':
                    fichier_path = generer_rapport_excel(rapport, options)
                elif rapport.format_fichier == 'csv':
                    fichier_path = generer_rapport_csv(rapport, options)

                # Mettre à jour le rapport
                rapport.fichier = fichier_path
                rapport.statut = 'genere'

                # Calculer la taille du fichier
                if os.path.exists(fichier_path):
                    rapport.taille_fichier = os.path.getsize(fichier_path)

                rapport.save()

                messages.success(request, f"Rapport {type_rapport} généré avec succès")
                return redirect('rapports:telecharger', rapport_id=rapport.id)

            except Exception as e:
                rapport.statut = 'erreur'
                rapport.save()
                messages.error(request, f"Erreur lors de la génération: {str(e)}")
                return redirect('rapports:liste')

    else:
        form = GenerationRapportForm()

    context = {
        'form': form,
    }

    return render(request, 'rapports/generer.html', context)


@login_required
def telecharger_rapport(request, rapport_id):
    """Télécharger un rapport"""
    rapport = get_object_or_404(RapportMensuel, id=rapport_id)

    # Vérifier les permissions
    if request.user.role == 'admin_association':
        try:
            association = Association.objects.get(admin_principal=request.user)
            if rapport.association != association:
                raise Http404("Rapport non trouvé")
        except Association.DoesNotExist:
            raise Http404("Rapport non trouvé")

    # Vérifier que le fichier existe
    if not rapport.fichier or not os.path.exists(rapport.fichier.path):
        messages.error(request, "Fichier de rapport introuvable")
        return redirect('rapports:liste')

    # Préparer la réponse de téléchargement
    with open(rapport.fichier.path, 'rb') as fichier:
        response = HttpResponse(
            fichier.read(),
            content_type='application/octet-stream'
        )

        # Nom du fichier
        nom_fichier = f"rapport_{rapport.type_rapport}_{rapport.association.nom}_{rapport.periode.strftime('%Y-%m')}.{rapport.format_fichier}"
        nom_fichier = nom_fichier.replace(' ', '_').replace('/', '-')

        response['Content-Disposition'] = f'attachment; filename="{nom_fichier}"'

        return response


@login_required
def details_rapport(request, rapport_id):
    """Afficher les détails d'un rapport"""
    rapport = get_object_or_404(RapportMensuel, id=rapport_id)

    # Vérifier les permissions
    if request.user.role == 'admin_association':
        try:
            association = Association.objects.get(admin_principal=request.user)
            if rapport.association != association:
                raise Http404("Rapport non trouvé")
        except Association.DoesNotExist:
            raise Http404("Rapport non trouvé")

    context = {
        'rapport': rapport,
        'donnees': rapport.get_donnees(),
    }

    return render(request, 'rapports/details.html', context)


@login_required
def supprimer_rapport(request, rapport_id):
    """Supprimer un rapport"""
    rapport = get_object_or_404(RapportMensuel, id=rapport_id)

    # Vérifier les permissions
    if request.user.role == 'admin_association':
        try:
            association = Association.objects.get(admin_principal=request.user)
            if rapport.association != association:
                raise Http404("Rapport non trouvé")
        except Association.DoesNotExist:
            raise Http404("Rapport non trouvé")

    if request.method == 'POST':
        # Supprimer le fichier physique
        if rapport.fichier and os.path.exists(rapport.fichier.path):
            os.remove(rapport.fichier.path)

        rapport.delete()
        messages.success(request, "Rapport supprimé avec succès")
        return redirect('rapports:liste')

    context = {
        'rapport': rapport,
    }

    return render(request, 'rapports/supprimer.html', context)


@login_required
def statistiques_rapports(request):
    """Statistiques sur les rapports générés"""
    if request.user.role not in ['super_admin', 'admin_association']:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)

    # Filtrer selon le rôle
    if request.user.role == 'admin_association':
        try:
            association = Association.objects.get(admin_principal=request.user)
            rapports = RapportMensuel.objects.filter(association=association)
        except Association.DoesNotExist:
            rapports = RapportMensuel.objects.none()
    else:
        rapports = RapportMensuel.objects.all()

    # Statistiques générales
    stats = {
        'total_rapports': rapports.count(),
        'rapports_par_type': list(rapports.values('type_rapport').annotate(count=Count('id'))),
        'rapports_par_format': list(rapports.values('format_fichier').annotate(count=Count('id'))),
        'rapports_par_statut': list(rapports.values('statut').annotate(count=Count('id'))),
        'taille_totale': rapports.aggregate(total=Sum('taille_fichier'))['total'] or 0,
    }

    return JsonResponse(stats)