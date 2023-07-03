from django import forms
from django.contrib.gis.db.models.functions import Distance
from django.db.models import BooleanField, Case, Q, Value, When

from lemarche.favorites.models import FavoriteList
from lemarche.networks.models import Network
from lemarche.perimeters.models import Perimeter
from lemarche.sectors.models import Sector
from lemarche.siaes import constants as siae_constants
from lemarche.siaes.models import Siae, SiaeClientReference, SiaeGroup
from lemarche.tenders.models import Tender
from lemarche.users.models import User
from lemarche.utils.fields import GroupedModelMultipleChoiceField


FORM_KIND_CHOICES_GROUPED = (
    ("Insertion par l'activité économique", siae_constants.KIND_CHOICES_WITH_EXTRA_INSERTION),
    ("Handicap", siae_constants.KIND_CHOICES_WITH_EXTRA_HANDICAP),
)
FORM_TERRITORY_CHOICES = (
    ("QPV", "Quartier prioritaire de la politique de la ville (QPV)"),
    ("ZRR", "Zone de revitalisation rurale (ZRR)"),
)

FORM_CA_CHOICES = (
    ("", ""),
    ("-100000", "Moins de 100 K€"),
    ("100000-500000", "100 K€ à 500 K€"),
    ("500000-1000000", "500 K€ à 1 M€"),
    ("1000000-5000000", "1 M€ à 5 M€"),
    ("5000000-10000000", "5 M€ à 10 M€"),
    ("10000000-", "Plus de 10 M€"),
)


