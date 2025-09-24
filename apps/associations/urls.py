from django.urls import path
from . import views

app_name = "associations"

urlpatterns = [
    path(
        "association/dashboard/",
        views.tableau_bord_association,
        name="tableau_bord_association"
    ),
]

