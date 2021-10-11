import django_filters

from lemarche.sectors.models import Sector
from lemarche.siaes.models import Siae


class SiaeFilter(django_filters.FilterSet):
    kind = django_filters.MultipleChoiceFilter(label="Type(s) de structure", choices=Siae.KIND_CHOICES)
    presta_type = django_filters.MultipleChoiceFilter(
        label="Type(s) de prestation", choices=Siae.PRESTA_CHOICES, lookup_expr="icontains"
    )
    department = django_filters.CharFilter(label="Numéro du département")
    sectors = django_filters.ModelMultipleChoiceFilter(
        label="Secteur(s) d'activité<br /><br /><i>Mettre le slug de chaque secteur d'activité</i>",
        field_name="sectors__slug",
        to_field_name="slug",
        queryset=Sector.objects.all(),
    )
    updated_at = django_filters.IsoDateTimeFromToRangeFilter(label="Date de dernière mise à jour")

    class Meta:
        model = Siae
        fields = ["kind", "presta_type", "department", "updated_at"]
