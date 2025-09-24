from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.contrib.auth import update_session_auth_hash
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import os

from .forms import (
    ProfilResidentForm, FiltresCotisationsResidentForm,
    DemandeContactForm, ChangePasswordForm
)
from apps.associations.models import Logement
from apps.cotisations.models import Cotisation
from apps.paiements.models import Paiement


@login_required
def tableau_bord_resident(request):
    """Tableau de bord principal pour les résidents"""
    if request.user.role != 'resident':
        messages.error(request, "Accès réservé aux résidents")
        return redirect('accounts:login')

    try:
        logement = Logement.objects.get(resident=request.user)
    except Logement.DoesNotExist:
        messages.warning(request, "Aucun logement assigné. Contactez votre administrateur.")
        return render(request, 'residents/no_logement.html')

    # Statistiques générales
    cotisations = logement.cotisations.all()
    paiements = Paiement.objects.filter(cotisation__logement=logement)

    # Statistiques financières
    total_cotisations = cotisations.count()
    cotisations_payees = cotisations.filter(statut='payee').count()
    cotisations_dues = cotisations.filter(statut__in=['due', 'retard']).count()
    cotisations_retard = cotisations.filter(statut='retard').count()

    total_paye = paiements.aggregate(total=Sum('montant'))['total'] or 0
    total_du = cotisations.filter(statut__in=['due', 'retard']).aggregate(total=Sum('montant'))['total'] or 0

    # Cotisations récentes
    cotisations_recentes = cotisations.order_by('-periode')[:5]

    # Paiements récents
    paiements_recents = paiements.order_by('-date_enregistrement')[:5]

    # Prochaine échéance
    prochaine_echeance = cotisations.filter(
        statut__in=['due', 'retard']
    ).order_by('date_echeance').first()

    context = {
        'logement': logement,
        'association': logement.association,
        'stats': {
            'total_cotisations': total_cotisations,
            'cotisations_payees': cotisations_payees,
            'cotisations_dues': cotisations_dues,
            'cotisations_retard': cotisations_retard,
            'total_paye': total_paye,
            'total_du': total_du,
            'taux_paiement': round((cotisations_payees / total_cotisations * 100), 1) if total_cotisations > 0 else 0,
        },
        'cotisations_recentes': cotisations_recentes,
        'paiements_recents': paiements_recents,
        'prochaine_echeance': prochaine_echeance,
    }

    return render(request, 'residents/tableau_bord.html', context)


@login_required
def mes_cotisations(request):
    """Liste des cotisations du résident avec filtres"""
    if request.user.role != 'resident':
        messages.error(request, "Accès non autorisé")
        return redirect('accounts:login')

    try:
        logement = Logement.objects.get(resident=request.user)
        cotisations = logement.cotisations.all().select_related('type_cotisation')
    except Logement.DoesNotExist:
        cotisations = Cotisation.objects.none()
        logement = None

    # Appliquer les filtres
    form = FiltresCotisationsResidentForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('statut'):
            cotisations = cotisations.filter(statut=form.cleaned_data['statut'])
        if form.cleaned_data.get('annee'):
            cotisations = cotisations.filter(periode__year=form.cleaned_data['annee'])

    cotisations = cotisations.order_by('-periode')

    # Statistiques pour les filtres
    if logement:
        stats_annees = logement.cotisations.values_list('periode__year', flat=True).distinct().order_by(
            '-periode__year')
    else:
        stats_annees = []

    context = {
        'cotisations': cotisations,
        'logement': logement,
        'form': form,
        'stats_annees': stats_annees,
        'total_affiches': cotisations.count(),
    }

    return render(request, 'residents/cotisations.html', context)


@login_required
def details_cotisation(request, cotisation_id):
    """Détails d'une cotisation spécifique"""
    if request.user.role != 'resident':
        messages.error(request, "Accès non autorisé")
        return redirect('accounts:login')

    cotisation = get_object_or_404(
        Cotisation.objects.select_related('logement', 'type_cotisation'),
        id=cotisation_id,
        logement__resident=request.user
    )

    # Paiement associé s'il existe
    paiement = None
    if hasattr(cotisation, 'paiement'):
        paiement = cotisation.paiement

    context = {
        'cotisation': cotisation,
        'paiement': paiement,
        'logement': cotisation.logement,
    }

    return render(request, 'residents/details_cotisation.html', context)


