import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ClothesFinderServer.settings")
import django

django.setup()
from ClothesSearchApp.scrappers.HOUSEScrapper import HOUSEScrapper
from ClothesSearchApp.scrappers.abstract import AbstractClothesType
from ClothesSearchApp.scrappers.defaults import ClothesType


class _RESERVEDClothesType(AbstractClothesType):
    clothes_types = {
        ClothesType.T_SHIRT: 't-shirts',
        ClothesType.SHIRT: 'shirts',
        ClothesType.PANTS: 'trousers',
        ClothesType.SHORTS: 'jeans',
        ClothesType.JACKET: 'jackets',
        ClothesType.SWEATER: 'sweaters',
    }


class RESERVEDScrapper(HOUSEScrapper):
    shop_name = 'Reserved'
    clothes_type_class = _RESERVEDClothesType

    general_page_prefix = 'https://www.reserved.com/pl/pl/man/clothes/'
    detail_page_prefix = 'https://www.reserved.com/pl/pl/'
