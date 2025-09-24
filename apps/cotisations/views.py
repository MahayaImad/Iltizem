from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from .models import Cotisation, TypeCotisation
from apps.associations.models import Association


@login_required
def liste_cotisations(request):
    """Liste des cotisations avec filtres"""
    if request.user.role == 'admin_association':
        association = get_object_or_404(Association, admin_principal=request.user)
        cotisations = Cotisation.objects.filter(
            logement__association=association
        ).select_related('logement', 'type_cotisation').order_by('-periode')
    else:
        cotisations = Cotisation.objects.none()

    # Filtres
    statut = request.GET.get('statut')
    logement = request.GET.get('logement')

    if statut:
        cotisations = cotisations.filter(statut=statut)
    if logement:
        cotisations = cotisations.filter(logement__numero=logement)

    context = {
        'cotisations': cotisations[:100],
        'association': association if request.user.role == 'admin_association' else None,
        'logements': association.logements.all() if request.user.role == 'admin_association' else [],
    }
    return render(request, 'cotisations/liste.html', context)


@login_required
def generer_cotisations(request):
    """Générer les cotisations pour la période suivante"""
    if request.user.role != 'admin_association':
        messages.error(request, "Accès non autorisé")
        return redirect('home')

    association = get_object_or_404(Association, admin_principal=request.user)

    if request.method == 'POST':
        periode = request.POST['periode']  # Format YYYY-MM-DD
        type_cotisation_id = request.POST['type_cotisation']

        type_cotisation = get_object_or_404(TypeCotisation,
                                            id=type_cotisation_id,
                                            association=association)

        # Calculer la date d'échéance selon la périodicité
        periode_date = date.fromisoformat(periode)

        if type_cotisation.periodicite == 'mensuelle':
            echeance = periode_date + relativedelta(months=1, day=10)
        elif type_cotisation.periodicite == 'trimestrielle':
            echeance = periode_date + relativedelta(months=3, day=10)
        else:  # annuelle
            echeance = periode_date + relativedelta(years=1, day=10)

        # Créer les cotisations pour tous les logements
        created_count = 0
        for logement in association.logements.all():
            cotisation, created = Cotisation.objects.get_or_create(
                logement=logement,
                type_cotisation=type_cotisation,
                periode=periode_date,
                defaults={
                    'montant': type_cotisation.montant,
                    'date_echeance': echeance,
                }
            )
            if created:
                created_count += 1

        messages.success(request, f"{created_count} cotisations générées pour {periode_date.strftime('%B %Y')}")
        return redirect('cotisations:liste')

    context = {
        'association': association,
        'types_cotisations': association.types_cotisations.filter(actif=True),
    }
    return render(request, 'cotisations/generer.html', context)
