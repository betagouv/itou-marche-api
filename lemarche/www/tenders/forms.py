from datetime import date

from django import forms

from lemarche.sectors.models import Sector
from lemarche.tenders import constants
from lemarche.tenders.models import Tender
from lemarche.users.models import User
from lemarche.utils.fields import GroupedModelMultipleChoiceField


class AddTenderStepGeneralForm(forms.ModelForm):
    sectors = GroupedModelMultipleChoiceField(
        label=Sector._meta.verbose_name_plural,
        queryset=Sector.objects.form_filter_queryset(),
        choices_groupby="group",
        to_field_name="slug",
        required=True,
    )
    presta_type = forms.MultipleChoiceField(
        label="Type(s) de prestation(s)",
        choices=Tender._meta.get_field("presta_type").base_field.choices,
        widget=forms.CheckboxSelectMultiple,
        required=True,
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
        self.fields["is_country_area"].help_text = None

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

        if self.instance.start_working_date:
            self.initial["start_working_date"] = self.instance.start_working_date.isoformat()  # Here

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
    user: User = None

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
            "response_kind",
            "deadline_date",
        ]
        widgets = {
            "deadline_date": forms.widgets.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, max_deadline_date, external_link, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_deadline_date = max_deadline_date
        self.external_link = external_link
        user_is_anonymous = not user.is_authenticated

        if self.instance.deadline_date:
            self.initial["deadline_date"] = self.instance.deadline_date.isoformat()  # Here

        # required fields
        self.fields["contact_first_name"].required = True
        self.fields["contact_last_name"].required = True
        if user_is_anonymous:
            self.fields["contact_email"].required = True
            self.fields["contact_phone"].required = True
        else:
            self.initial["contact_first_name"] = user.first_name
            self.initial["contact_last_name"] = user.last_name
            self.initial["contact_email"] = user.email
            self.initial["contact_phone"] = user.phone

        user_does_not_have_company_name = user_is_anonymous or not user.company_name
        if user_does_not_have_company_name:
            self.fields["contact_company_name"].widget = forms.TextInput()  # HiddenInput() by default
            self.fields["contact_company_name"].required = True
        else:
            self.initial["contact_company_name"] = user.company_name

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


class AddTenderStepSurveyForm(forms.ModelForm):
    scale_marche_useless = forms.ChoiceField(
        label=Tender._meta.get_field("scale_marche_useless").help_text,
        choices=constants.SURVEY_SCALE_QUESTION_CHOICES,
        widget=forms.RadioSelect,
        required=True,
    )

    worked_with_inclusif_siae_this_kind_tender = forms.ChoiceField(
        label="Q°2. Avez-vous déjà travaillé avec des prestataires inclusifs sur ce type de prestation ?",
        choices=constants.SURVEY_YES_NO_DONT_KNOW_CHOICES,
        widget=forms.RadioSelect,
        required=True,
    )
    # hidden if worked_with_inclusif_siae_this_kind_tender is no or don't know
    is_encouraged_by_le_marche = forms.ChoiceField(
        label="""Q°3. Est-ce la plateforme du Marché de l'inclusion qui vous a encouragé à consulter des prestataires inclusifs
        pour ce besoin ?""",
        choices=constants.SURVEY_ENCOURAGED_BY_US_CHOICES,
        widget=forms.RadioSelect,
        required=False,
    )

    providers_out_of_insertion = forms.ChoiceField(
        label="Q°4. Comptez-vous consulter d'autres prestataires en dehors de l'Insertion et du Handicap ?",
        choices=constants.SURVEY_SCALE_QUESTION_CHOICES,
        widget=forms.RadioSelect,
        required=True,
    )

    le_marche_doesnt_exist_how_to_find_siae = forms.CharField(
        label="""Q°5. Si le Marché de l'inclusion n'existait pas,
            comment auriez-vous fait pour trouver un prestataire inclusif ?""",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "cols": 15}),
    )

    class Meta:
        model = Tender
        fields = [
            "scale_marche_useless",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.initial["worked_with_inclusif_siae_this_kind_tender"] = self.instance.extra_data.get(
                "worked_with_inclusif_siae_this_kind_tender"
            )
            self.initial["is_encouraged_by_le_marche"] = self.instance.extra_data.get("is_encouraged_by_le_marche")
            self.initial["providers_out_of_insertion"] = self.instance.extra_data.get("providers_out_of_insertion")
            self.initial["le_marche_doesnt_exist_how_to_find_siae"] = self.instance.extra_data.get(
                "le_marche_doesnt_exist_how_to_find_siae"
            )
        else:
            self.initial["scale_marche_useless"] = None

    def clean(self) -> dict[str, any]:
        if not self.errors:
            super_cleaned_data = super().clean()
            if super_cleaned_data:
                cleaned_data = {
                    "scale_marche_useless": super_cleaned_data.pop("scale_marche_useless"),
                    "extra_data": super_cleaned_data,
                }
                return cleaned_data


class AddTenderStepConfirmationForm(forms.Form):
    pass
