import itertools

from RESERVEDScrapper import RESERVEDScrapper
from HMScrapper import HMScrapper
from HOUSEScrapper import HOUSEScrapper
from defaults import transform_request

scrapper_mapping = {
    'HM': HMScrapper,
    'HOUSE': HOUSEScrapper,
    'RESERVED': RESERVEDScrapper,
}

detailed_request = {
    'id': '0684021066',
    'shop': 'HM',
}

request = {
    'sort_type': 2,
    'size': 'M',
    'type': 'Marynarki'
}

# request = {
#     'sort_type': 2,
#     'size': 'M',
#     'type': 'T-Shirty'
# }

transformed_request = transform_request(request)
scrapper_classes = [HMScrapper, HOUSEScrapper, RESERVEDScrapper]


def create_scrappers(scrapper_classes):
    return [scrapper_class() for scrapper_class in scrapper_classes if
            transformed_request['type'] in scrapper_class.clothes_type_class.clothes_types]


def find_clothes():
    scrappers = create_scrappers(scrapper_classes)
    clothes = [scrapper.retrieve_general_data(transformed_request) for scrapper in scrappers]
    clothes = list(itertools.chain(*clothes))
    print(clothes)


def find_info():
    scrapper = scrapper_mapping[detailed_request['shop']]()
    clothes_info = scrapper.get_clothes_type_detailed_data(detailed_request['id'])
    print(clothes_info)


if __name__ == '__main__':
    # find_clothes()

    find_info()

    # RESERVEDScrapper(transformed_request).retrieve_general_data()

    # retrieve_data(clothes_types, request)
    # HMScrapper(transform_request(request)).retrieve_data()
