from itou_c4_api.c4_directory.models import Siae
from itou_c4_api.c4_directory.serializers import (
    SectorSerializer,
    SectorStringSerializer,
    SiaeHyperSerializer,
    SiaeLightSerializer,
    SiaeSerializer,
)
from itou_c4_api.cocorico.models import Directory, DirectorySector, Sector, SectorString
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from hashids import Hashids
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from itou_c4_api.users.models import User


hasher = Hashids(alphabet="1234567890ABCDEF", min_length=5)


class SiaesViewSet(viewsets.ModelViewSet):
    queryset = Directory.objects.all()
    serializer_class = SiaeHyperSerializer

    def list(self, request):
        """
        Liste des structures inclusives reprises dans le marché de l'inclusion.
        """
        if request.method == "GET":
            siaes = Directory.objects.all()
            token = request.GET.get("token", None)
            if not token:
                # serializer = SiaeLightSerializer(siaes[:10], many=True)
                serializer = SiaeHyperSerializer(
                    siaes[:10],
                    many=True,
                    context={"request": request},
                )
            else:

                try:
                    user = User.objects.get(api_key=token)
                    assert user.has_perm("c4_directory.access_api")
                except User.DoesNotExist:
                    return HttpResponse("503: Not Allowed", status=503)

                serializer = SiaeLightSerializer(siaes, many=True)
            # return JsonResponse(serializer.data, safe=False)
            return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Détail d'une structure
        """
        try:
            queryset = Directory.objects.filter()
            # siae = DirectorySector.objects.all().select_related('Directory').select_related('Sector')
            token = request.GET.get("token", None)
            if not token:
                # serializer = SiaeLightSerializer(siae, many=False)
                siae = get_object_or_404(queryset, pk=pk)
                serializer = SiaeHyperSerializer(
                    queryset,
                    context={"request": request},
                )
            else:
                try:
                    user = User.objects.get(api_key=token)
                    assert user.has_perm("c4_directory.access_api")
                except User.DoesNotExist:
                    return HttpResponse("503: Not Allowed", status=503)

                serializer = SiaeSerializer(siae, many=False)
            return Response(serializer.data)
        except Siae.DoesNotExist:
            return HttpResponse(status=404)


# @csrf_exempt
# @api_view(['GET'])
# def siae_list(request, token=None):
#     """
#     Liste des structures inclusives reprises dans le marché de l'inclusion.
#     """
#     if request.method == 'GET':
#         siaes = Directory.objects.all()
#         token = request.GET.get('token', None)
#         if not token:
#             serializer = SiaeLightSerializer(siaes[:10], many=True)
#         else:
#
#             try:
#                 user = User.objects.get(api_key=token)
#                 assert user.has_perm('c4_directory.access_api')
#             except User.DoesNotExist:
#                 return HttpResponse('503: Not Allowed', status=503)
#
#             serializer = SiaeLightSerializer(siaes, many=True)
#         # return JsonResponse(serializer.data, safe=False)
#         return Response(serializer.data)


@csrf_exempt
@api_view(["GET"])
def siae_detail(request, key):
    """
    Détail d'une structure
    """
    try:
        siae = Directory.objects.get(pk=key)
        # siae = DirectorySector.objects.all().select_related('Directory').select_related('Sector')
        token = request.GET.get("token", None)
        if not token:
            serializer = SiaeLightSerializer(siae, many=False)
        else:
            try:
                user = User.objects.get(api_key=token)
                assert user.has_perm("c4_directory.access_api")
            except User.DoesNotExist:
                return HttpResponse("503: Not Allowed", status=503)

            serializer = SiaeSerializer(siae, many=False)
        return Response(serializer.data)
    except Siae.DoesNotExist:
        return HttpResponse(status=404)


@csrf_exempt
@api_view(["GET"])
def sector_list(request):
    """
    Liste hiérarchisée des secteurs d'activité des structures.
    """
    if request.method == "GET":
        # sectors = Sector.objects.select_related('SectorString').all()
        sectors = SectorString.objects.filter(translatable__gte=10).select_related("translatable").all()
        # sectors = Sector.objects.all()
        serializer = SectorStringSerializer(sectors, many=True)
        return Response(serializer.data)


@csrf_exempt
@api_view(["GET"])
def sector_detail(request, key):
    """
    Détail secteur d'activité
    """
    if request.method == "GET":
        # sectors = Sector.objects.select_related('SectorString').all()
        ckey = hasher.decode(key)[0]
        sector = SectorString.objects.select_related("translatable").get(translatable=ckey)
        # sector = SectorString.objects.filter(translatable=ckey).select_related('translatable').all()
        serializer = SectorStringSerializer(sector, many=False)
        return Response(serializer.data)
