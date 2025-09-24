from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration de l'application Accounts"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Gestion des Utilisateurs'

    def ready(self):
        """Signaux et configurations supplémentaires"""
        try:
            import apps.accounts.signals  # Import des signaux si nécessaire
        except ImportError:
            pass