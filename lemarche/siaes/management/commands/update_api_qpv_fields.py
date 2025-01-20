from django.db.models import Q

from lemarche.siaes.management.base_update_api import UpdateAPICommand
from lemarche.utils.apis.api_qpv import IS_QPV_KEY, QPV_CODE_KEY, QPV_NAME_KEY, get_default_client, is_in_qpv


class Command(UpdateAPICommand):
    """
    Populates API QPV

    Note: Only on Siae who have coords, filter only on Siae not updated by the API since a two months

    Usage: poetry run python manage.py update_api_qpv_fields
    Usage: poetry run python manage.py update_api_qpv_fields --limit 10
    Usage: poetry run python manage.py update_api_qpv_fields --force
    Usage: poetry run python manage.py update_api_qpv_fields --limit 100 --no-force
    """

    API_NAME = "QPV"
    FIELDS_TO_BULK_UPDATE = ["is_qpv", "api_qpv_last_sync_date", "qpv_code", "qpv_name"]
    CLIENT = get_default_client()

    IS_TAGET_KEY = IS_QPV_KEY
    TARGET_CODE_KEY = QPV_CODE_KEY
    TARGET_NAME_KEY = QPV_NAME_KEY

    @staticmethod
    def get_filter_query(date_limit) -> Q:
        return Q(api_qpv_last_sync_date__lte=date_limit) | Q(api_qpv_last_sync_date__isnull=True)

    @staticmethod
    def is_in_target(latitude, longitude, client):
        return is_in_qpv(latitude, longitude, client=client)