class SiaeFilterForm(forms.Form):
    q = forms.CharField(
        label="Recherche via le numéro de SIRET ou le nom de votre structure",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Votre recherche…"}),
    )
    sectors = GroupedModelMultipleChoiceField(
        label=Sector._meta.verbose_name_plural,
        queryset=Sector.objects.form_filter_queryset(),
        choices_groupby="group",
        to_field_name="slug",
        required=False,
    )
    # The hidden `perimeters` field is populated by the JS autocomplete library, see `perimeters_autocomplete_field.js`
    perimeters = forms.ModelMultipleChoiceField(
        label=Perimeter._meta.verbose_name_plural,
        queryset=Perimeter.objects.all(),
        to_field_name="slug",
        required=False,
        # widget=forms.HiddenInput()
    )
    kind = forms.MultipleChoiceField(
        label=Siae._meta.get_field("kind").verbose_name,
        choices=FORM_KIND_CHOICES_GROUPED,
        required=False,
    )
    presta_type = forms.MultipleChoiceField(
        label=Siae._meta.get_field("presta_type").verbose_name,
        choices=siae_constants.PRESTA_CHOICES,
        required=False,
    )
    territory = forms.MultipleChoiceField(
        label="Territoire spécifique",
        choices=FORM_TERRITORY_CHOICES,
        required=False,
    )
    networks = forms.ModelMultipleChoiceField(
        label="Réseau",
        queryset=Network.objects.all().order_by("name"),
        to_field_name="slug",
        required=False,
    )

    locations = forms.ModelMultipleChoiceField(
        label="Localisation",
        queryset=Perimeter.objects.all(),
        to_field_name="slug",
        required=False,
    )

    has_client_references = forms.ChoiceField(
        label=SiaeClientReference._meta.verbose_name,
        help_text="Le prestataire inclusif a-t-il des références clients ?",
        choices=[("", ""), (True, "Oui"), (False, "Non")],
        required=False,
    )
    has_groups = forms.ChoiceField(
        label=SiaeGroup._meta.verbose_name,
        help_text="Le prestataire inclusif fait-il partie d'un groupement ?",
        choices=[("", ""), (True, "Oui"), (False, "Non")],
        required=False,
    )
    legal_form = forms.MultipleChoiceField(
        label=Siae._meta.get_field("legal_form").verbose_name,
        choices=siae_constants.LEGAL_FORM_CHOICES,
        required=False,
    )

    ca = forms.ChoiceField(
        label=Siae._meta.get_field("ca").verbose_name,
        choices=FORM_CA_CHOICES,
        required=False,
    )

    company_client_reference = forms.CharField(
        label="Indiquez le nom de votre entreprise",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Votre entreprise…"}),
    )

    # other hidden filters
    tender = forms.ModelChoiceField(
        queryset=Tender.objects.all(), to_field_name="slug", required=False, widget=forms.HiddenInput()
    )
    tender_status = forms.CharField(required=False, widget=forms.HiddenInput())
    favorite_list = forms.ModelChoiceField(
        queryset=FavoriteList.objects.all(), to_field_name="slug", required=False, widget=forms.HiddenInput()
    )

    def filter_queryset(self, qs=None):  # noqa C901
        """
        Method to filter the Siaes depending on the search filters.
        We also make sure there are no duplicates.
        """
        if qs is None:
            # we only display live Siae
            qs = Siae.objects.search_query_set()

        if not hasattr(self, "cleaned_data"):
            self.full_clean()

        full_text_string = self.cleaned_data.get("q", None)
        if full_text_string:
            # case where a siret search was done, strip all spaces
            if full_text_string.replace(" ", "").isdigit():
                full_text_string = full_text_string.replace(" ", "")
            qs = qs.filter_full_text(full_text_string)

        sectors = self.cleaned_data.get("sectors", None)
        if sectors:
            qs = qs.filter_sectors(sectors)

        perimeters = self.cleaned_data.get("perimeters", None)
        if perimeters:
            qs = qs.geo_range_in_perimeter_list(perimeters)

        kinds = self.cleaned_data.get("kind", None)
        if kinds:
            qs = qs.filter(kind__in=kinds)

        presta_types = self.cleaned_data.get("presta_type", None)
        if presta_types:
            qs = qs.filter(presta_type__overlap=presta_types)

        territory = self.cleaned_data.get("territory", None)
        if territory:
            if len(territory) == 1:
                if "QPV" in territory:
                    qs = qs.filter(is_qpv=True)
                elif "ZRR" in territory:
                    qs = qs.filter(is_zrr=True)
            elif len(territory) == 2:
                qs = qs.filter(Q(is_qpv=True) | Q(is_zrr=True))

        networks = self.cleaned_data.get("networks", None)
        if networks:
            qs = qs.filter_networks(networks)

        has_client_references = self.cleaned_data.get("has_client_references", None)
        if has_client_references in (True, "True"):
            qs = qs.filter(client_reference_count__gte=1)
        elif has_client_references in (False, "False"):
            qs = qs.filter(client_reference_count=0)

        has_groups = self.cleaned_data.get("has_groups", None)
        if has_groups in (True, "True"):
            qs = qs.filter(group_count__gte=1)
        elif has_groups in (False, "False"):
            qs = qs.filter(group_count=0)

        # for CA, "ca" field is taken first, otherwise "api_entreprise_ca" is taken
        ca = self.cleaned_data.get("ca", None)
        if ca:
            lower_limit, upper_limit = ca.split("-")
            if lower_limit:
                qs = qs.filter(
                    (Q(ca__gt=0) & Q(ca__gte=int(lower_limit)))
                    | ((Q(ca=None) | Q(ca=0)) & Q(api_entreprise_ca__gte=int(lower_limit)))
                )
            if upper_limit:
                qs = qs.filter(
                    (Q(ca__gt=0) & Q(ca__lt=int(upper_limit)))
                    | ((Q(ca=None) | Q(ca=0)) & Q(api_entreprise_ca__gt=0) & Q(api_entreprise_ca__lt=int(upper_limit)))
                )

        legal_forms = self.cleaned_data.get("legal_form", None)
        if legal_forms:
            qs = qs.filter(legal_form__in=legal_forms)

        company_client_reference = self.cleaned_data.get("company_client_reference", None)
        if company_client_reference:
            qs = qs.prefetch_related("client_references").filter(
                client_references__name__icontains=company_client_reference
            )

        # a Tender author can export its Siae list
        tender = self.cleaned_data.get("tender", None)
        tender_status = self.cleaned_data.get("tender_status", None)
        if tender:
            if tender_status:  # status == "INTERESTED"
                qs = qs.filter(tendersiae__tender=tender, tendersiae__detail_contact_click_date__isnull=False)
            else:
                qs = qs.filter(tendersiae__tender=tender, tendersiae__email_send_date__isnull=False)

        locations = self.cleaned_data.get("locations", None)
        if locations:
            qs = qs.address_in_perimeter_list(locations)

        favorite_list = self.cleaned_data.get("favorite_list", None)
        if favorite_list:
            qs = qs.filter(favorite_lists__in=[favorite_list])

        # avoid duplicates
        qs = qs.distinct()

        return qs

    def order_queryset(self, qs):
        """
        Method to order the search results (can depend on the search filters).

        By default, Siae will be ordered by "-updated_at"
        **WHY**
        - push siae to update their profile, and have the freshest data at the top
        - we tried random order ("?"), but it had some bugs with pagination
        **BUT**
        - if a Siae has a a SiaeOffer, or a description, or a User, then it is "boosted"
        - if the search is on a CITY perimeter, we order by coordinates first
        - if the search is by keyword, order by "similarity" only
        """
        DEFAULT_ORDERING = ["-updated_at"]
        ORDER_BY_FIELDS = ["-has_offer", "-has_description", "-has_user"] + DEFAULT_ORDERING
        # annotate on description presence: https://stackoverflow.com/a/65014409/4293684
        # qs = qs.annotate(has_description=Exists(F("description")))  # doesn't work
        qs = qs.annotate(
            has_description=Case(
                When(description__gte=1, then=Value(True)), default=Value(False), output_field=BooleanField()
            )
        )
        qs = qs.annotate(
            has_offer=Case(
                When(offer_count__gte=1, then=Value(True)), default=Value(False), output_field=BooleanField()
            )
        )
        qs = qs.annotate(
            has_user=Case(When(user_count__gte=1, then=Value(True)), default=Value(False), output_field=BooleanField())
        )

        # annotate on distance to siae if CITY searched
        # TODO: QUID des distances
        perimeters = self.cleaned_data.get("perimeters", None)
        if perimeters and len(perimeters) == 1:
            perimeter = perimeters[0]
            if perimeter and perimeter.kind == Perimeter.KIND_CITY:
                qs = qs.annotate(
                    distance=Case(
                        # if it's in the same city we set the distance at 0
                        When(post_code__in=perimeter.post_codes, then=Distance("coords", "coords")),
                        default=Distance("coords", perimeter.coords),
                    )
                )
                ORDER_BY_FIELDS = ["distance"] + ORDER_BY_FIELDS

        full_text_string = self.cleaned_data.get("q", None)
        if full_text_string:
            ORDER_BY_FIELDS = ["-similarity"]

        # final ordering
        qs = qs.order_by(*ORDER_BY_FIELDS)
        return qs


