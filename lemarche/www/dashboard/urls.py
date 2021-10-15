from django.urls import include, path
from django.views.generic.base import RedirectView

from lemarche.www.dashboard.views import (
    DashboardHomeView,
    ProfileEditView,
    SiaeEditInfoContactView,
    SiaeEditOfferView,
    SiaeEditOtherView,
    SiaeEditPrestaView,
    SiaeSearchAdoptConfirmView,
    SiaeSearchBySiretView,
)


# https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = "dashboard"

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="home"),
    path("modifier/", ProfileEditView.as_view(), name="profile_edit"),
    path("prestataires/rechercher/", SiaeSearchBySiretView.as_view(), name="siae_search_by_siret"),
    path("prestataires/<str:slug>/adopter/", SiaeSearchAdoptConfirmView.as_view(), name="siae_search_adopt_confirm"),
    path(
        "prestataires/<str:slug>/modifier/",
        include(
            [
                path(
                    "",
                    RedirectView.as_view(pattern_name="dashboard:siae_edit_info_contact", permanent=False),
                    name="siae_edit",
                ),
                path("info-contact/", SiaeEditInfoContactView.as_view(), name="siae_edit_info_contact"),
                path("offre/", SiaeEditOfferView.as_view(), name="siae_edit_offer"),
                path("prestations/", SiaeEditPrestaView.as_view(), name="siae_edit_presta"),
                path("autre/", SiaeEditOtherView.as_view(), name="siae_edit_other"),
            ]
        ),
    ),
    path(
        "prestataires/<str:slug>/",
        RedirectView.as_view(pattern_name="dashboard:siae_edit_info_contact", permanent=False),
        name="siae",
    ),
    path(
        "prestataires/",
        RedirectView.as_view(pattern_name="dashboard:siae_search_by_siret", permanent=False),
        name="siae_search",
    ),
]
