from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime, date
import json


class IltizamJSONEncoder(DjangoJSONEncoder):
    """Encodeur JSON personnalisé pour Iltizam"""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def api_response(data=None, message=None, status_code=status.HTTP_200_OK, errors=None):
    """Fonction utilitaire pour des réponses API cohérentes"""
    response_data = {
        'success': status_code < 400,
        'status_code': status_code,
        'timestamp': datetime.now().isoformat(),
    }

    if message:
        response_data['message'] = message

    if data is not None:
        response_data['data'] = data

    if errors:
        response_data['errors'] = errors

    return Response(response_data, status=status_code)


def api_error(message, status_code=status.HTTP_400_BAD_REQUEST, errors=None):
    """Fonction utilitaire pour les erreurs API"""
    return api_response(
        message=message,
        status_code=status_code,
        errors=errors
    )


def api_success(data=None, message="Opération réussie"):
    """Fonction utilitaire pour les succès API"""
    return api_response(
        data=data,
        message=message,
        status_code=status.HTTP_200_OK
    )


def validate_association_access(user, association):
    """Valider l'accès d'un utilisateur à une association"""
    if user.role == 'super_admin':
        return True

    if user.role == 'admin_association':
        try:
            from apps.associations.models import Association
            admin_association = Association.objects.get(admin_principal=user)
            return admin_association == association
        except Association.DoesNotExist:
            return False

    return False


def get_user_associations(user):
    """Récupérer les associations accessibles à un utilisateur"""
    from apps.associations.models import Association

    if user.role == 'super_admin':
        return Association.objects.all()

    if user.role == 'admin_association':
        try:
            association = Association.objects.get(admin_principal=user)
            return Association.objects.filter(id=association.id)
        except Association.DoesNotExist:
            return Association.objects.none()

    if user.role == 'resident':
        try:
            logement = user.logement.first()
            if logement:
                return Association.objects.filter(id=logement.association.id)
        except:
            pass

    return Association.objects.none()


def format_api_error(errors):
    """Formater les erreurs de validation pour l'API"""
    if isinstance(errors, dict):
        formatted_errors = {}
        for field, field_errors in errors.items():
            if isinstance(field_errors, list):
                formatted_errors[field] = [str(error) for error in field_errors]
            else:
                formatted_errors[field] = str(field_errors)
        return formatted_errors

    return {'non_field_errors': [str(errors)]}
