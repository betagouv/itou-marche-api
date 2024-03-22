import json
from datetime import timedelta
from unittest import mock

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from sesame.utils import get_query_string as sesame_get_query_string

from lemarche.perimeters.factories import PerimeterFactory
from lemarche.perimeters.models import Perimeter
from lemarche.sectors.factories import SectorFactory
from lemarche.siaes import constants as siae_constants
from lemarche.siaes.factories import SiaeFactory
from lemarche.siaes.models import Siae
from lemarche.tenders import constants as tender_constants
from lemarche.tenders.factories import TenderFactory, TenderQuestionFactory
from lemarche.tenders.models import Tender, TenderSiae, TenderStepsData
from lemarche.users.factories import UserFactory
from lemarche.users.models import User
from lemarche.www.tenders.views import TenderCreateMultiStepView


class TenderCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_siae = UserFactory(kind=User.KIND_SIAE)
        cls.user_buyer = UserFactory(kind=User.KIND_BUYER, company_name="Entreprise Buyer")
        cls.sectors = [SectorFactory().slug for _ in range(3)]
        cls.location_slug = PerimeterFactory().slug

    @classmethod
    def _generate_fake_data_form(
        cls, _step_1={}, _step_2={}, _step_3={}, _step_4={}, _step_5={}, tender_not_saved: Tender = None
    ):
        if not tender_not_saved:
            tender_not_saved = TenderFactory.build(author=cls.user_buyer)

        step_1 = {
            "tender_create_multi_step_view-current_step": "general",
            "general-kind": tender_not_saved.kind,
            "general-title": tender_not_saved.title,
            "general-description": tender_not_saved.description,
            "general-sectors": cls.sectors,
            "general-location": cls.location_slug,
            "general-is_country_area": tender_not_saved.is_country_area,
        } | _step_1
        step_2 = {
            "tender_create_multi_step_view-current_step": "detail",
            "detail-start_working_date": tender_not_saved.start_working_date,
            "detail-deadline_date": tender_not_saved.deadline_date,
            "detail-external_link": tender_not_saved.external_link,
            "detail-amount": tender_constants.AMOUNT_RANGE_1000_MORE,
        } | _step_2
        step_3 = {
            "tender_create_multi_step_view-current_step": "contact",
            "contact-contact_first_name": tender_not_saved.contact_first_name,
            "contact-contact_last_name": tender_not_saved.contact_last_name,
            "contact-contact_email": tender_not_saved.contact_email,
            "contact-contact_phone": "0123456789",
            "contact-contact_company_name": "TEST",
            "contact-response_kind": [tender_constants.RESPONSE_KIND_EMAIL],
        } | _step_3
        step_4 = {
            "tender_create_multi_step_view-current_step": "survey",
            "survey-scale_marche_useless": tender_constants.SURVEY_SCALE_QUESTION_0,
            "survey-le_marche_doesnt_exist_how_to_find_siae": "TEST",
        } | _step_4

        step_5 = {
            "tender_create_multi_step_view-current_step": "confirmation",
        } | _step_5

        return [step_1, step_2, step_3, step_4, step_5]

    def _check_every_step(self, tenders_step_data, final_redirect_page: str = reverse("wagtail_serve", args=("",))):
        for step, data_step in enumerate(tenders_step_data, 1):
            response = self.client.post(reverse("tenders:create"), data=data_step, follow=True)
            if step == len(tenders_step_data):
                # make sure that after the create tender we are redirected to ??
                self.assertEqual(response.status_code, 200)
                self.assertRedirects(response, final_redirect_page)
                # has the step datas been cleaned ?
                self.assertEqual(TenderStepsData.objects.count(), 0)
                return response
            else:
                self.assertEqual(response.status_code, 200)
                current_errors = response.context_data["form"].errors
                self.assertEquals(current_errors, {})

                # Is the step data stored correctly ?
                tender_step_data = TenderStepsData.objects.first()
                self.assertEqual(
                    data_step["tender_create_multi_step_view-current_step"],
                    tender_step_data.steps_data[-1]["tender_create_multi_step_view-current_step"],
                )

    def test_anyone_can_access_create_tender(self):
        # anonymous user
        url = reverse("tenders:create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # user buyer
        self.client.force_login(self.user_buyer)
        url = reverse("tenders:create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # user siae
        self.client.force_login(self.user_siae)
        url = reverse("tenders:create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tender_wizard_form_all_good_authenticated(self):
        tenders_step_data = self._generate_fake_data_form()
        self.client.force_login(self.user_buyer)
        final_response = self._check_every_step(tenders_step_data, final_redirect_page=reverse("siae:search_results"))
        tender = Tender.objects.get(title=tenders_step_data[0].get("general-title"))
        self.assertIsNotNone(tender)
        self.assertIsInstance(tender, Tender)
        messages = list(get_messages(final_response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            TenderCreateMultiStepView.get_success_message(
                TenderCreateMultiStepView, tenders_step_data, tender, is_draft=False
            ),
        )
        self.assertEqual(tender.contact_first_name, self.user_buyer.first_name)
        self.assertEqual(tender.contact_last_name, self.user_buyer.last_name)
        self.assertEqual(tender.contact_email, self.user_buyer.email)
        self.assertEqual(tender.contact_phone, self.user_buyer.phone)

    def test_tender_wizard_form_not_created(self):
        self.client.force_login(self.user_buyer)
        tenders_step_data = self._generate_fake_data_form()
        # remove required field in survey
        tenders_step_data[3].pop("survey-scale_marche_useless")
        with self.assertRaises(AssertionError):
            self._check_every_step(tenders_step_data, final_redirect_page=reverse("siae:search_results"))

    def test_tender_wizard_form_external_link_required_for_tender(self):
        self.client.force_login(self.user_buyer)
        tenders_step_data = self._generate_fake_data_form(_step_1={"general-kind": tender_constants.KIND_TENDER})
        # remove required field in survey
        tenders_step_data[1].pop("detail-external_link")
        with self.assertRaises(AssertionError):
            self._check_every_step(tenders_step_data, final_redirect_page=reverse("siae:search_results"))

    def test_tender_wizard_form_contact_response_required_for_project(self):
        self.client.force_login(self.user_buyer)
        tenders_step_data = self._generate_fake_data_form(_step_1={"general-kind": tender_constants.KIND_PROJECT})
        # remove required field in survey
        tenders_step_data[2].pop("contact-response_kind")
        with self.assertRaises(AssertionError):
            self._check_every_step(tenders_step_data, final_redirect_page=reverse("siae:search_results"))

    def test_tender_wizard_form_all_good_anonymous(self):
        tenders_step_data = self._generate_fake_data_form()
        final_response = self._check_every_step(tenders_step_data, final_redirect_page=reverse("siae:search_results"))
        tender = Tender.objects.get(title=tenders_step_data[0].get("general-title"))
        self.assertIsNotNone(tender)
        self.assertIsInstance(tender, Tender)
        self.assertEqual(tender.status, tender_constants.STATUS_PUBLISHED)
        self.assertIsNotNone(tender.published_at)
        messages = list(get_messages(final_response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            TenderCreateMultiStepView.get_success_message(
                TenderCreateMultiStepView, tenders_step_data, tender, is_draft=False
            ),
        )

    def test_tender_wizard_form_all_good_perimeters(self):
        self.client.force_login(self.user_buyer)
        tenders_step_data = self._generate_fake_data_form()
        self._check_every_step(tenders_step_data, final_redirect_page=reverse("siae:search_results"))
        tender: Tender = Tender.objects.get(title=tenders_step_data[0].get("general-title"))
        self.assertIsNotNone(tender)
        self.assertIsInstance(tender, Tender)
        self.assertEqual(tender.location.slug, self.location_slug)
        tender_list_perimeter_id = [perimeter.slug for perimeter in tender.perimeters.all()]
        self.assertEqual(len(tender_list_perimeter_id), 1)
        self.assertEqual(tender_list_perimeter_id, [self.location_slug])
        tenders_sectors = tender.sectors.all()
        tender_list_sector_slug = [sector.slug for sector in tenders_sectors]
        self.assertEqual(len(tender_list_sector_slug), tenders_sectors.count())
        self.assertEqual(tender_list_sector_slug.sort(), self.sectors.sort())

    def test_tender_wizard_form_draft(self):
        tenders_step_data = self._generate_fake_data_form(_step_5={"is_draft": "1"})
        final_response = self._check_every_step(tenders_step_data, final_redirect_page=reverse("siae:search_results"))
        tender: Tender = Tender.objects.get(title=tenders_step_data[0].get("general-title"))
        self.assertIsNotNone(tender)
        self.assertIsInstance(tender, Tender)
        self.assertEqual(tender.status, tender_constants.STATUS_DRAFT)
        self.assertIsNone(tender.published_at)
        messages = list(get_messages(final_response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            TenderCreateMultiStepView.get_success_message(
                TenderCreateMultiStepView, tenders_step_data, tender, is_draft=True
            ),
        )

    def test_tender_wizard_form_questions_list(self):
        initial_data_questions_list = [
            {"text": "Avez-vous suffisamment d'effectifs ? "},
            {"text": "Êtes-vous disponible tout l'été ? "},
        ]
        tenders_step_data = self._generate_fake_data_form(
            _step_2={"detail-questions_list": json.dumps(initial_data_questions_list)}  # json field
        )

        self._check_every_step(tenders_step_data, final_redirect_page=reverse("siae:search_results"))
        tender: Tender = Tender.objects.get(title=tenders_step_data[0].get("general-title"))
        self.assertIsNotNone(tender)
        self.assertIsInstance(tender, Tender)
        self.assertEqual(tender.questions.count(), len(initial_data_questions_list))  # count is 2
        self.assertEqual(tender.questions_list()[0].get("text"), initial_data_questions_list[0].get("text"))


class TenderMatchingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sectors = [SectorFactory() for i in range(10)]
        cls.perimeter_paris = PerimeterFactory(department_code="75", post_codes=["75019", "75018"])
        cls.perimeter_marseille = PerimeterFactory(coords=Point(43.35101634452076, 5.379616625955892))
        cls.perimeters = [cls.perimeter_paris, PerimeterFactory()]
        # by default is Paris
        coords_paris = Point(48.86385199985207, 2.337071483848432)

        cls.siae_one = SiaeFactory(
            is_active=True,
            kind=siae_constants.KIND_AI,
            presta_type=[siae_constants.PRESTA_PREST, siae_constants.PRESTA_BUILD],
            geo_range=siae_constants.GEO_RANGE_CUSTOM,
            coords=coords_paris,
            geo_range_custom_distance=100,
        )
        cls.siae_two = SiaeFactory(
            is_active=True,
            kind=siae_constants.KIND_ESAT,
            presta_type=[siae_constants.PRESTA_BUILD],
            geo_range=siae_constants.GEO_RANGE_CUSTOM,
            coords=coords_paris,
            geo_range_custom_distance=10,
        )
        for i in range(5):
            cls.siae_one.sectors.add(cls.sectors[i])
            cls.siae_two.sectors.add(cls.sectors[i + 5])

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

    def test_matching_siae_distance_location(self):
        # create SIAE in Tours
        siae_tours = SiaeFactory(
            is_active=True,
            kind=siae_constants.KIND_AI,
            presta_type=[siae_constants.PRESTA_PREST, siae_constants.PRESTA_BUILD],
            coords=Point(47.392287, 0.690049),  # Tours city
        )
        siae_tours.sectors.add(self.sectors[0])

        # create SIAE in Marseille
        siae_marseille = SiaeFactory(
            is_active=True,
            kind=siae_constants.KIND_AI,
            presta_type=[siae_constants.PRESTA_PREST, siae_constants.PRESTA_BUILD],
            coords=self.perimeter_marseille.coords,
            geo_range=siae_constants.GEO_RANGE_COUNTRY,
        )
        siae_marseille.sectors.add(self.sectors[0])

        # create tender in Azay-le-rideau (near Tours ~25km)
        perimeter_azaylerideau = PerimeterFactory(coords=Point(47.262352, 0.466372))
        tender = TenderFactory(
            location=perimeter_azaylerideau,
            distance_location=30,
            siae_kind=[siae_constants.KIND_ESAT, siae_constants.KIND_AI],
            sectors=self.sectors,
        )
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 1)
        self.assertIn(siae_tours, siae_found_list)

        # Azay-le-rideau is less than 240km from Paris but more 550km from Marseille
        tender = TenderFactory(
            location=perimeter_azaylerideau,
            distance_location=300,
            siae_kind=[siae_constants.KIND_ESAT, siae_constants.KIND_AI],
            sectors=self.sectors,
            perimeters=[self.perimeter_paris],  # test this option without effect when the distance is setted
        )
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 3)
        self.assertIn(siae_tours, siae_found_list)
        self.assertIn(self.siae_one, siae_found_list)
        self.assertIn(self.siae_two, siae_found_list)

        # unset distance location, perimeters is used instead, Paris as it happens
        tender.distance_location = None
        tender.save()
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2)
        self.assertIn(self.siae_one, siae_found_list)
        self.assertIn(self.siae_two, siae_found_list)

        # set distance location and include country
        tender = TenderFactory(
            location=perimeter_azaylerideau,
            distance_location=50,
            siae_kind=[siae_constants.KIND_ESAT, siae_constants.KIND_AI],
            sectors=self.sectors,
            include_country_area=True,
        )
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2)
        self.assertIn(siae_tours, siae_found_list)
        self.assertIn(siae_marseille, siae_found_list)

        # set a department in location disable distance_location, perimeters is used instead
        tender = TenderFactory(
            location=PerimeterFactory(
                name="Indre-et-loire", kind=Perimeter.KIND_DEPARTMENT, insee_code="37", region_code="24"
            ),
            distance_location=50,
            siae_kind=[siae_constants.KIND_ESAT, siae_constants.KIND_AI],
            sectors=self.sectors,
            include_country_area=True,  # check this option without effect when the distance is setted
            perimeters=[self.perimeter_paris],  # without effect too
        )
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 3)
        self.assertIn(self.siae_one, siae_found_list)
        self.assertIn(self.siae_two, siae_found_list)
        self.assertIn(siae_marseille, siae_found_list)

    def test_matching_siae_perimeters_custom(self):
        # add Siae with geo_range_country
        siae_country = SiaeFactory(is_active=True, geo_range=siae_constants.GEO_RANGE_COUNTRY)
        siae_country.sectors.add(self.sectors[0])
        # tender perimeter custom with include_country_area = False
        tender_1 = TenderFactory(sectors=self.sectors, perimeters=self.perimeters)
        siae_found_list = Siae.objects.filter_with_tender(tender_1)
        self.assertEqual(len(siae_found_list), 2 + 0)
        # tender perimeter custom with include_country_area = True
        tender_2 = TenderFactory(sectors=self.sectors, perimeters=self.perimeters, include_country_area=True)
        siae_found_list = Siae.objects.filter_with_tender(tender_2)
        self.assertEqual(len(siae_found_list), 2 + 1)

    def test_matching_siae_country(self):
        # add Siae with geo_range_country
        siae_country = SiaeFactory(is_active=True, geo_range=siae_constants.GEO_RANGE_COUNTRY)
        siae_country_2 = SiaeFactory(is_active=True, geo_range=siae_constants.GEO_RANGE_COUNTRY)
        siae_country.sectors.add(self.sectors[0])
        siae_country_2.sectors.add(self.sectors[0])
        # tender perimeter custom with is_country_area = False
        tender_1 = TenderFactory(sectors=self.sectors, is_country_area=True)
        siae_found_list_1 = Siae.objects.filter_with_tender(tender_1)
        self.assertEqual(len(siae_found_list_1), 2)
        # tender perimeter custom with include_country_area = True
        tender_2 = TenderFactory(sectors=self.sectors, include_country_area=True)
        siae_found_list_2 = Siae.objects.filter_with_tender(tender_2)
        # we should have the same length of structures
        self.assertEqual(len(siae_found_list_1), len(siae_found_list_2))
        # add perimeters
        tender_2.perimeters.set(self.perimeters)
        siae_found_list_2 = Siae.objects.filter_with_tender(tender_2)
        self.assertEqual(len(siae_found_list_2), 2 + 2)
        tender_2.is_country_area = True
        tender_2.save()
        siae_found_list_2 = Siae.objects.filter_with_tender(tender_2)
        # we should have only siaes with country geo range
        self.assertEqual(len(siae_found_list_2), 2 + 0)

    def test_matching_siae_perimeters_custom_2(self):
        # add Siae with geo_range_department (75)
        siae_department = SiaeFactory(is_active=True, department="75", geo_range=siae_constants.GEO_RANGE_DEPARTMENT)
        siae_department.sectors.add(self.sectors[0])
        # tender perimeter custom
        tender = TenderFactory(sectors=self.sectors, perimeters=self.perimeters)
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 2 + 1)

    def test_matching_siae_perimeters_france(self):
        # tender france
        tender = TenderFactory(sectors=self.sectors, is_country_area=True)
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 0)
        # add Siae with geo_range_country
        siae_country = SiaeFactory(is_active=True, geo_range=siae_constants.GEO_RANGE_COUNTRY)
        siae_country.sectors.add(self.sectors[0])
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 1)

    def test_no_siaes(self):
        # tender with empty sectors list
        tender = TenderFactory(sectors=[SectorFactory()], perimeters=self.perimeters)
        siae_found_list = Siae.objects.filter_with_tender(tender)
        self.assertEqual(len(siae_found_list), 0)
        # tender near Marseille
        tender_marseille = TenderFactory(sectors=self.sectors, perimeters=[self.perimeter_marseille])
        siae_found_list_marseille = Siae.objects.filter_with_tender(tender_marseille)
        self.assertEqual(len(siae_found_list_marseille), 0)

    def test_with_no_contact_email(self):
        tender = TenderFactory(sectors=self.sectors, perimeters=self.perimeters)
        SiaeFactory(
            is_active=True, geo_range=siae_constants.GEO_RANGE_COUNTRY, contact_email="", sectors=[self.sectors[0]]
        )
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
        cls.siae_1 = SiaeFactory()
        cls.siae_2 = SiaeFactory(post_code=perimeter.post_codes[0])
        cls.siae_user_2 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_1])
        cls.user_buyer_1 = UserFactory(kind=User.KIND_BUYER, company_name="Entreprise Buyer")
        cls.user_buyer_2 = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.tender = TenderFactory(author=cls.user_buyer_1, perimeters=[perimeter])
        cls.tender_2 = TenderFactory(
            author=cls.user_buyer_1, deadline_date=timezone.now() - timedelta(days=5), perimeters=[perimeter]
        )
        cls.tender_3 = TenderFactory(
            author=cls.user_buyer_1,
            amount=tender_constants.AMOUNT_RANGE_100_150,
            accept_share_amount=False,
            deadline_date=timezone.now() - timedelta(days=5),
            perimeters=[perimeter],
        )
        cls.tendersiae_3_1 = TenderSiae.objects.create(
            tender=cls.tender_3, siae=cls.siae_1, email_send_date=timezone.now()
        )
        cls.tendersiae_3_2 = TenderSiae.objects.create(
            tender=cls.tender_3,
            siae=cls.siae_2,
            email_send_date=timezone.now(),
            detail_contact_click_date=timezone.now(),
        )
        cls.tender_4 = TenderFactory(
            author=cls.user_buyer_1, perimeters=[perimeter], kind=tender_constants.KIND_TENDER
        )
        cls.tendersiae_4_1 = TenderSiae.objects.create(
            tender=cls.tender_4, siae=cls.siae_1, email_send_date=timezone.now()
        )

    def test_anonymous_user_cannot_list_tenders(self):
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_siae_user_should_see_matching_tenders(self):
        # TODO: add more matching tests
        # user without siae
        self.client.force_login(self.siae_user_1)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 0)
        # user with siae
        self.client.force_login(self.siae_user_2)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 2)
        self.assertContains(response, self.tender_3.title)
        self.assertContains(response, self.tender_4.title)
        self.assertContains(response, "Entreprise Buyer")
        self.assertNotContains(response, "K€")  # !accept_share_amount
        self.assertNotContains(response, "2 prestataires ciblés")  # tender_3, but only visible to author
        self.assertNotContains(response, "1 prestataire intéressé")  # tender_3, but only visible to author

    def test_buyer_user_should_only_see_his_tenders(self):
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 4)
        self.assertContains(response, "2 prestataires ciblés")  # tender_3
        self.assertContains(response, "1 prestataire intéressé")  # tender_3
        self.assertNotContains(response, "Demandes reçues")
        self.assertNotContains(
            response, '<span class="float-right badge badge-sm badge-pill badge-new">Nouveau</span>'
        )

    def test_other_user_without_tender_should_not_see_any_tenders(self):
        self.client.force_login(self.user_partner)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 0)

    def test_viewing_tender_list_should_update_stats(self):
        self.assertIsNone(self.siae_user_1.tender_list_last_seen_date)
        self.client.force_login(self.siae_user_1)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(User.objects.get(id=self.siae_user_1.id).tender_list_last_seen_date)

    def test_siae_user_should_see_unread_badge(self):
        self.client.force_login(self.siae_user_2)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 2)
        # The badge in header, only one because one is outdated
        self.assertContains(response, 'Demandes reçues <span class="badge badge-pill badge-important fs-xs">1</span>')
        # The badge in tender list
        self.assertContains(
            response, '<span class="float-right badge badge-sm badge-pill badge-new">Nouveau</span>', 1
        )

        # Open tender detail page
        detail_url = reverse("tenders:detail", kwargs={"slug": self.tender_4.slug})
        self.client.get(detail_url)

        # The badges have disappeared
        response = self.client.get(url)
        self.assertNotContains(
            response, 'Demandes reçues <span class="badge badge-pill badge-important fs-xs">1</span>'
        )
        self.assertNotContains(
            response, '<span class="float-right badge badge-sm badge-pill badge-new">Nouveau</span>'
        )

    def test_siae_user_should_only_see_filtered_kind(self):
        self.client.force_login(self.siae_user_2)
        url = reverse("tenders:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 2)
        self.assertContains(
            response,
            f'<option value="{tender_constants.KIND_QUOTE}">{tender_constants.KIND_QUOTE_DISPLAY}</option>',
            1,
            html=True,
        )
        self.assertContains(
            response,
            f'<option value="{tender_constants.KIND_TENDER}">{tender_constants.KIND_TENDER_DISPLAY} (1)</option>',
            1,
            html=True,
        )

        url = reverse("tenders:list")
        response = self.client.get(f"{url}?kind={tender_constants.KIND_TENDER}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tenders"]), 1)
        self.assertEqual(response.context["tenders"][0], self.tender_4)
        expected_option = (
            f'<option value="{tender_constants.KIND_TENDER}" selected>'
            f"{tender_constants.KIND_TENDER_DISPLAY} (1)</option>"
        )
        self.assertContains(response, expected_option, 1, html=True)


class TenderDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae_1 = SiaeFactory(name="ZZ ESI")
        cls.siae_2 = SiaeFactory(name="ABC Insertion")
        cls.siae_3 = SiaeFactory(name="ABC Insertion bis")
        cls.siae_4 = SiaeFactory(name="ESAT 4")
        cls.siae_5 = SiaeFactory(name="ESAT 5")
        cls.siae_6 = SiaeFactory(name="ESAT 6")
        cls.siae_user_1 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_1])
        cls.siae_user_2 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_2, cls.siae_3])
        cls.siae_user_4 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_4])
        cls.siae_user_5 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_5])
        cls.siae_user_6 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_6])
        cls.siae_user_without_siae = UserFactory(kind=User.KIND_SIAE)
        cls.user_buyer_1 = UserFactory(kind=User.KIND_BUYER, company_name="Entreprise Buyer")
        cls.user_buyer_2 = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.user_admin = UserFactory(kind=User.KIND_ADMIN)
        sector_1 = SectorFactory(name="Bricolage")
        grenoble_perimeter = PerimeterFactory(
            name="Grenoble",
            kind=Perimeter.KIND_CITY,
            insee_code="38185",
            department_code="38",
            region_code="84",
            post_codes=["38000", "38100", "38700"],
            # coords=Point(5.7301, 45.1825),
        )
        cls.tender_1 = TenderFactory(
            kind=tender_constants.KIND_TENDER,
            author=cls.user_buyer_1,
            amount=tender_constants.AMOUNT_RANGE_100_150,
            accept_share_amount=True,
            response_kind=[tender_constants.RESPONSE_KIND_EMAIL],
            sectors=[sector_1],
            location=grenoble_perimeter,
            status=tender_constants.STATUS_SENT,
            first_sent_at=timezone.now(),
        )
        cls.tendersiae_1_1 = TenderSiae.objects.create(
            tender=cls.tender_1,
            siae=cls.siae_1,
            source="EMAIL",
            email_send_date=timezone.now(),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
            detail_contact_click_date=timezone.now(),
        )
        cls.tendersiae_1_4 = TenderSiae.objects.create(
            tender=cls.tender_1,
            siae=cls.siae_4,
            source="EMAIL",
            email_send_date=timezone.now(),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
            detail_cocontracting_click_date=timezone.now(),
        )
        cls.tendersiae_1_5 = TenderSiae.objects.create(
            tender=cls.tender_1,
            siae=cls.siae_5,
            source="EMAIL",
            email_send_date=timezone.now(),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
            detail_not_interested_click_date=timezone.now(),
        )
        TenderQuestionFactory(tender=cls.tender_1)
        cls.tender_2 = TenderFactory(
            author=cls.user_buyer_1,
            contact_company_name="Another company",
            status=tender_constants.STATUS_SENT,
            first_sent_at=timezone.now(),
        )
        cls.tender_3_response_is_anonymous = TenderFactory(
            kind=tender_constants.KIND_TENDER,
            author=cls.user_buyer_1,
            contact_company_name="Another company",
            status=tender_constants.STATUS_SENT,
            first_sent_at=timezone.now(),
            response_is_anonymous=True,
        )
        cls.tendersiae_3_1 = TenderSiae.objects.create(
            tender=cls.tender_3_response_is_anonymous,
            siae=cls.siae_1,
            source="EMAIL",
            email_send_date=timezone.now(),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
            detail_contact_click_date=timezone.now(),
        )
        cls.tendersiae_3_4 = TenderSiae.objects.create(
            tender=cls.tender_3_response_is_anonymous,
            siae=cls.siae_4,
            source="EMAIL",
            email_send_date=timezone.now(),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
            detail_cocontracting_click_date=timezone.now(),
        )
        cls.tendersiae_3_5 = TenderSiae.objects.create(
            tender=cls.tender_3_response_is_anonymous,
            siae=cls.siae_5,
            source="EMAIL",
            email_send_date=timezone.now(),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
            detail_not_interested_click_date=timezone.now(),
        )

    def test_anyone_can_view_sent_tenders(self):
        for tender in Tender.objects.all():
            # anonymous user
            url = reverse("tenders:detail", kwargs={"slug": tender.slug})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, tender.title)
            # users
            for user in User.objects.all():
                self.client.force_login(user)
                url = reverse("tenders:detail", kwargs={"slug": tender.slug})
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_only_author_or_admin_can_view_non_sent_tender(self):
        tender_draft = TenderFactory(author=self.user_buyer_1, status=tender_constants.STATUS_DRAFT)
        tender_published = TenderFactory(
            author=self.user_buyer_1, status=tender_constants.STATUS_PUBLISHED, published_at=timezone.now()
        )
        tender_validated_but_not_sent = TenderFactory(
            author=self.user_buyer_1,
            status=tender_constants.STATUS_VALIDATED,
            published_at=timezone.now(),
            validated_at=timezone.now(),
        )
        for tender in [tender_draft, tender_published, tender_validated_but_not_sent]:
            # anonymous user
            url = reverse("tenders:detail", kwargs={"slug": tender.slug})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            # self.assertContains(response.url, "/accounts/login/?next=/besoins/")
            # author & admin
            for user in [self.user_buyer_1, self.user_admin]:
                self.client.force_login(user)
                url = reverse("tenders:detail", kwargs={"slug": tender.slug})
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
            # other users
            for user in [self.siae_user_1, self.user_buyer_2, self.user_partner]:
                self.client.force_login(user)
                url = reverse("tenders:detail", kwargs={"slug": tender.slug})
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, "/")

    def test_tender_unknown_should_return_404(self):
        url = reverse("tenders:detail", kwargs={"slug": f"{self.tender_1.slug}-bug"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_tender_basic_fields_display(self):
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # sector
        self.assertContains(response, "Bricolage")
        # localisation
        self.assertContains(response, "Grenoble")
        # company_name
        self.assertContains(response, "Entreprise Buyer")  # tender.author.company_name
        url = reverse("tenders:detail", kwargs={"slug": self.tender_2.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Another company")  # tender.contact_company_name

    def test_tender_questions_display(self):
        # tender with questions: section should be visible
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Questions du client")
        # author has different wording
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Questions à poser aux prestataires ciblés")
        # tender without questions: section should be hidden
        tender_2 = TenderFactory(author=self.user_buyer_2, constraints="")
        url = reverse("tenders:detail", kwargs={"slug": tender_2.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Questions à poser aux prestataires ciblés")
        self.assertNotContains(response, "Questions du client")

    def test_tender_constraints_display(self):
        # tender with constraints: section should be visible
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Comment répondre à cette demande ?")
        # tender without constraints: section should be hidden
        tender_2 = TenderFactory(author=self.user_buyer_2, constraints="")
        url = reverse("tenders:detail", kwargs={"slug": tender_2.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Comment répondre à cette demande ?")

    def test_tender_amount_display(self):
        # tender with amount + accept_share_amount: section should be visible
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Budget du client")
        # author has different wording
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Montant du marché")
        self.assertContains(response, tender_constants.ACCEPT_SHARE_AMOUNT_TRUE)
        # tender with amount + !accept_share_amount: section should be hidden
        tender_2 = TenderFactory(
            author=self.user_buyer_2, amount=tender_constants.AMOUNT_RANGE_100_150, accept_share_amount=False
        )
        url = reverse("tenders:detail", kwargs={"slug": tender_2.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Montant du marché")
        self.assertNotContains(response, "Budget du client")
        # author has section
        self.client.force_login(self.user_buyer_2)
        url = reverse("tenders:detail", kwargs={"slug": tender_2.slug})
        response = self.client.get(url)
        self.assertContains(response, "Montant du marché")
        self.assertContains(response, tender_constants.ACCEPT_SHARE_AMOUNT_FALSE)

    def test_tender_author_has_additional_stats(self):
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "3 prestataires ciblés")
        self.assertContains(response, "1 prestataire intéressé")
        # but hidden for non-author
        self.client.force_login(self.user_buyer_2)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertNotContains(response, "3 prestataires ciblés")
        self.assertNotContains(response, "1 prestataire intéressé")

    def test_admin_has_extra_info(self):
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        # anonymous user
        response = self.client.get(url)
        self.assertNotContains(response, "Informations Admin")
        # other users
        for user in [self.user_buyer_1, self.user_partner, self.siae_user_1]:
            self.client.force_login(user)
            response = self.client.get(url)
            self.assertNotContains(response, "Informations Admin")
        # admin
        self.client.force_login(self.user_admin)
        response = self.client.get(url)
        self.assertContains(response, "Informations Admin")

    def test_tender_contact_display(self):
        # anonymous user
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertContains(response, "Répondre en co-traitance ?")
        self.assertContains(response, "Cette demande ne vous intéresse pas ?")
        # siae user interested
        self.client.force_login(self.siae_user_1)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertContains(response, "Contactez le client dès maintenant")
        self.assertContains(response, "Répondre en co-traitance ?")
        self.assertNotContains(response, "votre intérêt a bien été signalé au client")
        self.assertNotContains(response, "Cette demande ne vous intéresse pas ?")
        # siae user cocontracting
        self.client.force_login(self.siae_user_4)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertNotContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, "Répondre en co-traitance ?")
        self.assertContains(response, "votre intérêt a bien été signalé au client")
        self.assertNotContains(response, "Cette demande ne vous intéresse pas ?")
        # siae user not interested
        self.client.force_login(self.siae_user_5)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertNotContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, "Répondre en co-traitance ?")
        self.assertNotContains(response, "Cette demande ne vous intéresse pas ?")
        self.assertContains(response, "Vous n'êtes pas intéressé par ce besoin")
        # siae user not concerned
        self.client.force_login(self.siae_user_6)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertContains(response, "Répondre en co-traitance ?")
        self.assertContains(response, "Cette demande ne vous intéresse pas ?")
        # siae user without siae
        self.client.force_login(self.siae_user_without_siae)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "veuillez d'abord vous")
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertNotContains(response, "Répondre en co-traitance ?")
        self.assertNotContains(response, "Cette demande ne vous intéresse pas ?")
        # author
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Coordonnées")
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertNotContains(response, "Répondre en co-traitance ?")
        self.assertNotContains(response, "Cette demande ne vous intéresse pas ?")

    def test_tender_response_is_anonymous_contact_display(self):
        # anonymous user
        url = reverse("tenders:detail", kwargs={"slug": self.tender_3_response_is_anonymous.slug})
        response = self.client.get(url)
        self.assertContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertContains(response, "Répondre en co-traitance ?")
        self.assertContains(response, "Cette demande ne vous intéresse pas ?")
        # siae user interested
        self.client.force_login(self.siae_user_1)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_3_response_is_anonymous.slug})
        response = self.client.get(url)
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertNotContains(response, "Contactez le client dès maintenant")
        self.assertContains(response, "Votre intérêt a été signalé au client")
        self.assertContains(response, "Répondre en co-traitance ?")
        self.assertNotContains(response, "votre intérêt a bien été signalé au client")
        self.assertNotContains(response, "Cette demande ne vous intéresse pas ?")
        # siae user cocontracting
        self.client.force_login(self.siae_user_4)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_3_response_is_anonymous.slug})
        response = self.client.get(url)
        self.assertContains(response, "Cet appel d'offres vous intéresse ?")  # TODO: fix
        self.assertNotContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, "Répondre en co-traitance ?")
        self.assertContains(response, "votre intérêt a bien été signalé au client")
        self.assertNotContains(response, "Cette demande ne vous intéresse pas ?")
        # siae user not interested
        self.client.force_login(self.siae_user_5)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_3_response_is_anonymous.slug})
        response = self.client.get(url)
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertNotContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, "Répondre en co-traitance ?")
        self.assertNotContains(response, "Cette demande ne vous intéresse pas ?")
        self.assertContains(response, "Vous n'êtes pas intéressé par ce besoin")
        # siae user not concerned
        self.client.force_login(self.siae_user_6)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_3_response_is_anonymous.slug})
        response = self.client.get(url)
        self.assertContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertContains(response, "Répondre en co-traitance ?")
        self.assertContains(response, "Cette demande ne vous intéresse pas ?")
        # siae user without siae
        self.client.force_login(self.siae_user_without_siae)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_3_response_is_anonymous.slug})
        response = self.client.get(url)
        self.assertContains(response, "veuillez d'abord vous")
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")
        # author
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_3_response_is_anonymous.slug})
        response = self.client.get(url)
        self.assertContains(response, "Coordonnées")
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")

    def test_tender_outdated_contact_display(self):
        tender_2 = TenderFactory(
            kind=tender_constants.KIND_QUOTE,
            author=self.user_buyer_1,
            deadline_date=timezone.now() - timedelta(days=1),
        )
        TenderSiae.objects.create(tender=tender_2, siae=self.siae_1, detail_contact_click_date=timezone.now())
        # anonymous user
        url = reverse("tenders:detail", kwargs={"slug": tender_2.slug})
        response = self.client.get(url)
        self.assertNotContains(response, "Répondre à cette opportunité")
        # siae user interested
        self.client.force_login(self.siae_user_1)
        url = reverse("tenders:detail", kwargs={"slug": tender_2.slug})
        response = self.client.get(url)
        self.assertNotContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, "Répondre à cette opportunité")
        # siae user not concerned
        self.client.force_login(self.siae_user_6)
        url = reverse("tenders:detail", kwargs={"slug": tender_2.slug})
        response = self.client.get(url)
        self.assertNotContains(response, "Répondre à cette opportunité")
        # siae user without siae
        self.client.force_login(self.siae_user_without_siae)
        url = reverse("tenders:detail", kwargs={"slug": tender_2.slug})
        response = self.client.get(url)
        self.assertNotContains(response, "veuillez d'abord vous")
        self.assertNotContains(response, "Répondre à cette opportunité")
        # author
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail", kwargs={"slug": tender_2.slug})
        response = self.client.get(url)
        self.assertContains(response, "Coordonnées")
        self.assertNotContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, "Répondre à cette opportunité")

    def test_some_partners_can_display_contact_details(self):
        # this partner cannot
        self.client.force_login(self.user_partner)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "pour être mis en relation avec le client.")
        self.assertNotContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")
        # this one can!
        user_partner_2 = UserFactory(kind=User.KIND_PARTNER, can_display_tender_contact_details=True)
        self.client.force_login(user_partner_2)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertNotContains(response, "pour être mis en relation avec le client.")
        self.assertContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")

    def test_tender_contact_details_display(self):
        # tender_1 author
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Coordonnées")
        self.assertContains(response, self.tender_1.contact_email)  # RESPONSE_KIND_EMAIL
        self.assertNotContains(response, self.tender_1.contact_phone)
        self.assertNotContains(response, settings.TEAM_CONTACT_EMAIL)
        self.assertNotContains(response, "Cet appel d'offres vous intéresse ?")
        self.assertNotContains(response, "Lien partagé")
        # tender with same kind & different response_kind
        tender_2 = TenderFactory(
            kind=tender_constants.KIND_TENDER,
            author=self.user_buyer_1,
            response_kind=[tender_constants.RESPONSE_KIND_EMAIL, tender_constants.RESPONSE_KIND_EXTERNAL],
            external_link="https://example.com",
        )
        # tender_2 author
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail", kwargs={"slug": tender_2.slug})
        response = self.client.get(url)
        self.assertContains(response, "Coordonnées")
        self.assertContains(response, tender_2.contact_email)  # RESPONSE_KIND_EMAIL
        self.assertNotContains(response, tender_2.contact_phone)
        self.assertNotContains(response, settings.TEAM_CONTACT_EMAIL)
        self.assertContains(response, "Voir l'appel d'offres")  # KIND_TENDER & RESPONSE_KIND_EXTERNAL
        self.assertNotContains(response, "Lien partagé")
        # tender with different kind & response_kind
        tender_3 = TenderFactory(
            kind=tender_constants.KIND_PROJECT,
            author=self.user_buyer_2,
            response_kind=[tender_constants.RESPONSE_KIND_TEL, tender_constants.RESPONSE_KIND_EXTERNAL],
            external_link="https://example.com",
        )
        TenderSiae.objects.create(tender=tender_3, siae=self.siae_1, detail_contact_click_date=timezone.now())
        # tender_3 author
        self.client.force_login(self.user_buyer_2)
        url = reverse("tenders:detail", kwargs={"slug": tender_3.slug})
        response = self.client.get(url)
        self.assertContains(response, "Coordonnées")
        self.assertNotContains(response, tender_3.contact_email)
        self.assertContains(response, tender_3.contact_phone)  # RESPONSE_KIND_TEL
        self.assertNotContains(response, settings.TEAM_CONTACT_EMAIL)
        self.assertNotContains(response, "Voir l'appel d'offres")
        self.assertContains(response, "Lien partagé")  # !KIND_TENDER & RESPONSE_KIND_EXTERNAL
        # tender_3 siae user interested
        self.client.force_login(self.siae_user_1)
        url = reverse("tenders:detail", kwargs={"slug": tender_3.slug})
        response = self.client.get(url)
        self.assertContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, tender_3.contact_email)
        self.assertContains(response, tender_3.contact_phone)
        self.assertContains(response, settings.TEAM_CONTACT_EMAIL)
        self.assertNotContains(response, "Voir l'appel d'offres")
        self.assertContains(response, "Lien partagé")
        # tender with different response_kind
        tender_4 = TenderFactory(
            kind=tender_constants.KIND_PROJECT,
            author=self.user_buyer_2,
            response_kind=[tender_constants.RESPONSE_KIND_EXTERNAL],
            external_link="https://example.com",
        )
        TenderSiae.objects.create(tender=tender_4, siae=self.siae_1, detail_contact_click_date=timezone.now())
        # tender_4 author
        self.client.force_login(self.user_buyer_2)
        url = reverse("tenders:detail", kwargs={"slug": tender_4.slug})
        response = self.client.get(url)
        self.assertContains(response, "Coordonnées")
        self.assertNotContains(response, tender_4.contact_email)
        self.assertNotContains(response, tender_4.contact_phone)
        self.assertNotContains(response, settings.TEAM_CONTACT_EMAIL)
        self.assertNotContains(response, "Voir l'appel d'offres")
        self.assertContains(response, "Lien partagé")  # !KIND_TENDER & RESPONSE_KIND_EXTERNAL
        # tender_4 siae user interested
        self.client.force_login(self.siae_user_1)
        url = reverse("tenders:detail", kwargs={"slug": tender_4.slug})
        response = self.client.get(url)
        self.assertContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, tender_4.contact_email)
        self.assertNotContains(response, tender_4.contact_phone)
        self.assertNotContains(response, settings.TEAM_CONTACT_EMAIL)
        self.assertNotContains(response, "Voir l'appel d'offres")
        self.assertContains(response, "Lien partagé")
        # tender_4 siae user interested but logged out (with siae_id parameter)
        self.client.logout()
        url = reverse("tenders:detail", kwargs={"slug": tender_4.slug}) + f"?siae_id={self.siae_1.id}"
        response = self.client.get(url)
        self.assertContains(response, "Contactez le client dès maintenant")
        self.assertNotContains(response, tender_4.contact_email)
        self.assertNotContains(response, tender_4.contact_phone)
        self.assertNotContains(response, settings.TEAM_CONTACT_EMAIL)
        self.assertNotContains(response, "Voir l'appel d'offres")
        self.assertContains(response, "Lien partagé")

    def test_update_tendersiae_stats_on_tender_view(self):
        self.tender_1.siaes.add(self.siae_2)
        self.assertEqual(self.tender_1.tendersiae_set.count(), 3 + 1)
        self.assertEqual(self.tender_1.tendersiae_set.first().siae, self.siae_2)
        self.assertIsNone(self.tender_1.tendersiae_set.first().email_link_click_date)
        self.assertIsNone(self.tender_1.tendersiae_set.first().detail_display_date)
        self.assertEqual(self.tender_1.tendersiae_set.last().siae, self.siae_1)
        self.assertIsNotNone(self.tender_1.tendersiae_set.last().email_link_click_date)
        self.assertIsNotNone(self.tender_1.tendersiae_set.last().detail_display_date)
        # first load anonymous user
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Déjà 3 prestataires inclusifs")
        # reload anonymous user with ?siae_id= (already in tendersiae)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug}) + f"?siae_id={self.siae_2.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tender_1.tendersiae_set.count(), 4)  # unchanged
        siae_2_email_link_click_date = self.tender_1.tendersiae_set.first().email_link_click_date
        self.assertIsNotNone(siae_2_email_link_click_date)  # email_link_click_date updated
        self.assertIsNone(self.tender_1.tendersiae_set.first().detail_display_date)
        self.assertIsNotNone(self.tender_1.tendersiae_set.last().detail_display_date)
        self.assertContains(response, "Déjà 4 prestataires inclusifs")
        self.assertNotContains(response, "contactez dès maintenant le client")
        # reload logged in with ?siae_id= (updats detail_display_date, but not email_link_click_date)
        self.client.force_login(self.siae_user_2)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug}) + f"?siae_id={self.siae_2.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tender_1.tendersiae_set.count(), 4)  # unchanged
        self.assertEqual(self.tender_1.tendersiae_set.first().email_link_click_date, siae_2_email_link_click_date)
        siae_2_detail_display_date = self.tender_1.tendersiae_set.first().detail_display_date
        self.assertIsNotNone(siae_2_detail_display_date)  # detail_display_date updated
        self.assertIsNotNone(self.tender_1.tendersiae_set.last().detail_display_date)
        self.assertContains(response, "Déjà 4 prestataires inclusifs")
        self.assertNotContains(response, "contactez dès maintenant le client")
        # reload (doesn't update detail_display_date)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tender_1.tendersiae_set.count(), 4)  # unchanged
        self.assertEqual(self.tender_1.tendersiae_set.first().detail_display_date, siae_2_detail_display_date)
        self.assertContains(response, "Déjà 4 prestataires inclusifs")
        self.assertNotContains(response, "contactez dès maintenant le client")

    def test_create_tendersiae_stats_on_tender_view_by_existing_user(self):
        self.tender_1.siaes.add(self.siae_2)
        self.assertEqual(self.tender_1.tendersiae_set.count(), 3 + 1)
        self.assertEqual(self.tender_1.tendersiae_set.first().siae, self.siae_2)
        self.assertIsNone(self.tender_1.tendersiae_set.first().email_link_click_date)
        self.assertIsNone(self.tender_1.tendersiae_set.first().detail_display_date)
        self.assertEqual(self.tender_1.tendersiae_set.last().siae, self.siae_1)
        self.assertIsNotNone(self.tender_1.tendersiae_set.last().email_link_click_date)
        self.assertIsNotNone(self.tender_1.tendersiae_set.last().detail_display_date)
        # first load anonymous user
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Déjà 3 prestataires inclusifs")
        # first load, new user has already 1 siae contacted, we update only this one
        self.client.force_login(self.siae_user_2)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tender_1.tendersiae_set.count(), 3 + 1)
        self.assertEqual(self.tender_1.tendersiae_set.first().siae, self.siae_2)
        self.assertIsNone(self.tender_1.tendersiae_set.first().email_link_click_date)
        self.assertIsNotNone(self.tender_1.tendersiae_set.first().detail_display_date)
        self.assertContains(response, "Déjà 4 prestataires inclusifs")

    def test_create_tendersiae_stats_on_tender_view_by_new_user(self):
        self.assertEqual(self.tender_1.tendersiae_set.count(), 3)
        self.assertEqual(self.tender_1.tendersiae_set.first().siae, self.siae_5)
        self.assertIsNotNone(self.tender_1.tendersiae_set.first().detail_display_date)  # siae_5
        # first load anonymous user
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Déjà 3 prestataires inclusifs")
        # first load, new user has 2 siaes
        self.client.force_login(self.siae_user_2)
        url = reverse("tenders:detail", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tender_1.tendersiae_set.count(), 3 + 2)  # adds both siae_2 & siae_3
        self.assertEqual(self.tender_1.tendersiae_set.first().siae, self.siae_3)
        self.assertIsNone(self.tender_1.tendersiae_set.first().email_link_click_date)
        self.assertIsNotNone(self.tender_1.tendersiae_set.first().detail_display_date)
        self.assertContains(response, "Déjà 5 prestataires inclusifs")

    def test_badge_is_new_for_siaes(self):
        # assert the new badge is here
        tender_outdated = TenderFactory(
            kind=tender_constants.KIND_QUOTE,
            author=self.user_buyer_1,
            deadline_date=timezone.now() - timedelta(days=1),
        )
        self.client.force_login(self.siae_user_1)
        url = reverse("tenders:detail", kwargs={"slug": tender_outdated.slug})
        response = self.client.get(url)
        self.assertNotContains(
            response, '<span class="float-right badge badge-sm badge-pill badge-new">Nouveau</span>'
        )

        tender_new = TenderFactory(
            kind=tender_constants.KIND_QUOTE,
            author=self.user_buyer_1,
            deadline_date=timezone.now() + timedelta(days=1),
        )
        self.client.force_login(self.siae_user_1)
        url = reverse("tenders:detail", kwargs={"slug": tender_new.slug})
        response = self.client.get(url)
        self.assertContains(
            response, '<span class="float-right badge badge-sm badge-pill badge-new">Nouveau</span>', 1
        )

        response = self.client.get(url)
        self.assertNotContains(
            response, '<span class="float-right badge badge-sm badge-pill badge-new">Nouveau</span>'
        )


class TenderDetailContactClickStatViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae = SiaeFactory(name="ZZ ESI")
        cls.siae_user_1 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae])
        cls.siae_user_2 = UserFactory(kind=User.KIND_SIAE)
        cls.user_buyer_1 = UserFactory(kind=User.KIND_BUYER)
        cls.user_buyer_2 = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.user_admin = UserFactory(kind=User.KIND_ADMIN)
        cls.tender = TenderFactory(kind=tender_constants.KIND_TENDER, author=cls.user_buyer_1, siaes=[cls.siae])
        cls.cta_message = "Cet appel d'offres vous intéresse ?"
        cls.cta_message_success = "contactez dès maintenant le client"
        cls.tender_detail_url = reverse("tenders:detail", kwargs={"slug": cls.tender.slug})
        cls.tender_contact_click_stat_url = reverse(
            "tenders:detail-contact-click-stat", kwargs={"slug": cls.tender.slug}
        )

    def test_anonymous_user_cannot_notify_interested(self):
        response = self.client.get(self.tender_detail_url)
        self.assertContains(response, self.cta_message)
        self.assertContains(response, 'id="login_or_signup_siae_tender_modal"')
        self.assertNotContains(response, 'id="detail_contact_click_confirm_modal"')
        self.assertNotContains(response, self.cta_message_success)
        # anonymous user
        response = self.client.post(self.tender_contact_click_stat_url, data={})
        self.assertEqual(response.status_code, 403)

    def test_only_siae_user_or_with_siae_id_param_can_call_tender_contact_click(self):
        # forbidden
        for user in [self.user_buyer_1, self.user_buyer_2, self.user_partner, self.user_admin]:
            self.client.force_login(user)
            response = self.client.post(
                self.tender_contact_click_stat_url, data={"detail_contact_click_confirm": "false"}
            )
            self.assertEqual(response.status_code, 403)
        # authorized
        for user in [self.siae_user_1, self.siae_user_2]:
            self.client.force_login(user)
            response = self.client.post(
                self.tender_contact_click_stat_url, data={"detail_contact_click_confirm": "false"}
            )
            self.assertEqual(response.status_code, 302)
        # authorized with siae_id parameter
        self.client.logout()
        response = self.client.post(
            f"{self.tender_contact_click_stat_url}?siae_id={self.siae.id}",
            data={"detail_contact_click_confirm": "false"},
        )
        self.assertEqual(response.status_code, 302)
        # forbidden because wrong siae_id parameter
        self.client.logout()
        response = self.client.post(
            f"{self.tender_contact_click_stat_url}?siae_id=test", data={"detail_contact_click_confirm": "false"}
        )
        self.assertEqual(response.status_code, 403)

    def test_update_tendersiae_stats_on_tender_contact_click_with_authenticated_user(self):
        siae_2 = SiaeFactory(name="ABC Insertion")
        self.siae_user_2.siaes.add(siae_2)
        self.tender.siaes.add(siae_2)
        self.assertEqual(self.tender.tendersiae_set.count(), 2)
        self.assertEqual(self.tender.tendersiae_set.first().siae, siae_2)
        self.assertEqual(self.tender.tendersiae_set.last().siae, self.siae)
        self.assertIsNone(self.tender.tendersiae_set.first().detail_contact_click_date)
        self.assertIsNone(self.tender.tendersiae_set.last().detail_contact_click_date)
        # first load
        self.client.force_login(self.siae_user_2)
        response = self.client.get(self.tender_detail_url)
        self.assertContains(response, self.cta_message)
        self.assertNotContains(response, 'id="login_or_signup_siae_tender_modal"')
        self.assertContains(response, 'id="detail_contact_click_confirm_modal"')
        self.assertNotContains(response, self.cta_message_success)
        # click on button
        response = self.client.post(self.tender_contact_click_stat_url, data={"detail_contact_click_confirm": "true"})
        self.assertEqual(response.status_code, 302)
        siae_2_detail_contact_click_date = self.tender.tendersiae_set.first().detail_contact_click_date
        self.assertIsNotNone(siae_2_detail_contact_click_date)
        self.assertIsNone(self.tender.tendersiae_set.last().detail_contact_click_date)
        # reload page
        response = self.client.get(self.tender_detail_url)
        self.assertNotContains(response, self.cta_message)
        self.assertNotContains(response, 'id="login_or_signup_siae_tender_modal"')
        self.assertNotContains(response, 'id="detail_contact_click_confirm_modal"')
        self.assertContains(response, self.cta_message_success)
        # clicking again on the button doesn't update detail_contact_click_date
        # Note: button will disappear on reload anyway
        response = self.client.post(self.tender_contact_click_stat_url, data={"detail_contact_click_confirm": "false"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.tender.tendersiae_set.first().detail_contact_click_date, siae_2_detail_contact_click_date
        )

    def test_update_tendersiae_stats_on_tender_contact_click_with_siae_id(self):
        siae_2 = SiaeFactory(name="ABC Insertion")
        self.siae_user_2.siaes.add(siae_2)
        self.tender.siaes.add(siae_2)
        self.assertEqual(self.tender.tendersiae_set.count(), 2)
        self.assertEqual(self.tender.tendersiae_set.first().siae, siae_2)
        self.assertEqual(self.tender.tendersiae_set.last().siae, self.siae)
        self.assertIsNone(self.tender.tendersiae_set.first().detail_contact_click_date)
        self.assertIsNone(self.tender.tendersiae_set.last().detail_contact_click_date)
        # first load
        response = self.client.get(f"{self.tender_detail_url}?siae_id={siae_2.id}")
        self.assertNotContains(response, self.cta_message_success)
        # click on button
        response = self.client.post(
            f"{self.tender_contact_click_stat_url}?siae_id={siae_2.id}", data={"detail_contact_click_confirm": "true"}
        )
        self.assertEqual(response.status_code, 302)
        siae_2_detail_contact_click_date = self.tender.tendersiae_set.first().detail_contact_click_date
        self.assertIsNotNone(siae_2_detail_contact_click_date)
        self.assertIsNone(self.tender.tendersiae_set.last().detail_contact_click_date)
        # reload page
        response = self.client.get(f"{self.tender_detail_url}?siae_id={siae_2.id}")
        self.assertContains(response, self.cta_message_success)
        # clicking again on the button doesn't update detail_contact_click_date
        # Note: button will disappear on reload anyway
        response = self.client.post(
            f"{self.tender_contact_click_stat_url}?siae_id={siae_2.id}", data={"detail_contact_click_confirm": "false"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.tender.tendersiae_set.first().detail_contact_click_date, siae_2_detail_contact_click_date
        )


class TenderDetailCocontractingClickView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae = SiaeFactory(name="ZZ ESI")
        cls.siae_user = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae])
        cls.user_buyer = UserFactory(kind=User.KIND_BUYER, company_name="Entreprise Buyer")
        cls.tender = TenderFactory(
            kind=tender_constants.KIND_TENDER,
            author=cls.user_buyer,
            amount=tender_constants.AMOUNT_RANGE_100_150,
            accept_share_amount=True,
            response_kind=[tender_constants.RESPONSE_KIND_EMAIL],
        )
        cls.tendersiae = TenderSiae.objects.create(
            tender=cls.tender,
            siae=cls.siae,
            source="EMAIL",
            email_send_date=timezone.now(),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
        )
        TenderQuestionFactory(tender=cls.tender)
        cls.cta_message = "Répondre en co-traitance ?"
        cls.cta_message_success = "votre intérêt a bien été signalé au client."
        cls.tender_detail_url = reverse("tenders:detail", kwargs={"slug": cls.tender.slug})
        cls.tender_cocontracting_url = reverse("tenders:detail-cocontracting-click", kwargs={"slug": cls.tender.slug})

    def test_anonymous_user_cannot_notify_cocontracting(self):
        response = self.client.get(self.tender_detail_url)
        self.assertContains(response, self.cta_message)
        self.assertContains(response, 'id="login_or_signup_siae_tender_modal"')
        # self.assertNotContains(response, 'id="detail_not_interested_click_confirm_modal"')
        self.assertNotContains(response, self.cta_message_success)
        # anonymous user
        response = self.client.post(self.tender_cocontracting_url, data={})
        self.assertEqual(response.status_code, 403)

    def test_user_can_notify_cocontracting_wish_with_siae_id(self):
        # missing data
        with mock.patch("lemarche.www.tenders.tasks.send_mail_async") as mock_send_mail_async:
            response = self.client.post(self.tender_cocontracting_url, data={})
        self.assertEqual(response.status_code, 403)
        mock_send_mail_async.assert_not_called()
        # missing siae
        with mock.patch("lemarche.www.tenders.tasks.send_mail_async") as mock_send_mail_async:
            response = self.client.post(f"{self.tender_cocontracting_url}?siae_id=999999", data={})
        tendersiae = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertContains(
            response, "nous n'avons pas pu prendre en compte votre souhait de répondre en co-traitance"
        )
        mock_send_mail_async.assert_not_called()
        self.assertIsNone(tendersiae.detail_cocontracting_click_date)
        response = self.client.get(self.tender_detail_url)
        self.assertContains(response, self.cta_message)
        self.assertNotContains(response, self.cta_message_success)
        # valid siae
        with mock.patch("lemarche.www.tenders.tasks.send_mail_async") as mock_send_mail_async:
            response = self.client.post(f"{self.tender_cocontracting_url}?siae_id={self.siae.id}", data={})
        tendersiae = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertContains(response, self.cta_message_success)
        mock_send_mail_async.assert_called_once()
        email_body = mock_send_mail_async.call_args[1]["email_body"]
        self.assertTrue(f"La structure {self.siae.name} souhaite répondre en co-traitance" in email_body)
        self.assertIsNotNone(tendersiae.detail_cocontracting_click_date)
        response = self.client.get(f"{self.tender_detail_url}?siae_id={self.siae.id}")
        self.assertNotContains(response, self.cta_message)
        self.assertContains(response, self.cta_message_success)

    def test_user_can_notify_cocontracting_wish_with_authenticated_user(self):
        self.client.force_login(self.siae_user)

        response = self.client.get(self.tender_detail_url)
        self.assertContains(response, self.cta_message)
        self.assertNotContains(response, self.cta_message_success)

        tendersiae = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertIsNone(tendersiae.detail_cocontracting_click_date)
        with mock.patch("lemarche.www.tenders.tasks.send_mail_async") as mock_send_mail_async:
            response = self.client.post(self.tender_cocontracting_url, data={})
        tendersiae = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertContains(response, self.cta_message_success)
        mock_send_mail_async.assert_called_once()
        email_body = mock_send_mail_async.call_args[1]["email_body"]
        self.assertTrue(f"La structure {self.siae.name } souhaite répondre en co-traitance" in email_body)
        self.assertIsNotNone(tendersiae.detail_cocontracting_click_date)
        response = self.client.get(self.tender_detail_url)
        self.assertNotContains(response, self.cta_message)
        self.assertContains(response, self.cta_message_success)
        user_without_siae = UserFactory(kind=User.KIND_SIAE)
        self.client.force_login(user_without_siae)
        with mock.patch("lemarche.www.tenders.tasks.send_mail_async") as mock_send_mail_async:
            response = self.client.post(self.tender_cocontracting_url, data={})
        self.assertContains(
            response, "nous n'avons pas pu prendre en compte votre souhait de répondre en co-traitance"
        )
        mock_send_mail_async.assert_not_called()


