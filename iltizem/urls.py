from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),

    # Application principale (authentification, accueil)
    path('', include('apps.accounts.urls')),

    # Applications métier
    path('associations/', include('apps.associations.urls')),
    path('residents/', include('apps.residents.urls')),  # ✅ AJOUTÉ
    path('cotisations/', include('apps.cotisations.urls')),
    path('paiements/', include('apps.paiements.urls')),
    path('rapports/', include('apps.rapports.urls')),  # ✅ AJOUTÉ

    # API REST
    path('api/', include('apps.api.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)