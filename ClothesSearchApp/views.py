import itertools
from pprint import pprint

import django
from django.contrib.auth.models import User
from django.db.models import Q, Model
from rest_framework import status, authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from ClothesSearchApp.db_loader import load_db_cloth
from ClothesSearchApp.models import Clothes, DetailedClothes, Type, Color, Size
from ClothesSearchApp.scrappers import HMScrapper, HOUSEScrapper, RESERVEDScrapper
# from ClothesSearchApp.scrappers.main import scrapper_test, get_clothes_general_info
from ClothesSearchApp.serializers import ClothesSerializer, DetailedClothesSerializer, TypeSerializer, \
    ColorSerializer, SizeSerializer, UserSerializer

scrapper_mapping = {
    'HM': HMScrapper,
    'HOUSE': HOUSEScrapper,
    'RESERVED': RESERVEDScrapper,
}


class UserCreateAPI(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(token.key)


class ClothesView(ListAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = ClothesSerializer

    def get_queryset(self):
        clothes = Clothes.objects.all()
        filters = Q()

        type = self.request.query_params.get('type')
        if type:
            filters &= Q(type__name=type)
            # clothes = clothes.filter(type=type)
        else:
            pass

        color = self.request.query_params.get('color')
        if color:
            filters &= Q(colors__name=color)
            # clothes = clothes.filter(detailedclothes__colors__in=color)

        size = self.request.query_params.get('size')
        if size:
            filters &= Q(sizes__name=size)
            # clothes = clothes.filter(sizes_)

        lower_price = self.request.query_params.get('lowerPrice')
        if lower_price:
            filters &= Q(price__gte=lower_price)
            # clothes = clothes.filter(price__gte=lower_price)

        higher_price = self.request.query_params.get('higherPrice')
        if higher_price:
            filters &= Q(price__lte=higher_price)
            # clothes = clothes.filter(price__lte=higher_price)

        clothes = clothes.filter(filters)

        sort_type = self.request.query_params.get('sortType')
        if sort_type == 'ascending':
            clothes = clothes.order_by('price')
        elif sort_type == 'descending':
            clothes = clothes.order_by('-price')
        return clothes[:50]


class DetailedClothesView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        detailed_clothes = None
        try:
            key = request.query_params.get('id')
            shop = request.query_params.get('shop')
            if not key or not shop:
                return Response(data="Zły format zapytania", status=status.HTTP_400_BAD_REQUEST)

            req = {
                'id': key,
                'shop': shop
            }
            detailed_clothes = DetailedClothes.objects.get(clothes__key=key)
        except DetailedClothes.DoesNotExist as e:
            if Clothes.objects.filter(key=key):
                detailed_clothes = load_db_cloth(req)
                # print("Nie ma detali ale jest general")
            else:
                return Response(data="Produkt nie występuje w bazie", status=status.HTTP_400_BAD_REQUEST)
        serializer = DetailedClothesSerializer(detailed_clothes)
        return Response(serializer.data)


class FavouriteClothesView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.auth.user
        serializer = ClothesSerializer(user.clothes_set.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.auth.user
        try:
            cloth = Clothes.objects.get(key=request.data['key'])
            user.clothes_set.add(cloth)
            user.save()
            serializer = ClothesSerializer(user.clothes_set.all(), many=True)
            return Response(serializer.data)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.auth.user
        try:
            cloth = Clothes.objects.get(key=request.data['key'])
            user.clothes_set.remove(cloth)
            user.save()
            serializer = ClothesSerializer(user.clothes_set.all(), many=True)
            return Response(serializer.data)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TypeView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        types = Type.objects.all()
        serializer = TypeSerializer(types, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ColorView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, cloth_type):
        colors = get_object_or_404(Type, name=cloth_type).colors.all()
        serializer = ColorSerializer(colors, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class SizeView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sizes = Size.objects.all()
        serializer = SizeSerializer(sizes, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

