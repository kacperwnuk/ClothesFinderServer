import re
from typing import List

from bs4 import BeautifulSoup

from abstract import AbstractSortType, AbstractClothesType, AbstractSizeType, Scrapper
from defaults import SortType, ClothesType, SizeType, Clothes, DetailedClothes
import string


class _HMSortType(AbstractSortType):
    sort_types = {
        SortType.NONE: '',
        SortType.ASCENDING: 'ascPrice',
        SortType.DESCENDING: 'descPrice'
    }
    "Key used in url"
    key = 'sort'

    def __init__(self, sort_type: SortType):
        super().__init__(sort_type)


class _HMClothesType(AbstractClothesType):
    clothes_types = {
        ClothesType.T_SHIRT: 't-shirty-i-podkoszulki',
        ClothesType.SHIRT: 'koszule',
        ClothesType.PANTS: 'spodnie',
        ClothesType.SHORTS: 'szorty',
        ClothesType.JEANS: 'dzinsy',
        ClothesType.JACKET: 'marynarki-i-garnitury',
    }

    def __init__(self, clothes_type: ClothesType):
        super().__init__(clothes_type)


class _HMSizeType(AbstractSizeType):
    size_types = {
        SizeType.XS: '296_xs_3_menswear',
        SizeType.S: '298_s_3_menswear',
        SizeType.M: '300_m_3_menswear',
        SizeType.L: '301_l_3_menswear',
        SizeType.XL: '303_xl_3_menswear',
        SizeType.XXL: '305_xxl_3_menswear'
    }
    key = 'sizes'

    def __init__(self, size_type: SizeType):
        super().__init__(size_type)


class HMScrapper(Scrapper):
    active_filters = {
        'sort_type': _HMSortType,
        'size': _HMSizeType,
    }

    clothes_type_class = _HMClothesType

    general_page_prefix = "https://www2.hm.com/pl_pl/on/produkty/"
    detail_page_prefix = "https://www2.hm.com/pl_pl/productpage."

    def __init__(self):
        super().__init__()

    @property
    def detailed_url(self):
        return f"{super().detailed_url}.html"

    def generate_general_page_url(self):
        return f"{self.general_page_prefix}{self.url_filter}.html"

    def get_clothes_type_general_data(self, filters) -> List[Clothes]:

        self.load_filters(filters)
        page = self.beautiful_page(self.general_url)
        products_container = page.find('ul', class_='products-listing small')

        products = []
        for product_item in products_container.find_all_next('li', class_='product-item'):
            # print(product_item, end="\n\n\n")
            sale_text = product_item.find(class_='price sale')
            if not sale_text:
                price_text = product_item.find(class_="price regular").getText()
                price = float(re.search("\\d+,\\d+", price_text).group(0).replace(',', '.'))
            else:
                price = float(re.search("\\d+,\\d+", sale_text.getText()).group(0).replace(',', '.'))

            clothes_id_and_name = product_item.find(class_="item-link")
            name = clothes_id_and_name['title']
            id = re.search(".\\d+.", clothes_id_and_name['href']).group(0)[1:-1]
            products.append(Clothes(id, name, price))

        return products

    def get_clothes_type_detailed_data(self, id) -> DetailedClothes:
        self.load_id(id)
        page = self.beautiful_page(self.detailed_url)

        name_price = page.find('section', class_='name-price')
        name = name_price.find('h1', class_='primary product-item-headline').getText()
        name = name.strip()

        price_text = name_price.find('span', class_='price-value').getText()
        price = float(re.search("\\d+,\\d+", price_text).group(0).replace(',', '.'))

        colors = []
        colors_container = page.find('div', class_='mini-slider').find('ul', class_='inputlist clearfix')
        for color_item in colors_container.find_all_next('li', class_='list-item hidden'):
            color = color_item.find('a')['title']
            colors.append(color)

        description_container = page.find('div', class_='details parbase').find('div', class_='content pdp-text pdp-content')
        description = description_container.find('p', class_='pdp-description-text').getText()

        composition = page.find('div', class_='product-details-details sidedrawer__content').find_all_next('div', class_='details-attributes-list-item')[1].find('dd').getText()

        # print(f"{name}\n{price}\n{colors}\n{description}\n{composition}")
        print(f"{name} {price} {colors} {description} {composition}")
        return DetailedClothes(id, name, price, description, colors, composition)

    # def beautiful_page(self, url):
    #     import os
    #     with open(f"{os.getcwd()}\\tmp\HMTshirt.html", encoding='utf-8') as f:
    #         return BeautifulSoup(f, 'html.parser')
