from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.edit import FormMixin
from formtools.wizard.views import SessionWizardView

from lemarche.siaes.models import Siae
from lemarche.tenders import constants as tender_constants
from lemarche.tenders.models import Tender, TenderSiae, TenderStepsData
from lemarche.users import constants as user_constants
from lemarche.users.models import User
from lemarche.utils.data import get_choice
from lemarche.utils.mixins import (
    SesameTenderAuthorRequiredMixin,
    SiaeUserRequiredOrSiaeIdParamMixin,
    TenderAuthorOrAdminRequiredIfNotSentMixin,
    TenderAuthorOrAdminRequiredMixin,
)
from lemarche.www.siaes.forms import SiaeFilterForm
from lemarche.www.tenders.forms import (
    TenderCreateStepConfirmationForm,
    TenderCreateStepContactForm,
    TenderCreateStepDetailForm,
    TenderCreateStepGeneralForm,
    TenderCreateStepSurveyForm,
    TenderSurveyTransactionedForm,
)
from lemarche.www.tenders.tasks import (  # , send_tender_emails_to_siaes
    notify_admin_siae_wants_cocontracting,
    notify_admin_tender_created,
    send_siae_interested_email_to_author,
)
from lemarche.www.tenders.utils import create_tender_from_dict, get_or_create_user, update_or_create_questions_list


TITLE_DETAIL_PAGE_SIAE = "Trouver de nouvelles opportunités"
TITLE_DETAIL_PAGE_OTHERS = "Mes besoins"
TITLE_KIND_SOURCING_SIAE = "Consultation en vue d'un achat"


