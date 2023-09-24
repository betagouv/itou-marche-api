from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models import Value

from lemarche.siaes.models import Siae
from lemarche.utils.commands import BaseCommand


class Command(BaseCommand):
    """
    Usage:
    - poetry run python manage.py set_search_vector_field
    """

    def handle(self, *args, **options):
        self.stdout_info("-" * 80)
        self.stdout_info("Reseting search_vector field...")
        progress = 0
        for siae in Siae.objects.prefetch_related("offers", "labels").all():
            siae_search_vector = (
                SearchVector(
                    Value(siae.name, output_field=models.CharField()),
                    # weight="A",
                    # config="french",
                )
                + SearchVector(
                    Value(siae.brand, output_field=models.CharField()),
                    # weight="A",
                    # config="french",
                )
                + SearchVector(
                    Value(siae.kind, output_field=models.CharField()),
                    # weight="A",
                    # config="french",
                )
                + SearchVector(
                    Value(siae.description, output_field=models.CharField()),
                    # weight="A",
                    config="french",
                )
            )
            if siae.offers:
                siae_search_vector += SearchVector(
                    Value(
                        " ".join(str(offer.name) for offer in siae.offers.all()),
                    ),
                    # weight="A",
                    config="french",
                )
            if siae.labels:
                siae_search_vector += SearchVector(
                    Value(
                        " ".join(str(label.name) for label in siae.labels.all()),
                    ),
                    # weight="A",
                    config="french",
                )
            siae.search_vector = siae_search_vector
            siae.save(update_fields=["search_vector"])
            progress += 1
            if (progress % 500) == 0:
                print(f"{progress}...")
