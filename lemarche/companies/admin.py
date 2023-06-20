from django.contrib import admin
from django.utils.html import mark_safe

from lemarche.companies.models import Company
from lemarche.utils.admin.admin_site import admin_site


@admin.register(Company, site=admin_site)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "created_at"]
    search_fields = ["id", "name"]
    search_help_text = "Cherche sur les champs : ID, Nom"

    readonly_fields = ["logo_url_display", "created_at", "updated_at"]

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "slug", "description", "siret", "website"),
            },
        ),
        ("Logo", {"fields": ("logo_url", "logo_url_display")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )

    def get_readonly_fields(self, request, obj=None):
        # slug cannot be changed (to avoid query errors)
        if obj:
            return self.readonly_fields + ["slug"]
        return self.readonly_fields

    def get_prepopulated_fields(self, request, obj=None):
        # set slug on create
        if not obj:
            return {"slug": ("name",)}
        return {}

    def logo_url_display(self, instance):
        if instance.logo_url:
            return mark_safe(
                f'<a href="{instance.logo_url}" target="_blank">'
                f'<img src="{instance.logo_url}" title="{instance.logo_url}" style="max-height:300px" />'
                f"</a>"
            )
        return mark_safe("<div>-</div>")

    logo_url_display.short_description = "Logo"
