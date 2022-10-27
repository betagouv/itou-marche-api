from datetime import date, timedelta

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from lemarche.perimeters.factories import PerimeterFactory
from lemarche.sectors.factories import SectorFactory
from lemarche.siaes import constants as siae_constants
from lemarche.siaes.factories import SiaeFactory
from lemarche.siaes.models import GEO_RANGE_COUNTRY, GEO_RANGE_CUSTOM, GEO_RANGE_DEPARTMENT, Siae
from lemarche.tenders import constants as tender_constants
from lemarche.tenders.factories import TenderFactory
from lemarche.tenders.models import Tender, TenderSiae
from lemarche.users.factories import DEFAULT_PASSWORD, UserFactory
from lemarche.users.models import User
from lemarche.utils import constants


class TenderCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_siae = UserFactory(kind=User.KIND_SIAE)
        cls.user_buyer = UserFactory(kind=User.KIND_BUYER, company_name="Test")
        cls.sectors = [SectorFactory().slug for _ in range(3)]
        cls.perimeters = [PerimeterFactory().slug for _ in range(3)]

    @classmethod
    def _generate_fake_data_form(cls, _step_1={}, _step_2={}, _step_3={}, _step_4={}, tender_not_saved: Tender = None):
        if not tender_not_saved:
            tender_not_saved = TenderFactory.build(author=cls.user_buyer)

        step_1 = {
            "tender_create_multi_step_view-current_step": "general",
            "general-kind": tender_not_saved.kind,
            "general-title": tender_not_saved.title,
            "general-sectors": cls.sectors,
            "general-presta_type": siae_constants.PRESTA_BUILD,
            "general-perimeters": cls.perimeters,
            "general-is_country_area": tender_not_saved.is_country_area,
        } | _step_1
        step_2 = {
            "tender_create_multi_step_view-current_step": "description",
            "description-description": tender_not_saved.description,
            "description-start_working_date": tender_not_saved.start_working_date,
            "description-external_link": tender_not_saved.external_link,
            "description-constraints": tender_not_saved.constraints,
            "description-amount": tender_constants.AMOUNT_RANGE_1000_MORE,
        } | _step_2
        step_3 = {
            "tender_create_multi_step_view-current_step": "contact",
            "contact-contact_first_name": tender_not_saved.contact_first_name,
            "contact-contact_last_name": tender_not_saved.contact_last_name,
            "contact-contact_email": tender_not_saved.contact_email,
            # "contact-contact_phone": tender_not_saved.contact_phone,
            # "contact-contact_company_name": "TEST",
            "contact-response_kind": [Tender.RESPONSE_KIND_EMAIL],
            "contact-deadline_date": tender_not_saved.deadline_date,
        } | _step_3
        step_4 = {
            "tender_create_multi_step_view-current_step": "confirmation",
            "confirmation-is_marche_useful": True,
            "confirmation-marche_benefits": [constants.MARCHE_BENEFIT_TIME, constants.MARCHE_BENEFIT_MORE],
        } | _step_4

        return [step_1, step_2, step_3, step_4]

    def _check_every_step(self, tenders_step_data, final_redirect_page: str = reverse("pages:home")):
        for step, data_step in enumerate(tenders_step_data, 1):
            response = self.client.post(reverse("tenders:create"), data=data_step)
            if step == len(tenders_step_data):
                # make sure that after the create tender we are redirected to ??
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, final_redirect_page)
                return response, None
            else:
                self.assertEqual(response.status_code, 200)
                current_errors = response.context_data["form"].errors
                self.assertEquals(current_errors, {})
                return None, current_errors

    def test_anyone_can_access_create_tender(self):
        # anonymous
        url = reverse("tenders:create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # buyer
        self.client.login(email=self.user_buyer.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # siae
        self.client.login(email=self.user_siae.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tender_wizard_form_all_good_authenticated(self):
        tenders_step_data = self._generate_fake_data_form()
        self.client.login(email=self.user_buyer.email, password=DEFAULT_PASSWORD)
        self._check_every_step(tenders_step_data, final_redirect_page=reverse("tenders:list"))

    def test_tender_wizard_form_all_good_anonymous(self):
        tenders_step_data = self._generate_fake_data_form(
            _step_4={"contact-contact_phone": "0123456789", "contact-contact_company_name": "TEST"}
        )
        self._check_every_step(tenders_step_data, final_redirect_page=reverse("pages:home"))


class TenderMatchingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sectors = [SectorFactory() for i in range(10)]
        cls.perimeter_paris = PerimeterFactory(department_code="75", post_codes=["75019", "75018"])
        cls.perimeter_marseille = PerimeterFactory(coords=Point(43.35101634452076, 5.379616625955892))
        cls.perimeters = [cls.perimeter_paris, PerimeterFactory()]
        # by default is Paris
        coords_paris = Point(48.86385199985207, 2.337071483848432)

        siae_one = SiaeFactory(
            is_active=True,
            kind=siae_constants.KIND_AI,
            presta_type=[siae_constants.PRESTA_PREST, siae_constants.PRESTA_BUILD],
            geo_range=GEO_RANGE_CUSTOM,
            coords=coords_paris,
            geo_range_custom_distance=100,
        )
        siae_two = SiaeFactory(
            is_active=True,
            kind=siae_constants.KIND_ESAT,
            presta_type=[siae_constants.PRESTA_BUILD],
            geo_range=GEO_RANGE_CUSTOM,
            coords=coords_paris,
            geo_range_custom_distance=10,
        )
        for i in range(5):
            siae_one.sectors.add(cls.sectors[i])
            siae_two.sectors.add(cls.sectors[i + 5])

    def test_matching_siae_presta_type(self):
        tender = TenderFactory(presta_type=[], sectors=self.sectors, perimeters=self.perimeters)
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2)
        tender = TenderFactory(
            presta_type=[siae_constants.PRESTA_BUILD], sectors=self.sectors, perimeters=self.perimeters
        )
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2)
        tender = TenderFactory(
            presta_type=[siae_constants.PRESTA_PREST], sectors=self.sectors, perimeters=self.perimeters
        )
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 1)

    def test_matching_siae_kind(self):
        tender = TenderFactory(siae_kind=[], sectors=self.sectors, perimeters=self.perimeters)
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2)
        tender = TenderFactory(siae_kind=[siae_constants.KIND_AI], sectors=self.sectors, perimeters=self.perimeters)
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 1)
        tender = TenderFactory(
            siae_kind=[siae_constants.KIND_ESAT, siae_constants.KIND_AI],
            sectors=self.sectors,
            perimeters=self.perimeters,
        )
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2)
        tender = TenderFactory(siae_kind=[siae_constants.KIND_SEP], sectors=self.sectors, perimeters=self.perimeters)
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 0)

    def test_matching_siae_sectors(self):
        tender = TenderFactory(sectors=self.sectors)
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2)

    def test_with_siae_country(self):
        # add Siae with geo_range_country
        tender = TenderFactory(sectors=self.sectors, perimeters=self.perimeters)
        siae_country = SiaeFactory(is_active=True, geo_range=GEO_RANGE_COUNTRY)
        siae_country.sectors.add(self.sectors[0])
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2 + 1)

    def test_with_siae_department(self):
        # add Siae with geo_range_department (75)
        tender = TenderFactory(sectors=self.sectors, perimeters=self.perimeters)
        siae_department = SiaeFactory(is_active=True, department="75", geo_range=GEO_RANGE_DEPARTMENT)
        siae_department.sectors.add(self.sectors[0])
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2 + 1)

    def test_no_siaes(self):
        tender = TenderFactory(sectors=[SectorFactory()], perimeters=self.perimeters)
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 0)
        tender_marseille = TenderFactory(sectors=self.sectors, perimeters=[self.perimeter_marseille])
        siae_found_list_marseille = Siae.objects.filter_with_tender(tender_marseille)
        self.assertEqual(len(siae_found_list_marseille), 0)
        siae = SiaeFactory(is_active=True, department="75", geo_range=GEO_RANGE_COUNTRY)
        siae_found_list_marseille = Siae.objects.filter_with_tender(tender_marseille)
        self.assertEqual(len(siae_found_list_marseille), 0)
        # add sector
        siae.sectors.add(self.sectors[0])
        siae_found_list_marseille = Siae.objects.filter_with_tender(tender_marseille)
        self.assertEqual(len(siae_found_list_marseille), 1)

    def test_with_no_contact_email(self):
        tender = TenderFactory(sectors=self.sectors, perimeters=self.perimeters)
        SiaeFactory(is_active=True, geo_range=GEO_RANGE_COUNTRY, contact_email="", sectors=[self.sectors[0]])
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2 + 0)

    # def test_number_queries(self):
    #     tender = TenderFactory(sectors=self.sectors)
    #     with self.assertNumQueries(8):
    #         siae_found_list = Siae.objects.filter_with_tender(tender)
    #     self.assertEqual(len(siae_found_list), 2)


class TenderListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        perimeter = PerimeterFactory(post_codes=["43705"], insee_code="06", name="Auvergne-Rhône-Alpes")
        cls.siae_user_1 = UserFactory(kind=User.KIND_SIAE)
        cls.siae_1 = SiaeFactory(post_code=perimeter.post_codes[0])
        cls.siae_user_2 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_1])
        cls.user_buyer_1 = UserFactory(kind=User.KIND_BUYER)
        cls.user_buyer_2 = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.tender = TenderFactory(author=cls.user_buyer_1, validated_at=date.today(), perimeters=[perimeter])
        cls.tender_2 = TenderFactory(
            author=cls.user_buyer_1, deadline_date=date.today() - timedelta(days=5), perimeters=[perimeter]
        )
        cls.tender_3 = TenderFactory(
            author=cls.user_buyer_1,
            validated_at=date.today(),
            deadline_date=date.today() - timedelta(days=5),
            perimeters=[perimeter],
        )
        cls.tendersiae_3_1 = TenderSiae.objects.create(
            tender=cls.tender_3, siae=cls.siae_1, contact_click_date=timezone.now()
        )

    def test_anonymous_user_cannot_list_tenders(self):
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_siae_user_should_see_matching_tenders(self):
        # TODO: add more matching tests
        # user without siae
        self.client.login(email=self.siae_user_1.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 0)
        # user with siae
        self.client.login(email=self.siae_user_2.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 1)
        self.assertNotContains(response, "1 structures intéressées")  # tender_3, but only visible to author

    def test_buyer_user_should_only_see_his_tenders(self):
        self.client.login(email=self.user_buyer_1.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 3)
        self.assertContains(response, "1 structures intéressées")  # tender_3

    def test_other_user_without_tender_should_not_see_any_tenders(self):
        self.client.login(email=self.user_partner.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 0)

    def test_viewing_tender_list_should_update_stats(self):
        self.assertIsNone(self.siae_user_1.tender_list_last_seen_date)
        self.client.login(email=self.siae_user_1.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(User.objects.get(id=self.siae_user_1.id).tender_list_last_seen_date)


class TenderDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae_1 = SiaeFactory(name="ZZ ESI")
        cls.siae_user_1 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_1])
        cls.siae_user_2 = UserFactory(kind=User.KIND_SIAE)
        cls.user_buyer_1 = UserFactory(kind=User.KIND_BUYER)
        cls.user_buyer_2 = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.tender_1 = TenderFactory(author=cls.user_buyer_1)
        cls.tendersiae_1_1 = TenderSiae.objects.create(
            tender=cls.tender_1, siae=cls.siae_1, contact_click_date=timezone.now()
        )

    def test_anyone_can_view_tenders(self):
        # anonymous
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # users
        for user in User.objects.all():
            self.client.login(email=user.email, password=DEFAULT_PASSWORD)
            url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_tender_author_has_additional_stats(self):
        self.client.login(email=self.user_buyer_1.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 structures intéressées")
        # but hidden for non-author
        self.client.login(email=self.user_buyer_2.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "1 structures intéressées")

    def test_update_tendersiae_stats_on_tender_view(self):
        siae_2 = SiaeFactory(name="ABC Insertion")
        self.siae_user_2.siaes.add(siae_2)
        self.tender_1.siaes.add(siae_2)
        self.assertEqual(self.tender_1.tendersiae_set.count(), 1 + 1)
        self.assertEqual(self.tender_1.tendersiae_set.first().siae, siae_2)
        self.assertEqual(self.tender_1.tendersiae_set.last().siae, self.siae_1)
        self.assertIsNone(self.tender_1.tendersiae_set.first().detail_display_date)
        self.assertIsNone(self.tender_1.tendersiae_set.last().detail_display_date)
        # first load
        self.client.login(email=self.siae_user_2.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        siae_2_detail_display_date = self.tender_1.tendersiae_set.first().detail_display_date
        self.assertIsNotNone(siae_2_detail_display_date)
        self.assertIsNone(self.tender_1.tendersiae_set.last().detail_display_date)
        # reload doesn't update detail_display_date
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tender_1.tendersiae_set.first().detail_display_date, siae_2_detail_display_date)

    def test_create_tendersiae_stats_on_tender_view_by_new_siae(self):
        siae_2 = SiaeFactory(name="ABC Insertion")
        self.siae_user_2.siaes.add(siae_2)
        # self.tender_1.siaes.add(siae_2)
        self.assertEqual(self.tender_1.tendersiae_set.count(), 1)
        self.assertEqual(self.tender_1.tendersiae_set.first().siae, self.siae_1)
        self.assertIsNone(self.tender_1.tendersiae_set.first().detail_display_date)
        # first load
        self.client.login(email=self.siae_user_2.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tender_1.tendersiae_set.count(), 1 + 1)
        self.assertEqual(self.tender_1.tendersiae_set.first().siae, siae_2)
        self.assertIsNotNone(self.tender_1.tendersiae_set.first().detail_display_date)


class TenderDetailContactClickStatViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae = SiaeFactory(name="ZZ ESI")
        cls.siae_user_1 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae])
        cls.siae_user_2 = UserFactory(kind=User.KIND_SIAE)
        cls.user_buyer_1 = UserFactory(kind=User.KIND_BUYER)
        cls.user_buyer_2 = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.tender = TenderFactory(author=cls.user_buyer_1, siaes=[cls.siae])

    def test_anonymous_user_cannot_call_tender_contact_click(self):
        url = reverse("tenders:detail-contact-click-stat", kwargs={"slug": self.tender.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_only_siae_user_can_call_tender_contact_click(self):
        # authorized
        for user in [self.siae_user_1, self.siae_user_2]:
            self.client.login(email=user.email, password=DEFAULT_PASSWORD)
            url = reverse("tenders:detail-contact-click-stat", kwargs={"slug": self.tender.slug})
            response = self.client.post(url, data={"contact_click_confirm": "false"})
            self.assertEqual(response.status_code, 302)  # redirect
        # forbidden
        for user in [self.user_buyer_1, self.user_buyer_2, self.user_partner]:
            self.client.login(email=user.email, password=DEFAULT_PASSWORD)
            url = reverse("tenders:detail-contact-click-stat", kwargs={"slug": self.tender.slug})
            response = self.client.post(url, data={"contact_click_confirm": "false"})
            self.assertEqual(response.status_code, 403)

    def test_update_tendersiae_stats_on_tender_contact_click(self):
        siae_2 = SiaeFactory(name="ABC Insertion")
        self.siae_user_2.siaes.add(siae_2)
        self.tender.siaes.add(siae_2)
        self.assertEqual(self.tender.tendersiae_set.count(), 2)
        self.assertEqual(self.tender.tendersiae_set.first().siae, siae_2)
        self.assertEqual(self.tender.tendersiae_set.last().siae, self.siae)
        self.assertIsNone(self.tender.tendersiae_set.first().contact_click_date)
        self.assertIsNone(self.tender.tendersiae_set.last().contact_click_date)
        self.client.login(email=self.siae_user_2.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:detail-contact-click-stat", kwargs={"slug": self.tender.slug})
        response = self.client.post(url, data={"contact_click_confirm": "true"})
        self.assertEqual(response.status_code, 302)  # redirect
        siae_2_contact_click_date = self.tender.tendersiae_set.first().contact_click_date
        self.assertNotEqual(siae_2_contact_click_date, None)
        self.assertEqual(self.tender.tendersiae_set.last().contact_click_date, None)
        # clicking again on the button doesn't update contact_click_date
        # Note: button will disappear on reload
        url = reverse("tenders:detail-contact-click-stat", kwargs={"slug": self.tender.slug})
        response = self.client.post(url, data={"contact_click_confirm": "false"})
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(self.tender.tendersiae_set.first().contact_click_date, siae_2_contact_click_date)


# TODO: this test doesn't work anymore. find a way to test logging post-email in non-prod environments?
# class TenderTasksTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.tender = TenderFactory()

#     def test_send_email_for_feedbacks_set_log(self):
#         self.assertEqual(len(self.tender.logs), 0)
#         send_tenders_author_feedback_30_days(self.tender)
#         # fetch tender to be sure to have the last version of tender
#         tender: Tender = Tender.objects.get(pk=self.tender.pk)
#         self.assertEqual(len(tender.logs), 1)
#         self.assertEqual(tender.logs[0]["action"], "email_feedback_30d_sent")


class TenderSiaeInterestedListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae_1 = SiaeFactory(name="ZZ ESI")
        cls.siae_2 = SiaeFactory(name="ABC Insertion")
        cls.siae_3 = SiaeFactory(name="Une autre structure")
        cls.siae_user_1 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_1, cls.siae_2])
        cls.siae_user_2 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_3])
        cls.user_buyer_1 = UserFactory(kind=User.KIND_BUYER)
        cls.user_buyer_2 = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.tender_1 = TenderFactory(author=cls.user_buyer_1)
        cls.tender_2 = TenderFactory(author=cls.user_buyer_2)
        cls.tendersiae_1_1 = TenderSiae.objects.create(
            tender=cls.tender_1, siae=cls.siae_1, contact_click_date=timezone.now()
        )
        cls.tendersiae_1_2 = TenderSiae.objects.create(tender=cls.tender_1, siae=cls.siae_2)
        cls.tendersiae_1_3 = TenderSiae.objects.create(
            tender=cls.tender_1, siae=cls.siae_3, contact_click_date=timezone.now() - timedelta(hours=1)
        )
        cls.tendersiae_2_1 = TenderSiae.objects.create(
            tender=cls.tender_2, siae=cls.siae_2, contact_click_date=timezone.now()
        )

    def test_anonymous_user_cannot_view_tender_siae_interested_list(self):
        url = reverse("tenders:detail-siae-interested", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_only_tender_author_can_view_tender_1_siae_interested_list(self):
        # authorized
        self.client.login(email=self.user_buyer_1.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:detail-siae-interested", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tendersiaes"]), 2)
        # forbidden
        for user in [self.user_buyer_2, self.user_partner, self.siae_user_1, self.siae_user_2]:
            self.client.login(email=user.email, password=DEFAULT_PASSWORD)
            url = reverse("tenders:detail-siae-interested", kwargs={"slug": self.tender_1.slug})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/besoins/")

    def test_viewing_tender_siae_interested_list_should_update_stats(self):
        self.assertIsNone(self.tender_1.siae_interested_list_last_seen_date)
        self.client.login(email=self.user_buyer_1.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:detail-siae-interested", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tendersiaes"]), 2)
        self.assertIsNotNone(Tender.objects.get(id=self.tender_1.id).siae_interested_list_last_seen_date)

    def test_order_tender_siae_by_last_contact_click_date(self):
        # TenderSiae are ordered by -created_at by default
        self.assertEqual(self.tender_1.tendersiae_set.first().id, self.tendersiae_1_3.id)
        # but TenderSiaeInterestedListView are ordered by -contact_click_date
        self.client.login(email=self.user_buyer_1.email, password=DEFAULT_PASSWORD)
        url = reverse("tenders:detail-siae-interested", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.context["tendersiaes"][0].id, self.tendersiae_1_1.id)
