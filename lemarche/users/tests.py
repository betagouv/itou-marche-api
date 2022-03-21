from django.test import TestCase

from lemarche.favorites.factories import FavoriteListFactory
from lemarche.siaes.factories import SiaeFactory
from lemarche.users.factories import UserFactory
from lemarche.users.models import User


class UserModelTest(TestCase):
    def setUp(self):
        pass

    def test_str(self):
        user = UserFactory(email="coucou@example.com")
        self.assertEqual(str(user), "coucou@example.com")

    def test_full_name(self):
        user = UserFactory(first_name="Paul", last_name="Anploi")
        self.assertEqual(user.full_name, "Paul Anploi")

    def test_has_siae_queryset(self):
        UserFactory()
        user = UserFactory()
        siae = SiaeFactory()
        siae.users.add(user)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.has_siae().count(), 1)

    def test_has_favorite_list_queryset(self):
        UserFactory()
        user = UserFactory()
        FavoriteListFactory(user=user)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.has_favorite_list().count(), 1)

    def test_with_api_key_queryset(self):
        UserFactory()
        UserFactory(api_key="coucou")
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.with_api_key().count(), 1)


class UserModelSaveTest(TestCase):
    def setUp(self):
        pass

    def test_update_last_updated_fields(self):
        user = UserFactory()
        self.assertEqual(user.api_key, None)
        self.assertEqual(user.api_key_last_updated, None)
        # new value: last_updated field will be set
        user = User.objects.get(id=user.id)  # we need to fetch it again to pass through the __init__
        user.api_key = "AZERTY"
        user.save()
        self.assertEqual(user.api_key, "AZERTY")
        self.assertNotEqual(user.api_key_last_updated, None)
        api_key_last_updated = user.api_key_last_updated
        # same value: last_updated field will not be updated
        user = User.objects.get(id=user.id)
        user.api_key = "AZERTY"
        user.save()
        self.assertEqual(user.api_key, "AZERTY")
        self.assertEqual(user.api_key_last_updated, api_key_last_updated)
        # updated value: last_updated field will be updated
        user = User.objects.get(id=user.id)
        user.api_key = "QWERTY"
        user.save()
        self.assertEqual(user.api_key, "QWERTY")
        self.assertNotEqual(user.api_key_last_updated, api_key_last_updated)
