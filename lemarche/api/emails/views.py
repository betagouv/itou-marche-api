import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lemarche.api.emails.serializers import EmailsSerializer
from lemarche.conversations.models import Conversation


logger = logging.getLogger(__name__)


class InboundParsingEmailView(APIView):
    def post(self, request):
        serializer = EmailsSerializer(data=request.data)
        if serializer.is_valid():
            # TODO make transfert
            inboundEmail = serializer.validated_data.get("items")[0]
            logger.info("Transfert email from : ", inboundEmail["From"])
            logger.info("To : ", inboundEmail["To"])
            logger.info("Content Email Text : ", inboundEmail["RawTextBody"])
            logger.info("Content Email Html : ", inboundEmail["RawHtmlBody"])
            conv: Conversation = Conversation.objects.create(data=serializer.data)
            logger.info(conv)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
