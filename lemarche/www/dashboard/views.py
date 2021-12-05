from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.edit import FormMixin

from lemarche.siaes.models import Siae
from lemarche.utils.s3 import S3Upload
from lemarche.utils.tracker import extract_meta_from_request, track
from lemarche.www.dashboard.forms import (
    ProfileEditForm,
    SiaeClientReferenceFormSet,
    SiaeEditInfoContactForm,
    SiaeEditOfferForm,
    SiaeEditOtherForm,
    SiaeEditPrestaForm,
    SiaeImageFormSet,
    SiaeLabelFormSet,
    SiaeOfferFormSet,
    SiaeSearchAdoptConfirmForm,
    SiaeSearchBySiretForm,
)
from lemarche.www.dashboard.mixins import SiaeOwnerRequiredMixin, SiaeUserRequiredMixin


class DashboardHomeView(LoginRequiredMixin, DetailView):
    template_name = "dashboard/home.html"
    context_object_name = "user"

    def get_object(self):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = ProfileEditForm
    template_name = "dashboard/profile_edit.html"
    success_message = "Votre profil a été mis à jour."
    success_url = reverse_lazy("dashboard:home")

    def get_object(self):
        return self.request.user


class SiaeSearchBySiretView(LoginRequiredMixin, SiaeUserRequiredMixin, FormMixin, ListView):
    form_class = SiaeSearchBySiretForm
    template_name = "dashboard/siae_search_by_siret.html"
    context_object_name = "siaes"

    def get_queryset(self):
        """Filter results."""
        filter_form = SiaeSearchBySiretForm(data=self.request.GET)
        results = filter_form.filter_queryset()
        return results

    def get_context_data(self, **kwargs):
        """
        - initialize the form with the query parameters (only if they are present)
        """
        context = super().get_context_data(**kwargs)
        if len(self.request.GET.keys()):
            context["form"] = SiaeSearchBySiretForm(data=self.request.GET)
        return context

    def get(self, request, *args, **kwargs):
        # Track adopt search event
        track(
            "backend",
            "adopt_search",
            meta=extract_meta_from_request(self.request),
            session_id=request.COOKIES.get("sessionid", None),
        )
        return super().get(request, *args, **kwargs)


class SiaeSearchAdoptConfirmView(LoginRequiredMixin, SiaeUserRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = SiaeSearchAdoptConfirmForm
    template_name = "dashboard/siae_search_adopt_confirm.html"
    context_object_name = "siae"
    queryset = Siae.objects.all()
    success_message = "Votre structure a été rajoutée dans votre espace."
    success_url = reverse_lazy("dashboard:home")

    def get(self, request, *args, **kwargs):
        """The Siae should not have any users yet."""
        response = super().get(request, *args, **kwargs)
        if self.object.users.count():
            messages.add_message(
                request, messages.INFO, "La structure a déjà été enregistrée sur le marché par un autre utilisateur."
            )
            return HttpResponseRedirect(reverse_lazy("dashboard:home"))
        return response

    def form_valid(self, form):
        """Add the Siae to the User."""
        self.object.users.add(self.request.user)
        return super().form_valid(form)


class SiaeEditInfoContactView(LoginRequiredMixin, SiaeOwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = SiaeEditInfoContactForm
    template_name = "dashboard/siae_edit_info_contact.html"
    context_object_name = "siae"
    queryset = Siae.objects.all()
    success_message = "Vos modifications ont bien été prises en compte."

    def get_context_data(self, **kwargs):
        """
        - pass s3 image upload config
        """
        context = super().get_context_data(**kwargs)
        s3_upload = S3Upload(kind="siae_logo")
        context["s3_form_values"] = s3_upload.form_values
        context["s3_upload_config"] = s3_upload.config
        return context

    def get_success_url(self):
        return reverse_lazy("dashboard:siae_edit_info_contact", args=[self.kwargs.get("slug")])


class SiaeEditOfferView(LoginRequiredMixin, SiaeOwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = SiaeEditOfferForm
    template_name = "dashboard/siae_edit_offer.html"
    context_object_name = "siae"
    queryset = Siae.objects.all()
    success_message = "Vos modifications ont bien été prises en compte."

    def get_success_url(self):
        return reverse_lazy("dashboard:siae_edit_offer", args=[self.kwargs.get("slug")])


class SiaeEditPrestaView(LoginRequiredMixin, SiaeOwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = SiaeEditPrestaForm
    template_name = "dashboard/siae_edit_presta.html"
    context_object_name = "siae"
    queryset = Siae.objects.all()
    success_message = "Vos modifications ont bien été prises en compte."

    def get_context_data(self, **kwargs):
        """
        - init forms
        - pass s3 image upload config
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["offer_formset"] = SiaeOfferFormSet(self.request.POST, instance=self.object)
            context["client_reference_formset"] = SiaeClientReferenceFormSet(self.request.POST, instance=self.object)
            context["image_formset"] = SiaeImageFormSet(self.request.POST, instance=self.object)
        else:
            context["offer_formset"] = SiaeOfferFormSet(instance=self.object)
            context["client_reference_formset"] = SiaeClientReferenceFormSet(instance=self.object)
            context["image_formset"] = SiaeImageFormSet(instance=self.object)
        s3_upload = S3Upload(kind="client_reference_logo")
        context["s3_form_values"] = s3_upload.form_values
        context["s3_upload_config"] = s3_upload.config
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        offer_formset = SiaeOfferFormSet(self.request.POST, instance=self.object)
        client_reference_formset = SiaeClientReferenceFormSet(self.request.POST, instance=self.object)
        image_formset = SiaeImageFormSet(self.request.POST, instance=self.object)
        if (
            form.is_valid()
            and offer_formset.is_valid()
            and client_reference_formset.is_valid()
            and image_formset.is_valid()
        ):
            return self.form_valid(form, offer_formset, client_reference_formset, image_formset)
        else:
            return self.form_invalid(form, offer_formset, client_reference_formset, image_formset)

    def form_valid(self, form, offer_formset, client_reference_formset, image_formset):
        self.object = form.save()
        offer_formset.instance = self.object
        offer_formset.save()
        client_reference_formset.instance = self.object
        client_reference_formset.save()
        image_formset.instance = self.object
        image_formset.save()
        return super().form_valid(form)

    def form_invalid(self, form, offer_formset, client_reference_formset, image_formset):
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        return reverse_lazy("dashboard:siae_edit_presta", args=[self.kwargs.get("slug")])


class SiaeEditOtherView(LoginRequiredMixin, SiaeOwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = SiaeEditOtherForm
    template_name = "dashboard/siae_edit_other.html"
    context_object_name = "siae"
    queryset = Siae.objects.all()
    success_message = "Vos modifications ont bien été prises en compte."

    def get_context_data(self, **kwargs):
        """
        - init forms
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["label_formset"] = SiaeLabelFormSet(self.request.POST, instance=self.object)
        else:
            context["label_formset"] = SiaeLabelFormSet(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        label_formset = SiaeLabelFormSet(self.request.POST, instance=self.object)
        if form.is_valid() and label_formset.is_valid():
            return self.form_valid(form, label_formset)
        else:
            return self.form_invalid(form, label_formset)

    def form_valid(self, form, label_formset):
        self.object = form.save()
        label_formset.instance = self.object
        label_formset.save()
        return super().form_valid(form)

    def form_invalid(self, form, label_formset):
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        return reverse_lazy("dashboard:siae_edit_other", args=[self.kwargs.get("slug")])
