from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configuration de l'application API"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api'
    verbose_name = 'API REST'

    def ready(self):
        """Signaux et configurations supplémentaires"""
        try:
            import apps.api.signals
        except ImportError:
            pass
