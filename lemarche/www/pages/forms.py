from django import forms
from django.db.models import Case, Count, F, IntegerField, Sum, When

from lemarche.siaes.models import Siae
from lemarche.utils.constants import EMPTY_CHOICE
from lemarche.utils.mtcaptcha import check_captcha_token
from lemarche.www.siaes.forms import SiaeFilterForm


class ContactForm(forms.Form):
    KIND_CHOICES = EMPTY_CHOICE + (
        ("SIAE", "Entreprise sociale inclusive (SIAE, EA, GEIQ, ESAT)"),
        ("BUYER", "Acheteurs privés ou publics"),
        ("PARTNER", "Facilitateurs des clauses sociales"),
        ("OTHER", "Autre"),
    )
    first_name = forms.CharField(
        label="Prénom",
        widget=forms.TextInput(attrs={"autofocus": "autofocus"}),
        required=False,
    )
    last_name = forms.CharField(label="Nom", required=False)
    email = forms.EmailField(label="Adresse e-mail", required=True)
    phone = forms.CharField(
        label="Numéro de téléphone",
        max_length=16,
        required=False,
    )
    kind = forms.ChoiceField(label="Type d'utilisateur", widget=forms.Select, choices=KIND_CHOICES, required=True)
    siret = forms.CharField(
        label="SIRET",
        required=False,
    )

    # subject = ChoiceField + choices=SUBJECT_CHOICES ?
    subject = forms.CharField(label="Sujet", max_length=150, required=True)

    message = forms.CharField(label="Message", widget=forms.Textarea(attrs={"data-expandable": "true"}), required=True)

    def clean(self):
        super().clean()
        if not check_captcha_token(self.data):
            raise forms.ValidationError("Le code de protection est incorrect. Veuillez réessayer.")


class ImpactCalculatorForm(SiaeFilterForm):
    class Meta:
        model = Siae
        fields = ["sectors", "perimeters", "presta_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # required fields
        self.fields["sectors"].required = True
        self.fields["perimeters"].required = True
        self.fields["presta_type"].required = True

    def impact_aggregation(self, qs=None):
        if not qs:
            qs = self.filter_queryset()
        qs = qs.annotate(
            ca_declared=Case(
                When(ca__isnull=False, then=F("ca")),
                When(ca__isnull=True, api_entreprise_ca__isnull=False, then=F("api_entreprise_ca")),
                default=0,
            ),
            employees_insertion=Case(
                When(c2_etp_count__isnull=False, then=F("c2_etp_count")),
                When(employees_insertion_count__isnull=False, then=F("employees_insertion_count")),
                default=0,
                output_field=IntegerField(),
            ),
        )
        return qs.aggregate(Count("id"), Sum("employees_insertion"), Sum("ca_declared"))


class SocialImpactBuyersCalculatorForm(forms.Form):
    amount = forms.IntegerField(min_value=100, max_value=10e8, label="Montant de votre achat (en €)")


class CompanyReferenceCalculatorForm(SiaeFilterForm):
    class Meta:
        model = Siae
        fields = ["company_client_reference"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # required fields
        self.fields["company_client_reference"].required = True
