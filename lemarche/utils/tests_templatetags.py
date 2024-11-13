from django.template import Context, Template
from django.test import TestCase

from lemarche.sectors.factories import SectorFactory, SectorGroupFactory
from lemarche.siaes.factories import SiaeActivityFactory, SiaeFactory
from lemarche.utils.templatetags.siae_sectors_display import siae_sectors_display


class SiaeSectorDisplayTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        siae_with_one_sector = SiaeFactory()
        siae_with_two_sectors = SiaeFactory()
        siae_with_many_sectors = SiaeFactory()
        cls.siae_etti = SiaeFactory(kind="ETTI")
        sector_1 = SectorFactory(name="Entretien")
        sector_2 = SectorFactory(name="Agro")
        sector_3 = SectorFactory(name="Hygiène")
        sector_4 = SectorFactory(name="Bâtiment")
        sector_5 = SectorFactory(name="Informatique")

        cls.siae_activity_with_one_sector = SiaeActivityFactory(siae=siae_with_one_sector)
        cls.siae_activity_with_one_sector.sectors.add(sector_1)
        cls.siae_activity_with_two_sectors = SiaeActivityFactory(siae=siae_with_two_sectors)
        cls.siae_activity_with_two_sectors.sectors.add(sector_1, sector_2)
        cls.siae_activity_with_many_sectors = SiaeActivityFactory(siae=siae_with_many_sectors)
        cls.siae_activity_with_many_sectors.sectors.add(sector_1, sector_2, sector_3, sector_4, sector_5)

        cls.siae_etti.sectors.add(sector_1, sector_2, sector_3, sector_4, sector_5)

    def test_should_return_list_of_siae_sector_strings(self):
        self.assertEqual(siae_sectors_display(self.siae_activity_with_one_sector), "Entretien")
        self.assertEqual(
            siae_sectors_display(self.siae_activity_with_two_sectors), "Agro, Entretien"
        )  # default ordering: name
        self.assertEqual(
            siae_sectors_display(self.siae_activity_with_many_sectors),
            "Agro, Bâtiment, Entretien, Hygiène, Informatique",
        )

    def test_should_filter_list_of_siae_sectors(self):
        self.assertEqual(
            siae_sectors_display(self.siae_activity_with_many_sectors, display_max=3), "Agro, Bâtiment, Entretien, …"
        )

    def test_should_return_list_in_the_specified_format(self):
        self.assertEqual(
            siae_sectors_display(self.siae_activity_with_two_sectors, output_format="list"), ["Agro", "Entretien"]
        )
        self.assertEqual(
            siae_sectors_display(self.siae_activity_with_two_sectors, output_format="li"),
            "<li>Agro</li><li>Entretien</li>",
        )

    def test_should_have_different_behavior_for_etti(self):
        self.assertEqual(siae_sectors_display(self.siae_etti), "Multisectoriel")

    def test_should_filter_list_on_current_search_query(self):
        self.assertEqual(
            siae_sectors_display(self.siae_activity_with_one_sector, current_search_query="sectors=agro"), ""
        )
        self.assertEqual(
            siae_sectors_display(self.siae_activity_with_two_sectors, current_search_query="sectors=entretien"),
            "Entretien",
        )
        self.assertEqual(
            siae_sectors_display(
                self.siae_activity_with_many_sectors, current_search_query="sectors=entretien&sectors=agro"
            ),
            "Agro, Entretien",
        )
        # priority is on current_search (over ETTI)
        self.assertEqual(
            siae_sectors_display(self.siae_etti, current_search_query="sectors=entretien&sectors=agro"),
            "Agro, Entretien",
        )


class SiaeSectorGroupsDisplayTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae_with_one_sector = SiaeFactory()
        cls.siae_with_three_sectors = SiaeFactory()
        cls.siae_with_many_sectors = SiaeFactory()

        cls.sector_group_1 = SectorGroupFactory(name="Entretien du linge")
        cls.sector_group_2 = SectorGroupFactory(name="Espaces verts")
        cls.sector_group_3 = SectorGroupFactory(name="Bâtiment")
        cls.sector_group_4 = SectorGroupFactory(name="Agro-Alimentaire")

        sector_1 = SectorFactory(name="Blanchisserie", group=cls.sector_group_1)
        sector_2 = SectorFactory(name="Génie écologique", group=cls.sector_group_2)
        sector_3 = SectorFactory(name="Menuiserie", group=cls.sector_group_3)
        sector_4 = SectorFactory(name="Agriculture", group=cls.sector_group_4)
        sector_5 = SectorFactory(name="Plomberie", group=cls.sector_group_3)

        siae_with_one_sector_activity = SiaeActivityFactory(
            siae=cls.siae_with_one_sector, sector_group=cls.sector_group_1
        )
        siae_with_one_sector_activity.sectors.add(sector_1)

        siae_with_three_sectors_activity_1 = SiaeActivityFactory(
            siae=cls.siae_with_three_sectors, sector_group=cls.sector_group_1
        )
        siae_with_three_sectors_activity_1.sectors.add(sector_1)
        siae_with_three_sectors_activity_2 = SiaeActivityFactory(
            siae=cls.siae_with_three_sectors, sector_group=cls.sector_group_2
        )
        siae_with_three_sectors_activity_2.sectors.add(sector_2)
        siae_with_three_sectors_activity_3 = SiaeActivityFactory(
            siae=cls.siae_with_three_sectors, sector_group=cls.sector_group_3
        )
        siae_with_three_sectors_activity_3.sectors.add(sector_3, sector_5)

        siae_with_many_sectors_activity_1 = SiaeActivityFactory(
            siae=cls.siae_with_many_sectors, sector_group=cls.sector_group_1
        )
        siae_with_many_sectors_activity_1.sectors.add(sector_1)
        siae_with_many_sectors_activity_2 = SiaeActivityFactory(
            siae=cls.siae_with_many_sectors, sector_group=cls.sector_group_2
        )
        siae_with_many_sectors_activity_2.sectors.add(sector_2)
        siae_with_many_sectors_activity_3 = SiaeActivityFactory(
            siae=cls.siae_with_many_sectors, sector_group=cls.sector_group_3
        )
        siae_with_many_sectors_activity_3.sectors.add(sector_3)
        siae_with_many_sectors_activity_4 = SiaeActivityFactory(
            siae=cls.siae_with_many_sectors, sector_group=cls.sector_group_4
        )
        siae_with_many_sectors_activity_4.sectors.add(sector_4)
        siae_with_many_sectors_activity_5 = SiaeActivityFactory(
            siae=cls.siae_with_many_sectors, sector_group=cls.sector_group_3
        )
        siae_with_many_sectors_activity_5.sectors.add(sector_5)

    # Test siae_sector_groups_display if return only one sector group
    def test_should_return_html_with_siae_sector_groups(self):
        template = Template(
            "{% load siae_sectors_display %}"
            "{% siae_sector_groups_display siae display_max=3 current_sector_groups=current_sector_groups %}"
        )

        # Render the template with a context (if needed)
        rendered = template.render(Context({"siae": self.siae_with_one_sector, "current_sector_groups": []}))

        self.assertInHTML("Entretien du linge", rendered)
        self.assertNotIn("+", rendered)

        rendered = template.render(Context({"siae": self.siae_with_three_sectors, "current_sector_groups": []}))
        self.assertInHTML("Bâtiment", rendered)
        self.assertInHTML("Entretien du linge", rendered)
        self.assertInHTML("Espaces verts", rendered)
        self.assertNotIn("+", rendered)

        rendered = template.render(Context({"siae": self.siae_with_many_sectors, "current_sector_groups": []}))

        self.assertInHTML("Agro-Alimentaire", rendered)
        self.assertInHTML("Bâtiment", rendered)
        self.assertInHTML("Entretien du linge", rendered)
        self.assertInHTML("+1", rendered)

        self.assertNotIn("Espaces verts", rendered)

        rendered = template.render(
            Context(
                {
                    "siae": self.siae_with_many_sectors,
                    "current_sector_groups": [self.sector_group_3],
                }
            )
        )
        self.assertInHTML('<span class="fr-tag fr-tag--green-emeraude fr-tag--sm">Bâtiment</span>', rendered)
        self.assertInHTML("Agro-Alimentaire", rendered)
        self.assertInHTML("Entretien du linge", rendered)
        self.assertInHTML("+1", rendered)
        self.assertNotIn("Espaces verts", rendered)
