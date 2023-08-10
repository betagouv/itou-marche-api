import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lemarche.api.emails.serializers import EmailsSerializer
from lemarche.conversations.models import Conversation
from lemarche.www.conversations.tasks import send_email_from_conversation


logger = logging.getLogger(__name__)


class InboundParsingEmailView(APIView):
    def post(self, request):
        serializer = EmailsSerializer(data=request.data)
        if serializer.is_valid():
            inboundEmail = serializer.validated_data.get("items")[0]
            address_mail = inboundEmail["To"][0]["Address"]
            # get conversation object
            conv_uuid, user_kind = Conversation.get_email_info_from_address(address_mail)
            conv: Conversation = Conversation.objects.get(uuid=conv_uuid)
            # save the input data
            conv.data.append(serializer.data)
            conv.save()
            # make the transfert of emails
            send_email_from_conversation(
                conv=conv,
                user_kind=user_kind,
                email_subject=inboundEmail.get("Subject", conv.title),
                email_body=inboundEmail.get("RawTextBody"),
                email_body_html=inboundEmail.get("RawHtmlBody"),
            )
            return Response(conv.uuid, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"[INBOUND_PARSING_WEBHOOK_ERROR] {str(serializer.errors)}")
            logger.error(f"[INBOUND_PARSING_WEBHOOK_ERROR] {str(serializer.data)}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
