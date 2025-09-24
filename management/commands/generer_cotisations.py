from django.core.management.base import BaseCommand
from datetime import date, timedelta
from apps.associations.models import Association
from apps.cotisations.models import TypeCotisation, Cotisation


class Command(BaseCommand):
    help = 'Génère automatiquement les cotisations pour le mois/trimestre suivant'

    def handle(self, *args, **options):
        """Génération automatique - Principe KISS"""
        aujourd_hui = date.today()

        for association in Association.objects.filter(actif=True):
            for type_cotisation in association.types_cotisations.filter(actif=True):

                # Calculer la prochaine période selon la périodicité
                if type_cotisation.periodicite == 'mensuelle':
                    prochaine_periode = aujourd_hui.replace(day=1)
                    echeance = prochaine_periode + timedelta(days=31)
                elif type_cotisation.periodicite == 'trimestrielle':
                    # Logique simplifiée pour trimestre
                    prochaine_periode = aujourd_hui.replace(day=1, month=((aujourd_hui.month - 1) // 3) * 3 + 1)
                    echeance = prochaine_periode + timedelta(days=93)
                else:  # annuelle
                    prochaine_periode = aujourd_hui.replace(day=1, month=1)
                    echeance = prochaine_periode + timedelta(days=366)

                # Créer cotisations pour tous les logements
                for logement in association.logements.all():
                    cotisation, created = Cotisation.objects.get_or_create(
                        logement=logement,
                        type_cotisation=type_cotisation,
                        periode=prochaine_periode,
                        defaults={
                            'montant': type_cotisation.montant,
                            'date_echeance': echeance,
                        }
                    )

                    if created:
                        self.stdout.write(f"Cotisation créée: {cotisation}")

        self.stdout.write(self.style.SUCCESS("Génération des cotisations terminée"))