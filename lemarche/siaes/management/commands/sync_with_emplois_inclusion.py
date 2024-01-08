import os
import re
from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import CommandError
from django.utils import timezone
from stdnum.fr import siret

from lemarche.siaes import constants as siae_constants
from lemarche.siaes.models import Siae
from lemarche.utils.apis import api_emplois_inclusion, api_mailjet, api_slack
from lemarche.utils.commands import BaseCommand
from lemarche.utils.constants import DEPARTMENT_TO_REGION
from lemarche.utils.data import rename_dict_key


UPDATE_FIELDS = [
    # "name",  # what happens to the slug if the name is updated?
    "brand",
    # "kind"
    "siret",
    "siret_is_valid",
    "naf",
    "phone",
    "email",
    "website",
    "address",
    "post_code",
    "city",
    "department",
    "region",
    "coords",
    "source",
    "admin_name",
    "admin_email",
    "asp_id",
    "is_active",
    "is_delisted",
    "c1_last_sync_date",
]

C1_EXTRA_KEYS = ["convention_is_active", "convention_asp_id"]


def map_siae_presta_type(siae_kind):
    if siae_kind:
        if siae_kind in ["ETTI", "AI"]:
            return [siae_constants.PRESTA_DISP]
        return [siae_constants.PRESTA_PREST, siae_constants.PRESTA_BUILD]
    return []


def map_siae_nature(siae_source):
    if siae_source:
        if siae_source in ["ASP", "GEIQ", "EA_EATT"]:
            return siae_constants.NATURE_HEAD_OFFICE
        if siae_source == "USER_CREATED":
            return siae_constants.NATURE_ANTENNA
    return ""


def set_is_active(siae):
    """
    les-emplois field
    Most Siae have a convention (AI, ACI, EI, ETTI, EITI)
    We consider the Siae as active if "having a convention" + "this convention is active".

    Some Siae do not have a convention: e.g. GEIQ, EA, EATT
    If the Siae does not have a convention, we consider the Siae as active
    """
    # Siae with convention
    if siae["kind"] in ["AI", "ACI", "EI", "ETTI", "EITI"]:
        if ("convention_is_active" in siae) and siae["convention_is_active"]:
            return True
        return False
    # Siae without convention
    return True


def set_is_delisted(siae):
    """
    le-marche field
    Helps to track the number of Siae who were set from active to inactive during a sync.
    """
    is_active = set_is_active(siae)
    return not is_active


