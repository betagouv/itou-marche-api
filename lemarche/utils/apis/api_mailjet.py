from huey.contrib.djhuey import task
import httpx
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


BASE_URL = "https://api.mailjet.com/v3/REST/"


def get_endpoint_url(endpoint):
    return f"{BASE_URL}{endpoint}"


contact_list_endpoint = get_endpoint_url(
    f"contactslist/{settings.MAILJET_NEWSLETTER_CONTACT_LIST_BUYER_ID}/managecontact"
)


def get_default_params():
    return {}


def get_default_client(params={}):
    params |= get_default_params()
    headers = {
        "user-agent": "betagouv-lemarche/0.0.1",
    }
    client = httpx.Client(
        params=params, headers=headers, auth=(settings.MAILJET_MASTER_API_KEY, settings.MAILJET_MASTER_API_SECRET)
    )
    return client


@task()
def add_to_newsletter_async(email_adress, properties, client=None):
    """Huey task adding contact to configured contact list

    Args:
        email_adress (String): e-mail of contact
        properties (Dict): {"nom": "", "prénom": "", "pays": "france", "nomsiae": "", "poste": ""}
        client (httpx.Client, optional): client to send requests. Defaults to None.

    Raises:
        e: httpx.HTTPStatusError

    """
    data = {
        "name": email_adress,
        "properties": properties,
        "action": "addnoforce",
        "email": email_adress,
    }

    if not client:
        client = get_default_client()

    try:
        result = client.post(contact_list_endpoint, json=data)
        result.raise_for_status()
        data = result.json()
        logger.info("add user to newsletter")
        logger.info(data)
        return data
    except httpx.HTTPStatusError as e:
        logger.error("Error while fetching `%s`: %s", e.request.url, e)
        raise e
