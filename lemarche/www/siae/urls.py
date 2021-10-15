from django.urls import include, path

from lemarche.www.siae.views import SiaeDetailView, SiaeSearchResultsDownloadView, SiaeSearchResultsView


# https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = "siae"

urlpatterns = [
    path("", SiaeSearchResultsView.as_view(), name="search_results"),
    path("download/", SiaeSearchResultsDownloadView.as_view(), name="search_results_download"),
    path("<str:slug>/", include([path("", SiaeDetailView.as_view(), name="detail")])),
]
