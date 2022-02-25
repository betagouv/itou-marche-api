from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone

from lemarche.utils.apis import api_mailjet
from lemarche.utils.emails import whitelist_recipient_list
from lemarche.utils.urls import get_domain_url


EMAIL_SUBJECT_PREFIX = f"[{settings.BITOUBI_ENV.upper()}] " if settings.BITOUBI_ENV != "prod" else ""


def send_siae_user_request_email_to_assignee(siae_user_request):
    """
    Send request to the assignee
    """
    email_subject = EMAIL_SUBJECT_PREFIX + "Nouveau collaborateur"
    recipient_list = whitelist_recipient_list([siae_user_request.assignee.email])
    recipient_email = recipient_list[0] if recipient_list else ""
    recipient_name = siae_user_request.assignee.full_name

    variables = {
        "ASSIGNEE_FULL_NAME": siae_user_request.assignee.full_name,
        "INITIATOR_FULL_NAME": siae_user_request.initiator.full_name,
        "SIAE_NAME": siae_user_request.siae.name_display,
        "SIAE_EDIT_USERS_URL": f"https://{get_domain_url()}{reverse_lazy('dashboard:siae_edit_users', args=[siae_user_request.siae.slug])}",  # noqa
    }

    api_mailjet.send_transactional_email_with_template(
        template_id=settings.MAILJET_SIAEUSERREQUEST_ASSIGNEE_TEMPLATE_ID,
        subject=email_subject,
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        variables=variables,
    )

    # log email
    log_item = {
        "action": "email_sent",
        "email_to": recipient_email,
        "email_subject": email_subject,
        # "email_body": email_body,
        "email_timestamp": timezone.now().isoformat(),
    }
    siae_user_request.logs.append(log_item)
    siae_user_request.save()


def send_siae_user_request_response_email_to_initiator(siae_user_request, response=None):
    """
    Send request response (True or False) to the initial user
    """
    email_subject_text = "Accéder à votre structure" if response else "Rattachement refusé"
    email_subject = EMAIL_SUBJECT_PREFIX + email_subject_text
    email_template_id = (
        settings.MAILJET_SIAEUSERREQUEST_INITIATOR_RESPONSE_POSITIVE_TEMPLATE_ID
        if response
        else settings.MAILJET_SIAEUSERREQUEST_INITIATOR_RESPONSE_NEGATIVE_TEMPLATE_ID
    )
    recipient_list = whitelist_recipient_list([siae_user_request.initiator.email])
    recipient_email = recipient_list[0] if recipient_list else ""
    recipient_name = siae_user_request.initiator.full_name

    variables = {
        "ASSIGNEE_FULL_NAME": siae_user_request.assignee.full_name,
        "INITIATOR_FULL_NAME": siae_user_request.initiator.full_name,
        "SIAE_NAME": siae_user_request.siae.name_display,
        "SIAE_EDIT_USERS_URL": f"https://{get_domain_url()}{reverse_lazy('dashboard:siae_edit_users', args=[siae_user_request.siae.slug])}",  # noqa
    }

    api_mailjet.send_transactional_email_with_template(
        template_id=email_template_id,
        subject=email_subject,
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        variables=variables,
    )

    # log email
    log_item = {
        "action": "email_sent",
        "email_to": recipient_email,
        "email_subject": email_subject,
        # "email_body": email_body,
        "email_timestamp": timezone.now().isoformat(),
    }
    siae_user_request.logs.append(log_item)
    siae_user_request.save()


def send_siae_user_request_reminder_3_days_emails(siae_user_request):
    """
    Send request reminder (after 3 days) to:
    - the initial user
    - to the assignee
    """
    send_siae_user_request_reminder_3_days_email_to_assignee(siae_user_request)
    send_siae_user_request_reminder_3_days_email_to_initiator(siae_user_request)


def send_siae_user_request_reminder_3_days_email_to_assignee(siae_user_request):
    email_subject = EMAIL_SUBJECT_PREFIX + "Nouveau collaborateur"
    recipient_list = whitelist_recipient_list([siae_user_request.assignee.email])
    recipient_email = recipient_list[0] if recipient_list else ""
    recipient_name = siae_user_request.assignee.full_name

    variables = {
        "ASSIGNEE_FULL_NAME": siae_user_request.assignee.full_name,
        "INITIATOR_FULL_NAME": siae_user_request.initiator.full_name,
        "SIAE_NAME": siae_user_request.siae.name_display,
        "SIAE_EDIT_USERS_URL": f"https://{get_domain_url()}{reverse_lazy('dashboard:siae_edit_users', args=[siae_user_request.siae.slug])}",  # noqa
    }

    api_mailjet.send_transactional_email_with_template(
        template_id=settings.MAILJET_SIAEUSERREQUEST_REMINDER_1_ASSIGNEE_TEMPLATE_ID,
        subject=email_subject,
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        variables=variables,
    )

    # log email
    log_item = {
        "action": "email_sent",
        "email_to": recipient_email,
        "email_subject": email_subject,
        # "email_body": email_body,
        "email_timestamp": timezone.now().isoformat(),
    }
    siae_user_request.logs.append(log_item)
    siae_user_request.save()


