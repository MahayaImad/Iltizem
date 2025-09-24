from django.conf import settings


def iltizam_context(request):
    """Variables globales pour les templates"""
    context = {
        'THEME_COLORS': getattr(settings, 'THEME_COLORS', {}),
        'APP_NAME': 'Iltizam',
        'APP_VERSION': '1.0.0',
        'SUPPORT_EMAIL': 'support@iltizam.dz',
    }

    if request.user.is_authenticated:
        context['user_role'] = request.user.role

        if request.user.role == 'admin_association':
            try:
                from associations.models import Association
                context['user_association'] = Association.objects.get(
                    admin_principal=request.user
                )
            except Association.DoesNotExist:
                pass

    return context