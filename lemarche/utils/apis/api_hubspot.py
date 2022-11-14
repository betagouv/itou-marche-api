import logging

from django.conf import settings
from hubspot import Client
from hubspot.crm.contacts import ApiException, SimplePublicObjectInput


# from huey.contrib.djhuey import task


logger = logging.getLogger(__name__)


BASE_URL = "https://api.hubapi.com/crm/v3/"


def get_default_client():
    client = Client.create(access_token=settings.HUBSPOT_API_KEY)
    return client


ENV_NOT_ALLOWED = "test"


# @task()
def add_to_contacts_async(
    email: str, company: str, firstname: str, lastname: str, phone: str, website: str, client: Client = None
):
    """Huey task adding contact to Hubspot CRM

    Args:
        email (str)
        company (str)
        firstname (str)
        lastname (str)
        phone (str)
        website (str)
        client (Client, optional): HubspotClient. Defaults to None.

    Raises:
        e: ApiException

    Returns:
        _type_: _description_
    """
    if not client:
        client = get_default_client()

    if settings.BITOUBI_ENV not in ENV_NOT_ALLOWED:
        try:
            properties = {
                "company": company,
                "email": email,
                "firstname": firstname,
                "lastname": lastname,
                "phone": phone,
                "website": website,
            }
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            api_response = client.crm.contacts.basic_api.create(simple_public_object_input=simple_public_object_input)
            print(api_response)
            return api_response
        except ApiException as e:
            logger.error("Exception when calling basic_api->create: %s\n" % e)
            raise e
    else:
        logger.info("Hubspot: not add contact to the crm (DEV or TEST environment detected)")
