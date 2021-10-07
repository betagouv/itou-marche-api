from django import forms
from django.forms.models import inlineformset_factory

from lemarche.networks.models import Network
from lemarche.siaes.models import Siae, SiaeClientReference, SiaeLabel, SiaeOffer
from lemarche.users.models import User
from lemarche.utils.fields import GroupedModelMultipleChoiceField
from lemarche.www.siae.forms import SECTOR_FORM_QUERYSET


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mandatory fields.
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True

        # Disabled fields
        self.fields["email"].disabled = True


class SiaeSearchBySiretForm(forms.Form):
    siret = forms.CharField(
        label="Entrez le numéro SIRET ou SIREN de votre structure",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )

    def clean_siret(self):
        siret = self.cleaned_data["siret"]
        if siret:
            # strip spaces (beginning, inbetween, end)
            siret = siret.replace(" ", "")
            # siret/siren validation
            if len(siret) < 9:
                msg = "Le longueur du numéro doit être supérieure ou égale à 9 caractères."
                raise forms.ValidationError(msg)
            if len(siret) > 14:
                msg = "Le longueur du numéro ne peut pas dépasser 14 caractères."
                raise forms.ValidationError(msg)
            if not siret.isdigit():
                msg = "Le numéro ne doit être composé que de chiffres."
                raise forms.ValidationError(msg)
        return siret

    def filter_queryset(self):
        qs = Siae.objects.prefetch_related("users")

        if not hasattr(self, "cleaned_data"):
            self.full_clean()

        siret = self.cleaned_data.get("siret", None)
        if siret:
            qs = qs.filter(siret__startswith=siret)
        else:
            # show results only if there is a valid siret provided
            qs = qs.none()

        return qs


class SiaeAdoptConfirmForm(forms.ModelForm):
    class Meta:
        model = Siae
        fields = []


class SiaeEditInfoContactForm(forms.ModelForm):
    # slug =
    kind = forms.CharField(label=Siae._meta.get_field("kind").verbose_name)
    department = forms.CharField(label=Siae._meta.get_field("department").verbose_name)
    region = forms.CharField(label=Siae._meta.get_field("region").verbose_name)

    class Meta:
        model = Siae
        fields = [
            "name",
            "brand",
            "siret",
            "kind",
            "city",
            "post_code",
            "department",
            "region",
            "website",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disabled fields
        for field in Siae.READONLY_FIELDS_FROM_C1:
            if field in self.fields:
                self.fields[field].disabled = True
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})


class SiaeEditOfferForm(forms.ModelForm):
    presta_type = forms.MultipleChoiceField(
        label=Siae._meta.get_field("presta_type").verbose_name,
        choices=Siae.PRESTA_CHOICES,
        required=True,
        widget=forms.CheckboxSelectMultiple,
    )
    geo_range = forms.ChoiceField(
        label=Siae._meta.get_field("geo_range").verbose_name,
        choices=Siae.GEO_RANGE_CHOICES,
        required=True,
        widget=forms.RadioSelect,
    )
    sectors = GroupedModelMultipleChoiceField(
        label=Siae._meta.get_field("sectors").verbose_name,
        queryset=SECTOR_FORM_QUERYSET,
        choices_groupby="group",
        required=True,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Siae
        fields = [
            "presta_type",
            # "is_cocontracting",
            "geo_range",
            "geo_range_custom_distance",
            "sectors",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["geo_range_custom_distance"].widget.attrs.update(
            {
                "placeholder": "Distance en kilomètres",
            }
        )

    def save(self, *args, **kwargs):
        """Clean geo_range_custom_distance before save."""
        if self.cleaned_data["geo_range"] != Siae.GEO_RANGE_CUSTOM:
            self.instance.geo_range_custom_distance = None
        super().save(*args, **kwargs)


class SiaeEditPrestaForm(forms.ModelForm):
    class Meta:
        model = Siae
        fields = [
            "description",
            # "offers",  # inlineformset
            # "client_references",  # inlineformset
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget.attrs.update(
            {
                "placeholder": "N'hésitez pas à mettre en avant les spécificités de votre structure",
                "class": "form-control",
            }
        )


class SiaeOfferForm(forms.ModelForm):
    class Meta:
        model = SiaeOffer
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )
        self.fields["description"].widget.attrs.update(
            {
                "class": "form-control",
                "rows": 5,
            }
        )


SiaeOfferFormSet = inlineformset_factory(Siae, SiaeOffer, form=SiaeOfferForm, extra=2, can_delete=True)


class SiaeClientReferenceForm(forms.ModelForm):
    class Meta:
        model = SiaeClientReference
        fields = ["name", "image_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )
        self.fields["image_name"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )


SiaeClientReferenceFormSet = inlineformset_factory(
    Siae, SiaeClientReference, form=SiaeClientReferenceForm, extra=2, can_delete=True
)


class SiaeEditOtherForm(forms.ModelForm):
    is_cocontracting = forms.BooleanField(
        label="Êtes-vous ouvert à la co-traitance ?",
        widget=forms.RadioSelect(choices=[(True, "Oui"), (False, "Non")]),
    )
    networks = forms.ModelMultipleChoiceField(
        queryset=Network.objects.all().order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Siae
        fields = [
            "is_cocontracting",
            "networks",
            # "labels",  # inlineformset
        ]


class SiaeLabelForm(forms.ModelForm):
    class Meta:
        model = SiaeLabel
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )


SiaeLabelFormSet = inlineformset_factory(Siae, SiaeLabel, form=SiaeLabelForm, extra=2, can_delete=True)