class TenderDetailNotInterestedClickView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae = SiaeFactory(name="ZZ ESI")
        cls.siae_user = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae])
        cls.user_buyer = UserFactory(kind=User.KIND_BUYER, company_name="Entreprise Buyer")
        cls.tender = TenderFactory(
            kind=tender_constants.KIND_TENDER,
            author=cls.user_buyer,
            amount=tender_constants.AMOUNT_RANGE_100_150,
            accept_share_amount=True,
            response_kind=[tender_constants.RESPONSE_KIND_EMAIL],
        )
        cls.tendersiae = TenderSiae.objects.create(
            tender=cls.tender,
            siae=cls.siae,
            source="EMAIL",
            email_send_date=timezone.now(),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
        )
        cls.cta_message = "Cette demande ne vous intéresse pas ?"
        cls.cta_message_success = "Vous n'êtes pas intéressé par ce besoin."
        cls.tender_detail_url = reverse("tenders:detail", kwargs={"slug": cls.tender.slug})
        cls.tender_not_interested_url = reverse(
            "tenders:detail-not-interested-click", kwargs={"slug": cls.tender.slug}
        )

    def test_anonymous_user_cannot_notify_not_interested(self):
        response = self.client.get(self.tender_detail_url)
        self.assertContains(response, self.cta_message)
        self.assertContains(response, 'id="login_or_signup_siae_tender_modal"')
        self.assertNotContains(response, 'id="detail_not_interested_click_confirm_modal"')
        self.assertNotContains(response, self.cta_message_success)
        # anonymous user
        response = self.client.post(self.tender_not_interested_url, data={})
        self.assertEqual(response.status_code, 403)

    def test_user_can_notify_not_interested_wish_with_authenticated_user(self):
        self.client.force_login(self.siae_user)
        # workflow
        response = self.client.get(self.tender_detail_url)
        self.assertContains(response, self.cta_message)
        self.assertNotContains(response, 'id="login_or_signup_siae_tender_modal"')
        self.assertContains(response, 'id="detail_not_interested_click_confirm_modal"')
        self.assertNotContains(response, self.cta_message_success)
        response = self.client.post(
            self.tender_not_interested_url, data={"detail_not_interested_feedback": "reason"}, follow=True
        )
        tendersiae = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertNotContains(response, self.cta_message)
        self.assertNotContains(response, 'id="detail_not_interested_click_confirm_modal"')
        self.assertContains(response, self.cta_message_success)
        self.assertIsNotNone(tendersiae.detail_not_interested_click_date)
        self.assertEqual(tendersiae.detail_not_interested_feedback, "reason")
        response = self.client.get(self.tender_detail_url)
        self.assertNotContains(response, self.cta_message)
        self.assertNotContains(response, 'id="detail_not_interested_click_confirm_modal"')
        self.assertContains(response, self.cta_message_success)

    def test_user_can_notify_not_interested_wish_with_siae_id_in_url(self):
        # wrong siae_id
        response = self.client.post(f"{self.tender_not_interested_url}?siae_id=999999", data={}, follow=True)
        self.assertContains(response, self.cta_message)
        self.assertNotContains(response, 'id="login_or_signup_siae_tender_modal"')
        self.assertContains(response, 'id="detail_not_interested_click_confirm_modal"')
        self.assertNotContains(response, self.cta_message_success)
        # workflow
        tendersiae = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertIsNone(tendersiae.detail_not_interested_click_date)
        response = self.client.post(f"{self.tender_not_interested_url}?siae_id={self.siae.id}", data={}, follow=True)
        self.assertNotContains(response, self.cta_message)
        self.assertNotContains(response, 'id="detail_not_interested_click_confirm_modal"')
        self.assertContains(response, self.cta_message_success)
        tendersiae = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertIsNotNone(tendersiae.detail_not_interested_click_date)
        response = self.client.get(f"{self.tender_detail_url}?siae_id={self.siae.id}")
        self.assertNotContains(response, self.cta_message)
        self.assertNotContains(response, 'id="detail_not_interested_click_confirm_modal"')
        self.assertContains(response, self.cta_message_success)

    def test_user_can_notify_not_interested_wish_with_siae_id_and_answer_in_url(self):
        # wrong siae_id
        response = self.client.post(
            f"{self.tender_not_interested_url}?siae_id=999999&not_interested=True", data={}, follow=True
        )
        self.assertContains(response, self.cta_message)
        self.assertNotContains(response, 'id="login_or_signup_siae_tender_modal"')
        self.assertContains(response, 'modal-siae" id="detail_not_interested_click_confirm_modal"')
        self.assertNotContains(response, 'modal-siae show" id="detail_not_interested_click_confirm_modal"')
        self.assertNotContains(response, self.cta_message_success)
        # workflow
        tendersiae = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertIsNone(tendersiae.detail_not_interested_click_date)
        response = self.client.post(
            f"{self.tender_not_interested_url}?siae_id={self.siae.id}&not_interested=True", data={}, follow=True
        )
        self.assertNotContains(response, self.cta_message)
        self.assertNotContains(response, 'modal-siae" id="detail_not_interested_click_confirm_modal"')
        # self.assertContains(response, 'modal-siae show" id="detail_not_interested_click_confirm_modal"')
        # self.assertNotContains(response, self.cta_message_success)
        tendersiae = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertIsNotNone(tendersiae.detail_not_interested_click_date)
        response = self.client.get(f"{self.tender_detail_url}?siae_id={self.siae.id}")
        self.assertNotContains(response, self.cta_message)
        self.assertNotContains(response, 'id="detail_not_interested_click_confirm_modal"')
        self.assertContains(response, self.cta_message_success)