class Command(BaseCommand):
    """
    This command syncs the list of siae (creates new, updates existing) from les-emplois to le-marché.
    C1 = les-emplois
    C4 = le-marche

    Steps:
    1. First we fetch all the siae from les-emplois
    2. Then we loop on each of them, to create or update it (depends if its c1_id already exists or not)
    3. Don't forget to delist the siae who were not updated or inactive

    Usage:
    - poetry run python manage.py sync_with_emplois_inclusion --dry-run
    - poetry run python manage.py sync_with_emplois_inclusion
    """

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Dry run, no writes")

    def handle(self, dry_run=False, **options):
        if not os.environ.get("API_EMPLOIS_INCLUSION_TOKEN"):
            raise CommandError("Missing API_EMPLOIS_INCLUSION_TOKEN in env")

        self.stdout_info("-" * 80)
        self.stdout_info("Sync script between les-emplois & le-marché...")

        if dry_run:
            self.stdout_info("Running in dry run mode !")

        self.stdout_info("-" * 80)
        self.stdout_info("Step 1: fetching les-emplois data")
        c1_list = self.c1_export()

        self.stdout_info("-" * 80)
        self.stdout_info("Step 2: filter les-emplois data")
        c1_list_filtered = self.filter_c1_export(c1_list)

        self.stdout_info("-" * 80)
        self.stdout_info("Step 3: update le-marche data")
        # count before
        siae_total_before = Siae.objects.all().count()
        siae_active_before = Siae.objects.filter(is_active=True).count()
        siae_delisted_before = Siae.objects.filter(is_delisted=True).count()

        self.c4_update(c1_list_filtered, dry_run)
        self.c4_delist_old_siae(dry_run)

        # count after
        siae_total_after = Siae.objects.all().count()
        siae_active_after = Siae.objects.filter(is_active=True).count()
        siae_delisted_after = Siae.objects.filter(is_delisted=True).count()

        self.stdout_info("Done ! Some stats...")
        created_count = siae_total_after - siae_total_before
        updated_count = len(c1_list_filtered) - created_count
        msg_success = [
            "----- Synchronisation emplois/marché -----",
            f"Siae total: before {siae_total_before} / after {siae_total_after} / +{created_count}",
            f"Siae updated: {updated_count}",
            f"Siae active: before {siae_active_before} / after {siae_active_after}",
            f"Siae inactive: before {siae_total_before - siae_active_before} / after {siae_total_after - siae_active_after}",  # noqa
            f"Siae delisted: before {siae_delisted_before} / after {siae_delisted_after}",
        ]
        self.stdout_messages_success(msg_success)
        api_slack.send_message_to_channel("\n".join(msg_success), service_id=settings.SLACK_WEBHOOK_C4_SUPPORT_CHANNEL)

    def c1_export(self):  # noqa C901
        try:
            c1_list_temp = api_emplois_inclusion.get_siae_list()

            # clean fields
            c1_list_cleaned = list()
            for c1_siae in c1_list_temp:
                c1_siae_cleaned = {
                    **c1_siae,
                    "siret_is_valid": siret.is_valid(c1_siae["siret"]),
                    "presta_type": map_siae_presta_type(c1_siae["kind"]),
                    "nature": map_siae_nature(c1_siae["source"]),
                    "phone": re.sub("[^0-9]", "", c1_siae["phone"]),
                    "email": c1_siae["email"] or "",
                    "website": c1_siae["website"] or "",
                    # "address"
                    "post_code": c1_siae["post_code"],
                    "city": c1_siae["city"],
                    "department": c1_siae["department"],
                    "region": DEPARTMENT_TO_REGION.get(c1_siae["department"], ""),
                    # "coords"
                    "admin_name": c1_siae["admin_name"] or "",
                    "admin_email": c1_siae["admin_email"] or "",
                    "source": c1_siae["source"],
                    "is_active": set_is_active(c1_siae),
                    "asp_id": c1_siae["convention_asp_id"],
                    "is_delisted": set_is_delisted(c1_siae),
                    "c1_last_sync_date": timezone.now(),
                }

                # set coords from latitude & longitude
                c1_siae_cleaned["address"] = c1_siae_cleaned["address_line_1"]
                if c1_siae_cleaned["address_line_2"]:
                    c1_siae_cleaned["address"] += c1_siae_cleaned["address_line_2"]
                del c1_siae_cleaned["address_line_1"]
                del c1_siae_cleaned["address_line_2"]

                # set coords from latitude & longitude
                if "latitude" in c1_siae_cleaned and "longitude" in c1_siae_cleaned:
                    if c1_siae_cleaned["latitude"] and c1_siae_cleaned["longitude"]:
                        coords = {
                            "type": "Point",
                            "coordinates": [float(c1_siae["longitude"]), float(c1_siae_cleaned["latitude"])],
                        }
                        c1_siae_cleaned["coords"] = GEOSGeometry(f"{coords}")  # Feed `GEOSGeometry` with GeoJSON.
                    del c1_siae_cleaned["latitude"]
                    del c1_siae_cleaned["longitude"]

                # remove useless keys
                [c1_siae_cleaned.pop(key) for key in C1_EXTRA_KEYS]

                c1_list_cleaned.append(c1_siae_cleaned)

            self.stdout_info(f"Found {len(c1_list_cleaned)} Siae in les-emplois")
            return c1_list_cleaned
        except Exception as e:
            api_slack.send_message_to_channel("Erreur lors de la synchronisation emplois <-> marché")
            self.stdout_error(str(e))
            raise Exception(e)

    def filter_c1_export(self, c1_list):
        """
        Some rules to filter out the siae that we don't want:
        - siae with kind='RESERVED'
        """
        c1_list_filtered = []

        for c1_siae in c1_list:
            if c1_siae["kind"] not in ("RESERVED",):
                c1_list_filtered.append(c1_siae)

        return c1_list_filtered

    def c4_update(self, c1_list, dry_run):
        """
        Loop on c1_list and figure out if each siae needs to be created OR already exists (update)
        """
        progress = 0
        for c1_siae in c1_list:
            progress += 1
            if (progress % 1000) == 0:
                self.stdout_info(f"{progress}...")
            # if force_siret and c1['siret'] != force_siret:
            #     continue
            try:
                c4_siae = Siae.objects.get(c1_id=c1_siae["id"])
                self.c4_update_siae(c1_siae, c4_siae, dry_run)
            except Siae.DoesNotExist:
                self.c4_create_siae(c1_siae, dry_run)

        self.c4_delist_old_siae(dry_run)

    def c4_create_siae(self, c1_siae, dry_run):
        """
        Here we create a new Siae with les-emplois data
        """
        self.stdout_info("Creating Siae...")

        # clean fields
        rename_dict_key(c1_siae, "id", "c1_id")

        # init fields
        c1_siae["description"] = ""
        c1_siae["contact_website"] = c1_siae["website"]
        c1_siae["contact_email"] = c1_siae["admin_email"] or c1_siae["email"]
        c1_siae["contact_phone"] = c1_siae["phone"]

        # other fields
        c1_siae["is_delisted"] = False

        # create object
        if not dry_run:
            siae = Siae.objects.create(**c1_siae)
            self.add_siae_to_contact_list(siae)
            self.stdout_info(f"New Siae created / {siae.id} / {siae.name} / {siae.siret}")

    def add_siae_to_contact_list(self, siae: Siae):
        if siae.kind != "OPCS" and siae.is_active:
            properties = {
                "pays": "france",
                "nomsiae": siae.name,
            }
            mailjet_contact_list_id = settings.MAILJET_NL_CL_IMPORT_C1_SIAE_LIST_ID
            if siae.contact_email:
                api_mailjet.add_to_contact_list_async(siae.contact_email, properties, mailjet_contact_list_id)
            if siae.admin_email:
                api_mailjet.add_to_contact_list_async(siae.admin_email, properties, mailjet_contact_list_id)

    def c4_update_siae(self, c1_siae, c4_siae, dry_run):
        """
        Here we update an existing Siae with a subset of les-emplois data
        """
        if not dry_run:
            # other fields
            # c1_siae["is_delisted"] = True if not c1_siae["convention_is_active"] else False

            # keep only certain fields for update
            c1_siae_filtered = dict()
            for key in UPDATE_FIELDS:
                if key in c1_siae:
                    c1_siae_filtered[key] = c1_siae[key]

            Siae.objects.filter(c1_id=c4_siae.c1_id).update(**c1_siae_filtered)  # avoid updated_at change
            # self.stdout_info(f"Siae updated / {c4_siae.id} / {c4_siae.siret}")

    def c4_delist_old_siae(self, dry_run):
        """
        Which Siae should we delist?
        - the existing ones who haven't been updated
        - all the ones who have is_active as False
        """
        if not dry_run:
            date_yesterday = timezone.now() - timedelta(days=1)
            Siae.objects.exclude(c1_sync_skip=True).filter(c1_last_sync_date__lt=date_yesterday).update(
                is_delisted=True
            )
            Siae.objects.filter(is_active=False).update(is_delisted=True)
