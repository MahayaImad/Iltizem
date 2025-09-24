from django.apps import AppConfig


class ResidentsConfig(AppConfig):
    """Configuration de l'application Residents"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.residents'
    verbose_name = 'Espace Résidents'

    def ready(self):
        """Signaux et configurations supplémentaires"""
        try:
            import apps.residents.signals
        except ImportError:
            pass