from HOUSEScrapper import HOUSEScrapper
from abstract import AbstractClothesType
from defaults import ClothesType


class _RESERVEDClothesType(AbstractClothesType):
    clothes_types = {
        ClothesType.T_SHIRT: 't-shirts',
        ClothesType.SHIRT: 'shirts',
        ClothesType.PANTS: 'trousers',
        ClothesType.SHORTS: 'jeans',
        ClothesType.JACKET: 'jackets',
    }


class RESERVEDScrapper(HOUSEScrapper):
    clothes_type_class = _RESERVEDClothesType

    general_page_prefix = 'https://www.reserved.com/pl/pl/man/all-3/clothes/'
    detail_page_prefix = 'https://www.reserved.com/pl/pl/'
