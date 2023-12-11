from lemarche.conversations.models import Conversation
from lemarche.siaes.models import Siae
from lemarche.utils.emails import send_mail_async, whitelist_recipient_list


DISCLAIMER_ATTACHMENTS = (
    "\n\n<i>Veuillez noter que cette conversation email ne prend pas en charge les pièces jointes.\n"
    "Pour envoyer un document, un devis ou autre, demandez les coordonnées direct de votre interlocuteur</i>"
)


def send_first_email_from_conversation(conv: Conversation):
    siae: Siae = conv.siae
    from_email = f"{conv.sender_first_name} {conv.sender_last_name} <{conv.sender_email_buyer_encoded}>"

    sender_company_name = ""
    if conv.sender_user and conv.sender_user.company_name:
        sender_company_name = f"{conv.sender_user.company_name}\n"

    disclaimer = (
        f"\n\n{conv.sender_first_name} {conv.sender_last_name}\n"
        f"{sender_company_name}"
        f"\n\n{'*'*80}\n\n"
        f"<i>Ce client vous a contacté via le Marché de l'inclusion. "
        "Pour échanger avec lui, répondez simplement à cet e-mail.</i>\n"
    ) + DISCLAIMER_ATTACHMENTS

    send_mail_async(
        email_subject=conv.title,
        email_body=conv.initial_body_message + disclaimer,
        recipient_list=whitelist_recipient_list([siae.contact_email]),
        from_email=from_email,
    )


def send_email_from_conversation(
    conv: Conversation, user_kind: str, email_subject: str, email_body: str, email_body_html: str
):
    if user_kind == Conversation.USER_KIND_SENDER_TO_SIAE:
        # from the buyer to the siae
        from_email = f"{conv.sender_first_name} {conv.sender_last_name} <{conv.sender_email_buyer_encoded}>"
        send_mail_async(
            email_subject=email_subject,
            email_body=email_body + DISCLAIMER_ATTACHMENTS,
            recipient_list=whitelist_recipient_list([conv.sender_email_siae]),
            from_email=from_email,
            email_body_html=email_body_html,
        )
    elif user_kind == Conversation.USER_KIND_SENDER_TO_BUYER:
        # from the siae to the buyer
        siae: Siae = conv.siae
        from_email = f"{siae.contact_full_name} <{conv.sender_email_siae_encoded}>"
        send_mail_async(
            email_subject=email_subject,
            email_body=email_body + DISCLAIMER_ATTACHMENTS,
            recipient_list=whitelist_recipient_list([conv.sender_email_buyer]),
            from_email=from_email,
            email_body_html=email_body_html,
        )
