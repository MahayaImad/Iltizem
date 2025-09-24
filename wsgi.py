"""
Configuration WSGI pour le projet iltizam.

Ce module contient l'application WSGI utilisée par les serveurs web
compatibles WSGI pour servir votre projet.

Pour plus d'informations sur ce fichier, voir :
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Définir le module de configuration Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iltizam.settings')

# Créer l'application WSGI
application = get_wsgi_application()