from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import date, timedelta
from cotisations.models import Cotisation


@shared_task
def envoyer_rappels_automatiques():
    """Envoyer des rappels pour les cotisations en retard"""
    # Cotisations en retard (échéance dépassée de 7 jours)
    date_limite = date.today() - timedelta(days=7)

    cotisations_retard = Cotisation.objects.filter(
        statut='due',
        date_echeance__lt=date_limite,
        logement__resident__isnull=False,
        logement__resident__email__isnull=False
    )

    for cotisation in cotisations_retard:
        # Marquer en retard
        cotisation.statut = 'retard'
        cotisation.save()

        # Envoyer email de rappel
        resident = cotisation.logement.resident

        if resident.email:
            sujet = f"Rappel - Cotisation en retard - {cotisation.logement.association.nom}"

            message = render_to_string('emails/rappel_retard.html', {
                'resident': resident,
                'cotisation': cotisation,
                'association': cotisation.logement.association,
            })

            try:
                send_mail(
                    sujet,
                    message,
                    'noreply@iltizem.dz',
                    [resident.email],
                    html_message=message
                )
            except Exception as e:
                print(f"Erreur envoi email pour {resident.email}: {e}")

    return f"Rappels envoyés pour {cotisations_retard.count()} cotisations"


@shared_task
def generer_cotisations_automatiques():
    """Générer automatiquement les cotisations mensuelles"""
    from apps.associations.models import Association
    from apps.cotisations.models import TypeCotisation
    from dateutil.relativedelta import relativedelta

    today = date.today()
    # Premier jour du mois prochain
    prochaine_periode = (today + relativedelta(months=1)).replace(day=1)

    total_created = 0

    for association in Association.objects.filter(actif=True):
        for type_cotisation in association.types_cotisations.filter(
                actif=True,
                periodicite='mensuelle'
        ):

            # Échéance au 10 du mois suivant
            echeance = prochaine_periode + relativedelta(day=10)

            for logement in association.logements.all():
                cotisation, created = Cotisation.objects.get_or_create(
                    logement=logement,
                    type_cotisation=type_cotisation,
                    periode=prochaine_periode,
                    defaults={
                        'montant': type_cotisation.montant,
                        'date_echeance': echeance,
                    }
                )

                if created:
                    total_created += 1

    return f"Cotisations générées: {total_created}"
