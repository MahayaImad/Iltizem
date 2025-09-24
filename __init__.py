"""
Initialisation du projet Django Iltizam
Configuration Celery pour les tâches asynchrones
"""

# Ceci garantit que l'app Celery est toujours importée quand Django démarre
from .celery import app as celery_app

__all__ = ('celery_app',)