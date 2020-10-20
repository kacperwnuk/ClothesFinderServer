import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ClothesFinderServer.settings")
import django

django.setup()

import re
from typing import List
from bs4 import BeautifulSoup
from requests_html import HTMLSession, AsyncHTMLSession
from django import db
from ClothesSearchApp.scrappers.abstract import Scrapper, AbstractClothesType, AbstractSortType, AbstractSizeType, \
    AbstractColorType
from ClothesSearchApp.scrappers.defaults import ClothesType, SortType, SizeType, ColorType

db.connections.close_all()
# session.browser


class _HOUSEClothesType(AbstractClothesType):
    clothes_types = {
        ClothesType.T_SHIRT: 't-shirty',
        ClothesType.SHIRT: 'koszule',
        ClothesType.PANTS: 'spodnie',
        ClothesType.SHORTS: 'szorty',
        ClothesType.SWEATER: 'swetry',
    }


class _HOUSESortType(AbstractSortType):
    sort_types = {
        SortType.NONE: '',
        SortType.ASCENDING: 'sb/0',
        SortType.DESCENDING: 'sb/1'
    }

    def __init__(self, sort_type: SortType):
        super().__init__(sort_type)


class _HOUSESizeType(AbstractSizeType):
    size_types = {
        SizeType.S: 's/S',
        SizeType.M: 's/M',
        SizeType.L: 's/L',
        SizeType.XL: 's/XL',
        SizeType.XXL: 's/XXL'
    }

    def __init__(self, size_type: SizeType):
        super().__init__(size_type)


class _HOUSEColorType(AbstractColorType):
    color_types = {
        ColorType.WHITE: 'c/biały',
        ColorType.BLACK: 'c/czarny',
        ColorType.GREEN: 'c/zielony',
        ColorType.BLUE: 'c/niebieski',
        ColorType.PINK: 'c/różowy',
        ColorType.WHITE_BONE: 'c/kość słoniowa',
        ColorType.RED: 'c/czerwony',
        ColorType.GREY: 'c/szary',
        ColorType.BEIGE: 'c/beżowy',
        ColorType.BROWN: 'c/brązowy',
        ColorType.DARK_BLUE: 'c/granatowy',
        ColorType.TURQUOISE: 'c/turkusowy',
    }

    def __init__(self, color_type: ColorType):
        super().__init__(color_type)


class HOUSEScrapper(Scrapper):
    active_filters = {
        'sort_type': _HOUSESortType,
        'size': _HOUSESizeType,
        'color': _HOUSEColorType,
    }
    shop_name = 'House'

    clothes_type_class = _HOUSEClothesType

    general_page_prefix = "https://www.housebrand.com/pl/pl/on/kolekcja/"
    detail_page_prefix = "https://www.housebrand.com/pl/pl/"

    def __init__(self):
        super().__init__()

    def generate_query_string(self):
        url = '/'
        for filter in self.query_filters:
            url += f"{filter.value}/"
        return url

    def _scrap_general_data(self, page) -> List[Scrapper.BaseClothesInfo]:
        products = []
        products_container = page.find('section', id='categoryProducts')
        if products_container:
            for product_item in products_container.find_all_next('article', class_='es-product'):
                try:
                    sale_text = product_item.find('p', class_='es-discount-price')
                    if not sale_text:
                        price_text = product_item.find('p', class_="es-final-price").findChildren('span')[0].getText()
                        price = float(re.search("\\d+,\\d+", price_text).group(0).replace(',', '.'))
                    else:
                        sale_text = sale_text.findChildren('span')[0]
                        price = float(re.search("\\d+,\\d+", sale_text.getText()).group(0).replace(',', '.'))

                    id = str.lower(product_item['data-sku'])
                    name = product_item.find('figcaption', class_='es-product-name').getText()
                    img_link = product_item.figure.a.img['src']
                    products.append(Scrapper.BaseClothesInfo(id, name, price, img_link))
                except Exception as e:
                    logging.warning(f"{self.shop_name} -> Cannot scrap product {product_item}!\n {e}")
        else:
            logging.info(f"{self.shop_name} no clothes for {self.general_url}")
        return products

    def _scrap_detailed_data(self, page) -> Scrapper.DetailedClothesInfo:
        description = page.find('section', class_='product-description').get_text("\n")
        description = description.replace("\n ", "\n")
        composition = ""
        for li in page.find('ul', class_='composition-list').children:
            composition += li.getText()

        # print(f"{name}\n{price_text}\n{colors}\n{description}\n{composition}")
        print(f"{description} {composition}")
        return Scrapper.DetailedClothesInfo(description, composition)

    def _get_beautiful_page(self, url) -> BeautifulSoup:
        session = HTMLSession()
        print(url)
        r = session.get(url)
        r.html.render()
        html = r.html.html
        session.close()
        return BeautifulSoup(html, 'html.parser')
    #     import os
    #     with open(f"{os.getcwd()}\\tmp\HOUSETshirt.html", encoding='utf-8') as f:
    #         return BeautifulSoup(f, 'html.parser')
