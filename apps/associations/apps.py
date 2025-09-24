from django.apps import AppConfig


class AssociationsConfig(AppConfig):
    """Configuration de l'application Associations"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.associations'
    verbose_name = 'Gestion des Associations'

    def ready(self):
        """Signaux et configurations supplémentaires"""
        try:
            import apps.associations.signals
        except ImportError:
            pass