"""
Configuration Celery pour les tâches asynchrones
- Envoi d'emails automatiques
- Génération de cotisations
- Rappels de paiement
- Rapports programmés
"""

import os
from celery import Celery
from django.conf import settings

# Définir le module de configuration Django par défaut pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iltizem.settings')

# Créer l'instance Celery
app = Celery('iltizem')

# Configuration à partir des settings Django avec le préfixe CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-découverte des tâches dans toutes les applications Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Tâche de debug pour tester Celery"""
    print(f'Request: {self.request!r}')


# Configuration des tâches périodiques
app.conf.beat_schedule = {
    # Envoi des rappels de retard tous les jours à 9h
    'envoyer-rappels-quotidiens': {
        'task': 'notifications.tasks.envoyer_rappels_automatiques',
        'schedule': 60.0 * 60 * 24,  # 24 heures en secondes (plus simple que crontab pour commencer)
        'options': {'expires': 30.0}
    },

    # Génération des cotisations mensuelles le 25 de chaque mois
    'generer-cotisations-mensuelles': {
        'task': 'cotisations.tasks.generer_cotisations_automatiques',
        'schedule': 60.0 * 60 * 24 * 30,  # 30 jours (sera affiné avec crontab plus tard)
        'options': {'expires': 60.0}
    },

    # Mise à jour des statuts de cotisations (retard) tous les jours à 1h
    'mettre-a-jour-statuts': {
        'task': 'cotisations.tasks.mettre_a_jour_statuts_retard',
        'schedule': 60.0 * 60 * 24,  # 24 heures
        'options': {'expires': 30.0}
    },
}

# Fuseau horaire
app.conf.timezone = 'Africa/Algiers'