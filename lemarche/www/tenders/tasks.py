from django.conf import settings
from django.utils import timezone

from lemarche.siaes.models import Siae
from lemarche.tenders.models import Tender, TenderSiae
from lemarche.utils.apis import api_mailjet
from lemarche.utils.emails import whitelist_recipient_list
from lemarche.utils.urls import get_share_url_object
from lemarche.www.tenders.constants import match_tender_for_partners


EMAIL_SUBJECT_PREFIX = f"[{settings.BITOUBI_ENV.upper()}] " if settings.BITOUBI_ENV != "prod" else ""


# @task()
def send_tender_emails_to_siaes(tender: Tender):
    """
    All corresponding Siae will be contacted
    """
    for siae in tender.siaes.all():
        send_tender_email_to_siae(tender, siae)

    tender.tendersiae_set.update(email_send_date=timezone.now())
    # will be moved on global action in backoffice admin
    match_tender_for_partners(tender=tender, send_email_func=send_tender_email_to_partner)


def send_tender_email_to_partner(tender: Tender, partner: dict):
    email_subject = EMAIL_SUBJECT_PREFIX + f"{tender.author.company_name} recherchent des structures inclusives"
    recipient_list = whitelist_recipient_list(partner.get("contacts_email"))
    if recipient_list:
        variables = {
            "TENDER_AUTHOR_COMPANY": tender.author.company_name,
            "TENDER_SECTORS": tender.get_sectors_names,
            "TENDER_PERIMETERS": tender.get_perimeters_names,
            "TENDER_URL": get_share_url_object(tender),
        }

        api_mailjet.send_transactional_email_many_recipient_with_template(
            template_id=settings.MAILJET_TENDERS_PRESENTATION_TEMPLATE_PARTNERS_ID,
            subject=email_subject,
            recipient_email_list=recipient_list,
            variables=variables,
        )


# @task()
def send_tender_email_to_siae(tender: Tender, siae: Siae):
    email_subject = (
        EMAIL_SUBJECT_PREFIX + f"{tender.author.company_name} a besoin de vous sur le marché de l'inclusion"
    )
    recipient_list = whitelist_recipient_list([siae.contact_email])
    if recipient_list:
        recipient_email = recipient_list[0] if recipient_list else ""
        recipient_name = siae.contact_full_name

        variables = {
            "SIAE_CONTACT_FIRST_NAME": siae.contact_first_name,
            "TENDER_AUTHOR_COMPANY": tender.author.company_name,
            "TENDER_KIND": tender.get_kind_display(),
            "TENDER_SECTORS": tender.get_sectors_names,
            "TENDER_PERIMETERS": tender.get_perimeters_names,
            "TENDER_URL": get_share_url_object(tender),
        }

        api_mailjet.send_transactional_email_with_template(
            template_id=settings.MAILJET_TENDERS_PRESENTATION_TEMPLATE_ID,
            subject=email_subject,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            variables=variables,
        )


def send_siae_interested_email_to_author(tender: Tender):
    """
    The author is notified (by intervals) when new Siaes show interest (contact_click_date set)
    Intervals:
    - first Siae
    - every 5 Siae
    """
    tender_siae_contact_click_count = TenderSiae.objects.filter(
        tender=tender, contact_click_date__isnull=False
    ).count()

    if (tender_siae_contact_click_count > 0) and (tender_siae_contact_click_count < 50):
        if (tender_siae_contact_click_count == 1) or (tender_siae_contact_click_count % 5 == 0):
            if tender_siae_contact_click_count == 1:
                email_subject = EMAIL_SUBJECT_PREFIX + "Une première structure intéressée !"
                template_id = settings.MAILJET_TENDERS_SIAE_INTERESTED_1_TEMPLATE_ID
            else:
                email_subject = EMAIL_SUBJECT_PREFIX + "5 nouvelles structures intéressées !"
                template_id = settings.MAILJET_TENDERS_SIAE_INTERESTED_5_TEMPLATE_ID
            recipient_list = whitelist_recipient_list([tender.author.email])  # tender.contact_email ?
            if recipient_list:
                recipient_email = recipient_list[0] if recipient_list else ""
                recipient_name = tender.author.full_name

                variables = {
                    "TENDER_AUTHOR_FIRST_NAME": tender.author.first_name,
                    "TENDER_TITLE": tender.title,
                    "TENDER_SIAE_INTERESTED_LIST_URL": f"{get_share_url_object(tender)}/structures-interessees",  # noqa
                }

                api_mailjet.send_transactional_email_with_template(
                    template_id=template_id,
                    subject=email_subject,
                    recipient_email=recipient_email,
                    recipient_name=recipient_name,
                    variables=variables,
                )
