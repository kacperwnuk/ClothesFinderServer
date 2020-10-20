import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ClothesFinderServer.settings")
import django

django.setup()

import re
from typing import List

from django import db
from ClothesSearchApp.scrappers.abstract import AbstractSortType, AbstractClothesType, AbstractSizeType, Scrapper, \
    AbstractColorType
from ClothesSearchApp.scrappers.defaults import SortType, ClothesType, SizeType, ColorType

db.connections.close_all()


class _HMSortType(AbstractSortType):
    sort_types = {
        SortType.NONE: '',
        SortType.ASCENDING: 'ascPrice',
        SortType.DESCENDING: 'descPrice'
    }
    key = 'sort'

    def __init__(self, sort_type: SortType):
        super().__init__(sort_type)


class _HMClothesType(AbstractClothesType):
    clothes_types = {
        ClothesType.T_SHIRT: 't-shirty-i-podkoszulki',
        ClothesType.SHIRT: 'koszule',
        ClothesType.PANTS: 'spodnie',
        ClothesType.SHORTS: 'szorty',
        ClothesType.JACKET: 'marynarki-i-garnitury',
        ClothesType.SWEATER: 'kardigany-i-swetry'
    }

    def __init__(self, clothes_type: ClothesType):
        super().__init__(clothes_type)


class _HMSizeType(AbstractSizeType):
    size_types = {
        SizeType.XS: '299_xs_3_menswear',
        SizeType.S: '302_s_3_menswear',
        SizeType.M: '305_m_3_menswear',
        SizeType.L: '306_l_3_menswear',
        SizeType.XL: '308_xl_3_menswear',
        SizeType.XXL: '311_xxl_3_menswear'
    }
    key = 'sizes'

    def __init__(self, size_type: SizeType):
        super().__init__(size_type)


class _HMColorType(AbstractColorType):
    color_types = {
        ColorType.WHITE: 'biały_ffffff',
        ColorType.BLACK: 'czarny_000000',
        ColorType.GREEN: 'zielony_008000',
        ColorType.BLUE: 'niebieski_0000ff',
        ColorType.PINK: 'różowy_ffc0cb',
        ColorType.RED: 'czerwony_ff0000',
        ColorType.GREY: 'szary_808080',
        ColorType.BEIGE: 'beżowy_f5f5dc',
        ColorType.BROWN: 'brązowy_a52a2a',
        ColorType.TURQUOISE: 'turkusowy_40e0d0',
    }
    key = 'colorWithNames'

    def __init__(self, color_type: ColorType):
        super().__init__(color_type)


class HMScrapper(Scrapper):
    active_filters = {
        'sort_type': _HMSortType,
        'size': _HMSizeType,
        'color': _HMColorType,
    }
    shop_name = 'HM'
    clothes_type_class = _HMClothesType

    general_page_prefix = "https://www2.hm.com/pl_pl/on/produkty/"
    detail_page_prefix = "https://www2.hm.com/pl_pl/productpage/"

    def __init__(self):
        super().__init__()

    @property
    def detailed_url(self):
        return f"{super().detailed_url}.html"

    def generate_general_page_url(self):
        return f"{self.general_page_prefix}{self.url_filter}.html"

    def _scrap_general_data(self, page) -> List[Scrapper.BaseClothesInfo]:
        products = []
        products_container = page.find('ul', class_='products-listing small')
        if products_container:
            for product_item in products_container.find_all_next('li', class_='product-item'):
                try:
                    sale_text = product_item.find(class_='price sale')
                    if not sale_text:
                        price_text = product_item.find(class_="price regular").getText()
                        price = float(re.search("\\d+,\\d+", price_text).group(0).replace(',', '.'))
                    else:
                        price = float(re.search("\\d+,\\d+", sale_text.getText()).group(0).replace(',', '.'))

                    img_link = product_item.find(class_='image-container').a.img['data-src']
                    img_link = "http:" + img_link
                    clothes_id_and_name = product_item.find(class_="item-link")
                    name = clothes_id_and_name['title']
                    id = re.search(".\\d+.", clothes_id_and_name['href']).group(0)[1:-1]
                    products.append(Scrapper.BaseClothesInfo(id, name, price, img_link))
                except Exception as e:
                    logging.warning(f"{self.shop_name} -> Cannot scrap product {product_item}!\n {e}")
        else:
            logging.info(f"{self.shop_name} no clothes for {self.general_url}")
        return products

    def _scrap_detailed_data(self, page) -> Scrapper.DetailedClothesInfo:
        description_container = page.find('div', class_='details parbase').find('div',
                                                                                class_='content pdp-text pdp-content')
        description = description_container.find('p', class_='pdp-description-text').get_text("\n")

        composition = ''
        for attribute_item in page.find('div', class_='product-details-details sidedrawer__content').find_all_next(
                'div',
                class_='details-attributes-list-item'):
            if attribute_item.dt.getText() == 'Skład':
                composition = attribute_item.dd.getText()
        return Scrapper.DetailedClothesInfo(description, composition)

    def generate_query_string(self) -> str:
        query = "?"
        for filter in self.query_filters:
            query += f"{filter.key}={filter.value}&"
        query += f"page-size=100"
        return query


