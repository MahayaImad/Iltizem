from django.utils import timezone
from django.conf import settings


class TimezoneMiddleware:
    """Middleware pour gérer le fuseau horaire Algérie"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timezone.activate(settings.TIME_ZONE)
        response = self.get_response(request)
        return response