class SiaeFavoriteForm(forms.ModelForm):
    favorite_lists = forms.ModelChoiceField(
        label="Liste à associer",
        queryset=FavoriteList.objects.all(),
        widget=forms.RadioSelect,
        required=False,
    )

    class Meta:
        model = Siae
        fields = ["favorite_lists"]


class SiaeDownloadForm(SiaeFilterForm):
    marche_benefits = forms.MultipleChoiceField(
        label="Pourquoi téléchargez-vous cette liste ?",
        choices=Tender._meta.get_field("marche_benefits").base_field.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    download_source = forms.CharField(required=False, widget=forms.HiddenInput())
    format = forms.ChoiceField(
        label="Format", widget=forms.RadioSelect, choices=(("xls", "xls"), ("csv", "csv")), required=False
    )


SHARE_PLATEFORM = (
    ("email", "E-Mail"),
    # ("linkedin", "Linkedin"),
    # ("facebook", "Facebook"),
    # ("twitter", "Twitter"),
    ("download", "Téléchargement"),
)


class SiaeShareForm(SiaeFilterForm):
    # global field
    share_with = forms.ChoiceField(
        label="Partager par",
        widget=forms.RadioSelect(attrs={"x-model": "formData.share_with"}),
        choices=SHARE_PLATEFORM,
        required=False,
    )

    subject = forms.CharField(
        label="Sujet",
        widget=forms.Textarea(attrs={"x-model": "formData.subject", "rows": 1}),
        required=False,
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"x-model": "formData.message", "rows": 2}),
        required=False,
    )
    # download fields
    marche_benefits = forms.MultipleChoiceField(
        label="Pourquoi partagez-vous cette liste ?",
        choices=Tender._meta.get_field("marche_benefits").base_field.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    download_source = forms.CharField(required=False, widget=forms.HiddenInput())
    format = forms.ChoiceField(
        label="Format", widget=forms.RadioSelect, choices=(("XLS", "xls"), ("CLS", "csv")), required=False
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_authenticated:
            subject = self.fields.get("subject")
            message = self.fields.get("message")
            subject.initial = f"{user.full_name} vous envoie une liste de prestataires inclusifs"
            message.initial = (
                "Bonjour,\n"
                + "Vous pouvez consulter cette liste de prestataires inclusifs dans le cadre de votre besoin de sous-traitance...\n"  # noqa
                + f"{user.full_name}"
            )


class NetworkSiaeFilterForm(forms.Form):
    perimeter = forms.ModelChoiceField(
        label="Filtrer par région",
        queryset=Perimeter.objects.regions().order_by("name"),
        to_field_name="slug",
        required=False,
    )

    def filter_queryset(self, qs=None):
        if qs is None:
            qs = Siae.objects.search_query_set()

        if not hasattr(self, "cleaned_data"):
            self.full_clean()

        perimeter = self.cleaned_data.get("perimeter", None)
        if perimeter:
            qs = qs.address_in_perimeter_list([perimeter])

        # avoid duplicates
        qs = qs.distinct()

        return qs
