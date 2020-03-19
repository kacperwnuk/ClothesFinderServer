import itertools

import django
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from ClothesSearchApp.models import Clothes, DetailedClothes, Type, Color, Size
from ClothesSearchApp.scrappers import HMScrapper, HOUSEScrapper, RESERVEDScrapper
# from ClothesSearchApp.scrappers.main import scrapper_test, get_clothes_general_info
from ClothesSearchApp.serializers import ClothesSerializer, DetailedClothesSerializer, TypeColorsSerializer

scrapper_mapping = {
    'HM': HMScrapper,
    'HOUSE': HOUSEScrapper,
    'RESERVED': RESERVEDScrapper,
}


# TODO: wylistowanie wszystkich dostępnych typów ubrań, rozmiarów i kolorów w zależności od typu

class ClothesView(ListAPIView):
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
        if sort_type:
            if sort_type == 'ascending':
                clothes = clothes.order_by('price')
            elif sort_type == 'descending':
                clothes = clothes.order_by('-price')

        return clothes


class DetailedClothesView(APIView):
    def get(self, request):
        detailed_clothes = DetailedClothes.objects.all()
        serializer = DetailedClothesSerializer(detailed_clothes, many=True)
        return Response(serializer.data)


class FavouriteClothesView(APIView):

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = ClothesSerializer(user.clothes_set.all(), many=True)
        return Response(serializer.data)

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        try:
            cloth = Clothes.objects.get(key=request.data['key'])
            user.clothes_set.add(cloth)
            user.save()
            serializer = ClothesSerializer(user.clothes_set.all(), many=True)
            return Response(serializer.data)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username):
        user = get_object_or_404(User, username=username)
        try:
            cloth = Clothes.objects.get(key=request.data['key'])
            user.clothes_set.remove(cloth)
            user.save()
            serializer = ClothesSerializer(user.clothes_set.all(), many=True)
            return Response(serializer.data)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TypeColorView(APIView):

    def get(self, request, cloth_type):
        type_colors = Type.objects.filter(cloth_type=cloth_type)
        return Response(TypeColorsSerializer(type_colors, many=True).data)

    def post(self, request, cloth_type):
        # laduj baze
        colors_dict = {
            'T-SHIRT': {'Beżowy', 'Czarny', 'Biały',
                        'Turkusowy', 'Kość słoniowa', 'Niebieski', 'Zielony', 'Szary'},
            'SHIRT': {'Czerwony', 'Brązowy', 'Beżowy', 'Czarny', 'Biały',
                      'Kość słoniowa', 'Niebieski', 'Zielony', 'Szary', 'Granatowy'},
            'PANTS': {'Brązowy', 'Beżowy', 'Czarny', 'Niebieski',
                      'Zielony', 'Szary', 'Granatowy'},
            'SHORTS': {'Czerwony', 'Brązowy', 'Czarny', 'Biały', 'Różowy', 'Niebieski', 'Zielony', 'Szary',
                       },
            'JACKET': {'Brązowy', 'Czarny', 'Niebieski', 'Zielony', 'Szary',
                       'Granatowy'},
            'SWEATER': {'Czerwony', 'Brązowy', 'Beżowy', 'Niebieski', 'Zielony'},

        }

        # laduj kolory
        colors = {color for sub_list in colors_dict.values() for color in sub_list}

        for color in colors:
            Color(name=color).save()

        for cloth_type in colors_dict:
            Type(cloth_type=cloth_type).save()

        for key, value in colors_dict.items():
            for color in value:
                c = Color.objects.get(name=color)
                Type.objects.get(cloth_type=key).colors.add(c)

        return Response(status=status.HTTP_200_OK)

