from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django_admin_filters import MultiChoice
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from fieldsets_with_inlines import FieldsetsInlineMixin

from lemarche.notes.models import Note
from lemarche.perimeters.admin import PerimeterRegionFilter
from lemarche.tenders import constants as tender_constants
from lemarche.tenders.forms import TenderAdminForm
from lemarche.tenders.models import PartnerShareTender, Tender, TenderQuestion, TenderStepsData
from lemarche.utils.admin.admin_site import admin_site
from lemarche.utils.fields import ChoiceArrayField, pretty_print_readonly_jsonfield
from lemarche.www.tenders.tasks import restart_send_tender_task


class KindFilter(MultiChoice):
    FILTER_LABEL = Tender._meta.get_field("kind").verbose_name
    BUTTON_LABEL = "Appliquer"


class ScaleMarcheUselessFilter(MultiChoice):
    FILTER_LABEL = Tender._meta.get_field("scale_marche_useless").verbose_name
    BUTTON_LABEL = "Appliquer"


class SourceFilter(MultiChoice):
    FILTER_LABEL = Tender._meta.get_field("source").verbose_name
    BUTTON_LABEL = "Appliquer"


class HasAmountFilter(admin.SimpleListFilter):
    title = "Montant renseigné ?"
    parameter_name = "has_amount"

    def lookups(self, request, model_admin):
        return (("Yes", "Oui"), ("No", "Non"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.has_amount()
        elif value == "No":
            return queryset.filter(amount__isnull=True, amount_exact__isnull=True)
        return queryset


class AmountFilter(MultiChoice):
    FILTER_LABEL = Tender._meta.get_field("amount").verbose_name
    BUTTON_LABEL = "Appliquer"


class ResponseKindFilter(admin.SimpleListFilter):
    title = Tender._meta.get_field("response_kind").verbose_name
    parameter_name = "response_kind"

    def lookups(self, request, model_admin):
        return tender_constants.RESPONSE_KIND_CHOICES

    def queryset(self, request, queryset):
        lookup_value = self.value()
        if lookup_value:
            queryset = queryset.filter(response_kind__contains=[lookup_value])
        return queryset


class TenderNoteInline(GenericTabularInline):
    model = Note
    fields = ["text", "author", "created_at", "updated_at"]
    readonly_fields = ["author", "created_at", "updated_at"]
    extra = 1

    formfield_overrides = {
        models.TextField: {"widget": CKEditorWidget(config_name="admin_note_text")},
    }


class TenderQuestionInline(admin.TabularInline):
    model = TenderQuestion
    fields = ["text", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
    extra = 0


@admin.register(Tender, site=admin_site)
class TenderAdmin(FieldsetsInlineMixin, admin.ModelAdmin):
    list_display = [
        "id",
        "status",
        "is_validated_or_sent",
        "title",
        "user_with_link",
        "kind",
        "deadline_date",
        "start_working_date",
        "siae_count_annotated_with_link",
        # "siae_email_send_count_annotated_with_link",
        "siae_email_link_click_count_annotated_with_link",
        "siae_detail_display_count_annotated_with_link",
        # "siae_email_link_click_or_detail_display_count_annotated_with_link",
        "siae_detail_contact_click_count_annotated_with_link",
        "siae_transactioned",
        "created_at",
        "validated_at",
        "sent_at",
    ]

    list_filter = [
        ("kind", KindFilter),
        "status",
        ("scale_marche_useless", ScaleMarcheUselessFilter),
        ("source", SourceFilter),
        HasAmountFilter,
        ("amount", AmountFilter),
        "deadline_date",
        "start_working_date",
        ResponseKindFilter,
        "siae_transactioned",
    ]
    advanced_filter_fields = (
        "kind",
        "status",
        "scale_marche_useless",
        "deadline_date",
        "start_working_date",
    )
    # filter on "perimeters"? (loads ALL the perimeters... Use django-admin-autocomplete-filter instead?)
    search_fields = ["id", "title", "slug", "author__id", "author__email"]
    search_help_text = "Cherche sur les champs : ID, Titre, Slug, Auteur (ID, E-mail)"
    ordering = ["-created_at"]

    autocomplete_fields = ["sectors", "location", "perimeters", "author"]
    readonly_fields = [field.name for field in Tender._meta.fields if field.name.endswith("_last_seen_date")] + [
        # slug
        # status
        "survey_transactioned_send_date",
        "survey_transactioned_answer",
        "survey_transactioned_amount",
        "survey_transactioned_feedback",
        "survey_transactioned_answer_date",
        "validated_at",
        "sent_at",
        "question_count_with_link",
        "siae_count_annotated_with_link",
        "siae_email_send_count_annotated_with_link",
        "siae_email_link_click_count_annotated_with_link",
        "siae_detail_display_count_annotated_with_link",
        "siae_email_link_click_or_detail_display_count_annotated_with_link",
        "siae_detail_contact_click_count_annotated_with_link",
        "logs_display",
        "extra_data_display",
        "source",
        # "import_raw_object",
        "import_raw_object_display",
        "created_at",
        "published_at",
        "updated_at",
    ]
    formfield_overrides = {
        models.TextField: {"widget": CKEditorWidget},
        ChoiceArrayField: {"widget": forms.CheckboxSelectMultiple(attrs={"class": "custom-checkbox-select-multiple"})},
    }

    fieldsets_with_inlines = [
        (
            None,
            {
                "fields": ("title", "slug", "kind"),
            },
        ),
        TenderNoteInline,
        (
            "Détails",
            {
                "fields": (
                    "description",
                    "constraints",
                    "external_link",
                    "accept_cocontracting",
                    "question_count_with_link",
                ),
            },
        ),
        TenderQuestionInline,
        (
            "Filtres",
            {
                "fields": (
                    "siae_kind",
                    "sectors",
                    "presta_type",
                )
            },
        ),
        (
            "Lieux d'exécution 'France entière'",
            {
                "fields": ("is_country_area",),
            },
        ),
        (
            "Lieux d'exécution 'spécifique'",
            {
                "fields": (
                    "location",
                    "perimeters",
                    "distance_location",
                    "include_country_area",
                ),
            },
        ),
        (
            "Montant",
            {
                "fields": (
                    "amount",
                    "why_amount_is_blank",
                    "accept_share_amount",
                    "amount_exact",
                    "incremental_custom",
                ),
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "deadline_date",
                    "start_working_date",
                ),
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "author",
                    "contact_first_name",
                    "contact_last_name",
                    "contact_company_name",
                    "contact_email",
                    "contact_phone",
                    "response_kind",
                    "response_is_anonymous",
                ),
            },
        ),
        (
            "Structures",
            {
                "fields": (
                    "siae_count_annotated_with_link",
                    "siae_email_send_count_annotated_with_link",
                    "siae_email_link_click_count_annotated_with_link",
                    "siae_detail_display_count_annotated_with_link",
                    "siae_email_link_click_or_detail_display_count_annotated_with_link",
                    "siae_detail_contact_click_count_annotated_with_link",
                )
            },
        ),
        (
            "Transaction ?",
            {
                "fields": (
                    "survey_transactioned_send_date",
                    "survey_transactioned_answer",
                    "survey_transactioned_amount",
                    "survey_transactioned_feedback",
                    "survey_transactioned_answer_date",
                    "siae_transactioned",
                )
            },
        ),
        (
            "Utilité du marché de l'inclusion",
            {
                "fields": (
                    "scale_marche_useless",
                    "marche_benefits",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "published_at",
                    "validated_at",
                    "sent_at",
                )
            },
        ),
        (
            "Stats",
            {
                "fields": (
                    "siae_list_last_seen_date",
                    "source",
                    "logs_display",
                    "extra_data_display",
                ),
            },
        ),
        ("Si importé", {"fields": ("import_raw_object_display",)}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    ]

    change_form_template = "tenders/admin_change_form.html"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.with_siae_stats()
        # qs = qs.with_question_stats()  # doesn't work when chaining these 2 querysets: adds duplicates...
        return qs

    def get_changeform_initial_data(self, request):
        """
        Default values in add form.
        """
        return {"source": tender_constants.SOURCE_STAFF_C4_CREATED}

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in [
            "tendersiae__email_send_date__isnull",
            "tendersiae__email_link_click_date__isnull",
            "tendersiae__detail_display_date__isnull",
            "tendersiae__detail_contact_click_date__isnull",
        ]:
            return True
        return super().lookup_allowed(lookup, *args, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:
            # add status in read only when the tender is not owned by the current user
            if obj.author_id and obj.author_id != request.user.id:
                readonly_fields.append("status")
            # slug cannot be changed once the tender is validated
            if obj.status == tender_constants.STATUS_VALIDATED:
                readonly_fields.append("slug")
        return readonly_fields

    def save_model(self, request, obj: Tender, form, change):
        """
        Set Tender author on create
        """
        if not obj.id and not obj.author_id:
            obj.author = request.user
        obj.save()

    def save_related(self, request, form, formsets, change):
        super().save_related(request=request, form=form, formsets=formsets, change=change)
        tender: Tender = form.instance
        # we can add `and obj.status != obj.STATUS_DRAFT` to disable matching when is draft
        if not tender.is_validated_or_sent:
            tender.set_siae_found_list()

    def save_formset(self, request, form, formset, change):
        """
        Set Note author on create
        """
        for form in formset:
            if type(form.instance) is Note:
                if not form.instance.id and form.instance.text and change:
                    form.instance.author = request.user
        super().save_formset(request, form, formset, change)

    def is_validated_or_sent(self, tender: Tender):
        return tender.is_validated_or_sent

    is_validated_or_sent.boolean = True
    is_validated_or_sent.short_description = "Validé / Envoyé"

    def user_with_link(self, tender):
        url = reverse("admin:users_user_change", args=[tender.author_id])
        return format_html(f'<a href="{url}">{tender.author}</a>')

    user_with_link.short_description = "Auteur"
    user_with_link.admin_order_field = "author"

    def question_count_with_link(self, tender):
        url = reverse("admin:tenders_tenderquestion_changelist") + f"?tender__in={tender.id}"
        return format_html(f'<a href="{url}">{tender.questions.count()}</a>')

    question_count_with_link.short_description = TenderQuestion._meta.verbose_name_plural

    def siae_count_annotated_with_link(self, tender):
        url = reverse("admin:siaes_siae_changelist") + f"?tenders__in={tender.id}"
        return format_html(f'<a href="{url}">{getattr(tender, "siae_count_annotated", 0)}</a>')

    siae_count_annotated_with_link.short_description = "S. concernées"
    siae_count_annotated_with_link.admin_order_field = "siae_count_annotated"

    def siae_email_send_count_annotated_with_link(self, tender):
        url = (
            reverse("admin:siaes_siae_changelist")
            + f"?tenders__in={tender.id}&tendersiae__email_send_date__isnull=False"
        )
        return format_html(f'<a href="{url}">{getattr(tender, "siae_email_send_count_annotated", 0)}</a>')

    siae_email_send_count_annotated_with_link.short_description = "S. contactées"
    siae_email_send_count_annotated_with_link.admin_order_field = "siae_email_send_count_annotated"

    def siae_email_link_click_count_annotated_with_link(self, tender):
        url = (
            reverse("admin:siaes_siae_changelist")
            + f"?tenders__in={tender.id}&tendersiae__email_link_click_date__isnull=False"
        )
        return format_html(f'<a href="{url}">{getattr(tender, "siae_email_link_click_count_annotated", 0)}</a>')

    siae_email_link_click_count_annotated_with_link.short_description = "S. cliquées"
    siae_email_link_click_count_annotated_with_link.admin_order_field = "siae_email_link_click_count_annotated"

    def siae_detail_display_count_annotated_with_link(self, tender):
        url = (
            reverse("admin:siaes_siae_changelist")
            + f"?tenders__in={tender.id}&tendersiae__detail_display_date__isnull=False"
        )
        return format_html(f'<a href="{url}">{getattr(tender, "siae_detail_display_count_annotated", 0)}</a>')

    siae_detail_display_count_annotated_with_link.short_description = "S. vues"
    siae_detail_display_count_annotated_with_link.admin_order_field = "siae_detail_display_count_annotated"

    def siae_email_link_click_or_detail_display_count_annotated_with_link(self, tender):
        url = (
            reverse("admin:siaes_siae_changelist")
            + f"?tenders__in={tender.id}&tendersiae__detail_display_date__isnull=False"
        )
        return format_html(
            f'<a href="{url}">{getattr(tender, "siae_email_link_click_or_detail_display_count_annotated", 0)}</a>'
        )

    siae_email_link_click_or_detail_display_count_annotated_with_link.short_description = "S. cliquées ou vues"
    siae_email_link_click_or_detail_display_count_annotated_with_link.admin_order_field = (
        "siae_email_link_click_or_detail_display_count_annotated"
    )

    def siae_detail_contact_click_count_annotated_with_link(self, tender):
        url = (
            reverse("admin:siaes_siae_changelist")
            + f"?tenders__in={tender.id}&tendersiae__detail_contact_click_date__isnull=False"
        )
        return format_html(f'<a href="{url}">{getattr(tender, "siae_detail_contact_click_count_annotated", 0)}</a>')

    siae_detail_contact_click_count_annotated_with_link.short_description = "S. intéressées"
    siae_detail_contact_click_count_annotated_with_link.admin_order_field = "siae_detail_contact_click_count_annotated"

    def logs_display(self, tender=None):
        if tender:
            return pretty_print_readonly_jsonfield(tender.logs)
        return "-"

    logs_display.short_description = Tender._meta.get_field("logs").verbose_name

    def response_change(self, request, obj: Tender):
        """
        Catch submit of custom admin button to Validate or Resend Tender
        """
        if request.POST.get("_validate_tender"):
            obj.set_validated()
            self.message_user(request, "Ce dépôt de besoin a été validé. Il sera envoyé en temps voulu :)")
            return HttpResponseRedirect(".")
        elif request.POST.get("_restart_tender"):
            restart_send_tender_task(tender=obj)
            self.message_user(request, "Ce dépôt de besoin a été renvoyé aux structures")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    def extra_data_display(self, instance: Tender = None):
        if instance:
            return pretty_print_readonly_jsonfield(instance.extra_data)
        return "-"

    extra_data_display.short_description = Tender._meta.get_field("extra_data").verbose_name

    def import_raw_object_display(self, instance: Tender = None):
        if instance:
            return pretty_print_readonly_jsonfield(instance.import_raw_object)
        return "-"

    import_raw_object_display.short_description = Tender._meta.get_field("import_raw_object").verbose_name


@admin.register(TenderQuestion, site=admin_site)
class TenderQuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "text", "tender_with_link", "created_at"]
    search_fields = ["id", "text", "tender__id", "tender__name"]
    search_help_text = "Cherche sur les champs : ID, Texte, Besoin (ID, Titre)"

    autocomplete_fields = ["tender"]
    readonly_fields = ["created_at", "updated_at"]

    def tender_with_link(self, tender_question):
        url = reverse("admin:tenders_tender_change", args=[tender_question.tender_id])
        return format_html(f'<a href="{url}">{tender_question.tender}</a>')

    tender_with_link.short_description = "Besoin d'achat"
    tender_with_link.admin_order_field = "tender"


class PartnerShareTenderNoteInline(GenericTabularInline):
    model = Note
    fields = ["text", "author", "created_at", "updated_at"]
    readonly_fields = ["author", "created_at", "updated_at"]
    extra = 1

    formfield_overrides = {
        models.TextField: {"widget": CKEditorWidget(config_name="admin_note_text")},
    }


@admin.register(PartnerShareTender, site=admin_site)
class PartnerShareTenderAdmin(FieldsetsInlineMixin, admin.ModelAdmin, DynamicArrayMixin):
    form = TenderAdminForm
    list_display = ["id", "name", "perimeters_string", "amount_in", "created_at"]
    list_filter = [PerimeterRegionFilter, "amount_in"]
    search_fields = ["id", "name", "contact_email_list"]
    search_help_text = "Cherche sur les champs : ID, Nom, Contact (E-mail)"

    readonly_fields = ["perimeters_string", "logs_display", "created_at", "updated_at"]
    autocomplete_fields = ["perimeters"]

    fieldsets_with_inlines = [
        (
            None,
            {
                "fields": ("name", "perimeters", "amount_in", "contact_email_list"),
            },
        ),
        TenderNoteInline,
        (
            "Stats",
            {
                "fields": ("logs_display",),
            },
        ),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("perimeters")
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

    def perimeters_string(self, partnersharetender):
        return partnersharetender.perimeters_list_string

    perimeters_string.short_description = "Périmètres"

    def logs_display(self, partnersharetender=None):
        if partnersharetender:
            return pretty_print_readonly_jsonfield(partnersharetender.logs)
        return "-"

    logs_display.short_description = PartnerShareTender._meta.get_field("logs").verbose_name


@admin.register(TenderStepsData, site=admin_site)
class TenderStepsDataAdmin(admin.ModelAdmin):
    list_display = ["created_at", "updated_at", "uuid"]

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "uuid",
        "steps_data_display",
    ]

    def steps_data_display(self, tender_steps_data: TenderStepsData = None):
        if tender_steps_data:
            return pretty_print_readonly_jsonfield(tender_steps_data.steps_data)
        return "-"

    steps_data_display.short_description = "Données saisies dans les étapes"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
