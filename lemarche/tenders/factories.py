import random
from datetime import date, timedelta

import factory.fuzzy
from django.utils import timezone
from factory.django import DjangoModelFactory

from lemarche.tenders import constants as tender_constants
from lemarche.tenders.models import PartnerShareTender, Tender, TenderQuestion
from lemarche.users.factories import UserFactory


class TenderFactory(DjangoModelFactory):
    class Meta:
        model = Tender

    title = factory.Faker("name", locale="fr_FR")
    # slug auto-generated
    kind = tender_constants.KIND_QUOTE
    presta_type = []
    response_kind = factory.List(
        [
            factory.fuzzy.FuzzyChoice([key for (key, _) in tender_constants.RESPONSE_KIND_CHOICES]),
        ]
    )
    # presta_type = factory.List(
    #     [
    #         factory.fuzzy.FuzzyChoice([key for (key, _) in siae_constants.PRESTA_CHOICES]),
    #     ]
    # )
    description = factory.Faker("paragraph", nb_sentences=5, locale="fr_FR")
    constraints = factory.Faker("paragraph", nb_sentences=5, locale="fr_FR")
    deadline_date = date.today() + timedelta(days=10)
    start_working_date = date.today() + timedelta(days=random.randint(12, 90))
    author = factory.SubFactory(UserFactory)
    external_link = factory.Sequence("https://{0}example.com".format)
    # Contact fields
    contact_first_name = factory.Sequence("first_name{0}".format)
    contact_last_name = factory.Sequence("last_name{0}".format)
    contact_email = factory.Sequence("email_contact_tender{0}@example.com".format)
    contact_phone = "0123456789"  # factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    # amount = tender_constants.AMOUNT_RANGE_100_150
    # marche_benefits = factory.fuzzy.FuzzyChoice([key for (key, _) in constants.MARCHE_BENEFIT_CHOICES])
    status = tender_constants.STATUS_SENT
    validated_at = timezone.now()
    first_sent_at = timezone.now()

    @factory.post_generation
    def perimeters(self, create, extracted, **kwargs):
        if extracted:
            # Add the iterable of groups using bulk addition
            self.perimeters.add(*extracted)

    @factory.post_generation
    def sectors(self, create, extracted, **kwargs):
        if extracted:
            # Add the iterable of groups using bulk addition
            self.sectors.add(*extracted)

    @factory.post_generation
    def siaes(self, create, extracted, **kwargs):
        if extracted:
            # Add the iterable of groups using bulk addition
            self.siaes.add(*extracted)

    @factory.post_generation
    def admins(self, create, extracted, **kwargs):
        if extracted:
            # Add the iterable of groups using bulk addition
            self.admins.add(*extracted)


class TenderQuestionFactory(DjangoModelFactory):
    class Meta:
        model = TenderQuestion

    text = factory.Faker("paragraph", nb_sentences=1, locale="fr_FR")


class PartnerShareTenderFactory(DjangoModelFactory):
    class Meta:
        model = PartnerShareTender

    name = factory.Faker("name", locale="fr_FR")

    contact_email_list = factory.LazyFunction(
        lambda: [factory.Faker("email", locale="fr_FR") for i in range(random.randint(1, 4))]
    )

    @factory.post_generation
    def perimeters(self, create, extracted, **kwargs):
        if extracted:
            # Add the iterable of groups using bulk addition
            self.perimeters.add(*extracted)
