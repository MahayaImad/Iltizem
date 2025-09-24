"""
Configuration ASGI pour le projet iltizam.

Ce module contient l'application ASGI utilisée par les serveurs web
compatibles ASGI pour servir votre projet.

Utile pour les WebSockets et les fonctionnalités temps réel futures.
"""

import os
from django.core.asgi import get_asgi_application

# Définir le module de configuration Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iltizam.settings')

# Créer l'application ASGI
application = get_asgi_application()
