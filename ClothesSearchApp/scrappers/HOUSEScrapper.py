import re
from typing import List

from bs4 import BeautifulSoup
from requests_html import HTMLSession

from django import db
from django.db import IntegrityError, transaction
from ClothesSearchApp.models import Clothes, DetailedClothes, Shop, Color, Size, Type
from ClothesSearchApp.scrappers.abstract import Scrapper, AbstractClothesType, AbstractSortType, AbstractSizeType, \
    AbstractColorType
from ClothesSearchApp.scrappers.defaults import ClothesType, SortType, SizeType, ColorType

db.connections.close_all()
session = HTMLSession()


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

    def get_clothes_type_general_data(self, request) -> List[Clothes]:
        self.load_filters(request)
        page = self.beautiful_page(self.general_url)
        products_container = page.find('section', id='categoryProducts')

        products = []
        try:
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
                # products.append(Clothes(id, name, price))
                img_link = product_item.figure.a.img['data-src']

                color = Color.objects.get(name=request['color'].value)
                size = Size.objects.get(name=request['size'].value)
                shop = Shop.objects.get(name=self.shop_name)
                type = Type.objects.get(name=request['type'].value)
                try:
                    c = Clothes.objects.create(key=id, name=name, type=type, price=price, shop=shop)
                    products.append(c)
                    print(f"{id} {name} {color} {request}")
                except IntegrityError:
                    transaction.commit()
                    c = Clothes.objects.get(key=id)
                    print(f"Already exists! {id} {name} {color} {request}")
                finally:
                    c.img_link = img_link
                    c.colors.add(color)
                    c.sizes.add(size)
                    c.save()
                    transaction.commit()
        except:
            print(f"Data not found! {request} {self.general_url}")

        return products

    def get_clothes_type_detailed_data(self, key) -> DetailedClothes:
        self.load_key(key)
        page = self.beautiful_page_js(self.detailed_url)

        description = page.find('section', class_='product-description').getText()

        composition = ""
        for li in page.find('ul', class_='composition-list').children:
            composition += li.getText()

        # print(f"{name}\n{price_text}\n{colors}\n{description}\n{composition}")
        print(f"{description} {composition}")

        try:
            general_info = Clothes.objects.get(key=key)
            dc = DetailedClothes.objects.create(clothes=general_info, description=description, composition=composition)
            dc.save()
            transaction.commit()
            return dc
        except IntegrityError:
            print(f"Integrity Error ")
            dc = DetailedClothes.objects.get(clothes__key=key)
            dc.composition = composition
            dc.description = description
            dc.save()
            transaction.commit()
        except Exception as e:
            print(f"Exception raised {e}")
            return None

        # print(f"{}\n")

    def beautiful_page_js(self, url):
        r = session.get(url)
        r.html.render()

        return BeautifulSoup(r.html.html, 'html.parser')
    #     import os
    #     with open(f"{os.getcwd()}\\tmp\HOUSETshirt.html", encoding='utf-8') as f:
    #         return BeautifulSoup(f, 'html.parser')
