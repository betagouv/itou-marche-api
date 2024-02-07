from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from django.urls import reverse
from django.utils.html import format_html, mark_safe
from fieldsets_with_inlines import FieldsetsInlineMixin

from lemarche.notes.models import Note
from lemarche.siaes.models import Siae, SiaeUser
from lemarche.users.forms import UserChangeForm, UserCreationForm
from lemarche.users.models import User
from lemarche.utils.admin.admin_site import admin_site


class HasCompanyFilter(admin.SimpleListFilter):
    """Custom admin filter to target users who are linked to a Company."""

    title = "Rattaché à une entreprise ?"
    parameter_name = "has_company"

    def lookups(self, request, model_admin):
        return (("Yes", "Oui"), ("No", "Non"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.has_company()
        elif value == "No":
            return queryset.filter(company__isnull=True)
        return queryset


class HasSiaeFilter(admin.SimpleListFilter):
    """Custom admin filter to target users who are linked to a Siae."""

    title = "Gestionnaire de structure ?"
    parameter_name = "has_siae"

    def lookups(self, request, model_admin):
        return (("Yes", "Oui"), ("No", "Non"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.has_siae()
        elif value == "No":
            return queryset.filter(siaes__isnull=True)
        return queryset


class HasTenderFilter(admin.SimpleListFilter):
    """Custom admin filter to target users who have tenders."""

    title = "Besoin déposé ?"
    parameter_name = "has_tender"

    def lookups(self, request, model_admin):
        return (("Yes", "Oui"), ("No", "Non"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.has_tender()
        elif value == "No":
            return queryset.filter(tenders__isnull=True)
        return queryset


class HasFavoriteListFilter(admin.SimpleListFilter):
    """Custom admin filter to target users who have favorite lists."""

    title = "Listes d'achats favoris ?"
    parameter_name = "has_favorite_list"

    def lookups(self, request, model_admin):
        return (("Yes", "Oui"), ("No", "Non"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.has_favorite_list()
        elif value == "No":
            return queryset.filter(favorite_lists__isnull=True)
        return queryset


class HasPartnerNetworkFilter(admin.SimpleListFilter):
    """Custom admin filter to target users who have a partner_network."""

    title = "Partenaire avec réseau ?"
    parameter_name = "has_partner_network"

    def lookups(self, request, model_admin):
        return (("Yes", "Oui"), ("No", "Non"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.has_partner_network()
        elif value == "No":
            return queryset.filter(partner_network__isnull=True)
        return queryset


class HasApiKeyFilter(admin.SimpleListFilter):
    """Custom admin filter to target users who have a api_key."""

    title = "Clé API ?"
    parameter_name = "has_api_key"

    def lookups(self, request, model_admin):
        return (("Yes", "Oui"), ("No", "Non"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.has_api_key()
        elif value == "No":
            return queryset.filter(api_key__isnull=True)
        return queryset


class UserNoteInline(GenericTabularInline):
    model = Note
    fields = ["text", "author", "created_at", "updated_at"]
    readonly_fields = ["author", "created_at", "updated_at"]
    extra = 1

    formfield_overrides = {
        models.TextField: {"widget": CKEditorWidget(config_name="admin_note_text")},
    }


class SiaeUserInline(admin.TabularInline):
    model = SiaeUser
    fields = ["siae", "siae_with_link", "created_at", "updated_at"]
    autocomplete_fields = ["siae"]
    readonly_fields = ["siae_with_link", "created_at", "updated_at"]
    extra = 0

    def siae_with_link(self, siae_user):
        url = reverse("admin:siaes_siae_change", args=[siae_user.siae_id])
        return format_html(f'<a href="{url}">{siae_user.siae}</a>')

    siae_with_link.short_description = Siae._meta.verbose_name


@admin.register(User, site=admin_site)
class UserAdmin(FieldsetsInlineMixin, UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = [
        "id",
        "first_name",
        "last_name",
        "kind",
        "company_name",
        "siae_count_annotated_with_link",
        "tender_count_annotated_with_link",
        "last_login",
        "created_at",
    ]
    list_filter = [
        "kind",
        HasCompanyFilter,
        HasSiaeFilter,
        HasTenderFilter,
        "buyer_kind",
        "partner_kind",
        HasPartnerNetworkFilter,
        "can_display_tender_contact_details",
        HasFavoriteListFilter,
        HasApiKeyFilter,
        "is_staff",
        "is_superuser",
    ]
    search_fields = ["id", "email", "first_name", "last_name"]
    search_help_text = "Cherche sur les champs : ID, E-mail, Prénom, Nom"
    ordering = ["-created_at"]

    autocomplete_fields = ["company", "partner_network"]
    readonly_fields = (
        [field.name for field in User._meta.fields if field.name.startswith("c4_")]
        + [field for field in User.READONLY_FIELDS]
        + [
            "siae_count_annotated_with_link",
            "tender_count_annotated_with_link",
            "favorite_list_count_with_link",
            "image_url",
            "image_url_display",
            "extra_data",
        ]
    )

    fieldsets_with_inlines = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "kind",
                    "phone",
                    "company",
                    "company_name",
                    "position",
                    "buyer_kind",
                    "buyer_kind_detail",
                    "partner_kind",
                    "partner_network",
                )
            },
        ),
        UserNoteInline,
        SiaeUserInline,
        (
            "Dépôt de besoin",
            {
                "fields": (
                    "tender_count_annotated_with_link",
                    "can_display_tender_contact_details",
                ),
            },
        ),
        (
            "Listes d'achats favoris",
            {
                "fields": ("favorite_list_count_with_link",),
            },
        ),
        (
            "RGPD & co",
            {
                "fields": (
                    "accept_rgpd",
                    "accept_survey",
                    "accept_share_contact_to_external_partners",
                    "source",
                )
            },
        ),
        ("API", {"fields": ("api_key", "api_key_last_updated")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups")},
        ),
        (
            "Données C4 Cocorico",
            {
                "fields": (
                    "c4_id",
                    "c4_website",
                    "c4_siret",
                    "c4_naf",
                    "c4_phone_prefix",
                    "c4_time_zone",
                    "c4_phone_verified",
                    "c4_email_verified",
                    "c4_id_card_verified",
                    "image_url",
                    "image_url_display",
                )
            },
        ),
        ("Stats", {"fields": ("dashboard_last_seen_date", "tender_list_last_seen_date", "extra_data")}),
        (
            "Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "kind",
                    "phone",
                )
            },
        ),
        ("API", {"fields": ("api_key",)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.with_siae_stats()
        qs = qs.with_tender_stats()
        return qs

    def save_formset(self, request, form, formset, change):
        """
        Set Note author on create
        """
        for form in formset:
            if type(form.instance) is Note:
                if not form.instance.id and form.instance.text and change:
                    form.instance.author = request.user
        super().save_formset(request, form, formset, change)

    def siae_count_annotated_with_link(self, user):
        url = reverse("admin:siaes_siae_changelist") + f"?users__in={user.id}"
        return format_html(f'<a href="{url}">{getattr(user, "siae_count_annotated", 0)}</a>')

    siae_count_annotated_with_link.short_description = "Nombre de structures"
    siae_count_annotated_with_link.admin_order_field = "siae_count_annotated"

    def tender_count_annotated_with_link(self, user):
        url = reverse("admin:tenders_tender_changelist") + f"?author__id__exact={user.id}"
        return format_html(f'<a href="{url}">{getattr(user, "tender_count_annotated", 0)}</a>')

    tender_count_annotated_with_link.short_description = "Nombre de besoins déposés"
    tender_count_annotated_with_link.admin_order_field = "tender_count_annotated"

    def favorite_list_count_with_link(self, user):
        url = reverse("admin:favorites_favoritelist_changelist") + f"?users__in={user.id}"
        return format_html(f'<a href="{url}">{user.favorite_list_count}</a>')

    favorite_list_count_with_link.short_description = "Nombre de listes de favoris"
    favorite_list_count_with_link.admin_order_field = "favorite_list_count"

    def image_url_display(self, user):
        if user.image_url:
            return mark_safe(
                f'<a href="{user.image_url}" target="_blank">'
                f'<img src="{user.image_url}" title="{user.image_url}" style="max-height:300px" />'
                f"</a>"
            )
        return mark_safe("<div>-</div>")

    image_url_display.short_description = "Image"
