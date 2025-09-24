"""
Configuration ASGI pour le projet iltizem.

Ce module contient l'application ASGI utilisée par les serveurs web
compatibles ASGI pour servir votre projet.

Utile pour les WebSockets et les fonctionnalités temps réel futures.
"""

import os
from django.core.asgi import get_asgi_application

# Définir le module de configuration Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iltizem.settings')

# Créer l'application ASGI
application = get_asgi_application()