class TenderCreateMultiStepView(SessionWizardView):
    """
    Multi-step Tender create form.
    Note: there is also some code in pages/views.py > csrf_failure to manage edge cases
    """

    instance = None
    success_url = reverse_lazy("siae:search_results")
    success_message = """
        <h3>Je suis Sofiane, votre conseiller chargé de vous accompagner sur votre {tender_kind}</h3>
        Votre besoin <strong>{tender_title}</strong> est bien pris en compte. <br /><br />
        Vous recevrez une notification par email dès que des prestataires seront identifiés ! <br /><br />
        À très vite
    """

    success_message_draft = """
        Votre besoin <strong>{tender_title}</strong> a été enregistré en brouillon.<br />
        Vous pourrez revenir plus tard pour le publier. Vous le retrouverez dans votre tableau de bord.
    """
    STEP_GENERAL = "general"
    STEP_DETAIL = "detail"
    STEP_CONTACT = "contact"
    STEP_SURVEY = "survey"
    STEP_CONFIRMATION = "confirmation"

    TEMPLATES = {
        STEP_GENERAL: "tenders/create_step_general.html",
        STEP_DETAIL: "tenders/create_step_detail.html",
        STEP_CONTACT: "tenders/create_step_contact.html",
        STEP_SURVEY: "tenders/create_step_survey.html",
        STEP_CONFIRMATION: "tenders/create_step_confirmation.html",
    }

    form_list = [
        (STEP_GENERAL, TenderCreateStepGeneralForm),
        (STEP_DETAIL, TenderCreateStepDetailForm),
        (STEP_CONTACT, TenderCreateStepContactForm),
        (STEP_SURVEY, TenderCreateStepSurveyForm),
        (STEP_CONFIRMATION, TenderCreateStepConfirmationForm),
    ]

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get(self, request, *args, **kwargs):
        """
        Manage case when slug is sent (Tender draft edition)
        """
        if "slug" in self.kwargs:
            self.instance = get_object_or_404(Tender, slug=self.kwargs.get("slug"))
            if self.instance.status != tender_constants.STATUS_DRAFT:
                return redirect("tenders:detail", slug=self.instance.slug)
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self, step):
        """
        Initial data
        """
        kwargs = super().get_form_kwargs(step)
        if step == self.STEP_DETAIL:
            kwargs["kind"] = self.get_cleaned_data_for_step(self.STEP_GENERAL).get("kind")
            if self.instance.id:
                kwargs["questions_list"] = list(self.instance.questions_list())
        if step == self.STEP_CONTACT:
            kwargs["external_link"] = self.get_cleaned_data_for_step(self.STEP_DETAIL).get("external_link")
            kwargs["user"] = self.request.user
        return kwargs

    def get_form_instance(self, step):
        """
        Manage case when slug is sent (Tender draft edition)
        """
        if "slug" in self.kwargs:
            self.instance = get_object_or_404(Tender, slug=self.kwargs.get("slug"))
        if self.instance is None:
            self.instance = Tender()
        return self.instance

    def get_context_data(self, form, **kwargs):
        """
        Pretty display of Tender at the last step
        """
        context = super().get_context_data(form=form, **kwargs)
        # needed to display the Tender preview template
        if self.steps.current == self.STEP_CONFIRMATION:
            tender_dict = self.get_all_cleaned_data()
            tender_dict["get_kind_display"] = get_choice(tender_constants.KIND_CHOICES, tender_dict["kind"])
            tender_dict["sectors_list_string"] = ", ".join(tender_dict["sectors"].values_list("name", flat=True))
            tender_dict["location_display"] = (
                Tender._meta.get_field("is_country_area").verbose_name
                if tender_dict["is_country_area"]
                else tender_dict["location"].name
            )
            tender_dict["get_amount_display"] = get_choice(
                tender_constants.AMOUNT_RANGE_CHOICES, tender_dict["amount"]
            )
            tender_dict["accept_share_amount_display"] = (
                tender_constants.ACCEPT_SHARE_AMOUNT_TRUE
                if tender_dict["accept_share_amount"]
                else tender_constants.ACCEPT_SHARE_AMOUNT_FALSE
            )
            context.update({"tender": tender_dict})
        return context

    def process_step(self, form):
        """
        Save step data
        """
        data = form.data.copy()
        if "csrfmiddlewaretoken" in data:
            del data["csrfmiddlewaretoken"]

        # Hide personal data
        for field_to_redacted in TenderStepsData.FIELDS_TO_REDACT:
            if field_to_redacted in data:
                data[field_to_redacted] = "[REDACTED]"

        data["timestamp"] = timezone.now().isoformat()

        uuid = self.request.session.get("tender_steps_data_uuid", None)
        if uuid:
            try:
                tender_steps_data = TenderStepsData.objects.get(uuid=uuid)
                tender_steps_data.steps_data.append(data)
                tender_steps_data.save()
            except TenderStepsData.DoesNotExist:
                tender_steps_data = TenderStepsData.objects.create(uuid=uuid, steps_data=[data])
        else:
            tender_steps_data = TenderStepsData.objects.create(steps_data=[data])
            self.request.session["tender_steps_data_uuid"] = tender_steps_data.uuid

        return form.data

    def save_instance_tender(self, tender_dict: dict, form_dict: dict, is_draft: bool):
        tender_status = tender_constants.STATUS_DRAFT if is_draft else tender_constants.STATUS_PUBLISHED
        tender_published_at = None if is_draft else timezone.now()

        if self.request.user.is_authenticated:
            tender_dict |= {
                "contact_first_name": self.request.user.first_name,
                "contact_last_name": self.request.user.last_name,
                "contact_email": self.request.user.email,
                "contact_phone": self.request.user.phone,
            }

        if self.instance.id:
            # update
            self.instance.status = tender_status
            self.instance.published_at = tender_published_at
            sectors = None
            for step, model_form in form_dict.items():
                if model_form.has_changed():
                    if step != self.STEP_SURVEY:
                        for attribute in model_form.changed_data:
                            match attribute:
                                case "sectors":
                                    sectors = tender_dict.get("sectors", None)
                                    self.instance.sectors.set(sectors)
                                case "location":
                                    location = tender_dict.get("location")
                                    self.instance.location = location
                                    self.instance.perimeters.set([location])
                                case "questions_list":
                                    update_or_create_questions_list(
                                        tender=self.instance, questions_list=tender_dict.get("questions_list")
                                    )
                                case _:
                                    setattr(self.instance, attribute, tender_dict.get(attribute))
                    elif step == self.STEP_SURVEY:
                        setattr(self.instance, "scale_marche_useless", tender_dict.get("scale_marche_useless"))
                        self.instance.extra_data.update(tender_dict.get("extra_data"))
            self.instance.save()
        else:
            tender_dict |= {"status": tender_status, "published_at": tender_published_at}
            self.instance = create_tender_from_dict(tender_dict)

    def done(self, _, form_dict, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        # anonymous user? create user (or get an existing user by email)
        user = get_or_create_user(
            self.request.user, tender_dict=cleaned_data, source=user_constants.SOURCE_TENDER_FORM
        )
        # when it's done we save the tender
        tender_dict = cleaned_data | {"author": user, "source": tender_constants.SOURCE_FORM}
        is_draft: bool = self.request.POST.get("is_draft", False)
        self.save_instance_tender(tender_dict=tender_dict, form_dict=form_dict, is_draft=is_draft)
        self.instance.set_siae_found_list()

        # remove steps data
        uuid = self.request.session.get("tender_steps_data_uuid", None)
        if uuid:
            TenderStepsData.objects.filter(uuid=uuid).delete()

        # we notify the admin team
        if settings.BITOUBI_ENV == "prod":
            notify_admin_tender_created(self.instance)

        # validation & siae contacted? in tenders/admin.py
        # success message & response
        if is_draft:
            messages.add_message(
                request=self.request,
                level=messages.INFO,
                message=self.get_success_message(cleaned_data, self.instance, is_draft=is_draft),
            )
        else:
            messages.add_message(
                request=self.request,
                level=messages.SUCCESS,
                message=self.get_success_message(cleaned_data, self.instance, is_draft=is_draft),
                extra_tags="modal_message_bizdev",
            )
        return redirect(self.get_success_url())

    def get_success_url(self):
        # if self.request.user.is_authenticated and not self.request.user.kind == User.KIND_SIAE:
        #     return reverse_lazy("tenders:list")  # super().get_success_url() doesn't work if called from CSRF error
        return reverse_lazy("siae:search_results")

    def get_success_message(self, cleaned_data, tender, is_draft):
        return mark_safe(
            self.success_message.format(tender_title=tender.title, tender_kind=tender.get_kind_display().lower())
            if not is_draft
            else self.success_message_draft.format(tender_title=tender.title)
        )


class TenderListView(LoginRequiredMixin, ListView):
    template_name = "tenders/list.html"
    model = Tender
    context_object_name = "tenders"
    paginate_by = 10
    paginator_class = Paginator
    status = None

    def get_queryset(self):
        """
        - show matching Tenders for Users KIND_SIAE
        - show owned Tenders for other Users
        """
        user = self.request.user
        qs = Tender.objects.none()
        if user.kind == User.KIND_SIAE and user.siaes:
            siaes = user.siaes.all()
            if siaes:
                # filtered prefetch to get detail_display_date on tendersiae_set related to user's siaes
                tendersiae_qs = TenderSiae.objects.filter(siae__in=siaes)
                qs = Tender.objects.filter_with_siaes(siaes).prefetch_related(
                    Prefetch("tendersiae_set", queryset=tendersiae_qs)
                )
        else:
            qs = Tender.objects.by_user(user).with_siae_stats()
            if self.status:
                qs = qs.filter(status=self.status)
        qs = qs.prefetch_many_to_many().select_foreign_keys()
        qs = qs.order_by_deadline_date()
        return qs

    def get(self, request, status=None, *args, **kwargs):
        """
        - set status
        - update 'tender_list_last_seen_date'
        """
        user = self.request.user
        self.status = status
        if user.is_authenticated:
            User.objects.filter(id=user.id).update(tender_list_last_seen_date=timezone.now())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_kind = self.request.user.kind if self.request.user.is_authenticated else "anonymous"
        context["page_title"] = TITLE_DETAIL_PAGE_SIAE if user_kind == User.KIND_SIAE else TITLE_DETAIL_PAGE_OTHERS
        context["title_kind_sourcing_siae"] = TITLE_KIND_SOURCING_SIAE
        context["tender_constants"] = tender_constants
        return context


class TenderDetailView(TenderAuthorOrAdminRequiredIfNotSentMixin, DetailView):
    model = Tender
    template_name = "tenders/detail.html"
    context_object_name = "tender"

    def get(self, request, *args, **kwargs):
        """
        - update 'email_link_click_date' (if ?siae_id in the URL)
        - update 'detail_display_date' (if the User has any Siae linked to this Tender)
        """
        self.object = self.get_object()
        user = self.request.user
        self.siae_id = request.GET.get("siae_id", None)
        # update 'email_link_click_date'
        if self.siae_id:
            TenderSiae.objects.filter(tender=self.object, siae_id=self.siae_id, email_link_click_date=None).update(
                email_link_click_date=timezone.now(), updated_at=timezone.now()
            )
        # update 'detail_display_date'
        if user.is_authenticated:
            if user.kind == User.KIND_SIAE:
                # user might not be concerned with this tender: we create TenderSiae stats
                if not user.has_tender_siae(self.object):
                    for siae in user.siaes.all():
                        TenderSiae.objects.create(
                            tender=self.object, siae=siae, source=TenderSiae.TENDER_SIAE_SOURCE_LINK
                        )
                # update stats
                TenderSiae.objects.filter(
                    tender=self.object, siae__in=user.siaes.all(), detail_display_date__isnull=True
                ).update(detail_display_date=timezone.now(), updated_at=timezone.now())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """ """
        context = super().get_context_data(**kwargs)
        # init
        user = self.request.user
        user_kind = user.kind if user.is_authenticated else "anonymous"
        show_nps = self.request.GET.get("nps", None)
        # enrich context
        context["is_admin"] = self.request.user.is_authenticated and self.request.user.is_admin
        context["parent_title"] = TITLE_DETAIL_PAGE_SIAE if user_kind == User.KIND_SIAE else TITLE_DETAIL_PAGE_OTHERS
        context["tender_kind_display"] = (
            TITLE_KIND_SOURCING_SIAE
            if user_kind == User.KIND_SIAE and self.object.kind == tender_constants.KIND_PROJECT
            else self.object.get_kind_display()
        )
        if self.siae_id:
            context["siae_id"] = self.siae_id
            context["siae_has_detail_contact_click_date"] = TenderSiae.objects.filter(
                tender=self.object, siae_id=int(self.siae_id), detail_contact_click_date__isnull=False
            ).exists()
            context["siae_has_detail_not_interested_click_date"] = TenderSiae.objects.filter(
                tender=self.object, siae_id=int(self.siae_id), detail_not_interested_click_date__isnull=False
            ).exists()
        if user.is_authenticated:
            if user.kind == User.KIND_SIAE:
                context["siae_has_detail_contact_click_date"] = (
                    getattr(context, "siae_has_detail_contact_click_date", None)
                    or TenderSiae.objects.filter(
                        tender=self.object, siae__in=user.siaes.all(), detail_contact_click_date__isnull=False
                    ).exists()
                )
                context["siae_has_detail_not_interested_click_date"] = (
                    getattr(context, "siae_has_detail_not_interested_click_date", None)
                    or TenderSiae.objects.filter(
                        tender=self.object, siae__in=user.siaes.all(), detail_not_interested_click_date__isnull=False
                    ).exists()
                )
                if show_nps:
                    context["show_nps"] = True
            elif user.kind == User.KIND_PARTNER:
                context["user_partner_can_display_tender_contact_details"] = user.can_display_tender_contact_details
            else:
                pass
        return context


class TenderDetailContactClickStatView(SiaeUserRequiredOrSiaeIdParamMixin, UpdateView):
    """
    Endpoint to track 'interested' button click
    We might also send a notification to the buyer
    """

    template_name = "tenders/_detail_contact_click_confirm_modal.html"
    model = Tender

    def get_object(self):
        return get_object_or_404(Tender, slug=self.kwargs.get("slug"))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.request.user
        detail_contact_click_confirm = self.request.POST.get("detail_contact_click_confirm", False) == "true"
        siae_id = request.GET.get("siae_id", None)
        if (user.is_authenticated and user.kind == User.KIND_SIAE) or siae_id:
            if detail_contact_click_confirm:
                # update detail_contact_click_date
                if user.is_authenticated:
                    TenderSiae.objects.filter(
                        tender=self.object, siae__in=user.siaes.all(), detail_contact_click_date__isnull=True
                    ).update(detail_contact_click_date=timezone.now(), updated_at=timezone.now())
                else:
                    TenderSiae.objects.filter(
                        tender=self.object, siae_id=int(siae_id), detail_contact_click_date__isnull=True
                    ).update(detail_contact_click_date=timezone.now(), updated_at=timezone.now())
                # notify the tender author
                send_siae_interested_email_to_author(self.object)
                messages.add_message(
                    self.request, messages.SUCCESS, self.get_success_message(detail_contact_click_confirm)
                )
            else:
                messages.add_message(
                    self.request, messages.WARNING, self.get_success_message(detail_contact_click_confirm)
                )
            # redirect
            return HttpResponseRedirect(self.get_success_url(detail_contact_click_confirm, siae_id))
        else:
            return HttpResponseForbidden()

    def get_success_url(self, detail_contact_click_confirm, siae_id=None):
        success_url = reverse_lazy("tenders:detail", args=[self.kwargs.get("slug")])
        if detail_contact_click_confirm:
            success_url += "?nps=true"
            if siae_id:
                success_url += f"&siae_id={siae_id}"
        return success_url

    def get_success_message(self, detail_contact_click_confirm):
        if detail_contact_click_confirm:
            return "<strong>Bravo !</strong><br />Vos coordonnées, ainsi que le lien vers votre fiche commerciale ont été transmis à l'acheteur. Assurez-vous d'avoir une fiche commerciale bien renseignée."  # noqa
        return f"<strong>{self.object.cta_card_button_text}</strong><br />Pour {self.object.cta_card_button_text.lower()}, vous devez accepter d'être mis en relation avec l'acheteur."  # noqa


class TenderDetailCocontractingClickView(SiaeUserRequiredOrSiaeIdParamMixin, DetailView):
    """
    Endpoint to handle 'cocontracting' button click
    """

    template_name = "tenders/_detail_cocontracting_click_confirm.html"
    model = Tender

    def get_object(self):
        return get_object_or_404(Tender, slug=self.kwargs.get("slug"))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.request.user

        if self.request.user.is_authenticated:
            siae = user.siaes.first()
        else:
            siae = Siae.objects.filter(pk=self.request.GET.get("siae_id", None)).first()

        if siae:
            # save the datetime of this action
            TenderSiae.objects.filter(
                tender=self.object, siae=siae, detail_cocontracting_click_date__isnull=True
            ).update(detail_cocontracting_click_date=timezone.now(), updated_at=timezone.now())

            notify_admin_siae_wants_cocontracting(self.object, siae)
        else:
            self.template_name = "tenders/_detail_cocontracting_click_error.html"

        return self.get(request)


class TenderDetailNotInterestedClickView(SiaeUserRequiredOrSiaeIdParamMixin, DetailView):
    """
    Endpoint to handle 'not interested' button click
    """

    template_name = "tenders/_detail_not_interested_click_confirm.html"
    model = Tender

    def get_object(self):
        return get_object_or_404(Tender, slug=self.kwargs.get("slug"))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.request.user

        if self.request.user.is_authenticated:
            siae = user.siaes.first()
        else:
            siae = Siae.objects.filter(pk=self.request.GET.get("siae_id", None)).first()

        if siae:
            # save the datetime of this action
            TenderSiae.objects.filter(
                tender=self.object, siae=siae, detail_not_interested_click_date__isnull=True
            ).update(
                detail_not_interested_feedback=self.request.POST.get("detail_not_interested_feedback", ""),
                detail_not_interested_click_date=timezone.now(),
                updated_at=timezone.now(),
            )
        else:
            self.template_name = "tenders/_detail_not_interested_click_error.html"

        return self.get(request)


class TenderSiaeListView(TenderAuthorOrAdminRequiredMixin, FormMixin, ListView):
    template_name = "tenders/siae_interested_list.html"
    form_class = SiaeFilterForm
    queryset = Siae.objects.prefetch_related("tendersiae_set").all()
    context_object_name = "siaes"
    status = None

    def get_queryset(self):
        qs = super().get_queryset()
        # first get the tender's siaes
        self.tender = Tender.objects.get(slug=self.kwargs.get("slug"))
        qs = qs.filter_with_tender(tender=self.tender, tender_status=self.status)
        # then filter with the form
        self.filter_form = SiaeFilterForm(data=self.request.GET)
        qs = self.filter_form.filter_queryset(qs)
        return qs

    def get(self, request, status="ALL", *args, **kwargs):
        """
        - set status
        - update 'siae_list_last_seen_date'
        """
        self.status = status
        Tender.objects.filter(slug=self.kwargs.get("slug")).update(siae_list_last_seen_date=timezone.now())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tender"] = self.tender
        context["status"] = self.status
        siae_search_form = self.filter_form if self.filter_form else SiaeFilterForm(data=self.request.GET)
        context["form"] = siae_search_form
        context["current_search_query"] = self.request.GET.urlencode()
        if len(self.request.GET.keys()):
            if siae_search_form.is_valid():
                current_locations = siae_search_form.cleaned_data.get("locations")
                if current_locations:
                    context["current_locations"] = list(current_locations.values("id", "slug", "name"))
        return context


class TenderDetailSurveyTransactionedView(SesameTenderAuthorRequiredMixin, UpdateView):
    """
    Endpoint to store the tender author survey transactioned answer
    """

    template_name = "tenders/survey_transactioned_detail.html"
    form_class = TenderSurveyTransactionedForm
    queryset = Tender.objects.all()
    # success_message (see get_success_message() below)
    # success_url (see get_success_url() below)

    def get(self, request, *args, **kwargs):
        """
        Tender.survey_transactioned_answer field is updated only if:
        - the user should be the tender author (thanks to SesameTenderAuthorRequiredMixin)
        - the field is None in the database (first time answering)
        - the GET parameter 'answer' is passed
        """
        self.object = self.get_object()
        survey_transactioned_answer = request.GET.get("answer", None)
        # first time answering
        if self.object.survey_transactioned_answer is None:
            if survey_transactioned_answer in ["True", "False"]:
                # transform survey_transactioned_answer into bool
                survey_transactioned_answer = survey_transactioned_answer == "True"
                # update survey_transactioned_answer
                Tender.objects.filter(id=self.object.id).update(
                    survey_transactioned_answer=survey_transactioned_answer,
                    survey_transactioned_answer_date=timezone.now(),
                    siae_transactioned=survey_transactioned_answer,
                    updated_at=timezone.now(),
                )
            else:
                pass
                # TODO or not? "answer" should always be passed
            return super().get(request, *args, **kwargs)
        # already answered
        else:
            messages.add_message(self.request, messages.WARNING, self.get_success_message(already_answered=True))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tender"] = self.object
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tender_survey_transactioned_answer"] = self.object.survey_transactioned_answer
        return kwargs

    def form_valid(self, form):
        super().form_valid(form)
        messages.add_message(self.request, messages.SUCCESS, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        success_url = reverse_lazy("tenders:detail", args=[self.kwargs.get("slug")])
        return success_url

    def get_success_message(self, already_answered=False):
        if already_answered:
            return "Votre réponse a déjà été prise en compte."
        return "Merci pour votre réponse !"