@login_required
def mes_paiements(request):
    """Liste des paiements du résident"""
    if request.user.role != 'resident':
        messages.error(request, "Accès non autorisé")
        return redirect('accounts:login')

    try:
        logement = Logement.objects.get(resident=request.user)
        paiements = Paiement.objects.filter(
            cotisation__logement=logement
        ).select_related('cotisation').order_by('-date_enregistrement')
    except Logement.DoesNotExist:
        paiements = Paiement.objects.none()
        logement = None

    # Statistiques
    if paiements.exists():
        total_paye = paiements.aggregate(total=Sum('montant'))['total'] or 0
        repartition_methodes = paiements.values('methode').annotate(
            count=Count('id'),
            total=Sum('montant')
        ).order_by('-total')
    else:
        total_paye = 0
        repartition_methodes = []

    context = {
        'paiements': paiements[:50],  # Limiter pour performance
        'logement': logement,
        'stats': {
            'total_paye': total_paye,
            'nombre_paiements': paiements.count(),
            'repartition_methodes': repartition_methodes,
        }
    }

    return render(request, 'residents/paiements.html', context)


@login_required
def mes_reçus(request):
    """Liste des reçus disponibles"""
    if request.user.role != 'resident':
        messages.error(request, "Accès non autorisé")
        return redirect('accounts:login')

    try:
        logement = Logement.objects.get(resident=request.user)
        paiements_avec_reçu = Paiement.objects.filter(
            cotisation__logement=logement,
            recu_genere=True
        ).select_related('cotisation').order_by('-date_paiement')
    except Logement.DoesNotExist:
        paiements_avec_reçu = Paiement.objects.none()
        logement = None

    context = {
        'paiements_avec_reçu': paiements_avec_reçu,
        'logement': logement,
        'total_reçus': paiements_avec_reçu.count(),
    }

    return render(request, 'residents/reçus.html', context)


@login_required
def telecharger_reçu(request, paiement_id):
    """Télécharger un reçu de paiement"""
    if request.user.role != 'resident':
        raise Http404("Reçu non trouvé")

    paiement = get_object_or_404(
        Paiement.objects.select_related('cotisation__logement'),
        id=paiement_id,
        cotisation__logement__resident=request.user,
        recu_genere=True
    )

    # Générer le reçu à la demande (simple)
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from io import BytesIO

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # En-tête
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 80, "REÇU DE PAIEMENT")

    # Informations association
    association = paiement.cotisation.logement.association
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 120, f"Association: {association.nom}")
    p.drawString(50, height - 140, f"Adresse: {association.adresse}")

    # Informations résident
    resident = paiement.cotisation.logement.resident
    p.drawString(50, height - 180, f"Résident: {resident.get_full_name()}")
    p.drawString(50, height - 200, f"Logement: {paiement.cotisation.logement.numero}")

    # Informations paiement
    y = height - 250
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "DÉTAILS DU PAIEMENT")

    y -= 30
    p.setFont("Helvetica", 11)
    infos = [
        f"Période: {paiement.cotisation.periode.strftime('%B %Y')}",
        f"Montant: {paiement.montant} DA",
        f"Méthode: {paiement.get_methode_display()}",
        f"Date de paiement: {paiement.date_paiement.strftime('%d/%m/%Y')}",
        f"Référence: {paiement.reference or 'N/A'}",
        f"Reçu N°: RECU-{paiement.id}",
    ]

    for info in infos:
        p.drawString(50, y, info)
        y -= 20

    # Signature
    y -= 40
    p.drawString(50, y, f"Reçu généré le {date.today().strftime('%d/%m/%Y')}")
    p.drawString(50, y - 20, "Signature électronique - Plateforme Iltizam")

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_paiement_{paiement.id}.pdf"'

    return response


@login_required
def modifier_profil(request):
    """Modifier le profil du résident"""
    if request.user.role != 'resident':
        messages.error(request, "Accès non autorisé")
        return redirect('accounts:login')

    if request.method == 'POST':
        form = ProfilResidentForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès")
            return redirect('residents:profil')
    else:
        form = ProfilResidentForm(instance=request.user)

    # Informations sur le logement
    try:
        logement = Logement.objects.get(resident=request.user)
    except Logement.DoesNotExist:
        logement = None

    context = {
        'form': form,
        'logement': logement,
    }

    return render(request, 'residents/profil.html', context)


