from django.contrib import admin
from django.urls import reverse
from django.db.models import Count
from django.utils.html import format_html

from lemarche.sectors.models import SectorGroup, Sector


@admin.register(SectorGroup)
class SectorGroupAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "nb_sectors", "created_at"]
    search_fields = ["id", "name"]

    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(sector_count=Count('sectors'))
        return qs

    def nb_sectors(self, sector_group):
        url = reverse("admin:sectors_sector_changelist") + f"?group__id__exact={sector_group.id}"
        return format_html(f"<a href=\"{url}\">{sector_group.sector_count}</a>")
    nb_sectors.short_description = "Nombre de secteurs d'activité"
    nb_sectors.admin_order_field = "sector_count"


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "group", "created_at"]
    list_filter = ["group"]
    search_fields = ["id", "name"]

    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
