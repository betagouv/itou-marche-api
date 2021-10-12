from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse

from lemarche.perimeters.factories import PerimeterFactory
from lemarche.perimeters.models import Perimeter
from lemarche.siaes.factories import SiaeFactory, SiaeOfferFactory
from lemarche.siaes.models import Siae
from lemarche.users.factories import UserFactory
from lemarche.www.siae.forms import SiaeSearchForm


class SiaePerimeterSearchFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create the Perimeters
        PerimeterFactory(
            name="Grenoble",
            kind=Perimeter.KIND_CITY,
            insee_code="38185",
            department_code="38",
            region_code="84",
            coords=Point(5.7301, 45.1825),
        )
        PerimeterFactory(
            name="Chamrousse",
            kind=Perimeter.KIND_CITY,
            insee_code="38567",
            department_code="38",
            region_code="84",
            coords=Point(5.8862, 45.1106),
        )
        PerimeterFactory(name="Isère", kind=Perimeter.KIND_DEPARTMENT, insee_code="38", region_code="84")
        PerimeterFactory(name="Auvergne-Rhône-Alpes", kind=Perimeter.KIND_REGION, insee_code="R84")
        # create the Siaes
        SiaeFactory(city="Grenoble", department="38", region="Auvergne-Rhône-Alpes", geo_range=Siae.GEO_RANGE_COUNTRY)
        SiaeFactory(city="Grenoble", department="38", region="Auvergne-Rhône-Alpes", geo_range=Siae.GEO_RANGE_REGION)
        SiaeFactory(
            city="Grenoble", department="38", region="Auvergne-Rhône-Alpes", geo_range=Siae.GEO_RANGE_DEPARTMENT
        )
        SiaeFactory(
            city="Grenoble",
            department="38",
            region="Auvergne-Rhône-Alpes",
            geo_range=Siae.GEO_RANGE_CUSTOM,
            geo_range_custom_distance=0,
            coords=Point(5.7301, 45.1825),
        )
        # La Tronche is a city located just next to Grenoble
        SiaeFactory(
            city="La Tronche",
            department="38",
            region="Auvergne-Rhône-Alpes",
            geo_range=Siae.GEO_RANGE_CUSTOM,
            geo_range_custom_distance=10,
            coords=Point(5.746, 45.2124),
        )
        # Chamrousse is a city located further away from Grenoble
        SiaeFactory(
            city="Chamrousse",
            department="38",
            region="Auvergne-Rhône-Alpes",
            geo_range=Siae.GEO_RANGE_CUSTOM,
            geo_range_custom_distance=5,
            coords=Point(5.8862, 45.1106),
        )
        SiaeFactory(city="Lyon", department="69", region="Auvergne-Rhône-Alpes", geo_range=Siae.GEO_RANGE_COUNTRY)
        SiaeFactory(city="Lyon", department="69", region="Auvergne-Rhône-Alpes", geo_range=Siae.GEO_RANGE_REGION)
        SiaeFactory(city="Lyon", department="69", region="Auvergne-Rhône-Alpes", geo_range=Siae.GEO_RANGE_DEPARTMENT)
        SiaeFactory(
            city="Lyon",
            department="69",
            region="Auvergne-Rhône-Alpes",
            geo_range=Siae.GEO_RANGE_CUSTOM,
            geo_range_custom_distance=50,
            coords=Point(4.8236, 45.7685),
        )
        SiaeFactory(city="Quimper", department="29", region="Bretagne", geo_range=Siae.GEO_RANGE_COUNTRY)
        SiaeFactory(city="Quimper", department="29", region="Bretagne", geo_range=Siae.GEO_RANGE_REGION)
        SiaeFactory(city="Quimper", department="29", region="Bretagne", geo_range=Siae.GEO_RANGE_DEPARTMENT)
        SiaeFactory(
            city="Quimper",
            department="29",
            region="Bretagne",
            geo_range=Siae.GEO_RANGE_CUSTOM,
            geo_range_custom_distance=50,
            coords=Point(-4.0916, 47.9914),
        )

    def test_search_perimeter_empty(self):
        form = SiaeSearchForm({"perimeter": "", "perimeter_name": ""})
        qs = form.filter_queryset()
        self.assertEqual(qs.count(), 14)

    def test_search_perimeter_name_empty(self):
        form = SiaeSearchForm({"perimeter": "old-search", "perimeter_name": ""})
        qs = form.filter_queryset()
        self.assertEqual(qs.count(), 14)

    def test_search_perimeter_name_not_empty(self):
        form = SiaeSearchForm({"perimeter": "", "perimeter_name": "Old Search"})
        qs = form.filter_queryset()
        self.assertEqual(qs.count(), 14)
        self.assertFalse(form.is_valid())
        self.assertIn("perimeter_name", form.errors.keys())
        self.assertIn("Périmètre inconnu", form.errors["perimeter_name"][0])

    def test_search_perimeter_region(self):
        form = SiaeSearchForm({"perimeter": "auvergne-rhone-alpes", "perimeter_name": "Auvergne-Rhône-Alpes (région)"})
        qs = form.filter_queryset()
        self.assertEqual(qs.count(), 10)

    def test_search_perimeter_department(self):
        form = SiaeSearchForm({"perimeter": "isere", "perimeter_name": "Isère (département)"})
        qs = form.filter_queryset()
        self.assertEqual(qs.count(), 6)

    def test_search_perimeter_city(self):
        """
        We should return:
        all the Siae with geo_range=GEO_RANGE_CUSTOM + coords in the geo_range_custom_distance range of Grenoble (2 SIAE: Grenoble & La Tronche. Chamrousse is outside)  # noqa
        + all the Siae with geo_range=GEO_RANGE_DEPARTMENT + department=38 (1 SIAE)
        """
        form = SiaeSearchForm({"perimeter": "grenoble-38", "perimeter_name": "Grenoble (38)"})
        qs = form.filter_queryset()
        self.assertEqual(qs.count(), 2 + 1)

    def test_search_perimeter_city_2(self):
        """
        We should return:
        all the Siae with geo_range=GEO_RANGE_CUSTOM + coords in the geo_range_custom_distance range of Grenoble (2 SIAE: Chamrousse. Grenoble & La Tronche are outside)  # noqa
        + all the Siae with geo_range=GEO_RANGE_DEPARTMENT + department=38 (1 SIAE)
        """
        form = SiaeSearchForm({"perimeter": "chamrousse-38", "perimeter_name": "Chamrousse (38)"})
        qs = form.filter_queryset()
        self.assertEqual(qs.count(), 1 + 1)


class SiaeSearchOrderTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiaeFactory(name="Ma boite")
        SiaeFactory(name="Une autre structure")
        SiaeFactory(name="ABC Insertion")

    def test_should_order_by_name(self):
        url = reverse("siae:search_results", kwargs={})
        response = self.client.get(url)
        siaes = list(response.context["siaes"])
        self.assertEqual(len(siaes), 3)
        self.assertEqual(siaes[0].name, "ABC Insertion")
        self.assertEqual(siaes[-1].name, "Une autre structure")

    def test_should_bring_the_siae_with_users_to_the_top(self):
        siae_with_user = SiaeFactory(name="ZZ ESI")
        user = UserFactory()
        siae_with_user.users.add(user)
        url = reverse("siae:search_results", kwargs={})
        response = self.client.get(url)
        siaes = list(response.context["siaes"])
        self.assertEqual(len(siaes), 3 + 1)
        self.assertEqual(siaes[0].has_user, True)
        self.assertEqual(siaes[0].name, "ZZ ESI")
        self.assertEqual(siaes[1].name, "ABC Insertion")

    def test_should_bring_the_siae_with_descriptions_to_the_top(self):
        SiaeFactory(name="ZZ ESI 2", description="coucou")
        url = reverse("siae:search_results", kwargs={})
        response = self.client.get(url)
        siaes = list(response.context["siaes"])
        self.assertEqual(len(siaes), 3 + 1)
        self.assertEqual(siaes[0].has_description, True)
        self.assertEqual(siaes[0].name, "ZZ ESI 2")
        self.assertEqual(siaes[1].name, "ABC Insertion")

    def test_should_bring_the_siae_with_offers_to_the_top(self):
        siae_with_offer = SiaeFactory(name="ZZ ESI 3")
        SiaeOfferFactory(siae=siae_with_offer)
        url = reverse("siae:search_results", kwargs={})
        response = self.client.get(url)
        siaes = list(response.context["siaes"])
        self.assertEqual(len(siaes), 3 + 1)
        self.assertEqual(siaes[0].has_offer, True)
        self.assertEqual(siaes[0].name, "ZZ ESI 3")
        self.assertEqual(siaes[1].name, "ABC Insertion")

    def test_should_bring_the_siae_closer_to_the_city_to_the_top(self):
        PerimeterFactory(
            name="Grenoble",
            kind=Perimeter.KIND_CITY,
            insee_code="38185",
            department_code="38",
            region_code="84",
            coords=Point(5.7301, 45.1825),
        )
        SiaeFactory(
            name="ZZ GEO Pontcharra",
            department="38",
            geo_range=Siae.GEO_RANGE_DEPARTMENT,
            coords=Point(6.0271, 45.4144),
        )
        SiaeFactory(
            name="ZZ GEO La Tronche",
            department="38",
            geo_range=Siae.GEO_RANGE_CUSTOM,
            geo_range_custom_distance=10,
            coords=Point(5.746, 45.2124),
        )
        SiaeFactory(
            name="ZZ GEO Grenoble",
            department="38",
            geo_range=Siae.GEO_RANGE_CUSTOM,
            geo_range_custom_distance=10,
            coords=Point(5.7301, 45.1825),
        )
        url = f"{reverse('siae:search_results')}?perimeter=grenoble-38&perimeter_name=Grenoble+%2838%29"
        response = self.client.get(url)
        siaes = list(response.context["siaes"])
        self.assertEqual(len(siaes), 3)
        self.assertEqual(siaes[0].distance.km, 0)
        self.assertEqual(siaes[0].name, "ZZ GEO Grenoble")
        self.assertEqual(siaes[1].name, "ZZ GEO La Tronche")
        self.assertEqual(siaes[2].name, "ZZ GEO Pontcharra")
