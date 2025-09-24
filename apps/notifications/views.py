from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from datetime import date, timedelta

from .models import NotificationTemplate, NotificationLog
from .forms import NotificationTemplateForm, EnvoiNotificationForm, FiltresNotificationLogForm
from apps.associations.models import Association
from apps.cotisations.models import Cotisation
from apps.accounts.models import User


@login_required
def liste_notifications(request):
    """Vue principale des notifications"""
    if request.user.role not in ['super_admin', 'admin_association']:
        messages.error(request, "Accès non autorisé")
        return redirect('home')

    # Statistiques simples
    if request.user.role == 'admin_association':
        try:
            association = Association.objects.get(admin_principal=request.user)
            logs = NotificationLog.objects.filter(association=association)
        except Association.DoesNotExist:
            logs = NotificationLog.objects.none()
    else:
        logs = NotificationLog.objects.all()

    stats = {
        'total_envoyes': logs.filter(statut='envoye').count(),
        'en_erreur': logs.filter(statut='erreur').count(),
        'en_attente': logs.filter(statut='en_attente').count(),
        'derniers_logs': logs.order_by('-date_envoi')[:10],
    }

    context = {
        'stats': stats,
        'templates_actifs': NotificationTemplate.objects.filter(actif=True).count(),
    }

    return render(request, 'notifications/liste.html', context)


@login_required
def gestion_templates(request):
    """Gestion des templates de notifications"""
    if request.user.role not in ['super_admin', 'admin_association']:
        messages.error(request, "Accès non autorisé")
        return redirect('home')

    templates = NotificationTemplate.objects.all().order_by('nom')

    context = {
        'templates': templates,
    }

    return render(request, 'notifications/templates.html', context)


@login_required
def creer_template(request):
    """Créer un nouveau template"""
    if request.user.role not in ['super_admin', 'admin_association']:
        messages.error(request, "Accès non autorisé")
        return redirect('home')

    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST)
        if form.is_valid():
            template = form.save()
            messages.success(request, f"Template '{template.nom}' créé avec succès")
            return redirect('notifications:templates')
    else:
        form = NotificationTemplateForm()

    context = {
        'form': form,
        'action': 'Créer',
    }

    return render(request, 'notifications/template_form.html', context)


@login_required
def modifier_template(request, template_id):
    """Modifier un template existant"""
    if request.user.role not in ['super_admin', 'admin_association']:
        messages.error(request, "Accès non autorisé")
        return redirect('home')

    template = get_object_or_404(NotificationTemplate, id=template_id)

    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST, instance=template)
        if form.is_valid():
            template = form.save()
            messages.success(request, f"Template '{template.nom}' modifié avec succès")
            return redirect('notifications:templates')
    else:
        form = NotificationTemplateForm(instance=template)

    context = {
        'form': form,
        'template': template,
        'action': 'Modifier',
    }

    return render(request, 'notifications/template_form.html', context)


@login_required
def envoyer_notification(request):
    """Envoyer une notification ponctuelle"""
    if request.user.role not in ['super_admin', 'admin_association']:
        messages.error(request, "Accès non autorisé")
        return redirect('home')

    if request.method == 'POST':
        form = EnvoiNotificationForm(request.POST, user=request.user)
        if form.is_valid():
            template = form.cleaned_data['template']
            critere = form.cleaned_data['critere']

            # Déterminer les destinataires selon le critère
            destinataires = []

            if critere == 'tous':
                residents = User.objects.filter(role='resident', is_active=True, email__isnull=False)
                destinataires = [r.email for r in residents if r.email]

            elif critere == 'retard':
                cotisations_retard = Cotisation.objects.filter(statut='retard')
                residents = User.objects.filter(
                    logement__cotisations__in=cotisations_retard,
                    email__isnull=False
                ).distinct()
                destinataires = [r.email for r in residents if r.email]

            elif critere == 'association':
                association = form.cleaned_data.get('association')
                if association:
                    residents = User.objects.filter(
                        logement__association=association,
                        email__isnull=False
                    )
                    destinataires = [r.email for r in residents if r.email]

            elif critere == 'manuel':
                emails_saisis = form.cleaned_data['destinataires']
                destinataires = [email.strip() for email in emails_saisis.split(',') if email.strip()]

            # Envoyer les notifications
            count_envoyes = 0
            for email in destinataires:
                try:
                    # Context simple pour le template
                    context = {
                        'destinataire': email,
                        'association': form.cleaned_data.get('association'),
                    }

                    contenu_rendu = template.render(context)

                    # Envoyer l'email
                    send_mail(
                        subject=template.sujet,
                        message=contenu_rendu,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False
                    )

                    # Logger la notification
                    NotificationLog.objects.create(
                        type_notification='email',
                        destinataire=email,
                        sujet=template.sujet,
                        contenu=contenu_rendu,
                        statut='envoye',
                        template=template,
                        association=form.cleaned_data.get('association'),
                        envoye_par=request.user
                    )

                    count_envoyes += 1

                except Exception as e:
                    # Logger l'erreur
                    NotificationLog.objects.create(
                        type_notification='email',
                        destinataire=email,
                        sujet=template.sujet,
                        contenu=template.contenu,
                        statut='erreur',
                        erreur_message=str(e),
                        template=template,
                        association=form.cleaned_data.get('association'),
                        envoye_par=request.user
                    )

            messages.success(request, f"{count_envoyes} notification(s) envoyée(s) avec succès")
            return redirect('notifications:logs')

    else:
        form = EnvoiNotificationForm(user=request.user)

    context = {
        'form': form,
    }

    return render(request, 'notifications/envoyer.html', context)


