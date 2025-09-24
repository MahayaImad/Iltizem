from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime, timedelta
from django.core.cache import cache
import json


class APIRateLimitMiddleware(MiddlewareMixin):
    """Middleware de limitation du taux de requêtes API"""

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response

    def process_request(self, request):
        # Appliquer seulement aux URLs API
        if not request.path.startswith('/api/'):
            return None

        # Identifier l'utilisateur (IP ou token)
        if hasattr(request.user, 'auth_token'):
            identifier = f"api_rate_limit_user_{request.user.id}"
            limit = 120  # 120 requêtes par minute pour utilisateurs authentifiés
        else:
            identifier = f"api_rate_limit_ip_{self.get_client_ip(request)}"
            limit = 60  # 60 requêtes par minute pour IP anonymes

        # Vérifier le cache
        current_requests = cache.get(identifier, 0)

        if current_requests >= limit:
            return JsonResponse({
                'error': 'Limite de taux dépassée',
                'message': f'Maximum {limit} requêtes par minute',
                'retry_after': 60
            }, status=429)

        # Incrémenter le compteur
        cache.set(identifier, current_requests + 1, 60)
        return None

    def get_client_ip(self, request):
        """Récupérer l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APILoggingMiddleware(MiddlewareMixin):
    """Middleware de logging des requêtes API"""

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response

    def process_request(self, request):
        if request.path.startswith('/api/'):
            request.api_start_time = datetime.now()
        return None

    def process_response(self, request, response):
        if hasattr(request, 'api_start_time') and request.path.startswith('/api/'):
            duration = datetime.now() - request.api_start_time

            # Logger les informations de la requête
            log_data = {
                'timestamp': request.api_start_time.isoformat(),
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': duration.total_seconds() * 1000,
                'user_id': request.user.id if hasattr(request.user, 'id') else None,
                'user_role': getattr(request.user, 'role', None),
                'ip_address': self.get_client_ip(request),
            }

            # En développement, afficher dans la console
            # En production, envoyer vers un service de logging
            import logging
            api_logger = logging.getLogger('api')
            api_logger.info(json.dumps(log_data))

        return response

    def get_client_ip(self, request):
        """Récupérer l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
