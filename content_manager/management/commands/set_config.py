import json
from os.path import isfile

from django.conf import settings
from django.core.management.base import BaseCommand
from wagtail.models import Site

from content_manager.models import CmsDsfrConfig


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        Sets the site hostname and site_name,
        and imports contents from the config.json file if present.
        """
        if "http://" in settings.HOST_URL or "https://" in settings.HOST_URL:
            raise ValueError(
                """The HOST_URL environment variable must contain the domain name only,
                without the port or http/https protocol."""
            )

        site = Site.objects.filter(is_default_site=True).first()
        site.hostname = settings.HOST_URL
        site.site_name = settings.WAGTAIL_SITE_NAME
        site.save()

        if isfile("config.json"):
            with open("config.json") as config_file:
                config_data = json.load(config_file)

                config_data["site_id"] = site.id

                _config, created = CmsDsfrConfig.objects.get_or_create(id=1, defaults=config_data)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Config imported for {config_data.get('site_title', '')}"))
                else:
                    self.stdout.write(self.style.SUCCESS("Config already existing, data not imported."))