@login_required
def logs_notifications(request):
    """Afficher les logs de notifications avec filtres"""
    if request.user.role not in ['super_admin', 'admin_association']:
        messages.error(request, "Accès non autorisé")
        return redirect('home')

    # Filtrer selon le rôle
    if request.user.role == 'admin_association':
        try:
            association = Association.objects.get(admin_principal=request.user)
            logs = NotificationLog.objects.filter(association=association)
        except Association.DoesNotExist:
            logs = NotificationLog.objects.none()
    else:
        logs = NotificationLog.objects.all()

    # Appliquer les filtres
    form = FiltresNotificationLogForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('type_notification'):
            logs = logs.filter(type_notification=form.cleaned_data['type_notification'])
        if form.cleaned_data.get('statut'):
            logs = logs.filter(statut=form.cleaned_data['statut'])
        if form.cleaned_data.get('date_debut'):
            logs = logs.filter(date_envoi__date__gte=form.cleaned_data['date_debut'])
        if form.cleaned_data.get('date_fin'):
            logs = logs.filter(date_envoi__date__lte=form.cleaned_data['date_fin'])

    logs = logs.order_by('-date_envoi')[:100]  # Limiter pour performance

    context = {
        'logs': logs,
        'form': form,
    }

    return render(request, 'notifications/logs.html', context)


@login_required
def envoyer_rappels(request):
    """Envoyer des rappels automatiques"""
    if request.user.role not in ['super_admin', 'admin_association']:
        messages.error(request, "Accès non autorisé")
        return redirect('home')

    if request.method == 'POST':
        # Trouver les cotisations en retard
        if request.user.role == 'admin_association':
            try:
                association = Association.objects.get(admin_principal=request.user)
                cotisations_retard = Cotisation.objects.filter(
                    logement__association=association,
                    statut='retard'
                )
            except Association.DoesNotExist:
                cotisations_retard = Cotisation.objects.none()
        else:
            cotisations_retard = Cotisation.objects.filter(statut='retard')

        # Template de rappel
        try:
            template = NotificationTemplate.objects.get(nom='Rappel Retard', actif=True)
        except NotificationTemplate.DoesNotExist:
            messages.error(request, "Template 'Rappel Retard' introuvable")
            return redirect('notifications:liste')

        count_envoyes = 0

        for cotisation in cotisations_retard:
            if cotisation.logement.resident and cotisation.logement.resident.email:
                try:
                    context = {
                        'resident': cotisation.logement.resident,
                        'cotisation': cotisation,
                        'association': cotisation.logement.association,
                    }

                    contenu_rendu = template.render(context)

                    send_mail(
                        subject=template.sujet,
                        message=contenu_rendu,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[cotisation.logement.resident.email],
                        fail_silently=False
                    )

                    # Logger
                    NotificationLog.objects.create(
                        type_notification='email',
                        destinataire=cotisation.logement.resident.email,
                        sujet=template.sujet,
                        contenu=contenu_rendu,
                        statut='envoye',
                        template=template,
                        association=cotisation.logement.association,
                        envoye_par=request.user
                    )

                    count_envoyes += 1

                except Exception as e:
                    # Logger l'erreur
                    NotificationLog.objects.create(
                        type_notification='email',
                        destinataire=cotisation.logement.resident.email,
                        sujet=template.sujet,
                        contenu=template.contenu,
                        statut='erreur',
                        erreur_message=str(e),
                        template=template,
                        association=cotisation.logement.association,
                        envoye_par=request.user
                    )

        messages.success(request, f"{count_envoyes} rappel(s) envoyé(s)")
        return redirect('notifications:logs')

    # Compter les cotisations en retard
    if request.user.role == 'admin_association':
        try:
            association = Association.objects.get(admin_principal=request.user)
            count_retard = Cotisation.objects.filter(
                logement__association=association,
                statut='retard'
            ).count()
        except Association.DoesNotExist:
            count_retard = 0
    else:
        count_retard = Cotisation.objects.filter(statut='retard').count()

    context = {
        'count_retard': count_retard,
    }

    return render(request, 'notifications/rappels.html', context)


@login_required
def test_email(request):
    """Tester l'envoi d'email"""
    if request.user.role not in ['super_admin', 'admin_association']:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)

    try:
        send_mail(
            subject='Test Iltizam - Configuration Email',
            message='Ceci est un test de configuration email depuis la plateforme Iltizam.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False
        )

        return JsonResponse({'success': True, 'message': 'Email de test envoyé avec succès'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})