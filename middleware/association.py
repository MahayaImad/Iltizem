from django.shortcuts import redirect
from django.contrib import messages
from apps.associations.models import Association


class AssociationMiddleware:
    """Middleware pour vérifier l'association de l'admin"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.user.is_authenticated and
                request.user.role == 'admin_association' and
                request.path.startswith('/associations/')):

            try:
                Association.objects.get(admin_principal=request.user, actif=True)
            except Association.DoesNotExist:
                messages.error(request, "Association inactive ou non trouvée")
                return redirect('accounts:login')

        return self.get_response(request)