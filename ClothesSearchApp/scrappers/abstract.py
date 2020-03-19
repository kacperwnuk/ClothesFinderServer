import abc
from typing import List

import requests
from bs4 import BeautifulSoup

from ClothesSearchApp.models import Clothes, DetailedClothes
from ClothesSearchApp.scrappers.defaults import SortType, ClothesType, SizeType, ColorType


class AbstractSortType(abc.ABC):
    sort_types = {}
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
                    hm_filter = self.active_filters[key](value)
                    self.query_filters.append(hm_filter)
                except KeyError:
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

    def generate_general_page_url(self):
        return f"{self.general_page_prefix}{self.url_filter}"

    def generate_query_string(self):
        query = "?"
        for filter in self.query_filters:
            query += f"{filter.key}={filter.value}&"
        query += f"page-size=100"
        return query

    def beautiful_page(self, url):
        html_file = requests.get(url, headers={"User-agent":
                                                   "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/73.0"})

        # import os
        # with open(f"{os.getcwd()}\\tmp\HOUSETshirt.html", encoding='UTF-8', mode='w') as f:
        #     f.write(r.html.html)
        return BeautifulSoup(html_file.text, 'html.parser')

    def retrieve_general_data(self, filters):
        return self.get_clothes_type_general_data(filters)

    def retrieve_detailed_data(self, id):
        return self.get_clothes_type_detailed_data(id)

    @abc.abstractmethod
    def get_clothes_type_general_data(self, filters) -> List[Clothes]:
        ...

    @abc.abstractmethod
    def get_clothes_type_detailed_data(self, id) -> DetailedClothes:
        ...
