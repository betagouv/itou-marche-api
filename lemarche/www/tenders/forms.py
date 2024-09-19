from datetime import date

from ckeditor.widgets import CKEditorWidget
from django import forms

from lemarche.sectors.models import Sector
from lemarche.tenders import constants as tender_constants
from lemarche.tenders.enums import SurveyDoesNotExistQuestionChoices, SurveyScaleQuestionChoices
from lemarche.tenders.models import Tender, TenderSiae
from lemarche.users.models import User
from lemarche.utils import constants
from lemarche.utils.fields import GroupedModelMultipleChoiceField
from lemarche.utils.widgets import CustomSelectMultiple


class TenderCreateStepGeneralForm(forms.ModelForm):
    FORM_KIND_CHOICES = (
        (tender_constants.KIND_TENDER, tender_constants.KIND_TENDER_DISPLAY),
        (tender_constants.KIND_QUOTE, tender_constants.KIND_QUOTE_DISPLAY),
        (tender_constants.KIND_PROJECT, "Sourcing inversé"),  # tender_constants.KIND_PROJECT_DISPLAY
    )

    description = forms.CharField(widget=CKEditorWidget(config_name="frontuser"))

    sectors = GroupedModelMultipleChoiceField(
        label=Sector._meta.verbose_name_plural,
        queryset=Sector.objects.form_filter_queryset(),
        choices_groupby="group",
        to_field_name="slug",
        required=True,
        widget=CustomSelectMultiple(),
    )

    class Meta:
        model = Tender
        fields = [
            "kind",
            "title",
            "description",
            "sectors",
            "location",  # generated by js
            "is_country_area",
        ]
        widgets = {
            "kind": forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kind"].choices = self.FORM_KIND_CHOICES
        self.fields["location"].to_field_name = "slug"
        # required fields
        self.fields["description"].required = True
        self.fields["description"].widget.group_class = "form-description-ckeditor fr-input-group"

        # self.fields["perimeters"].required = True  # JS
        # label, placeholder & help_text
        self.fields["title"].widget.attrs["placeholder"] = "Ex : Demande de devis rénovation façade à Grenoble"
        self.fields["sectors"].help_text = Tender._meta.get_field("sectors").help_text  # else doesn't appear
        self.fields["is_country_area"].help_text = None

    def clean(self):
        super().clean()
        msg_field_missing = "{} est un champ obligatoire"
        if "location" in self.errors or not (
            self.cleaned_data.get("is_country_area") or self.cleaned_data.get("location")
        ):
            self.add_error("location", msg_field_missing.format("Lieu d'intervention"))
        if "sectors" in self.errors:
            self.add_error("sectors", msg_field_missing.format(Sector._meta.verbose_name_plural))


class TenderCreateStepDetailForm(forms.ModelForm):
    # fields from previous step
    kind = None

    questions_list = forms.JSONField(required=False)

    class Meta:
        model = Tender
        fields = [
            "start_working_date",
            "deadline_date",
            "external_link",
            "amount",
            "why_amount_is_blank",
            "accept_share_amount",
        ]
        widgets = {
            "start_working_date": forms.widgets.DateInput(attrs={"class": "fr-input", "type": "date"}),
            "deadline_date": forms.widgets.DateInput(attrs={"class": "fr-input", "type": "date"}),
            "why_amount_is_blank": forms.widgets.RadioSelect,
            "amount": forms.Select(attrs={"x-model": "formData.amount", "x-on:change": "getImpactMessage()"}),
        }

    def __init__(self, kind, questions_list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # required fields
        self.fields["deadline_date"].required = True

        if self.instance.deadline_date:
            self.initial["deadline_date"] = self.instance.deadline_date.isoformat()
        if questions_list:
            self.initial["questions_list"] = questions_list
        # to remove blank option
        self.fields["why_amount_is_blank"].choices = self.fields["why_amount_is_blank"].choices[1:]
        if self.instance.start_working_date:
            self.initial["start_working_date"] = self.instance.start_working_date.isoformat()

        # label, placeholder & help_text
        if kind != tender_constants.KIND_TENDER:
            self.fields["external_link"].label = "Lien à partager"
            self.fields["external_link"].help_text = None

        if kind == tender_constants.KIND_TENDER:
            self.fields["external_link"].required = True

        self.fields["amount"].label = "Montant € estimé de votre besoin"
        self.fields["accept_share_amount"].label = self.fields["accept_share_amount"].help_text
        self.fields["external_link"].widget.attrs["placeholder"] = "https://www.example.fr"
        self.fields["accept_share_amount"].help_text = None

    def clean_questions_list(self):
        questions = self.cleaned_data["questions_list"]
        if questions is None:
            return questions
        elif not isinstance(questions, list):
            raise ValueError("It's not a list")
        for index, question in enumerate(questions):
            if not isinstance(question, dict):
                raise ValueError("Bad format")
            if not question.get("text"):
                questions.pop(index)
        return questions

    def clean(self):
        super().clean()
        today = date.today()
        max_deadline_date = self.cleaned_data.get("start_working_date")
        deadline_date = self.cleaned_data.get("deadline_date")
        # check that deadline_date < start_working_date
        if max_deadline_date and deadline_date and (deadline_date > max_deadline_date):
            self.add_error(
                "deadline_date",
                (
                    "La date de clôture des réponses ne doit pas être supérieure à la date "
                    f"de début d'intervention ({max_deadline_date})."
                ),
            )
        # check that deadline_date > today
        if deadline_date and (deadline_date < today):
            self.add_error(
                "deadline_date", "La date de clôture des réponses ne doit pas être antérieure à aujourd'hui."
            )


class TenderCreateStepContactForm(forms.ModelForm):
    # fields from previous step
    external_link = None
    user: User = None

    response_kind = forms.MultipleChoiceField(
        label="Comment les prestataires doivent vous répondre",
        choices=Tender._meta.get_field("response_kind").base_field.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
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
            "response_is_anonymous",
        ]
        labels = {
            "contact_first_name": "Prénom",
            "contact_last_name": "Nom",
            "contact_email": "E-mail",
            "contact_phone": "Téléphone",
        }

    def __init__(self, kind, external_link, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind
        self.external_link = external_link
        self.user = user
        user_is_anonymous = not user.is_authenticated
        user_does_not_have_company_name = user_is_anonymous or not user.company_name

        # display response_is_anonymous only if the tender is a project
        if self.instance and (self.instance.kind != tender_constants.KIND_PROJECT):
            self.fields["response_is_anonymous"].widget = forms.HiddenInput()
        # if TENDER & external_link, then response_kind should have RESPONSE_KIND_EXTERNAL
        if self.instance and (self.instance.kind == tender_constants.KIND_TENDER) and self.external_link:
            self.initial["response_kind"] = [tender_constants.RESPONSE_KIND_EXTERNAL]
        # required fields
        if user_is_anonymous:
            self.fields["contact_first_name"].required = True
            self.fields["contact_last_name"].required = True
            self.fields["contact_email"].required = True
            self.fields["contact_phone"].required = True
        else:
            del self.fields["contact_first_name"]
            del self.fields["contact_last_name"]
            del self.fields["contact_email"]
            del self.fields["contact_phone"]
        # user company_name field
        if user_does_not_have_company_name:
            self.fields["contact_company_name"].widget = forms.TextInput()  # HiddenInput() by default
            self.fields["contact_company_name"].required = True
        else:
            self.initial["contact_company_name"] = user.company_name

    def clean(self):
        super().clean()
        if not self.cleaned_data.get("response_kind") and not self.cleaned_data.get("response_is_anonymous"):
            self.add_error("response_kind", "Ce champ est obligatoire.")

        if not self.user.is_authenticated:
            # contact_email must be filled if RESPONSE_KIND_EMAIL
            if self.cleaned_data.get("response_kind") and (
                tender_constants.RESPONSE_KIND_EMAIL in self.cleaned_data.get("response_kind")
                and not self.cleaned_data.get("contact_email")
            ):
                self.add_error("response_kind", "E-mail sélectionné mais aucun e-mail renseigné.")
            # contact_phone must be filled if RESPONSE_KIND_TEL
            if self.cleaned_data.get("response_kind") and (
                tender_constants.RESPONSE_KIND_TEL in self.cleaned_data.get("response_kind")
                and not self.cleaned_data.get("contact_phone")
            ):
                self.add_error("response_kind", "Téléphone sélectionné mais aucun téléphone renseigné.")
        elif not self.user.phone:
            if self.cleaned_data.get("response_kind") and (
                tender_constants.RESPONSE_KIND_TEL in self.cleaned_data.get("response_kind")
            ):
                self.add_error(
                    "response_kind", "Téléphone sélectionné mais aucun téléphone renseigné dans votre profil."
                )

        # external_link must be filled if RESPONSE_KIND_EXTERNAL
        if self.cleaned_data.get("response_kind") and (
            tender_constants.RESPONSE_KIND_EXTERNAL in self.cleaned_data.get("response_kind")
            and not self.external_link
        ):
            self.add_error(
                "response_kind", "Lien externe sélectionné mais aucun lien renseigné (à l'étape précédente)."
            )
        if (
            self.kind == tender_constants.KIND_TENDER
            and self.external_link
            and self.cleaned_data.get("response_kind")
            and tender_constants.RESPONSE_KIND_EXTERNAL not in self.cleaned_data.get("response_kind")
        ):
            self.add_error("response_kind", "Appel d'offre avec lien renseigné.")


class TenderCreateStepSurveyForm(forms.ModelForm):
    scale_marche_useless = forms.ChoiceField(
        label=Tender._meta.get_field("scale_marche_useless").help_text,
        choices=SurveyScaleQuestionChoices.choices,
        widget=forms.RadioSelect,
        required=True,
    )

    le_marche_doesnt_exist_how_to_find_siae = forms.ChoiceField(
        label=Tender._meta.get_field("le_marche_doesnt_exist_how_to_find_siae").help_text,
        choices=SurveyDoesNotExistQuestionChoices.choices,
        required=False,
    )

    class Meta:
        model = Tender
        fields = [
            "scale_marche_useless",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.id:
            self.initial["scale_marche_useless"] = None


class TenderCreateStepConfirmationForm(forms.Form):
    pass


class TenderSurveyTransactionedForm(forms.ModelForm):
    class Meta:
        model = Tender
        fields = [
            "survey_transactioned_answer",
            "survey_transactioned_amount",
            "survey_transactioned_feedback",
        ]

    def __init__(self, tender_survey_transactioned_answer=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "survey_transactioned_answer"
        ].label = "Avez-vous contractualisé avec un prestataire trouvé via le Marché de l'inclusion ?"
        self.fields["survey_transactioned_amount"].label = "Quel est le montant de la transaction ? (facultatif)"
        self.fields["survey_transactioned_feedback"].label = "Partagez-nous votre retour d'expérience (facultatif)"
        self.fields["survey_transactioned_feedback"].widget.attrs.update(
            {
                "placeholder": "Lors de mon expérience avec le Marché de l'inclusion :\n- j'ai apprécié ...\n- j'ai moins aimé ...\n- vous pourriez vous améliorer dans ..."  # noqa
            }
        )
        if tender_survey_transactioned_answer is not None:
            self.fields["survey_transactioned_answer"].disabled = True
            if tender_survey_transactioned_answer in constants.FALSE_VALUES + [constants.DONT_KNOW]:
                self.fields["survey_transactioned_amount"].widget = forms.HiddenInput()


class TenderSiaeSurveyTransactionedForm(forms.ModelForm):
    class Meta:
        model = TenderSiae
        fields = [
            "survey_transactioned_answer",
            "survey_transactioned_amount",
            "survey_transactioned_feedback",
        ]

    def __init__(self, tender_survey_transactioned_answer=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["survey_transactioned_answer"].label = "Avez-vous contractualisé avec le client ?"
        self.fields["survey_transactioned_amount"].label = "Quel est le montant de la transaction ? (facultatif)"
        self.fields["survey_transactioned_feedback"].label = "Partagez-nous votre retour d'expérience (facultatif)"
        self.fields["survey_transactioned_feedback"].widget.attrs.update(
            {
                "placeholder": "Lors de mon expérience avec le Marché de l'inclusion :\n- j'ai apprécié ...\n- j'ai moins aimé ...\n- vous pourriez vous améliorer dans ..."  # noqa
            }
        )
        if tender_survey_transactioned_answer is not None:
            self.fields["survey_transactioned_answer"].disabled = True
            if tender_survey_transactioned_answer in constants.FALSE_VALUES:
                self.fields["survey_transactioned_amount"].widget = forms.HiddenInput()


class TenderFilterForm(forms.Form):
    FORM_KIND_CHOICES = (
        ("", "Toutes les opportunités"),
        (tender_constants.KIND_QUOTE, tender_constants.KIND_QUOTE_DISPLAY),
        (tender_constants.KIND_TENDER, tender_constants.KIND_TENDER_DISPLAY),
        (tender_constants.KIND_PROJECT, tender_constants.KIND_PROJECT_SIAE_DISPLAY),
    )

    kind = forms.ChoiceField(
        label="Type de besoin",
        choices=FORM_KIND_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
        required=False,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        stats = Tender.objects.unread_stats(user=user)
        new_choices = []
        for kind_key, kind_label in self.FORM_KIND_CHOICES:
            count_key = f"unread_count_{kind_key}_annotated"
            if count_key in stats and stats[count_key] > 0:
                new_choices.append((kind_key, f"{kind_label} ({stats[count_key]})"))
            else:
                new_choices.append((kind_key, kind_label))

        self.fields["kind"].choices = new_choices