def send_siae_user_request_reminder_3_days_email_to_initiator(siae_user_request):
    email_subject = EMAIL_SUBJECT_PREFIX + "Rattachement sans réponse"
    recipient_list = whitelist_recipient_list([siae_user_request.initiator.email])
    recipient_email = recipient_list[0] if recipient_list else ""
    recipient_name = siae_user_request.initiator.full_name

    variables = {
        "ASSIGNEE_FULL_NAME": siae_user_request.assignee.full_name,
        "INITIATOR_FULL_NAME": siae_user_request.initiator.full_name,
        "SIAE_NAME": siae_user_request.siae.name_display,
        "SIAE_EDIT_USERS_URL": f"https://{get_domain_url()}{reverse_lazy('dashboard:siae_edit_users', args=[siae_user_request.siae.slug])}",  # noqa
    }

    api_mailjet.send_transactional_email_with_template(
        template_id=settings.MAILJET_SIAEUSERREQUEST_REMINDER_1_INITIATOR_TEMPLATE_ID,
        subject=email_subject,
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        variables=variables,
    )

    # log email
    log_item = {
        "action": "email_sent",
        "email_to": recipient_email,
        "email_subject": email_subject,
        # "email_body": email_body,
        "email_timestamp": timezone.now().isoformat(),
    }
    siae_user_request.logs.append(log_item)
    siae_user_request.save()


def send_siae_user_request_reminder_8_days_emails(siae_user_request):
    """
    Send request reminder (after 8 days) to:
    - the initial user
    - to the assignee
    """
    send_siae_user_request_reminder_8_days_email_to_assignee(siae_user_request)
    send_siae_user_request_reminder_8_days_email_to_initiator(siae_user_request)


def send_siae_user_request_reminder_8_days_email_to_assignee(siae_user_request):
    email_subject = EMAIL_SUBJECT_PREFIX + "Nouveau collaborateur"
    recipient_list = whitelist_recipient_list([siae_user_request.assignee.email])
    recipient_email = recipient_list[0] if recipient_list else ""
    recipient_name = siae_user_request.assignee.full_name

    variables = {
        "ASSIGNEE_FULL_NAME": siae_user_request.assignee.full_name,
        "INITIATOR_FULL_NAME": siae_user_request.initiator.full_name,
        "SIAE_NAME": siae_user_request.siae.name_display,
        "SIAE_EDIT_USERS_URL": f"https://{get_domain_url()}{reverse_lazy('dashboard:siae_edit_users', args=[siae_user_request.siae.slug])}",  # noqa
        # "SUPPORT_URL": f"https://{get_domain_url()}{reverse_lazy('pages:contact')}?siret={siae_user_request.siae.siret}",  # noqa
    }

    api_mailjet.send_transactional_email_with_template(
        template_id=settings.MAILJET_SIAEUSERREQUEST_REMINDER_2_ASSIGNEE_TEMPLATE_ID,
        subject=email_subject,
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        variables=variables,
    )

    # log email
    log_item = {
        "action": "email_sent",
        "email_to": recipient_email,
        "email_subject": email_subject,
        # "email_body": email_body,
        "email_timestamp": timezone.now().isoformat(),
    }
    siae_user_request.logs.append(log_item)
    siae_user_request.save()


def send_siae_user_request_reminder_8_days_email_to_initiator(siae_user_request):
    email_subject = EMAIL_SUBJECT_PREFIX + "Rattachement sans réponse"
    recipient_list = whitelist_recipient_list([siae_user_request.initiator.email])
    recipient_email = recipient_list[0] if recipient_list else ""
    recipient_name = siae_user_request.initiator.full_name

    variables = {
        "ASSIGNEE_FULL_NAME": siae_user_request.assignee.full_name,
        "INITIATOR_FULL_NAME": siae_user_request.initiator.full_name,
        "SIAE_NAME": siae_user_request.siae.name_display,
        "SIAE_EDIT_USERS_URL": f"https://{get_domain_url()}{reverse_lazy('dashboard:siae_edit_users', args=[siae_user_request.siae.slug])}",  # noqa
        "SUPPORT_URL": f"https://{get_domain_url()}{reverse_lazy('pages:contact')}?siret={siae_user_request.siae.siret}",  # noqa
    }

    api_mailjet.send_transactional_email_with_template(
        template_id=settings.MAILJET_SIAEUSERREQUEST_REMINDER_2_INITIATOR_TEMPLATE_ID,
        subject=email_subject,
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        variables=variables,
    )

    # log email
    log_item = {
        "action": "email_sent",
        "email_to": recipient_email,
        "email_subject": email_subject,
        # "email_body": email_body,
        "email_timestamp": timezone.now().isoformat(),
    }
    siae_user_request.logs.append(log_item)
    siae_user_request.save()
