from django.test import TestCase

from lemarche.sectors.factories import SectorFactory
from lemarche.siaes.factories import SiaeFactory, SiaeLabelFactory, SiaeOfferFactory
from lemarche.siaes.models import Siae
from lemarche.users.factories import UserFactory


class SiaeModelTest(TestCase):
    def setUp(self):
        pass

    def test_str(self):
        siae = SiaeFactory(name="Ma boite")
        self.assertEqual(str(siae), "Ma boite")

    def test_name_display_property(self):
        siae_without_brand = SiaeFactory(name="Ma raison sociale")
        siae_with_brand = SiaeFactory(name="Ma raison sociale", brand="Mon enseigne")
        self.assertEqual(siae_without_brand.name_display, "Ma raison sociale")
        self.assertEqual(siae_with_brand.name_display, "Mon enseigne")

    def test_siret_display_property(self):
        siae_with_siret = SiaeFactory(siret="12312312312345")
        self.assertEqual(siae_with_siret.siret_display, "123 123 123 12345")
        siae_with_siren = SiaeFactory(siret="123123123")
        self.assertEqual(siae_with_siren.siret_display, "123 123 123")
        siae_with_anormal_siret = SiaeFactory(siret="123123123123")
        self.assertEqual(siae_with_anormal_siret.siret_display, "123123123123")

    def test_geo_range_pretty_display_property(self):
        siae_country = SiaeFactory(geo_range=Siae.GEO_RANGE_COUNTRY)
        self.assertEqual(siae_country.geo_range_pretty_display, "France entière")
        siae_region = SiaeFactory(geo_range=Siae.GEO_RANGE_REGION, region="Guadeloupe")
        self.assertEqual(siae_region.geo_range_pretty_display, "région (Guadeloupe)")
        siae_department = SiaeFactory(geo_range=Siae.GEO_RANGE_DEPARTMENT, region="Bretagne", department="29")
        self.assertEqual(siae_department.geo_range_pretty_display, "département (29)")
        siae_custom = SiaeFactory(
            geo_range=Siae.GEO_RANGE_CUSTOM,
            region="Bretagne",
            department="29",
            city="Quimper",
            geo_range_custom_distance=50,
        )
        self.assertEqual(siae_custom.geo_range_pretty_display, "50 km")
        siae_custom_empty = SiaeFactory(
            geo_range=Siae.GEO_RANGE_CUSTOM, region="Bretagne", department="29", city="Quimper"
        )
        self.assertEqual(siae_custom_empty.geo_range_pretty_display, "non disponible")

    def test_is_missing_content_property(self):
        siae_missing = SiaeFactory(name="Ma boite")
        self.assertTrue(siae_missing.is_missing_content)
        siae_full = SiaeFactory(
            name="Ma boite",
            contact_website="https://example.com",
            contact_email="email@domain.com",
            contact_phone="0000000000",
            description="test",
        )
        sector = SectorFactory()
        siae_full.sectors.add(sector)
        SiaeOfferFactory(siae=siae_full)
        SiaeLabelFactory(siae=siae_full)
        siae_full.save()  # to update stats
        self.assertFalse(siae_full.is_missing_content)


class SiaeModelSaveTest(TestCase):
    def setUp(self):
        pass

    def test_slug_field_on_save(self):
        siae = SiaeFactory(name="L'Insertion par le HAUT", department="01")
        self.assertEqual(siae.slug, "linsertion-par-le-haut-01")
        siae = SiaeFactory(name="Structure sans département", department=None)
        self.assertEqual(siae.slug, "structure-sans-departement-")
        siae = SiaeFactory(name="Structure sans département 2", department="")
        self.assertEqual(siae.slug, "structure-sans-departement-2-")
        siae_doublon_1 = SiaeFactory(name="Structure doublon", department="01")
        siae_doublon_2 = SiaeFactory(name="Structure doublon", department="15")
        siae_doublon_3 = SiaeFactory(name="Structure doublon", department="15")
        self.assertEqual(siae_doublon_1.slug, "structure-doublon-01")
        self.assertEqual(siae_doublon_2.slug, "structure-doublon-15")
        self.assertTrue(siae_doublon_3.slug.startswith("structure-doublon-15-"))  # uuid4 at the end
        self.assertTrue(len(siae_doublon_2.slug) < len(siae_doublon_3.slug))
        siae_doublon_10 = SiaeFactory(name="Structure doublon sans departement", department="")
        siae_doublon_11 = SiaeFactory(name="Structure doublon sans departement", department="")
        self.assertEqual(siae_doublon_10.slug, "structure-doublon-sans-departement-")
        self.assertTrue(siae_doublon_11.slug.startswith("structure-doublon-sans-departement--"))  # uuid4 at the end
        self.assertTrue(len(siae_doublon_10.slug) < len(siae_doublon_11.slug))

    def test_stats_on_save(self):
        siae = SiaeFactory()
        user = UserFactory()
        siae.users.add(user.id)
        self.assertEqual(siae.users.count(), 1)
        # self.assertEqual(siae.user_count, 1)  # won't work, need to call save() method to update stat fields
        siae.save()
        self.assertEqual(siae.user_count, 1)
        self.assertEqual(siae.sector_count, 0)


class SiaeModelQuerysetTest(TestCase):
    def setUp(self):
        pass

    def test_is_live_queryset(self):
        SiaeFactory(is_active=True, is_delisted=True)
        SiaeFactory(is_active=False, is_delisted=True)
        SiaeFactory(is_active=True, is_delisted=False)  # live
        SiaeFactory(is_active=False, is_delisted=False)
        self.assertEqual(Siae.objects.count(), 4)
        self.assertEqual(Siae.objects.is_live().count(), 1)
        self.assertEqual(Siae.objects.is_not_live().count(), 3)

    def test_has_user_queryset(self):
        SiaeFactory()
        siae = SiaeFactory()
        user = UserFactory()
        siae.users.add(user)
        self.assertEqual(Siae.objects.count(), 2)
        self.assertEqual(Siae.objects.has_user().count(), 1)
