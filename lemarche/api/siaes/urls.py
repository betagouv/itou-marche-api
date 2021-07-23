from lemarche.api.siaes import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


# Basic idea is to use hyperlinkedmodelserializer and viewsets
# But unclear documentation and confusing error messages did
# not allow it to work, yet.

urlpatterns = [
    # path("siaes/", views.SiaeList.as_view()),
    # path("siaes/<str:pk>/", views.SiaeDetail.as_view()),
    path("siae/id/<str:pk>/", views.Siae.as_view({"get": "retrieve_by_id"})),
    path("siae/siret/<str:siret>/", views.Siae.as_view({"get": "retrieve_by_siret"})),
    path("siae/", views.Siae.as_view({"get": "list"})),
    path("secteurs/", views.Sectors.as_view({"get": "list"})),
    path("secteurs/<str:pk>", views.Sectors.as_view({"get": "retrieve"})),
    # Schema
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="OpenAPI"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
