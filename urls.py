from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('associations/', include('associations.urls')),
    path('cotisations/', include('cotisations.urls')),
    path('paiements/', include('paiements.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# associations/urls.py
from django.urls import path
from . import views

app_name = 'associations'

urlpatterns = [
    path('tableau-bord/', views.tableau_bord_association, name='tableau_bord'),
    path('logements/', views.gestion_logements, name='logements'),
    path('parametres/', views.parametres_association, name='parametres'),
]