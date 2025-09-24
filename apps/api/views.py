from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from .serializers import AssociationSerializer, Association, PaiementSerializer, CotisationSerializer, Cotisation, Paiement, serializers


class AssociationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssociationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Association.objects.all()

    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Association.objects.all()
        elif self.request.user.role == 'admin_association':
            return Association.objects.filter(admin_principal=self.request.user)
        return Association.objects.none()


class CotisationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CotisationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Association.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin_association':
            return Cotisation.objects.filter(logement__association__admin_principal=user)
        elif user.role == 'resident':
            return Cotisation.objects.filter(logement__resident=user)
        return Cotisation.objects.none()


class PaiementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaiementSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Association.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin_association':
            return Paiement.objects.filter(cotisation__logement__association__admin_principal=user)
        elif user.role == 'resident':
            return Paiement.objects.filter(cotisation__logement__resident=user)
        return Paiement.objects.none()


class StatsView(APIView):
    """API simple pour les statistiques"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'admin_association':
            association = Association.objects.get(admin_principal=user)

            stats = {
                'total_logements': association.logements.count(),
                'logements_occupes': association.logements.filter(resident__isnull=False).count(),
                'total_cotisations': association.logements.aggregate(
                    total=Count('cotisations')
                )['total'] or 0,
                'cotisations_payees': Cotisation.objects.filter(
                    logement__association=association,
                    statut='payee'
                ).count(),
                'montant_collecte': Paiement.objects.filter(
                    cotisation__logement__association=association
                ).aggregate(total=Sum('montant'))['total'] or 0,
            }

        elif user.role == 'resident':
            try:
                logement = user.logement.first()
                stats = {
                    'total_cotisations': logement.cotisations.count() if logement else 0,
                    'cotisations_payees': logement.cotisations.filter(statut='payee').count() if logement else 0,
                    'montant_paye': Paiement.objects.filter(
                        cotisation__logement__resident=user
                    ).aggregate(total=Sum('montant'))['total'] or 0,
                }
            except:
                stats = {'error': 'Aucun logement assigné'}

        else:
            stats = {'error': 'Accès non autorisé'}

        return Response(stats)
