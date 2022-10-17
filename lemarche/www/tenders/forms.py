from datetime import date

from django import forms

from lemarche.sectors.models import Sector
from lemarche.tenders.models import Tender
from lemarche.utils.fields import GroupedModelMultipleChoiceField


class AddTenderStepGeneralForm(forms.ModelForm):
    sectors = GroupedModelMultipleChoiceField(
        label=Sector._meta.verbose_name_plural,
        queryset=Sector.objects.form_filter_queryset(),
        choices_groupby="group",
        to_field_name="slug",
    )
    presta_type = forms.MultipleChoiceField(
        label="Type(s) de prestation(s)",
        choices=Tender._meta.get_field("presta_type").base_field.choices,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Tender
        fields = [
            "kind",
            "title",
            "sectors",
            "presta_type",
            "perimeters",  # generated by js
            "is_country_area",
        ]
        widgets = {
            "kind": forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["perimeters"].to_field_name = "slug"
        # required fields
        self.fields["sectors"].required = True
        # self.fields["perimeters"].required = True  # JS
        # label, placeholder & help_text
        self.fields["title"].widget.attrs["placeholder"] = "Ex : Devis rénovation façade"
        self.fields["sectors"].help_text = Tender._meta.get_field("sectors").help_text  # else doesn't appear

    def clean(self):
        super().clean()
        msg_field_missing = "{} est un champ obligatoire"
        if "perimeters" in self.errors or not (
            self.cleaned_data.get("is_country_area") or self.cleaned_data.get("perimeters")
        ):
            self.add_error("perimeters", msg_field_missing.format("Lieux d'exécution"))
        if "sectors" in self.errors:
            self.add_error("sectors", msg_field_missing.format(Sector._meta.verbose_name_plural))


class AddTenderStepDescriptionForm(forms.ModelForm):
    # fields from previous step
    kind = None

    class Meta:
        model = Tender
        fields = [
            "description",
            "start_working_date",
            "external_link",
            "constraints",
            "amount",
            "accept_share_amount",
            "accept_cocontracting",
        ]
        widgets = {
            "start_working_date": forms.widgets.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, kind, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind
        # required fields
        self.fields["description"].required = True
        if self.kind == Tender.TENDER_KIND_TENDER:
            self.fields["amount"].required = True
        # label, placeholder & help_text
        self.fields["amount"].label = "Montant estimé du marché"  # add "estimé"
        self.fields["accept_share_amount"].label = self.fields["accept_share_amount"].help_text
        self.fields["accept_cocontracting"].label = self.fields["accept_cocontracting"].help_text
        self.fields["external_link"].widget.attrs["placeholder"] = "https://www.example.fr"
        self.fields["constraints"].widget.attrs["placeholder"] = "Ex : Déplacements"
        self.fields["accept_share_amount"].help_text = None
        self.fields["accept_cocontracting"].help_text = None


class AddTenderStepContactForm(forms.ModelForm):
    # fields from previous step
    max_deadline_date = None
    external_link = None
    user_is_anonymous = None
    user_does_not_have_company_name = None

    response_kind = forms.MultipleChoiceField(
        label="Comment répondre",
        choices=Tender._meta.get_field("response_kind").base_field.choices,
        widget=forms.CheckboxSelectMultiple,
    )

    contact_company_name = forms.CharField(label="Votre entreprise", widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Tender
        fields = [
            "contact_first_name",
            "contact_last_name",
            "contact_email",
            "contact_phone",
            "contact_company_name",
            "response_kind",
            "deadline_date",
        ]
        widgets = {
            "deadline_date": forms.widgets.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(
        self,
        max_deadline_date,
        external_link,
        user_is_anonymous=False,
        user_does_not_have_company_name=False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.max_deadline_date = max_deadline_date
        self.external_link = external_link
        self.user_is_anonymous = user_is_anonymous
        self.user_does_not_have_company_name = user_does_not_have_company_name
        # required fields
        self.fields["contact_first_name"].required = True
        self.fields["contact_last_name"].required = True
        if self.user_is_anonymous:
            self.fields["contact_email"].required = True
            self.fields["contact_phone"].required = True
        if self.user_does_not_have_company_name:
            self.fields["contact_company_name"].widget = forms.TextInput()  # HiddenInput() by default
            self.fields["contact_company_name"].required = True

    def clean(self):
        super().clean()
        today = date.today()
        # check that deadline_date < start_working_date
        if (
            self.max_deadline_date
            and self.cleaned_data.get("deadline_date")
            and (self.cleaned_data.get("deadline_date") > self.max_deadline_date)
        ):
            self.add_error(
                "deadline_date",
                f"La date de clôture des réponses ne doit pas être supérieure à la date de début d'intervention ({self.max_deadline_date}).",  # noqa
            )
        # check that deadline_date > today
        if self.cleaned_data.get("deadline_date") and (self.cleaned_data.get("deadline_date") < today):
            self.add_error(
                "deadline_date", "La date de clôture des réponses ne doit pas être antérieure à aujourd'hui."
            )
        # contact_email must be filled if RESPONSE_KIND_TEL
        if self.cleaned_data.get("response_kind") and (
            Tender.RESPONSE_KIND_EMAIL in self.cleaned_data.get("response_kind")
            and not self.cleaned_data.get("contact_email")
        ):
            self.add_error("response_kind", "E-mail sélectionné mais aucun e-mail renseigné.")
        # contact_phone must be filled if RESPONSE_KIND_TEL
        if self.cleaned_data.get("response_kind") and (
            Tender.RESPONSE_KIND_TEL in self.cleaned_data.get("response_kind")
            and not self.cleaned_data.get("contact_phone")
        ):
            self.add_error("response_kind", "Téléphone sélectionné mais aucun téléphone renseigné.")
        # external_link must be filled if RESPONSE_KIND_EXTERNAL
        if self.cleaned_data.get("response_kind") and (
            Tender.RESPONSE_KIND_EXTERNAL in self.cleaned_data.get("response_kind") and not self.external_link
        ):
            self.add_error(
                "response_kind", "Lien externe sélectionné mais aucun lien renseigné (à l'étape précédente)."
            )


class AddTenderStepConfirmationForm(forms.Form):
    is_marche_useful = forms.BooleanField(
        label=Tender._meta.get_field("is_marche_useful").help_text,
        widget=forms.RadioSelect(choices=[(True, "Oui"), (False, "Non")]),
        required=False,  # if a BooleanField is required, then it won't allow a False value...
        initial=True,  # ...so we initialize it
    )
    marche_benefits = forms.MultipleChoiceField(
        label=Tender._meta.get_field("marche_benefits").help_text,
        choices=Tender._meta.get_field("marche_benefits").base_field.choices,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Tender
        fields = [
            "is_marche_useful",
            "marche_benefits",
        ]
