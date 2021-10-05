from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.edit import FormMixin

from lemarche.siaes.models import Siae
from lemarche.www.dashboard.forms import ProfileEditForm, SiaeAdoptConfirmForm, SiaeSearchBySiretForm
from lemarche.www.dashboard.mixins import SiaeUserRequiredMixin


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


class SiaeAdoptConfirmView(LoginRequiredMixin, SiaeUserRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = SiaeAdoptConfirmForm
    template_name = "dashboard/siae_adopt_confirm.html"
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
