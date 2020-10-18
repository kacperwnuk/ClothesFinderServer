import abc
from typing import List
import logging
import requests
import os
from bs4 import BeautifulSoup
from django.db import IntegrityError, transaction

from ClothesSearchApp.models import Clothes, DetailedClothes, Color, Size, Shop, Type
from ClothesSearchApp.scrappers.defaults import SortType, ClothesType, SizeType, ColorType


class AbstractSortType(abc.ABC):
    sort_types = {}
    # Key used in url
    key = ''

    def __init__(self, sort_type: SortType):
        self.value = self.convert_type(sort_type)

    def convert_type(self, sort_type):
        try:
            return self.sort_types[sort_type]
        except KeyError:
            return ''


class AbstractColorType(abc.ABC):
    color_types = {}
    key = ''

    def __init__(self, color_type: ColorType):
        self.value = self.convert_type(color_type)

    def convert_type(self, color_type):
        try:
            return self.color_types[color_type]
        except KeyError:
            return ''


class AbstractClothesType(abc.ABC):
    clothes_types = {}

    def __init__(self, clothes_type: ClothesType):
        self.value = self.convert_type(clothes_type)

    def convert_type(self, clothes_type):
        return self.clothes_types[clothes_type]


class AbstractSizeType(abc.ABC):
    size_types = {}
    key = ''

    def __init__(self, size_type: SizeType):
        self.value = self.convert_type(size_type)

    def convert_type(self, size_type):
        try:
            return self.size_types[size_type]
        except KeyError:
            return ''


class Scrapper(abc.ABC):
    class BaseClothesInfo:
        def __init__(self, id, name, price, img_link):
            self.id = id
            self.name = name
            self.price = price
            self.img_link = img_link

        def get_values(self):
            return self.id, self.name, self.price, self.img_link

    class DetailedClothesInfo:
        def __init__(self, description, composition):
            self.description = description
            self.composition = composition

        def get_values(self):
            return self.description, self.composition

    active_filters = {}
    shop_name = ''
    clothes_type_class = None
    general_page_prefix = ''
    detail_page_prefix = ''

    def __init__(self):
        self.query_filters = []
        self.url_filter = None
        self.detail_key = None

    def load_filters(self, filters):
        self.query_filters = []
        for key, value in filters.items():
            if key in self.active_filters:
                try:
                    active_filter = self.active_filters[key](value)
                    self.query_filters.append(active_filter)
                except KeyError:
                    logging.warning(f"Wrong filter key {key}!")
                    continue
            elif key == 'type':
                self.url_filter = self.clothes_type_class(value).value

    def load_key(self, key):
        self.detail_key = key

    @property
    def general_url(self):
        return self.generate_general_page_url() + self.generate_query_string()

    @property
    def detailed_url(self):
        return f"{self.detail_page_prefix}{self.detail_key}"

    def generate_general_page_url(self) -> str:
        return f"{self.general_page_prefix}{self.url_filter}"

    def _get_beautiful_page(self, url) -> BeautifulSoup:
        html_file = requests.get(url, headers={"User-agent":
                                                   "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/73.0"})

        return BeautifulSoup(html_file.text, 'html.parser')

    def save_html_page(self, url) -> None:
        soup = self._get_beautiful_page(url)
        with open(f"{os.getcwd()}\\tmp\\{self.shop_name}.html", mode="w", encoding="utf-8") as f:
            f.write(soup.prettify())

    def retrieve_general_data(self, filters):
        return self.get_clothes_type_general_data(filters)

    def retrieve_detailed_data(self, id):
        return self.get_clothes_type_detailed_data(id)

    @abc.abstractmethod
    def generate_query_string(self) -> str:
        ...

    def get_clothes_type_general_data(self, request) -> List[Clothes]:
        self.load_filters(request)
        page = self._get_beautiful_page(self.general_url)

        clothes = []
        basic_data_list: List[Scrapper.BaseClothesInfo] = self._scrap_general_data(page)
        for basic_data in basic_data_list:
            clothes.append(self._save_or_update_general_info(request, basic_data))

        return clothes


    @abc.abstractmethod
    def _scrap_general_data(self, page):
        ...

    @abc.abstractmethod
    def _scrap_detailed_data(self, page):
        ...

    def get_clothes_type_detailed_data(self, key) -> DetailedClothes:
        self.load_key(key)
        page = self._get_beautiful_page(self.detailed_url)

        detailed_info = self._scrap_detailed_data(page)
        return self._save_or_update_detailed_info(key, detailed_info)

    def _save_or_update_general_info(self, request, base_info: BaseClothesInfo):
        color = Color.objects.get(name=request['color'].value)
        size = Size.objects.get(name=request['size'].value)
        shop = Shop.objects.get(name=self.shop_name)
        type = Type.objects.get(name=request['type'].value)
        id, name, price, img_link = base_info.get_values()
        try:
            c = Clothes.objects.create(key=id, name=name, type=type, price=price, shop=shop, img_link=img_link)
            print(f"Created: {id} {name} {color} {request}")
        except IntegrityError:
            transaction.commit()
            c = Clothes.objects.get(key=id)
            c.price = price
            c.img_link = img_link
            c.colors.add(color)
            c.sizes.add(size)
            c.save()
            transaction.commit()
            print(f"Already exists: {id} {name} {color} {request}")
        except Exception as e:
            logging.warning(f"{e} {id} {name} {color} {request} {img_link}")
            return None
        return c

    def _save_or_update_detailed_info(self, key, detailed_info) -> DetailedClothes:
        description, composition = detailed_info.get_values()
        try:
            general_info = Clothes.objects.get(key=key)
            dc = DetailedClothes.objects.create(clothes=general_info, description=description, composition=composition)
            dc.clothes.page_link = self.detailed_url
            dc.clothes.save()
            dc.save()
            transaction.commit()
            return dc
        except IntegrityError:
            dc = DetailedClothes.objects.get(clothes__key=key)
            dc.composition = composition
            dc.description = description
            dc.clothes.page_link = self.detailed_url
            dc.clothes.save()
            dc.save()
            transaction.commit()
            print(f"Detailed cloth {dc.clothes.name} already exists, updating info..")
        except Exception as e:
            print(f"Exception raised {e}")
            return None
        return dc