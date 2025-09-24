from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration de l'application Accounts"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'  # ✅ Chemin complet CORRECT
    verbose_name = 'Gestion des Utilisateurs'

    def ready(self):
        """Signaux et configurations supplémentaires"""
        try:
            # Import des signaux si nécessaire (création de profils, etc.)
            import apps.accounts.signals
        except ImportError:
            pass