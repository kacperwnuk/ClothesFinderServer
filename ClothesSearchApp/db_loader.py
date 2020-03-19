import os
from multiprocessing.pool import Pool
from pprint import pprint
from time import perf_counter

from ClothesSearchApp.scrappers.defaults import transform_request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ClothesFinderServer.settings")
import django

django.setup()

from ClothesSearchApp.scrappers.RESERVEDScrapper import RESERVEDScrapper
from ClothesSearchApp.scrappers.HMScrapper import HMScrapper
from ClothesSearchApp.scrappers.HOUSEScrapper import HOUSEScrapper

from ClothesSearchApp.models import (
    Clothes,
    Shop,
    Color,
    Type,
    DetailedClothes,
    Size,
)

scrapper_mapping = {
    'HM': HMScrapper,
    'House': HOUSEScrapper,
    'Reserved': RESERVEDScrapper,
}
# scrappers = [HMScrapper, RESERVEDScrapper, HOUSEScrapper]
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
    'SWEATER': {'Czerwony', 'Brązowy', 'Beżowy', 'Niebieski', 'Zielony', 'Szary', 'Biały', 'Granatowy'},

}
shop_names = ['HM', 'Reserved', 'House']


def load_shops():
    for shop_name in shop_names:
        Shop(name=shop_name).save()


def load_colors():
    colors = {color for sub_list in colors_dict.values() for color in sub_list}

    for color in colors:
        Color(name=color).save()


def load_type_colors():
    for cloth_type in colors_dict:
        Type(cloth_type=cloth_type).save()

    for key, value in colors_dict.items():
        for color in value:
            c = Color.objects.get(name=color)
            Type.objects.get(cloth_type=key).colors.add(c)


def load_sizes():
    for (size_name, _) in Size.SIZES:
        Size(name=size_name).save()


def load_general_clothes():
    requests = _get_general_requests()

    t1 = perf_counter()
    get_clothes_general_info(requests)
    t2 = perf_counter()

    print(t2 - t1)


def create_scrappers(scrapper_classes):
    return [scrapper_class() for scrapper_class in scrapper_classes]


def get_clothes_general_info(requests):
    trs = [transform_request(request) for request in requests]
    clothes = []
    for shop_name in shop_names:
        # if shop_name == 'Reserved':
            scrapper = scrapper_mapping[shop_name]()
            for tr in trs:
                if tr['type'] in scrapper.clothes_type_class.clothes_types:
                    clothes += scrapper.get_clothes_type_general_data(tr)
    # p = Pool(2)
    # clothes = p.map(hs.get_clothes_type_general_data, trs)
    # p.terminate()
    # p.join()
    return clothes


def load_detailed_clothes():
    requests = _get_detailed_requests()
    clothes = []
    t1 = perf_counter()

    for shop_name in shop_names:
        if shop_name == 'HM':
            scrapper = scrapper_mapping[shop_name]()
            shop_requests = [request for request in requests if request['shop'] == shop_name]
            # p = Pool(2)
            # clothes = p.map(scrapper.get_clothes_type_detailed_data, [request['id'] for request in shop_requests])
            # p.terminate()
            # p.join()

            clothes += [scrapper.get_clothes_type_detailed_data(request['id']) for request in shop_requests]
    t2 = perf_counter()
    print(t2 - t1)
    return clothes


def _get_detailed_requests():
    reqs = []
    for cloth in Clothes.objects.all():
        req = _create_detailed_request(cloth.key, cloth.shop.name)
        reqs.append(req)
    return reqs


def _get_general_requests():
    reqs = []
    for (cloth_type, _) in Type.TYPES:
        for (size, _) in Size.SIZES:
            for color in Type.objects.get(name=cloth_type).colors.all():
                req = _create_general_request(cloth_type, size, color.name)
                reqs.append(req)
        break
    pprint(reqs)
    return reqs


def _create_general_request(cloth_type, size, color):
    return {
        'sort_type': 3,
        'size': size,
        'type': cloth_type,
        'color': color
    }


def _create_detailed_request(cloth_id, shop_name):
    return {
        'id': cloth_id,
        'shop': shop_name
    }


def load_db():
    # TODO: wczytac sklepy - done
    # wczytac kolory
    # wczytac rozmiary
    # wczytac ciuchy ogólne info
    # wczytac czesc szczegolowego info - na ile czas pozwoli
    load_shops()
    load_colors()
    load_type_colors()
    load_sizes()
    load_general_clothes()
    # load_detailed_clothes()


def clear_db():
    models = [Size, Color, Type, Clothes, DetailedClothes, Shop]
    for model in models:
        model.objects.all().delete()


def show_db():
    models = [Size, Color, Type, Clothes, DetailedClothes, Shop]
    for model in models:
        print(model.objects.all())


if __name__ == '__main__':
    # load_db()
    # clear_db()
    # show_db()
    # load_general_clothes()
    load_detailed_clothes()
