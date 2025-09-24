from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Association, Logement


@login_required
def tableau_bord_association(request):
    """Tableau de bord admin association - Simple et efficace"""
    if request.user.role != 'admin_association':
        messages.error(request, "Accès non autorisé")
        return redirect('login')

    association = get_object_or_404(Association, admin_principal=request.user)

    # Statistiques simples
    total_logements = association.logements.count()
    logements_occupes = association.logements.filter(resident__isnull=False).count()

    # Cotisations du mois en cours
    from datetime import date
    mois_actuel = date.today().replace(day=1)
    cotisations_mois = Cotisation.objects.filter(
        logement__association=association,
        periode=mois_actuel
    )

    total_attendu = sum(c.montant for c in cotisations_mois)
    total_paye = sum(c.montant for c in cotisations_mois if c.statut == 'payee')

    context = {
        'association': association,
        'total_logements': total_logements,
        'logements_occupes': logements_occupes,
        'taux_occupation': round((logements_occupes / total_logements * 100), 1) if total_logements > 0 else 0,
        'total_attendu': total_attendu,
        'total_paye': total_paye,
        'taux_recouvrement': round((total_paye / total_attendu * 100), 1) if total_attendu > 0 else 0,
        'cotisations_impayees': cotisations_mois.filter(statut__in=['due', 'retard']),
    }

    return render(request, 'associations/tableau_bord.html', context)
