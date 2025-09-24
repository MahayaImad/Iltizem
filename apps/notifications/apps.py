from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Configuration de l'application Notifications"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Système de Notifications'

    def ready(self):
        """Signaux et configurations supplémentaires"""
        try:
            import apps.notifications.signals
        except ImportError:
            pass