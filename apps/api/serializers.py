from rest_framework import serializers
from associations.models import Association
from cotisations.models import Cotisation
from paiements.models import Paiement


class AssociationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Association
        fields = ['id', 'nom', 'adresse', 'plan', 'nombre_logements', 'date_creation']


class CotisationSerializer(serializers.ModelSerializer):
    logement_numero = serializers.CharField(source='logement.numero', read_only=True)
    resident_nom = serializers.CharField(source='logement.resident.get_full_name', read_only=True)

    class Meta:
        model = Cotisation
        fields = ['id', 'logement_numero', 'resident_nom', 'periode', 'montant', 'statut', 'date_echeance']


class PaiementSerializer(serializers.ModelSerializer):
    cotisation_info = CotisationSerializer(source='cotisation', read_only=True)

    class Meta:
        model = Paiement
        fields = ['id', 'montant', 'methode', 'date_paiement', 'reference', 'cotisation_info']
