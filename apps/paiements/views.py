from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import date

from .models import Paiement
from cotisations.models import Cotisation
from associations.models import Association


@login_required
def enregistrer_paiement(request, cotisation_id):
    """Enregistrer un paiement - Simple et efficace"""
    cotisation = get_object_or_404(Cotisation, id=cotisation_id)

    # Vérifier que l'admin peut gérer cette cotisation
    if request.user.role == 'admin_association':
        association = get_object_or_404(Association, admin_principal=request.user)
        if cotisation.logement.association != association:
            messages.error(request, "Accès non autorisé")
            return redirect('associations:tableau_bord')

    if request.method == 'POST':
        # Validation simple
        montant = float(request.POST['montant'])
        methode = request.POST['methode']
        date_paiement = request.POST['date_paiement']
        reference = request.POST.get('reference', '')

        # Créer le paiement
        paiement = Paiement.objects.create(
            cotisation=cotisation,
            montant=montant,
            methode=methode,
            reference=reference,
            date_paiement=date_paiement,
            enregistre_par=request.user
        )

        # Mettre à jour le statut de la cotisation
        cotisation.statut = 'payee'
        cotisation.save()

        messages.success(request, f"Paiement enregistré pour {cotisation.logement.numero}")
        return redirect('associations:tableau_bord')

    context = {
        'cotisation': cotisation,
        'association': cotisation.logement.association,
    }
    return render(request, 'paiements/enregistrer.html', context)


@login_required
def generer_recu(request, paiement_id):
    """Générer un reçu PDF simple"""
    paiement = get_object_or_404(Paiement, id=paiement_id)

    # Créer le PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # En-tête
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 80, "REÇU DE PAIEMENT")

    # Informations association
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 120, f"Association: {paiement.cotisation.logement.association.nom}")
    p.drawString(50, height - 140, f"Adresse: {paiement.cotisation.logement.association.adresse}")

    # Informations paiement
    y = height - 200
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "DÉTAILS DU PAIEMENT")

    y -= 30
    p.setFont("Helvetica", 11)
    infos = [
        f"Logement: {paiement.cotisation.logement.numero}",
        f"Période: {paiement.cotisation.periode.strftime('%B %Y')}",
        f"Montant: {paiement.montant} DA",
        f"Méthode: {paiement.get_methode_display()}",
        f"Date de paiement: {paiement.date_paiement.strftime('%d/%m/%Y')}",
        f"Référence: {paiement.reference or 'N/A'}",
    ]

    for info in infos:
        p.drawString(50, y, info)
        y -= 20

    # Signature
    y -= 40
    p.drawString(50, y, f"Reçu généré le {date.today().strftime('%d/%m/%Y')}")
    p.drawString(50, y - 20, f"Par: {paiement.enregistre_par.get_full_name() or paiement.enregistre_par.username}")

    p.showPage()
    p.save()

    # Marquer le reçu comme généré
    paiement.recu_genere = True
    paiement.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_{paiement.id}.pdf"'

    return response


@login_required
def liste_paiements(request):
    """Liste des paiements avec filtres simples"""
    if request.user.role == 'admin_association':
        association = get_object_or_404(Association, admin_principal=request.user)
        paiements = Paiement.objects.filter(
            cotisation__logement__association=association
        ).order_by('-date_enregistrement')
    else:
        paiements = Paiement.objects.none()

    # Filtres simples
    statut = request.GET.get('statut')
    mois = request.GET.get('mois')

    if statut:
        paiements = paiements.filter(cotisation__statut=statut)
    if mois:
        paiements = paiements.filter(date_paiement__month=mois)

    context = {
        'paiements': paiements[:50],  # Limite pour performance
        'total_paiements': paiements.count(),
        'sum_montants': sum(p.montant for p in paiements),
    }
    return render(request, 'paiements/liste.html', context)
