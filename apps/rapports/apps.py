from django.apps import AppConfig


class RapportsConfig(AppConfig):
    """Configuration de l'application Rapports"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rapports'
    verbose_name = 'Génération de Rapports'

    def ready(self):
        """Signaux et configurations supplémentaires"""
        try:
            import apps.rapports.signals
        except ImportError:
            pass