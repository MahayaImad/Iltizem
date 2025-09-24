"""
Utilitaire de ligne de commande administrative Django pour Iltizam.

Ce script permet d'exécuter les commandes de gestion Django :
- python manage.py runserver : Lancer le serveur de développement
- python manage.py migrate : Appliquer les migrations
- python manage.py createsuperuser : Créer un super utilisateur
- python manage.py collectstatic : Collecter les fichiers statiques
- python manage.py makemigrations : Créer de nouvelles migrations

Pour plus d'informations sur ce fichier, voir :
https://docs.djangoproject.com/en/4.2/ref/django-admin/
"""

import os
import sys

if __name__ == '__main__':
    # Définir le module de configuration Django par défaut
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iltizam.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Êtes-vous sûr qu'il est installé et "
            "disponible dans votre variable d'environnement PYTHONPATH ? "
            "Avez-vous oublié d'activer un environnement virtuel ?"
        ) from exc

    # Exécuter la commande Django
    execute_from_command_line(sys.argv)