@login_required
def changer_mot_de_passe(request):
    """Changer le mot de passe"""
    if request.user.role != 'resident':
        messages.error(request, "Accès non autorisé")
        return redirect('accounts:login')

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            # Changer le mot de passe
            request.user.set_password(form.cleaned_data['nouveau_mot_de_passe'])
            request.user.save()

            # Maintenir la session active
            update_session_auth_hash(request, request.user)

            messages.success(request, "Mot de passe modifié avec succès")
            return redirect('residents:profil')
    else:
        form = ChangePasswordForm(user=request.user)

    context = {
        'form': form,
    }

    return render(request, 'residents/changer_mot_de_passe.html', context)


@login_required
def contacter_administration(request):
    """Contacter l'administration de l'association"""
    if request.user.role != 'resident':
        messages.error(request, "Accès non autorisé")
        return redirect('accounts:login')

    try:
        logement = Logement.objects.get(resident=request.user)
        association = logement.association
    except Logement.DoesNotExist:
        messages.error(request, "Aucun logement assigné")
        return redirect('residents:tableau_bord')

    if request.method == 'POST':
        form = DemandeContactForm(request.POST)
        if form.is_valid():
            # Envoyer l'email à l'admin de l'association
            sujet_email = f"[{association.nom}] {form.cleaned_data['titre']}"
            message_email = f"""
Nouvelle demande de contact de la part d'un résident :

Résident : {request.user.get_full_name() or request.user.username}
Logement : {logement.numero}
Email : {request.user.email}
Téléphone : {request.user.telephone or 'Non renseigné'}

Sujet : {form.cleaned_data['sujet']}
Titre : {form.cleaned_data['titre']}

Message :
{form.cleaned_data['message']}

---
Message envoyé depuis la plateforme Iltizam
            """

            try:
                send_mail(
                    subject=sujet_email,
                    message=message_email,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[association.admin_principal.email],
                    fail_silently=False
                )

                messages.success(request, "Votre message a été envoyé à l'administration")
                return redirect('residents:tableau_bord')

            except Exception as e:
                messages.error(request, "Erreur lors de l'envoi du message. Réessayez plus tard.")

    else:
        form = DemandeContactForm()

    context = {
        'form': form,
        'association': association,
        'logement': logement,
    }

    return render(request, 'residents/contact.html', context)


@login_required
def statistiques_resident_api(request):
    """API pour les statistiques du résident (pour graphiques)"""
    if request.user.role != 'resident':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)

    try:
        logement = Logement.objects.get(resident=request.user)
    except Logement.DoesNotExist:
        return JsonResponse({'error': 'Aucun logement assigné'}, status=404)

    # Paiements par mois sur les 12 derniers mois
    aujourd_hui = date.today()
    debut_periode = aujourd_hui - relativedelta(months=11)
    debut_periode = debut_periode.replace(day=1)

    paiements_par_mois = []
    current_date = debut_periode

    while current_date <= aujourd_hui:
        fin_mois = (current_date + relativedelta(months=1)) - relativedelta(days=1)

        montant_mois = Paiement.objects.filter(
            cotisation__logement=logement,
            date_paiement__gte=current_date,
            date_paiement__lte=fin_mois
        ).aggregate(total=Sum('montant'))['total'] or 0

        paiements_par_mois.append({
            'mois': current_date.strftime('%m/%Y'),
            'montant': float(montant_mois)
        })

        current_date += relativedelta(months=1)

    # Répartition par statut
    cotisations = logement.cotisations.all()
    repartition_statuts = []
    for statut, label in Cotisation._meta.get_field('statut').choices:
        count = cotisations.filter(statut=statut).count()
        if count > 0:
            repartition_statuts.append({
                'statut': label,
                'count': count
            })

    data = {
        'paiements_par_mois': paiements_par_mois,
        'repartition_statuts': repartition_statuts,
        'logement_info': {
            'numero': logement.numero,
            'association': logement.association.nom,
            'superficie': float(logement.superficie) if logement.superficie else None,
        }
    }

    return JsonResponse(data)