from rest_framework import permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée pour permettre aux utilisateurs
    de voir seulement leurs propres données ou aux admins de voir tout
    """

    def has_permission(self, request, view):
        # L'utilisateur doit être authentifié
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Super admin peut tout voir
        if request.user.role == 'super_admin':
            return True

        # Admin association peut voir les données de son association
        if request.user.role == 'admin_association':
            # Vérifier selon le type d'objet
            if hasattr(obj, 'association'):
                try:
                    from apps.associations.models import Association
                    admin_association = Association.objects.get(admin_principal=request.user)
                    return obj.association == admin_association
                except Association.DoesNotExist:
                    return False

            # Pour les logements
            if hasattr(obj, 'logement'):
                try:
                    from apps.associations.models import Association
                    admin_association = Association.objects.get(admin_principal=request.user)
                    return obj.logement.association == admin_association
                except Association.DoesNotExist:
                    return False

        # Résident peut voir seulement ses propres données
        if request.user.role == 'resident':
            if hasattr(obj, 'resident'):
                return obj.resident == request.user
            if hasattr(obj, 'logement') and hasattr(obj.logement, 'resident'):
                return obj.logement.resident == request.user

        return False


class IsAssociationAdmin(permissions.BasePermission):
    """Permission pour les admins d'association"""

    def has_permission(self, request, view):
        return (request.user and
                request.user.is_authenticated and
                request.user.role in ['super_admin', 'admin_association'])


class IsSuperAdmin(permissions.BasePermission):
    """Permission pour les super admins uniquement"""

    def has_permission(self, request, view):
        return (request.user and
                request.user.is_authenticated and
                request.user.role == 'super_admin')


class IsResident(permissions.BasePermission):
    """Permission pour les résidents"""

    def has_permission(self, request, view):
        return (request.user and
                request.user.is_authenticated and
                request.user.role == 'resident')


class APITokenPermission(permissions.BasePermission):
    """Permission basée sur les tokens API"""

    def has_permission(self, request, view):
        # Vérifier si l'utilisateur a un token API valide
        if hasattr(request.user, 'auth_token'):
            return True

        # Vérifier le header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            try:
                token = Token.objects.get(key=token_key)
                return token.user.is_active
            except Token.DoesNotExist:
                return False

        return False
