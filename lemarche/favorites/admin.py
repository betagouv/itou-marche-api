from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from fieldsets_with_inlines import FieldsetsInlineMixin

from lemarche.favorites.models import FavoriteItem, FavoriteList
from lemarche.utils.admin.admin_site import admin_site


class FavoriteItemInline(admin.TabularInline):
    model = FavoriteItem
    autocomplete_fields = ["siae"]
    readonly_fields = ["created_at", "updated_at"]
    extra = 0


@admin.register(FavoriteList, site=admin_site)
class FavoriteListAdmin(FieldsetsInlineMixin, admin.ModelAdmin):
    list_display = ["id", "name", "user_with_link", "siae_count_annotated_with_link", "created_at", "updated_at"]
    search_fields = ["id", "name", "slug", "user__id", "user__email"]
    search_help_text = "Cherche sur les champs : ID, Nom, Slug, Utilisateur (ID, E-mail)"

    autocomplete_fields = ["user"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]

    fieldsets_with_inlines = [
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                )
            },
        ),
        ("Utilisateur", {"fields": ("user",)}),
        FavoriteItemInline,
        ("Dates", {"fields": ("created_at", "updated_at")}),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.with_siae_stats()
        return qs

    def user_with_link(self, favorite_list):
        url = reverse("admin:users_user_change", args=[favorite_list.user_id])
        return format_html(f'<a href="{url}">{favorite_list.user}</a>')

    user_with_link.short_description = "Utilisateur"
    user_with_link.admin_order_field = "user"

    def siae_count_annotated_with_link(self, favorite_list):
        url = reverse("admin:siaes_siae_changelist") + f"?favorite_lists__in={favorite_list.id}"
        return format_html(f'<a href="{url}">{favorite_list.siae_count}</a>')

    siae_count_annotated_with_link.short_description = "Nombre de structures"
    siae_count_annotated_with_link.admin_order_field = "siae_count_annotated"
