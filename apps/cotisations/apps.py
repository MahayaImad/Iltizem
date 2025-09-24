from django.apps import AppConfig


class CotisationsConfig(AppConfig):
    """Configuration de l'application Cotisations"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cotisations'
    verbose_name = 'Gestion des Cotisations'

    def ready(self):
        """Signaux et configurations supplémentaires"""
        try:
            import apps.cotisations.signals
        except ImportError:
            pass
