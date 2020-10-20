import enum


class SortType(enum.Enum):
    NONE = 1
    ASCENDING = 2
    DESCENDING = 3


class ClothesType(enum.Enum):
    T_SHIRT = 'T-SHIRT'
    SHIRT = 'SHIRT'
    PANTS = 'PANTS'
    SHORTS = 'SHORTS'
    JACKET = 'JACKET'
    SWEATER = 'SWEATER'
    JEANS = 'JEANS'


class SizeType(enum.Enum):
    XS = 'XS'
    S = 'S'
    M = 'M'
    L = 'L'
    XL = 'XL'
    XXL = 'XXL'


class ColorType(enum.Enum):
    WHITE = 'Biały'
    BLACK = 'Czarny'
    GREEN = 'Zielony'
    BLUE = 'Niebieski'
    PINK = 'Różowy'
    WHITE_BONE = 'Kość słoniowa'
    RED = 'Czerwony'
    GREY = 'Szary'
    BEIGE = 'Beżowy'
    BROWN = 'Brązowy'
    DARK_BLUE = 'Granatowy'
    TURQUOISE = 'Turkusowy'


def transform_request(request):
    transformed_request = {}
    for key, value in request.items():
        if key == 'sort_type':
            transformed_request[key] = SortType(value)
        elif key == 'size':
            transformed_request[key] = SizeType(value)
        elif key == 'color':
            transformed_request[key] = ColorType(value)
        elif key == 'type':
            transformed_request[key] = ClothesType(value)
    return transformed_request
