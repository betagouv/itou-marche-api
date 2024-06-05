from django.contrib import admin

from lemarche.utils.admin.admin_site import admin_site

from .models import Datum


@admin.register(Datum, site=admin_site)
class DatumAdmin(admin.ModelAdmin):
    list_display = ["pk", "code", "bucket", "value", "measured_at"]
    list_filter = ["code"]
    ordering = ["-measured_at", "code"]
    date_hierarchy = "measured_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
