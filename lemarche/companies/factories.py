import factory
from factory.django import DjangoModelFactory

from lemarche.companies.models import Company


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Faker("company", locale="fr_FR")
    # slug: auto-generated
    website = "https://example.com"

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if extracted:
            self.users.add(*extracted)
