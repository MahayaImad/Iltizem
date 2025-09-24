from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class iltizemTokenAuthentication(TokenAuthentication):
    """Authentification par token personnalisée pour iltizem"""

    keyword = 'Bearer'  # Utiliser Bearer au lieu de Token

    def authenticate_credentials(self, key):
        """Authentifier les credentials avec vérifications supplémentaires"""
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed(_('Token invalide.'))

        if not token.user.is_active:
            raise AuthenticationFailed(_('Utilisateur inactif ou supprimé.'))

        # Vérifications supplémentaires pour iltizem
        if token.user.role not in ['super_admin', 'admin_association', 'resident']:
            raise AuthenticationFailed(_('Rôle utilisateur invalide.'))

        return (token.user, token)


class APIKeyAuthentication(TokenAuthentication):
    """Authentification par clé API pour intégrations externes"""

    keyword = 'ApiKey'

    def authenticate_credentials(self, key):
        """Authentifier avec clé API"""
        # Pour le futur : système de clés API séparées des tokens utilisateurs
        # Pour l'instant, utilise le système de tokens existant
        return super().authenticate_credentials(key)
