from django.apps import AppConfig


class PaiementsConfig(AppConfig):
    """Configuration de l'application Paiements"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.paiements'
    verbose_name = 'Gestion des Paiements'

    def ready(self):
        """Signaux et configurations supplémentaires"""
        try:
            import apps.paiements.signals
        except ImportError:
            pass