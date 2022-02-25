from django.urls import include, path
from django.views.generic.base import RedirectView

from lemarche.www.dashboard.views import (
    DashboardHomeView,
    ProfileEditView,
    ProfileFavoriteItemDeleteView,
    ProfileFavoriteListCreateView,
    ProfileFavoriteListDeleteView,
    ProfileFavoriteListDetailView,
    ProfileFavoriteListEditView,
    ProfileFavoriteListView,
    SiaeEditInfoContactView,
    SiaeEditOfferView,
    SiaeEditOtherView,
    SiaeEditPrestaView,
    SiaeSearchAdoptConfirmView,
    SiaeSearchBySiretView,
    SiaeUserRequestCancel,
    SiaeUserRequestConfirm,
    SiaeUsersView,
)


# https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = "dashboard"

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="home"),
    path("modifier/", ProfileEditView.as_view(), name="profile_edit"),
    # FavoriteList
    path("listes-dachats/", ProfileFavoriteListView.as_view(), name="profile_favorite_list"),
    path("listes-dachats/creer/", ProfileFavoriteListCreateView.as_view(), name="profile_favorite_list_create"),
    path("listes-dachats/<str:slug>/", ProfileFavoriteListDetailView.as_view(), name="profile_favorite_list_detail"),
    path(
        "listes-dachats/<slug:slug>/prestataires/<slug:siae_slug>/",
        ProfileFavoriteItemDeleteView.as_view(),
        name="profile_favorite_item_delete",
    ),
    path(
        "listes-dachats/<str:slug>/modifier/", ProfileFavoriteListEditView.as_view(), name="profile_favorite_list_edit"
    ),
    path(
        "listes-dachats/<str:slug>/supprimer/",
        ProfileFavoriteListDeleteView.as_view(),
        name="profile_favorite_list_delete",
    ),
    # Adopt Siae
    path("prestataires/rechercher/", SiaeSearchBySiretView.as_view(), name="siae_search_by_siret"),
    path("prestataires/<str:slug>/adopter/", SiaeSearchAdoptConfirmView.as_view(), name="siae_search_adopt_confirm"),
    # Edit Siae
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
    # Siae Users (& Requests)
    path(
        "prestataires/<str:slug>/collaborateurs/",
        SiaeUsersView.as_view(),
        name="siae_users",
    ),
    path(
        "prestataires/<str:slug>/collaborateurs/<str:siaeuserrequest_id>/accepter",
        SiaeUserRequestConfirm.as_view(),
        name="siae_user_request_confirm",
    ),
    path(
        "prestataires/<str:slug>/collaborateurs/<str:siaeuserrequest_id>/refuser",
        SiaeUserRequestCancel.as_view(),
        name="siae_user_request_cancel",
    ),
    # Redirects
    path(
        "prestataires/<str:slug>/",
        RedirectView.as_view(pattern_name="dashboard:siae_users", permanent=False),
        name="siae",
    ),
    path(
        "prestataires/",
        RedirectView.as_view(pattern_name="dashboard:siae_search_by_siret", permanent=False),
        name="siae_search",
    ),
]
