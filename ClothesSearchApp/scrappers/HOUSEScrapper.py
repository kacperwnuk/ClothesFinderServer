import re
from typing import List

from bs4 import BeautifulSoup
from requests_html import HTMLSession

from ClothesSearchApp.models import Clothes, DetailedClothes
from ClothesSearchApp.scrappers.abstract import Scrapper, AbstractClothesType, AbstractSortType, AbstractSizeType
from ClothesSearchApp.scrappers.defaults import ClothesType, SortType, SizeType

class _HOUSEClothesType(AbstractClothesType):
    clothes_types = {
        ClothesType.T_SHIRT: 't-shirty',
        ClothesType.SHIRT: 'koszule',
        ClothesType.PANTS: 'spodnie',
        ClothesType.SHORTS: 'szorty',
        ClothesType.JEANS: 'jeansy',
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


class HOUSEScrapper(Scrapper):
    active_filters = {
        'sort_type': _HOUSESortType,
        'size': _HOUSESizeType,
    }

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

    def get_clothes_type_general_data(self, filters) -> List[Clothes]:
        self.load_filters(filters)
        page = self.beautiful_page(self.general_url)
        products_container = page.find('section', id='categoryProducts')

        products = []
        for product_item in products_container.find_all_next('article', class_='es-product'):
            # print(product_item, end="\n\n\n")
            sale_text = product_item.find('p', class_='es-discount-price')
            if not sale_text:
                price_text = product_item.find('p', class_="es-final-price").findChildren('span')[0].getText()
                price = float(re.search("\\d+,\\d+", price_text).group(0).replace(',', '.'))
            else:
                sale_text = sale_text.findChildren('span')[0]
                price = float(re.search("\\d+,\\d+", sale_text.getText()).group(0).replace(',', '.'))

            id = str.lower(product_item['data-sku'])
            name = product_item.find('figcaption', class_='es-product-name').getText()
            products.append(Clothes(id, name, price))

        return products

    def get_clothes_type_detailed_data(self, id) -> DetailedClothes:
        self.load_id(id)
        page = self.beautiful_page(self.detailed_url)

        name = page.find('h1', class_='product-name').getText()
        price_text = page.find('div', class_='regular-price').getText()
        price = float(re.search("\\d+,\\d+", price_text).group(0).replace(',', '.'))

        colors = []

        for li in page.find('ul', class_='color-picker').children:
            colors.append(li.button.img['title'])

        description = page.find('section', class_='product-description').getText()

        composition = ""
        for li in page.find('ul', class_='composition-list').children:
            composition += li.getText()

        # print(f"{name}\n{price_text}\n{colors}\n{description}\n{composition}")
        print(f"{name} {price_text} {colors} {description} {composition}")
        return DetailedClothes(id, name, price, description, colors, composition)

        # print(f"{}\n")

    def beautiful_page(self, url):

        session = HTMLSession()
        r = session.get(url)
        r.html.render()

        return BeautifulSoup(r.html.html, 'html.parser')
    #     import os
    #     with open(f"{os.getcwd()}\\tmp\HOUSETshirt.html", encoding='utf-8') as f:
    #         return BeautifulSoup(f, 'html.parser')
