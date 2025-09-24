from django.conf import settings


def iltizem_context(request):
    """Variables globales pour les templates"""
    context = {
        'THEME_COLORS': getattr(settings, 'THEME_COLORS', {}),
        'APP_NAME': 'iltizem',
        'APP_VERSION': '1.0.0',
        'SUPPORT_EMAIL': 'support@iltizem.dz',
    }

    if request.user.is_authenticated:
        context['user_role'] = request.user.role

        if request.user.role == 'admin_association':
            try:
                from apps.associations.models import Association
                context['user_association'] = Association.objects.get(
                    admin_principal=request.user
                )
            except Association.DoesNotExist:
                pass

    return context