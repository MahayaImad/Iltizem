from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string


def calculer_echeance(periode, periodicite):
    """Calculer la date d'échéance selon la périodicité"""
    if periodicite == 'mensuelle':
        return periode + relativedelta(months=1, day=10)
    elif periodicite == 'trimestrielle':
        return periode + relativedelta(months=3, day=10)
    else:  # annuelle
        return periode + relativedelta(years=1, day=10)


def calculer_penalite(cotisation):
    """Calculer la pénalité de retard (plan Silver+)"""
    if cotisation.date_echeance < date.today():
        jours_retard = (date.today() - cotisation.date_echeance).days
        if jours_retard > 30:  # Pénalité après 30 jours
            return cotisation.montant * Decimal('0.05')  # 5%
    return Decimal('0')


def envoyer_notification_email(destinataire, template, context, sujet):
    """Envoyer une notification par email"""
    try:
        message_html = render_to_string(f'emails/{template}.html', context)
        message_text = render_to_string(f'emails/{template}.txt', context)

        send_mail(
            sujet,
            message_text,
            'noreply@iltizam.dz',
            [destinataire],
            html_message=message_html,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False


def generer_numero_recu(paiement):
    """Générer un numéro de reçu unique"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"RECU-{paiement.id}-{timestamp}"