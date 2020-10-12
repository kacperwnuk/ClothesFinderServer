from pprint import pprint

import django
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Model
from rest_framework import status, authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from ClothesSearchApp.db_loader import load_db_cloth
from ClothesSearchApp.models import Clothes, DetailedClothes, Type, Color, Size, Occasion
from ClothesSearchApp.scrappers import HMScrapper, HOUSEScrapper, RESERVEDScrapper
from ClothesSearchApp.serializers import ClothesSerializer, DetailedClothesSerializer, TypeSerializer, \
    ColorSerializer, SizeSerializer, UserSerializer, OccasionSerializer

from ClothesSearchApp.mail import sender

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
        return clothes[:100]


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
            key = request.data['key']
            if key == 'all':
                user.clothes_set.clear()
                return Response(data={}, status=status.HTTP_200_OK)

            cloth = Clothes.objects.get(key=key)
            user.clothes_set.remove(cloth)
            user.save()
            serializer = ClothesSerializer(user.clothes_set.all(), many=True)
            return Response(serializer.data)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)


class OccasionView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.auth.user
        serializer = OccasionSerializer(user.occasion_set.all(), many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.auth.user
        key = request.data['key']
        type_name = request.data['type']
        color_name = request.data['color']
        size_name = request.data['size']
        price = request.data['price']
        occasion = Occasion(key=key, type=Type.objects.get(name=type_name), color=Color.objects.get(name=color_name),
                            size=Size.objects.get(name=size_name), price=price, user=user)
        occasion.save()
        serializer = OccasionSerializer(occasion)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.auth.user
        key = request.data['key']
        try:
            occasion = Occasion.objects.get(key=key, user=user)
            serializer = OccasionSerializer(occasion)
            occasion.delete()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(data="There is no key for this user", status=status.HTTP_400_BAD_REQUEST)


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


@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def email_favourites(request):
    user = request.auth.user

    clothes_urls = [clothes.page_link for clothes in user.clothes_set.all()]
    message = "".join([f"{url} \n" for url in clothes_urls])
    sender.send_mail(user.email, message)

    return Response(data="Email sent.", status=status.HTTP_200_OK)
