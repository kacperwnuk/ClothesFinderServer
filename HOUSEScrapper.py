import re
from typing import List

from abstract import Scrapper, AbstractClothesType, AbstractSortType, AbstractSizeType
from defaults import Clothes, ClothesType, SortType, SizeType


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

            id = product_item['data-sku']
            name = product_item.find('figcaption', class_='es-product-name').getText()
            products.append(Clothes(id, name, price))

        return products
