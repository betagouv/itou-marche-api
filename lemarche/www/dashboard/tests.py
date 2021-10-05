from django.test import TestCase
from django.urls import reverse

from lemarche.siaes.factories import SiaeFactory
from lemarche.users.factories import DEFAULT_PASSWORD, UserFactory
from lemarche.users.models import User


class DashboardHomeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_anonymous_user_cannot_access_profile(self):
        url = reverse("dashboard:home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/dashboard/")

    def user_can_access_profile(self):
        self.client.login(email=self.user.email, password=DEFAULT_PASSWORD)
        url = reverse("dashboard:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class SiaeAdoptViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_siae = UserFactory(kind=User.KIND_SIAE)
        cls.user_buyer = UserFactory(kind=User.KIND_BUYER)
        cls.user_partner = UserFactory(kind=User.KIND_PARTNER)
        cls.user_admin = UserFactory(kind=User.KIND_ADMIN)
        cls.siae_with_user = SiaeFactory()
        cls.siae_with_user.users.add(cls.user_siae)
        cls.siae_without_user = SiaeFactory()

    def test_anonymous_user_cannot_adopt_siae(self):
        url = reverse("dashboard:siae_search_by_siret")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_only_siae_user_or_admin_can_adopt_siae(self):
        ALLOWED_USERS = [self.user_siae, self.user_admin]
        for user in ALLOWED_USERS:
            self.client.login(email=user.email, password=DEFAULT_PASSWORD)
            url = reverse("dashboard:siae_search_by_siret")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        NOT_ALLOWED_USERS = [self.user_buyer, self.user_partner]
        for user in NOT_ALLOWED_USERS:
            self.client.login(email=user.email, password=DEFAULT_PASSWORD)
            url = reverse("dashboard:siae_search_by_siret")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/dashboard/")

    def test_only_siaes_without_users_can_be_adopted(self):
        self.client.login(email=self.user_siae.email, password=DEFAULT_PASSWORD)

        url = reverse("dashboard:siae_adopt_confirm", args=[self.siae_without_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("dashboard:siae_adopt_confirm", args=[self.siae_with_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/dashboard/")

    def test_siae_without_user_adopt_confirm(self):
        self.client.login(email=self.user_siae.email, password=DEFAULT_PASSWORD)
        self.assertEqual(self.siae_without_user.users.count(), 0)
        self.assertEqual(self.user_siae.siaes.count(), 1)  # setUpTestData

        url = reverse("dashboard:siae_adopt_confirm", args=[self.siae_without_user.id])
        response = self.client.post(url)  # data={}
        self.assertEqual(response.status_code, 302)  # redirect to success_url
        self.assertEqual(response.url, "/dashboard/")
        self.assertEqual(self.siae_without_user.users.count(), 1)
        self.assertEqual(self.user_siae.siaes.count(), 1 + 1)