# TODO: this test doesn't work anymore. find a way to test logging post-email in non-prod environments?
# class TenderTasksTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.tender = TenderFactory()

#     def test_send_email_for_feedbacks_set_log(self):
#         self.assertEqual(len(self.tender.logs), 0)
#         send_tenders_author_feedback_or_survey(self.tender, kind="feedback_30d")
#         # fetch tender to be sure to have the last version of tender
#         tender: Tender = Tender.objects.get(pk=self.tender.pk)
#         self.assertEqual(len(tender.logs), 1)
#         self.assertEqual(tender.logs[0]["action"], "email_feedback_30d_sent")


class TenderSiaeListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae_1 = SiaeFactory(
            name="ZZ ESI",
            kind=siae_constants.KIND_EI,
            is_qpv=True,
            city="Grenoble",
            post_code="38100",
            employees_insertion_count=103,
        )
        cls.siae_2 = SiaeFactory(
            name="ABC Insertion", kind=siae_constants.KIND_EI, city="Grenoble", post_code="38000", ca=276000
        )
        cls.siae_3 = SiaeFactory(
            name="Une autre structure", kind=siae_constants.KIND_ETTI, employees_insertion_count=53
        )
        cls.siae_4 = SiaeFactory(
            name="Une structure ouverte à la co-traitance",
            kind=siae_constants.KIND_EA,
            city="Grenoble",
            post_code="38000",
            is_cocontracting=True,
        )
        cls.siae_5 = SiaeFactory(name="Une dernière structure", kind=siae_constants.KIND_ETTI)
        cls.siae_user_1 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_1, cls.siae_2])
        cls.siae_user_2 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae_3])
        cls.user_buyer_1 = UserFactory(kind=User.KIND_BUYER)
        cls.user_buyer_2 = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.tender_1 = TenderFactory(author=cls.user_buyer_1)
        cls.tender_2 = TenderFactory(author=cls.user_buyer_2)
        cls.tendersiae_1_1 = TenderSiae.objects.create(
            tender=cls.tender_1,
            siae=cls.siae_1,
            email_send_date=timezone.now(),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
            detail_contact_click_date=timezone.now(),
        )
        cls.tendersiae_1_2 = TenderSiae.objects.create(
            tender=cls.tender_1, siae=cls.siae_2, email_send_date=timezone.now()
        )
        cls.tendersiae_1_3 = TenderSiae.objects.create(
            tender=cls.tender_1,
            siae=cls.siae_3,
            email_send_date=timezone.now() - timedelta(hours=1),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
            detail_contact_click_date=timezone.now() - timedelta(hours=1),
        )
        cls.tendersiae_1_4 = TenderSiae.objects.create(
            tender=cls.tender_1,
            siae=cls.siae_4,
            detail_display_date=timezone.now(),
            detail_cocontracting_click_date=timezone.now() - timedelta(hours=3),
        )
        cls.tendersiae_1_5 = TenderSiae.objects.create(
            tender=cls.tender_1,
            siae=cls.siae_5,
            detail_display_date=timezone.now(),
            detail_contact_click_date=timezone.now() - timedelta(hours=2),
        )
        cls.tendersiae_2_1 = TenderSiae.objects.create(
            tender=cls.tender_2,
            siae=cls.siae_2,
            email_send_date=timezone.now(),
            email_link_click_date=timezone.now(),
            detail_display_date=timezone.now(),
            detail_contact_click_date=timezone.now(),
        )
        cls.perimeter_city = PerimeterFactory(
            name="Grenoble",
            kind=Perimeter.KIND_CITY,
            insee_code="38185",
            department_code="38",
            region_code="84",
            post_codes=["38000", "38100", "38700"],
            # coords=Point(5.7301, 45.1825),
        )

    def test_anonymous_user_cannot_view_tender_siae_interested_list(self):
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_only_tender_author_can_view_tender_siae_interested_list(self):
        # forbidden
        for user in [self.user_buyer_2, self.user_partner, self.siae_user_1, self.siae_user_2]:
            self.client.force_login(user)
            url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/besoins/")
        # authorized
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tender_author_viewing_tender_siae_interested_list_should_update_stats(self):
        self.assertIsNone(self.tender_1.siae_list_last_seen_date)
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(Tender.objects.get(id=self.tender_1.id).siae_list_last_seen_date)

    def test_tender_siae_tabs(self):
        self.client.force_login(self.user_buyer_1)
        # ALL
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 3)  # email_send_date
        # VIEWED
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug, "status": "VIEWED"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 4)  # email_link_click_date or detail_display_date
        # INTERESTED
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug, "status": "INTERESTED"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 3)  # detail_contact_click_date
        # COCONTRACTED
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug, "status": "COCONTRACTED"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 1)  # detail_cocontracting_click_date

    def test_order_tender_siae_by_last_detail_contact_click_date(self):
        # TenderSiae are ordered by -created_at by default
        self.assertEqual(self.tender_1.tendersiae_set.first().id, self.tendersiae_1_5.id)
        # but TenderSiaeListView are ordered by -detail_contact_click_date
        self.client.force_login(self.user_buyer_1)
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug, "status": "INTERESTED"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 3)  # detail_contact_click_date
        self.assertEqual(response.context["siaes"][0].id, self.tendersiae_1_1.siae.id)

    def test_filter_tender_siae_list(self):
        self.client.force_login(self.user_buyer_1)
        # filter by location
        url = (
            reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug})
            + f"?locations={self.perimeter_city.slug}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 2)  # email_send_date & located in Grenoble
        url = (
            reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug, "status": "INTERESTED"})
            + f"?locations={self.perimeter_city.slug}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 1)  # detail_contact_click_date & located in Grenoble
        # filter by kind
        url = (
            reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug})
            + f"?kind={siae_constants.KIND_ETTI}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 1)  # email_send_date & ETTI
        url = (
            reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug, "status": "INTERESTED"})
            + f"?kind={siae_constants.KIND_ETTI}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 2)  # detail_contact_click_date & ETTI
        # filter by territory
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug}) + "?territory=QPV"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 1)  # email_send_date & QPV
        # filter by count of employees
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug}) + "?employees=50-99"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 1)
        self.assertEqual(response.context["siaes"][0].id, self.siae_3.id)
        # filter by ca
        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug}) + "?ca=100000-500000"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 1)
        self.assertEqual(response.context["siaes"][0].id, self.siae_2.id)

        url = reverse("tenders:detail-siae-list", kwargs={"slug": self.tender_1.slug, "status": "COCONTRACTED"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["siaes"]), 1)  # detail_cocontracting_click_date
        self.assertEqual(response.context["siaes"][0].id, self.siae_4.id)


class TenderDetailSurveyTransactionedViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae = SiaeFactory(name="ZZ ESI")
        cls.siae_user_1 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae])
        cls.siae_user_2 = UserFactory(kind=User.KIND_SIAE)
        cls.user_buyer_1 = UserFactory(kind=User.KIND_BUYER)
        cls.user_buyer_2 = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.user_admin = UserFactory(kind=User.KIND_ADMIN)
        cls.tender = TenderFactory(kind=tender_constants.KIND_TENDER, author=cls.user_buyer_1, siaes=[cls.siae])
        cls.user_buyer_1_sesame_query_string = sesame_get_query_string(cls.user_buyer_1)
        cls.url = reverse("tenders:detail-survey-transactioned", kwargs={"slug": cls.tender.slug})

    def test_anonymous_user_cannot_call_tender_survey_transactioned(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_only_tender_author_with_sesame_token_can_call_tender_survey_transactioned(self):
        # forbidden
        for user in [
            self.siae_user_1,
            self.siae_user_2,
            self.user_buyer_1,
            self.user_buyer_2,
            self.user_partner,
            self.user_admin,
        ]:
            self.client.force_login(user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)
        # logout the last user to be sure
        self.client.logout()
        # authorized
        user_sesame_query_string = sesame_get_query_string(self.user_buyer_1)
        url = self.url + user_sesame_query_string
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        # full form displayed (but should never happen)

    def test_update_tender_stats_on_tender_survey_transactioned_answer_true(self):
        t = Tender.objects.get(id=self.tender.id)
        self.assertIsNone(t.survey_transactioned_answer)
        self.assertIsNone(t.siae_transactioned)
        self.assertIsNone(t.siae_transactioned_source)
        self.assertIsNone(t.siae_transactioned_last_updated)
        # load with answer 'True': partial form
        url = self.url + self.user_buyer_1_sesame_query_string + "&answer=True"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        t = Tender.objects.get(id=self.tender.id)
        self.assertTrue(t.survey_transactioned_answer)
        self.assertTrue(t.siae_transactioned)
        self.assertEqual(
            t.siae_transactioned_source,
            tender_constants.TENDER_SIAE_TRANSACTIONED_SOURCE_AUTHOR,
        )
        self.assertIsNotNone(t.siae_transactioned_last_updated)
        # fill in form
        response = self.client.post(
            url, data={"survey_transactioned_amount": 1000, "survey_transactioned_feedback": "Feedback"}, follow=True
        )
        self.assertEqual(response.status_code, 200)  # redirect
        t = Tender.objects.get(id=self.tender.id)
        self.assertRedirects(response, reverse("tenders:detail", kwargs={"slug": self.tender.slug}))
        self.assertContains(response, "Merci pour votre réponse")
        self.assertTrue(t.survey_transactioned_answer)
        self.assertEqual(t.survey_transactioned_amount, 1000)
        # reload with answer, ignore changes and redirect
        url = self.url + self.user_buyer_1_sesame_query_string + "&answer=False"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)  # redirect
        t = Tender.objects.get(id=self.tender.id)
        self.assertRedirects(response, reverse("tenders:detail", kwargs={"slug": self.tender.slug}))
        self.assertContains(response, "Votre réponse a déjà été prise en compte")
        self.assertTrue(t.survey_transactioned_answer)
        self.assertTrue(t.siae_transactioned)

    def test_update_tender_stats_on_tender_survey_transactioned_answer_false(self):
        # load with answer 'False': partial form
        url = self.url + self.user_buyer_1_sesame_query_string + "&answer=False"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        t = Tender.objects.get(id=self.tender.id)
        self.assertFalse(t.survey_transactioned_answer)
        self.assertFalse(t.siae_transactioned)
        # fill in form
        response = self.client.post(url, data={"survey_transactioned_feedback": "Feedback"}, follow=True)
        self.assertEqual(response.status_code, 200)  # redirect
        t = Tender.objects.get(id=self.tender.id)
        self.assertRedirects(response, reverse("tenders:detail", kwargs={"slug": self.tender.slug}))
        self.assertContains(response, "Merci pour votre réponse")
        self.assertFalse(t.survey_transactioned_answer)
        self.assertIsNone(t.survey_transactioned_amount)
        # reload with answer, ignore changes
        url = self.url + self.user_buyer_1_sesame_query_string + "&answer=True"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)  # redirect
        t = Tender.objects.get(id=self.tender.id)
        self.assertRedirects(response, reverse("tenders:detail", kwargs={"slug": self.tender.slug}))
        self.assertContains(response, "Votre réponse a déjà été prise en compte")
        self.assertFalse(t.survey_transactioned_answer)
        self.assertFalse(t.siae_transactioned)


class TenderDetailSiaeSurveyTransactionedViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siae = SiaeFactory(name="ZZ ESI")
        cls.siae_user_1 = UserFactory(kind=User.KIND_SIAE, siaes=[cls.siae])
        cls.siae_user_2 = UserFactory(kind=User.KIND_SIAE)
        cls.user_buyer_1 = UserFactory(kind=User.KIND_BUYER)
        cls.user_buyer_2 = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.user_admin = UserFactory(kind=User.KIND_ADMIN)
        cls.tender = TenderFactory(kind=tender_constants.KIND_TENDER, author=cls.user_buyer_1)
        cls.tendersiae = TenderSiae.objects.create(tender=cls.tender, siae=cls.siae)
        cls.url = reverse(
            "tenders:detail-siae-survey-transactioned", kwargs={"slug": cls.tender.slug, "siae_slug": cls.siae.slug}
        )
        cls.user_siae_1_sesame_query_string = sesame_get_query_string(cls.siae_user_1)

    def test_anonymous_user_cannot_call_tender_siae_survey_transactioned(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_only_tender_author_with_sesame_token_can_call_tender_siae_survey_transactioned(self):
        # forbidden
        for user in [
            self.siae_user_1,
            self.siae_user_2,
            self.user_buyer_1,
            self.user_buyer_2,
            self.user_partner,
            self.user_admin,
        ]:
            self.client.force_login(user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)
        # logout the last user to be sure
        self.client.logout()
        # authorized
        user_sesame_query_string = sesame_get_query_string(self.siae_user_1)
        url = self.url + user_sesame_query_string
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        # full form displayed (but should never happen)

    def test_update_tender_stats_on_tender_siae_survey_transactioned_answer_true(self):
        ts = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertIsNone(ts.survey_transactioned_answer)
        self.assertIsNone(ts.transactioned)
        self.assertIsNone(ts.transactioned_source)
        self.assertIsNone(ts.tender.siae_transactioned)
        self.assertIsNone(ts.tender.siae_transactioned_source)
        self.assertIsNone(ts.tender.siae_transactioned_last_updated)
        # load with answer 'True': partial form
        url = self.url + self.user_siae_1_sesame_query_string + "&answer=True"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        ts = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertTrue(ts.survey_transactioned_answer)
        self.assertTrue(ts.transactioned)
        self.assertEqual(
            ts.transactioned_source,
            tender_constants.TENDER_SIAE_TRANSACTIONED_SOURCE_SIAE,
        )
        self.assertTrue(ts.tender.siae_transactioned)
        self.assertEqual(ts.tender.siae_transactioned_source, tender_constants.TENDER_SIAE_TRANSACTIONED_SOURCE_SIAE)
        self.assertIsNotNone(ts.tender.siae_transactioned_last_updated)
        # fill in form
        response = self.client.post(
            url, data={"survey_transactioned_amount": 1000, "survey_transactioned_feedback": "Feedback"}, follow=True
        )
        self.assertEqual(response.status_code, 200)  # redirect
        ts = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertRedirects(response, reverse("tenders:detail", kwargs={"slug": self.tender.slug}))
        self.assertContains(response, "Merci pour votre réponse")
        self.assertTrue(ts.survey_transactioned_answer)
        self.assertEqual(ts.survey_transactioned_amount, 1000)
        # reload with answer, ignore changes and redirect
        url = self.url + self.user_siae_1_sesame_query_string + "&answer=False"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)  # redirect
        ts = TenderSiae.objects.get(tender=self.tender, siae=self.siae)
        self.assertRedirects(response, reverse("tenders:detail", kwargs={"slug": self.tender.slug}))
        self.assertContains(response, "Votre réponse a déjà été prise en compte")
        self.assertTrue(ts.survey_transactioned_answer)

    def test_update_tender_stats_on_tender_siae_survey_transactioned_answer_false(self):
        # load with answer 'False': partial form
        url = self.url + self.user_siae_1_sesame_query_string + "&answer=False"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TenderSiae.objects.get(tender=self.tender, siae=self.siae).survey_transactioned_answer)
        # fill in form
        response = self.client.post(url, data={"survey_transactioned_feedback": "Feedback"}, follow=True)
        self.assertEqual(response.status_code, 200)  # redirect
        self.assertRedirects(response, reverse("tenders:detail", kwargs={"slug": self.tender.slug}))
        self.assertContains(response, "Merci pour votre réponse")
        self.assertFalse(TenderSiae.objects.get(tender=self.tender, siae=self.siae).survey_transactioned_answer)
        self.assertIsNone(TenderSiae.objects.get(tender=self.tender, siae=self.siae).survey_transactioned_amount)
        # reload with answer, ignore changes
        url = self.url + self.user_siae_1_sesame_query_string + "&answer=True"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)  # redirect
        self.assertRedirects(response, reverse("tenders:detail", kwargs={"slug": self.tender.slug}))
        self.assertContains(response, "Votre réponse a déjà été prise en compte")
        self.assertFalse(TenderSiae.objects.get(tender=self.tender, siae=self.siae).survey_transactioned_answer)
