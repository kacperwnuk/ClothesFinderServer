import re
from typing import List

from django import db
from django.db import IntegrityError, transaction

from ClothesSearchApp.models import Clothes, DetailedClothes, Shop, Color, Size, Type
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
        ClothesType.JACKET: 'marynarki-i-garnitury',
        ClothesType.SWEATER: 'kardigany-i-swetry'
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


class _HMColorType(AbstractColorType):
    color_types = {
        ColorType.WHITE: 'biały_ffffff',
        ColorType.BLACK: 'czarny_000000',
        ColorType.GREEN: 'zielony_008000',
        ColorType.BLUE: 'niebieski_0000ff',
        ColorType.PINK: 'różowy_ffc0cb',
        # ColorType.WHITE_BONE: 'Kość słoniowa',
        ColorType.RED: 'czerwony_ff0000',
        ColorType.GREY: 'szary_808080',
        ColorType.BEIGE: 'beżowy_f5f5dc',
        ColorType.BROWN: 'brązowy_a52a2a',
        # ColorType.DARK_BLUE: 'Granatowy',
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
    detail_page_prefix = "https://www2.hm.com/pl_pl/productpage."

    def __init__(self):
        super().__init__()

    @property
    def detailed_url(self):
        return f"{super().detailed_url}.html"

    def generate_general_page_url(self):
        return f"{self.general_page_prefix}{self.url_filter}.html"

    def get_clothes_type_general_data(self, request) -> List[Clothes]:

        self.load_filters(request)
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

            img_link = product_item.find(class_='image-container').a.img['data-src']
            clothes_id_and_name = product_item.find(class_="item-link")
            name = clothes_id_and_name['title']
            id = re.search(".\\d+.", clothes_id_and_name['href']).group(0)[1:-1]

            color = Color.objects.get(name=request['color'].value)
            size = Size.objects.get(name=request['size'].value)
            shop = Shop.objects.get(name=self.shop_name)
            type = Type.objects.get(name=request['type'].value)
            try:
                c = Clothes.objects.create(key=id, name=name, type=type, price=price, shop=shop, img_link=img_link)
                products.append(c)
            except IntegrityError:
                transaction.commit()
                c = Clothes.objects.get(key=id)
                print(f"{id} {name} {color} {request}")
            finally:
                c.img_link = img_link
                c.colors.add(color)
                c.sizes.add(size)
                c.save()
                transaction.commit()
        return products

    def get_clothes_type_detailed_data(self, key) -> DetailedClothes:
        self.load_key(key)
        page = self.beautiful_page(self.detailed_url)

        description_container = page.find('div', class_='details parbase').find('div',                                                                         class_='content pdp-text pdp-content')
        description = description_container.find('p', class_='pdp-description-text').getText()

        composition = ''
        for attribute_item in page.find('div', class_='product-details-details sidedrawer__content').find_all_next('div',
                                                                                                           class_='details-attributes-list-item'):
            if attribute_item.dt.getText() == 'Skład':
                composition = attribute_item.dd.getText()

        # print(f"{name}\n{price}\n{colors}\n{description}\n{composition}")
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



    # def beautiful_page(self, url):
    #     import os
    #     with open(f"{os.getcwd()}\\tmp\HMTshirt.html", encoding='utf-8') as f:
    #         return BeautifulSoup(f, 'html.parser')
